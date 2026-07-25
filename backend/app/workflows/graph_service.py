"""Organization-scoped graph revision creation and fail-closed validation."""

# ruff: noqa: E501, I001
from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime

from app.models.common import RecordMetadata, utc_now
from app.models.contracts import ErrorCode, ErrorDetail, ErrorField, Result
from app.models.control_plane import (
    AgentVersionId,
    CommonAgentVersion,
    CommonPatternVersion,
    CommonPatternVersionId,
    ContractStatus,
    GraphRevision,
    GraphRevisionId,
    GraphValidationCategory,
    GraphValidationCategoryResult,
    GraphValidationId,
    GraphValidationReport,
    SwarmInstance,
)
from app.models.identifiers import CorrelationId, OrganizationId, new_record_id
from app.repositories.control_plane import ControlPlaneUnitOfWork
from app.repositories.graph_repository import GraphRepository
from app.workflows.graph_validator import GraphDefinitionValidator
from app.workflows.validator import RegisteredReferences, ValidationIssue


_WORKFLOW_POLICY_FIELDS = frozenset(
    {
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
        "entry_node",
        "terminal_node_ids",
    }
)


@dataclass(frozen=True, slots=True)
class _ResolvedVersions:
    agents: Mapping[AgentVersionId, CommonAgentVersion]
    patterns: Mapping[CommonPatternVersionId, CommonPatternVersion]
    issues: tuple[ValidationIssue, ...]


class GraphService:
    """Create immutable revisions and append complete, library-compatible validation evidence."""

    def __init__(
        self,
        unit_of_work_factory: Callable[[], ControlPlaneUnitOfWork],
        graph_repository: GraphRepository,
        registered_references: RegisteredReferences,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._graph_repository = graph_repository
        self._registered_references = registered_references
        self._clock = clock

    def create_revision(
        self,
        organization_id: OrganizationId,
        instance: SwarmInstance,
        revision: GraphRevision,
        expected_revision: int,
    ) -> Result[GraphRevision, ErrorDetail]:
        """Append the supplied next revision only when ownership, version, and custom nodes are safe."""
        invalid = self._creation_issue(organization_id, instance, revision, expected_revision)
        if invalid is not None:
            return Result.failure(invalid)
        existing = self._graph_repository.get_instance(organization_id, instance.swarm_instance_id)
        if not existing.is_success:
            if expected_revision != 0:
                return Result.failure(existing.error or self._not_found(revision))
            created = self._graph_repository.create_instance(instance)
            if not created.is_success:
                return Result.failure(created.error or self._conflict(revision))
        persisted = self._graph_repository.append_revision(revision, expected_revision)
        if not persisted.is_success:
            return Result.failure(persisted.error or self._conflict(revision))
        return Result.success(revision)

    def validate_revision(
        self, organization_id: OrganizationId, graph_revision_id: GraphRevisionId
    ) -> Result[GraphValidationReport, ErrorDetail]:
        """Persist every category result; only a fully validated library definition is run-eligible."""
        revision_result = self._graph_repository.get_revision(organization_id, graph_revision_id)
        if not revision_result.is_success:
            return Result.failure(revision_result.error or self._unknown_revision(graph_revision_id))
        revision = revision_result.value
        assert revision is not None
        resolved = self._resolve_versions(organization_id, revision)
        category_issues: dict[GraphValidationCategory, list[ValidationIssue]] = {
            category: [] for category in GraphValidationCategory
        }
        category_issues[GraphValidationCategory.VERSION_RESOLUTION].extend(resolved.issues)
        workflow_definition = self._workflow_definition(revision, resolved.agents)
        validator_issues = GraphDefinitionValidator(
            self._validator_references(resolved.agents)
        ).validate(workflow_definition).issues
        self._categorize_validator_issues(validator_issues, category_issues)
        category_issues[GraphValidationCategory.SCHEMA_COMPATIBILITY].extend(
            self._schema_compatibility_issues(revision, resolved.agents)
        )
        category_issues[GraphValidationCategory.TOOL_POLICY].extend(
            self._tool_policy_issues(revision, resolved.agents)
        )
        category_issues[GraphValidationCategory.VERIFICATION_POLICY].extend(
            self._verification_policy_issues(revision, resolved.patterns)
        )
        results = tuple(
            GraphValidationCategoryResult(
                category=category,
                passed=not category_issues[category],
                fields=tuple(
                    ErrorField(issue.field, issue.reason) for issue in category_issues[category]
                ),
            )
            for category in GraphValidationCategory
        )
        eligible = all(result.passed for result in results)
        workflow_version = workflow_definition.get("version")
        report = GraphValidationReport(
            metadata=self._validation_metadata(revision),
            graph_validation_id=GraphValidationId(str(new_record_id())),
            graph_revision_id=revision.graph_revision_id,
            categories=results,
            eligible_for_run=eligible,
            workflow_definition=workflow_definition if eligible else None,
            workflow_definition_version=workflow_version if eligible and isinstance(workflow_version, str) else None,
            agent_version_ids=tuple(resolved.agents),
            pattern_version_ids=tuple(resolved.patterns),
        )
        persisted = self._graph_repository.append_validation(report)
        if not persisted.is_success:
            return Result.failure(persisted.error or self._validation_failure(revision))
        return Result.success(report)

    def latest_validation(
        self, organization_id: OrganizationId, graph_revision_id: GraphRevisionId
    ) -> Result[GraphValidationReport, ErrorDetail]:
        """Read the retained eligibility result used by later run-creation orchestration."""
        return self._graph_repository.latest_validation(organization_id, graph_revision_id)

    def _creation_issue(
        self,
        organization_id: OrganizationId,
        instance: SwarmInstance,
        revision: GraphRevision,
        expected_revision: int,
    ) -> ErrorDetail | None:
        if (
            organization_id != instance.metadata.organization_id
            or organization_id != revision.metadata.organization_id
        ):
            return ErrorDetail(
                ErrorCode.AUTHORIZATION_DENIED,
                "The swarm graph is unavailable.",
                revision.metadata.correlation_id,
            )
        if instance.swarm_instance_id != revision.swarm_instance_id:
            return ErrorDetail(
                ErrorCode.VALIDATION_FAILED,
                "The graph revision is invalid.",
                revision.metadata.correlation_id,
                fields=(ErrorField("swarm_instance_id", "must match the owning swarm instance"),),
            )
        if expected_revision < 0:
            return ErrorDetail(
                ErrorCode.VALIDATION_FAILED,
                "The graph revision is invalid.",
                revision.metadata.correlation_id,
                fields=(ErrorField("expected_revision", "must be zero or greater"),),
            )
        if revision.revision != expected_revision + 1:
            return self._conflict(revision)
        custom_fields = self._custom_node_issues(revision.nodes)
        if custom_fields:
            return ErrorDetail(
                ErrorCode.VALIDATION_FAILED,
                "The graph revision is invalid.",
                revision.metadata.correlation_id,
                fields=tuple(ErrorField(issue.field, issue.reason) for issue in custom_fields),
            )
        return None

    def _resolve_versions(
        self, organization_id: OrganizationId, revision: GraphRevision
    ) -> _ResolvedVersions:
        agent_ids, issues = self._pinned_ids(
            revision.version_pins.get("agent_version_ids"), "version_pins.agent_version_ids"
        )
        pattern_ids, pattern_issues = self._pinned_ids(
            revision.version_pins.get("pattern_version_ids"), "version_pins.pattern_version_ids"
        )
        issues.extend(pattern_issues)
        agents: dict[AgentVersionId, CommonAgentVersion] = {}
        patterns: dict[CommonPatternVersionId, CommonPatternVersion] = {}
        with self._unit_of_work_factory() as unit_of_work:
            for agent_id in agent_ids:
                agent_result = unit_of_work.common_contracts.get_agent_version(
                    organization_id, AgentVersionId(agent_id)
                )
                if (
                    not agent_result.is_success
                    or agent_result.value is None
                    or agent_result.value.status is not ContractStatus.PUBLISHED
                ):
                    issues.append(
                        ValidationIssue(
                            "version_pins.agent_version_ids",
                            "must reference a published agent version",
                        )
                    )
                else:
                    agents[agent_result.value.agent_version_id] = agent_result.value
            for pattern_id in pattern_ids:
                pattern_result = unit_of_work.common_contracts.get_pattern_version(
                    organization_id, CommonPatternVersionId(pattern_id)
                )
                if (
                    not pattern_result.is_success
                    or pattern_result.value is None
                    or pattern_result.value.status is not ContractStatus.PUBLISHED
                ):
                    issues.append(
                        ValidationIssue(
                            "version_pins.pattern_version_ids",
                            "must reference a published pattern version",
                        )
                    )
                else:
                    patterns[pattern_result.value.pattern_version_id] = pattern_result.value
        for index, node in enumerate(revision.nodes):
            version_id = node.get("agent_version_id")
            if not isinstance(version_id, str) or AgentVersionId(version_id) not in agents:
                issues.append(
                    ValidationIssue(
                        f"nodes[{index}].agent_version_id",
                        "must reference a pinned published agent version",
                    )
                )
        return _ResolvedVersions(agents=agents, patterns=patterns, issues=tuple(issues))

    @staticmethod
    def _pinned_ids(value: object, field: str) -> tuple[tuple[str, ...], list[ValidationIssue]]:
        if isinstance(value, str) or not isinstance(value, Sequence):
            return (), [ValidationIssue(field, "must be an array of version identifiers")]
        values = tuple(item for item in value if isinstance(item, str) and item.strip())
        issues: list[ValidationIssue] = []
        if len(values) != len(value) or len(values) != len(set(values)):
            issues.append(ValidationIssue(field, "must contain unique non-empty version identifiers"))
        return values, issues

    def _workflow_definition(
        self,
        revision: GraphRevision,
        agents: Mapping[AgentVersionId, CommonAgentVersion],
    ) -> dict[str, object]:
        policy_source = revision.policies.get("workflow_definition", revision.policies)
        source = policy_source if isinstance(policy_source, Mapping) else {}
        definition = {
            key: self._library_value(source[key])
            for key in _WORKFLOW_POLICY_FIELDS
            if key in source
        }
        definition["definition_type"] = "pack_graph"
        definition["nodes"] = [self._workflow_node(node, agents) for node in revision.nodes]
        definition["edges"] = [self._library_value(edge) for edge in revision.edges]
        return definition

    @staticmethod
    def _workflow_node(
        node: Mapping[str, object], agents: Mapping[AgentVersionId, CommonAgentVersion]
    ) -> dict[str, object]:
        workflow_node = {
            key: GraphService._library_value(node[key])
            for key in ("id", "tool_ids", "memory_reads", "memory_writes")
            if key in node
        }
        version_id = node.get("agent_version_id")
        agent = agents.get(AgentVersionId(version_id)) if isinstance(version_id, str) else None
        workflow_node["agent_id"] = agent.canonical_identity if agent is not None else node.get("agent_id", "")
        return workflow_node

    @staticmethod
    def _library_value(value: object) -> object:
        """Convert frozen durable snapshots back to the library's JSON-compatible input shape."""
        if isinstance(value, Mapping):
            return {key: GraphService._library_value(item) for key, item in value.items()}
        if isinstance(value, tuple):
            return [GraphService._library_value(item) for item in value]
        return value

    def _validator_references(
        self, agents: Mapping[AgentVersionId, CommonAgentVersion]
    ) -> RegisteredReferences:
        tool_ids = frozenset(
            tool_id for agent in agents.values() for tool_id in self._allowed_tools(agent)
        )
        return RegisteredReferences(
            agent_ids=frozenset(agent.canonical_identity for agent in agents.values()),
            tool_ids=tool_ids,
            memory_scope_ids=self._registered_references.memory_scope_ids,
            risk_gate_ids=self._registered_references.risk_gate_ids,
            rollback_plan_ids=self._registered_references.rollback_plan_ids,
            authorization_ids=self._registered_references.authorization_ids,
        )

    @staticmethod
    def _categorize_validator_issues(
        issues: Sequence[ValidationIssue],
        categories: dict[GraphValidationCategory, list[ValidationIssue]],
    ) -> None:
        for issue in issues:
            if issue.field == "authorization_id":
                category = GraphValidationCategory.APPROVAL_POLICY
            elif issue.field.startswith("execution_budget"):
                category = GraphValidationCategory.BUDGET_POLICY
            elif issue.field.startswith("rollback"):
                category = GraphValidationCategory.ROLLBACK_POLICY
            elif "tool_ids" in issue.field:
                category = GraphValidationCategory.TOOL_POLICY
            elif issue.field == "risk_gate_ids":
                category = GraphValidationCategory.VERIFICATION_POLICY
            else:
                category = GraphValidationCategory.SCHEMA_COMPATIBILITY
            categories[category].append(issue)

    @staticmethod
    def _schema_compatibility_issues(
        revision: GraphRevision, agents: Mapping[AgentVersionId, CommonAgentVersion]
    ) -> tuple[ValidationIssue, ...]:
        node_agents: dict[str, CommonAgentVersion] = {}
        for node in revision.nodes:
            node_id = node.get("id")
            version_id = node.get("agent_version_id")
            if isinstance(node_id, str) and isinstance(version_id, str):
                agent = agents.get(AgentVersionId(version_id))
                if agent is not None:
                    node_agents[node_id] = agent
        issues: list[ValidationIssue] = []
        for index, edge in enumerate(revision.edges):
            source_id = edge.get("from")
            target_id = edge.get("to")
            source = node_agents.get(source_id) if isinstance(source_id, str) else None
            target = node_agents.get(target_id) if isinstance(target_id, str) else None
            if source is None or target is None:
                continue
            output_type = source.output_schema.get("type")
            input_type = target.input_schema.get("type")
            if (
                isinstance(output_type, str)
                and isinstance(input_type, str)
                and output_type != input_type
                and input_type != "any"
            ):
                issues.append(
                    ValidationIssue(
                        f"edges[{index}]",
                        "source output schema is incompatible with target input schema",
                    )
                )
        return tuple(issues)

    def _tool_policy_issues(
        self, revision: GraphRevision, agents: Mapping[AgentVersionId, CommonAgentVersion]
    ) -> tuple[ValidationIssue, ...]:
        issues: list[ValidationIssue] = []
        for index, node in enumerate(revision.nodes):
            version_id = node.get("agent_version_id")
            agent = agents.get(AgentVersionId(version_id)) if isinstance(version_id, str) else None
            tool_ids = node.get("tool_ids")
            if agent is None or isinstance(tool_ids, str) or not isinstance(tool_ids, Sequence):
                continue
            allowed = self._allowed_tools(agent)
            if any(not isinstance(tool_id, str) or tool_id not in allowed for tool_id in tool_ids):
                issues.append(
                    ValidationIssue(
                        f"nodes[{index}].tool_ids",
                        "must be allowed by the pinned agent tool policy",
                    )
                )
        return tuple(issues)

    @staticmethod
    def _allowed_tools(agent: CommonAgentVersion) -> frozenset[str]:
        values: set[str] = set()
        for key in ("tool_ids", "allowed_tool_ids", "allow"):
            candidate = agent.tool_policy.get(key)
            if isinstance(candidate, str) and candidate:
                values.add(candidate)
            elif isinstance(candidate, Sequence) and not isinstance(candidate, str):
                values.update(value for value in candidate if isinstance(value, str) and value)
        return frozenset(values)

    @staticmethod
    def _verification_policy_issues(
        revision: GraphRevision,
        patterns: Mapping[CommonPatternVersionId, CommonPatternVersion],
    ) -> tuple[ValidationIssue, ...]:
        supplied = revision.policies.get("verification")
        supplied_mapping = supplied if isinstance(supplied, Mapping) else {}
        issues: list[ValidationIssue] = []
        for pattern in patterns.values():
            for key, value in pattern.verification_requirements.items():
                if supplied_mapping.get(key) != value:
                    issues.append(
                        ValidationIssue(
                            f"policies.verification.{key}",
                            "must satisfy the pinned pattern verification requirement",
                        )
                    )
        return tuple(issues)

    @staticmethod
    def _custom_node_issues(nodes: Sequence[Mapping[str, object]]) -> tuple[ValidationIssue, ...]:
        issues: list[ValidationIssue] = []
        for index, node in enumerate(nodes):
            if node.get("node_type") != "custom_agent":
                continue
            fork_origin = node.get("fork_origin")
            custom_reason = node.get("custom_reason")
            has_fork = isinstance(fork_origin, str) and bool(fork_origin.strip())
            has_reason = isinstance(custom_reason, str) and bool(custom_reason.strip())
            if not has_fork and not has_reason:
                issues.append(
                    ValidationIssue(
                        f"nodes[{index}]",
                        "custom agent nodes require a fork origin or custom reason",
                    )
                )
        return tuple(issues)

    def _validation_metadata(self, revision: GraphRevision) -> RecordMetadata:
        timestamp = self._clock()
        return RecordMetadata(
            record_id=new_record_id(),
            organization_id=revision.metadata.organization_id,
            correlation_id=revision.metadata.correlation_id,
            schema_version=revision.metadata.schema_version,
            version=1,
            created_at=timestamp,
            updated_at=timestamp,
        )

    @staticmethod
    def _conflict(revision: GraphRevision) -> ErrorDetail:
        return ErrorDetail(ErrorCode.CONFLICT, "Swarm revision conflict.", revision.metadata.correlation_id)

    @staticmethod
    def _not_found(revision: GraphRevision) -> ErrorDetail:
        return ErrorDetail(ErrorCode.NOT_FOUND, "Swarm instance was not found.", revision.metadata.correlation_id)

    @staticmethod
    def _unknown_revision(graph_revision_id: GraphRevisionId) -> ErrorDetail:
        return ErrorDetail(
            ErrorCode.NOT_FOUND,
            "Graph revision was not found.",
            correlation_id=CorrelationId(f"graph-revision:{graph_revision_id}"),
        )

    @staticmethod
    def _validation_failure(revision: GraphRevision) -> ErrorDetail:
        return ErrorDetail(
            ErrorCode.REPOSITORY_UNAVAILABLE,
            "Graph validation could not be retained.",
            revision.metadata.correlation_id,
            retryable=True,
        )

