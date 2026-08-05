"""Offline General Creative Agent (GCA) foundation — SSOR-lite ideation.

Process-local, deterministic multi-POV → sparse outliers → value-gate ranking.
Not full GCA MCTS, live LLM SSOR, FAISS/Chroma, NLAE, or CreativeAgentFactory.
"""

from __future__ import annotations

import math
import re
import threading
from hashlib import sha256
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

_TOKEN = re.compile(r"[a-z0-9]+", re.I)

ACTIVATION_POLICY: dict[str, Any] = {
    "production_gca": False,
    "live_generation": False,
    "mcts": False,
    "mode": "offline_ssor_lite",
    "learned_patterns_scope": "process_local",
    "note": (
        "Offline GCA SSOR-lite foundation: multi-POV mapping, sparse outliers "
        "(≤4), novelty/usefulness/coherence/feasibility value-gate, phase_trace, "
        "integration/refinement notes, process-local learned patterns. "
        "Not live LLM SSOR, FAISS/Chroma, NLAE, MCTS, durable memory, "
        "or CreativeAgentFactory."
    ),
}

# Human-role POVs used offline (AI-native NLAE modes are not claimed live).
_BASE_POVS: list[dict[str, str]] = [
    {"name": "audience_first", "description": "What the viewer notices and feels first"},
    {"name": "constraint_craft", "description": "Budget, format, and production limits as creative fuel"},
    {"name": "emotional_arc", "description": "Beat-level affect change across the piece"},
    {"name": "visual_grammar", "description": "Framing, light, color, and cut language"},
    {"name": "sound_design", "description": "Diegetic vs score and silence as structure"},
    {"name": "narrative_structure", "description": "Hook, turn, and payoff skeleton"},
    {"name": "brand_or_intent", "description": "Fidelity to brief intent without hard-sell noise"},
    {"name": "risk_edge", "description": "Where safe convention can be strategically broken"},
]

_DOMAIN_EXTRA_POVS: dict[str, list[dict[str, str]]] = {
    "video": [
        {"name": "edit_rhythm", "description": "Cut tempo and montage vs held takes"},
        {"name": "format_aspect", "description": "9:16 / 16:9 / square composition rules"},
    ],
    "scientific": [
        {"name": "hypothesis_space", "description": "Falsifiable claim and measurement path"},
        {"name": "prior_art", "description": "Conventional literature vs atypical combinations"},
    ],
    "artistic": [
        {"name": "medium_material", "description": "Material, palette, and form language"},
        {"name": "intertextual", "description": "Dialogue with existing works without pastiche"},
    ],
    "business": [
        {"name": "stakeholder_value", "description": "Who pays, who benefits, who blocks"},
        {"name": "go_to_market", "description": "Distribution and adoption friction"},
    ],
    "engineering": [
        {"name": "system_constraints", "description": "Reliability, latency, and failure modes"},
        {"name": "interface_contract", "description": "API and operator surface clarity"},
    ],
    "educational": [
        {"name": "learner_model", "description": "Prior knowledge and misconception risk"},
        {"name": "transfer", "description": "What skill should transfer after exposure"},
    ],
}

# Domain value-gate weights for U,Q,F emphasis (N/K still enter via balance).
_DOMAIN_WEIGHTS: dict[str, dict[str, float]] = {
    "video": {"novelty": 1.0, "usefulness": 1.05, "coherence": 1.0, "feasibility": 1.1},
    "scientific": {"novelty": 1.15, "usefulness": 1.1, "coherence": 1.15, "feasibility": 0.95},
    "artistic": {"novelty": 1.2, "usefulness": 0.9, "coherence": 1.05, "feasibility": 0.9},
    "business": {"novelty": 0.95, "usefulness": 1.2, "coherence": 1.0, "feasibility": 1.15},
    "engineering": {"novelty": 0.9, "usefulness": 1.1, "coherence": 1.15, "feasibility": 1.25},
    "educational": {"novelty": 0.95, "usefulness": 1.15, "coherence": 1.2, "feasibility": 1.05},
}

_OUTLIER_POOL: list[str] = [
    "single-practical light character study",
    "kinetic montage with diegetic sound motif",
    "split-world contrast (day/night palette shift)",
    "object-as-protagonist micro-narrative",
    "audience POV confession structure",
    "time-loop reveal in final beat",
    "found-footage authenticity frame",
    "tabletop tableau → live-action match cut",
    "silence-first then music surge",
    "brand product as McGuffin only once",
    "ensemble cross-cut three locations",
    "negative-space typography cold open",
    "inverted causality cold open",
    "constraint-as-aesthetic (one location only)",
    "unreliable narrator via cutaway only",
    "scientific anomaly as emotional beat",
]

_PHASE_NAMES = (
    "multi_pov_mapping",
    "normal_range_definition",
    "sparse_outlier_sampling",
    "cross_dimensional_recombination",
    "value_gated_selection",
    "integration_refinement",
    "output",
)


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class CreativeIdeateRequest(StrictModel):
    brief: str = Field(min_length=1, max_length=8_000)
    n_candidates: int = Field(default=4, ge=1, le=12)
    genre: str = Field(default="", max_length=120)
    domain: str = Field(default="", max_length=80)
    allow_live_generation: bool = False


class CreativeService:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._runs: list[dict[str, Any]] = []

    @property
    def activation_policy(self) -> dict[str, Any]:
        return dict(ACTIVATION_POLICY)

    def policy(self) -> dict[str, Any]:
        return {
            "activation_policy": self.activation_policy,
            "modes": ["ideate", "rank", "direction", "patterns", "handoff"],
            "ssor_lite": {
                "formula": "Cr = B(N,K) · U · Q · F",
                "max_outlier_dimensions": 4,
                "phases": list(_PHASE_NAMES),
                "domains": sorted(_DOMAIN_WEIGHTS.keys()),
                "integration_refinement": True,
                "learned_patterns_scope": "process_local",
                "next_agent_handoff": True,
            },
            "agent_id": "specials.general-creative-agent",
            "linked_agents": [
                "video.ideation",
                "video.creativedirector",
                "video.novelty",
                "video.director",
            ],
            "host_entrypoints": [
                "POST /api/v1/creative/ideate",
                "GET /api/v1/creative/patterns",
                "GET /api/v1/creative/runs",
                "GET /api/v1/creative/policy",
            ],
            "note": ACTIVATION_POLICY["note"],
        }

    def ideate(self, request: CreativeIdeateRequest) -> dict[str, Any]:
        if request.allow_live_generation:
            return {
                "ok": False,
                "error": (
                    "Live generative creativity is not enabled. "
                    "Fail-closed offline ideation only."
                ),
                "activation_policy": self.activation_policy,
            }

        brief = request.brief.strip()
        genre = (request.genre or "").strip() or _guess_genre(brief)
        domain = _normalize_domain(request.domain, brief, genre)
        n = request.n_candidates
        weights = dict(_DOMAIN_WEIGHTS[domain])
        povs = _build_povs(domain)
        digest = sha256(
            f"{brief}|{genre}|{domain}|{n}".encode("utf-8", errors="replace")
        ).hexdigest()

        # Phase 1–2: multi-POV map + normal (conventional) ranges per POV
        normal_ranges = {
            p["name"]: _normal_range_for_pov(p["name"], brief, genre, domain) for p in povs
        }
        phase_trace: list[dict[str, Any]] = [
            {
                "phase": "multi_pov_mapping",
                "status": "ok",
                "detail": f"{len(povs)} offline POVs for domain={domain}",
                "pov_names": [p["name"] for p in povs],
            },
            {
                "phase": "normal_range_definition",
                "status": "ok",
                "detail": "Conventional consequence bands per POV (deterministic stub)",
                "normal_range_keys": list(normal_ranges.keys()),
            },
        ]

        candidates: list[dict[str, Any]] = []
        for i in range(n):
            cand = _build_candidate(
                index=i,
                brief=brief,
                genre=genre,
                domain=domain,
                digest=digest,
                povs=povs,
                normal_ranges=normal_ranges,
                weights=weights,
            )
            candidates.append(cand)

        phase_trace.append(
            {
                "phase": "sparse_outlier_sampling",
                "status": "ok",
                "detail": "Strategic sparse outliers (1–4 dimensions) per candidate",
                "max_outliers": 4,
            }
        )
        phase_trace.append(
            {
                "phase": "cross_dimensional_recombination",
                "status": "ok",
                "detail": "Seed motif recombined with brief tokens and outlier labels",
            }
        )

        candidates.sort(key=lambda c: (-float(c["overall_cr"]), c["candidate_id"]))
        phase_trace.append(
            {
                "phase": "value_gated_selection",
                "status": "ok",
                "detail": "Ranked by offline Cr = B(N,K)·U·Q·F with domain weights",
                "best_candidate_id": candidates[0]["candidate_id"] if candidates else None,
            }
        )

        # Phase 6: offline integration & refinement (audit fields; no live self-critique LLM)
        for cand in candidates:
            _apply_integration_refinement(cand, domain=domain, brief=brief)
        phase_trace.append(
            {
                "phase": "integration_refinement",
                "status": "ok",
                "detail": (
                    "Offline risks/mitigations + refinement notes per candidate "
                    "(not live ECN self-critique)"
                ),
            }
        )

        best = candidates[0] if candidates else None
        next_agents = _next_agents_for_domain(domain)
        direction = {
            "logline": f"A {genre or 'video'} piece that {brief[:160]}",
            "tone": _tone(brief),
            "visual_pillar": best["concept"] if best else brief[:120],
            "must_haves": _must_haves(brief),
            "avoid": ["generic stock b-roll only", "naked scalar beauty without intent"],
            "next_agents": next_agents,
            "domain": domain,
        }
        handoff = _build_handoff(best=best, direction=direction, domain=domain, genre=genre)
        phase_trace.append(
            {
                "phase": "output",
                "status": "ok",
                "detail": "Direction pack + ranked candidates + next-agent handoff (offline SSOR-lite)",
            }
        )

        # Process-local patterns from prior successful runs only (not this run yet)
        with self._lock:
            learned_patterns = _learned_patterns_from_runs(self._runs)

        run_id = f"gca_{digest[:12]}"
        payload = {
            "ok": True,
            "run_id": run_id,
            "genre": genre,
            "domain": domain,
            "domain_weights": weights,
            "povs": povs,
            "phase_trace": phase_trace,
            "candidates": candidates,
            "best_candidate_id": best["candidate_id"] if best else None,
            "creative_direction": direction,
            "handoff": handoff,
            "learned_patterns": learned_patterns,
            "learned_patterns_scope": "process_local",
            "activation_policy": self.activation_policy,
            "note": ACTIVATION_POLICY["note"],
            "patterns_used": [
                "MultiPOVMapping",
                "SparseOutlierSampling",
                "Recombination",
                "ValueGate_SSOR_lite",
                "IntegrationRefinement",
                "DirectionPack",
                "NextAgentHandoff",
            ],
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

    def learned_patterns(self, *, limit: int = 12) -> list[dict[str, Any]]:
        """Process-local successful motifs from prior offline runs (not durable)."""
        with self._lock:
            return _learned_patterns_from_runs(self._runs, limit=limit)

    def patterns(self, *, limit: int = 12) -> dict[str, Any]:
        """Lean Host entry: process-local motifs without full run history dump."""
        items = self.learned_patterns(limit=limit)
        return {
            "ok": True,
            "items": items,
            "count": len(items),
            "scope": "process_local",
            "learned_patterns_scope": "process_local",
            "activation_policy": self.activation_policy,
            "note": (
                "Process-local learned motifs from successful offline ideate runs "
                "in this Host process only. Not durable memory or live model update."
            ),
        }


def _normalize_domain(domain: str, brief: str, genre: str) -> str:
    d = (domain or "").strip().lower().replace("-", "_").replace(" ", "_")
    aliases = {
        "video": "video",
        "film": "video",
        "cinema": "video",
        "cinematic": "video",
        "scientific": "scientific",
        "science": "scientific",
        "research": "scientific",
        "artistic": "artistic",
        "art": "artistic",
        "business": "business",
        "product": "business",
        "engineering": "engineering",
        "eng": "engineering",
        "educational": "educational",
        "education": "educational",
        "pedagogy": "educational",
    }
    if d in aliases:
        return aliases[d]
    if d in _DOMAIN_WEIGHTS:
        return d
    # Infer from brief/genre when domain omitted
    b = f"{brief} {genre}".lower()
    if any(k in b for k in ("hypothesis", "experiment", "paper", "lab")):
        return "scientific"
    if any(k in b for k in ("canvas", "gallery", "poem", "sculpture")):
        return "artistic"
    if any(k in b for k in ("roi", "stakeholder", "gtm", "go-to-market", "startup")):
        return "business"
    if any(k in b for k in ("latency", "api", "reliability", "system design")):
        return "engineering"
    if any(k in b for k in ("lesson", "curriculum", "learner", "classroom")):
        return "educational"
    return "video"


def _build_povs(domain: str) -> list[dict[str, str]]:
    extra = _DOMAIN_EXTRA_POVS.get(domain, _DOMAIN_EXTRA_POVS["video"])
    # Cap at 10 offline POVs (spec wants 8–12; we stay lean offline)
    return list(_BASE_POVS) + list(extra)


def _normal_range_for_pov(name: str, brief: str, genre: str, domain: str) -> dict[str, Any]:
    return {
        "conventional": f"expected {name} choices for {genre or domain}",
        "high_probability": [
            "clear single intent",
            "readable primary subject",
            f"genre-typical {genre or domain} cues",
        ],
        "brief_anchor": brief[:80],
    }


def _build_candidate(
    *,
    index: int,
    brief: str,
    genre: str,
    domain: str,
    digest: str,
    povs: list[dict[str, str]],
    normal_ranges: dict[str, dict[str, Any]],
    weights: dict[str, float],
) -> dict[str, Any]:
    seed_idx = (int(digest[index * 2 : index * 2 + 2], 16) + index * 3) % len(_OUTLIER_POOL)
    seed = _OUTLIER_POOL[seed_idx]

    # Sparse outliers: 1–4 dimensions drawn from POVs (deterministic)
    n_out = 1 + ((int(digest[(index + 3) % 30 : (index + 3) % 30 + 2], 16) + index) % 4)
    n_out = max(1, min(4, n_out))
    start = (seed_idx + index) % len(povs)
    outlier_dimensions: list[str] = []
    for j in range(n_out):
        outlier_dimensions.append(povs[(start + j * 2) % len(povs)]["name"])
    # unique preserve order
    seen: set[str] = set()
    outlier_dimensions = [x for x in outlier_dimensions if not (x in seen or seen.add(x))][:4]

    concept = f"[{genre or domain}] {seed} — grounded in: {brief[:120]}"
    pov_map = [
        {
            "name": p["name"],
            "description": p["description"],
            "is_outlier": p["name"] in outlier_dimensions,
            "normal_range": normal_ranges.get(p["name"], {}).get("conventional", ""),
        }
        for p in povs
    ]

    novelty = _novelty_score(concept, brief, index, outlier_dimensions)
    combination = _combination_score(outlier_dimensions, seed, brief)
    usefulness = _usefulness_score(concept, brief, domain, weights)
    coherence = _coherence_score(concept, brief, outlier_dimensions, weights)
    feasibility = _feasibility_score(concept, brief, n_out, weights)

    # Inverted-U balance on total surprise (N and rare-combination K)
    total_surprise = max(0.0, min(1.0, 0.55 * novelty + 0.45 * combination))
    balance = _balance_function(total_surprise)

    # Domain-weighted product Cr = B · U · Q · F (scores already weight-scaled)
    raw = balance * usefulness * coherence * feasibility
    overall_cr = round(max(0.01, min(0.99, raw)), 4)
    # Backward-compatible alias used by older callers
    ssor = overall_cr

    cand_digest = sha256(
        f"{digest}|{index}|{seed}|{','.join(outlier_dimensions)}".encode(
            "utf-8", errors="replace"
        )
    ).hexdigest()

    return {
        "candidate_id": f"gca_{cand_digest[:12]}",
        "concept": concept,
        "seed_motif": seed,
        "multi_pov": pov_map,
        "outlier_dimensions": outlier_dimensions,
        "outlier_count": len(outlier_dimensions),
        "surprise_vector": {
            "pov_scores": {
                p["name"]: (0.75 if p["name"] in outlier_dimensions else 0.25)
                for p in povs[:8]
            },
            "total_surprise": round(total_surprise, 4),
            "outlier_dimensions": list(outlier_dimensions),
        },
        "novelty": novelty,
        "combination_rarity": combination,
        "usefulness": usefulness,
        "coherence": coherence,
        "feasibility": feasibility,
        "balance_b": round(balance, 4),
        "overall_cr": overall_cr,
        "ssor": ssor,
        "prompt_steer": (
            f"emphasize {seed}; outlier on {', '.join(outlier_dimensions)}; "
            f"stay faithful to brief constraints"
        ),
        "risk": "may feel generic" if novelty < 0.4 else "manage complexity",
        "transformational": n_out >= 3 and novelty >= 0.55,
        "prototype_plan": (
            f"1) Lock brief intent 2) Prototype {seed} on {outlier_dimensions[0]} "
            f"3) Gate on usefulness/feasibility for domain={domain}"
        ),
    }


def _apply_integration_refinement(
    cand: dict[str, Any], *, domain: str, brief: str
) -> None:
    """Attach offline integration/refinement audit fields (mutates candidate)."""
    risk = str(cand.get("risk") or "unspecified risk")
    novelty = float(cand.get("novelty") or 0)
    feasibility = float(cand.get("feasibility") or 0)
    outliers = list(cand.get("outlier_dimensions") or [])
    mitigations: list[str] = [
        "Re-check brief intent fidelity before locking the direction pack",
    ]
    if novelty < 0.45:
        mitigations.append("Raise one sparse outlier dimension without dropping usefulness")
    if feasibility < 0.55:
        mitigations.append("Cut production scope to one location / practical light path")
    if len(outliers) >= 3:
        mitigations.append("Keep at most two active outlier beats in the final cut")
    if domain == "video" and any(k in brief.lower() for k in ("15s", "30s", "60s")):
        mitigations.append("Timebox cold open and payoff for short-form duration")

    cand["risks_mitigations"] = {
        "risk": risk,
        "mitigations": mitigations,
    }
    seed = str(cand.get("seed_motif") or "motif")
    primary = outliers[0] if outliers else "audience_first"
    cand["refinement_note"] = (
        f"Refine {seed} by anchoring {primary}; protect coherence≥threshold "
        f"and re-score feasibility for domain={domain} before handoff."
    )
    # Keep legacy single-string risk for older callers
    cand["risk"] = risk


def _learned_patterns_from_runs(
    runs: list[dict[str, Any]], *, limit: int = 12
) -> list[dict[str, Any]]:
    """Extract successful best-candidate motifs from process-local run history."""
    limit = max(1, min(limit, 50))
    out: list[dict[str, Any]] = []
    seen_motifs: set[str] = set()
    for run in runs:
        if not run.get("ok"):
            continue
        best_id = run.get("best_candidate_id")
        cands = run.get("candidates") or []
        best = next((c for c in cands if c.get("candidate_id") == best_id), None)
        if best is None and cands:
            best = cands[0]
        if not best:
            continue
        motif = str(best.get("seed_motif") or best.get("concept") or "")[:160]
        if not motif or motif in seen_motifs:
            continue
        seen_motifs.add(motif)
        out.append(
            {
                "seed_motif": motif,
                "domain": run.get("domain"),
                "overall_cr": best.get("overall_cr"),
                "outlier_dimensions": list(best.get("outlier_dimensions") or [])[:4],
                "run_id": run.get("run_id"),
                "scope": "process_local",
            }
        )
    return out[-limit:]


def _balance_function(total_surprise: float) -> float:
    """Inverted-U: peaks near moderate surprise (~0.5)."""
    return math.exp(-((total_surprise - 0.5) ** 2) / (2 * 0.15**2))


def _novelty_score(
    concept: str, brief: str, idx: int, outliers: list[str]
) -> float:
    ct = set(_TOKEN.findall(concept.lower()))
    bt = set(_TOKEN.findall(brief.lower()))
    overlap = len(ct & bt) / max(1, len(ct))
    base = 0.32 + 0.07 * ((idx * 3) % 7) + 0.22 * (1.0 - min(1.0, overlap))
    base += 0.04 * min(4, len(outliers))
    return round(min(0.95, base), 4)


def _combination_score(outliers: list[str], seed: str, brief: str) -> float:
    # Sparse rare-combination proxy: more distinct outliers + uncommon seed tokens
    rarity = 0.35 + 0.12 * len(outliers)
    if "→" in seed or "only" in seed.lower():
        rarity += 0.08
    brief_l = brief.lower()
    if any(k in brief_l for k in ("noir", "wuxia", "ugc")) and "montage" in seed.lower():
        rarity += 0.06
    return round(max(0.1, min(0.95, rarity)), 4)


def _usefulness_score(
    concept: str, brief: str, domain: str, weights: dict[str, float]
) -> float:
    b = brief.lower()
    score = 0.5
    if any(k in concept.lower() for k in ("brief", "constraint", "product", "character")):
        score += 0.1
    if any(k in b for k in ("15s", "30s", "60s", "short")) and "montage" in concept.lower():
        score += 0.15
    if domain == "business" and any(k in b for k in ("brand", "product", "campaign")):
        score += 0.08
    if domain == "educational" and any(k in b for k in ("learn", "teach", "lesson")):
        score += 0.08
    if "generic" in concept.lower():
        score -= 0.2
    score *= weights.get("usefulness", 1.0)
    return round(max(0.1, min(0.95, score)), 4)


def _coherence_score(
    concept: str,
    brief: str,
    outliers: list[str],
    weights: dict[str, float],
) -> float:
    # Reachability proxy: fewer outliers + brief token presence → higher coherence
    ct = set(_TOKEN.findall(concept.lower()))
    bt = set(_TOKEN.findall(brief.lower()))
    overlap = len(ct & bt) / max(1, min(12, len(bt)))
    score = 0.55 + 0.25 * min(1.0, overlap) - 0.04 * max(0, len(outliers) - 2)
    score *= weights.get("coherence", 1.0)
    return round(max(0.15, min(0.95, score)), 4)


def _feasibility_score(
    concept: str, brief: str, n_out: int, weights: dict[str, float]
) -> float:
    b = brief.lower()
    score = 0.7 - 0.05 * max(0, n_out - 2)
    if any(k in b for k in ("budget", "low budget", "practical", "one location")):
        score += 0.1
    if "ensemble" in concept.lower() and "budget" in b:
        score -= 0.12
    if "found-footage" in concept.lower() or "practical" in concept.lower():
        score += 0.05
    score *= weights.get("feasibility", 1.0)
    return round(max(0.15, min(0.95, score)), 4)


def _guess_genre(brief: str) -> str:
    b = brief.lower()
    for g, keys in (
        ("noir", ("noir", "crime", "shadow")),
        ("ugc_ad", ("ugc", "ad", "tiktok", "product")),
        ("documentary", ("doc", "interview", "true story")),
        ("comedy", ("comedy", "funny", "sketch")),
        ("wuxia", ("wuxia", "martial", "sword")),
    ):
        if any(k in b for k in keys):
            return g
    return "cinematic_short"


def _tone(brief: str) -> str:
    b = brief.lower()
    if any(k in b for k in ("dark", "noir", "tragic")):
        return "low-key serious"
    if any(k in b for k in ("upbeat", "fun", "comedy", "ugc")):
        return "energetic approachable"
    return "cinematic measured"


def _must_haves(brief: str) -> list[str]:
    out = ["intent fidelity to brief", "one clear audience takeaway"]
    b = brief.lower()
    if "9:16" in b or "vertical" in b:
        out.append("vertical composition safe margins")
    if "brand" in b or "product" in b:
        out.append("product readability without hard-sell overload")
    return out


def _next_agents_for_domain(domain: str) -> list[str]:
    base = ["video.director", "video.screenwriter", "specials.aesthetics-agent"]
    extras = {
        "scientific": ["specials.research-agent", "specials.thinking-model"],
        "artistic": ["specials.aesthetics-agent", "video.moodboard"],
        "business": ["specials.optimization-agent", "specials.strategic-goal-achievement-agent"],
        "engineering": ["specials.coding-agent", "specials.complex-problem-solution-process-model"],
        "educational": ["specials.thinking-model", "specials.knowledge-router-agent"],
        "video": ["video.creativedirector", "video.novelty"],
    }
    extra = extras.get(domain, extras["video"])
    # unique preserve order
    seen: set[str] = set()
    out: list[str] = []
    for a in base + extra:
        if a not in seen:
            seen.add(a)
            out.append(a)
    return out[:6]


def _build_handoff(
    *,
    best: dict[str, Any] | None,
    direction: dict[str, Any],
    domain: str,
    genre: str,
) -> dict[str, Any]:
    """Explicit next-agent handoff for Host orchestration (offline only)."""
    next_agents = list(direction.get("next_agents") or _next_agents_for_domain(domain))
    return {
        "best_candidate_id": best.get("candidate_id") if best else None,
        "concept": best.get("concept") if best else "",
        "prompt_steer": best.get("prompt_steer") if best else "",
        "overall_cr": best.get("overall_cr") if best else None,
        "seed_motif": best.get("seed_motif") if best else "",
        "refinement_note": best.get("refinement_note") if best else "",
        "risks_mitigations": best.get("risks_mitigations") if best else {},
        "creative_direction": {
            "logline": direction.get("logline", ""),
            "tone": direction.get("tone", ""),
            "visual_pillar": direction.get("visual_pillar", ""),
            "must_haves": list(direction.get("must_haves") or []),
            "avoid": list(direction.get("avoid") or []),
            "domain": domain,
            "genre": genre,
        },
        "next_agents": next_agents,
        "recommended_tools": [
            "aesthetics.evaluate",
            "screenwriting.plan",
            "creative.patterns",
        ],
        "scope": "offline_host_handoff",
        "note": (
            "Use this package for Host orchestration handoff; "
            "not a live multi-agent factory spawn."
        ),
    }


_SERVICE: CreativeService | None = None
_LOCK = threading.Lock()


def get_creative_service() -> CreativeService:
    global _SERVICE
    with _LOCK:
        if _SERVICE is None:
            _SERVICE = CreativeService()
        return _SERVICE


def reset_creative_service_for_tests() -> CreativeService:
    global _SERVICE
    with _LOCK:
        _SERVICE = CreativeService()
        return _SERVICE
