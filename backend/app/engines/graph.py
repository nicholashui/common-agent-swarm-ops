"""Bounded in-process graph execution using Host-owned persistence and broker services."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, replace
from time import monotonic
from typing import Protocol, TypeVar

from app.engines.compiler import (
    CompiledGraph,
    CompiledGraphEdge,
    CompiledGraphNode,
    GraphCompilationError,
    GraphCompiler,
    GraphExecutionBudget,
)
from app.engines.protocol import WorkflowEngine
from app.governance.authorization import AuthorizationContext
from app.governance.tool_broker import ToolInvocationResult, ToolRequest
from app.models.common import OptimisticTransition, RecordMetadata, utc_now
from app.models.contracts import ErrorCode, ErrorDetail, Result
from app.models.evidence import EvidenceReference
from app.models.identifiers import CorrelationId, OrganizationId, RunId
from app.models.runs import RunRecord, RunStatus, ToolEffect, WorkflowEngineKind
from app.repositories.protocols import RunRepository
from app.runs.failure_processing import FailureProcessor

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class GraphNodeResult:
    """Safe completion marker returned by a Host-owned graph node implementation."""


class GraphCancellationToken(Protocol):
    """Local cancellation seam checked before the engine schedules every graph node."""

    def cancellation_reason(self) -> str | None:
        """Return a non-empty reason when the current graph must stop scheduling."""


@dataclass(frozen=True, slots=True)
class GraphExecutionMetrics:
    """Observed counters for one bounded in-process graph execution."""

    node_visits: int
    handoffs: int
    tool_requests: int


@dataclass(frozen=True, slots=True)
class GraphExecutionOutcome:
    """Terminal persisted outcome and observed metrics for one graph attempt."""

    record: RunRecord
    completed: bool
    metrics: GraphExecutionMetrics


class GraphExecutionError(RuntimeError):
    """Safe graph execution failure that may preserve Host-generated evidence."""

    def __init__(
        self,
        code: str,
        *,
        evidence_references: tuple[EvidenceReference, ...] = (),
    ) -> None:
        super().__init__(code)
        self.code = code
        self.evidence_references = evidence_references


class GraphToolBroker(Protocol):
    """Host broker capability available to GraphEngine, never directly to graph nodes."""

    def request_tool(
        self, request: ToolRequest, context: AuthorizationContext
    ) -> ToolInvocationResult:
        """Authorize and invoke one deterministic local adapter request."""


class GraphNodeServices(Protocol):
    """The broker-only Host service surface exposed to a graph node."""

    def request_tool(
        self, adapter_id: str, arguments: Mapping[str, object]
    ) -> ToolInvocationResult:
        """Authorize and invoke one declared local tool through the Host broker."""


class GraphNodeExecutor(Protocol):
    """Run one compiled node using only its narrow broker service surface."""

    def execute(
        self,
        run: RunRecord,
        node: CompiledGraphNode,
        services: GraphNodeServices,
    ) -> GraphNodeResult:
        """Perform safe node work and return only a completion marker."""


class _ExecutionBudget:
    """Mutable counters that reject the first attempt to exceed a compiled limit."""

    def __init__(self, limits: GraphExecutionBudget, clock: Callable[[], float]) -> None:
        self._limits = limits
        self._clock = clock
        self._started_at = clock()
        self.node_visits = 0
        self.handoffs = 0
        self.tool_requests = 0

    def check_wall_clock(self) -> None:
        """Reject work once elapsed execution time exceeds the configured limit."""
        if self._clock() - self._started_at > self._limits.max_wall_clock_seconds:
            raise GraphExecutionError("graph_wall_clock_budget_exceeded")

    def consume_node_visit(self) -> None:
        """Reserve the next node visit without allowing a 101st visit."""
        self.check_wall_clock()
        if self.node_visits >= self._limits.max_node_visits:
            raise GraphExecutionError("graph_node_budget_exceeded")
        self.node_visits += 1

    def consume_handoff(self) -> None:
        """Reserve an inter-agent transition without allowing a 13th handoff."""
        self.check_wall_clock()
        if self.handoffs >= self._limits.max_handoffs:
            raise GraphExecutionError("graph_handoff_budget_exceeded")
        self.handoffs += 1

    def consume_tool_request(self) -> None:
        """Reserve a broker request without allowing a 51st tool request."""
        self.check_wall_clock()
        if self.tool_requests >= self._limits.max_tool_requests:
            raise GraphExecutionError("graph_tool_budget_exceeded")
        self.tool_requests += 1

    def metrics(self) -> GraphExecutionMetrics:
        """Return immutable counters suitable for terminal outcome reporting."""
        return GraphExecutionMetrics(self.node_visits, self.handoffs, self.tool_requests)


class _BrokerNodeServices:
    """Broker-only node facade that counts and retains every completed effect."""

    def __init__(
        self,
        run: RunRecord,
        node: CompiledGraphNode,
        broker: GraphToolBroker,
        authorization_context: Callable[[RunRecord, CompiledGraphNode], AuthorizationContext],
        budget: _ExecutionBudget,
    ) -> None:
        self._run = run
        self._node = node
        self._broker = broker
        self._authorization_context = authorization_context
        self._budget = budget
        self._effects: list[ToolEffect] = []

    def request_tool(
        self, adapter_id: str, arguments: Mapping[str, object]
    ) -> ToolInvocationResult:
        """Make one fresh broker request using only Host-derived authorization context."""
        self._budget.consume_tool_request()
        if adapter_id not in self._node.declared_tool_ids:
            raise GraphExecutionError("graph_undeclared_tool_request")
        result = self._broker.request_tool(
            ToolRequest(adapter_id=adapter_id, arguments=arguments),
            self._authorization_context(self._run, self._node),
        )
        if result.effect is not None:
            self._effects.append(result.effect)
        self._budget.check_wall_clock()
        return result

    def drain_effects(self) -> tuple[ToolEffect, ...]:
        """Return every completed effect once for durable retention before later work."""
        effects = tuple(self._effects)
        self._effects.clear()
        return effects


class GraphEngine(WorkflowEngine[GraphExecutionOutcome]):
    """Execute compiled graphs in the Host process with hard per-run bounds."""

    def __init__(
        self,
        repository: RunRepository,
        node_executor: GraphNodeExecutor,
        broker: GraphToolBroker,
        authorization_context: Callable[[RunRecord, CompiledGraphNode], AuthorizationContext],
        *,
        compiler: GraphCompiler | None = None,
        failure_processor: FailureProcessor | None = None,
        cancellation_token: GraphCancellationToken | None = None,
        monotonic_clock: Callable[[], float] = monotonic,
    ) -> None:
        self._repository = repository
        self._node_executor = node_executor
        self._broker = broker
        self._authorization_context = authorization_context
        self._compiler = compiler or GraphCompiler()
        self._failure_processor = failure_processor or FailureProcessor(repository)
        self._cancellation_token = cancellation_token
        self._monotonic_clock = monotonic_clock

    def execute(
        self,
        organization_id: OrganizationId,
        run_id: RunId,
        definition: Mapping[str, object],
        correlation_id: CorrelationId,
    ) -> Result[GraphExecutionOutcome, ErrorDetail]:
        """Compile and execute one dispatched graph without any graph-server boundary."""
        current_result = self._repository.get_by_run_id(organization_id, run_id)
        if not current_result.is_success:
            return Result.failure(self._with_correlation(current_result.error, correlation_id))
        current = self._required_value(current_result)
        if (
            current.engine is not WorkflowEngineKind.GRAPH
            or current.status is not RunStatus.DISPATCHING
        ):
            return Result.failure(
                ErrorDetail(
                    ErrorCode.INVALID_TRANSITION,
                    "GraphEngine executes only an actively dispatched graph run.",
                    correlation_id,
                )
            )
        if not self._definition_matches(current, definition):
            return self._fail(
                current,
                "invalid_graph_definition",
                (),
                self._compiler.candidate_node_ids(definition),
                correlation_id,
                GraphExecutionMetrics(0, 0, 0),
            )

        try:
            graph = self._compiler.compile(definition)
        except GraphCompilationError:
            return self._fail(
                current,
                "invalid_graph_definition",
                (),
                self._compiler.candidate_node_ids(definition),
                correlation_id,
                GraphExecutionMetrics(0, 0, 0),
            )
        initialized = self._initialize_graph_state(current, graph, correlation_id)
        if not initialized.is_success:
            return Result.failure(self._with_correlation(initialized.error, correlation_id))
        return self._run_graph(self._required_value(initialized), graph, correlation_id)

    def _run_graph(
        self,
        current: RunRecord,
        graph: CompiledGraph,
        correlation_id: CorrelationId,
    ) -> Result[GraphExecutionOutcome, ErrorDetail]:
        budget = _ExecutionBudget(graph.budget, self._monotonic_clock)
        current_node_id = graph.entry_node_id
        visited_node_ids: set[str] = set()
        traversals: dict[tuple[str, str], int] = {}
        while True:
            services: _BrokerNodeServices | None = None
            try:
                cancellation_reason = self._cancellation_reason()
                if cancellation_reason is not None:
                    preserved = self._persist_cancellation_state(
                        current,
                        graph,
                        current_node_id,
                        visited_node_ids,
                        cancellation_reason,
                        correlation_id,
                    )
                    if not preserved.is_success:
                        failure = self._with_correlation(preserved.error, correlation_id)
                        return Result.failure(failure)
                    current = self._required_value(preserved)
                    raise GraphExecutionError(cancellation_reason)
                budget.consume_node_visit()
                node = graph.node_by_id[current_node_id]
                visited_node_ids.add(node.node_id)
                services = _BrokerNodeServices(
                    current,
                    node,
                    self._broker,
                    self._authorization_context,
                    budget,
                )
                node_result = self._node_executor.execute(current, node, services)
                if not isinstance(node_result, GraphNodeResult):
                    raise GraphExecutionError("graph_node_result_invalid")
                effects = services.drain_effects()
                if effects:
                    persisted = self._persist_effects(current, effects, correlation_id)
                    if not persisted.is_success:
                        return self._fail(
                            current,
                            "graph_effect_persistence_ambiguous",
                            effects,
                            self._unstarted_node_ids(graph, visited_node_ids),
                            correlation_id,
                            budget.metrics(),
                        )
                    current = self._required_value(persisted)
                budget.check_wall_clock()
                cancellation_reason = self._cancellation_reason()
                if cancellation_reason is not None:
                    preserved = self._persist_cancellation_state(
                        current,
                        graph,
                        current_node_id,
                        visited_node_ids,
                        cancellation_reason,
                        correlation_id,
                    )
                    if not preserved.is_success:
                        failure = self._with_correlation(preserved.error, correlation_id)
                        return Result.failure(failure)
                    current = self._required_value(preserved)
                    raise GraphExecutionError(cancellation_reason)
                if node.node_id in graph.terminal_node_ids:
                    return self._complete(current, correlation_id, budget.metrics())
                edge = self._next_edge(graph, node.node_id, traversals)
                if edge is None:
                    raise GraphExecutionError("graph_terminal_unreachable")
                target = graph.node_by_id[edge.target_node_id]
                if target.agent_id != node.agent_id:
                    budget.consume_handoff()
                traversals[(edge.source_node_id, edge.target_node_id)] = (
                    traversals.get((edge.source_node_id, edge.target_node_id), 0) + 1
                )
                current_node_id = edge.target_node_id
            except GraphExecutionError as error:
                effects = services.drain_effects() if services is not None else ()
                return self._fail(
                    current,
                    error.code,
                    effects,
                    self._unstarted_node_ids(graph, visited_node_ids),
                    correlation_id,
                    budget.metrics(),
                    error.evidence_references,
                )
            except Exception:
                effects = services.drain_effects() if services is not None else ()
                return self._fail(
                    current,
                    "graph_node_failed",
                    effects,
                    self._unstarted_node_ids(graph, visited_node_ids),
                    correlation_id,
                    budget.metrics(),
                )

    def _cancellation_reason(self) -> str | None:
        """Query a local token without exposing it to graph node implementations."""
        if self._cancellation_token is None:
            return None
        reason = self._cancellation_token.cancellation_reason()
        return reason if reason is not None and reason.strip() else None

    def _persist_cancellation_state(
        self,
        current: RunRecord,
        graph: CompiledGraph,
        current_node_id: str,
        visited_node_ids: set[str],
        cancellation_reason: str,
        correlation_id: CorrelationId,
    ) -> Result[RunRecord, ErrorDetail]:
        """Persist an operator-visible graph snapshot before stopping unscheduled work."""
        latest_result = self._repository.get_by_run_id(
            current.metadata.organization_id, current.run_id
        )
        if not latest_result.is_success:
            return Result.failure(self._with_correlation(latest_result.error, correlation_id))
        latest = self._required_value(latest_result)
        output = dict(latest.output or {})
        output["graph_state"] = {
            "graph_id": graph.graph_id,
            "current_node_id": current_node_id,
            "visited_node_ids": sorted(visited_node_ids),
            "unstarted_node_ids": self._unstarted_node_ids(graph, visited_node_ids),
            "interruption": cancellation_reason,
        }
        updated = replace(
            latest,
            metadata=self._next_metadata(latest, correlation_id),
            output=output,
        )
        persisted = self._repository.transition(
            updated, self._transition_for(latest, correlation_id)
        )
        if not persisted.is_success:
            return Result.failure(self._with_correlation(persisted.error, correlation_id))
        return persisted

    def _fail(
        self,
        current: RunRecord,
        code: str,
        effects: Sequence[ToolEffect],
        unstarted_node_ids: Sequence[str],
        correlation_id: CorrelationId,
        metrics: GraphExecutionMetrics,
        evidence_references: Sequence[EvidenceReference] = (),
    ) -> Result[GraphExecutionOutcome, ErrorDetail]:
        """Durably fail without scheduling another graph node after any breach or error."""
        metrics_recorded = self._persist_failure_metrics(current, metrics, correlation_id)
        if not metrics_recorded.is_success:
            return Result.failure(self._with_correlation(metrics_recorded.error, correlation_id))
        failed = self._failure_processor.process(
            self._required_value(metrics_recorded),
            code=code,
            completed_effects=effects,
            evidence_references=evidence_references,
            unstarted_step_ids=unstarted_node_ids,
            correlation_id=correlation_id,
        )
        if not failed.is_success:
            return Result.failure(self._with_correlation(failed.error, correlation_id))
        return Result.success(
            GraphExecutionOutcome(
                self._required_value(failed).record,
                completed=False,
                metrics=metrics,
            )
        )

    def _persist_failure_metrics(
        self,
        current: RunRecord,
        metrics: GraphExecutionMetrics,
        correlation_id: CorrelationId,
    ) -> Result[RunRecord, ErrorDetail]:
        """Persist accepted pre-breach counters before terminal failure processing."""
        updated = replace(
            current,
            metadata=self._next_metadata(current, correlation_id),
            output=self._output_with_metrics(current.output, metrics),
        )
        persisted = self._repository.transition(
            updated, self._transition_for(current, correlation_id)
        )
        if not persisted.is_success:
            return Result.failure(self._with_correlation(persisted.error, correlation_id))
        return persisted

    def _initialize_graph_state(
        self,
        current: RunRecord,
        graph: CompiledGraph,
        correlation_id: CorrelationId,
    ) -> Result[RunRecord, ErrorDetail]:
        """Persist the in-process graph identity before the first node can execute."""
        initialized = replace(
            current,
            metadata=self._next_metadata(current, correlation_id),
            graph_id=graph.graph_id,
            graph_thread_id=f"{current.metadata.organization_id}:{current.run_id}",
        )
        persisted = self._repository.transition(
            initialized, self._transition_for(current, correlation_id)
        )
        if not persisted.is_success:
            return Result.failure(self._with_correlation(persisted.error, correlation_id))
        return persisted

    def _persist_effects(
        self,
        current: RunRecord,
        effects: Sequence[ToolEffect],
        correlation_id: CorrelationId,
    ) -> Result[RunRecord, ErrorDetail]:
        """Retain broker effects before another graph node may execute."""
        updated = replace(
            current,
            metadata=self._next_metadata(current, correlation_id),
            tool_effects=tuple(dict.fromkeys((*current.tool_effects, *effects))),
        )
        persisted = self._repository.transition(
            updated, self._transition_for(current, correlation_id)
        )
        if not persisted.is_success:
            return Result.failure(self._with_correlation(persisted.error, correlation_id))
        return persisted

    def _complete(
        self,
        current: RunRecord,
        correlation_id: CorrelationId,
        metrics: GraphExecutionMetrics,
    ) -> Result[GraphExecutionOutcome, ErrorDetail]:
        """Complete a graph run while retaining its effects and observable counters."""
        completed = replace(
            current,
            metadata=self._next_metadata(current, correlation_id),
            status=RunStatus.COMPLETED,
            output=self._output_with_metrics(current.output, metrics),
        )
        persisted = self._repository.transition(
            completed, self._transition_for(current, correlation_id)
        )
        if not persisted.is_success:
            return Result.failure(self._with_correlation(persisted.error, correlation_id))
        return Result.success(GraphExecutionOutcome(self._required_value(persisted), True, metrics))

    @staticmethod
    def _output_with_metrics(
        output: Mapping[str, object] | None, metrics: GraphExecutionMetrics
    ) -> dict[str, object]:
        """Return the operator-visible metrics retained for a terminal graph outcome."""
        result = dict(output or {})
        result["graph_metrics"] = {
            "node_visits": metrics.node_visits,
            "handoffs": metrics.handoffs,
            "tool_requests": metrics.tool_requests,
        }
        return result


    @staticmethod
    def _definition_matches(run: RunRecord, definition: Mapping[str, object]) -> bool:
        return (
            definition.get("definition_type") == "pack_graph"
            and definition.get("engine") == WorkflowEngineKind.GRAPH.value
            and definition.get("id") == run.workflow_definition_id
            and definition.get("version") == run.workflow_definition_version
            and GraphCompiler.definition_digest(definition) == run.workflow_definition_digest
        )

    @staticmethod
    def _next_edge(
        graph: CompiledGraph,
        source_node_id: str,
        traversals: Mapping[tuple[str, str], int],
    ) -> CompiledGraphEdge | None:
        for edge in graph.outgoing[source_node_id]:
            if traversals.get((edge.source_node_id, edge.target_node_id), 0) < edge.max_traversals:
                return edge
        return None

    @staticmethod
    def _unstarted_node_ids(graph: CompiledGraph, visited_node_ids: set[str]) -> tuple[str, ...]:
        return tuple(node.node_id for node in graph.nodes if node.node_id not in visited_node_ids)

    @staticmethod
    def _next_metadata(record: RunRecord, correlation_id: CorrelationId) -> RecordMetadata:
        return replace(
            record.metadata,
            correlation_id=correlation_id,
            version=record.metadata.version + 1,
            updated_at=utc_now(),
        )

    @staticmethod
    def _transition_for(record: RunRecord, correlation_id: CorrelationId) -> OptimisticTransition:
        return OptimisticTransition(
            record_id=record.metadata.record_id,
            organization_id=record.metadata.organization_id,
            expected_version=record.metadata.version,
            correlation_id=correlation_id,
        )

    @staticmethod
    def _with_correlation(
        error: ErrorDetail | None, correlation_id: CorrelationId
    ) -> ErrorDetail:
        if error is None:
            return ErrorDetail(
                ErrorCode.REPOSITORY_UNAVAILABLE,
                "Run storage is unavailable during graph execution.",
                correlation_id,
            )
        return ErrorDetail(
            error.code,
            error.message,
            correlation_id,
            retryable=error.retryable,
            fields=error.fields,
        )

    @staticmethod
    def _required_value(result: Result[T, ErrorDetail]) -> T:
        if result.value is None:
            raise RuntimeError("A successful result did not contain its expected value.")
        return result.value
