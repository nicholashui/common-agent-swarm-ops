"""Validation for data-only, bounded pack graph definitions."""

from __future__ import annotations

from collections import deque
from collections.abc import Mapping, Sequence
from typing import Final

from app.models.runs import WorkflowEngineKind
from app.workflows.validator import (
    MAX_NODES,
    DefinitionValidationError,
    RegisteredReferences,
    ValidationIssue,
    ValidationReport,
    WorkflowDefinitionValidator,
)

_ALLOWED_PATTERNS: Final[frozenset[str]] = frozenset(
    {"pipeline", "supervisor", "router", "critique", "map_reduce", "pack_spine"}
)
MAX_LOOP_ITERATIONS: Final[int] = 10


class GraphDefinitionValidator:
    """Reject pack graphs that could bypass registered Host controls or bounds."""

    def __init__(self, registered_references: RegisteredReferences) -> None:
        self._registered_references = registered_references

    def validate(self, definition: Mapping[str, object]) -> ValidationReport:
        """Return all deterministic failures without compiling or executing the graph."""
        issues: list[ValidationIssue] = []
        declared_reads, declared_writes = WorkflowDefinitionValidator.validate_common_fields(
            definition, self._registered_references, issues, "pack_graph"
        )
        self._validate_pattern(definition, issues)
        nodes = self._validate_nodes(definition, declared_reads, declared_writes, issues)
        self._validate_edges(definition, nodes, issues)
        WorkflowDefinitionValidator._validate_rollback(
            definition.get("rollback"), nodes, self._registered_references.rollback_plan_ids, issues
        )
        self._reject_unknown_fields(definition, issues)
        return ValidationReport(tuple(issues))

    def validate_or_reject(self, definition: Mapping[str, object]) -> None:
        """Raise before run creation, compilation, dispatch, adapter calls, or effects."""
        report = self.validate(definition)
        if not report.is_valid:
            raise DefinitionValidationError(report)

    def _validate_pattern(
        self, definition: Mapping[str, object], issues: list[ValidationIssue]
    ) -> None:
        pattern = definition.get("pattern")
        if pattern not in _ALLOWED_PATTERNS:
            issues.append(ValidationIssue("pattern", "must be a permitted graph pattern"))
        if definition.get("engine") != WorkflowEngineKind.GRAPH:
            issues.append(ValidationIssue("engine", "pack graphs require the graph engine"))

    def _validate_nodes(
        self,
        definition: Mapping[str, object],
        declared_reads: frozenset[str],
        declared_writes: frozenset[str],
        issues: list[ValidationIssue],
    ) -> frozenset[str]:
        raw_nodes = definition.get("nodes")
        if not isinstance(raw_nodes, list) or not 1 <= len(raw_nodes) <= MAX_NODES:
            issues.append(ValidationIssue("nodes", f"must contain 1 through {MAX_NODES} nodes"))
            return frozenset()
        node_ids: set[str] = set()
        for index, raw_node in enumerate(raw_nodes):
            field = f"nodes[{index}]"
            if not isinstance(raw_node, Mapping):
                issues.append(ValidationIssue(field, "must be an object"))
                continue
            WorkflowDefinitionValidator._reject_unknown_fields(
                raw_node,
                frozenset({"id", "agent_id", "tool_ids", "memory_reads", "memory_writes"}),
                issues,
                field,
            )
            node_id = raw_node.get("id")
            WorkflowDefinitionValidator._validate_identifier(node_id, f"{field}.id", issues)
            if isinstance(node_id, str):
                if node_id in node_ids:
                    issues.append(ValidationIssue(f"{field}.id", "must be unique"))
                node_ids.add(node_id)
            WorkflowDefinitionValidator._validate_registered_identifier(
                raw_node.get("agent_id"),
                f"{field}.agent_id",
                self._registered_references.agent_ids,
                issues,
            )
            WorkflowDefinitionValidator._validate_step_access(
                raw_node,
                field,
                declared_reads,
                declared_writes,
                self._registered_references,
                issues,
            )
        return frozenset(node_ids)

    def _validate_edges(
        self,
        definition: Mapping[str, object],
        node_ids: frozenset[str],
        issues: list[ValidationIssue],
    ) -> None:
        raw_edges = definition.get("edges")
        if not isinstance(raw_edges, list):
            issues.append(ValidationIssue("edges", "must be an array"))
            return
        adjacency: dict[str, set[str]] = {node_id: set() for node_id in node_ids}
        reverse_adjacency: dict[str, set[str]] = {
            node_id: set() for node_id in node_ids
        }
        edge_pairs: set[tuple[str, str]] = set()
        for index, raw_edge in enumerate(raw_edges):
            field = f"edges[{index}]"
            if not isinstance(raw_edge, Mapping):
                issues.append(ValidationIssue(field, "must be an object"))
                continue
            WorkflowDefinitionValidator._reject_unknown_fields(
                raw_edge, frozenset({"from", "to", "max_traversals"}), issues, field
            )
            source = raw_edge.get("from")
            target = raw_edge.get("to")
            WorkflowDefinitionValidator._validate_identifier(source, f"{field}.from", issues)
            WorkflowDefinitionValidator._validate_identifier(target, f"{field}.to", issues)
            max_traversals = raw_edge.get("max_traversals")
            if (
                not isinstance(max_traversals, int)
                or isinstance(max_traversals, bool)
                or not 1 <= max_traversals <= MAX_LOOP_ITERATIONS
            ):
                issues.append(
                    ValidationIssue(
                        f"{field}.max_traversals", f"must be 1 through {MAX_LOOP_ITERATIONS}"
                    )
                )
            if isinstance(source, str) and isinstance(target, str):
                if source not in node_ids or target not in node_ids:
                    issues.append(ValidationIssue(field, "must connect declared nodes"))
                    continue
                if (source, target) in edge_pairs:
                    issues.append(ValidationIssue(field, "must not duplicate an edge"))
                    continue
                edge_pairs.add((source, target))
                adjacency[source].add(target)
                reverse_adjacency[target].add(source)
        self._validate_topology(definition, node_ids, adjacency, reverse_adjacency, issues)

    def _validate_topology(
        self,
        definition: Mapping[str, object],
        node_ids: frozenset[str],
        adjacency: Mapping[str, set[str]],
        reverse_adjacency: Mapping[str, set[str]],
        issues: list[ValidationIssue],
    ) -> None:
        entry_node = definition.get("entry_node")
        WorkflowDefinitionValidator._validate_identifier(entry_node, "entry_node", issues)
        if not isinstance(entry_node, str) or entry_node not in node_ids:
            issues.append(ValidationIssue("entry_node", "must reference a declared node"))
            return
        terminal_nodes = WorkflowDefinitionValidator._string_list(
            definition.get("terminal_node_ids"), "terminal_node_ids", issues
        )
        if terminal_nodes is None or not terminal_nodes:
            issues.append(
                ValidationIssue("terminal_node_ids", "must declare at least one terminal node")
            )
            return
        if any(node_id not in node_ids for node_id in terminal_nodes):
            issues.append(ValidationIssue("terminal_node_ids", "must reference declared nodes"))
            return
        reached = self._reachable((entry_node,), adjacency)
        if node_ids - reached:
            issues.append(
                ValidationIssue("edges", "must make every node reachable from entry_node")
            )
        can_reach_terminal = self._reachable(terminal_nodes, reverse_adjacency)
        if node_ids - can_reach_terminal:
            issues.append(
                ValidationIssue("edges", "must allow every node to reach a terminal node")
            )

    @staticmethod
    def _reachable(starts: Sequence[str], adjacency: Mapping[str, set[str]]) -> set[str]:
        pending: deque[str] = deque(starts)
        reached: set[str] = set()
        while pending:
            node_id = pending.popleft()
            if node_id in reached:
                continue
            reached.add(node_id)
            pending.extend(adjacency.get(node_id, ()))
        return reached

    @staticmethod
    def _reject_unknown_fields(
        definition: Mapping[str, object], issues: list[ValidationIssue]
    ) -> None:
        WorkflowDefinitionValidator._reject_unknown_fields(
            definition,
            frozenset(
                {
                    "definition_type",
                    "id",
                    "version",
                    "owner_id",
                    "authorization_id",
                    "engine",
                    "execution_budget",
                    "memory",
                    "risk_gate_ids",
                    "rollback",
                    "pattern",
                    "nodes",
                    "edges",
                    "entry_node",
                    "terminal_node_ids",
                }
            ),
            issues,
        )
