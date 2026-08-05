"""AestheticsAgent facade — offline Host service (spec §§5, 7, 9)."""

from __future__ import annotations

import threading
from typing import Any

from app.aesthetics.aligner import build_aligner_payload, preference_pairs_from_ranking
from app.aesthetics.bus import AestheticCritiqueBus
from app.aesthetics.critic import score_artifact
from app.aesthetics.handoff import attach_verdict_to_handoff
from app.aesthetics.memory import AestheticProjectMemory
from app.aesthetics.models import (
    ACTIVATION_POLICY,
    AestheticCompareRequest,
    AestheticCompareResult,
    AestheticEvaluateRequest,
    AestheticProfileCreate,
    AestheticVerdict,
)
from app.aesthetics.taste_keeper import TasteKeeper
from app.aesthetics.verdict_md import format_verdict_markdown


class AestheticsService:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._taste = TasteKeeper()
        self._verdicts: list[dict[str, Any]] = []
        self._bus = AestheticCritiqueBus()
        self._memory = AestheticProjectMemory()
        self._refine_counts: dict[str, int] = {}

    @property
    def activation_policy(self) -> dict[str, Any]:
        return dict(ACTIVATION_POLICY)

    def list_profiles(self) -> list[dict[str, Any]]:
        return self._taste.list_profiles()

    def upsert_profile(self, body: AestheticProfileCreate) -> dict[str, Any]:
        return self._taste.upsert(body).model_dump()

    def evaluate(self, request: AestheticEvaluateRequest) -> dict[str, Any]:
        if request.allow_live_vision:
            return {
                "ok": False,
                "error": (
                    "Live vision / network multimodal scoring is not enabled. "
                    "Fail-closed offline Critic only (set allow_live_vision=false)."
                ),
                "activation_policy": self.activation_policy,
            }

        profile_id, neutral_fallback = self._taste.resolve_profile_id(request.profile_id)
        profile = self._taste.get(profile_id)

        constraints = {
            "aspect_ratio": request.constraints.aspect_ratio,
            "color_space": request.constraints.color_space,
            "deliverable": request.constraints.deliverable,
        }
        parts = score_artifact(
            artifact_ref=request.artifact_ref,
            media_type=request.media_type,
            profile_weights=profile.weights,
            intent_text=request.intent.shot_intent_text,
            emotional_target={
                "valence": request.emotional_target.valence,
                "arousal": request.emotional_target.arousal,
            },
            tier=request.budget.tier,
            constraints=constraints,
        )
        align = build_aligner_payload(parts)

        # screen mode: scalar gate only still includes vector (spec: no naked scalar)
        mode = request.mode
        reward = align["reward"] if mode in {"align", "refine", "score"} else None
        pairs = align["preference_pairs"] if mode in {"align", "compare", "refine"} else None

        if mode == "screen":
            # Fast path: still attach vector + hack for auditability
            pass

        note_bits = [
            "Offline deterministic Critic/Aligner stub.",
            "Not live SigLIP/VLM.",
        ]
        if neutral_fallback:
            note_bits.append(
                f"Profile fallback to {profile_id} (taste-agnostic baseline flagged)."
            )
        if parts["escalate_to_hitl"]:
            note_bits.append("HiTL escalation recommended (uncertainty or anti-hack).")

        verdict = AestheticVerdict(
            artifact_ref=request.artifact_ref,
            profile_id=profile_id,
            mode=mode,
            media_type=request.media_type,
            aesthetic_vector=parts["aesthetic_vector"],
            confidence=parts["confidence"],
            intent_fidelity=parts["intent_fidelity"],
            emotion_match=parts["emotion_match"],
            hack_likelihood=parts["hack_likelihood"],
            aesthetic_quality=parts["aesthetic_quality"],
            top_failing_dimensions=parts["top_failing_dimensions"],
            actionable_critique=align["actionable_critique"],
            prompt_steer_hints=align["prompt_steer_hints"],
            uncertainty_flag=parts["uncertainty_flag"],
            escalate_to_hitl=parts["escalate_to_hitl"],
            provenance={
                "models": ["offline_stub_ensemble_v1"],
                "ensemble_agreement": parts["ensemble_agreement"],
                "tier": request.budget.tier,
                "gated_parts": parts["gated_parts"],
                "constraints_applied": parts.get("constraints_applied"),
                "profile_version": profile.version,
                "profile_type": profile.profile_type,
            },
            reward=reward,
            preference_pairs=pairs,
            activation_policy=self.activation_policy,
            note=" ".join(note_bits),
        )
        payload = verdict.model_dump()
        md = format_verdict_markdown(payload)
        with self._lock:
            self._verdicts.append(payload)
            if len(self._verdicts) > 2000:
                self._verdicts = self._verdicts[-1500:]
        # Auto-record as candidate in episodic memory (project default)
        self._memory.record(
            project_id="default",
            artifact_ref=request.artifact_ref,
            decision="candidate",
            verdict=payload,
            note=f"mode={mode}",
        )
        return {"ok": True, "verdict": payload, "verdict_markdown": md}

    def compare(self, request: AestheticCompareRequest) -> dict[str, Any]:
        if request.allow_live_vision:
            return {
                "ok": False,
                "error": "Live vision compare denied (fail-closed offline only).",
                "activation_policy": self.activation_policy,
            }
        ranking: list[dict[str, Any]] = []
        for ref in request.candidates:
            sub = AestheticEvaluateRequest(
                artifact_ref=ref,
                media_type=request.media_type,
                profile_id=request.profile_id,
                intent=request.intent,
                emotional_target=request.emotional_target,
                mode="compare",
            )
            result = self.evaluate(sub)
            if not result.get("ok"):
                return result
            v = result["verdict"]
            ranking.append(
                {
                    "artifact_ref": ref,
                    "aesthetic_quality": v["aesthetic_quality"],
                    "hack_likelihood": v["hack_likelihood"],
                    "top_failing_dimensions": v["top_failing_dimensions"],
                }
            )
        ranking.sort(key=lambda r: r["aesthetic_quality"], reverse=True)
        best = ranking[0]["artifact_ref"] if ranking else ""
        pairs = preference_pairs_from_ranking(ranking)
        out = AestheticCompareResult(
            ranking=ranking,
            best_artifact_ref=best,
            profile_id=self._taste.resolve_profile_id(request.profile_id)[0],
            activation_policy=self.activation_policy,
            note="Offline compare ranks deterministic stub AQ scores.",
        )
        return {
            "ok": True,
            **out.model_dump(),
            "preference_pairs": pairs,
        }

    def refine(self, request: AestheticEvaluateRequest) -> dict[str, Any]:
        """Refine step: score + critique + prompt steers (≤3 iter scaffold, §9)."""
        req = request.model_copy(update={"mode": "refine"})
        result = self.evaluate(req)
        if not result.get("ok"):
            return result
        v = result["verdict"]
        max_iter = 3
        with self._lock:
            key = str(request.artifact_ref)
            iteration = int(self._refine_counts.get(key, 0)) + 1
            self._refine_counts[key] = iteration
        if v.get("escalate_to_hitl"):
            next_action = "escalate_hitl"
        elif iteration >= max_iter:
            next_action = "stop_max_iterations"
        else:
            next_action = "apply_prompt_steer_and_rescore"
        return {
            "ok": True,
            "iteration": iteration,
            "max_iterations_hint": max_iter,
            "verdict": v,
            "verdict_markdown": result.get("verdict_markdown"),
            "next_action": next_action,
            "activation_policy": self.activation_policy,
            "note": "Offline refine scaffold — does not call generators.",
        }

    def compose_profiles(
        self,
        *,
        base_profile_id: str,
        overlay_profile_id: str,
        new_profile_id: str,
        owner: str = "local",
        precedence: str = "overlay",
    ) -> dict[str, Any]:
        rec = self._taste.compose(
            base_profile_id=base_profile_id,
            overlay_profile_id=overlay_profile_id,
            new_profile_id=new_profile_id,
            owner=owner,
            precedence=precedence,
        )
        return {"ok": True, "profile": rec.model_dump()}

    def recent_verdicts(self, *, limit: int = 20) -> list[dict[str, Any]]:
        limit = max(1, min(limit, 100))
        with self._lock:
            return list(self._verdicts[-limit:])

    def publish_to_bus(
        self,
        verdict: dict[str, Any],
        *,
        to_agent_ids: list[str] | None = None,
        correlation_id: str | None = None,
    ) -> list[dict[str, Any]]:
        return self._bus.publish_verdict(
            verdict=verdict,
            to_agent_ids=to_agent_ids,
            correlation_id=correlation_id,
        )

    def list_bus(
        self,
        *,
        to_agent_id: str | None = None,
        artifact_ref: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        return self._bus.list_messages(
            to_agent_id=to_agent_id,
            artifact_ref=artifact_ref,
            limit=limit,
        )

    def record_decision(
        self,
        *,
        project_id: str,
        artifact_ref: str,
        decision: str,
        note: str = "",
        ratchet_profile: bool = True,
    ) -> dict[str, Any]:
        # Attach latest matching verdict if any
        with self._lock:
            match = next(
                (
                    v
                    for v in reversed(self._verdicts)
                    if v.get("artifact_ref") == artifact_ref
                ),
                None,
            )
        entry = self._memory.record(
            project_id=project_id,
            artifact_ref=artifact_ref,
            decision=decision,
            verdict=match,
            note=note,
        )
        ratcheted = None
        if ratchet_profile and match and decision.strip().lower() in {
            "accepted",
            "rejected",
        }:
            updated = self._taste.ratchet(
                profile_id=str(match.get("profile_id") or ""),
                decision=decision,
                top_failing_dimensions=list(match.get("top_failing_dimensions") or []),
                aesthetic_quality=float(match.get("aesthetic_quality") or 0.0),
            )
            if updated is not None:
                ratcheted = updated.model_dump()
        return {
            "ok": True,
            "entry": entry,
            "project": self._memory.summary(project_id),
            "profile_ratcheted": ratcheted,
        }

    def project_memory(
        self, project_id: str, *, limit: int = 50
    ) -> dict[str, Any]:
        return {
            "items": self._memory.list_project(project_id, limit=limit),
            "summary": self._memory.summary(project_id),
        }

    def attach_to_handoff(
        self, handoff: dict[str, Any], verdict: dict[str, Any]
    ) -> dict[str, Any]:
        return attach_verdict_to_handoff(handoff, verdict)


_SERVICE: AestheticsService | None = None
_LOCK = threading.Lock()


def get_aesthetics_service() -> AestheticsService:
    global _SERVICE
    with _LOCK:
        if _SERVICE is None:
            _SERVICE = AestheticsService()
        return _SERVICE


def reset_aesthetics_service_for_tests() -> AestheticsService:
    global _SERVICE
    with _LOCK:
        _SERVICE = AestheticsService()
        return _SERVICE
