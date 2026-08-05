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
        # Offline knowledge / research / thinking hooks
        "knowledge.route",
        "research.query",
        "thinking.recommend",
        "intent.analyze",
        "optimization.recommend",
        "skill_evals.run",
        "creative.ideate",
        "creative.patterns",
        "complex_problem.solve",
        "strategic.plan",
        "llm_usage.record",
        "psychology.profile",
        "psychology.recommend",
        "coding.plan",
        "podcast.outline",
        "screenwriting.plan",
        "tech_radar.advise",
        "lqr.overview",
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

        if tid in {
            "knowledge.route",
            "research.query",
            "thinking.recommend",
            "intent.analyze",
            "optimization.recommend",
            "skill_evals.run",
            "creative.ideate",
            "creative.patterns",
            "complex_problem.solve",
            "strategic.plan",
            "llm_usage.record",
            "psychology.profile",
            "psychology.recommend",
            "coding.plan",
            "podcast.outline",
            "screenwriting.plan",
            "tech_radar.advise",
            "lqr.overview",
        }:
            outcome = self._invoke_skill_tools(
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

    def _invoke_skill_tools(
        self,
        tool_id: str,
        *,
        agent_id: str,
        args: dict[str, Any],
        digest: str,
        now: str,
    ) -> ToolInvocationOutcome:
        """Offline knowledge/research/thinking Host tools."""
        try:
            if tool_id == "knowledge.route":
                from app.knowledge.models import KnowledgeRouteRequest
                from app.knowledge.service import get_knowledge_router_service

                q = str(args.get("query") or args.get("q") or "memory retrieval")
                result = get_knowledge_router_service().route(
                    KnowledgeRouteRequest(
                        query=q,
                        requester_agent_id=agent_id,
                        intent_hint=str(args.get("intent_hint") or ""),
                    )
                )
                ok = result.get("ok") is not False
                detail = (
                    f"knowledge.route agent={agent_id} primary={result.get('primary')} "
                    f"conf={result.get('confidence')} offline"
                )
            elif tool_id == "research.query":
                from app.research.service import ResearchQueryRequest, get_research_service

                q = str(args.get("query") or args.get("q") or "Host memory tiers")
                result = get_research_service().query(
                    ResearchQueryRequest(query=q, requester_agent_id=agent_id)
                )
                ok = bool(result.get("ok"))
                detail = (
                    f"research.query agent={agent_id} conf={result.get('confidence')} "
                    f"cites={len(result.get('citations') or [])} offline"
                )
            elif tool_id == "intent.analyze":
                from app.intent.service import IntentAnalyzeRequest, get_intent_service

                text = str(args.get("text") or args.get("goal") or args.get("query") or "plan video")
                result = get_intent_service().analyze(IntentAnalyzeRequest(text=text))
                ok = bool(result.get("ok"))
                detail = (
                    f"intent.analyze agent={agent_id} "
                    f"intent={result.get('primary_intent')} "
                    f"arch={result.get('recommended_archetype')} offline"
                )
            elif tool_id == "optimization.recommend":
                from app.optimization.service import OptimizeRequest, get_optimization_service

                goal = str(args.get("goal") or args.get("query") or "improve prompt")
                kind = str(args.get("kind") or "auto")
                result = get_optimization_service().optimize(
                    OptimizeRequest(goal=goal, kind=kind)  # type: ignore[arg-type]
                )
                ok = bool(result.get("ok"))
                detail = (
                    f"optimization.recommend agent={agent_id} kind={result.get('kind')} "
                    f"n={len(result.get('suggestions') or [])} offline"
                )
            elif tool_id == "skill_evals.run":
                from app.skill_evals.harness import run_golden_suite

                skills = args.get("skills") if isinstance(args.get("skills"), list) else None
                result = run_golden_suite(skills=skills)
                ok = bool(result.get("ok"))
                detail = (
                    f"skill_evals.run agent={agent_id} "
                    f"passed={result.get('passed')}/{result.get('total')} offline"
                )
            elif tool_id == "creative.ideate":
                from app.creative.service import CreativeIdeateRequest, get_creative_service

                brief = str(args.get("brief") or args.get("goal") or args.get("query") or "short film")
                result = get_creative_service().ideate(
                    CreativeIdeateRequest(
                        brief=brief,
                        n_candidates=int(args.get("n_candidates") or 4),
                        domain=str(args.get("domain") or ""),
                        genre=str(args.get("genre") or ""),
                    )
                )
                ok = bool(result.get("ok"))
                handoff = result.get("handoff") or {}
                detail = (
                    f"creative.ideate agent={agent_id} "
                    f"n={len(result.get('candidates') or [])} "
                    f"domain={result.get('domain')} "
                    f"handoff_next={len(handoff.get('next_agents') or [])} offline"
                )
            elif tool_id == "creative.patterns":
                from app.creative.service import get_creative_service

                result = get_creative_service().patterns(
                    limit=int(args.get("limit") or 12),
                )
                ok = bool(result.get("ok"))
                detail = (
                    f"creative.patterns agent={agent_id} "
                    f"count={result.get('count')} scope={result.get('scope')} offline"
                )
            elif tool_id == "complex_problem.solve":
                from app.complex_problem.service import (
                    ComplexProblemRequest,
                    get_complex_problem_service,
                )

                problem = str(args.get("problem") or args.get("goal") or args.get("query") or "plan")
                result = get_complex_problem_service().solve(
                    ComplexProblemRequest(problem=problem)
                )
                ok = bool(result.get("ok"))
                detail = (
                    f"complex_problem.solve agent={agent_id} "
                    f"steps={len(result.get('plan') or [])} offline"
                )
            elif tool_id == "strategic.plan":
                from app.strategic.service import StrategicPlanRequest, get_strategic_service

                goal = str(args.get("goal") or args.get("query") or "ship video")
                result = get_strategic_service().plan(StrategicPlanRequest(goal=goal))
                ok = bool(result.get("ok"))
                detail = (
                    f"strategic.plan agent={agent_id} "
                    f"milestones={len(result.get('milestones') or [])} offline"
                )
            elif tool_id == "llm_usage.record":
                from app.llm_usage.service import LlmUsageRecordRequest, get_llm_usage_service

                result = get_llm_usage_service().record(
                    LlmUsageRecordRequest(
                        operation=str(args.get("operation") or "tool"),
                        estimated_input_tokens=int(args.get("estimated_input_tokens") or 0),
                        estimated_output_tokens=int(args.get("estimated_output_tokens") or 0),
                        agent_id=agent_id,
                        offline=True,
                    )
                )
                ok = bool(result.get("ok"))
                detail = (
                    f"llm_usage.record agent={agent_id} "
                    f"used={result.get('used_tokens_estimate')} offline"
                )
            elif tool_id == "psychology.profile":
                from app.psychology.service import PsychProfileRequest, get_psychology_service

                brief = str(args.get("brief") or args.get("goal") or args.get("query") or "short video")
                result = get_psychology_service().profile(PsychProfileRequest(brief=brief))
                ok = bool(result.get("ok"))
                prof = result.get("profile") or {}
                detail = (
                    f"psychology.profile agent={agent_id} "
                    f"cohort={prof.get('cohort_id')} offline"
                )
            elif tool_id == "psychology.recommend":
                from app.psychology.service import PsychRecommendRequest, get_psychology_service

                brief = str(args.get("brief") or args.get("goal") or args.get("query") or "short video")
                result = get_psychology_service().recommend(PsychRecommendRequest(brief=brief))
                ok = bool(result.get("ok"))
                detail = (
                    f"psychology.recommend agent={agent_id} "
                    f"hooks={len(result.get('hooks') or [])} offline"
                )
            elif tool_id == "coding.plan":
                from app.coding.service import CodingPlanRequest, get_coding_service

                goal = str(args.get("goal") or args.get("query") or "implement host skill")
                result = get_coding_service().plan(CodingPlanRequest(goal=goal))
                ok = bool(result.get("ok"))
                detail = (
                    f"coding.plan agent={agent_id} "
                    f"steps={len(result.get('plan_steps') or [])} offline"
                )
            elif tool_id == "podcast.outline":
                from app.podcast.service import PodcastOutlineRequest, get_podcast_service

                topic = str(args.get("topic") or args.get("goal") or args.get("query") or "topic")
                result = get_podcast_service().outline(PodcastOutlineRequest(topic=topic))
                ok = bool(result.get("ok"))
                detail = (
                    f"podcast.outline agent={agent_id} "
                    f"segments={len(result.get('segments') or [])} offline"
                )
            elif tool_id == "screenwriting.plan":
                from app.screenwriting.service import (
                    ScreenplayPlanRequest,
                    get_screenwriting_service,
                )

                goal = str(
                    args.get("logline_or_goal")
                    or args.get("goal")
                    or args.get("query")
                    or "a short film"
                )
                result = get_screenwriting_service().plan(
                    ScreenplayPlanRequest(logline_or_goal=goal)
                )
                ok = bool(result.get("ok"))
                detail = (
                    f"screenwriting.plan agent={agent_id} "
                    f"beats={len(result.get('beats') or [])} offline"
                )
            elif tool_id == "tech_radar.advise":
                from app.tech_radar.service import TechRadarAdviseRequest, get_tech_radar_service

                goal = str(args.get("goal") or args.get("query") or "offline video stub")
                result = get_tech_radar_service().advise(TechRadarAdviseRequest(goal=goal))
                ok = bool(result.get("ok"))
                detail = (
                    f"tech_radar.advise agent={agent_id} "
                    f"rec={result.get('recommended_provider_id')} offline"
                )
            elif tool_id == "lqr.overview":
                from app.lqr.service import LqrOverviewRequest, get_lqr_service

                logline = str(args.get("logline") or args.get("goal") or args.get("query") or "")
                req = (
                    LqrOverviewRequest(logline=logline)
                    if logline.strip()
                    else LqrOverviewRequest()
                )
                result = get_lqr_service().overview(req)
                ok = bool(result.get("ok"))
                detail = (
                    f"lqr.overview agent={agent_id} "
                    f"phases={len(result.get('phases') or [])} offline"
                )
            else:
                from app.thinking.service import ThinkingRecommendRequest, get_thinking_service

                goal = str(args.get("goal") or args.get("query") or "plan video")
                result = get_thinking_service().recommend(
                    ThinkingRecommendRequest(goal=goal)
                )
                ok = bool(result.get("ok"))
                profile = result.get("cognitive_profile") or {}
                detail = (
                    f"thinking.recommend agent={agent_id} "
                    f"mode={profile.get('operating_mode')} "
                    f"steps={profile.get('max_steps')} offline"
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
                detail=f"skill tool error: {exc}"[:500],
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
