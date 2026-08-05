"""Agentic RAG Host facade — offline foundation."""

from __future__ import annotations

import threading
from typing import Any

from app.rag.bus import RagCritiqueBus
from app.rag.index import LocalDocumentIndex
from app.rag.models import ACTIVATION_POLICY, RagIngestRequest, RagQueryRequest
from app.rag.pipeline import run_agentic_query


class AgenticRagService:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._index = LocalDocumentIndex()
        self._bus = RagCritiqueBus()
        self._runs: list[dict[str, Any]] = []

    @property
    def activation_policy(self) -> dict[str, Any]:
        return dict(ACTIVATION_POLICY)

    def policy(self) -> dict[str, Any]:
        return {
            "activation_policy": self.activation_policy,
            "patterns": [
                "Reflection",
                "Planning",
                "Tool Use",
                "Multi-Agent Collaboration",
            ],
            "elements": [
                "single_agent_routing",
                "adaptive_retrieval",
                "stateful_memory_lite",
                "hybrid_knowledge_lite",
                "iterative_refinement",
                "evaluation_aware_trace",
            ],
            "agent_id": "specials.agentic-rag-agent",
            "index": self._index.stats(),
            "note": ACTIVATION_POLICY["note"],
        }

    def ingest(self, body: RagIngestRequest) -> dict[str, Any]:
        result = self._index.ingest(
            title=body.title,
            content=body.content,
            source_ref=body.source_ref,
            tags=body.tags,
        )
        return {**result, "index": self._index.stats()}

    def query(self, request: RagQueryRequest) -> dict[str, Any]:
        if request.allow_live_web:
            return {
                "ok": False,
                "error": (
                    "Live web search is not enabled. "
                    "Fail-closed offline index only (set allow_live_web=false)."
                ),
                "activation_policy": self.activation_policy,
            }
        if request.allow_chroma:
            return {
                "ok": False,
                "error": "Chroma vector DB is not enabled on Host foundation.",
                "activation_policy": self.activation_policy,
            }
        if request.allow_lightrag:
            return {
                "ok": False,
                "error": (
                    "Commercial LightRAG / OpenSearch is not enabled "
                    "(product-bar non-goal). Offline hierarchical index only."
                ),
                "activation_policy": self.activation_policy,
            }

        run = run_agentic_query(
            self._index,
            query=request.query,
            max_iterations=request.max_iterations,
            top_k=request.top_k,
            require_relationships=request.require_relationships,
        )
        bus_msgs: list[dict[str, Any]] = []
        if request.publish_bus:
            bus_msgs = self._bus.publish_run(run)
        with self._lock:
            self._runs.append(run)
            if len(self._runs) > 500:
                self._runs = self._runs[-400:]
        return {
            "ok": True,
            "run": run,
            "critique_bus_messages": bus_msgs,
            "activation_policy": self.activation_policy,
        }

    def index_stats(self) -> dict[str, Any]:
        return self._index.stats()

    def list_documents(self, *, limit: int = 50) -> list[dict[str, Any]]:
        return self._index.list_documents(limit=limit)

    def recent_runs(self, *, limit: int = 20) -> list[dict[str, Any]]:
        limit = max(1, min(limit, 100))
        with self._lock:
            return list(self._runs[-limit:])

    def list_bus(self, *, limit: int = 50) -> list[dict[str, Any]]:
        return self._bus.list_messages(limit=limit)


_SERVICE: AgenticRagService | None = None
_LOCK = threading.Lock()


def get_rag_service() -> AgenticRagService:
    global _SERVICE
    with _LOCK:
        if _SERVICE is None:
            _SERVICE = AgenticRagService()
        return _SERVICE


def reset_rag_service_for_tests() -> AgenticRagService:
    global _SERVICE
    with _LOCK:
        _SERVICE = AgenticRagService()
        return _SERVICE
