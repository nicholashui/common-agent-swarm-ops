"""Schemas for offline Host Agentic RAG foundation (study agentic_rag spec, lite)."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


QueryComplexity = Literal["simple", "multi_hop", "relational"]
RetrievalStrategy = Literal["vector_lite", "relationship_lite", "hybrid_lite"]

ACTIVATION_POLICY: dict[str, Any] = {
    "production_rag": False,
    "live_web": False,
    "chroma": False,
    "lightrag": False,
    "opensearch": False,
    "network": False,
    "mode": "offline_deterministic_stub",
    "note": (
        "Offline Host Agentic RAG foundation. Chroma, commercial LightRAG, "
        "Tavily, and 65k production ingest are not enabled."
    ),
}


class RagIngestRequest(StrictModel):
    """Ingest a single Markdown/text document into the process-local index."""

    title: str = Field(min_length=1, max_length=300)
    content: str = Field(min_length=1, max_length=200_000)
    source_ref: str = Field(default="", max_length=500)
    tags: list[str] = Field(default_factory=list, max_length=32)


class RagQueryRequest(StrictModel):
    """§7-style query contract (offline)."""

    query: str = Field(min_length=1, max_length=4_000)
    max_iterations: int = Field(default=3, ge=1, le=3)
    top_k: int = Field(default=8, ge=1, le=32)
    require_relationships: bool | None = Field(
        default=None,
        description="Force relationship tier; None = auto from analyzer",
    )
    # Fail-closed production switches
    allow_live_web: bool = False
    allow_chroma: bool = False
    allow_lightrag: bool = False
    publish_bus: bool = True


class RetrievedChunk(StrictModel):
    chunk_id: str
    parent_id: str
    title: str
    content: str
    source_ref: str
    chunk_type: Literal["parent", "child"]
    headers: list[str] = Field(default_factory=list)
    relevance_score: float = Field(ge=0.0, le=1.0)
    grade: float = Field(default=0.0, ge=0.0, le=1.0)


class RagCitation(StrictModel):
    chunk_id: str
    source_ref: str
    title: str
    excerpt: str
    score: float


class RagRunResult(StrictModel):
    """Offline agentic run output (AgentState projection)."""

    run_id: str
    query: str
    complexity: QueryComplexity
    strategy: RetrievalStrategy
    plan: list[str]
    iterations: int
    confidence: float
    retrieved: list[RetrievedChunk]
    graded_docs: list[RetrievedChunk]
    critique: str
    final_answer: str
    citations: list[RagCitation]
    patterns_used: list[str]
    elements_used: list[str]
    reflection_triggered: bool
    escalate_to_hitl: bool
    activation_policy: dict[str, Any]
    note: str
    trace: list[dict[str, Any]] = Field(default_factory=list)
