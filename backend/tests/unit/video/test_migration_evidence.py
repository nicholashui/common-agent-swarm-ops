"""Focused tests for append-only migration evidence and release decisions."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime
from pathlib import Path

import pytest

from app.video.migration.contracts import MigrationEvidence, MigrationResult, SourceSnapshot
from app.video.migration.evidence import (
    REQUIRED_COMPLETION_GATES,
    CompletionClaim,
    EvidenceAppendError,
    ExecutableGateResult,
    InMemoryMigrationEvidenceStore,
    JsonlMigrationEvidenceStore,
    MigrationEvidenceRecorder,
    RollbackRequest,
    RuntimePosture,
    evaluate_completion,
    verify_authorized_rollback,
)

_NOW = datetime(2025, 1, 1, 12, 0, tzinfo=UTC)
_DIGEST = "a" * 64
_CHANGE_SET_DIGEST = "b" * 64


def _snapshot() -> SourceSnapshot:
    return SourceSnapshot(
        "https://example.invalid/video",
        "commit-1",
        "fixtures/source/video",
        _NOW,
    )


def _gates(*, failed: str | None = None) -> tuple[ExecutableGateResult, ...]:
    return tuple(
        ExecutableGateResult(
            gate=name,
            result=MigrationResult.FAIL if name == failed else MigrationResult.PASS,
            evidence_ref=f"check:{name}",
        )
        for name in REQUIRED_COMPLETION_GATES
    )


def _record(
    recorder: MigrationEvidenceRecorder, *, blockers: tuple[str, ...] = ()
) -> MigrationEvidence:
    return recorder.record_phase(
        evidence_id="phase-1" if not blockers else "phase-blocked",
        phase="intake",
        source_snapshot=_snapshot(),
        correlation_id="correlation-1",
        recorded_at=_NOW,
        commands=("check --offline",),
        results=("pass",),
        change_set_ref="change-set-1",
        blockers=blockers,
        pre_import_manifest_digest=_DIGEST,
        corpus_manifest_digest=_DIGEST,
        change_set_digest=_CHANGE_SET_DIGEST,
    )


def test_in_memory_evidence_is_append_only_and_records_are_frozen() -> None:
    store = InMemoryMigrationEvidenceStore()
    recorder = MigrationEvidenceRecorder(store)
    first = _record(recorder)

    assert first.result is MigrationResult.PASS
    assert store.records() == (first,)
    with pytest.raises(FrozenInstanceError):
        first.phase = "changed"  # type: ignore[misc]
    with pytest.raises(EvidenceAppendError):
        store.append(first)
    assert store.records() == (first,)


def test_phase_with_unresolved_blocker_is_recorded_as_blocked() -> None:
    store = InMemoryMigrationEvidenceStore()
    record = _record(MigrationEvidenceRecorder(store), blockers=("licensing uncertainty",))

    assert record.result is MigrationResult.BLOCKED
    assert record.blockers == ("licensing uncertainty",)


def test_completion_requires_every_executable_gate_and_claim_evidence() -> None:
    gates = _gates()
    claim = CompletionClaim(
        claim_id="claim-1",
        statement="Migration completion is supported by local checks.",
        executable_evidence=tuple(gate.evidence_ref for gate in gates),
    )

    report = evaluate_completion(gates, completion_claim=claim)

    assert report.is_complete
    assert report.claim is not None and report.claim.is_valid
    assert report.runtime_activation_changed is False
    assert (
        report.canonical_json()
        == evaluate_completion(gates, completion_claim=claim).canonical_json()
    )


def test_completion_blocks_on_gate_failure_and_named_security_blocker() -> None:
    report = evaluate_completion(
        _gates(failed="workflow_adaptation"),
        blockers=("security finding remains",),
    )

    assert report.result is MigrationResult.BLOCKED
    assert report.failed_gates == ("workflow_adaptation",)
    assert "security finding remains" in report.blockers
    assert any(finding.code == "completion_blocker_security" for finding in report.findings)


def test_prose_only_completion_claim_is_rejected() -> None:
    report = evaluate_completion(_gates(), completion_claim="The migration is complete.")

    assert report.result is MigrationResult.BLOCKED
    assert report.claim is not None
    assert any(
        finding.code == "completion_claim_requires_executable_evidence"
        for finding in report.claim.findings
    )


def test_jsonl_store_appends_canonical_records_without_replacing_previous_lines(
    tmp_path: Path,
) -> None:
    log = JsonlMigrationEvidenceStore(tmp_path / "migration-evidence.jsonl")
    recorder = MigrationEvidenceRecorder(log)
    first = _record(recorder)
    second = recorder.record_phase(
        evidence_id="phase-2",
        phase="standalone",
        source_snapshot=_snapshot(),
        correlation_id="correlation-1",
        recorded_at=_NOW,
        commands=("standalone --offline",),
        results=("pass",),
        change_set_ref="change-set-1",
        pre_import_manifest_digest=_DIGEST,
        corpus_manifest_digest=_DIGEST,
        change_set_digest=_CHANGE_SET_DIGEST,
    )

    lines = (tmp_path / "migration-evidence.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    assert log.raw_records()[0]["evidence_id"] == first.evidence_id
    assert log.raw_records()[1]["evidence_id"] == second.evidence_id
    assert tuple(record.evidence_id for record in log.records()) == (
        first.evidence_id,
        second.evidence_id,
    )
    with pytest.raises(EvidenceAppendError):
        log.append(first)


def test_authorized_rollback_requires_exact_recorded_digests_and_preserves_runtime_posture() -> (
    None
):
    store = InMemoryMigrationEvidenceStore()
    record = _record(MigrationEvidenceRecorder(store))
    request = RollbackRequest(
        change_set_ref=record.change_set_ref,
        predecessor_manifest_digest=_DIGEST,
        restored_manifest_digest=_DIGEST,
        authorization_ref="rollback-approval-1",
        authorized=True,
        authorized_by="reviewer-1",
        git_revert_applied=True,
        change_set_digest=_CHANGE_SET_DIGEST,
        runtime_before=RuntimePosture("L0", False),
        runtime_after=RuntimePosture("L0", False),
    )

    verification = verify_authorized_rollback(record, request)

    assert verification.is_valid
    assert verification.runtime_activation_changed is False


def test_rollback_blocks_change_set_or_runtime_posture_drift() -> None:
    store = InMemoryMigrationEvidenceStore()
    record = _record(MigrationEvidenceRecorder(store))
    request = RollbackRequest(
        change_set_ref="other-change-set",
        predecessor_manifest_digest=_DIGEST,
        restored_manifest_digest=_DIGEST,
        authorization_ref="rollback-approval-1",
        authorized=True,
        authorized_by="reviewer-1",
        git_revert_applied=True,
        change_set_digest=_CHANGE_SET_DIGEST,
        runtime_before=RuntimePosture("L0", False),
        runtime_after=RuntimePosture("L1", True),
    )

    verification = verify_authorized_rollback(record, request)

    assert verification.result is MigrationResult.BLOCKED
    assert {finding.code for finding in verification.findings} == {
        "rollback_change_set_mismatch",
        "rollback_runtime_posture_changed",
    }


def test_completion_evidence_retains_gate_outcomes_reviews_and_digests() -> None:
    store = InMemoryMigrationEvidenceStore()
    recorder = MigrationEvidenceRecorder(store)
    completion = evaluate_completion(_gates())

    record = recorder.record_completion(
        evidence_id="completion-1",
        source_snapshot=_snapshot(),
        correlation_id="correlation-1",
        recorded_at=_NOW,
        change_set_ref="change-set-1",
        completion=completion,
        commands=("release-check --offline",),
        results=("pass",),
        pre_import_manifest_digest=_DIGEST,
        corpus_manifest_digest=_DIGEST,
        review_references=("mapping-review-1", "release-review-1"),
        change_set_digest=_CHANGE_SET_DIGEST,
    )

    assert record.result is MigrationResult.PASS
    assert record.pre_import_manifest_digest == _DIGEST
    assert record.corpus_manifest_digest == _DIGEST
    assert record.review_references == ("mapping-review-1", "release-review-1")
    assert len(record.release_outcomes) == len(REQUIRED_COMPLETION_GATES)
