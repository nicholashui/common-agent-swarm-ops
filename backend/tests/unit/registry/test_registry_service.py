"""Focused deterministic registry-service coverage for immutable common contracts."""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime

from app.models.common import RecordMetadata
from app.models.contracts import ErrorCode
from app.models.control_plane import (
    AgentVersionId,
    CommonAgentVersion,
    CommonContractKind,
    CommonPatternVersion,
    CommonPatternVersionId,
    ContractStatus,
    VulnerabilityMigration,
    VulnerabilityMigrationId,
)
from app.models.identifiers import CorrelationId, OrganizationId, RecordId
from app.registry.service import RegistryService
from app.repositories.control_plane import ControlPlaneUnitOfWork, InMemoryControlPlaneDatabase

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_ORGANIZATION = OrganizationId("registry-organization")
_CORRELATION = CorrelationId("registry-correlation")


def _metadata(record_id: str, version: int = 1) -> RecordMetadata:
    return RecordMetadata(
        record_id=RecordId(record_id),
        organization_id=_ORGANIZATION,
        correlation_id=_CORRELATION,
        schema_version=1,
        version=version,
        created_at=_NOW,
        updated_at=_NOW,
    )


def _agent(
    version_id: str = "agent-published",
    status: ContractStatus = ContractStatus.PUBLISHED,
    record_id: str = "agent-published-record",
) -> CommonAgentVersion:
    return CommonAgentVersion(
        metadata=_metadata(record_id),
        agent_version_id=AgentVersionId(version_id),
        status=status,
        canonical_identity="operations.planner",
        category="planning",
        responsibilities=("plan",),
        boundaries=("no-production",),
        escalation_targets=("operator",),
        approval_authority=("release-approval",),
        runtime_policy={"max_retries": 2},
        tool_policy={"allow": ("knowledge.lookup",)},
        quality_rubric={"minimum": 0.8},
        critique_relationships=("reviewer",),
        knowledge_bindings=("operations-knowledge",),
        input_schema={"type": "object"},
        output_schema={"type": "object"},
        provenance_policy={"retain": True},
        content_digest=f"sha256:{version_id}",
    )


def _pattern(
    version_id: str = "pattern-published",
    status: ContractStatus = ContractStatus.PUBLISHED,
    record_id: str = "pattern-published-record",
) -> CommonPatternVersion:
    return CommonPatternVersion(
        metadata=_metadata(record_id),
        pattern_version_id=CommonPatternVersionId(version_id),
        status=status,
        graph_template={"nodes": ("plan",), "edges": ()},
        slot_constraints={"required": ("planner",)},
        compatibility_rules={"schema": "v1"},
        risk_requirements={"level": "low"},
        verification_requirements={"checks": ("review",)},
        provenance={"source": "registry"},
        content_digest=f"sha256:{version_id}",
    )


def _service() -> tuple[RegistryService, InMemoryControlPlaneDatabase]:
    database = InMemoryControlPlaneDatabase()

    def unit_of_work_factory() -> ControlPlaneUnitOfWork:
        return database.unit_of_work()

    return RegistryService(unit_of_work_factory), database


def test_authorized_draft_updates_replace_only_separately_identified_drafts() -> None:
    """Authorized draft edits replace draft snapshots without changing published sources."""
    service, database = _service()
    published_agent = _agent()
    published_pattern = _pattern()
    agent_draft = _agent("agent-draft", ContractStatus.DRAFT, "agent-draft-record")
    pattern_draft = _pattern("pattern-draft", ContractStatus.DRAFT, "pattern-draft-record")
    updated_agent_draft = replace(
        agent_draft,
        metadata=replace(agent_draft.metadata, version=2),
        responsibilities=("plan", "coordinate"),
        runtime_policy={"max_retries": 3},
        content_digest="sha256:agent-draft-updated",
    )
    updated_pattern_draft = replace(
        pattern_draft,
        metadata=replace(pattern_draft.metadata, version=2),
        compatibility_rules={"schema": "v2"},
        risk_requirements={"level": "medium"},
        content_digest="sha256:pattern-draft-updated",
    )

    assert service.publish_agent(_ORGANIZATION, published_agent).is_success
    assert service.publish_pattern(_ORGANIZATION, published_pattern).is_success
    assert service.create_agent_draft(
        _ORGANIZATION, published_agent.agent_version_id, agent_draft
    ).is_success
    assert service.create_pattern_draft(
        _ORGANIZATION, published_pattern.pattern_version_id, pattern_draft
    ).is_success

    agent_update = service.update_agent_draft(_ORGANIZATION, updated_agent_draft)
    pattern_update = service.update_pattern_draft(_ORGANIZATION, updated_pattern_draft)

    assert agent_update.is_success and agent_update.value == updated_agent_draft
    assert pattern_update.is_success and pattern_update.value == updated_pattern_draft
    with database.unit_of_work() as unit_of_work:
        stored_agent = unit_of_work.common_contracts.get_agent_version(
            _ORGANIZATION, published_agent.agent_version_id
        )
        stored_agent_draft = unit_of_work.common_contracts.get_agent_version(
            _ORGANIZATION, agent_draft.agent_version_id
        )
        stored_pattern = unit_of_work.common_contracts.get_pattern_version(
            _ORGANIZATION, published_pattern.pattern_version_id
        )
        stored_pattern_draft = unit_of_work.common_contracts.get_pattern_version(
            _ORGANIZATION, pattern_draft.pattern_version_id
        )

    assert stored_agent.is_success and stored_agent.value == published_agent
    assert stored_agent_draft.is_success and stored_agent_draft.value == updated_agent_draft
    assert stored_pattern.is_success and stored_pattern.value == published_pattern
    assert stored_pattern_draft.is_success and stored_pattern_draft.value == updated_pattern_draft


def test_published_contract_mutations_are_rejected_without_changing_history() -> None:
    """Published agents and patterns cannot be changed through draft update operations."""
    service, database = _service()
    published_agent = _agent()
    published_pattern = _pattern()
    attempted_agent_change = replace(
        published_agent,
        metadata=replace(published_agent.metadata, version=2),
        responsibilities=("changed",),
    )
    attempted_pattern_change = replace(
        published_pattern,
        metadata=replace(published_pattern.metadata, version=2),
        compatibility_rules={"schema": "changed"},
    )

    assert service.publish_agent(_ORGANIZATION, published_agent).is_success
    assert service.publish_pattern(_ORGANIZATION, published_pattern).is_success

    rejected_agent = service.update_agent_draft(_ORGANIZATION, attempted_agent_change)
    rejected_pattern = service.update_pattern_draft(_ORGANIZATION, attempted_pattern_change)

    assert not rejected_agent.is_success and rejected_agent.error is not None
    assert rejected_agent.error.code is ErrorCode.INVALID_TRANSITION
    assert not rejected_pattern.is_success and rejected_pattern.error is not None
    assert rejected_pattern.error.code is ErrorCode.INVALID_TRANSITION
    with database.unit_of_work() as unit_of_work:
        stored_agent = unit_of_work.common_contracts.get_agent_version(
            _ORGANIZATION, published_agent.agent_version_id
        )
        stored_pattern = unit_of_work.common_contracts.get_pattern_version(
            _ORGANIZATION, published_pattern.pattern_version_id
        )

    assert stored_agent.is_success and stored_agent.value == published_agent
    assert stored_pattern.is_success and stored_pattern.value == published_pattern


def test_vulnerabilities_persist_distinct_patched_versions_and_migration_records() -> None:
    """A vulnerability preserves sources while recording agent and pattern migration targets."""
    service, database = _service()
    source_agent = _agent()
    source_pattern = _pattern()
    patched_agent = _agent("agent-patched", ContractStatus.PUBLISHED, "agent-patched-record")
    patched_pattern = _pattern(
        "pattern-patched", ContractStatus.PUBLISHED, "pattern-patched-record"
    )
    agent_migration = VulnerabilityMigration(
        metadata=_metadata("agent-migration-record"),
        migration_id=VulnerabilityMigrationId("agent-migration"),
        contract_kind=CommonContractKind.AGENT,
        source_version_id=str(source_agent.agent_version_id),
        target_version_id=str(patched_agent.agent_version_id),
        vulnerability_reference="CVE-2025-0001",
    )
    pattern_migration = VulnerabilityMigration(
        metadata=_metadata("pattern-migration-record"),
        migration_id=VulnerabilityMigrationId("pattern-migration"),
        contract_kind=CommonContractKind.PATTERN,
        source_version_id=str(source_pattern.pattern_version_id),
        target_version_id=str(patched_pattern.pattern_version_id),
        vulnerability_reference="CVE-2025-0002",
    )

    assert service.publish_agent(_ORGANIZATION, source_agent).is_success
    assert service.publish_pattern(_ORGANIZATION, source_pattern).is_success
    recorded_agent = service.record_agent_vulnerability(
        _ORGANIZATION, source_agent.agent_version_id, patched_agent, agent_migration
    )
    recorded_pattern = service.record_pattern_vulnerability(
        _ORGANIZATION, source_pattern.pattern_version_id, patched_pattern, pattern_migration
    )

    assert recorded_agent.is_success and recorded_agent.value == agent_migration
    assert recorded_pattern.is_success and recorded_pattern.value == pattern_migration
    with database.unit_of_work() as unit_of_work:
        stored_agent = unit_of_work.common_contracts.get_agent_version(
            _ORGANIZATION, source_agent.agent_version_id
        )
        stored_agent_patch = unit_of_work.common_contracts.get_agent_version(
            _ORGANIZATION, patched_agent.agent_version_id
        )
        stored_pattern = unit_of_work.common_contracts.get_pattern_version(
            _ORGANIZATION, source_pattern.pattern_version_id
        )
        stored_pattern_patch = unit_of_work.common_contracts.get_pattern_version(
            _ORGANIZATION, patched_pattern.pattern_version_id
        )
        stored_agent_migration = unit_of_work.common_contracts.get_vulnerability_migration(
            _ORGANIZATION, agent_migration.migration_id
        )
        stored_pattern_migration = unit_of_work.common_contracts.get_vulnerability_migration(
            _ORGANIZATION, pattern_migration.migration_id
        )

    assert stored_agent.is_success and stored_agent.value == source_agent
    assert stored_agent_patch.is_success and stored_agent_patch.value == patched_agent
    assert stored_pattern.is_success and stored_pattern.value == source_pattern
    assert stored_pattern_patch.is_success and stored_pattern_patch.value == patched_pattern
    assert stored_agent_migration.is_success and stored_agent_migration.value == agent_migration
    assert (
        stored_pattern_migration.is_success and stored_pattern_migration.value == pattern_migration
    )
