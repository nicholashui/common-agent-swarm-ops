"""Focused checks for pure WorkflowDNA and pack-graph validation."""

from __future__ import annotations

from copy import deepcopy

import pytest

from app.workflows import (
    DefinitionValidationError,
    GraphDefinitionValidator,
    RegisteredReferences,
    WorkflowDefinitionValidator,
)


@pytest.fixture
def references() -> RegisteredReferences:
    """Return the Host-owned registries that valid local fixtures may reference."""
    return RegisteredReferences(
        agent_ids=frozenset({"ops.planner", "ops.reviewer"}),
        tool_ids=frozenset({"audit.log", "crm.lookup"}),
        memory_scope_ids=frozenset({"organization", "workflow"}),
        risk_gate_ids=frozenset({"low-risk"}),
        rollback_plan_ids=frozenset({"compensate.crm"}),
        authorization_ids=frozenset({"approval-123"}),
    )


@pytest.fixture
def valid_dna() -> dict[str, object]:
    """Return a bounded definition with only registered references."""
    return {
        "definition_type": "workflow_dna",
        "id": "ops.onboarding",
        "version": "1.0.0",
        "owner_id": "ops.owner",
        "authorization_id": "approval-123",
        "engine": "legacy",
        "execution_budget": {
            "max_node_visits": 2,
            "max_handoffs": 1,
            "max_wall_clock_seconds": 30,
            "max_tool_requests": 2,
        },
        "memory": {"reads": ["organization", "workflow"], "writes": ["workflow"]},
        "risk_gate_ids": ["low-risk"],
        "rollback": {"plan_id": "compensate.crm", "compensation_step_ids": ["review"]},
        "steps": [
            {
                "id": "review",
                "agent_id": "ops.planner",
                "tool_ids": ["crm.lookup"],
                "memory_reads": ["organization"],
                "memory_writes": ["workflow"],
            }
        ],
    }


def test_valid_dna_is_accepted_without_execution(
    references: RegisteredReferences, valid_dna: dict[str, object]
) -> None:
    """A fully declared, bounded workflow passes the pre-execution gate."""
    report = WorkflowDefinitionValidator(references).validate(valid_dna)

    assert report.is_valid
    WorkflowDefinitionValidator(references).validate_or_reject(valid_dna)


@pytest.mark.parametrize(
    ("path", "value", "expected_field"),
    [
        (("authorization_id",), "missing-approval", "authorization_id"),
        (("engine",), "remote", "engine"),
        (("execution_budget", "max_node_visits"), 101, "execution_budget.max_node_visits"),
        (("steps", 0, "tool_ids"), ["unregistered.tool"], "steps[0].tool_ids"),
        (("rollback", "plan_id"), "missing-plan", "rollback.plan_id"),
        (("steps", 0, "memory_reads"), ["foreign-scope"], "steps[0].memory_reads"),
    ],
)
def test_invalid_dna_is_rejected_before_a_lifecycle_operation(
    references: RegisteredReferences,
    valid_dna: dict[str, object],
    path: tuple[str | int, ...],
    value: object,
    expected_field: str,
) -> None:
    """Every unbounded or unregistered declaration fails the explicit reject gate."""
    invalid_definition = deepcopy(valid_dna)
    target: object = invalid_definition
    for part in path[:-1]:
        target = target[part]  # type: ignore[index]
    target[path[-1]] = value  # type: ignore[index]

    validator = WorkflowDefinitionValidator(references)
    report = validator.validate(invalid_definition)

    assert not report.is_valid
    assert any(issue.field == expected_field for issue in report.issues)
    with pytest.raises(DefinitionValidationError):
        validator.validate_or_reject(invalid_definition)


@pytest.fixture
def valid_graph(valid_dna: dict[str, object]) -> dict[str, object]:
    """Return a reachable, bounded graph using only declared Host references."""
    definition = deepcopy(valid_dna)
    definition.update(
        {
            "definition_type": "pack_graph",
            "engine": "graph",
            "pattern": "pipeline",
            "nodes": [
                {
                    "id": "plan",
                    "agent_id": "ops.planner",
                    "tool_ids": ["crm.lookup"],
                    "memory_reads": ["organization"],
                    "memory_writes": ["workflow"],
                },
                {
                    "id": "review",
                    "agent_id": "ops.reviewer",
                    "tool_ids": ["audit.log"],
                    "memory_reads": ["workflow"],
                    "memory_writes": ["workflow"],
                },
            ],
            "edges": [{"from": "plan", "to": "review", "max_traversals": 1}],
            "entry_node": "plan",
            "terminal_node_ids": ["review"],
        }
    )
    definition.pop("steps")
    return definition


def test_valid_pack_graph_is_accepted(
    references: RegisteredReferences, valid_graph: dict[str, object]
) -> None:
    """A permitted graph has bounded edges and a complete topology."""
    report = GraphDefinitionValidator(references).validate(valid_graph)

    assert report.is_valid


@pytest.mark.parametrize(
    ("path", "value", "expected_field"),
    [
        (("pattern",), "unbounded", "pattern"),
        (("edges", 0, "max_traversals"), 11, "edges[0].max_traversals"),
        (("entry_node",), "missing-node", "entry_node"),
    ],
)
def test_invalid_pack_graph_is_rejected(
    references: RegisteredReferences,
    valid_graph: dict[str, object],
    path: tuple[str | int, ...],
    value: object,
    expected_field: str,
) -> None:
    """Invalid patterns, traversal bounds, and topology never pass the graph gate."""
    invalid_definition = deepcopy(valid_graph)
    target: object = invalid_definition
    for part in path[:-1]:
        target = target[part]  # type: ignore[index]
    target[path[-1]] = value  # type: ignore[index]

    validator = GraphDefinitionValidator(references)
    report = validator.validate(invalid_definition)

    assert not report.is_valid
    assert any(issue.field == expected_field for issue in report.issues)
    with pytest.raises(DefinitionValidationError):
        validator.validate_or_reject(invalid_definition)
