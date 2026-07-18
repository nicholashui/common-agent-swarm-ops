"""Compile validated, data-only pack graphs into bounded in-process plans."""

from __future__ import annotations

import hashlib
import json
from collections import deque
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType
from typing import Final

from app.models.runs import WorkflowEngineKind
from app.workflows.validator import (
    MAX_HANDOFFS,
    MAX_NODES,
    MAX_TOOL_REQUESTS,
    MAX_WALL_CLOCK_SECONDS,
)

APPROVED_GRAPH_PATTERNS: Final[frozenset[str]] = frozenset(
    {"pipeline", "supervisor", "router", "critique", "map_reduce", "pack_spine"}
)


class GraphCompilationError(ValueError):
    """Raised when raw graph data cannot produce a bounded Host execution plan."""


@dataclass(frozen=True, slots=True)
class GraphExecutionBudget:
    """Immutable per-run limits extracted from a validated graph definition."""

    max_node_visits: int
    max_handoffs: int
    max_wall_clock_seconds: int
    max_tool_requests: int


@dataclass(frozen=True, slots=True)
class CompiledGraphNode:
    """One graph node limited to registered Host-facing data references."""

    node_id: str
    agent_id: str
    declared_tool_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class CompiledGraphEdge:
    """One bounded directed transition between compiled graph nodes."""

    source_node_id: str
    target_node_id: str
    max_traversals: int


@dataclass(frozen=True, slots=True)
class CompiledGraph:
    """A deterministic graph plan with immutable routing metadata."""

    graph_id: str
    pattern: str
    budget: GraphExecutionBudget
    nodes: tuple[CompiledGraphNode, ...]
    node_by_id: Mapping[str, CompiledGraphNode]
    outgoing: Mapping[str, tuple[CompiledGraphEdge, ...]]
    entry_node_id: str
    terminal_node_ids: frozenset[str]


class GraphCompiler:
    """Compile only bounded, permitted graph definitions into Host-owned plans."""

    def compile(self, definition: Mapping[str, object]) -> CompiledGraph:
        """Reject unrecognized graph data before the executor can schedule a node."""
        self._reject_unknown_fields(
            definition,
            {
                "definition_type", "id", "version", "owner_id", "authorization_id", "engine",
                "execution_budget", "memory", "risk_gate_ids", "rollback", "pattern", "nodes",
                "edges", "entry_node", "terminal_node_ids",
            },
            "definition",
        )
        if definition.get("definition_type") != "pack_graph":
            raise GraphCompilationError("graph definitions must be pack_graph definitions")
        if definition.get("engine") != WorkflowEngineKind.GRAPH.value:
            raise GraphCompilationError("graph definitions must select the graph engine")
        pattern = definition.get("pattern")
        if not isinstance(pattern, str) or pattern not in APPROVED_GRAPH_PATTERNS:
            raise GraphCompilationError("graph pattern is not approved")
        budget = self._parse_budget(definition.get("execution_budget"))
        nodes = self._parse_nodes(definition.get("nodes"))
        node_by_id = {node.node_id: node for node in nodes}
        edges, outgoing = self._parse_edges(definition.get("edges"), node_by_id)
        entry_node_id, terminals = self._parse_topology(definition, node_by_id, outgoing)
        self._validate_reachability(entry_node_id, terminals, node_by_id, outgoing, edges)
        graph_id = self._graph_id(definition)
        return CompiledGraph(
            graph_id=graph_id,
            pattern=pattern,
            budget=budget,
            nodes=nodes,
            node_by_id=MappingProxyType(node_by_id),
            outgoing=MappingProxyType(outgoing),
            entry_node_id=entry_node_id,
            terminal_node_ids=frozenset(terminals),
        )


    @staticmethod
    def definition_digest(definition: Mapping[str, object]) -> str:
        """Return the canonical digest used to bind a compiled graph to its run."""
        try:
            normalized = json.dumps(dict(definition), sort_keys=True, separators=(",", ":"))
        except (TypeError, ValueError):
            return ""
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    @classmethod
    def candidate_node_ids(cls, definition: Mapping[str, object]) -> tuple[str, ...]:
        """Return safe node identifiers for failure processing of invalid definitions."""
        raw_nodes = definition.get("nodes")
        if not isinstance(raw_nodes, list):
            return ()
        return tuple(
            node_id
            for raw_node in raw_nodes
            if isinstance(raw_node, Mapping)
            and isinstance((node_id := raw_node.get("id")), str)
            and node_id
        )

    @staticmethod
    def _parse_budget(value: object) -> GraphExecutionBudget:
        if not isinstance(value, Mapping):
            raise GraphCompilationError("graph execution budget must be an object")
        limits = {
            "max_node_visits": (1, MAX_NODES),
            "max_handoffs": (0, MAX_HANDOFFS),
            "max_wall_clock_seconds": (1, MAX_WALL_CLOCK_SECONDS),
            "max_tool_requests": (0, MAX_TOOL_REQUESTS),
        }
        GraphCompiler._reject_unknown_fields(value, set(limits), "execution_budget")
        parsed: dict[str, int] = {}
        for name, (minimum, maximum) in limits.items():
            raw_value = value.get(name)
            if (
                not isinstance(raw_value, int)
                or isinstance(raw_value, bool)
                or not minimum <= raw_value <= maximum
            ):
                raise GraphCompilationError(f"{name} must be {minimum} through {maximum}")
            parsed[name] = raw_value
        return GraphExecutionBudget(**parsed)

    @staticmethod
    def _parse_nodes(value: object) -> tuple[CompiledGraphNode, ...]:
        if not isinstance(value, list) or not 1 <= len(value) <= MAX_NODES:
            raise GraphCompilationError(f"graphs must declare 1 through {MAX_NODES} nodes")
        nodes: list[CompiledGraphNode] = []
        node_ids: set[str] = set()
        for raw_node in value:
            if not isinstance(raw_node, Mapping):
                raise GraphCompilationError("graph nodes must be objects")
            GraphCompiler._reject_unknown_fields(
                raw_node, {"id", "agent_id", "tool_ids", "memory_reads", "memory_writes"}, "node"
            )
            node_id = raw_node.get("id")
            agent_id = raw_node.get("agent_id")
            if (
                not isinstance(node_id, str)
                or not node_id
                or not isinstance(agent_id, str)
                or not agent_id
            ):
                raise GraphCompilationError("graph nodes require non-empty identifiers")
            if node_id in node_ids:
                raise GraphCompilationError("graph node identifiers must be unique")
            tool_ids = GraphCompiler._string_tuple(raw_node.get("tool_ids"), "node tool_ids")
            GraphCompiler._string_tuple(raw_node.get("memory_reads"), "node memory_reads")
            GraphCompiler._string_tuple(raw_node.get("memory_writes"), "node memory_writes")
            node_ids.add(node_id)
            nodes.append(CompiledGraphNode(node_id, agent_id, tool_ids))
        return tuple(nodes)


    @staticmethod
    def _parse_edges(
        value: object, node_by_id: Mapping[str, CompiledGraphNode]
    ) -> tuple[tuple[CompiledGraphEdge, ...], dict[str, tuple[CompiledGraphEdge, ...]]]:
        if not isinstance(value, list):
            raise GraphCompilationError("graph edges must be an array")
        edges: list[CompiledGraphEdge] = []
        seen: set[tuple[str, str]] = set()
        outgoing: dict[str, list[CompiledGraphEdge]] = {node_id: [] for node_id in node_by_id}
        for raw_edge in value:
            if not isinstance(raw_edge, Mapping):
                raise GraphCompilationError("graph edges must be objects")
            GraphCompiler._reject_unknown_fields(raw_edge, {"from", "to", "max_traversals"}, "edge")
            source = raw_edge.get("from")
            target = raw_edge.get("to")
            maximum = raw_edge.get("max_traversals")
            if not isinstance(source, str) or not isinstance(target, str):
                raise GraphCompilationError("graph edges require node identifiers")
            if source not in node_by_id or target not in node_by_id:
                raise GraphCompilationError("graph edges must reference declared nodes")
            if (source, target) in seen:
                raise GraphCompilationError("graph edges must be unique")
            if (
                not isinstance(maximum, int)
                or isinstance(maximum, bool)
                or not 1 <= maximum <= 10
            ):
                raise GraphCompilationError("graph edge max_traversals must be 1 through 10")
            edge = CompiledGraphEdge(source, target, maximum)
            seen.add((source, target))
            edges.append(edge)
            outgoing[source].append(edge)
        return tuple(edges), {node_id: tuple(edges) for node_id, edges in outgoing.items()}

    @staticmethod
    def _parse_topology(
        definition: Mapping[str, object],
        node_by_id: Mapping[str, CompiledGraphNode],
        outgoing: Mapping[str, tuple[CompiledGraphEdge, ...]],
    ) -> tuple[str, tuple[str, ...]]:
        entry_node_id = definition.get("entry_node")
        if not isinstance(entry_node_id, str) or entry_node_id not in node_by_id:
            raise GraphCompilationError("graph entry node must be declared")
        raw_terminals = definition.get("terminal_node_ids")
        terminals = GraphCompiler._string_tuple(raw_terminals, "terminal_node_ids")
        if not terminals or any(node_id not in node_by_id for node_id in terminals):
            raise GraphCompilationError("graph terminal nodes must be declared")
        if any(not outgoing[node_id] for node_id in node_by_id if node_id not in terminals):
            raise GraphCompilationError("non-terminal graph nodes must have an outgoing edge")
        return entry_node_id, terminals

    @staticmethod
    def _validate_reachability(
        entry_node_id: str,
        terminals: Sequence[str],
        node_by_id: Mapping[str, CompiledGraphNode],
        outgoing: Mapping[str, tuple[CompiledGraphEdge, ...]],
        edges: Sequence[CompiledGraphEdge],
    ) -> None:
        adjacency = {
            node_id: tuple(edge.target_node_id for edge in node_edges)
            for node_id, node_edges in outgoing.items()
        }
        reverse: dict[str, list[str]] = {node_id: [] for node_id in node_by_id}
        for edge in edges:
            reverse[edge.target_node_id].append(edge.source_node_id)
        if set(node_by_id) != GraphCompiler._reachable((entry_node_id,), adjacency):
            raise GraphCompilationError("all graph nodes must be reachable from entry")
        reverse_adjacency = {node_id: tuple(sources) for node_id, sources in reverse.items()}
        if set(node_by_id) != GraphCompiler._reachable(terminals, reverse_adjacency):
            raise GraphCompilationError("all graph nodes must reach a terminal node")


    @staticmethod
    def _reachable(
        starts: Sequence[str], adjacency: Mapping[str, Sequence[str]]
    ) -> set[str]:
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
    def _string_tuple(value: object, label: str) -> tuple[str, ...]:
        if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
            raise GraphCompilationError(f"{label} must be an array of non-empty identifiers")
        values = tuple(value)
        if len(values) != len(set(values)):
            raise GraphCompilationError(f"{label} must not contain duplicates")
        return values

    @staticmethod
    def _reject_unknown_fields(
        value: Mapping[str, object], allowed: set[str], location: str
    ) -> None:
        if any(not isinstance(key, str) or key not in allowed for key in value):
            raise GraphCompilationError(f"{location} contains unsupported fields")

    @classmethod
    def _graph_id(cls, definition: Mapping[str, object]) -> str:
        digest = cls.definition_digest(definition)
        if not digest:
            raise GraphCompilationError("graph definition must be serializable")
        return f"graph-{digest[:16]}"
