"""Property tests for semantic-first, scope-contained knowledge retrieval."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from hypothesis import example, given, settings, strategies as st

from app.memory import (
    InMemoryMemoryRepository,
    KnowledgeRetriever,
    MemoryImpact,
    MemoryScope,
    MemoryScopeType,
    RetrievalConfiguration,
    RetrievalMatch,
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

# Feature: generic-swarm-business-os, Property 7: Retrieval is semantic-first and cannot
# disclose across scope.
# **Validates: Requirements 3.6, 3.7**

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_ORGANIZATION_ID = OrganizationId("org-property-7")
_FOREIGN_ORGANIZATION_ID = OrganizationId("org-property-7-foreign")
_CORRELATION_ID = CorrelationId("corr-property-7")
_QUERY = "scoped-query-token"


@dataclass(frozen=True, slots=True)
class RetrievalCase:
    """One bounded local-corpus/query configuration for Property 7."""

    local_match_tier: RetrievalTier | None
    requires_relationships: bool
    relationship_enabled: bool
    synthesis_enabled: bool
    approved_record_count: int
    foreign_record_count: int
    scope_type: MemoryScopeType
    result_limit: int


@dataclass(frozen=True, slots=True)
class ScopedCorpus:
    """An in-memory corpus containing permitted and deliberately foreign records."""

    requester: RetrievalRequester
    approved_records: tuple[ScopedMemory, ...]
    foreign_records: tuple[ScopedMemory, ...]


@dataclass(slots=True)
class RecordingTierFake:
    """Deterministic local tier seam that always attempts foreign disclosure first."""

    tier: RetrievalTier
    local_match_tier: RetrievalTier | None
    foreign_matches: tuple[RetrievalMatch, ...]
    calls: list[RetrievalTier] = field(default_factory=list)
    candidate_record_ids: list[tuple[RecordId, ...]] = field(default_factory=list)

    def __call__(
        self,
        request: RetrievalRequest,
        candidates: tuple[ScopedMemory, ...],
    ) -> tuple[RetrievalMatch, ...]:
        """Return foreign matches plus a local match only for the configured tier."""
        del request
        self.calls.append(self.tier)
        self.candidate_record_ids.append(
            tuple(record.metadata.record_id for record in candidates)
        )
        if self.local_match_tier is self.tier and candidates:
            return (*self.foreign_matches, _match(candidates[0]))
        return self.foreign_matches


@st.composite
def _retrieval_cases(draw: st.DrawFn) -> RetrievalCase:
    """Generate bounded scope, tier, corpus, and query-control dimensions."""
    return RetrievalCase(
        local_match_tier=draw(
            st.sampled_from((None, RetrievalTier.SEMANTIC, RetrievalTier.RELATIONSHIP,
                            RetrievalTier.SYNTHESIS))
        ),
        requires_relationships=draw(st.booleans()),
        relationship_enabled=draw(st.booleans()),
        synthesis_enabled=draw(st.booleans()),
        approved_record_count=draw(st.integers(min_value=1, max_value=3)),
        foreign_record_count=draw(st.integers(min_value=1, max_value=3)),
        scope_type=draw(st.sampled_from(tuple(MemoryScopeType))),
        result_limit=draw(st.integers(min_value=1, max_value=3)),
    )


def _memory(
    record_id: str,
    organization_id: OrganizationId,
    scope: MemoryScope,
    content_reference: str,
) -> ScopedMemory:
    """Create one deterministic, provenance-bearing local memory record."""
    provenance = EvidenceReference(
        evidence_id=EvidenceId(f"evidence-{record_id}"),
        digest=f"digest-{record_id}",
        kind=f"local-source-{record_id}",
    )
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
        writer=ActorId("property-7-retriever"),
        content_reference=content_reference,
        provenance=(provenance,),
        source_log_set_id=f"log-set-{record_id}",
    )


def _corpus(case: RetrievalCase) -> tuple[InMemoryMemoryRepository, ScopedCorpus]:
    """Store a bounded corpus with both same-org and cross-org foreign records."""
    repository = InMemoryMemoryRepository()
    approved_scope = MemoryScope(case.scope_type, "approved-scope-property-7")
    foreign_scope = MemoryScope(case.scope_type, "foreign-scope-property-7")
    approved_records = tuple(
        _memory(
            f"approved-{index}",
            _ORGANIZATION_ID,
            approved_scope,
            f"approved {_QUERY}" if index == 0 and case.local_match_tier is RetrievalTier.SEMANTIC
            else f"approved-unrelated-{index}",
        )
        for index in range(case.approved_record_count)
    )
    foreign_records = tuple(
        _memory(
            f"foreign-{index}",
            _ORGANIZATION_ID if index % 2 == 0 else _FOREIGN_ORGANIZATION_ID,
            foreign_scope if index % 2 == 0 else approved_scope,
            f"foreign {_QUERY} {index}",
        )
        for index in range(case.foreign_record_count)
    )
    for record in (*approved_records, *foreign_records):
        stored = repository.create(record)
        assert stored.is_success
    return repository, ScopedCorpus(
        requester=RetrievalRequester(_ORGANIZATION_ID, (approved_scope,)),
        approved_records=approved_records,
        foreign_records=foreign_records,
    )


def _match(record: ScopedMemory) -> RetrievalMatch:
    """Project a valid retrieval seam match from a local corpus record."""
    return RetrievalMatch(
        content_reference=record.content_reference,
        source_record_ids=(record.metadata.record_id,),
        provenance=record.provenance,
        confidence=1.0,
    )


def _expected_tier(case: RetrievalCase) -> RetrievalTier | None:
    """Resolve which permitted local tier, if any, can return knowledge."""
    if case.local_match_tier is RetrievalTier.SEMANTIC:
        return RetrievalTier.SEMANTIC
    if (
        case.local_match_tier is RetrievalTier.RELATIONSHIP
        and case.requires_relationships
        and case.relationship_enabled
    ):
        return RetrievalTier.RELATIONSHIP
    if case.local_match_tier is RetrievalTier.SYNTHESIS and case.synthesis_enabled:
        return RetrievalTier.SYNTHESIS
    return None


def _expected_searched_tiers(case: RetrievalCase) -> tuple[RetrievalTier, ...]:
    """Derive the strict tier sequence for the bounded local case."""
    tiers = [RetrievalTier.SEMANTIC]
    if case.local_match_tier is RetrievalTier.SEMANTIC:
        return tuple(tiers)
    if case.requires_relationships and case.relationship_enabled:
        tiers.append(RetrievalTier.RELATIONSHIP)
        if case.local_match_tier is RetrievalTier.RELATIONSHIP:
            return tuple(tiers)
    if case.synthesis_enabled:
        tiers.append(RetrievalTier.SYNTHESIS)
    return tuple(tiers)


@settings(max_examples=100, deadline=None, derandomize=True)
@example(
    case=RetrievalCase(
        RetrievalTier.SEMANTIC, True, True, True, 1, 2, MemoryScopeType.WORKFLOW, 1
    )
)
@example(
    case=RetrievalCase(
        RetrievalTier.RELATIONSHIP, True, True, True, 2, 2, MemoryScopeType.AGENT, 2
    )
)
@example(
    case=RetrievalCase(
        RetrievalTier.SYNTHESIS, True, True, True, 3, 3, MemoryScopeType.ORGANIZATION, 3
    )
)
@example(
    case=RetrievalCase(None, True, True, True, 1, 3, MemoryScopeType.WORKFLOW, 1)
)
@given(case=_retrieval_cases())
def test_retrieval_is_semantic_first_and_cannot_disclose_across_scope(
    case: RetrievalCase,
) -> None:
    """Permitted retrieval is ordered, provenanced, and contained to requester scope."""
    repository, corpus = _corpus(case)
    foreign_matches = tuple(_match(record) for record in corpus.foreign_records)
    relationship = RecordingTierFake(
        RetrievalTier.RELATIONSHIP, case.local_match_tier, foreign_matches
    )
    synthesis = RecordingTierFake(RetrievalTier.SYNTHESIS, case.local_match_tier, foreign_matches)
    retriever = KnowledgeRetriever(
        repository,
        RetrievalConfiguration(case.relationship_enabled, case.synthesis_enabled),
        relationship,
        synthesis,
        clock=lambda: _NOW,
    )

    response = retriever.retrieve(
        RetrievalRequest(
            requester=corpus.requester,
            query=_QUERY,
            requires_relationships=case.requires_relationships,
            result_limit=case.result_limit,
        )
    )

    expected_tier = _expected_tier(case)
    assert response.searched_tiers == _expected_searched_tiers(case)
    assert relationship.calls + synthesis.calls == list(response.searched_tiers[1:])

    approved_ids = {record.metadata.record_id for record in corpus.approved_records}
    foreign_ids = {record.metadata.record_id for record in corpus.foreign_records}
    for fake in (relationship, synthesis):
        assert all(
            set(candidate_ids) == approved_ids for candidate_ids in fake.candidate_record_ids
        )

    if expected_tier is None:
        assert response.no_knowledge
        assert response.results == ()
        assert response.uncertainty == "No permitted knowledge matched within the requester scope."
        return

    expected_record = corpus.approved_records[0]
    assert not response.no_knowledge
    assert response.uncertainty is None
    assert len(response.results) == 1
    result = response.results[0]
    assert result.tier is expected_tier
    assert result.content_reference == expected_record.content_reference
    assert result.source_record_ids == (expected_record.metadata.record_id,)
    assert result.provenance == expected_record.provenance
    assert set(result.source_record_ids) <= approved_ids
    assert not set(result.source_record_ids) & foreign_ids
