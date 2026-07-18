"""Target-local E1 evidence for the bounded LegacyEngine path."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from hashlib import sha256

from app.adapters.local import default_local_adapters
from app.audit.writer import AuditWriter
from app.engines.legacy import LegacyEngine, LegacyStep, LegacyStepResult
from app.evaluation.product_bar import (
    ProductBarCommandResult,
    ProductBarCriterion,
    ProductBarEvidenceOutcome,
    ProductBarEvidenceService,
    ProductBarStatus,
)
from app.governance.authorization import ApprovalState, AuthorizationContext
from app.governance.tool_broker import HostToolBroker, ToolInvocationResult, ToolRequest
from app.models.audit import AuditEvent
from app.models.common import RecordMetadata
from app.models.contracts import ErrorDetail, Result
from app.models.evidence import EvidenceReference
from app.models.identifiers import (
    CorrelationId,
    EvidenceId,
    OrganizationId,
    RecordId,
    RunId,
    WorkflowDefinitionId,
)
from app.models.runs import RunRecord, RunStatus, WorkflowEngineKind
from app.repositories.product_bar_repository import InMemoryProductBarEvidenceRepository
from app.repositories.run_repository import InMemoryRunRepository

NOW = datetime(2025, 1, 1, tzinfo=UTC)
ORGANIZATION_ID = OrganizationId("org-e1-legacy")
CORRELATION_ID = CorrelationId("corr-e1-legacy")


@dataclass
class _AuditRepository:
    """Retain denied-call audit events in the target-local test process."""

    events: list[AuditEvent] = field(default_factory=list)

    def append(self, event: AuditEvent) -> Result[AuditEvent, ErrorDetail]:
        self.events.append(event)
        return Result.success(event)


@dataclass
class _DenyingExecutor:
    """Use the real Host broker and retain a denied adapter outcome for E1."""

    broker: HostToolBroker
    invocations: list[ToolInvocationResult] = field(default_factory=list)

    def execute(self, _run: RunRecord, step: LegacyStep) -> LegacyStepResult:
        invocation = self.broker.request_tool(
            ToolRequest(step.declared_tool_ids[0], {"account_id": "local-e1-account"}),
            AuthorizationContext(
                agent_id=step.agent_id,
                step_id=step.step_id,
                organization_id=str(ORGANIZATION_ID),
                actor_id="legacy-engine",
                correlation_id=str(CORRELATION_ID),
                agent_allowed_tools=frozenset(),
                step_declared_tools=frozenset(step.declared_tool_ids),
                role_allowed_tools=frozenset(step.declared_tool_ids),
                organization_allowed_tools=frozenset(step.declared_tool_ids),
                risk_allowed_tools=frozenset(step.declared_tool_ids),
                approval_state=ApprovalState.NOT_REQUIRED,
            ),
        )
        self.invocations.append(invocation)
        return LegacyStepResult()


def _definition() -> dict[str, object]:
    return {
        "definition_type": "workflow_dna",
        "id": "ops.e1-legacy",
        "version": "1.0.0",
        "engine": "legacy",
        "execution_budget": {
            "max_node_visits": 1,
            "max_wall_clock_seconds": 30,
            "max_tool_requests": 1,
        },
        "steps": [{"id": "step-1", "agent_id": "ops.planner", "tool_ids": ["crm.lookup"]}],
    }


def _run(definition: dict[str, object]) -> RunRecord:
    return RunRecord(
        metadata=RecordMetadata(
            record_id=RecordId("record-e1-legacy"),
            organization_id=ORGANIZATION_ID,
            correlation_id=CORRELATION_ID,
            schema_version=1,
            version=1,
            created_at=NOW,
            updated_at=NOW,
        ),
        run_id=RunId("run-e1-legacy"),
        workflow_definition_id=WorkflowDefinitionId("ops.e1-legacy"),
        workflow_definition_version="1.0.0",
        workflow_definition_digest=LegacyEngine._definition_digest(definition),
        engine=WorkflowEngineKind.LEGACY,
        status=RunStatus.DISPATCHING,
        created_for_dispatch_at=NOW,
    )


def _digest(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


def test_e1_legacy_execution_retains_hashes_and_denied_adapter_evidence() -> None:
    """E1 retains local run, definition, configuration, and adapter evidence without effects."""
    definition = _definition()
    run = _run(definition)
    repository = InMemoryRunRepository()
    assert repository.create(run).is_success
    audit_repository = _AuditRepository()
    executor = _DenyingExecutor(
        HostToolBroker(default_local_adapters(), AuditWriter(audit_repository))
    )

    execution = LegacyEngine(repository, executor).execute(
        ORGANIZATION_ID,
        run.run_id,
        definition,
        CORRELATION_ID,
    )

    assert execution.is_success and execution.value is not None
    terminal_run = execution.value.record
    assert execution.value.completed
    assert terminal_run.status is RunStatus.COMPLETED
    assert terminal_run.tool_effects == ()
    assert len(executor.invocations) == 1
    denied = executor.invocations[0]
    assert not denied.invoked
    assert denied.effect is None
    assert denied.denial_audit_recorded is True
    assert denied.authorization.denied_constraints
    assert len(audit_repository.events) == 1

    local_adapter = next(
        adapter for adapter in default_local_adapters() if adapter.adapter_id == "crm.lookup"
    )
    run_hash = _digest(f"{terminal_run.run_id}:{terminal_run.status}")
    definition_hash = terminal_run.workflow_definition_digest
    configuration_hash = _digest("legacy-e1:max_nodes=1:max_tools=1:timeout=30")
    adapter_hash = _digest(f"{local_adapter.adapter_id}:{local_adapter.version}")
    evidence_service = ProductBarEvidenceService(
        InMemoryProductBarEvidenceRepository(),
        clock=lambda: NOW,
    )

    recorded = evidence_service.record_evidence(
        ORGANIZATION_ID,
        CORRELATION_ID,
        ProductBarCriterion.E1,
        ProductBarEvidenceOutcome.PASS,
        run_ids=(terminal_run.run_id,),
        evidence_hashes=(run_hash, definition_hash, configuration_hash, adapter_hash),
        command_results=(
            ProductBarCommandResult(
                "python -m pytest --tb=short -q tests/evidence/test_e1_legacy.py",
                0,
                run_hash,
                NOW,
            ),
        ),
        supporting_references=(
            EvidenceReference(EvidenceId("e1-run"), run_hash, "run"),
            EvidenceReference(EvidenceId("e1-definition"), definition_hash, "definition"),
            EvidenceReference(EvidenceId("e1-configuration"), configuration_hash, "configuration"),
            EvidenceReference(EvidenceId("e1-adapter"), adapter_hash, "local_adapter"),
        ),
    )

    assert recorded.is_success and recorded.value is not None
    assert recorded.value.run_ids == (terminal_run.run_id,)
    assert recorded.value.evidence_hashes == (
        run_hash,
        definition_hash,
        configuration_hash,
        adapter_hash,
    )
    assessment = evidence_service.assess(ORGANIZATION_ID, CORRELATION_ID)
    assert assessment.is_success and assessment.value is not None
    assert assessment.value.status is ProductBarStatus.INCOMPLETE
    e1_entry = assessment.value.entries[0]
    assert e1_entry.criterion is ProductBarCriterion.E1
    assert e1_entry.outcome is ProductBarEvidenceOutcome.PASS
