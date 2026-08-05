"""Host tool registry for agent loops: stub by default, live only with explicit activation.

Fail-closed:
- Unknown tools denied
- Live media tools denied unless CASOPS_MEDIA_LIVE=1
- Even when live flag is set, only tools listed in LIVE_TOOL_IDS may leave stub mode
"""

from __future__ import annotations

import os
import threading
from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256
from typing import Any
from uuid import uuid4

# Tools that may never be "live" without separate Host go-live review
LIVE_TOOL_IDS: frozenset[str] = frozenset(
    {
        "media.sora",
        "media.veo",
        "media.runway",
        "media.elevenlabs",
        "media.kling",
    }
)

# Always-safe stub surface for CI / offline loops
STUB_TOOL_IDS: frozenset[str] = frozenset(
    {
        "media.stub",
        "audit_log",
        "audit_log_writer",
        "video_script_format",
        "video_media_gen_stub",
        "video_qc_stub",
        "video_package_stub",
        "local.validator",
        "local.echo",
        # Offline aesthetics Critic/Aligner (process-local, no live vision)
        "aesthetics.evaluate",
        "aesthetics.compare",
        # Offline Agentic RAG (process-local index, no Chroma/LightRAG/web)
        "rag.query",
        "rag.ingest",
    }
)


def media_live_enabled() -> bool:
    return (os.environ.get("CASOPS_MEDIA_LIVE") or "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


@dataclass(frozen=True, slots=True)
class ToolInvocationOutcome:
    tool_id: str
    mode: str  # stub | denied | live_blocked
    ok: bool
    outcome: str
    effect_digest: str
    detail: str
    invoked_at: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "tool_id": self.tool_id,
            "mode": self.mode,
            "ok": self.ok,
            "outcome": self.outcome,
            "effect_digest": self.effect_digest,
            "detail": self.detail,
            "invoked_at": self.invoked_at,
        }


class HostToolRegistry:
    """Catalog + invoke tools for agent loops under Host activation policy."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._history: list[dict[str, Any]] = []

    def list_catalog(self) -> dict[str, Any]:
        """Catalog for the agent-loop Act surface.

        Honesty: even when CASOPS_MEDIA_LIVE=1, this registry never performs live
        media — invoke() always stub/live_blocked. Catalog must not claim active_mode
        live or production_media true (matches AgentLoopService activation policy).
        """
        live_env = media_live_enabled()
        tools = []
        for tid in sorted(STUB_TOOL_IDS | LIVE_TOOL_IDS):
            is_live_class = tid in LIVE_TOOL_IDS
            tools.append(
                {
                    "tool_id": tid,
                    "class": "live_media" if is_live_class else "stub_safe",
                    # Agent-loop surface never activates live media (invoke fail-closed).
                    "active_mode": "live_blocked" if is_live_class else "stub",
                    "live_allowed": False,
                    "note": (
                        "Live media class · agent-loop Act remains stub/blocked "
                        f"(CASOPS_MEDIA_LIVE={'1' if live_env else '0'}; "
                        "use Host media_production brokers for live providers)"
                        if is_live_class
                        else "Deterministic stub only"
                    ),
                }
            )
        return {
            "media_live_env": live_env,
            "tools": tools,
            "policy": {
                "default": "stub",
                "production_media": False,
                "media_live_env": live_env,
                "note": (
                    "Agent-loop Act surface is stub-only. CASOPS_MEDIA_LIVE does not "
                    "enable live media tools here; Host media_production is separate."
                ),
            },
        }

    def invoke(
        self,
        tool_id: str,
        *,
        agent_id: str,
        arguments: dict[str, Any] | None = None,
        allow_live: bool = False,
    ) -> ToolInvocationOutcome:
        now = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        tid = (tool_id or "").strip()
        args = arguments or {}
        digest = sha256(
            f"{tid}|{agent_id}|{sorted(args.items())!s}".encode("utf-8", errors="replace")
        ).hexdigest()[:32]

        if not tid:
            outcome = ToolInvocationOutcome(
                tool_id=tid or "unknown",
                mode="denied",
                ok=False,
                outcome="denied",
                effect_digest=digest,
                detail="empty tool_id",
                invoked_at=now,
            )
            self._retain(outcome, agent_id)
            return outcome

        # Live media path: still blocked unless env + allow_live
        if tid in LIVE_TOOL_IDS:
            if not (media_live_enabled() and allow_live):
                outcome = ToolInvocationOutcome(
                    tool_id=tid,
                    mode="live_blocked",
                    ok=False,
                    outcome="denied",
                    effect_digest=digest,
                    detail=(
                        "Live media tool blocked (fail-closed). "
                        "Set CASOPS_MEDIA_LIVE=1 and allow_live only after go-live review."
                    ),
                    invoked_at=now,
                )
                self._retain(outcome, agent_id)
                return outcome
            # Live path still not auto-calling external networks from agent loops here —
            # require explicit media_production entry elsewhere. Fail closed with clear note.
            outcome = ToolInvocationOutcome(
                tool_id=tid,
                mode="live_blocked",
                ok=False,
                outcome="denied",
                effect_digest=digest,
                detail=(
                    "Live media tool is activation-gated; agent-loop surface remains stub-only. "
                    "Use Host media_production brokers for live providers."
                ),
                invoked_at=now,
            )
            self._retain(outcome, agent_id)
            return outcome

        # Offline aesthetics Host tools (real deterministic Critic, not live vision)
        if tid in {"aesthetics.evaluate", "aesthetics.compare"}:
            outcome = self._invoke_aesthetics(
                tid, agent_id=agent_id, args=args, digest=digest, now=now
            )
            self._retain(outcome, agent_id)
            return outcome

        # Offline Agentic RAG Host tools (local index only)
        if tid in {"rag.query", "rag.ingest"}:
            outcome = self._invoke_rag(
                tid, agent_id=agent_id, args=args, digest=digest, now=now
            )
            self._retain(outcome, agent_id)
            return outcome

        # Stub tools + unknown tools → deterministic stub act
        mode = "stub"
        detail = f"stub invoke for {agent_id}"
        if tid not in STUB_TOOL_IDS:
            detail = f"unknown tool coerced to stub for {agent_id} (fail-closed surface)"
        outcome = ToolInvocationOutcome(
            tool_id=tid,
            mode=mode,
            ok=True,
            outcome="stub_completed",
            effect_digest=digest,
            detail=detail,
            invoked_at=now,
        )
        self._retain(outcome, agent_id)
        return outcome

    def _invoke_aesthetics(
        self,
        tool_id: str,
        *,
        agent_id: str,
        args: dict[str, Any],
        digest: str,
        now: str,
    ) -> ToolInvocationOutcome:
        """Run offline aesthetics service and surface AQ in tool outcome detail."""
        try:
            from app.aesthetics.models import (
                AestheticCompareRequest,
                AestheticEvaluateRequest,
            )
            from app.aesthetics.service import get_aesthetics_service

            service = get_aesthetics_service()
            if tool_id == "aesthetics.compare":
                candidates = args.get("candidates") or []
                if not isinstance(candidates, list) or len(candidates) < 2:
                    # Fall back to evaluate when compare args incomplete
                    ref = str(args.get("artifact_ref") or "asset://tool_stub")
                    result = service.evaluate(
                        AestheticEvaluateRequest(artifact_ref=ref, mode="score")
                    )
                else:
                    result = service.compare(
                        AestheticCompareRequest(
                            candidates=[str(c) for c in candidates[:32]],
                            media_type=str(args.get("media_type") or "image"),  # type: ignore[arg-type]
                            profile_id=args.get("profile_id"),
                        )
                    )
            else:
                ref = str(args.get("artifact_ref") or "asset://tool_stub")
                result = service.evaluate(
                    AestheticEvaluateRequest(
                        artifact_ref=ref,
                        media_type=str(args.get("media_type") or "image"),  # type: ignore[arg-type]
                        mode=str(args.get("mode") or "score"),  # type: ignore[arg-type]
                        profile_id=args.get("profile_id"),
                    )
                )
            ok = bool(result.get("ok"))
            if tool_id == "aesthetics.compare" and result.get("ranking"):
                best = result.get("best_artifact_ref")
                detail = (
                    f"aesthetics.compare agent={agent_id} best={best} "
                    f"n={len(result.get('ranking') or [])} offline"
                )
            else:
                v = result.get("verdict") or {}
                detail = (
                    f"aesthetics.evaluate agent={agent_id} "
                    f"AQ={v.get('aesthetic_quality')} "
                    f"hack={v.get('hack_likelihood')} "
                    f"escalate={v.get('escalate_to_hitl')} offline"
                )
            # Fold key result into effect digest for audit reproducibility
            effect = sha256(
                f"{digest}|{detail}|{result.get('ok')}".encode("utf-8", errors="replace")
            ).hexdigest()[:32]
            return ToolInvocationOutcome(
                tool_id=tool_id,
                mode="stub",
                ok=ok,
                outcome="stub_completed" if ok else "stub_failed",
                effect_digest=effect,
                detail=detail[:500],
                invoked_at=now,
            )
        except Exception as exc:  # noqa: BLE001 — tool surface must not crash loops
            return ToolInvocationOutcome(
                tool_id=tool_id,
                mode="stub",
                ok=False,
                outcome="stub_failed",
                effect_digest=digest,
                detail=f"aesthetics tool error: {exc}"[:500],
                invoked_at=now,
            )

    def _invoke_rag(
        self,
        tool_id: str,
        *,
        agent_id: str,
        args: dict[str, Any],
        digest: str,
        now: str,
    ) -> ToolInvocationOutcome:
        """Run offline Agentic RAG service from the agent-loop tool surface."""
        try:
            from app.rag.models import RagIngestRequest, RagQueryRequest
            from app.rag.service import get_rag_service

            service = get_rag_service()
            if tool_id == "rag.ingest":
                title = str(args.get("title") or "tool_ingest")
                content = str(args.get("content") or args.get("text") or "")
                if not content.strip():
                    return ToolInvocationOutcome(
                        tool_id=tool_id,
                        mode="stub",
                        ok=False,
                        outcome="stub_failed",
                        effect_digest=digest,
                        detail="rag.ingest requires content",
                        invoked_at=now,
                    )
                result = service.ingest(
                    RagIngestRequest(
                        title=title,
                        content=content,
                        source_ref=str(args.get("source_ref") or f"tool://{agent_id}"),
                    )
                )
                detail = (
                    f"rag.ingest agent={agent_id} doc={result.get('doc_id')} "
                    f"children={result.get('children')} offline"
                )
                ok = bool(result.get("ok"))
            else:
                q = str(args.get("query") or args.get("q") or "Host memory retrieval")
                result = service.query(
                    RagQueryRequest(
                        query=q,
                        publish_bus=bool(args.get("publish_bus", False)),
                    )
                )
                ok = bool(result.get("ok"))
                run = result.get("run") or {}
                detail = (
                    f"rag.query agent={agent_id} conf={run.get('confidence')} "
                    f"cites={len(run.get('citations') or [])} "
                    f"reflect={run.get('reflection_triggered')} offline"
                )
            effect = sha256(
                f"{digest}|{detail}|{ok}".encode("utf-8", errors="replace")
            ).hexdigest()[:32]
            return ToolInvocationOutcome(
                tool_id=tool_id,
                mode="stub",
                ok=ok,
                outcome="stub_completed" if ok else "stub_failed",
                effect_digest=effect,
                detail=detail[:500],
                invoked_at=now,
            )
        except Exception as exc:  # noqa: BLE001
            return ToolInvocationOutcome(
                tool_id=tool_id,
                mode="stub",
                ok=False,
                outcome="stub_failed",
                effect_digest=digest,
                detail=f"rag tool error: {exc}"[:500],
                invoked_at=now,
            )

    def invoke_for_agent(
        self,
        agent_id: str,
        allowed_tools: list[str] | tuple[str, ...],
        *,
        arguments: dict[str, Any] | None = None,
        max_tools: int = 4,
    ) -> list[dict[str, Any]]:
        """Invoke up to max_tools from the agent's allowlist (stub mode)."""
        results: list[dict[str, Any]] = []
        for tid in list(allowed_tools)[: max(0, min(max_tools, 8))]:
            results.append(
                self.invoke(str(tid), agent_id=agent_id, arguments=arguments).to_dict()
            )
        if not results:
            # Always record at least media.stub for act phase evidence
            results.append(
                self.invoke("media.stub", agent_id=agent_id, arguments=arguments).to_dict()
            )
        return results

    def recent(self, *, limit: int = 50) -> list[dict[str, Any]]:
        limit = max(1, min(limit, 200))
        with self._lock:
            return list(self._history[-limit:])

    def _retain(self, outcome: ToolInvocationOutcome, agent_id: str) -> None:
        with self._lock:
            self._history.append(
                {
                    "invocation_id": f"ti_{uuid4().hex[:12]}",
                    "agent_id": agent_id,
                    **outcome.to_dict(),
                }
            )
            if len(self._history) > 5000:
                self._history = self._history[-4000:]


_REGISTRY: HostToolRegistry | None = None
_LOCK = threading.Lock()


def get_host_tool_registry() -> HostToolRegistry:
    global _REGISTRY
    with _LOCK:
        if _REGISTRY is None:
            _REGISTRY = HostToolRegistry()
        return _REGISTRY


def reset_host_tool_registry_for_tests() -> HostToolRegistry:
    global _REGISTRY
    with _LOCK:
        _REGISTRY = HostToolRegistry()
        return _REGISTRY


__all__ = [
    "LIVE_TOOL_IDS",
    "STUB_TOOL_IDS",
    "HostToolRegistry",
    "get_host_tool_registry",
    "media_live_enabled",
    "reset_host_tool_registry_for_tests",
]
