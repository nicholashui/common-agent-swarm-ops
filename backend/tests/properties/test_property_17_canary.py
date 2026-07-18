"""Property tests for active canary approved-scope containment."""

from __future__ import annotations

from datetime import UTC, datetime

from hypothesis import given, settings, strategies as st

from app.evolution.models import (
    CanaryId,
    CanaryRecord,
    CanaryScope,
    CanaryState,
    ImprovementDirection,
    RollbackRecord,
    RollbackRecordId,
    RollbackStatus,
    SandboxVariant,
    SandboxVariantId,
    SandboxVariantState,
)
from app.evolution.service import EvolutionService
from app.models.common import RecordMetadata
from app.models.identifiers import ActorId, CorrelationId, OrganizationId, RecordId
from app.repositories.evaluation_repository import InMemoryEvaluationRepository
from app.repositories.evolution_repository import InMemoryEvolutionRepository

# Feature: generic-swarm-business-os, Property 17: Active canaries enforce approved
# scope containment
# **Validates: Requirements 7.9**

NOW = datetime(2025, 1, 1, tzinfo=UTC)
CORRELATION_ID = CorrelationId("property-17")
IDENTIFIER = st.text(alphabet="abcdefghijklmnopqrstuvwxyz0123456789", min_size=1, max_size=8)
OPTIONAL_SCOPE_ID = st.one_of(st.none(), IDENTIFIER)
NARROW_SUBSCOPE = st.one_of(
    st.tuples(IDENTIFIER, st.none()),
    st.tuples(st.none(), IDENTIFIER),
    st.tuples(IDENTIFIER, IDENTIFIER),
)


def _metadata(record_id: str, organization_id: OrganizationId) -> RecordMetadata:
    return RecordMetadata(
        record_id=RecordId(record_id),
        organization_id=organization_id,
        correlation_id=CORRELATION_ID,
        schema_version=1,
        version=1,
        created_at=NOW,
        updated_at=NOW,
    )


def _active_canary_fixture(
    scope: CanaryScope,
) -> tuple[EvolutionService, InMemoryEvolutionRepository, CanaryRecord]:
    """Return an in-memory active record without invoking canary activation."""
    repository = InMemoryEvolutionRepository()
    variant_id = SandboxVariantId("variant-17")
    rollback_id = RollbackRecordId("rollback-17")
    variant = SandboxVariant(
        _metadata("variant-record-17", scope.organization_id),
        variant_id,
        "production-digest",
        "sandbox-digest",
        "{}",
        "quality",
        ImprovementDirection.INCREASE,
        SandboxVariantState.DRAFT,
    )
    rollback = RollbackRecord(
        _metadata("rollback-record-17", scope.organization_id),
        rollback_id,
        variant_id,
        "rollback-digest",
        RollbackStatus.PLANNED,
    )
    canary = CanaryRecord(
        _metadata("canary-record-17", scope.organization_id),
        CanaryId("canary-17"),
        variant_id,
        scope,
        ("quality",),
        (),
        rollback_id,
        CanaryState.ACTIVE,
        ActorId("approver-17"),
        NOW,
    )
    assert repository.create_variant(variant).is_success
    assert repository.create_rollback(rollback).is_success
    assert repository.create_canary(canary).is_success
    return (
        EvolutionService(repository, InMemoryEvaluationRepository(), clock=lambda: NOW),
        repository,
        canary,
    )


@settings(max_examples=100, deadline=None)
@given(
    approved_organization=IDENTIFIER,
    approved_subscope=NARROW_SUBSCOPE,
    requested_organization=IDENTIFIER,
    requested_workflow=OPTIONAL_SCOPE_ID,
    requested_case=OPTIONAL_SCOPE_ID,
)
def test_active_canary_decisions_permit_only_contained_organization_workflow_case_scopes(
    approved_organization: str,
    approved_subscope: tuple[str | None, str | None],
    requested_organization: str,
    requested_workflow: str | None,
    requested_case: str | None,
) -> None:
    """Every authorization decision is true exactly for an approved contained scope."""
    approved_scope = CanaryScope(
        OrganizationId(approved_organization), approved_subscope[0], approved_subscope[1]
    )
    requested_scope = CanaryScope(
        OrganizationId(requested_organization), requested_workflow, requested_case
    )
    service, repository, canary = _active_canary_fixture(approved_scope)

    decision = service.authorize_canary_operation(
        approved_scope.organization_id,
        CORRELATION_ID,
        canary.canary_id,
        requested_scope,
    )
    expected_permitted = approved_scope.contains(requested_scope)

    assert decision.is_success is expected_permitted
    if expected_permitted:
        assert decision.value is True
    else:
        assert decision.error is not None
    retained = repository.get_canary(approved_scope.organization_id, canary.canary_id)
    assert retained.is_success and retained.value == canary
