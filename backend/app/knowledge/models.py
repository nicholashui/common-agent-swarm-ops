"""Offline Knowledge Router contracts (study knowledge_router_agent, lite)."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


Destination = Literal[
    "memory",
    "rag",
    "pack_agent",
    "aesthetics",
    "agent_loop",
    "deny_live",
]

ACTIVATION_POLICY: dict[str, Any] = {
    "production_router": False,
    "live_web": False,
    "vector_embeddings": False,
    "gnn_router": False,
    "mode": "offline_deterministic_stub",
    "note": (
        "Offline Knowledge Router foundation. Not production hybrid "
        "metadata+GNN+LLM ranker over 5k MD corpus."
    ),
}


class KnowledgeRouteRequest(StrictModel):
    query: str = Field(min_length=1, max_length=4_000)
    requester_agent_id: str = Field(default="video.memory", max_length=120)
    intent_hint: str = Field(default="", max_length=200)
    allow_live_web: bool = False


class KnowledgeRouteResult(StrictModel):
    query: str
    primary: Destination
    secondary: list[Destination]
    confidence: float
    rationale: list[str]
    suggested_agent_ids: list[str]
    context_hints: list[str]
    activation_policy: dict[str, Any]
    note: str
