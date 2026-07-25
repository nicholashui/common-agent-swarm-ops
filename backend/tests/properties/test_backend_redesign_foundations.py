"""Property checks for backend-redesign durable control-plane foundation fakes."""

# ruff: noqa: E501
from __future__ import annotations

from datetime import UTC, datetime

from hypothesis import given, settings, strategies as st

from app.models.common import RecordMetadata
from app.models.control_plane import WorkItem, WorkItemId, WorkState, WorkTransition
from app.models.identifiers import CorrelationId, OrganizationId, RecordId
from app.repositories.control_plane import InMemoryControlPlaneDatabase

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_SAFE_IDENTIFIERS = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyz0123456789-", min_size=1, max_size=20
)


def _metadata(record_id: str, organization_id: OrganizationId) -> RecordMetadata:
    return RecordMetadata(
        record_id=RecordId(record_id),
        organization_id=organization_id,
        correlation_id=CorrelationId("property-correlation"),
        schema_version=1,
        version=1,
        created_at=_NOW,
        updated_at=_NOW,
    )


# Feature: backend-redesign, Property 8: Durable work transitions commit before dispatch/publication.
# **Validates: Requirements 5.2, 5.3**
@settings(max_examples=100, deadline=None)
@given(owner_suffix=_SAFE_IDENTIFIERS, foreign_suffix=_SAFE_IDENTIFIERS, work_suffix=_SAFE_IDENTIFIERS)
def test_property_8_scopes_work_and_retains_append_only_transition_history(
    owner_suffix: str, foreign_suffix: str, work_suffix: str
) -> None:
    """Every foreign read fails while a valid owner retains each immutable work transition."""
    owner = OrganizationId(f"owner-{owner_suffix}")
    foreign = OrganizationId(f"foreign-{foreign_suffix}")
    work_item = WorkItem(
        metadata=_metadata(f"work-record-{work_suffix}", owner),
        work_item_id=WorkItemId(f"work-{work_suffix}"),
        subject_reference="run-property",
        attempt=0,
        idempotency_key="key-property",
        scheduled_at=_NOW,
        cancellation_requested=False,
        state=WorkState.PENDING,
    )

    transition = WorkTransition(
        metadata=_metadata(f"transition-record-{work_suffix}", owner),
        transition_id=f"transition-{work_suffix}",
        work_item_id=work_item.work_item_id,
        from_state=WorkState.PENDING,
        to_state=WorkState.COMPLETE,
        recorded_at=_NOW,
        reason_code="complete",
    )
    database = InMemoryControlPlaneDatabase()

    with database.unit_of_work() as unit_of_work:
        assert unit_of_work.work_items.create(work_item).is_success
        assert unit_of_work.work_items.append_transition(transition).is_success
        owner_history = unit_of_work.work_items.transitions(owner, work_item.work_item_id)
        foreign_work = unit_of_work.work_items.get(foreign, work_item.work_item_id)
        foreign_history = unit_of_work.work_items.transitions(foreign, work_item.work_item_id)

        assert owner_history.is_success and owner_history.value == (transition,)
        assert not foreign_work.is_success
        assert not foreign_history.is_success
