"""Property tests for all-evidence dual-engine migration gating."""

# ruff: noqa: E501

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Final

from hypothesis import example, given, settings, strategies as st

from app.engines.migration import LegacyEngineRetirement
from app.evaluation.migration_evidence import (
    REQUIRED_MIGRATION_GATES,
    InMemoryMigrationEvidenceRepository,
    MigrationEvidenceService,
    MigrationGate,
    MigrationGateEvidence,
)
from app.models.identifiers import CorrelationId

# Feature: generic-swarm-business-os, Property 11: Migration gate satisfaction is an all-evidence conjunction.
# **Validates: Requirements 4.8**

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_CORRELATION_ID = CorrelationId("property-11-migration-gate")
_GATE_ORDER: Final[tuple[MigrationGate, ...]] = REQUIRED_MIGRATION_GATES


@dataclass(frozen=True, slots=True)
class GateProof:
    """One bounded retained-proof outcome for a named migration requirement."""

    retained: bool
    passed: bool


@dataclass(frozen=True, slots=True)
class MigrationEvidenceCase:
    """Independent local proof facts for every required migration gate."""

    configuration_seed: int
    both_engines: GateProof
    multi_specialist_handoffs: GateProof
    visible_graph_and_interrupt: GateProof
    stubbed_gated_video_spine: GateProof
    cross_organization_resume_denial: GateProof
    fail_closed_tool_allow_list: GateProof

    @property
    def proofs(self) -> tuple[GateProof, ...]:
        """Return proof facts in the immutable gate-enum order."""
        return (
            self.both_engines,
            self.multi_specialist_handoffs,
            self.visible_graph_and_interrupt,
            self.stubbed_gated_video_spine,
            self.cross_organization_resume_denial,
            self.fail_closed_tool_allow_list,
        )


@st.composite
def _migration_evidence_cases(draw: st.DrawFn) -> MigrationEvidenceCase:
    """Generate bounded independent retained/passing facts for all six required proofs."""
    def proof() -> GateProof:
        """Generate one independent retained/passing fact."""
        return GateProof(
            retained=draw(st.booleans()),
            passed=draw(st.booleans()),
        )

    return MigrationEvidenceCase(
        configuration_seed=draw(st.integers(min_value=0, max_value=9_999)),
        both_engines=proof(),
        multi_specialist_handoffs=proof(),
        visible_graph_and_interrupt=proof(),
        stubbed_gated_video_spine=proof(),
        cross_organization_resume_denial=proof(),
        fail_closed_tool_allow_list=proof(),
    )


def _configuration_digest(case: MigrationEvidenceCase) -> str:
    """Produce a bounded, valid local configuration digest for each assessment."""
    return f"{case.configuration_seed:064x}"


def _evidence(case: MigrationEvidenceCase) -> tuple[MigrationGateEvidence, ...]:
    """Retain only generated proof results while preserving every gate's identity."""
    return tuple(
        MigrationGateEvidence(
            gate=gate,
            passed=proof.passed,
            evidence_hashes=(f"{case.configuration_seed * len(_GATE_ORDER) + index:064x}",),
        )
        for index, (gate, proof) in enumerate(zip(_GATE_ORDER, case.proofs, strict=True))
        if proof.retained
    )


def _retirement() -> tuple[
    InMemoryMigrationEvidenceRepository, MigrationEvidenceService, LegacyEngineRetirement
]:
    """Create isolated deterministic local evidence services without external dependencies."""
    repository = InMemoryMigrationEvidenceRepository()
    service = MigrationEvidenceService(repository, clock=lambda: _NOW)
    return repository, service, LegacyEngineRetirement(service)


def _expected_satisfaction(case: MigrationEvidenceCase) -> bool:
    """Express the required conjunction: every named proof must be retained and pass."""
    return all(proof.retained and proof.passed for proof in case.proofs)


@settings(max_examples=100, deadline=None, derandomize=True)
@example(
    case=MigrationEvidenceCase(
        configuration_seed=11,
        both_engines=GateProof(True, True),
        multi_specialist_handoffs=GateProof(True, True),
        visible_graph_and_interrupt=GateProof(True, True),
        stubbed_gated_video_spine=GateProof(True, True),
        cross_organization_resume_denial=GateProof(True, True),
        fail_closed_tool_allow_list=GateProof(True, True),
    )
)
@given(case=_migration_evidence_cases())
def test_migration_gate_satisfaction_requires_every_named_evidence_proof(
    case: MigrationEvidenceCase,
) -> None:
    """Only both engines and every scoped safety proof can retire LegacyEngine."""
    repository, service, retirement = _retirement()
    gates = _evidence(case)
    outcome = retirement.assess_and_retire(
        _CORRELATION_ID,
        _configuration_digest(case),
        gates,
    )

    assert outcome.is_success and outcome.value is not None
    assessment = outcome.value.assessment
    record = assessment.record
    expected_satisfied = _expected_satisfaction(case)
    expected_missing = tuple(
        gate
        for gate, proof in zip(_GATE_ORDER, case.proofs, strict=True)
        if not proof.retained
    )
    expected_failed = tuple(
        gate
        for gate, proof in zip(_GATE_ORDER, case.proofs, strict=True)
        if proof.retained and not proof.passed
    )

    assert _GATE_ORDER == (
        MigrationGate.DUAL_ENGINE,
        MigrationGate.MULTI_SPECIALIST_HANDOFFS,
        MigrationGate.VISIBLE_GRAPH_AND_INTERRUPT,
        MigrationGate.STUBBED_VIDEO_SPINE_RELEASE_GATE,
        MigrationGate.CROSS_ORGANIZATION_RESUME_DENIAL,
        MigrationGate.FAIL_CLOSED_TOOL_ALLOWLIST,
    )
    assert record.gates == gates
    assert record.missing_gates == expected_missing
    assert record.failed_gates == expected_failed
    assert assessment.is_satisfied is expected_satisfied
    assert outcome.value.retired_now is expected_satisfied
    assert retirement.is_available() is not expected_satisfied
    assert repository.assessments() == (record,)

    retained_retirement = service.latest_retirement()
    if expected_satisfied:
        assert outcome.value.retirement_evidence is not None
        assert retained_retirement == outcome.value.retirement_evidence
    else:
        assert outcome.value.retirement_evidence is None
        assert retained_retirement is None
