"""Property checks for immutable common-contract publication history."""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime
from typing import cast

from hypothesis import given, settings, strategies as st

from app.models.common import RecordMetadata
from app.models.control_plane import (
    AgentVersionId,
    CommonAgentVersion,
    CommonContractKind,
    CommonPatternVersion,
    CommonPatternVersionId,
    ContractStatus,
    GraphRevisionId,
    RunProvenance,
    RunProvenanceId,
    VulnerabilityMigration,
    VulnerabilityMigrationId,
)
from app.models.identifiers import CorrelationId, OrganizationId, RecordId
from app.registry.service import RegistryService
from app.repositories.control_plane import ControlPlaneUnitOfWork, InMemoryControlPlaneDatabase

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_ORGANIZATION = OrganizationId("property-5-organization")
_CORRELATION = CorrelationId("property-5-correlation")
_SAFE_VALUES = st.text(alphabet="abcdefghijklmnopqrstuvwxyz0123456789", min_size=1, max_size=12)


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
    value: str,
    version_id: AgentVersionId,
    status: ContractStatus,
    metadata: RecordMetadata,
) -> CommonAgentVersion:
    return CommonAgentVersion(
        metadata=metadata,
        agent_version_id=version_id,
        status=status,
        canonical_identity=f"agent-{value}",
        category=f"category-{value}",
        responsibilities=(f"responsibility-{value}",),
        boundaries=(f"boundary-{value}",),
        escalation_targets=(f"escalation-{value}",),
        approval_authority=(f"approval-{value}",),
        runtime_policy={"max_retries": 2, "profile": value},
        tool_policy={"allow": (f"tool-{value}",)},
        quality_rubric={"minimum": 0.8, "rubric": value},
        critique_relationships=(f"reviewer-{value}",),
        knowledge_bindings=(f"knowledge-{value}",),
        input_schema={"type": "object", "title": f"input-{value}"},
        output_schema={"type": "object", "title": f"output-{value}"},
        provenance_policy={"retain": True, "source": value},
        content_digest=f"sha256:{version_id}",
    )


def _pattern(
    value: str,
    version_id: CommonPatternVersionId,
    status: ContractStatus,
    metadata: RecordMetadata,
) -> CommonPatternVersion:
    return CommonPatternVersion(
        metadata=metadata,
        pattern_version_id=version_id,
        status=status,
        graph_template={"nodes": (f"node-{value}",), "edges": ()},
        slot_constraints={"required": (f"slot-{value}",)},
        compatibility_rules={"schema": f"schema-{value}"},
        risk_requirements={"level": "low", "owner": value},
        verification_requirements={"checks": (f"verify-{value}",)},
        provenance={"source": value, "retained": True},
        content_digest=f"sha256:{version_id}",
    )


def _unit_of_work_factory(database: InMemoryControlPlaneDatabase) -> ControlPlaneUnitOfWork:
    return cast(ControlPlaneUnitOfWork, database.unit_of_work())


# **Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.8**
# Feature: backend-redesign, Property 5
@settings(max_examples=100)
@given(contract_value=_SAFE_VALUES, edit_value=_SAFE_VALUES, vulnerability_value=_SAFE_VALUES)
def test_property_5_common_contract_publication_preserves_immutable_history(
    contract_value: str, edit_value: str, vulnerability_value: str
) -> None:
    """Published snapshots and prior provenance survive draft edits and patched migrations."""
    database = InMemoryControlPlaneDatabase()
    service = RegistryService(lambda: _unit_of_work_factory(database))

    published_agent = _agent(
        contract_value,
        AgentVersionId(f"agent-published-{contract_value}"),
        ContractStatus.PUBLISHED,
        _metadata(f"agent-published-record-{contract_value}"),
    )
    published_pattern = _pattern(
        contract_value,
        CommonPatternVersionId(f"pattern-published-{contract_value}"),
        ContractStatus.PUBLISHED,
        _metadata(f"pattern-published-record-{contract_value}"),
    )
    agent_snapshot = published_agent
    pattern_snapshot = published_pattern
    provenance_snapshot = RunProvenance(
        metadata=_metadata(f"provenance-record-{contract_value}"),
        run_provenance_id=RunProvenanceId(f"provenance-{contract_value}"),
        graph_revision_id=GraphRevisionId(f"graph-{contract_value}"),
        workflow_definition={"workflow": f"workflow-{contract_value}"},
        workflow_definition_version="1.0.0",
        agent_version_ids=(published_agent.agent_version_id,),
        pattern_version_ids=(published_pattern.pattern_version_id,),
    )

    assert service.publish_agent(_ORGANIZATION, published_agent).is_success
    assert service.publish_pattern(_ORGANIZATION, published_pattern).is_success
    with database.unit_of_work() as unit_of_work:
        assert unit_of_work.provenance.append(provenance_snapshot).is_success

    agent_draft = replace(
        published_agent,
        metadata=_metadata(f"agent-draft-record-{contract_value}"),
        agent_version_id=AgentVersionId(f"agent-draft-{contract_value}"),
        status=ContractStatus.DRAFT,
        content_digest=f"sha256:agent-draft-{contract_value}",
    )
    pattern_draft = replace(
        published_pattern,
        metadata=_metadata(f"pattern-draft-record-{contract_value}"),
        pattern_version_id=CommonPatternVersionId(f"pattern-draft-{contract_value}"),
        status=ContractStatus.DRAFT,
        content_digest=f"sha256:pattern-draft-{contract_value}",
    )
    edited_agent_draft = replace(
        agent_draft,
        metadata=replace(agent_draft.metadata, version=2),
        responsibilities=(f"edited-responsibility-{edit_value}",),
        runtime_policy={"max_retries": 3, "profile": edit_value},
        content_digest=f"sha256:agent-draft-edit-{edit_value}",
    )
    edited_pattern_draft = replace(
        pattern_draft,
        metadata=replace(pattern_draft.metadata, version=2),
        compatibility_rules={"schema": f"edited-schema-{edit_value}"},
        risk_requirements={"level": "medium", "owner": edit_value},
        content_digest=f"sha256:pattern-draft-edit-{edit_value}",
    )

    assert service.create_agent_draft(
        _ORGANIZATION, published_agent.agent_version_id, agent_draft
    ).is_success
    assert service.create_pattern_draft(
        _ORGANIZATION, published_pattern.pattern_version_id, pattern_draft
    ).is_success
    assert service.update_agent_draft(_ORGANIZATION, edited_agent_draft).is_success
    assert service.update_pattern_draft(_ORGANIZATION, edited_pattern_draft).is_success

    patched_agent = replace(
        published_agent,
        metadata=_metadata(f"agent-patch-record-{contract_value}"),
        agent_version_id=AgentVersionId(f"agent-patch-{contract_value}"),
        content_digest=f"sha256:agent-patch-{contract_value}",
    )
    patched_pattern = replace(
        published_pattern,
        metadata=_metadata(f"pattern-patch-record-{contract_value}"),
        pattern_version_id=CommonPatternVersionId(f"pattern-patch-{contract_value}"),
        content_digest=f"sha256:pattern-patch-{contract_value}",
    )
    agent_migration = VulnerabilityMigration(
        metadata=_metadata(f"agent-migration-record-{contract_value}"),
        migration_id=VulnerabilityMigrationId(f"agent-migration-{contract_value}"),
        contract_kind=CommonContractKind.AGENT,
        source_version_id=str(published_agent.agent_version_id),
        target_version_id=str(patched_agent.agent_version_id),
        vulnerability_reference=f"CVE-agent-{vulnerability_value}",
    )
    pattern_migration = VulnerabilityMigration(
        metadata=_metadata(f"pattern-migration-record-{contract_value}"),
        migration_id=VulnerabilityMigrationId(f"pattern-migration-{contract_value}"),
        contract_kind=CommonContractKind.PATTERN,
        source_version_id=str(published_pattern.pattern_version_id),
        target_version_id=str(patched_pattern.pattern_version_id),
        vulnerability_reference=f"CVE-pattern-{vulnerability_value}",
    )

    assert service.record_agent_vulnerability(
        _ORGANIZATION, published_agent.agent_version_id, patched_agent, agent_migration
    ).is_success
    assert service.record_pattern_vulnerability(
        _ORGANIZATION, published_pattern.pattern_version_id, patched_pattern, pattern_migration
    ).is_success

    with database.unit_of_work() as unit_of_work:
        stored_agent = unit_of_work.common_contracts.get_agent_version(
            _ORGANIZATION, published_agent.agent_version_id
        )
        stored_pattern = unit_of_work.common_contracts.get_pattern_version(
            _ORGANIZATION, published_pattern.pattern_version_id
        )
        stored_agent_draft = unit_of_work.common_contracts.get_agent_version(
            _ORGANIZATION, agent_draft.agent_version_id
        )
        stored_pattern_draft = unit_of_work.common_contracts.get_pattern_version(
            _ORGANIZATION, pattern_draft.pattern_version_id
        )
        stored_agent_patch = unit_of_work.common_contracts.get_agent_version(
            _ORGANIZATION, patched_agent.agent_version_id
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
        stored_provenance = unit_of_work.provenance.get(
            _ORGANIZATION, provenance_snapshot.run_provenance_id
        )

    assert stored_agent.is_success and stored_agent.value == agent_snapshot
    assert stored_pattern.is_success and stored_pattern.value == pattern_snapshot
    assert stored_agent_draft.is_success and stored_agent_draft.value == edited_agent_draft
    assert stored_pattern_draft.is_success and stored_pattern_draft.value == edited_pattern_draft
    assert stored_agent_patch.is_success and stored_agent_patch.value == patched_agent
    assert stored_pattern_patch.is_success and stored_pattern_patch.value == patched_pattern
    assert stored_agent_migration.is_success and stored_agent_migration.value == agent_migration
    assert (
        stored_pattern_migration.is_success and stored_pattern_migration.value == pattern_migration
    )
    assert stored_provenance.is_success and stored_provenance.value == provenance_snapshot

    assert (
        len(
            {
                published_agent.agent_version_id,
                agent_draft.agent_version_id,
                patched_agent.agent_version_id,
            }
        )
        == 3
    )
    assert (
        len(
            {
                published_pattern.pattern_version_id,
                pattern_draft.pattern_version_id,
                patched_pattern.pattern_version_id,
            }
        )
        == 3
    )
    assert (
        len(
            {
                published_agent.metadata.record_id,
                agent_draft.metadata.record_id,
                patched_agent.metadata.record_id,
            }
        )
        == 3
    )
    assert (
        len(
            {
                published_pattern.metadata.record_id,
                pattern_draft.metadata.record_id,
                patched_pattern.metadata.record_id,
            }
        )
        == 3
    )
