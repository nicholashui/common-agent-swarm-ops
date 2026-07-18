"""Focused deterministic tests for the stub-only Video_Pack spine blocker path."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from app.adapters import StubMediaAdapter, default_local_adapters
from app.audit import AuditWriter
from app.engines.compiler import CompiledGraphNode, GraphCompiler
from app.engines.graph import GraphEngine
from app.governance.authorization import ApprovalState, AuthorizationContext
from app.governance.tool_broker import HostToolBroker
from app.models.common import RecordMetadata
from app.models.identifiers import (
    CorrelationId,
    OrganizationId,
    RecordId,
    RunId,
    WorkflowDefinitionId,
)
from app.models.runs import RunRecord, RunStatus, WorkflowEngineKind
from app.repositories.run_repository import InMemoryRunRepository
from app.video.blockers import (
    COMPLIANCE_AGENT_ID,
    LocalMonotonicBlockerScheduler,
    VideoBlockerCancellationToken,
    VideoBlockerDraft,
    VideoSpineNodeExecutor,
)
from app.workflows.validator import RegisteredReferences, WorkflowDefinitionValidator
from tests.fakes.broker import InMemoryAuditRepository

NOW = datetime(2025, 1, 1, tzinfo=UTC)
ORGANIZATION_ID = OrganizationId("org-video")
CORRELATION_ID = CorrelationId("corr-video")


def _definition() -> dict[str, object]:
    path = (
        Path(__file__).resolve().parents[4]
        / "business"
        / "video"
        / "workflows"
        / "pack_spine.json"
    )
    parsed: object = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(parsed, dict)
    return parsed


def _run(definition: dict[str, object]) -> RunRecord:
    return RunRecord(
        metadata=RecordMetadata(
            record_id=RecordId("record-video"),
            organization_id=ORGANIZATION_ID,
            correlation_id=CORRELATION_ID,
            schema_version=1,
            version=1,
            created_at=NOW,
            updated_at=NOW,
        ),
        run_id=RunId("run-video"),
        workflow_definition_id=WorkflowDefinitionId("video.pack-spine"),
        workflow_definition_version="1.0.0",
        workflow_definition_digest=GraphCompiler.definition_digest(definition),
        engine=WorkflowEngineKind.GRAPH,
        status=RunStatus.DISPATCHING,
        created_for_dispatch_at=NOW,
    )


def _authorization_context(run: RunRecord, node: CompiledGraphNode) -> AuthorizationContext:
    tools = frozenset(node.declared_tool_ids)
    return AuthorizationContext(
        agent_id=node.agent_id,
        step_id=node.node_id,
        organization_id=str(run.metadata.organization_id),
        actor_id="actor-video",
        correlation_id=str(run.metadata.correlation_id),
        agent_allowed_tools=tools,
        step_declared_tools=tools,
        role_allowed_tools=tools,
        organization_allowed_tools=tools,
        risk_allowed_tools=tools,
        approval_state=ApprovalState.NOT_REQUIRED,
    )


class _DetectedComplianceBlocker:
    """Deterministically produce one compliance blocker at the review node."""

    def detect(self, _run: RunRecord, _node: object) -> VideoBlockerDraft:
        return VideoBlockerDraft(
            blocker_id="blocker-compliance-1",
            source_agent_id=COMPLIANCE_AGENT_ID,
            category="rights-consent",
            evidence_reference="evidence-video-compliance-1",
        )


def test_pack_spine_configuration_is_data_only_and_declares_only_stub_media() -> None:
    definition = _definition()
    nodes = definition["nodes"]
    assert isinstance(nodes, list)
    references = RegisteredReferences(
        agent_ids=frozenset(
            {
                "video.orchestrator",
                "video.generative_media_operator",
                COMPLIANCE_AGENT_ID,
                "video.delivery_packager",
            }
        ),
        tool_ids=frozenset({"media.stub"}),
        memory_scope_ids=frozenset(),
        risk_gate_ids=frozenset({"video.local-safe"}),
        rollback_plan_ids=frozenset({"video.stub-compensation"}),
        authorization_ids=frozenset({"video.local-spine"}),
    )

    assert WorkflowDefinitionValidator(references).validate(definition).is_valid
    assert GraphCompiler().compile(definition).pattern == "pack_spine"
    assert {tool for node in nodes for tool in node["tool_ids"]} == {"media.stub"}


def test_compliance_blocker_stops_the_next_step_and_preserves_durable_graph_state() -> None:
    definition = _definition()
    repository = InMemoryRunRepository()
    run = _run(definition)
    assert repository.create(run).is_success
    scheduler = LocalMonotonicBlockerScheduler(clock=iter((10.0, 10.25)).__next__)
    token = VideoBlockerCancellationToken(
        repository,
        ORGANIZATION_ID,
        run.run_id,
        CORRELATION_ID,
        scheduler=scheduler,
        timestamp_clock=lambda: NOW,
    )
    adapters = default_local_adapters()
    broker = HostToolBroker(adapters, AuditWriter(InMemoryAuditRepository()))
    executor = VideoSpineNodeExecutor(token, _DetectedComplianceBlocker())

    outcome = GraphEngine(
        repository,
        executor,
        broker,
        _authorization_context,
        cancellation_token=token,
    ).execute(ORGANIZATION_ID, run.run_id, definition, CORRELATION_ID)

    assert outcome.is_success and outcome.value is not None
    assert not outcome.value.completed
    record = outcome.value.record
    assert record.status is RunStatus.FAILED
    assert record.failure is not None
    assert record.failure.code == "video_compliance_blocker_detected"
    assert record.failure.stopped_step_ids == ("complete",)
    assert record.tool_effects
    assert {effect.adapter_id for effect in record.tool_effects} == {"media.stub"}
    output = record.output
    assert output is not None
    events = output["video_blocker_events"]
    assert isinstance(events, list) and events[0]["status"] == "unresolved"
    graph_state = output["graph_state"]
    assert graph_state == {
        "graph_id": record.graph_id,
        "current_node_id": "compliance-review",
        "visited_node_ids": ["compliance-review", "media-stub", "supervise"],
        "unstarted_node_ids": ("complete",),
        "interruption": "video_compliance_blocker_detected",
    }
    assert token.last_stop_elapsed_seconds is not None
    assert token.last_stop_elapsed_seconds < 5
    stub_adapter = next(adapter for adapter in adapters if isinstance(adapter, StubMediaAdapter))
    assert len(stub_adapter.retained_effects) == 1
    assert all(not adapter.retained_effects for adapter in adapters if adapter is not stub_adapter)


def test_resolved_blocker_allows_the_local_cancellation_token_to_clear() -> None:
    definition = _definition()
    repository = InMemoryRunRepository()
    run = _run(definition)
    assert repository.create(run).is_success
    token = VideoBlockerCancellationToken(
        repository,
        ORGANIZATION_ID,
        run.run_id,
        CORRELATION_ID,
        scheduler=LocalMonotonicBlockerScheduler(clock=lambda: 1.0),
        timestamp_clock=lambda: NOW,
    )
    token.publish(
        VideoBlockerDraft(
            blocker_id="blocker-video-1",
            source_agent_id=COMPLIANCE_AGENT_ID,
            category="compliance",
            evidence_reference="evidence-video-1",
        )
    )

    assert token.cancellation_reason() == "video_compliance_blocker_detected"
    assert token.resolve("blocker-video-1", "human-correction-recorded")
    assert token.cancellation_reason() is None
    retained = repository.get_by_run_id(ORGANIZATION_ID, run.run_id)
    assert retained.is_success and retained.value is not None
    assert retained.value.output is not None
    events = retained.value.output["video_blocker_events"]
    assert isinstance(events, list) and events[0]["status"] == "resolved"
