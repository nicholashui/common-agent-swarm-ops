"""Scoped, provenance-bearing memory with fail-closed writes and retrieval."""

from app.memory.learning_lifecycle import ActivationEvidence, LearningLifecycleService
from app.memory.lesson_service import (
    LessonAssessment,
    LessonAssessmentCriteria,
    LessonRetrievalRequest,
    LessonService,
)
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
    "ActivationEvidence",
    "AuditUnavailableLatch",
    "InMemoryMemoryRepository",
    "KnowledgeRetriever",
    "LearningLifecycleService",
    "LessonAssessment",
    "LessonAssessmentCriteria",
    "LessonRetrievalRequest",
    "LessonService",
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
