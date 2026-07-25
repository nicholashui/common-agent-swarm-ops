"""Focused checks for strict control-plane records and deterministic transactional fakes."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from app.models.common import RecordMetadata
from app.models.control_plane import (
    AgentVersionId,
    CommonAgentVersion,
    ContractStatus,
    WorkItem,
    WorkItemId,
    WorkState,
    WorkTransition,
)
from app.models.identifiers import CorrelationId, OrganizationId, RecordId
from app.repositories.control_plane import InMemoryControlPlaneDatabase

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_ORGANIZATION = OrganizationId("organization-a")
_FOREIGN_ORGANIZATION = OrganizationId("organization-b")


def _metadata(record_id: str, organization_id: OrganizationId = _ORGANIZATION) -> RecordMetadata:
    return RecordMetadata(
        record_id=RecordId(record_id),
        organization_id=organization_id,
        correlation_id=CorrelationId("correlation-1"),
        schema_version=1,
        version=1,
        created_at=_NOW,
        updated_at=_NOW,
    )


def _work_item(work_item_id: str = "work-1") -> WorkItem:
    return WorkItem(
        metadata=_metadata(f"record-{work_item_id}"),
        work_item_id=WorkItemId(work_item_id),
        subject_reference="run-1",
        attempt=0,
        idempotency_key="key-1",
        scheduled_at=_NOW,
        cancellation_requested=False,
        state=WorkState.PENDING,
    )



def _agent_version() -> CommonAgentVersion:
    return CommonAgentVersion(
        metadata=_metadata("agent-record"),
        agent_version_id=AgentVersionId("agent-v1"),
        status=ContractStatus.PUBLISHED,
        canonical_identity="planner",
        category="planning",
        responsibilities=("plan",),
        boundaries=("no-production",),
        escalation_targets=("operator",),
        approval_authority=("approval-1",),
        runtime_policy={"max_retries": 2},
        tool_policy={"allow": "search"},
        quality_rubric={"minimum": 0.8},
        critique_relationships=("reviewer",),
        knowledge_bindings=("knowledge-1",),
        input_schema={"type": "object"},
        output_schema={"type": "object"},
        provenance_policy={"retain": True},
        content_digest="sha256:agent-v1",
    )


def test_published_common_contract_is_frozen_and_append_only() -> None:
    """Published contract policy snapshots cannot be mutated or inserted twice."""
    database = InMemoryControlPlaneDatabase()
    record = _agent_version()

    with pytest.raises(TypeError):
        record.runtime_policy["max_retries"] = 3  # type: ignore[index]

    with database.unit_of_work() as unit_of_work:
        first = unit_of_work.common_contracts.append_agent_version(record)
        duplicate = unit_of_work.common_contracts.append_agent_version(record)

        assert first.is_success and first.value == record
        assert not duplicate.is_success

    with database.unit_of_work() as unit_of_work:
        stored = unit_of_work.common_contracts.get_agent_version(
            _ORGANIZATION, AgentVersionId("agent-v1")
        )

        assert stored.is_success and stored.value == record


def test_protected_lookups_are_organization_scoped() -> None:
    """A foreign organization cannot retrieve a durable protected work record."""
    database = InMemoryControlPlaneDatabase()
    work_item = _work_item()

    with database.unit_of_work() as unit_of_work:
        assert unit_of_work.work_items.create(work_item).is_success
        foreign = unit_of_work.work_items.get(_FOREIGN_ORGANIZATION, work_item.work_item_id)

        assert not foreign.is_success
        assert foreign.error is not None


def test_work_transition_history_is_append_only() -> None:
    """Transition records retain insertion order and reject a duplicate transition identity."""
    database = InMemoryControlPlaneDatabase()
    work_item = _work_item()
    first = WorkTransition(
        metadata=_metadata("transition-record-1"),
        transition_id="transition-1",
        work_item_id=work_item.work_item_id,
        from_state=WorkState.PENDING,
        to_state=WorkState.CLAIMED,
        recorded_at=_NOW,
        reason_code="claimed",
    )
    second = WorkTransition(
        metadata=_metadata("transition-record-2"),
        transition_id="transition-2",
        work_item_id=work_item.work_item_id,
        from_state=WorkState.CLAIMED,
        to_state=WorkState.COMPLETE,
        recorded_at=_NOW,
        reason_code="complete",
    )

    with database.unit_of_work() as unit_of_work:
        assert unit_of_work.work_items.create(work_item).is_success
        assert unit_of_work.work_items.append_transition(first).is_success
        assert unit_of_work.work_items.append_transition(second).is_success
        duplicate = unit_of_work.work_items.append_transition(first)
        history = unit_of_work.work_items.transitions(_ORGANIZATION, work_item.work_item_id)

        assert not duplicate.is_success
        assert history.is_success and history.value == (first, second)



def test_rolled_back_unit_of_work_exposes_no_partial_durable_state() -> None:
    """A transaction rollback keeps a pre-dispatch work item out of shared state."""
    database = InMemoryControlPlaneDatabase()
    work_item = _work_item()

    with database.unit_of_work() as unit_of_work:
        assert unit_of_work.work_items.create(work_item).is_success
        unit_of_work.rollback()

    with database.unit_of_work() as unit_of_work:
        missing = unit_of_work.work_items.get(_ORGANIZATION, work_item.work_item_id)

        assert not missing.is_success
