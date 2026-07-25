"""Property tests for all-evidence dual-engine migration gating."""

# ruff: noqa: E501

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Final, Protocol

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

# Feature: generic-swarm-business-os, Property 11: Migration gate satisfaction is an all-evidence conjunction
# **Validates: Requirements 4.8**

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_CORRELATION_ID = CorrelationId("property-11-migration-gate")
_GATE_ORDER: Final[tuple[MigrationGate, ...]] = REQUIRED_MIGRATION_GATES


class MigrationProof(Protocol):
    """Common shape for target-local deterministic migration proof fakes."""

    @property
    def retained(self) -> bool:
        """Return whether this proof was independently retained."""

    @property
    def passed(self) -> bool:
        """Return whether the proof's concrete facts satisfy its gate."""


@dataclass(frozen=True, slots=True)
class DualEngineProof:
    """Fake evidence that both bounded engines completed the migration exercise."""

    retained: bool
    legacy_engine_completed: bool
    graph_engine_completed: bool

    @property
    def passed(self) -> bool:
        """Require successful evidence from both engines, not either engine alone."""
        return self.legacy_engine_completed and self.graph_engine_completed


@dataclass(frozen=True, slots=True)
class SpecialistHandoffProof:
    """Fake evidence for a handoff between at least two distinct specialists."""

    retained: bool
    handoff_count: int
    distinct_specialist_count: int

    @property
    def passed(self) -> bool:
        """Require a bounded multi-specialist handoff rather than a single-agent run."""
        return self.handoff_count >= 1 and self.distinct_specialist_count >= 2


@dataclass(frozen=True, slots=True)
class GraphInterruptProof:
    """Fake operator observation evidence for graph topology and interruption."""

    retained: bool
    graph_visible: bool
    interrupt_visible: bool
    operator_can_interrupt: bool

    @property
    def passed(self) -> bool:
        """Require both visible state and an actionable operator interrupt."""
        return self.graph_visible and self.interrupt_visible and self.operator_can_interrupt


@dataclass(frozen=True, slots=True)
class VideoSpineProof:
    """Fake evidence that the video spine is stub-only and release-gated."""

    retained: bool
    stub_media_tools_only: bool
    release_gate_passed: bool
    external_access_attempted: bool

    @property
    def passed(self) -> bool:
        """Reject a video proof that uses an external resource or skips its release gate."""
        return (
            self.stub_media_tools_only
            and self.release_gate_passed
            and not self.external_access_attempted
        )


@dataclass(frozen=True, slots=True)
class CrossOrganizationResumeProof:
    """Fake checkpoint evidence for denying a foreign-organization resume pre-lookup."""

    retained: bool
    cross_organization_resume_denied: bool
    checkpoint_lookup_before_denial: bool

    @property
    def passed(self) -> bool:
        """Require denial before a foreign checkpoint can be looked up."""
        return self.cross_organization_resume_denied and not self.checkpoint_lookup_before_denial


@dataclass(frozen=True, slots=True)
class ToolAllowListProof:
    """Fake broker evidence for allowed invocation and fail-closed denial."""

    retained: bool
    allowlisted_tool_invoked: bool
    denied_tool_invoked: bool
    denial_audited: bool

    @property
    def passed(self) -> bool:
        """Require allow-listed success and no effect from a denied request."""
        return (
            self.allowlisted_tool_invoked and not self.denied_tool_invoked and self.denial_audited
        )


@dataclass(frozen=True, slots=True)
class MigrationEvidenceCase:
    """Bounded independent facts for every required migration gate."""

    configuration_seed: int
    both_engines: DualEngineProof
    multi_specialist_handoffs: SpecialistHandoffProof
    visible_graph_and_interrupt: GraphInterruptProof
    stubbed_gated_video_spine: VideoSpineProof
    cross_organization_resume_denial: CrossOrganizationResumeProof
    fail_closed_tool_allow_list: ToolAllowListProof

    @property
    def proofs(self) -> tuple[MigrationProof, ...]:
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
    """Generate bounded retained and concrete pass/fail facts for all six proofs."""
    return MigrationEvidenceCase(
        configuration_seed=draw(st.integers(min_value=0, max_value=9_999)),
        both_engines=DualEngineProof(
            retained=draw(st.booleans()),
            legacy_engine_completed=draw(st.booleans()),
            graph_engine_completed=draw(st.booleans()),
        ),
        multi_specialist_handoffs=SpecialistHandoffProof(
            retained=draw(st.booleans()),
            handoff_count=draw(st.integers(min_value=0, max_value=3)),
            distinct_specialist_count=draw(st.integers(min_value=0, max_value=3)),
        ),
        visible_graph_and_interrupt=GraphInterruptProof(
            retained=draw(st.booleans()),
            graph_visible=draw(st.booleans()),
            interrupt_visible=draw(st.booleans()),
            operator_can_interrupt=draw(st.booleans()),
        ),
        stubbed_gated_video_spine=VideoSpineProof(
            retained=draw(st.booleans()),
            stub_media_tools_only=draw(st.booleans()),
            release_gate_passed=draw(st.booleans()),
            external_access_attempted=draw(st.booleans()),
        ),
        cross_organization_resume_denial=CrossOrganizationResumeProof(
            retained=draw(st.booleans()),
            cross_organization_resume_denied=draw(st.booleans()),
            checkpoint_lookup_before_denial=draw(st.booleans()),
        ),
        fail_closed_tool_allow_list=ToolAllowListProof(
            retained=draw(st.booleans()),
            allowlisted_tool_invoked=draw(st.booleans()),
            denied_tool_invoked=draw(st.booleans()),
            denial_audited=draw(st.booleans()),
        ),
    )


def _configuration_digest(case: MigrationEvidenceCase) -> str:
    """Produce a bounded, valid local configuration digest for each assessment."""
    return f"{case.configuration_seed:064x}"


def _evidence(case: MigrationEvidenceCase) -> tuple[MigrationGateEvidence, ...]:
    """Retain only generated proof results while preserving each gate's identity."""
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
    """Express the required conjunction: every proof is retained and passes."""
    return all(proof.retained and proof.passed for proof in case.proofs)


@settings(max_examples=100, deadline=None, derandomize=True)
@example(
    case=MigrationEvidenceCase(
        configuration_seed=11,
        both_engines=DualEngineProof(True, True, True),
        multi_specialist_handoffs=SpecialistHandoffProof(True, 1, 2),
        visible_graph_and_interrupt=GraphInterruptProof(True, True, True, True),
        stubbed_gated_video_spine=VideoSpineProof(True, True, True, False),
        cross_organization_resume_denial=CrossOrganizationResumeProof(True, True, False),
        fail_closed_tool_allow_list=ToolAllowListProof(True, True, False, True),
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
        gate for gate, proof in zip(_GATE_ORDER, case.proofs, strict=True) if not proof.retained
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
