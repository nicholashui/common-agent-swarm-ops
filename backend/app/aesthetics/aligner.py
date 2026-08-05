"""Aligner — offline critique / reward / preference / prompt-steer (spec §5.2, §9.2)."""

from __future__ import annotations

from typing import Any

from app.aesthetics.models import AESTHETIC_DIMENSIONS


_DIM_HINTS: dict[str, tuple[str, str]] = {
    "composition": (
        "Rebalance framing; subject collides with edge or lacks leading lines.",
        "add 'rule of thirds, clear negative space, intentional staging'",
    ),
    "color_harmony": (
        "Palette is incoherent or drifts; check temperature consistency.",
        "add 'cohesive palette, controlled contrast, intentional color grade'",
    ),
    "light": (
        "Exposure/zone issues; lift or shape key light on subject.",
        "add 'motivated key light, readable shadow detail, cinematic contrast'",
    ),
    "depth": (
        "Flat staging; improve layering and focal depth.",
        "add 'foreground midground background separation, shallow depth where useful'",
    ),
    "subject": (
        "Subject prominence/silhouette weak.",
        "add 'clear subject isolation, readable gesture/silhouette'",
    ),
    "technical": (
        "Technical quality issues (noise, softness, artifacts).",
        "add 'clean detail, minimal artifacts, sharp focus on subject'",
    ),
    "emotion": (
        "Emotional target mismatch (valence/arousal).",
        "add language that lands the intended mood/energy",
    ),
    "style_fidelity": (
        "Style bible / lookbook adherence low.",
        "add explicit style refs from the brief/lookbook",
    ),
    "novelty": (
        "Too generic or overly chaotic novelty.",
        "add one strategic distinctive choice without breaking coherence",
    ),
    "temporal": (
        "Temporal instability (flicker, color drift, cut rhythm).",
        "add 'stable exposure/color across cuts, authored motion gesture'",
    ),
}


def build_aligner_payload(parts: dict[str, Any]) -> dict[str, Any]:
    vector: dict[str, float] = dict(parts.get("aesthetic_vector") or {})
    failing: list[str] = list(parts.get("top_failing_dimensions") or [])
    if not failing:
        failing = sorted(AESTHETIC_DIMENSIONS, key=lambda d: vector.get(d, 1.0))[:2]

    critiques: list[str] = []
    steers: list[str] = []
    for dim in failing[:4]:
        tip = _DIM_HINTS.get(dim)
        if not tip:
            continue
        critiques.append(f"[{dim}] {tip[0]}")
        steers.append(tip[1])

    if not critiques:
        critiques.append("No critical aesthetic failures; maintain consistency with profile.")
        steers.append("keep current look; minor polish only")

    aq = float(parts.get("aesthetic_quality") or 0.0)
    hack = float(parts.get("hack_likelihood") or 0.0)
    agreement = float(parts.get("ensemble_agreement") or 0.0)

    reward = {
        "scalar": aq,
        "vector": vector,
        "variance_proxy": round(max(0.05, 1.0 - agreement), 4),
        "ensemble_agreement": agreement,
        "hack_likelihood": hack,
        "usable_for_training": hack < 0.55 and not parts.get("escalate_to_hitl"),
        "note": "Offline stub reward — not a live RLHF/DPO training channel.",
    }

    # Synthetic preference pair scaffold (rationale-bearing, not live ranking)
    preference_pairs = [
        {
            "preferred": "candidate_with_higher_AQ",
            "rejected": "candidate_with_lower_AQ",
            "rationale": critiques[0],
            "dimensions": failing[:3],
        }
    ]

    return {
        "actionable_critique": critiques,
        "prompt_steer_hints": steers,
        "reward": reward,
        "preference_pairs": preference_pairs,
    }


def preference_pairs_from_ranking(
    ranking: list[dict[str, Any]],
    *,
    max_pairs: int = 3,
) -> list[dict[str, Any]]:
    """Build rationale-bearing pairs from compare ranking (spec §9.2 step 4 scaffold)."""
    if len(ranking) < 2:
        return []
    pairs: list[dict[str, Any]] = []
    best = ranking[0]
    # Best vs each weaker candidate (capped)
    for worse in ranking[1 : 1 + max_pairs]:
        b_aq = float(best.get("aesthetic_quality") or 0.0)
        w_aq = float(worse.get("aesthetic_quality") or 0.0)
        dims = list(worse.get("top_failing_dimensions") or [])[:3]
        pairs.append(
            {
                "preferred": best.get("artifact_ref"),
                "rejected": worse.get("artifact_ref"),
                "preferred_aq": b_aq,
                "rejected_aq": w_aq,
                "rationale": (
                    f"Higher gated AQ ({b_aq} > {w_aq}); "
                    f"weaker on {', '.join(dims) if dims else 'overall quality'}."
                ),
                "dimensions": dims,
                "source": "compare_ranking",
            }
        )
    return pairs
