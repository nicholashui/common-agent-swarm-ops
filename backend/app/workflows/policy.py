"""Runtime barriers for declared workflow budgets, gates, and memory scopes."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from enum import StrEnum
from time import monotonic
from typing import TypeVar

from app.models.contracts import Allowed, Blocked, CommandOutcome, Denied, FailedRecoverable
from app.models.identifiers import CorrelationId, EvidenceId

T = TypeVar("T")


class WorkflowActionKind(StrEnum):
    """Action boundaries whose policy must be checked before execution."""

    NODE = "node"
    TOOL = "tool"
    HANDOFF = "handoff"
    MEMORY_READ = "memory_read"
    MEMORY_WRITE = "memory_write"
    APPROVAL = "approval"
    ROLLBACK = "rollback"


class ApprovalStatus(StrEnum):
    """Approval state supplied by the control-plane approval gate."""

    APPROVED = "approved"
    PENDING = "pending"
    DENIED = "denied"


@dataclass(frozen=True, slots=True)
class WorkflowAction:
    """Normalized, untrusted action description presented to the policy barrier."""

    action_id: str
    kind: WorkflowActionKind
    memory_scope: str | None = None
    requires_approval: bool = False
    approval_id: str | None = None
    approval_status: ApprovalStatus | str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.action_id, str) or not self.action_id.strip():
            raise ValueError("Workflow actions require a non-empty action ID.")
        object.__setattr__(self, "kind", WorkflowActionKind(self.kind))
        if self.memory_scope is not None and not self.memory_scope.strip():
            raise ValueError("Workflow action memory scopes must be non-empty when present.")
        if self.approval_id is not None and not self.approval_id.strip():
            raise ValueError("Workflow action approval IDs must be non-empty when present.")
        if self.approval_status is not None:
            object.__setattr__(self, "approval_status", ApprovalStatus(self.approval_status))


@dataclass(frozen=True, slots=True)
class WorkflowPolicy:
    """Immutable runtime view of the policies declared by one workflow definition."""

    workflow_id: str
    budget: Mapping[str, int]
    memory_reads: frozenset[str]
    memory_writes: frozenset[str]
    rollback_plan_id: str | None = None
    compensation_step_ids: tuple[str, ...] = ()
    authorization_id: str | None = None
    approval_required: bool = False
    approval_required_kinds: frozenset[WorkflowActionKind] = frozenset()

    @classmethod
    def from_definition(cls, definition: Mapping[str, object]) -> WorkflowPolicy:
        """Parse only declared policy fields; unknown values never become authority."""
        workflow_id = definition.get("id")
        if not isinstance(workflow_id, str) or not workflow_id.strip():
            raise ValueError("Workflow policy requires a workflow ID.")

        raw_budget = definition.get("execution_budget")
        budget: dict[str, int] = {}
        if isinstance(raw_budget, Mapping):
            for key in (
                "max_node_visits",
                "max_handoffs",
                "max_tool_requests",
                "max_wall_clock_seconds",
            ):
                value = raw_budget.get(key)
                if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
                    budget[key] = value

        raw_memory = definition.get("memory")
        reads: frozenset[str] = frozenset()
        writes: frozenset[str] = frozenset()
        if isinstance(raw_memory, Mapping):
            reads = _text_set(raw_memory.get("reads"))
            writes = _text_set(raw_memory.get("writes"))

        raw_rollback = definition.get("rollback")
        rollback_plan_id: str | None = None
        compensation_step_ids: tuple[str, ...] = ()
        if isinstance(raw_rollback, Mapping):
            plan_id = raw_rollback.get("plan_id")
            if isinstance(plan_id, str) and plan_id.strip():
                rollback_plan_id = plan_id
            raw_steps = raw_rollback.get("compensation_step_ids")
            if isinstance(raw_steps, (list, tuple)):
                compensation_step_ids = tuple(
                    value for value in raw_steps if isinstance(value, str) and value.strip()
                )

        authorization_id = definition.get("authorization_id")
        if not isinstance(authorization_id, str) or not authorization_id.strip():
            authorization_id = None

        approval_kinds: set[WorkflowActionKind] = set()
        approval_required = False
        raw_approval = definition.get("approval")
        if isinstance(raw_approval, Mapping):
            approval_required = raw_approval.get("required") is True
            raw_kinds = raw_approval.get("required_action_kinds", raw_approval.get("actions"))
            if isinstance(raw_kinds, (list, tuple, set, frozenset)):
                for value in raw_kinds:
                    try:
                        approval_kinds.add(WorkflowActionKind(value))
                    except (TypeError, ValueError):
                        continue

        return cls(
            workflow_id=workflow_id,
            budget=budget,
            memory_reads=reads,
            memory_writes=writes,
            rollback_plan_id=rollback_plan_id,
            compensation_step_ids=compensation_step_ids,
            authorization_id=authorization_id,
            approval_required=approval_required,
            approval_required_kinds=frozenset(approval_kinds),
        )


@dataclass(frozen=True, slots=True)
class WorkflowActionFailure:
    """Safe failure input for an effect that may require declared compensation."""

    action: WorkflowAction
    reason: str


class WorkflowPolicyBarrier:
    """Enforce declared workflow policy at every action boundary.

    The barrier is deliberately stateful only for bounded counters. It never treats a
    missing budget, scope, approval, or rollback declaration as permission to proceed.
    """

    def __init__(
        self,
        definition: Mapping[str, object] | WorkflowPolicy,
        *,
        rollback: Callable[[WorkflowAction], bool] | None = None,
        clock: Callable[[], float] = monotonic,
    ) -> None:
        self.policy = (
            definition
            if isinstance(definition, WorkflowPolicy)
            else WorkflowPolicy.from_definition(definition)
        )
        self._rollback = rollback
        self._clock = clock
        self._started_at = clock()
        self._counts: dict[WorkflowActionKind, int] = {kind: 0 for kind in WorkflowActionKind}

    @property
    def counts(self) -> Mapping[WorkflowActionKind, int]:
        """Return a read-only snapshot of bounded action counters."""
        return dict(self._counts)

    def authorize_action(
        self,
        action: WorkflowAction | Mapping[str, object],
        *,
        approval_status: ApprovalStatus | str | None = None,
    ) -> CommandOutcome[WorkflowAction]:
        """Return an explicit allow, denial, or block before an action can run."""
        try:
            normalized = _coerce_action(action)
        except (TypeError, ValueError):
            return Denied(
                "Workflow action is invalid and cannot be authorized.",
                CorrelationId("workflow-action:invalid"),
            )
        kind = normalized.kind
        wall_limit = self.policy.budget.get("max_wall_clock_seconds")
        try:
            elapsed = self._clock() - self._started_at
        except Exception:
            return FailedRecoverable(
                "Workflow wall-clock budget could not be evaluated.",
                evidence_correlation(normalized),
            )
        if wall_limit is None or elapsed >= wall_limit:
            return Denied(
                f"Workflow wall-clock budget denied action {normalized.action_id}.",
                evidence_correlation(normalized),
            )
        if kind is WorkflowActionKind.MEMORY_READ and (
            normalized.memory_scope is None
            or normalized.memory_scope not in self.policy.memory_reads
        ):
            return Denied(
                f"Workflow memory-read policy denied action {normalized.action_id}.",
                evidence_correlation(normalized),
            )
        if kind is WorkflowActionKind.MEMORY_WRITE and (
            normalized.memory_scope is None
            or normalized.memory_scope not in self.policy.memory_writes
        ):
            return Denied(
                f"Workflow memory-write policy denied action {normalized.action_id}.",
                evidence_correlation(normalized),
            )
        budget_key = _budget_key(kind)
        if budget_key is not None:
            limit = self.policy.budget.get(budget_key)
            if limit is None or self._counts[kind] >= limit:
                return Denied(
                    f"Workflow {budget_key} policy denied action {normalized.action_id}.",
                    evidence_correlation(normalized),
                )

        status_value = (
            approval_status if approval_status is not None else normalized.approval_status
        )
        needs_approval = (
            normalized.requires_approval
            or kind is WorkflowActionKind.APPROVAL
            or self.policy.approval_required
            or kind in self.policy.approval_required_kinds
        )
        if needs_approval:
            if self.policy.authorization_id is None:
                return Denied(
                    f"Workflow approval policy denied action {normalized.action_id}.",
                    evidence_correlation(normalized),
                )
            if (
                normalized.approval_id is not None
                and normalized.approval_id != self.policy.authorization_id
            ):
                return Denied(
                    f"Workflow approval policy denied action {normalized.action_id}.",
                    evidence_correlation(normalized),
                )
            try:
                status = (
                    ApprovalStatus(status_value)
                    if status_value is not None
                    else ApprovalStatus.PENDING
                )
            except ValueError:
                status = ApprovalStatus.PENDING
            if status is ApprovalStatus.PENDING:
                return Blocked(
                    f"Workflow approval is pending for action {normalized.action_id}.",
                    evidence_correlation(normalized),
                )
            if status is ApprovalStatus.DENIED:
                return Denied(
                    f"Workflow approval denied action {normalized.action_id}.",
                    evidence_correlation(normalized),
                )

        if kind is WorkflowActionKind.ROLLBACK and self.policy.rollback_plan_id is None:
            return Denied(
                f"Workflow rollback policy denied action {normalized.action_id}.",
                evidence_correlation(normalized),
            )
        self._counts[kind] += 1
        return Allowed(
            normalized,
            evidence=(
                EvidenceId(f"workflow-policy:{self.policy.workflow_id}:{normalized.action_id}"),
            ),
            correlation_id=evidence_correlation(normalized),
        )

    def authorize(
        self, action: WorkflowAction | Mapping[str, object], **kwargs: object
    ) -> CommandOutcome[WorkflowAction]:
        """Alias for callers that name the action-boundary method ``authorize``."""
        status = kwargs.get("approval_status")
        if status is not None and not isinstance(status, (str, ApprovalStatus)):
            status = None
        return self.authorize_action(action, approval_status=status)

    def execute_action(
        self,
        action: WorkflowAction | Mapping[str, object],
        effect: Callable[[], T],
        *,
        approval_status: ApprovalStatus | str | None = None,
    ) -> CommandOutcome[T]:
        """Authorize, execute, and compensate one action without a policy bypass."""
        decision = self.authorize_action(action, approval_status=approval_status)
        if not isinstance(decision, Allowed):
            return decision
        normalized = decision.value
        try:
            return Allowed(
                effect(),
                evidence=decision.evidence,
                correlation_id=decision.correlation_id,
            )
        except Exception as error:
            if self.policy.rollback_plan_id is None:
                return FailedRecoverable(
                    f"Workflow action {normalized.action_id} failed and has no declared rollback.",
                    decision.correlation_id,
                )
            rollback = self._rollback
            if rollback is None:
                return FailedRecoverable(
                    f"Workflow rollback is unavailable for action {normalized.action_id}.",
                    decision.correlation_id,
                )
            try:
                compensated = rollback(normalized)
            except Exception:
                compensated = False
            if not compensated:
                return FailedRecoverable(
                    f"Workflow rollback failed for action {normalized.action_id}.",
                    decision.correlation_id,
                )
            return FailedRecoverable(
                "Workflow action "
                f"{normalized.action_id} failed and rollback completed: "
                f"{error.__class__.__name__}.",
                decision.correlation_id,
            )

    execute = execute_action

    def authorize_node(
        self, action: WorkflowAction | Mapping[str, object]
    ) -> CommandOutcome[WorkflowAction]:
        """Authorize one node-visit boundary."""
        return self.authorize_action(action)

    def authorize_tool(
        self, action: WorkflowAction | Mapping[str, object]
    ) -> CommandOutcome[WorkflowAction]:
        """Authorize one tool-request boundary."""
        return self.authorize_action(action)

    def authorize_handoff(
        self, action: WorkflowAction | Mapping[str, object]
    ) -> CommandOutcome[WorkflowAction]:
        """Authorize one artifact-handoff boundary."""
        return self.authorize_action(action)

    def authorize_memory_read(
        self, action: WorkflowAction | Mapping[str, object]
    ) -> CommandOutcome[WorkflowAction]:
        """Authorize one declared memory-read boundary."""
        return self.authorize_action(action)

    def authorize_memory_write(
        self, action: WorkflowAction | Mapping[str, object]
    ) -> CommandOutcome[WorkflowAction]:
        """Authorize one declared memory-write boundary."""
        return self.authorize_action(action)

    def authorize_approval(
        self,
        action: WorkflowAction | Mapping[str, object],
        *,
        approval_status: ApprovalStatus | str | None = None,
    ) -> CommandOutcome[WorkflowAction]:
        """Authorize one approval boundary using the current gate state."""
        return self.authorize_action(action, approval_status=approval_status)

    def authorize_rollback(
        self, action: WorkflowAction | Mapping[str, object]
    ) -> CommandOutcome[WorkflowAction]:
        """Authorize one declared rollback boundary."""
        return self.authorize_action(action)


WorkflowPolicyEnforcer = WorkflowPolicyBarrier
DeclaredWorkflowPolicyBarrier = WorkflowPolicyBarrier
WorkflowExecutionService = WorkflowPolicyBarrier


def _coerce_action(value: WorkflowAction | Mapping[str, object]) -> WorkflowAction:
    if isinstance(value, WorkflowAction):
        return value
    if not isinstance(value, Mapping):
        raise TypeError("Workflow actions must be WorkflowAction values or mappings.")
    raw_kind = value.get("kind", value.get("action_type", value.get("type")))
    if not isinstance(raw_kind, (str, WorkflowActionKind)):
        raise ValueError("Workflow actions require a kind.")
    raw_status = value.get("approval_status")
    return WorkflowAction(
        action_id=str(value.get("action_id", value.get("id", "action"))),
        kind=WorkflowActionKind(raw_kind),
        memory_scope=_optional_text(value.get("memory_scope", value.get("scope"))),
        requires_approval=bool(
            value.get("requires_approval", value.get("approval_required", False))
        ),
        approval_id=_optional_text(value.get("approval_id", value.get("authorization_id"))),
        approval_status=raw_status if isinstance(raw_status, (str, ApprovalStatus)) else None,
    )


def _budget_key(kind: WorkflowActionKind) -> str | None:
    return {
        WorkflowActionKind.NODE: "max_node_visits",
        WorkflowActionKind.HANDOFF: "max_handoffs",
        WorkflowActionKind.TOOL: "max_tool_requests",
    }.get(kind)


def _text_set(value: object) -> frozenset[str]:
    if not isinstance(value, (list, tuple, set, frozenset)):
        return frozenset()
    return frozenset(item for item in value if isinstance(item, str) and item.strip())


def _optional_text(value: object) -> str | None:
    return value if isinstance(value, str) and value.strip() else None


def evidence_correlation(action: WorkflowAction) -> CorrelationId:
    """Return a stable correlation identifier for command-outcome evidence."""
    return CorrelationId(f"workflow-action:{action.action_id}")
