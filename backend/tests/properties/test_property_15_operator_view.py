"""Property tests for actionable operator projections and pre-effect previews."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Literal

from hypothesis import example, given, settings, strategies as st

from app.api.v1.approvals import _gate_response
from app.api.v1.runs import _event_response, _preview_response, _run_response
from app.api.v1.schemas import (
    ActionPreviewResponse,
    ApprovalGateResponse,
    DispatchResponse,
    OperatorEventResponse,
    RunResponse,
)
from app.api.v1.services import ControlPlaneServices
from app.governance.approvals import ActionPreview, ApprovalGate, ApprovalGateStatus
from app.models.common import RecordMetadata
from app.models.evidence import EvidenceReference
from app.models.identifiers import (
    ApprovalId,
    CorrelationId,
    EvidenceId,
    OrganizationId,
    RecordId,
    RunId,
    WorkflowDefinitionId,
)
from app.models.runs import FailureState, RunRecord, RunStatus, WorkflowEngineKind
from app.repositories.run_repository import InMemoryRunRepository

# Feature: generic-swarm-business-os, Property 15: Operator-visible executable state is
# actionable before effect.
# **Validates: Requirements 6.5, 6.6**

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_ORGANIZATION_ID = OrganizationId("org-property-15")
_CORRELATION_ID = CorrelationId("corr-property-15")


@dataclass(frozen=True, slots=True)
class OperatorViewCase:
    """One bounded visible-state projection and its human-context field."""

    visible_state: Literal["recommendation", "action", "approval", "failure"]
    context_field: Literal["evidence", "confidence", "uncertainty", "correction"]
    suffix: int


@dataclass(slots=True)
class RecordingStarter:
    """A deterministic execution boundary that verifies visible preview ordering."""

    services: ControlPlaneServices | None = None
    visible_events_at_effect: tuple[OperatorEventResponse, ...] = ()
    trace: list[str] | None = None

    def __post_init__(self) -> None:
        self.trace = []

    def __call__(self, _record: RunRecord) -> None:
        """Observe the persisted response event immediately before local execution starts."""
        assert self.services is not None
        events = self.services.get_events(
            _ORGANIZATION_ID,
            _record.run_id,
            _CORRELATION_ID,
        )
        assert events.is_success and events.value is not None
        self.visible_events_at_effect = tuple(_event_response(event) for event in events.value)
        assert self.visible_events_at_effect[-1].kind == "action_preview"
        assert self.visible_events_at_effect[-1].action_preview is not None
        assert self.trace is not None
        self.trace.append("effect-invoked")


@st.composite
def _operator_view_cases(draw: st.DrawFn) -> OperatorViewCase:
    """Generate bounded operator-visible state and valid context combinations."""
    return OperatorViewCase(
        visible_state=draw(
            st.sampled_from(("recommendation", "action", "approval", "failure"))
        ),
        context_field=draw(
            st.sampled_from(("evidence", "confidence", "uncertainty", "correction"))
        ),
        suffix=draw(st.integers(min_value=0, max_value=9_999)),
    )


def _preview(case: OperatorViewCase) -> ActionPreview:
    """Build an otherwise-minimal preview with exactly one human-centered field."""
    return ActionPreview(
        action_id=f"action-{case.suffix}",
        summary="Review the deterministic local action before it can execute.",
        intended_effect="A deterministic local effect would be recorded.",
        supporting_evidence=(f"evidence-{case.suffix}",)
        if case.context_field == "evidence"
        else (),
        confidence=0.5 if case.context_field == "confidence" else None,
        uncertainty="Operator review is required before execution."
        if case.context_field == "uncertainty"
        else None,
        correction_control="Do not confirm the action."
        if case.context_field == "correction"
        else None,
    )


def _record(case: OperatorViewCase, status: RunStatus) -> RunRecord:
    """Build one local run record, with a failure state when requested."""
    failure = (
        FailureState(
            code="deterministic_failure",
            evidence_references=(
                EvidenceReference(
                    evidence_id=EvidenceId(f"failure-evidence-{case.suffix}"),
                    digest=f"failure-digest-{case.suffix}",
                    kind="execution-event",
                ),
            ),
            stopped_step_ids=("step-1",),
            failure_processing_complete=True,
        )
        if status is RunStatus.FAILED
        else None
    )
    return RunRecord(
        metadata=RecordMetadata(
            record_id=RecordId(f"record-property-15-{case.suffix}"),
            organization_id=_ORGANIZATION_ID,
            correlation_id=_CORRELATION_ID,
            schema_version=1,
            version=1,
            created_at=_NOW,
            updated_at=_NOW,
        ),
        run_id=RunId(f"run-property-15-{case.suffix}"),
        workflow_definition_id=WorkflowDefinitionId("ops.operator-view"),
        workflow_definition_version="1.0.0",
        workflow_definition_digest="workflow-digest-property-15",
        engine=WorkflowEngineKind.LEGACY,
        status=status,
        created_for_dispatch_at=_NOW,
        failure=failure,
    )


def _operator_projection(
    case: OperatorViewCase,
) -> ActionPreviewResponse | DispatchResponse | ApprovalGateResponse | RunResponse:
    """Project each displayed state through its production response mapper."""
    preview = _preview(case)
    if case.visible_state == "recommendation":
        return _preview_response(preview, _NOW)
    if case.visible_state == "action":
        return DispatchResponse(
            run_id=f"run-property-15-{case.suffix}",
            status=RunStatus.QUEUED,
            executed=False,
            preview=_preview_response(preview, _NOW),
        )
    if case.visible_state == "approval":
        gate = ApprovalGate(
            metadata=RecordMetadata(
                record_id=RecordId(f"gate-record-property-15-{case.suffix}"),
                organization_id=_ORGANIZATION_ID,
                correlation_id=_CORRELATION_ID,
                schema_version=1,
                version=1,
                created_at=_NOW,
                updated_at=_NOW,
            ),
            approval_id=ApprovalId(f"approval-property-15-{case.suffix}"),
            run_id=RunId(f"run-property-15-{case.suffix}"),
            risk_tier="critical",
            action_preview=preview,
            status=ApprovalGateStatus.PAUSED,
        )
        return _gate_response(gate)
    return _run_response(
        _record(case, RunStatus.FAILED),
        _preview_response(preview, _NOW),
    )


def _preview_from(
    projection: ActionPreviewResponse | DispatchResponse | ApprovalGateResponse | RunResponse,
) -> ActionPreviewResponse:
    """Return the visible preview from each concrete operator response type."""
    if isinstance(projection, ActionPreviewResponse):
        return projection
    if isinstance(projection, DispatchResponse):
        return projection.preview
    if isinstance(projection, ApprovalGateResponse):
        return projection.action_preview
    assert projection.action_preview is not None
    return projection.action_preview


def _has_human_context(preview: ActionPreviewResponse) -> bool:
    """Return whether the preview gives an operator actionable context."""
    return bool(
        preview.supporting_evidence
        or preview.confidence is not None
        or preview.uncertainty
        or preview.correction_control
    )


@settings(max_examples=100, deadline=None, derandomize=True)
@example(OperatorViewCase("recommendation", "evidence", 1))
@example(OperatorViewCase("action", "confidence", 2))
@example(OperatorViewCase("approval", "uncertainty", 3))
@example(OperatorViewCase("failure", "correction", 4))
@given(case=_operator_view_cases())
def test_operator_visible_state_is_actionable_before_local_effect(
    case: OperatorViewCase,
) -> None:
    """All response projections expose human context, and execution sees preview first."""
    projection = _operator_projection(case)
    preview = _preview_from(projection)

    assert _has_human_context(preview)
    assert preview.emitted_at == _NOW
    if isinstance(projection, DispatchResponse):
        assert projection.run_id
        assert not projection.executed
    elif isinstance(projection, ApprovalGateResponse):
        assert projection.run_id
        assert projection.created_at == _NOW
    elif isinstance(projection, RunResponse):
        assert projection.run_id
        assert projection.updated_at == _NOW
        assert projection.failure_code == "deterministic_failure"

    repository = InMemoryRunRepository()
    record = _record(case, RunStatus.QUEUED)
    created = repository.create(record)
    assert created.is_success and created.value == record
    starter = RecordingStarter()
    services = ControlPlaneServices(run_repository=repository, starter=starter)
    starter.services = services

    dispatch = services.preview_or_dispatch(
        _ORGANIZATION_ID,
        _CORRELATION_ID,
        record.run_id,
        f"dispatch-property-15-{case.suffix}",
        confirm=True,
    )

    assert dispatch.is_success and dispatch.value is not None
    stored_events = services.get_events(_ORGANIZATION_ID, record.run_id, _CORRELATION_ID)
    assert stored_events.is_success and stored_events.value is not None
    projected_events = tuple(_event_response(event) for event in stored_events.value)
    assert tuple(event.kind for event in projected_events) == ("action_preview", "dispatch")
    assert starter.visible_events_at_effect == (projected_events[0],)
    assert starter.visible_events_at_effect[0].action_preview is not None
    assert starter.trace == ["effect-invoked"]
