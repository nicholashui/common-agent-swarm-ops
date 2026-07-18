"""Deterministic, scope-first local retrieval for provenance-bearing memory."""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from app.memory.models import MemoryScope, ScopedMemory
from app.models.common import utc_now
from app.models.evidence import EvidenceReference
from app.models.identifiers import OrganizationId, RecordId
from app.repositories.protocols import MemoryRepository

_TOKEN_PATTERN = re.compile(r"[a-z0-9]+")


class RetrievalTier(StrEnum):
    """The ordered, local-only retrieval tiers."""

    SEMANTIC = "tier-0-semantic"
    RELATIONSHIP = "tier-1-relationship"
    SYNTHESIS = "tier-2-synthesis"


@dataclass(frozen=True, slots=True)
class RetrievalRequester:
    """Host-derived organization and scopes that may be searched for one request."""

    organization_id: OrganizationId
    approved_scopes: tuple[MemoryScope, ...]

    def __post_init__(self) -> None:
        if not str(self.organization_id).strip():
            raise ValueError("A retrieval requester requires an organization identifier.")
        if not self.approved_scopes:
            raise ValueError("A retrieval requester requires at least one approved scope.")


@dataclass(frozen=True, slots=True)
class RetrievalRequest:
    """A query whose relationship requirement is resolved before retrieval begins."""

    requester: RetrievalRequester
    query: str
    requires_relationships: bool = False
    result_limit: int = 10

    def __post_init__(self) -> None:
        if not self.query.strip():
            raise ValueError("Retrieval queries must be non-empty.")
        if not 1 <= self.result_limit <= 100:
            raise ValueError("Retrieval result limits must be between 1 and 100.")


@dataclass(frozen=True, slots=True)
class RetrievalMatch:
    """A tier seam's candidate, which remains validated by the Host before output."""

    content_reference: str
    source_record_ids: tuple[RecordId, ...]
    provenance: tuple[EvidenceReference, ...]
    confidence: float


@dataclass(frozen=True, slots=True)
class RetrievalResult:
    """A permitted result with its retrieval tier and source provenance."""

    tier: RetrievalTier
    content_reference: str
    source_record_ids: tuple[RecordId, ...]
    provenance: tuple[EvidenceReference, ...]
    confidence: float


@dataclass(frozen=True, slots=True)
class RetrievalResponse:
    """A safe retrieval projection; an empty result set explicitly means no knowledge."""

    results: tuple[RetrievalResult, ...]
    searched_tiers: tuple[RetrievalTier, ...]
    retrieved_at: datetime
    uncertainty: str | None

    @property
    def no_knowledge(self) -> bool:
        """Make a scoped miss explicit instead of allowing a broader fallback."""
        return not self.results


TierRetriever = Callable[[RetrievalRequest, tuple[ScopedMemory, ...]], tuple[RetrievalMatch, ...]]


@dataclass(frozen=True, slots=True)
class RetrievalConfiguration:
    """Explicit permissions for non-semantic local retrieval seams."""

    relationship_retrieval_enabled: bool = True
    global_synthesis_enabled: bool = False


class KnowledgeRetriever:
    """Retrieve scoped memory in strict semantic, relationship, then synthesis order."""

    def __init__(
        self,
        repository: MemoryRepository,
        configuration: RetrievalConfiguration | None = None,
        relationship_retriever: TierRetriever | None = None,
        synthesis_retriever: TierRetriever | None = None,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._repository = repository
        self._configuration = configuration or RetrievalConfiguration()
        self._relationship_retriever = relationship_retriever or _local_relationship_retrieval
        self._synthesis_retriever = synthesis_retriever
        self._clock = clock

    def retrieve(self, request: RetrievalRequest) -> RetrievalResponse:
        """Return permitted knowledge, or an explicit scoped miss without widening access."""
        searched_tiers: list[RetrievalTier] = [RetrievalTier.SEMANTIC]
        semantic_candidates = self._scope_filtered_records(request.requester)
        semantic_results = self._permitted_results(
            RetrievalTier.SEMANTIC,
            _local_semantic_retrieval(request, semantic_candidates),
            semantic_candidates,
            request.result_limit,
        )
        if semantic_results:
            return self._response(semantic_results, searched_tiers)

        if request.requires_relationships and self._configuration.relationship_retrieval_enabled:
            searched_tiers.append(RetrievalTier.RELATIONSHIP)
            relationship_candidates = self._scope_filtered_records(request.requester)
            relationship_results = self._permitted_results(
                RetrievalTier.RELATIONSHIP,
                self._relationship_retriever(request, relationship_candidates),
                relationship_candidates,
                request.result_limit,
            )
            if relationship_results:
                return self._response(relationship_results, searched_tiers)

        if self._configuration.global_synthesis_enabled and self._synthesis_retriever is not None:
            searched_tiers.append(RetrievalTier.SYNTHESIS)
            synthesis_candidates = self._scope_filtered_records(request.requester)
            synthesis_results = self._permitted_results(
                RetrievalTier.SYNTHESIS,
                self._synthesis_retriever(request, synthesis_candidates),
                synthesis_candidates,
                request.result_limit,
            )
            if synthesis_results:
                return self._response(synthesis_results, searched_tiers)

        return self._response((), searched_tiers)

    def _scope_filtered_records(self, requester: RetrievalRequester) -> tuple[ScopedMemory, ...]:
        """Read each exact requester-approved scope; any repository fault fails closed."""
        records: dict[RecordId, ScopedMemory] = {}
        for scope in requester.approved_scopes:
            response = self._repository.records_for_scope(requester.organization_id, scope)
            if not response.is_success or response.value is None:
                return ()
            for record in response.value:
                belongs_to_requester = record.metadata.organization_id == requester.organization_id
                if belongs_to_requester and record.scope == scope:
                    records[record.metadata.record_id] = record
        return tuple(records.values())

    def _permitted_results(
        self,
        tier: RetrievalTier,
        matches: tuple[RetrievalMatch, ...],
        candidates: tuple[ScopedMemory, ...],
        result_limit: int,
    ) -> tuple[RetrievalResult, ...]:
        """Defend the output boundary against seams returning foreign or unprovenanced data."""
        permitted_by_id = {record.metadata.record_id: record for record in candidates}
        results: list[RetrievalResult] = []
        for match in matches:
            if len(results) >= result_limit:
                break
            if not _is_permitted_match(match, permitted_by_id):
                continue
            results.append(
                RetrievalResult(
                    tier=tier,
                    content_reference=match.content_reference,
                    source_record_ids=match.source_record_ids,
                    provenance=match.provenance,
                    confidence=match.confidence,
                )
            )
        return tuple(results)

    def _response(
        self,
        results: tuple[RetrievalResult, ...],
        searched_tiers: list[RetrievalTier],
    ) -> RetrievalResponse:
        uncertainty = None
        if not results:
            uncertainty = "No permitted knowledge matched within the requester scope."
        return RetrievalResponse(
            results=results,
            searched_tiers=tuple(searched_tiers),
            retrieved_at=self._clock(),
            uncertainty=uncertainty,
        )


def _local_semantic_retrieval(
    request: RetrievalRequest, candidates: tuple[ScopedMemory, ...]
) -> tuple[RetrievalMatch, ...]:
    """Score local content references by deterministic query-token coverage."""
    return _scored_matches(request.query, candidates, lambda record: record.content_reference)


def _local_relationship_retrieval(
    request: RetrievalRequest, candidates: tuple[ScopedMemory, ...]
) -> tuple[RetrievalMatch, ...]:
    """Match local source/provenance relationships only after semantic retrieval misses."""
    return _scored_matches(request.query, candidates, _relationship_text)


def _scored_matches(
    query: str,
    candidates: tuple[ScopedMemory, ...],
    text_for: Callable[[ScopedMemory], str],
) -> tuple[RetrievalMatch, ...]:
    query_terms = _terms(query)
    if not query_terms:
        return ()
    scored: list[tuple[float, ScopedMemory]] = []
    for record in candidates:
        score = _coverage(query_terms, _terms(text_for(record)))
        if score > 0:
            scored.append((score, record))
    scored.sort(key=lambda item: (-item[0], str(item[1].metadata.record_id)))
    return tuple(_record_match(record, score) for score, record in scored)


def _record_match(record: ScopedMemory, confidence: float) -> RetrievalMatch:
    return RetrievalMatch(
        content_reference=record.content_reference,
        source_record_ids=(record.metadata.record_id,),
        provenance=record.provenance,
        confidence=confidence,
    )


def _relationship_text(record: ScopedMemory) -> str:
    references = " ".join(
        f"{reference.evidence_id} {reference.kind}" for reference in record.provenance
    )
    return f"{record.source_log_set_id or ''} {references}"


def _is_permitted_match(
    match: RetrievalMatch,
    permitted_by_id: dict[RecordId, ScopedMemory],
) -> bool:
    if not match.content_reference.strip() or not 0 <= match.confidence <= 1:
        return False
    if not match.source_record_ids or not match.provenance:
        return False
    source_records = [permitted_by_id.get(record_id) for record_id in match.source_record_ids]
    if any(record is None for record in source_records):
        return False
    permitted_provenance = {
        (str(reference.evidence_id), reference.digest, reference.kind)
        for record in source_records
        if record is not None
        for reference in record.provenance
    }
    return all(
        (str(reference.evidence_id), reference.digest, reference.kind) in permitted_provenance
        for reference in match.provenance
    )


def _terms(value: str) -> frozenset[str]:
    return frozenset(_TOKEN_PATTERN.findall(value.lower()))


def _coverage(query_terms: frozenset[str], candidate_terms: frozenset[str]) -> float:
    return len(query_terms & candidate_terms) / len(query_terms)
