"""Property checks for append-only migration evidence and exact rollback restoration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import pytest
from hypothesis import example, given, settings, strategies as st

from app.video.migration.contracts import MigrationEvidence, MigrationResult, SourceSnapshot
from app.video.migration.evidence import (
    EvidenceAppendError,
    InMemoryMigrationEvidenceStore,
    MigrationEvidenceRecorder,
    RollbackRequest,
    RuntimePosture,
    append_rollback_evidence,
    verify_authorized_rollback,
)

_NOW = datetime(2025, 1, 1, 12, 0, tzinfo=UTC)
_PREDECESSOR_DIGEST = "a" * 64
_CHANGE_SET_DIGEST = "b" * 64
_OTHER_PREDECESSOR_DIGEST = "c" * 64
_OTHER_CHANGE_SET_DIGEST = "d" * 64
_CHANGE_SET_REF = "change-set-property-14"
_PHASE_NAMES: tuple[str, ...] = (
    "source_intake",
    "corpus_integrity",
    "agent_mapping",
    "standalone_verification",
)
_RUNTIME_POSTURES: tuple[str, ...] = (
    "none",
    "unchanged",
    "maturity_changed",
    "activation_changed",
    "omitted",
)


@dataclass(frozen=True, slots=True)
class PhaseEvidenceCase:
    """One bounded phase result with an optional unresolved blocker."""

    phase: str
    result: MigrationResult
    has_blocker: bool


@st.composite
def _ordered_phase_evidence(draw: st.DrawFn) -> tuple[PhaseEvidenceCase, ...]:
    """Generate a short ordered sequence of distinct migration phases."""
    phases = draw(
        st.lists(
            st.sampled_from(_PHASE_NAMES),
            min_size=1,
            max_size=len(_PHASE_NAMES),
            unique=True,
        )
    )
    return tuple(
        PhaseEvidenceCase(
            phase=phase,
            result=draw(
                st.sampled_from(
                    (MigrationResult.PASS, MigrationResult.FAIL, MigrationResult.NO_CHANGE)
                )
            ),
            has_blocker=draw(st.booleans()),
        )
        for phase in phases
    )


def _source_snapshot() -> SourceSnapshot:
    """Build the fixed local-only snapshot shared by generated records."""
    return SourceSnapshot(
        source_repository="https://example.invalid/video",
        source_commit="property-14-source-commit",
        source_root="fixtures/property-14/video",
        recorded_at=_NOW,
    )


def _record_phase(
    recorder: MigrationEvidenceRecorder,
    index: int,
    case: PhaseEvidenceCase,
) -> MigrationEvidence:
    """Append one generated phase with all evidence references populated."""
    blockers = (f"{case.phase}-blocker",) if case.has_blocker else ()
    return recorder.record_phase(
        evidence_id=f"phase-property-14-{index}",
        phase=case.phase,
        source_snapshot=_source_snapshot(),
        correlation_id="correlation-property-14",
        recorded_at=_NOW + timedelta(minutes=index),
        commands=(f"check-{case.phase} --offline",),
        results=(case.result.value,),
        change_set_ref=_CHANGE_SET_REF,
        result=case.result,
        blockers=blockers,
        residual_risks=(f"{case.phase}-residual-risk",),
        review_references=(f"review-{case.phase}",),
        release_outcomes=(f"{case.phase}:{case.result.value}",),
        pre_import_manifest_digest=_PREDECESSOR_DIGEST,
        corpus_manifest_digest=_PREDECESSOR_DIGEST,
        mapping_review_ref=f"mapping-review-{case.phase}",
        standalone_result="pass",
        documentation_check_result="pass",
        change_set_digest=_CHANGE_SET_DIGEST,
    )


# Feature: migration-redesign, Property 14: Evidence is append-only and rollback
# restores the recorded predecessor.
# **Validates: Requirements 9.2, 9.3, 9.4, 9.10, 9.11, 9.12**
@settings(max_examples=24, deadline=None, derandomize=True)
@example(
    (
        PhaseEvidenceCase("source_intake", MigrationResult.PASS, False),
        PhaseEvidenceCase("standalone_verification", MigrationResult.FAIL, True),
    )
)
@example((PhaseEvidenceCase("corpus_integrity", MigrationResult.NO_CHANGE, False),))
@given(phases=_ordered_phase_evidence())
def test_property_14_phase_evidence_is_ordered_append_only_and_blockers_are_retained(
    phases: tuple[PhaseEvidenceCase, ...],
) -> None:
    """Phase records retain outcomes in order and cannot be replaced by a duplicate ID."""
    store = InMemoryMigrationEvidenceStore()
    recorder = MigrationEvidenceRecorder(store)

    records = tuple(_record_phase(recorder, index, case) for index, case in enumerate(phases))

    assert store.records() == records
    assert tuple(record.phase for record in records) == tuple(case.phase for case in phases)
    assert tuple(record.evidence_id for record in records) == tuple(
        f"phase-property-14-{index}" for index in range(len(phases))
    )
    for record, case in zip(records, phases, strict=True):
        expected_result = MigrationResult.BLOCKED if case.has_blocker else case.result
        assert record.result is expected_result
        assert record.pre_import_manifest_digest == _PREDECESSOR_DIGEST
        assert record.corpus_manifest_digest == _PREDECESSOR_DIGEST
        assert record.change_set_ref == _CHANGE_SET_REF
        assert record.change_set_digest == _CHANGE_SET_DIGEST
        assert record.review_references == (f"review-{case.phase}",)
        assert record.blockers == ((f"{case.phase}-blocker",) if case.has_blocker else ())

    before_duplicate = store.records()
    with pytest.raises(EvidenceAppendError):
        store.append(records[0])
    assert store.records() == before_duplicate
    assert records[0].canonical_json() == before_duplicate[0].canonical_json()


@dataclass(frozen=True, slots=True)
class RollbackCase:
    """Bounded authorized and malformed rollback verification inputs."""

    authorized: bool
    git_revert_applied: bool
    correct_command: bool
    target_matches: bool
    change_digest_matches: bool
    predecessor_matches: bool
    restored_matches: bool
    runtime_posture: str


@st.composite
def _rollback_cases(draw: st.DrawFn) -> RollbackCase:
    """Generate exact-match and one-field rollback drift cases."""
    return RollbackCase(
        authorized=draw(st.booleans()),
        git_revert_applied=draw(st.booleans()),
        correct_command=draw(st.booleans()),
        target_matches=draw(st.booleans()),
        change_digest_matches=draw(st.booleans()),
        predecessor_matches=draw(st.booleans()),
        restored_matches=draw(st.booleans()),
        runtime_posture=draw(st.sampled_from(_RUNTIME_POSTURES)),
    )


def _runtime_pair(case: RollbackCase) -> tuple[RuntimePosture | None, RuntimePosture | None]:
    """Project the generated runtime posture mutation into before/after records."""
    if case.runtime_posture == "none":
        return None, None
    before = RuntimePosture("L0", False)
    if case.runtime_posture == "unchanged":
        return before, RuntimePosture("L0", False)
    if case.runtime_posture == "maturity_changed":
        return before, RuntimePosture("L1", False)
    if case.runtime_posture == "activation_changed":
        return before, RuntimePosture("L0", True)
    return before, None


def _rollback_request(case: RollbackCase) -> RollbackRequest:
    """Build a validly typed request whose fields may fail verification."""
    predecessor = _PREDECESSOR_DIGEST if case.predecessor_matches else _OTHER_PREDECESSOR_DIGEST
    if case.restored_matches:
        restored = predecessor
    else:
        restored = (
            _OTHER_PREDECESSOR_DIGEST if predecessor == _PREDECESSOR_DIGEST else _PREDECESSOR_DIGEST
        )
    runtime_before, runtime_after = _runtime_pair(case)
    return RollbackRequest(
        change_set_ref=_CHANGE_SET_REF if case.target_matches else "other-change-set-property-14",
        predecessor_manifest_digest=predecessor,
        restored_manifest_digest=restored,
        authorization_ref="rollback-approval-property-14",
        authorized=case.authorized,
        authorized_by="reviewer-property-14" if case.authorized else "",
        git_revert_applied=case.git_revert_applied,
        revert_command="git revert" if case.correct_command else "git apply",
        change_set_digest=(
            _CHANGE_SET_DIGEST if case.change_digest_matches else _OTHER_CHANGE_SET_DIGEST
        ),
        runtime_before=runtime_before,
        runtime_after=runtime_after,
    )


def _migration_evidence() -> tuple[MigrationEvidenceRecorder, MigrationEvidence]:
    """Create one predecessor-bearing phase record for rollback verification."""
    store = InMemoryMigrationEvidenceStore()
    recorder = MigrationEvidenceRecorder(store)
    record = recorder.record_phase(
        evidence_id="phase-property-14-rollback",
        phase="corpus_import",
        source_snapshot=_source_snapshot(),
        correlation_id="correlation-property-14-rollback",
        recorded_at=_NOW,
        commands=("import --write",),
        results=("pass",),
        change_set_ref=_CHANGE_SET_REF,
        pre_import_manifest_digest=_PREDECESSOR_DIGEST,
        corpus_manifest_digest=_PREDECESSOR_DIGEST,
        review_references=("import-review-property-14",),
        change_set_digest=_CHANGE_SET_DIGEST,
    )
    return recorder, record


def _expected_runtime_flags(case: RollbackCase) -> tuple[bool, bool]:
    """Return expected maturity and activation preservation flags."""
    return {
        "none": (True, True),
        "unchanged": (True, True),
        "maturity_changed": (False, True),
        "activation_changed": (True, False),
        "omitted": (False, False),
    }[case.runtime_posture]


# **Validates: Requirements 9.2, 9.3, 9.4, 9.10, 9.11, 9.12**
@settings(max_examples=32, deadline=None, derandomize=True)
@example(
    RollbackCase(
        authorized=True,
        git_revert_applied=True,
        correct_command=True,
        target_matches=True,
        change_digest_matches=True,
        predecessor_matches=True,
        restored_matches=True,
        runtime_posture="unchanged",
    )
)
@example(
    RollbackCase(
        authorized=False,
        git_revert_applied=True,
        correct_command=True,
        target_matches=True,
        change_digest_matches=True,
        predecessor_matches=True,
        restored_matches=True,
        runtime_posture="unchanged",
    )
)
@example(
    RollbackCase(
        authorized=True,
        git_revert_applied=True,
        correct_command=True,
        target_matches=True,
        change_digest_matches=False,
        predecessor_matches=True,
        restored_matches=True,
        runtime_posture="unchanged",
    )
)
@example(
    RollbackCase(
        authorized=True,
        git_revert_applied=True,
        correct_command=True,
        target_matches=True,
        change_digest_matches=True,
        predecessor_matches=True,
        restored_matches=True,
        runtime_posture="activation_changed",
    )
)
@given(case=_rollback_cases())
def test_property_14_authorized_rollback_restores_exact_predecessor_without_activation_change(
    case: RollbackCase,
) -> None:
    """Only an exact authorized Git revert verifies the recorded predecessor restoration."""
    recorder, evidence = _migration_evidence()
    request = _rollback_request(case)

    verification = verify_authorized_rollback(evidence, request)
    expected_runtime_maturity, expected_runtime_activation = _expected_runtime_flags(case)
    expected_valid = (
        case.authorized
        and case.git_revert_applied
        and case.correct_command
        and case.target_matches
        and case.change_digest_matches
        and case.predecessor_matches
        and case.restored_matches
        and expected_runtime_maturity
        and expected_runtime_activation
    )

    assert verification.is_valid is expected_valid
    assert verification.result is (
        MigrationResult.PASS if expected_valid else MigrationResult.BLOCKED
    )
    assert verification.evidence_id == evidence.evidence_id
    assert verification.change_set_ref == evidence.change_set_ref
    assert verification.predecessor_manifest_digest == request.predecessor_manifest_digest
    assert verification.restored_manifest_digest == request.restored_manifest_digest
    assert verification.runtime_maturity_unchanged is expected_runtime_maturity
    assert verification.runtime_activation_unchanged is expected_runtime_activation
    assert verification.runtime_activation_changed is (not expected_runtime_activation)
    assert bool(verification.findings) is (not expected_valid)

    rollback_record = append_rollback_evidence(
        recorder,
        evidence_id="rollback-property-14",
        original=evidence,
        verification=verification,
        recorded_at=_NOW + timedelta(minutes=1),
        correlation_id="correlation-property-14-rollback",
    )
    assert recorder.records() == (evidence, rollback_record)
    assert recorder.records()[0] is evidence
    assert rollback_record.result is (
        MigrationResult.PASS if expected_valid else MigrationResult.BLOCKED
    )
    assert rollback_record.pre_import_manifest_digest == evidence.pre_import_manifest_digest
    assert rollback_record.change_set_ref == evidence.change_set_ref
    assert rollback_record.change_set_digest == evidence.change_set_digest
