"""Scoped, provenance-bearing memory with fail-closed writes and retrieval."""

from app.memory.models import (
    AuditUnavailableLatch,
    MemoryImpact,
    MemoryScope,
    MemoryScopeType,
    MemoryWrite,
    MemoryWritePath,
    ScopedMemory,
)
from app.memory.repository import InMemoryMemoryRepository
from app.memory.retrieval import (
    KnowledgeRetriever,
    RetrievalConfiguration,
    RetrievalMatch,
    RetrievalRequest,
    RetrievalRequester,
    RetrievalResponse,
    RetrievalResult,
    RetrievalTier,
)
from app.memory.service import MemoryService, MemoryWriteRequest

__all__ = [
    "AuditUnavailableLatch",
    "InMemoryMemoryRepository",
    "KnowledgeRetriever",
    "MemoryImpact",
    "MemoryScope",
    "MemoryScopeType",
    "MemoryService",
    "MemoryWrite",
    "MemoryWritePath",
    "MemoryWriteRequest",
    "RetrievalConfiguration",
    "RetrievalMatch",
    "RetrievalRequest",
    "RetrievalRequester",
    "RetrievalResponse",
    "RetrievalResult",
    "RetrievalTier",
    "ScopedMemory",
]
