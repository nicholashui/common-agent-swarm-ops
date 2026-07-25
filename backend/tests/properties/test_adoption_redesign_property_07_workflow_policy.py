"""Property checks for declared workflow-policy enforcement at action boundaries."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import NoReturn

from hypothesis import given, settings, strategies as st

from app.models.contracts import Allowed, Blocked, Denied, FailedRecoverable
from app.workflows.policy import (
    ApprovalStatus,
    WorkflowAction,
    WorkflowActionKind,
    WorkflowPolicyBarrier,
)


@dataclass(frozen=True, slots=True)
class _WorkflowPolicyCase:
    """Bounded declarations and policy-breaching action inputs."""

    case_id: int
    node_limit: int
    handoff_limit: int
    tool_limit: int
    wall_limit: int
    read_declared: bool
    write_declared: bool
    approval_authorization_present: bool
    approval_status: ApprovalStatus
    rollback_declared: bool


@dataclass(slots=True)
class _DeterministicEffects:
    """Record effects only when the policy barrier authorizes their execution."""

    completed: list[str] = field(default_factory=list)
    rolled_back: list[str] = field(default_factory=list)

    def complete(self, action_id: str) -> None:
        """Record a completed effect for assertions about the authorization barrier."""
        self.completed.append(action_id)

    def completion_effect(self, action_id: str) -> Callable[[], None]:
        """Return a typed effect callback for one deterministic action."""

        def effect() -> None:
            self.complete(action_id)

        return effect

    def fail(self) -> NoReturn:
        """Raise a deterministic effect failure to exercise declared compensation."""
        raise RuntimeError("deterministic workflow effect failure")

    def rollback(self, action: WorkflowAction) -> bool:
        """Record the action compensated by the declared rollback plan."""
        self.rolled_back.append(action.action_id)
        return True


@dataclass(slots=True)
class _BreachClock:
    """Return zero at barrier creation and the configured elapsed time afterward."""

    elapsed_seconds: float
    reads: int = 0

    def __call__(self) -> float:
        """Supply deterministic monotonic readings without sleeping."""
        value = 0.0 if self.reads == 0 else self.elapsed_seconds
        self.reads += 1
        return value


@st.composite
def _workflow_policy_cases(draw: st.DrawFn) -> _WorkflowPolicyCase:
    """Generate bounded workflow declarations and unmet governance conditions."""
    return _WorkflowPolicyCase(
        case_id=draw(st.integers(min_value=0, max_value=10_000)),
        node_limit=draw(st.integers(min_value=0, max_value=3)),
        handoff_limit=draw(st.integers(min_value=0, max_value=3)),
        tool_limit=draw(st.integers(min_value=0, max_value=3)),
        wall_limit=draw(st.integers(min_value=0, max_value=3)),
        read_declared=draw(st.booleans()),
        write_declared=draw(st.booleans()),
        approval_authorization_present=draw(st.booleans()),
        approval_status=draw(st.sampled_from((ApprovalStatus.PENDING, ApprovalStatus.DENIED))),
        rollback_declared=draw(st.booleans()),
    )


def _generous_budget() -> dict[str, int]:
    """Return limits high enough to isolate non-budget policy checks."""
    return {
        "max_node_visits": 10,
        "max_handoffs": 10,
        "max_tool_requests": 10,
        "max_wall_clock_seconds": 100,
    }


def _definition(
    case: _WorkflowPolicyCase,
    *,
    budget: Mapping[str, int],
    reads: tuple[str, ...] = (),
    writes: tuple[str, ...] = (),
    approval_required: bool = False,
    authorization_id: str | None = None,
    rollback_declared: bool = False,
) -> dict[str, object]:
    """Build one declarative workflow definition consumed by WorkflowPolicyBarrier."""
    definition: dict[str, object] = {
        "id": f"workflow-property-7-{case.case_id}",
        "version": "1.0.0",
        "execution_budget": dict(budget),
        "memory": {"reads": list(reads), "writes": list(writes)},
    }
    if approval_required:
        definition["approval"] = {
            "required": True,
            "required_action_kinds": [WorkflowActionKind.TOOL.value],
        }
    if authorization_id is not None:
        definition["authorization_id"] = authorization_id
    if rollback_declared:
        definition["rollback"] = {
            "plan_id": f"rollback-property-7-{case.case_id}",
            "compensation_step_ids": [f"compensation-property-7-{case.case_id}"],
        }
    return definition


def _assert_budget_breach(
    case: _WorkflowPolicyCase,
    kind: WorkflowActionKind,
    budget_key: str,
    limit: int,
) -> None:
    """Exhaust one declared counter and prove its next effect cannot run."""
    budget = _generous_budget()
    budget[budget_key] = limit
    barrier = WorkflowPolicyBarrier(
        _definition(case, budget=budget),
        clock=lambda: 0.0,
    )
    effects = _DeterministicEffects()

    for index in range(limit):
        action_id = f"accepted-{kind.value}-{index}"
        outcome = barrier.execute_action(
            WorkflowAction(action_id=action_id, kind=kind),
            effects.completion_effect(action_id),
        )
        assert isinstance(outcome, Allowed)

    breach_id = f"breach-{kind.value}"
    breach = barrier.execute_action(
        WorkflowAction(action_id=breach_id, kind=kind),
        effects.completion_effect(breach_id),
    )
    assert isinstance(breach, Denied)
    assert not breach.is_allowed
    assert effects.completed == [f"accepted-{kind.value}-{index}" for index in range(limit)]


# Feature: adoption-redesign, Property 7: Declared workflow policies are enforced at every action
# **Validates: Requirements 3.15**
@settings(max_examples=100, deadline=None)
@given(policy_case=_workflow_policy_cases())
def test_property_7_declared_workflow_policies_are_enforced_at_every_action(
    policy_case: _WorkflowPolicyCase,
) -> None:
    """Every policy breach blocks its effect, while declared rollback compensates failures."""
    for kind, budget_key, limit in (
        (WorkflowActionKind.NODE, "max_node_visits", policy_case.node_limit),
        (WorkflowActionKind.HANDOFF, "max_handoffs", policy_case.handoff_limit),
        (WorkflowActionKind.TOOL, "max_tool_requests", policy_case.tool_limit),
    ):
        _assert_budget_breach(policy_case, kind, budget_key, limit)

    wall_budget = _generous_budget()
    wall_budget["max_wall_clock_seconds"] = policy_case.wall_limit
    wall_barrier = WorkflowPolicyBarrier(
        _definition(policy_case, budget=wall_budget),
        clock=_BreachClock(float(policy_case.wall_limit)),
    )
    wall_effects = _DeterministicEffects()
    wall_action_id = f"breach-wall-{policy_case.case_id}"
    wall_breach = wall_barrier.execute_action(
        WorkflowAction(action_id=wall_action_id, kind=WorkflowActionKind.NODE),
        lambda: wall_effects.complete(wall_action_id),
    )
    assert isinstance(wall_breach, Denied)
    assert not wall_breach.is_allowed
    assert wall_effects.completed == []

    reads = (f"read.scope.{policy_case.case_id}",) if policy_case.read_declared else ()
    writes = (f"write.scope.{policy_case.case_id}",) if policy_case.write_declared else ()
    memory_barrier = WorkflowPolicyBarrier(
        _definition(policy_case, budget=_generous_budget(), reads=reads, writes=writes),
        clock=lambda: 0.0,
    )
    memory_effects = _DeterministicEffects()
    memory_actions = (
        (WorkflowActionKind.MEMORY_READ, reads, "read"),
        (WorkflowActionKind.MEMORY_WRITE, writes, "write"),
    )
    for kind, declared_scopes, label in memory_actions:
        completed_before = list(memory_effects.completed)
        breach_id = f"breach-memory-{label}-{policy_case.case_id}"
        breach = memory_barrier.execute_action(
            WorkflowAction(
                action_id=breach_id,
                kind=kind,
                memory_scope=f"undeclared.{label}.{policy_case.case_id}",
            ),
            memory_effects.completion_effect(breach_id),
        )
        assert isinstance(breach, Denied)
        assert not breach.is_allowed
        assert memory_effects.completed == completed_before

        if declared_scopes:
            allowed_id = f"allowed-memory-{label}-{policy_case.case_id}"
            allowed = memory_barrier.execute_action(
                WorkflowAction(
                    action_id=allowed_id,
                    kind=kind,
                    memory_scope=declared_scopes[0],
                ),
                memory_effects.completion_effect(allowed_id),
            )
            assert isinstance(allowed, Allowed)
            assert memory_effects.completed[-1] == allowed_id

    approval_id = (
        f"authorization-property-7-{policy_case.case_id}"
        if policy_case.approval_authorization_present
        else None
    )
    approval_barrier = WorkflowPolicyBarrier(
        _definition(
            policy_case,
            budget=_generous_budget(),
            approval_required=True,
            authorization_id=approval_id,
        ),
        clock=lambda: 0.0,
    )
    approval_effects = _DeterministicEffects()
    approval_action_id = f"breach-approval-{policy_case.case_id}"
    approval_breach = approval_barrier.execute_action(
        WorkflowAction(
            action_id=approval_action_id,
            kind=WorkflowActionKind.TOOL,
            requires_approval=True,
            approval_id=approval_id,
            approval_status=policy_case.approval_status,
        ),
        lambda: approval_effects.complete(approval_action_id),
    )
    if policy_case.approval_authorization_present:
        expected_approval_type = (
            Blocked if policy_case.approval_status is ApprovalStatus.PENDING else Denied
        )
        assert isinstance(approval_breach, expected_approval_type)
    else:
        assert isinstance(approval_breach, Denied)
    assert not approval_breach.is_allowed
    assert approval_effects.completed == []

    missing_rollback_barrier = WorkflowPolicyBarrier(
        _definition(policy_case, budget=_generous_budget()),
        clock=lambda: 0.0,
    )
    rollback_effects = _DeterministicEffects()
    rollback_action_id = f"breach-rollback-{policy_case.case_id}"
    rollback_breach = missing_rollback_barrier.execute_action(
        WorkflowAction(action_id=rollback_action_id, kind=WorkflowActionKind.ROLLBACK),
        lambda: rollback_effects.complete(rollback_action_id),
    )
    assert isinstance(rollback_breach, Denied)
    assert not rollback_breach.is_allowed
    assert rollback_effects.completed == []

    declared_rollback_effects = _DeterministicEffects()
    declared_rollback_barrier = WorkflowPolicyBarrier(
        _definition(
            policy_case,
            budget=_generous_budget(),
            rollback_declared=policy_case.rollback_declared,
        ),
        rollback=declared_rollback_effects.rollback,
        clock=lambda: 0.0,
    )
    failed_action_id = f"failed-action-{policy_case.case_id}"
    failed_action = WorkflowAction(action_id=failed_action_id, kind=WorkflowActionKind.NODE)
    failed_outcome = declared_rollback_barrier.execute_action(
        failed_action,
        declared_rollback_effects.fail,
    )
    assert isinstance(failed_outcome, FailedRecoverable)
    assert not failed_outcome.is_allowed
    if policy_case.rollback_declared:
        assert declared_rollback_effects.rolled_back == [failed_action_id]
    else:
        assert declared_rollback_effects.rolled_back == []
