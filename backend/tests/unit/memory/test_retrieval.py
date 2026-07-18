"""Focused examples for deterministic, scope-contained local retrieval."""

from __future__ import annotations

from datetime import UTC, datetime

from app.memory import (
    InMemoryMemoryRepository,
    KnowledgeRetriever,
    MemoryImpact,
    MemoryScope,
    MemoryScopeType,
    RetrievalRequest,
    RetrievalRequester,
    RetrievalTier,
    ScopedMemory,
)
from app.models.common import SCHEMA_VERSION, RecordMetadata
from app.models.evidence import EvidenceReference
from app.models.identifiers import (
    ActorId,
    CorrelationId,
    EvidenceId,
    OrganizationId,
    RecordId,
)

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_ORGANIZATION_ID = OrganizationId("org-retrieval")
_CORRELATION_ID = CorrelationId("corr-retrieval")


def _memory(
    record_id: str,
    organization_id: OrganizationId,
    scope: MemoryScope,
    content_reference: str,
) -> ScopedMemory:
    """Create a local memory record without an index or external fixture."""
    return ScopedMemory(
        metadata=RecordMetadata(
            record_id=RecordId(record_id),
            organization_id=organization_id,
            correlation_id=_CORRELATION_ID,
            schema_version=SCHEMA_VERSION,
            version=1,
            created_at=_NOW,
            updated_at=_NOW,
        ),
        scope=scope,
        impact=MemoryImpact.LOW,
        writer=ActorId("local.writer"),
        content_reference=content_reference,
        provenance=(
            EvidenceReference(
                evidence_id=EvidenceId(f"evidence-{record_id}"),
                digest=f"digest-{record_id}",
                kind="local-record",
            ),
        ),
        source_log_set_id=f"log-set-{record_id}",
    )


def test_in_scope_miss_returns_explicit_no_knowledge_without_foreign_fallback() -> None:
    """A matching foreign record cannot satisfy an empty requester-scoped retrieval."""
    repository = InMemoryMemoryRepository()
    permitted_scope = MemoryScope(MemoryScopeType.ORGANIZATION, str(_ORGANIZATION_ID))
    foreign_scope = MemoryScope(MemoryScopeType.WORKFLOW, "foreign-workflow")
    local = _memory("local", _ORGANIZATION_ID, permitted_scope, "local unrelated record")
    foreign = _memory("foreign", _ORGANIZATION_ID, foreign_scope, "credential recovery")
    other_organization = _memory(
        "other-org",
        OrganizationId("other-org"),
        permitted_scope,
        "credential recovery",
    )
    for record in (local, foreign, other_organization):
        assert repository.create(record).is_success

    response = KnowledgeRetriever(repository, clock=lambda: _NOW).retrieve(
        RetrievalRequest(
            requester=RetrievalRequester(_ORGANIZATION_ID, (permitted_scope,)),
            query="credential recovery",
        )
    )

    assert response.no_knowledge
    assert response.results == ()
    assert response.searched_tiers == (RetrievalTier.SEMANTIC,)
    assert response.uncertainty == "No permitted knowledge matched within the requester scope."
