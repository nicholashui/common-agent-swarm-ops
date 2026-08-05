"""Offline golden harness for Host skill foundations (phase 3.4 lite)."""

from __future__ import annotations

from typing import Any, Callable

from app.aesthetics.models import AestheticEvaluateRequest
from app.aesthetics.service import get_aesthetics_service
from app.coding.service import CodingPlanRequest, get_coding_service
from app.complex_problem.service import ComplexProblemRequest, get_complex_problem_service
from app.creative.service import CreativeIdeateRequest, get_creative_service
from app.intent.service import IntentAnalyzeRequest, get_intent_service
from app.knowledge.models import KnowledgeRouteRequest
from app.knowledge.service import get_knowledge_router_service
from app.llm_usage.service import LlmUsageRecordRequest, get_llm_usage_service
from app.lqr.service import LqrOverviewRequest, get_lqr_service
from app.optimization.service import OptimizeRequest, get_optimization_service
from app.podcast.service import PodcastOutlineRequest, get_podcast_service
from app.psychology.service import PsychProfileRequest, get_psychology_service
from app.rag.models import RagQueryRequest
from app.rag.service import get_rag_service
from app.research.service import ResearchQueryRequest, get_research_service
from app.screenwriting.service import ScreenplayPlanRequest, get_screenwriting_service
from app.strategic.service import StrategicPlanRequest, get_strategic_service
from app.tech_radar.service import TechRadarAdviseRequest, get_tech_radar_service
from app.thinking.service import ThinkingRecommendRequest, get_thinking_service

CaseFn = Callable[[], dict[str, Any]]


def _case(skill: str, name: str, fn: CaseFn) -> dict[str, Any]:
    try:
        detail = fn()
        passed = bool(detail.get("pass"))
        return {
            "skill": skill,
            "case": name,
            "pass": passed,
            "detail": detail,
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "skill": skill,
            "case": name,
            "pass": False,
            "detail": {"error": str(exc)[:300]},
        }


def run_golden_suite(*, skills: list[str] | None = None) -> dict[str, Any]:
    """Run deterministic offline golden checks for selected Host skills."""
    all_cases: list[tuple[str, str, CaseFn]] = [
        (
            "rag",
            "seeded_query_has_citations",
            lambda: _rag_case(),
        ),
        (
            "knowledge",
            "routes_memory_or_rag",
            lambda: _knowledge_case(),
        ),
        (
            "research",
            "offline_brief_ok",
            lambda: _research_case(),
        ),
        (
            "thinking",
            "recommend_has_profile",
            lambda: _thinking_case(),
        ),
        (
            "aesthetics",
            "score_full_vector",
            lambda: _aesthetics_case(),
        ),
        (
            "intent",
            "analyze_primary_intent",
            lambda: _intent_case(),
        ),
        (
            "optimization",
            "prompt_suggestions",
            lambda: _optimization_case(),
        ),
        (
            "creative",
            "ideate_candidates",
            lambda: _creative_case(),
        ),
        (
            "complex_problem",
            "solve_has_plan",
            lambda: _complex_case(),
        ),
        (
            "strategic",
            "plan_has_milestones",
            lambda: _strategic_case(),
        ),
        (
            "llm_usage",
            "record_offline_budget",
            lambda: _llm_usage_case(),
        ),
        (
            "psychology",
            "profile_cohort",
            lambda: _psychology_case(),
        ),
        (
            "coding",
            "plan_only_fail_closed",
            lambda: _coding_case(),
        ),
        (
            "podcast",
            "outline_segments",
            lambda: _podcast_case(),
        ),
        (
            "screenwriting",
            "beat_sheet",
            lambda: _screenwriting_case(),
        ),
        (
            "tech_radar",
            "advise_prefers_stub",
            lambda: _tech_radar_case(),
        ),
        (
            "lqr",
            "overview_phases",
            lambda: _lqr_case(),
        ),
    ]
    allow = set(skills) if skills else None
    results = []
    for skill, name, fn in all_cases:
        if allow is not None and skill not in allow:
            continue
        results.append(_case(skill, name, fn))

    passed = sum(1 for r in results if r["pass"])
    failed = len(results) - passed
    return {
        "ok": failed == 0,
        "passed": passed,
        "failed": failed,
        "total": len(results),
        "results": results,
        "note": "Offline golden harness — not production RAGAS/LLM-judge suite.",
        "activation_policy": {
            "live_llm_judge": False,
            "network": False,
        },
    }


def _rag_case() -> dict[str, Any]:
    res = get_rag_service().query(
        RagQueryRequest(query="Host memory retrieval tiers", publish_bus=False)
    )
    run = res.get("run") or {}
    return {
        "pass": bool(res.get("ok") and run.get("citations")),
        "citations": len(run.get("citations") or []),
    }


def _knowledge_case() -> dict[str, Any]:
    res = get_knowledge_router_service().route(
        KnowledgeRouteRequest(query="How does memory retrieval work?")
    )
    return {
        "pass": res.get("primary") in {"memory", "rag"},
        "primary": res.get("primary"),
    }


def _research_case() -> dict[str, Any]:
    res = get_research_service().query(
        ResearchQueryRequest(query="Offline Agentic RAG foundation")
    )
    return {
        "pass": bool(res.get("ok") and res.get("brief")),
        "confidence": res.get("confidence"),
    }


def _thinking_case() -> dict[str, Any]:
    res = get_thinking_service().recommend(
        ThinkingRecommendRequest(goal="Plan a simple stub status check")
    )
    profile = res.get("cognitive_profile") or {}
    return {
        "pass": bool(profile.get("operating_mode") and profile.get("max_steps")),
        "mode": profile.get("operating_mode"),
    }


def _aesthetics_case() -> dict[str, Any]:
    res = get_aesthetics_service().evaluate(
        AestheticEvaluateRequest(artifact_ref="asset://golden_eval", mode="score")
    )
    v = res.get("verdict") or {}
    vec = v.get("aesthetic_vector") or {}
    return {
        "pass": bool(res.get("ok") and len(vec) >= 10),
        "dims": len(vec),
    }


def _intent_case() -> dict[str, Any]:
    res = get_intent_service().analyze(
        IntentAnalyzeRequest(
            text="Create a 30s TikTok UGC ad for a new tea brand, upbeat, 9:16"
        )
    )
    return {
        "pass": bool(res.get("ok") and res.get("primary_intent")),
        "intent": res.get("primary_intent"),
        "archetype": res.get("recommended_archetype"),
    }


def _optimization_case() -> dict[str, Any]:
    res = get_optimization_service().optimize(
        OptimizeRequest(goal="Improve prompt quality for cinematic short", kind="prompt")
    )
    return {
        "pass": bool(res.get("ok") and res.get("suggestions")),
        "count": len(res.get("suggestions") or []),
    }


def _creative_case() -> dict[str, Any]:
    res = get_creative_service().ideate(
        CreativeIdeateRequest(brief="30s noir product teaser with practical lamp", n_candidates=3)
    )
    cands = res.get("candidates") or []
    phases = [p.get("phase") for p in (res.get("phase_trace") or [])]
    complete = False
    if cands:
        c0 = cands[0]
        outliers = c0.get("outlier_dimensions") or []
        risks = c0.get("risks_mitigations") or {}
        complete = bool(
            c0.get("multi_pov")
            and 1 <= len(outliers) <= 4
            and all(
                k in c0
                for k in (
                    "novelty",
                    "usefulness",
                    "coherence",
                    "feasibility",
                    "overall_cr",
                )
            )
            and risks.get("risk")
            and risks.get("mitigations")
            and c0.get("refinement_note")
            and "multi_pov_mapping" in phases
            and "value_gated_selection" in phases
            and "integration_refinement" in phases
            and res.get("domain")
            and res.get("learned_patterns_scope") == "process_local"
            and isinstance(res.get("learned_patterns"), list)
            and (res.get("handoff") or {}).get("best_candidate_id")
            and (res.get("handoff") or {}).get("next_agents")
            and (res.get("handoff") or {}).get("prompt_steer")
        )
    patterns = get_creative_service().patterns(limit=12)
    patterns_ok = bool(
        patterns.get("ok")
        and patterns.get("scope") == "process_local"
        and isinstance(patterns.get("items"), list)
    )
    return {
        "pass": bool(res.get("ok") and len(cands) >= 1 and complete and patterns_ok),
        "n": len(cands),
        "domain": res.get("domain"),
        "ssor_lite": complete,
        "has_integration": bool(cands and (cands[0].get("refinement_note"))),
        "has_handoff": bool((res.get("handoff") or {}).get("next_agents")),
        "patterns_ok": patterns_ok,
    }


def _complex_case() -> dict[str, Any]:
    res = get_complex_problem_service().solve(
        ComplexProblemRequest(problem="Ship offline video spine with research and QC gates")
    )
    return {
        "pass": bool(res.get("ok") and res.get("plan") and res.get("gates")),
        "steps": len(res.get("plan") or []),
    }


def _strategic_case() -> dict[str, Any]:
    res = get_strategic_service().plan(
        StrategicPlanRequest(goal="Deliver a campaign of three short brand films")
    )
    return {
        "pass": bool(res.get("ok") and res.get("milestones") and res.get("key_results")),
        "milestones": len(res.get("milestones") or []),
    }


def _llm_usage_case() -> dict[str, Any]:
    res = get_llm_usage_service().record(
        LlmUsageRecordRequest(
            operation="golden_eval",
            estimated_input_tokens=100,
            estimated_output_tokens=50,
            offline=True,
        )
    )
    return {
        "pass": bool(res.get("ok") and res.get("within_budget")),
        "used": res.get("used_tokens_estimate"),
    }


def _psychology_case() -> dict[str, Any]:
    res = get_psychology_service().profile(
        PsychProfileRequest(brief="30s TikTok UGC ad for tea, upbeat, gen z")
    )
    prof = res.get("profile") or {}
    return {
        "pass": bool(res.get("ok") and prof.get("cohort_id") and prof.get("emotional_target")),
        "cohort": prof.get("cohort_id"),
    }


def _coding_case() -> dict[str, Any]:
    res = get_coding_service().plan(
        CodingPlanRequest(goal="Add offline Host skill API with unit tests")
    )
    denied = get_coding_service().plan(
        CodingPlanRequest(goal="x", allow_shell_exec=True)
    )
    return {
        "pass": bool(
            res.get("ok")
            and res.get("plan_steps")
            and denied.get("ok") is False
        ),
        "steps": len(res.get("plan_steps") or []),
    }


def _podcast_case() -> dict[str, Any]:
    res = get_podcast_service().outline(
        PodcastOutlineRequest(topic="Offline agent loops explained", duration_min=20)
    )
    return {
        "pass": bool(res.get("ok") and res.get("segments") and res.get("vo_plan")),
        "segments": len(res.get("segments") or []),
    }


def _screenwriting_case() -> dict[str, Any]:
    res = get_screenwriting_service().plan(
        ScreenplayPlanRequest(
            logline_or_goal="A quiet clerk seeks redemption after a small lie spreads",
            form="short",
        )
    )
    return {
        "pass": bool(res.get("ok") and res.get("beats") and res.get("controlling_idea")),
        "beats": len(res.get("beats") or []),
    }


def _tech_radar_case() -> dict[str, Any]:
    res = get_tech_radar_service().advise(
        TechRadarAdviseRequest(
            goal="Generate offline stub video for spine QC", prefer_offline=True
        )
    )
    return {
        "pass": bool(
            res.get("ok")
            and res.get("recommended_provider_id")
            in {"media_stub", "sora", "veo"}
        ),
        "recommended": res.get("recommended_provider_id"),
    }


def _lqr_case() -> dict[str, Any]:
    res = get_lqr_service().overview(LqrOverviewRequest())
    return {
        "pass": bool(res.get("ok") and len(res.get("phases") or []) >= 6),
        "phases": len(res.get("phases") or []),
    }


def _psychology_case() -> dict[str, Any]:
    res = get_psychology_service().profile(
        PsychProfileRequest(brief="30s TikTok UGC ad for tea, upbeat, gen z")
    )
    prof = res.get("profile") or {}
    return {
        "pass": bool(res.get("ok") and prof.get("cohort_id") and prof.get("emotional_target")),
        "cohort": prof.get("cohort_id"),
    }


def _coding_case() -> dict[str, Any]:
    res = get_coding_service().plan(
        CodingPlanRequest(goal="Add offline Host skill API with unit tests")
    )
    denied = get_coding_service().plan(
        CodingPlanRequest(goal="x", allow_shell_exec=True)
    )
    return {
        "pass": bool(
            res.get("ok")
            and res.get("plan_steps")
            and denied.get("ok") is False
        ),
        "steps": len(res.get("plan_steps") or []),
    }


def _podcast_case() -> dict[str, Any]:
    res = get_podcast_service().outline(
        PodcastOutlineRequest(topic="Offline agent loops explained", duration_min=20)
    )
    return {
        "pass": bool(res.get("ok") and res.get("segments") and res.get("vo_plan")),
        "segments": len(res.get("segments") or []),
    }


def _screenwriting_case() -> dict[str, Any]:
    res = get_screenwriting_service().plan(
        ScreenplayPlanRequest(
            logline_or_goal="A quiet clerk seeks redemption after a small lie spreads",
            form="short",
        )
    )
    return {
        "pass": bool(res.get("ok") and res.get("beats") and res.get("controlling_idea")),
        "beats": len(res.get("beats") or []),
    }


def _tech_radar_case() -> dict[str, Any]:
    res = get_tech_radar_service().advise(
        TechRadarAdviseRequest(goal="Generate offline stub video for spine QC", prefer_offline=True)
    )
    return {
        "pass": bool(
            res.get("ok") and res.get("recommended_provider_id") in {"media_stub", "sora", "veo"}
        ),
        "recommended": res.get("recommended_provider_id"),
    }


def _lqr_case() -> dict[str, Any]:
    res = get_lqr_service().overview(LqrOverviewRequest())
    return {
        "pass": bool(res.get("ok") and len(res.get("phases") or []) >= 6),
        "phases": len(res.get("phases") or []),
    }
