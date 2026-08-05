"""Knowledge Router Host facade."""

from __future__ import annotations

import threading
from typing import Any

from app.knowledge.models import ACTIVATION_POLICY, KnowledgeRouteRequest
from app.knowledge.router import route_knowledge


class KnowledgeRouterService:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._routes: list[dict[str, Any]] = []

    @property
    def activation_policy(self) -> dict[str, Any]:
        return dict(ACTIVATION_POLICY)

    def policy(self) -> dict[str, Any]:
        return {
            "activation_policy": self.activation_policy,
            "destinations": [
                "memory",
                "rag",
                "pack_agent",
                "aesthetics",
                "agent_loop",
                "deny_live",
            ],
            "agent_id": "specials.knowledge-router-agent",
            "note": ACTIVATION_POLICY["note"],
        }

    def route(self, request: KnowledgeRouteRequest) -> dict[str, Any]:
        if request.allow_live_web:
            return {
                "ok": False,
                "error": (
                    "Live web routing is not enabled. "
                    "Fail-closed offline destinations only."
                ),
                "activation_policy": self.activation_policy,
            }
        result = route_knowledge(
            request.query,
            requester_agent_id=request.requester_agent_id,
            intent_hint=request.intent_hint,
        )
        with self._lock:
            self._routes.append(
                {
                    "query": request.query[:200],
                    "primary": result.get("primary"),
                    "confidence": result.get("confidence"),
                }
            )
            if len(self._routes) > 500:
                self._routes = self._routes[-400:]
        return result

    def recent(self, *, limit: int = 20) -> list[dict[str, Any]]:
        limit = max(1, min(limit, 100))
        with self._lock:
            return list(self._routes[-limit:])


_SERVICE: KnowledgeRouterService | None = None
_LOCK = threading.Lock()


def get_knowledge_router_service() -> KnowledgeRouterService:
    global _SERVICE
    with _LOCK:
        if _SERVICE is None:
            _SERVICE = KnowledgeRouterService()
        return _SERVICE


def reset_knowledge_router_service_for_tests() -> KnowledgeRouterService:
    global _SERVICE
    with _LOCK:
        _SERVICE = KnowledgeRouterService()
        return _SERVICE
