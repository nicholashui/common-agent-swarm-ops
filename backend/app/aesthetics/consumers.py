"""Consumer adapters — who calls Aesthetics and why (spec §8.1).

Offline helpers that route evaluate() for known consumer agent ids.
"""

from __future__ import annotations

from typing import Any

from app.aesthetics.models import AestheticEvaluateRequest, IntentInput, EmotionalTarget
from app.aesthetics.service import AestheticsService

# agents.md consumers → default mode + emphasis note
CONSUMER_PRESETS: dict[str, dict[str, Any]] = {
    "video.cinematographer": {
        "mode": "score",
        "note": "DoP self-refine — composition/light/color emphasis",
        "to_bus": ["video.cinematographer", "video.director"],
    },
    "video.colorist": {
        "mode": "score",
        "note": "Colorist — palette / ΔE / mood vector (offline stub)",
        "to_bus": ["video.colorist", "video.director"],
    },
    "video.storyboard": {
        "mode": "score",
        "note": "Storyboard style-bible + composition",
        "to_bus": ["video.storyboard", "video.director"],
    },
    "video.conceptartist": {
        "mode": "score",
        "note": "Concept art style fidelity",
        "to_bus": ["video.conceptartist"],
    },
    "video.productiondesign": {
        "mode": "score",
        "note": "Production design coherence",
        "to_bus": ["video.productiondesign"],
    },
    "video.promptengineer": {
        "mode": "refine",
        "note": "Prompt engineer — refine + prompt_steer_hints (≤3 iter)",
        "to_bus": ["video.promptengineer"],
    },
    "video.aiqaconsistency": {
        "mode": "score",
        "note": "AIQA cross-check — temporal/hack_likelihood boundary",
        "to_bus": ["video.aiqaconsistency", "video.judge"],
    },
    "video.director": {
        "mode": "compare",
        "note": "Director tie-break / candidate adjudication",
        "to_bus": ["video.director", "video.judge"],
    },
    "video.judge": {
        "mode": "score",
        "note": "Judge blind preference adjudication",
        "to_bus": ["video.judge"],
    },
    "video.marketing": {
        "mode": "screen",
        "note": "Thumbnail/hook aesthetic screening",
        "to_bus": ["video.marketing"],
    },
    # Spec §8.1 niche aesthetic regressors
    "video.foodstylist": {
        "mode": "score",
        "note": "Food stylist — color/subject/appetite-composition emphasis",
        "to_bus": ["video.foodstylist", "video.director"],
    },
    "video.travelcine": {
        "mode": "score",
        "note": "Travel cine — light/novelty/location composition",
        "to_bus": ["video.travelcine", "video.director"],
    },
    "video.realestatephoto": {
        "mode": "score",
        "note": "Real-estate photo — composition/technical/light clarity",
        "to_bus": ["video.realestatephoto"],
    },
}


def list_consumers() -> list[dict[str, Any]]:
    return [
        {"agent_id": aid, **meta} for aid, meta in sorted(CONSUMER_PRESETS.items())
    ]


def evaluate_for_consumer(
    service: AestheticsService,
    *,
    consumer_agent_id: str,
    artifact_ref: str,
    media_type: str = "image",
    profile_id: str | None = None,
    shot_intent_text: str = "",
    publish_bus: bool = True,
) -> dict[str, Any]:
    """Run aesthetics for a known consumer agent id (offline)."""
    cid = consumer_agent_id.strip()
    preset = CONSUMER_PRESETS.get(cid)
    if not preset:
        return {
            "ok": False,
            "error": (
                f"Unknown aesthetics consumer '{cid}'. "
                f"Known: {', '.join(sorted(CONSUMER_PRESETS))}"
            ),
        }

    mode = str(preset.get("mode") or "score")
    if mode == "compare":
        # Single-artifact compare falls back to score for this helper
        mode = "score"

    req = AestheticEvaluateRequest(
        artifact_ref=artifact_ref,
        media_type=media_type,  # type: ignore[arg-type]
        profile_id=profile_id,
        intent=IntentInput(shot_intent_text=shot_intent_text),
        emotional_target=EmotionalTarget(),
        mode=mode,  # type: ignore[arg-type]
    )
    if mode == "refine":
        result = service.refine(req)
    else:
        result = service.evaluate(req)

    if not result.get("ok"):
        return result

    verdict = result.get("verdict")
    if not isinstance(verdict, dict):
        return {
            "ok": False,
            "error": "Consumer evaluate missing verdict payload",
        }

    bus_msgs: list[dict[str, Any]] = []
    if publish_bus:
        bus_msgs = service.publish_to_bus(
            verdict,
            to_agent_ids=list(preset.get("to_bus") or [cid]),
        )

    return {
        "ok": True,
        "consumer_agent_id": cid,
        "consumer_note": preset.get("note"),
        "result": result,
        "critique_bus_messages": bus_msgs,
        "activation_policy": service.activation_policy,
    }
