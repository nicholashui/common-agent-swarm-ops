"""Offline Critic — deterministic multi-head AestheticVector (spec §§4–6).

No network, no live vision models. Scores derive from artifact_ref digest so
CI and dry-runs are reproducible.
"""

from __future__ import annotations

from hashlib import sha256
from typing import Any

from app.aesthetics.models import AESTHETIC_DIMENSIONS, ACTIVATION_POLICY


def _unit(digest: bytes, offset: int) -> float:
    """Map two digest bytes at offset to [0.05, 0.98]."""
    i = offset % max(1, len(digest) - 1)
    raw = digest[i] * 256 + digest[(i + 1) % len(digest)]
    return 0.05 + (raw / 65535.0) * 0.93


def score_artifact(
    *,
    artifact_ref: str,
    media_type: str,
    profile_weights: dict[str, float],
    intent_text: str,
    emotional_target: dict[str, float],
    tier: str = "fast",
    constraints: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Return aesthetic_vector, confidence, gates, and intermediate AQ parts."""
    seed = f"{artifact_ref}|{media_type}|{tier}".encode("utf-8", errors="replace")
    digest = sha256(seed).digest()

    vector: dict[str, float] = {}
    confidence: dict[str, float] = {}
    for idx, dim in enumerate(AESTHETIC_DIMENSIONS):
        vector[dim] = round(_unit(digest, idx * 2), 4)
        confidence[dim] = round(0.55 + _unit(digest, 20 + idx) * 0.4, 4)

    # Temporal dimension only meaningful for video — still always present
    if media_type == "image":
        vector["temporal"] = round(min(1.0, vector["temporal"] * 0.85 + 0.1), 4)

    # Soft constraint nudges (offline heuristic — not live detectors)
    cons = constraints or {}
    if (cons.get("color_space") or "").strip():
        # Declared color space → slight technical/color confidence boost
        vector["color_harmony"] = round(min(0.98, vector["color_harmony"] + 0.03), 4)
        vector["technical"] = round(min(0.98, vector["technical"] + 0.02), 4)
    if (cons.get("aspect_ratio") or "").strip():
        vector["composition"] = round(min(0.98, vector["composition"] + 0.02), 4)
    if (cons.get("deliverable") or "").upper() in {"HDR", "HDR10", "DOLBY_VISION"}:
        vector["technical"] = round(min(0.98, vector["technical"] + 0.03), 4)
        vector["light"] = round(min(0.98, vector["light"] + 0.02), 4)

    # Intent fidelity: higher when intent text non-empty and shares tokens with ref
    intent = (intent_text or "").strip().lower()
    if not intent:
        intent_fidelity = 0.55
    else:
        tokens = [t for t in intent.replace(",", " ").split() if len(t) > 2]
        hit = sum(1 for t in tokens if t in artifact_ref.lower())
        intent_fidelity = round(0.45 + min(0.5, 0.08 * max(1, hit) + 0.1 * min(5, len(tokens))), 4)

    valence = float(emotional_target.get("valence", 0.0))
    arousal = float(emotional_target.get("arousal", 0.0))
    # Stub emotion match: distance of digest-derived affect from target
    pred_v = _unit(digest, 40) * 2 - 1
    pred_a = _unit(digest, 42)
    emotion_match = round(
        max(0.05, 1.0 - 0.5 * abs(pred_v - valence) - 0.4 * abs(pred_a - arousal)),
        4,
    )

    # Anti-hack: synthetic OOD + ensemble disagreement from digest tails
    ood = _unit(digest, 50)
    disagreement = _unit(digest, 52)
    hack_likelihood = round(min(0.95, 0.35 * ood + 0.45 * disagreement), 4)

    # Profile-weighted aggregate G(A, w_p)
    weights = {d: float(profile_weights.get(d, 1.0)) for d in AESTHETIC_DIMENSIONS}
    w_sum = sum(max(0.0, w) for w in weights.values()) or 1.0
    g = sum(vector[d] * max(0.0, weights[d]) for d in AESTHETIC_DIMENSIONS) / w_sum
    g = max(0.0, min(1.0, g))

    aq = g * intent_fidelity * emotion_match * (1.0 - hack_likelihood)
    aq = round(max(0.0, min(1.0, aq)), 4)

    # Top failing dimensions (lowest scores)
    ordered = sorted(AESTHETIC_DIMENSIONS, key=lambda d: vector[d])
    top_failing = list(ordered[:3])

    low_conf = any(confidence[d] < 0.65 for d in AESTHETIC_DIMENSIONS)
    escalate = hack_likelihood >= 0.55 or low_conf or aq < 0.25

    return {
        "aesthetic_vector": vector,
        "confidence": confidence,
        "intent_fidelity": intent_fidelity,
        "emotion_match": emotion_match,
        "hack_likelihood": hack_likelihood,
        "aesthetic_quality": aq,
        "top_failing_dimensions": top_failing,
        "uncertainty_flag": low_conf,
        "escalate_to_hitl": escalate,
        "ensemble_agreement": round(1.0 - disagreement, 4),
        "gated_parts": {
            "profiled_aggregate": round(g, 4),
            "intent_fidelity": intent_fidelity,
            "emotion_match": emotion_match,
            "anti_hack": round(1.0 - hack_likelihood, 4),
        },
        "constraints_applied": {
            "aspect_ratio": (cons.get("aspect_ratio") or "").strip() or None,
            "color_space": (cons.get("color_space") or "").strip() or None,
            "deliverable": (cons.get("deliverable") or "").strip() or None,
        },
        "activation_policy": dict(ACTIVATION_POLICY),
    }
