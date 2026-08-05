"""Offline Research Agent Host foundation.

Plan → route → gather (RAG) → synthesize → critic. Live web denied.
"""

from __future__ import annotations

import threading
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

from app.knowledge.models import KnowledgeRouteRequest
from app.knowledge.service import get_knowledge_router_service
from app.rag.models import RagQueryRequest
from app.rag.service import get_rag_service

ACTIVATION_POLICY: dict[str, Any] = {
    "production_research": False,
    "live_web": False,
    "tavily": False,
    "mode": "offline_deterministic_stub",
    "note": (
        "Offline Research foundation: plan/route/RAG gather/synthesize. "
        "Live web search is not enabled."
    ),
}


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ResearchQueryRequest(StrictModel):
    query: str = Field(min_length=1, max_length=4_000)
    requester_agent_id: str = Field(default="video.webresearch", max_length=120)
    max_sources: int = Field(default=6, ge=1, le=16)
    allow_live_web: bool = False
    publish_bus: bool = False


class ResearchService:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._runs: list[dict[str, Any]] = []

    @property
    def activation_policy(self) -> dict[str, Any]:
        return dict(ACTIVATION_POLICY)

    def policy(self) -> dict[str, Any]:
        return {
            "activation_policy": self.activation_policy,
            "steps": ["plan", "route", "gather_rag", "synthesize", "critic"],
            "agent_id": "specials.research-agent",
            "note": ACTIVATION_POLICY["note"],
        }

    def query(self, request: ResearchQueryRequest) -> dict[str, Any]:
        if request.allow_live_web:
            return {
                "ok": False,
                "error": (
                    "Live web research is not enabled. "
                    "Fail-closed offline RAG gather only."
                ),
                "activation_policy": self.activation_policy,
            }

        run_id = f"res_{uuid4().hex[:12]}"
        plan = [
            f"Clarify research question: {request.query[:200]}",
            "Route knowledge destination (offline router)",
            "Gather grounded evidence via offline RAG",
            "Synthesize brief with citations",
            "Critic: faithfulness / coverage check",
        ]

        router = get_knowledge_router_service()
        route = router.route(
            KnowledgeRouteRequest(
                query=request.query,
                requester_agent_id=request.requester_agent_id,
                intent_hint="research evidence",
            )
        )

        rag = get_rag_service()
        rag_result = rag.query(
            RagQueryRequest(
                query=request.query,
                max_iterations=2,
                top_k=request.max_sources,
                publish_bus=request.publish_bus,
            )
        )
        rag_run = (rag_result.get("run") or {}) if rag_result.get("ok") else {}
        citations = list(rag_run.get("citations") or [])[: request.max_sources]
        answer = str(rag_run.get("final_answer") or "")
        conf = float(rag_run.get("confidence") or 0.0)

        # Offline research critic
        issues: list[str] = []
        if not citations:
            issues.append("no_citations")
        if conf < 0.25:
            issues.append("low_confidence")
        if route.get("primary") == "deny_live":
            issues.append("route_denied")

        brief = {
            "title": f"Research brief: {request.query[:80]}",
            "question": request.query,
            "route_primary": route.get("primary"),
            "findings": answer[:4000],
            "citations": citations,
            "confidence": conf,
            "limitations": [
                "Offline Host foundation — no live web / Tavily",
                "Evidence limited to process-local RAG index + seeds",
            ],
        }

        payload = {
            "ok": True,
            "run_id": run_id,
            "plan": plan,
            "route": route,
            "brief": brief,
            "citations": citations,
            "confidence": conf,
            "issues": issues,
            "escalate_to_hitl": bool(issues) or conf < 0.3,
            "activation_policy": self.activation_policy,
            "note": ACTIVATION_POLICY["note"],
            "patterns_used": ["Planning", "Routing", "RAG_Gather", "Synthesis", "Critic"],
        }
        with self._lock:
            self._runs.append(payload)
            if len(self._runs) > 300:
                self._runs = self._runs[-200:]
        return payload

    def recent(self, *, limit: int = 20) -> list[dict[str, Any]]:
        limit = max(1, min(limit, 100))
        with self._lock:
            return list(self._runs[-limit:])


_SERVICE: ResearchService | None = None
_LOCK = threading.Lock()


def get_research_service() -> ResearchService:
    global _SERVICE
    with _LOCK:
        if _SERVICE is None:
            _SERVICE = ResearchService()
        return _SERVICE


def reset_research_service_for_tests() -> ResearchService:
    global _SERVICE
    with _LOCK:
        _SERVICE = ResearchService()
        return _SERVICE
