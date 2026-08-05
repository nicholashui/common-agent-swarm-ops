"""Markdown rendering for AestheticVerdict (spec §7.2 JSON + Markdown)."""

from __future__ import annotations

from typing import Any


def format_verdict_markdown(verdict: dict[str, Any]) -> str:
    """Human-readable critique card for handoffs / HiTL review."""
    aq = verdict.get("aesthetic_quality")
    hack = verdict.get("hack_likelihood")
    profile = verdict.get("profile_id") or "unknown"
    artifact = verdict.get("artifact_ref") or ""
    mode = verdict.get("mode") or "score"
    escalate = bool(verdict.get("escalate_to_hitl"))
    uncertainty = bool(verdict.get("uncertainty_flag"))

    lines = [
        f"# Aesthetic verdict — `{artifact}`",
        "",
        f"- **Profile:** `{profile}`",
        f"- **Mode:** `{mode}`",
        f"- **Aesthetic quality (gated):** `{aq}`",
        f"- **Hack likelihood:** `{hack}`",
        f"- **Intent fidelity:** `{verdict.get('intent_fidelity')}`",
        f"- **Emotion match:** `{verdict.get('emotion_match')}`",
        f"- **Escalate to HiTL:** `{escalate}`",
        f"- **Uncertainty:** `{uncertainty}`",
        "",
        "## Vector (D1–D10)",
        "",
    ]
    vector = verdict.get("aesthetic_vector") or {}
    conf = verdict.get("confidence") or {}
    if isinstance(vector, dict):
        for dim, score in vector.items():
            c = conf.get(dim, "—") if isinstance(conf, dict) else "—"
            lines.append(f"- **{dim}:** {score} (conf {c})")
    failing = verdict.get("top_failing_dimensions") or []
    if failing:
        lines.extend(["", f"**Top failing:** {', '.join(str(d) for d in failing)}", ""])
    critiques = verdict.get("actionable_critique") or []
    if critiques:
        lines.extend(["## Actionable critique", ""])
        for c in critiques[:8]:
            lines.append(f"- {c}")
    steers = verdict.get("prompt_steer_hints") or []
    if steers:
        lines.extend(["", "## Prompt steers", ""])
        for s in steers[:6]:
            lines.append(f"- {s}")
    note = (verdict.get("note") or "").strip()
    if note:
        lines.extend(["", f"_{note}_"])
    return "\n".join(lines).strip() + "\n"
