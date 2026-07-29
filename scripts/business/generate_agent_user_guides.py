#!/usr/bin/env python3
"""Generate rich docs/user_guide.md for every video + specials pack agent.

Design intent (what operators/architects actually need):
  - Understand the agent's mission without reading raw SPEC dumps
  - Decide when to involve it in a human or multi-agent workflow
  - Operate it safely on CASOPS (inspect, propose, swarm) under fail-closed rules
  - Improve quality over time without mutating published versions in place
  - Audit provenance: what is binding host config vs historical design corpus

Sources (synthesized, not dumped):
  - business/{video|specials}/agents/<id>/SPEC.md, agent_spec.json, README.md
  - sources/MAPPING.md, PROVENANCE.json, sources/excerpts/*, sources/generic/*
  - C:\\Project\\va-agent-swarm (study/agents.md + related markdown)
  - docs/special_agents_redesign/agents/*.md (specials historical design)

Output:
  business/.../agents/<id>/docs/user_guide.md
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_VA_ROOT = Path(r"C:\Project\va-agent-swarm")
_SPECIALS_REDESIGN = _ROOT / "docs" / "special_agents_redesign" / "agents"
_PACKS = (
    _ROOT / "business" / "video" / "agents",
    _ROOT / "business" / "specials" / "agents",
)

_TABLE_ROW = re.compile(
    r"^\|\s*(\d+)\s*\|\s*\*\*([^*]+)\*\*\s*\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|",
    re.M,
)

# Video VA category → production placement (heuristic for operator guidance)
_CATEGORY_PHASE: dict[str, dict[str, str]] = {
    "1-ATL": {
        "label": "Above-the-line leadership",
        "human": "Development and pre-production: creative vision, greenlight, script, casting leadership.",
        "ai": "Early DAG nodes that set intent, constraints, and approval gates before generation and craft agents run.",
        "handoffs": "Briefs, treatments, shot intents, series bibles, greenlight decisions.",
    },
    "2-Cam": {
        "label": "Camera & lighting craft",
        "human": "Principal photography / virtual production: image capture language and lighting.",
        "ai": "Generation and look-dev nodes that turn director intent into camera/lighting packages.",
        "handoffs": "Shot lists, lighting plots, camera packages, look references.",
    },
    "3-Edit": {
        "label": "Editorial & finishing",
        "human": "Post-production editorial, color, and picture finish.",
        "ai": "Cut assembly, grade, and picture QC nodes with critique loops against director/audience judges.",
        "handoffs": "Cuts, timelines, grades, continuity notes, QC tickets.",
    },
    "4-Sound": {
        "label": "Sound & music",
        "human": "Sound design, mix, score, and music supervision.",
        "ai": "Audio generation, stem assembly, loudness/mix validation, music rights-aware packaging.",
        "handoffs": "Stems, cue sheets, mix masters, music packages.",
    },
    "5-Perf": {
        "label": "Performance & choreography",
        "human": "Talent performance direction, movement, and on-screen presence.",
        "ai": "Performance simulation, choreography, casting/voice fit, avatar performance packages.",
        "handoffs": "Performance notes, movement scores, cast/voice selections.",
    },
    "6-Dist": {
        "label": "Distribution & marketing",
        "human": "Release packaging, go-to-market, channel ops.",
        "ai": "Launch packaging, metadata, campaign variants, and outlet-spec delivery branches.",
        "handoffs": "Launch kits, metadata, trailers, channel packages.",
    },
    "7-Edu": {
        "label": "Education & domain expertise",
        "human": "Subject-matter accuracy and instructional packaging.",
        "ai": "Domain grounding, instructional design, LMS packaging, learner simulation.",
        "handoffs": "Lesson packages, SME reviews, LMS bundles, assessment artifacts.",
    },
    "8-AI": {
        "label": "AI-era synthetic specialists",
        "human": "Synthetic media, clone, avatar, and deepfake-risk crafts that did not exist classically.",
        "ai": "Specialized generative nodes with strong provenance, consent, and forensic gates.",
        "handoffs": "Synthetic assets, consent records, forensic scores, identity hashes.",
    },
    "9-Meta": {
        "label": "Meta / optimization specialists",
        "human": "Cross-cutting optimization, evaluation, and system improvement roles.",
        "ai": "Observer and optimizer nodes over the full agent graph (latency, cost, prompts, retention, ROAS).",
        "handoffs": "Eval reports, optimization tickets, benchmark deltas, harness results.",
    },
    "10-Sup": {
        "label": "Workflow support & release gates",
        "human": "Support functions and final release gates (accessibility, brand, legal, archive, etc.).",
        "ai": "Gate and support nodes that accept/reject handoffs before publish or after launch.",
        "handoffs": "Gate decisions, compliance packs, accessibility layers, archive masters, corrections.",
    },
}

# Specials agents: capability families for placement guidance
_SPECIALS_FAMILY: dict[str, dict[str, str]] = {
    "planner": {
        "family": "Planning & decomposition",
        "use_when": "Large corpora must become hierarchical, evidence-traced plans and tasks.",
        "upstream": "Intent analysis, research, knowledge routing.",
        "downstream": "Controller, agent-loop creator, coding/execution agents.",
    },
    "controller": {
        "family": "Control & orchestration",
        "use_when": "Multiple specialists need coordinated execution with policy and budget.",
        "upstream": "Planner / strategic goal agents.",
        "downstream": "Specialist workers and evaluation loops.",
    },
    "intent": {
        "family": "Intent understanding",
        "use_when": "User goals are ambiguous and must be clarified before planning.",
        "upstream": "Raw user requests / product briefs.",
        "downstream": "Planner, research, knowledge router.",
    },
    "research": {
        "family": "Research & evidence gathering",
        "use_when": "Claims need external or corpus-backed evidence before synthesis.",
        "upstream": "Intent / planner questions.",
        "downstream": "Planner, RAG, strategy agents.",
    },
    "rag": {
        "family": "Retrieval-augmented reasoning",
        "use_when": "Answers must stay grounded in a controlled knowledge base.",
        "upstream": "Knowledge router / research.",
        "downstream": "Planner, creative, recommendation agents.",
    },
    "knowledge": {
        "family": "Knowledge routing",
        "use_when": "Queries must be directed to the right corpus, agent, or memory tier.",
        "upstream": "Intent analysis.",
        "downstream": "RAG, research, domain specialists.",
    },
    "optimization": {
        "family": "Optimization & self-improvement",
        "use_when": "Loops, prompts, or plans need measurable improvement under constraints.",
        "upstream": "Eval / critique outputs.",
        "downstream": "Controller, planner, agent-loop creator.",
    },
    "loop": {
        "family": "Agent-loop design",
        "use_when": "You need a reusable think–act–critique loop for a new specialty.",
        "upstream": "Planner / technology advisor.",
        "downstream": "Controller runtime and pack agents.",
    },
    "creative": {
        "family": "General creative synthesis",
        "use_when": "Open-ended creative generation under brand or aesthetic constraints.",
        "upstream": "Aesthetics / intent / strategic goal.",
        "downstream": "Domain pack craft agents (e.g. video).",
    },
    "aesthetics": {
        "family": "Aesthetic judgment",
        "use_when": "Taste, style coherence, and visual/sonic quality must be judged.",
        "upstream": "Creative outputs.",
        "downstream": "Creative director / craft agents; optimization.",
    },
    "psych": {
        "family": "Psychological modeling",
        "use_when": "Audience or user psychology should shape recommendations or narratives.",
        "upstream": "Research / intent.",
        "downstream": "Recommendation, creative, strategic goal agents.",
    },
    "strategic": {
        "family": "Strategic goal achievement",
        "use_when": "Long-horizon goals need staged plans with measurable milestones.",
        "upstream": "Intent / research.",
        "downstream": "Planner, controller, domain packs.",
    },
    "tech": {
        "family": "Technology advisory",
        "use_when": "Stack, model, or tooling choices need evidence-based advice.",
        "upstream": "Research / requirements.",
        "downstream": "Planner, agent-loop creator, controller.",
    },
    "llm": {
        "family": "LLM usage policy",
        "use_when": "Model selection, budgets, and safe LLM usage patterns must be governed.",
        "upstream": "Controller / planner requests.",
        "downstream": "All LLM-calling agents.",
    },
    "podcast": {
        "family": "Podcast / long-form audio production",
        "use_when": "Episode structure, dialogue, or audio-first packaging is the deliverable.",
        "upstream": "Research / creative / strategic goal.",
        "downstream": "Audio craft and distribution agents.",
    },
    "autotelic": {
        "family": "Intrinsic motivation / exploration",
        "use_when": "The system should explore useful subgoals without an external reward every step.",
        "upstream": "Controller / strategic goal.",
        "downstream": "Research, optimization, creative branches.",
    },
    "complex": {
        "family": "Complex problem-solving process",
        "use_when": "Ill-structured problems need an explicit multi-stage solution process model.",
        "upstream": "Intent / research.",
        "downstream": "Planner, strategic goal, controller.",
    },
}


def _read(path: Path, limit: int | None = None) -> str:
    if not path.is_file():
        return ""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    if limit is not None and len(text) > limit:
        return text[:limit] + "\n\n…(truncated)…"
    return text


def _section(markdown: str, heading: str) -> str:
    pattern = re.compile(
        rf"^##\s+{re.escape(heading)}\s*\n(.*?)(?=^##\s+|\Z)",
        re.S | re.M | re.I,
    )
    match = pattern.search(markdown)
    return match.group(1).strip() if match else ""


def _humanize(agent_id: str) -> str:
    bare = agent_id.split(".", 1)[-1]
    return " ".join(p.capitalize() for p in re.split(r"[-_.]+", bare) if p)


def _collapse_ws(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def _first_sentences(text: str, *, max_chars: int = 600, max_sentences: int = 4) -> str:
    text = _collapse_ws(text)
    if not text:
        return ""
    # Drop markdown tables / code fences early
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"\|[^|\n]+\|", " ", text)
    text = _collapse_ws(text)
    parts = re.split(r"(?<=[.!?])\s+", text)
    out: list[str] = []
    size = 0
    for p in parts:
        if len(p) < 12:
            continue
        if size + len(p) > max_chars and out:
            break
        out.append(p)
        size += len(p)
        if len(out) >= max_sentences:
            break
    return " ".join(out) if out else text[:max_chars]


def _ensure_sentence(text: str) -> str:
    text = _collapse_ws(text)
    if not text:
        return ""
    if text[-1] not in ".!?":
        text += "."
    return text


def _as_bullet_lines(text: str, *, max_items: int = 12) -> list[str]:
    """Preserve list structure from SPEC sections instead of collapsing to one paragraph."""
    items: list[str] = []
    for raw in (text or "").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("|") and line.count("|") >= 2:
            continue
        if line.startswith("- ") or line.startswith("* "):
            line = line[2:].strip()
        elif re.match(r"^\d+\.\s+", line):
            line = re.sub(r"^\d+\.\s+", "", line)
        if len(line) < 6:
            continue
        items.append(line)
        if len(items) >= max_items:
            break
    if not items and text:
        one = _first_sentences(text, max_chars=500, max_sentences=3)
        if one:
            items.append(one)
    return items


def _strip_historical_noise(text: str) -> str:
    """Remove oversized embedded tables and repeated historical blobs from SPEC sections."""
    if not text:
        return ""
    # Cut at VA Domain Pack specification body / category roster dumps
    cut_markers = (
        "### VA Domain Pack specification body",
        "Category roster section",
        "### Domain distillation (embedded",
        "```text",
        "```json",
    )
    for marker in cut_markers:
        idx = text.find(marker)
        if idx > 80:
            text = text[:idx].strip()
    # Drop pure table blocks
    lines = []
    for line in text.splitlines():
        if line.strip().startswith("|") and line.count("|") >= 3:
            continue
        if set(line.strip()) <= {"|", "-", ":", " "}:
            continue
        lines.append(line)
    return "\n".join(lines).strip()


def _extract_field_blocks(spec_md: str) -> dict[str, str]:
    """Pull labeled historical subsections from video SPECs."""
    labels = {
        "knowledge": r"(?:Knowledge distillation sources|Knowledge distillation)[^\n]*\n+(.*?)(?=\n###|\n##|\Z)",
        "quality": r"(?:Self-quality criteria)[^\n]*\n+(.*?)(?=\n###|\n##|\Z)",
        "surpass": r"(?:Surpass-human signal)[^\n]*\n+(.*?)(?=\n###|\n##|\Z)",
        "accepts": r"(?:Accepts critique from)[:\s*]*([^\n]+)",
        "comments": r"(?:Comments on)[:\s*]*([^\n]+)",
        "tools": r"(?:Tools design-time notes|Tool access)[^\n]*\n+(.*?)(?=\n###|\n\*\*Runtime|\n##|\Z)",
        "architecture": r"(?:Architecture pattern)[^\n]*\n+(.*?)(?=\n###|\n##|\Z)",
        "responsibility_va": r"(?:Responsibility \(from VA table\))[^\n]*\n+(.*?)(?=\n###|\n##|\Z)",
    }
    out: dict[str, str] = {}
    for key, pat in labels.items():
        m = re.search(pat, spec_md, re.S | re.I)
        if m:
            out[key] = _collapse_ws(m.group(1))
    return out


def _load_va_agent_table(va_root: Path) -> dict[str, dict[str, str]]:
    path = va_root / "study" / "agents.md"
    text = _read(path)
    by_key: dict[str, dict[str, str]] = {}
    for match in _TABLE_ROW.finditer(text):
        va_id, name, responsibility, knowledge, quality, surpass, accepts, comments, tools, architecture = (
            match.group(i).strip() for i in range(1, 11)
        )
        name_clean = name.strip()
        name_key = re.sub(r"[^a-z0-9]+", "", name_clean.lower())
        row = {
            "va_id": va_id,
            "name": name_clean,
            "responsibility": responsibility,
            "knowledge": knowledge,
            "quality": quality,
            "surpass": surpass,
            "accepts_critique": accepts,
            "comments_on": comments,
            "tools": tools,
            "architecture": architecture,
            "source_path": str(path),
        }
        by_key[name_key] = row
        by_key[f"id:{va_id}"] = row
        by_key[re.sub(r"agent$", "", name_key)] = row
    return by_key


def _index_va_markdown(va_root: Path) -> list[tuple[str, Path, str]]:
    if not va_root.is_dir():
        return []
    out: list[tuple[str, Path, str]] = []
    for path in va_root.rglob("*.md"):
        try:
            if path.stat().st_size > 2_000_000:
                continue
        except OSError:
            continue
        name = path.name.lower()
        try:
            head = path.read_text(encoding="utf-8", errors="replace")[:3500]
        except OSError:
            head = ""
        out.append((name, path, head))
    return out


def _find_va_related(
    index: list[tuple[str, Path, str]],
    tokens: list[str],
    *,
    limit: int = 10,
) -> list[tuple[Path, str, int]]:
    hits: list[tuple[int, Path, str]] = []
    tokens_l = [t.lower() for t in tokens if len(t) >= 3]
    for name, path, head in index:
        score = 0
        blob = f"{name}\n{head[:1200]}".lower()
        for tok in tokens_l:
            if tok in name:
                score += 5
            elif tok in blob:
                score += 1
        if score:
            hits.append((score, path, head[:600]))
    hits.sort(key=lambda x: (-x[0], str(x[1])))
    seen: set[Path] = set()
    out: list[tuple[Path, str, int]] = []
    for score, path, head in hits:
        if path in seen:
            continue
        seen.add(path)
        out.append((path, head, score))
        if len(out) >= limit:
            break
    return out


def _specials_design_doc(agent_id: str) -> tuple[Path | None, str]:
    if not agent_id.startswith("specials."):
        return None, ""
    bare = agent_id.removeprefix("specials.")
    stem = bare.replace("-", "_")
    candidates = [
        _SPECIALS_REDESIGN / f"{stem}.md",
        _SPECIALS_REDESIGN / f"{bare}.md",
        _SPECIALS_REDESIGN / f"{stem.replace('_', '-')}.md",
    ]
    if _SPECIALS_REDESIGN.is_dir():
        for path in _SPECIALS_REDESIGN.glob("*.md"):
            n = path.stem.lower().replace("_", "-")
            if bare in n or n in bare or bare.replace("-", "") in n.replace("-", ""):
                candidates.insert(0, path)
    for path in candidates:
        if path is not None and path.is_file():
            return path, _read(path, 12000)
    return None, ""


def _match_va_row(
    table: dict[str, dict[str, str]],
    agent_id: str,
    spec: dict,
    spec_md: str,
    *,
    pack: str,
) -> dict[str, str] | None:
    """Match VA roster rows carefully.

    Specials agents must NOT inherit video craft rows by bare-name collision
    (e.g. specials.planner-agent ≠ video PlannerAgent).
    """
    va_id = str(spec.get("va_id") or "")
    if va_id and f"id:{va_id}" in table:
        return table[f"id:{va_id}"]
    va_name = str(spec.get("va_name") or "")
    if va_name:
        key = re.sub(r"[^a-z0-9]+", "", va_name.lower())
        if key in table:
            return table[key]
        key2 = re.sub(r"agent$", "", key)
        if key2 in table:
            return table[key2]
    m = re.search(r"upstream_name\D+\*\*([^*]+)\*\*", spec_md, re.I)
    if m:
        key = re.sub(r"[^a-z0-9]+", "", m.group(1).lower())
        if key in table:
            return table[key]
    # Name-based fallback is only safe for video pack (VA Domain Pack taxonomy).
    if pack != "video":
        return None
    bare = agent_id.split(".", 1)[-1]
    key = re.sub(r"[^a-z0-9]+", "", bare.lower()) + "agent"
    if key in table:
        return table[key]
    key2 = re.sub(r"[^a-z0-9]+", "", bare.lower())
    if key2 in table:
        return table[key2]
    return None


def _collect_local_sources(agent_dir: Path) -> list[tuple[str, Path, str]]:
    """Return (rel, path, trust_tier)."""
    sources: list[tuple[str, Path, str]] = []
    binding = [
        ("agent_spec.json", "binding"),
        ("SPEC.md", "authoritative-design"),
        ("README.md", "local-index"),
        ("sources/MAPPING.md", "provenance"),
        ("sources/PROVENANCE.json", "provenance"),
    ]
    for rel, tier in binding:
        path = agent_dir / rel
        if path.is_file():
            sources.append((rel, path, tier))
    excerpts = agent_dir / "sources" / "excerpts"
    if excerpts.is_dir():
        for path in sorted(excerpts.glob("*.md")):
            sources.append((f"sources/excerpts/{path.name}", path, "historical-excerpt"))
    generic = agent_dir / "sources" / "generic"
    if generic.is_dir():
        for path in sorted(generic.glob("*.md")):
            sources.append((f"sources/generic/{path.name}", path, "historical-generic"))
    return sources


def _specials_family(agent_id: str) -> dict[str, str]:
    bare = agent_id.removeprefix("specials.").lower()
    # ordered keyword match
    order = [
        ("planner", "planner"),
        ("controller", "controller"),
        ("intent", "intent"),
        ("research", "research"),
        ("rag", "rag"),
        ("agentic-rag", "rag"),
        ("knowledge", "knowledge"),
        ("optim", "optimization"),
        ("loop", "loop"),
        ("creative", "creative"),
        ("aesthetic", "aesthetics"),
        ("psych", "psych"),
        ("strategic", "strategic"),
        ("screenwriter-strategic", "strategic"),
        ("tech", "tech"),
        ("techology", "tech"),
        ("llm", "llm"),
        ("podcast", "podcast"),
        ("autotelic", "autotelic"),
        ("complex", "complex"),
    ]
    for needle, key in order:
        if needle in bare:
            return _SPECIALS_FAMILY[key]
    return {
        "family": "Specials meta-capability",
        "use_when": "Cross-cutting special capability is required outside a pure domain craft pack.",
        "upstream": "Intent / planner / controller depending on the request.",
        "downstream": "Domain pack agents or human review gates.",
    }


def _category_info(spec: dict, pack: str) -> dict[str, str]:
    if pack == "specials":
        return {
            "label": "Specials meta-agent pack",
            "human": "Works above domain craft crews: planning, routing, retrieval, control, and strategy.",
            "ai": "Meta-layer nodes that shape how specialist agents are selected, informed, and improved.",
            "handoffs": "Plans, routes, evidence packs, control decisions, optimization tickets.",
        }
    cat = str(spec.get("va_category") or "")
    # normalize variants like "10-Sup"
    for key, info in _CATEGORY_PHASE.items():
        if key.lower() in cat.lower() or cat.lower() in key.lower():
            return info
    # prefix match on leading number
    m = re.match(r"(\d+)", cat)
    if m:
        num = m.group(1)
        for key, info in _CATEGORY_PHASE.items():
            if key.startswith(num + "-") or key.startswith(num):
                return info
    return {
        "label": f"Category `{cat or 'unknown'}`",
        "human": "Map this agent into the production phase that matches its responsibility.",
        "ai": "Place the agent on the multi-agent DAG near peers that share critique edges.",
        "handoffs": "Typed manifests with acceptance criteria and provenance.",
    }


def _mission_paragraph(
    title: str,
    pack: str,
    agent_id: str,
    responsibility: str,
    va_row: dict[str, str] | None,
    fields: dict[str, str],
) -> str:
    if pack == "specials":
        core = _ensure_sentence(
            _first_sentences(responsibility, max_chars=420, max_sentences=3)
            or f"Provides the specials capability `{agent_id}`."
        )
        return (
            f"**{title}** (`{agent_id}`) is a Specials pack capability on CASOPS. "
            f"In plain terms: {core} "
            "Use this guide to understand design intent, safe host usage, and how the capability "
            "should eventually sit in multi-agent planning or control loops."
        )
    core = (
        (va_row or {}).get("responsibility")
        or fields.get("responsibility_va")
        or _first_sentences(responsibility, max_chars=420, max_sentences=3)
        or f"Owns domain outcomes for `{agent_id}`."
    )
    core = _ensure_sentence(_first_sentences(core, max_chars=420, max_sentences=3))
    return (
        f"**{title}** (`{agent_id}`) is a Video Domain Pack role on CASOPS. "
        f"In plain terms: {core} "
        "Treat this guide as the human-readable operator map for catalog review, "
        "swarm design, and proposal-driven improvement — not as a runtime activation license."
    )


def _why_exists(
    title: str,
    pack: str,
    responsibility: str,
    va_row: dict[str, str] | None,
    fields: dict[str, str],
    specials_doc: str,
) -> list[str]:
    lines: list[str] = []
    knowledge = (va_row or {}).get("knowledge") or fields.get("knowledge") or ""
    surpass = (va_row or {}).get("surpass") or fields.get("surpass") or ""
    resp = _first_sentences(
        (va_row or {}).get("responsibility") or _strip_historical_noise(responsibility),
        max_chars=500,
        max_sentences=4,
    )
    if pack == "video":
        lines.append(
            f"Human video crews already solve this problem under time pressure: "
            f"{_ensure_sentence(resp or 'craft ownership for a specialized gate or role')} "
            f"The agent form exists so the multi-agent system can **encode that craft continuously**, "
            "apply it on every handoff, and escalate only the residual risk to humans."
        )
        if knowledge and knowledge != "—":
            lines.append(
                f"Its knowledge base is distilled from: **{_first_sentences(knowledge, max_chars=280, max_sentences=2)}** "
                "— historical design sources, not live network calls on this host."
            )
        if surpass and surpass != "—":
            lines.append(
                f"The design ambition (surpass-human signal) is: "
                f"*{_ensure_sentence(_first_sentences(surpass, max_chars=220, max_sentences=2))}* "
                "Use that as the north-star metric when you write evals or proposals later."
            )
    else:
        lines.append(
            "Specials agents capture **cross-domain cognitive skills** that domain craft packs should not reinvent. "
            f"This role's design outcome: {_ensure_sentence(resp or 'a self-contained specials capability for offline review')}"
        )
        if specials_doc:
            m = re.search(
                r"(?:##\s*(?:Executive Summary|Core Problem|Primary Goal)[^\n]*\n)(.*?)(?=\n##\s|\Z)",
                specials_doc,
                re.S | re.I,
            )
            if m:
                summary = _first_sentences(m.group(1), max_chars=450, max_sentences=4)
                if summary:
                    lines.append(f"From the historical redesign document: {_ensure_sentence(summary)}")
        if knowledge and knowledge != "—":
            lines.append(
                f"Reference knowledge themes: {_ensure_sentence(_first_sentences(knowledge, max_chars=260, max_sentences=2))}"
            )
    return lines


def _when_to_call(
    pack: str,
    title: str,
    responsibility: str,
    va_row: dict[str, str] | None,
    cat_info: dict[str, str],
    family: dict[str, str] | None,
) -> list[str]:
    resp = _first_sentences(
        (va_row or {}).get("responsibility") or responsibility,
        max_chars=200,
        max_sentences=1,
    )
    if pack == "video":
        return [
            f"**Call this agent when** the work product needs a decision or artifact owned by *{title}*: {resp or 'see responsibility above.'}",
            f"**Pipeline phase:** {cat_info['label']}. {cat_info['human']}",
            "**Do not call it for** generic orchestration, budget greenlight, or final legal sign-off unless those duties are explicitly in its responsibility — use producer/legal/compliance peers instead.",
            "**Human override:** any release-blocking safety, rights, or accessibility dispute escalates to a human gate even if the agent would auto-pass in a future active runtime.",
        ]
    assert family is not None
    return [
        f"**Call this capability when:** {family['use_when']}",
        f"**Capability family:** {family['family']}",
        f"**Typical upstream:** {family['upstream']}",
        f"**Typical downstream:** {family['downstream']}",
        f"**Concrete mission fragment:** {resp or title}",
        "**Do not use it as** a silent production activator or credential broker — specials stay data-only / draft until governance says otherwise.",
    ]


def _workflow_agent_snippet(agent_dir: Path, title: str, va_name: str) -> dict[str, str]:
    """Find agent-specific mentions in local workflow excerpts instead of dumping whole files."""
    result: dict[str, str] = {}
    names = {title, va_name, title.replace("Agent", ""), va_name.replace("Agent", "")}
    names = {n for n in names if n and len(n) > 2}
    for kind, rel in (
        ("ai", "sources/excerpts/ai_agent_video_production_workflow.md"),
        ("human", "sources/excerpts/human_video_production_workflow.md"),
    ):
        path = agent_dir / rel
        text = _read(path)
        if not text:
            continue
        chunks: list[str] = []
        for block in re.split(r"\n{2,}", text):
            if not any(n.lower() in block.lower() for n in names):
                continue
            # Prefer prose over raw markdown tables / ASCII diagrams
            if block.count("|") >= 6 and "---" in block:
                # Extract the matching table row(s) only
                for line in block.splitlines():
                    if any(n.lower() in line.lower() for n in names) and line.strip().startswith("|"):
                        cells = [c.strip() for c in line.strip().strip("|").split("|")]
                        cells = [c for c in cells if c and not set(c) <= {"-"}]
                        if cells:
                            chunks.append(" — ".join(cells)[:400])
                continue
            cleaned = _collapse_ws(re.sub(r"[`*#]+", " ", block))
            cleaned = re.sub(r"\s{2,}", " ", cleaned)
            if 40 < len(cleaned) < 500:
                chunks.append(cleaned)
            if len(chunks) >= 3:
                break
        if chunks:
            result[kind] = "\n".join(f"- {c}" for c in chunks[:3])
        else:
            head = _first_sentences(text[:1200], max_chars=320, max_sentences=2)
            if head:
                result[f"{kind}_generic"] = head
    return result


def _display_title(agent_id: str, spec: dict, spec_md: str, pack: str) -> str:
    if spec.get("va_name"):
        return str(spec["va_name"])
    # Prefer SPEC H1
    m = re.search(r"^#\s+(.+)$", spec_md, re.M)
    if m:
        return m.group(1).strip()
    if pack == "specials":
        bare = agent_id.removeprefix("specials.")
        return " ".join(p.capitalize() for p in bare.replace("_", "-").split("-") if p)
    return _humanize(agent_id)


def _clean_design_excerpt(text: str, *, max_chars: int = 420) -> str:
    """Strip redesign boilerplate (changelogs, headings) down to a usable mission sentence."""
    if not text:
        return ""
    # Cut before change logs / TOC / version banners
    for stopper in (
        "\n---",
        "\n## Change",
        "\n## Table of Contents",
        "\n# ",
        "\n## ",
        "Change Summary",
        "Version:",
        "Date:",
        "Status:",
    ):
        idx = text.find(stopper)
        if idx > 30:
            text = text[:idx]
    text = re.sub(r"^#+\s+.*$", " ", text, flags=re.M)
    text = re.sub(r"\*+", "", text)
    text = _collapse_ws(text)
    return _first_sentences(text, max_chars=max_chars, max_sentences=2)


def _specials_mission_from_design(specials_doc: str, responsibility_raw: str) -> str:
    """Prefer redesign primary goal / executive summary over accidental video VA matches."""
    if specials_doc:
        # Line-anchored primary goal first (most reliable)
        m = re.search(
            r"(?im)^\s*(?:\*\*)?Primary Goal(?:\*\*)?\s*[:：]\s*(.+?)\s*$",
            specials_doc,
        )
        if m:
            got = _clean_design_excerpt(m.group(1), max_chars=420)
            if got and len(got) > 40:
                return got
        for pat in (
            r"(?is)##\s*\d*\.?\s*Executive Summary\s*\n(.*?)(?=\n##\s|\Z)",
            r"(?is)##\s*\d*\.?\s*Core Problem\s*\n(.*?)(?=\n##\s|\Z)",
            r"(?is)##\s*\d*\.?\s*Purpose\s*\n(.*?)(?=\n##\s|\Z)",
        ):
            m = re.search(pat, specials_doc)
            if m:
                got = _clean_design_excerpt(m.group(1), max_chars=420)
                if got and len(got) > 40:
                    return got
    # SPEC responsibility often starts with generic "Owns the specials-domain..." — take first real sentence
    cleaned = _strip_historical_noise(responsibility_raw)
    # Prefer the long domain paragraph if present after the generic first line
    parts = [p.strip() for p in re.split(r"\n\s*\n", cleaned) if p.strip()]
    for part in parts:
        # skip generic owns-the-specials boilerplate
        if re.match(r"(?i)^owns the specials-domain", part):
            continue
        if "data-only" in part.lower() and len(part) < 180:
            continue
        got = _clean_design_excerpt(part, max_chars=420)
        if got and len(got) > 40:
            return got
    return _clean_design_excerpt(cleaned, max_chars=420)


def _readme_summary(readme: str) -> str:
    if not readme:
        return ""
    # drop title line, take first bullets
    lines = []
    for line in readme.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        if s.startswith(">"):
            s = s.lstrip("> ").strip()
        lines.append(s)
        if sum(len(x) for x in lines) > 500:
            break
    return " ".join(lines)[:600]


def generate_user_guide(
    agent_dir: Path,
    *,
    pack: str,
    va_table: dict[str, dict[str, str]],
    va_index: list[tuple[str, Path, str]],
    va_root: Path,
) -> str:
    agent_id = agent_dir.name
    spec_path = agent_dir / "agent_spec.json"
    try:
        spec = json.loads(spec_path.read_text(encoding="utf-8")) if spec_path.is_file() else {}
    except (OSError, json.JSONDecodeError):
        spec = {}
    spec_md = _read(agent_dir / "SPEC.md")
    readme = _read(agent_dir / "README.md")
    mapping = _read(agent_dir / "sources" / "MAPPING.md")
    provenance_raw = _read(agent_dir / "sources" / "PROVENANCE.json")
    try:
        provenance = json.loads(provenance_raw) if provenance_raw else {}
    except json.JSONDecodeError:
        provenance = {}

    role = str(spec.get("role") or "")
    status = str(spec.get("status") or "unknown")
    fields = _extract_field_blocks(spec_md)

    responsibility_raw = _strip_historical_noise(_section(spec_md, "Responsibility"))
    boundaries = _strip_historical_noise(_section(spec_md, "Boundaries and escalation"))
    io_sec = _strip_historical_noise(_section(spec_md, "Inputs and outputs"))
    quality_sec = _strip_historical_noise(_section(spec_md, "Quality and critique"))
    runtime_sec = _section(spec_md, "Runtime binding")
    local_knowledge = _strip_historical_noise(_section(spec_md, "Local knowledge sources"))
    provenance_sec = _strip_historical_noise(_section(spec_md, "Provenance"))

    specials_path, specials_doc = _specials_design_doc(agent_id)
    title = _display_title(agent_id, spec, spec_md, pack)
    va_row = _match_va_row(va_table, agent_id, spec, spec_md, pack=pack)

    tokens = [
        agent_id,
        agent_id.split(".", 1)[-1],
        title,
        title.replace("Agent", ""),
        str(spec.get("va_name") or ""),
        str(spec.get("previous_common_agent_id") or provenance.get("previous_common_agent_id") or ""),
    ]
    if pack == "specials":
        tokens.append(agent_id.removeprefix("specials."))
        # Prefer redesign filename tokens over video-craft collisions
        if specials_path:
            tokens.append(specials_path.stem)
    va_hits = _find_va_related(va_index, tokens, limit=10)
    local_sources = _collect_local_sources(agent_dir)
    cat_info = _category_info(spec, pack)
    family = _specials_family(agent_id) if pack == "specials" else None
    wf_snip = _workflow_agent_snippet(agent_dir, title, str(spec.get("va_name") or title))

    knowledge = (va_row or {}).get("knowledge") or fields.get("knowledge") or "—"
    quality = (va_row or {}).get("quality") or fields.get("quality") or "—"
    surpass = (va_row or {}).get("surpass") or fields.get("surpass") or "—"
    accepts = (va_row or {}).get("accepts_critique") or fields.get("accepts") or "—"
    comments = (va_row or {}).get("comments_on") or fields.get("comments") or "—"
    tools = (va_row or {}).get("tools") or fields.get("tools") or "—"
    architecture = (va_row or {}).get("architecture") or fields.get("architecture") or "—"

    if pack == "specials":
        responsibility = (
            _specials_mission_from_design(specials_doc, responsibility_raw)
            or f"Specials capability for `{agent_id}`."
        )
        # Family-aware quality defaults (SPEC quality section is host-binding, not craft rubric)
        fam = family or _specials_family(agent_id)
        if quality == "—":
            quality = (
                f"Traceable outputs for {fam['family'].lower()}; "
                "fail-closed schema validation; no silent production activation"
            )
        if architecture == "—":
            architecture = (
                f"{fam['family']} pattern — design-time hierarchical/multi-agent loops; "
                "host remains local_deterministic data-only until gated"
            )
        if surpass == "—":
            surpass = (
                f"Produces more consistent {fam['family'].lower()} outcomes than ad-hoc human process "
                "under the same corpus constraints"
            )
        if accepts == "—":
            accepts = "Human governance; peer specials (intent, research, controller, optimization)"
        if comments == "—":
            comments = f"Gaps in {fam['family'].lower()}, missing evidence, unsafe activation, weak handoffs"
        if tools == "—":
            tools = "None on host (fail-closed); redesign docs may name retrieval/planning tools historically"
    else:
        responsibility = (
            (va_row or {}).get("responsibility")
            or fields.get("responsibility_va")
            or _first_sentences(responsibility_raw, max_chars=500, max_sentences=4)
            or f"Domain outcomes for `{agent_id}`."
        )
    responsibility = _ensure_sentence(responsibility)

    model_policy = spec.get("model_policy") if isinstance(spec.get("model_policy"), dict) else {}
    budget = spec.get("budget_policy") if isinstance(spec.get("budget_policy"), dict) else {}
    edges = spec.get("critique_edges") if isinstance(spec.get("critique_edges"), dict) else {}
    allowed_tools = spec.get("allowed_tools") if isinstance(spec.get("allowed_tools"), list) else []
    prev_id = provenance.get("previous_common_agent_id") or spec.get("previous_common_agent_id")

    L: list[str] = []
    # ── Title & purpose ──────────────────────────────────────────
    L.append(f"# {title} — Operator & Design Guide")
    L.append("")
    L.append(
        "> **Who this is for:** operators, pack authors, swarm designers, and reviewers "
        "working in `common-agent-swarm-ops`."
    )
    L.append(
        "> **What you will get:** mission clarity, when-to-use guidance, collaboration map, "
        "CASOPS operating steps, improvement path, and a trust-tiered source map."
    )
    L.append(">")
    L.append(
        "> **What this is not:** a license to activate providers, open network access, or invent tools. "
        "Host truth is fail-closed `agent_spec.json`. Design text from VA / redesign docs is **untrusted provenance**."
    )
    L.append("")
    L.append(
        f"*Pack path:* `business/{pack}/agents/{agent_id}/` · "
        f"*Guide:* `docs/user_guide.md` · "
        f"*Generated by* `scripts/business/generate_agent_user_guides.py`"
    )
    L.append("")

    # ── 1 Snapshot ───────────────────────────────────────────────
    L.append("## 1. Snapshot")
    L.append("")
    # Prefer resolved responsibility string for mission prose
    mission_src = responsibility if pack == "specials" else responsibility_raw
    L.append(_mission_paragraph(title, pack, agent_id, mission_src, va_row, fields))
    L.append("")
    L.append("| | |")
    L.append("|---|---|")
    L.append(f"| **Display name** | {title} |")
    L.append(f"| **Pack agent id** | `{agent_id}` |")
    L.append(f"| **Pack** | `{pack}` |")
    L.append(f"| **Host role string** | {role or '—'} |")
    L.append(f"| **Catalog status** | `{status}` |")
    L.append(f"| **Maturity today** | L0 / non-active (catalog & design fidelity) |")
    L.append(f"| **VA id** | `{spec.get('va_id', '—')}` |")
    L.append(f"| **VA category** | `{spec.get('va_category', pack)}` — {cat_info['label']} |")
    L.append(f"| **Provider (host)** | `{model_policy.get('provider', '—')}` |")
    L.append(f"| **Network** | `{model_policy.get('network_access', False)}` |")
    L.append(f"| **Allowed tools (host)** | `{allowed_tools or []}` |")
    L.append(f"| **Production activation requested** | `{spec.get('production_activation_requested', False)}` |")
    L.append(f"| **Prompt / rubric refs** | `{spec.get('prompt_reference', '—')}` / `{spec.get('rubric_reference', '—')}` |")
    if prev_id:
        L.append(f"| **Previous common id** | `{prev_id}` |")
    if provenance.get("generic_source"):
        L.append(f"| **Generic lineage** | `{provenance.get('generic_source')}` |")
    L.append("")

    # ── 2 Why it exists ──────────────────────────────────────────
    L.append("## 2. Why this role exists")
    L.append("")
    why_src = responsibility if pack == "specials" else responsibility_raw
    for para in _why_exists(title, pack, why_src, va_row, fields, specials_doc):
        L.append(para)
        L.append("")

    # ── 3 Outcomes & quality ─────────────────────────────────────
    L.append("## 3. What good looks like")
    L.append("")
    L.append("Use these as **review criteria** when reading outputs, writing rubrics, or scoring proposals.")
    L.append("")
    L.append(f"- **Primary outcome:** {responsibility}")
    L.append(f"- **Self-quality bar:** {quality}")
    L.append(f"- **Ambition signal (design-time):** {surpass}")
    L.append(f"- **Architecture pattern (design-time):** {architecture}")
    if quality_sec:
        L.append("")
        L.append("### Host quality & critique binding")
        L.append("")
        for item in _as_bullet_lines(quality_sec, max_items=10):
            L.append(f"- {item}")
    L.append("")
    if io_sec:
        L.append("### Inputs → outputs → acceptance")
        L.append("")
        for item in _as_bullet_lines(io_sec, max_items=12):
            L.append(f"- {item}")
        L.append("")
    else:
        L.append("### Inputs → outputs → acceptance")
        L.append("")
        L.append("- **Inputs:** local pack artifacts, typed handoffs, and governance records already on disk.")
        L.append("- **Outputs:** reviewable domain deliverables with explicit acceptance criteria.")
        L.append("- **Acceptance:** host policy + SPEC criteria; fail closed without a separate activation gate.")
        L.append("")

    # ── 4 Scope ──────────────────────────────────────────────────
    L.append("## 4. Scope: owns, shares, and refuses")
    L.append("")
    L.append(f"### Owns")
    L.append("")
    L.append(f"{responsibility}")
    L.append("")
    L.append("### Shares with peers (critique surface)")
    L.append("")
    L.append(f"- **Listens to / accepts critique from:** {accepts}")
    L.append(f"- **Is qualified to comment on:** {comments}")
    if edges:
        L.append(f"- **Host critique edge inputs:** `{edges.get('inputs')}`")
        L.append(f"- **Host critique edge outputs:** `{edges.get('outputs')}`")
        L.append(f"- **Max refinement count:** `{spec.get('max_refinement_count', '—')}`")
    L.append("")
    L.append("### Refuses / escalates")
    L.append("")
    if boundaries:
        for line in boundaries.splitlines():
            s = line.strip()
            if s:
                L.append(s if s.startswith("-") else f"- {s}")
    else:
        L.append("- No provider activation, network, or credentials from design text.")
        L.append("- No production activation without a separate human governance gate.")
        L.append("- Safety, legal, rights, and release decisions escalate to humans.")
    L.append("")

    # ── 5 When to call ───────────────────────────────────────────
    L.append("## 5. When to involve this agent")
    L.append("")
    when_src = responsibility if pack == "specials" else responsibility_raw
    for bullet in _when_to_call(pack, title, when_src, va_row, cat_info, family):
        L.append(f"- {bullet}")
    L.append("")
    L.append("### Decision cheat-sheet")
    L.append("")
    L.append("| Question | Guidance |")
    L.append("|----------|----------|")
    L.append(f"| Is the missing skill *{title}*'s craft? | Yes → include in the swarm graph for that phase. |")
    L.append("| Is this only a metadata/catalog edit? | Use Registry inspect + proposal — do not invent runtime. |")
    L.append("| Does the task need tools/network? | Host currently disallows unless `agent_spec` + permission register say otherwise. |")
    L.append("| Is there a human-only risk (legal, harm, rights)? | Keep a human gate; agent output is advisory until activated. |")
    L.append("")

    # ── 6 Collaboration ──────────────────────────────────────────
    L.append("## 6. Collaboration map")
    L.append("")
    L.append(
        "Think of this agent as a **node on a critique bus**, not a standalone chatbot. "
        "Peers refine quality; judges/gates decide acceptance."
    )
    L.append("")
    L.append("| Direction | Agents / topics |")
    L.append("|-----------|-----------------|")
    L.append(f"| **Inbound critique** | {accepts} |")
    L.append(f"| **Outbound commentary** | {comments} |")
    L.append(f"| **Host edge inputs** | {edges.get('inputs', '—')} |")
    L.append(f"| **Host edge outputs** | {edges.get('outputs', '—')} |")
    L.append("")
    if pack == "specials" and family:
        L.append("### Specials lane placement")
        L.append("")
        L.append(f"- **Family:** {family['family']}")
        L.append(f"- **Upstream:** {family['upstream']}")
        L.append(f"- **Downstream:** {family['downstream']}")
        L.append("")

    # ── 7 Production placement ───────────────────────────────────
    L.append("## 7. Where it sits in production")
    L.append("")
    L.append("### 7.1 Human production workflow")
    L.append("")
    L.append(cat_info["human"])
    L.append("")
    L.append(f"**Typical handoff artifacts:** {cat_info['handoffs']}")
    L.append("")
    if wf_snip.get("human"):
        L.append("**Mentions in local human-workflow excerpt:**")
        L.append("")
        L.append(wf_snip["human"])
        L.append("")
    elif wf_snip.get("human_generic"):
        L.append(
            f"*No agent-specific human-workflow paragraph found; general human production framing:* "
            f"{wf_snip['human_generic']}"
        )
        L.append("")
    else:
        L.append(
            "Map the responsibility into classic phases: development → pre-production → production → "
            "post-production → delivery / live ops. Prefer the phase where a human with this job title would sign off."
        )
        L.append("")

    L.append("### 7.2 Multi-agent AI workflow")
    L.append("")
    L.append(cat_info["ai"])
    L.append("")
    L.append(
        f"Design-time tool notes (non-binding on host): {_first_sentences(str(tools), max_chars=280, max_sentences=2)}"
    )
    L.append("")
    L.append(
        f"Loop style to emulate when you later implement runtime: **{architecture}**. "
        "On CASOPS today, that pattern is documentation only — the live provider is local deterministic "
        "with empty or stub tool allow-lists."
    )
    L.append("")
    if wf_snip.get("ai"):
        L.append("**Mentions in local AI-workflow excerpt:**")
        L.append("")
        L.append(wf_snip["ai"])
        L.append("")
    elif wf_snip.get("ai_generic"):
        L.append(
            f"*General AI production architecture note:* {wf_snip['ai_generic']}"
        )
        L.append("")

    L.append("### 7.3 Shared handoff contract (swarm-ready)")
    L.append("")
    L.append(
        "When you wire this agent into a future active swarm, require machine-readable manifests between nodes:"
    )
    L.append("")
    L.append("| Field | Why it matters for this role |")
    L.append("|-------|------------------------------|")
    L.append("| `artifact_id` / version | Immutable identity for critique and replay |")
    L.append("| `parent_assets` | Provenance chain into this agent's inputs |")
    L.append("| `brief_scope` | Stops scope creep outside responsibility |")
    L.append("| `acceptance_criteria` | Ties to self-quality bar above |")
    L.append("| `qc_status` / gate flags | Lets downstream gates short-circuit |")
    L.append("| `rights_and_consent` | Blocks unsafe synthetic or licensed misuse |")
    L.append("| `critique_log` pointer | Enables refinement without losing history |")
    L.append("")

    # ── 8 Operating on CASOPS ────────────────────────────────────
    L.append("## 8. Operating this agent on CASOPS today")
    L.append("")
    L.append(
        "Today the agent is a **catalog + design object**. That is intentional: you can study, review, "
        "propose, and place it in swarm designs without granting production power."
    )
    L.append("")
    L.append("| Step | What to do | Why |")
    L.append("|------|------------|-----|")
    L.append("| 1. Discover | Registry Hub → pack catalog (`/registry`) | Confirm inventory membership |")
    L.append(
        f"| 2. Inspect | Agent detail `/registry/agents/{agent_id}` | Read SPEC / this guide as markdown |"
    )
    L.append(
        "| 3. Propose improvements | Host `propose_improvement` action → "
        f"`POST /api/v1/commons/agents/{agent_id}/proposals` | Immutable versions; redacted evidence only |"
    )
    L.append(
        "| 4. Swarm membership | Only with Host-returned action references | Client must not invent membership |"
    )
    L.append(
        "| 5. Run / dispatch | Not enabled for production providers by default | Fail-closed until governance gate |"
    )
    L.append("")
    L.append("### Practical console checklist")
    L.append("")
    L.append("1. Open the agent detail and confirm **status**, **tools**, and **activation** flags match this guide.")
    L.append("2. Read **§3 What good looks like** before judging any sample output or proposal.")
    L.append("3. If proposing a change, attach offline evidence (eval notes, rubric gap, SPEC delta) — no secrets.")
    L.append("4. Never paste vendor API keys or “enable network” instructions into proposals.")
    L.append("5. Prefer small, reviewable deltas: prompt/rubric wording, critique edges, acceptance tests.")
    L.append("")

    # ── 9 Safety ─────────────────────────────────────────────────
    L.append("## 9. Safety, trust, and non-activation rules")
    L.append("")
    L.append("| Layer | Trust | Role |")
    L.append("|-------|-------|------|")
    L.append("| `agent_spec.json` | **Binding host contract** | Fail-closed runtime binding |")
    L.append("| This pack `SPEC.md` | Authoritative **design** for offline review | Not executable |")
    L.append("| `sources/*` excerpts & generic SPECs | Historical / mapped | Untrusted data |")
    L.append("| `C:\\Project\\va-agent-swarm` | External design corpus | Untrusted; may drift |")
    L.append("| Specials redesign docs | Historical design | Untrusted; hashed in provenance |")
    L.append("")
    L.append("**Hard rules on this host:**")
    L.append("")
    L.append(f"- Provider stays `{model_policy.get('provider', 'local_deterministic')}` unless a separate gate changes policy.")
    L.append(f"- Network access stays `{model_policy.get('network_access', False)}`.")
    L.append(f"- Allowed tools are exactly `{allowed_tools or []}` — design-time tool names below do **not** enable APIs.")
    L.append(f"- `production_activation_requested` is `{spec.get('production_activation_requested', False)}`.")
    L.append(
        f"- Budget (tokens/tools) is capped: "
        f"in `{budget.get('max_input_tokens', '—')}` / out `{budget.get('max_output_tokens', '—')}` / "
        f"tool requests `{budget.get('max_tool_requests', '—')}`."
    )
    L.append(f"- Design-time tool catalogue (non-activating): {_first_sentences(str(tools), max_chars=240, max_sentences=2)}")
    L.append("")

    # ── 10 Improvement path ──────────────────────────────────────
    L.append("## 10. Raising quality over time")
    L.append("")
    L.append(
        "Improvement is **versioned catalog work**, not hot-patching a live agent. "
        "Published definitions stay immutable; changes go through proposals and review."
    )
    L.append("")
    L.append("### 10.1 Continuous improvement loop")
    L.append("")
    L.append("```text")
    L.append("Observe failure → Name the criterion (from §3) → Draft offline delta")
    L.append("    → Attach evidence → Propose on Host → Review / accept new version")
    L.append("    → Only then consider activation maturity gates")
    L.append("```")
    L.append("")
    L.append("### 10.2 Concrete levers for this agent")
    L.append("")
    L.append(f"1. **Rubric fidelity** — tighten `{spec.get('rubric_reference', 'rubric')}` against: {quality}")
    L.append(f"2. **Prompt precision** — align `{spec.get('prompt_reference', 'prompt')}` with responsibility: {responsibility}")
    L.append(f"3. **Critique graph** — ensure inbound `{accepts}` and host edges `{edges.get('inputs')}` actually catch known failure modes.")
    L.append(f"4. **Architecture emulation** — when implementing later, prefer: {architecture}")
    L.append(f"5. **Eval cases** — write fixed fixtures that would fail if *{surpass}* is not approached.")
    L.append("6. **Human gates** — keep legal/safety/release gates explicit; do not absorb them into silent automation.")
    L.append("")
    L.append("### 10.3 Suggested evaluation seeds")
    L.append("")
    L.append("| Seed | Pass condition |")
    L.append("|------|----------------|")
    L.append(f"| Happy path handoff | Output satisfies: { _first_sentences(str(quality), max_chars=120, max_sentences=1) } |")
    L.append("| Out-of-scope request | Agent refuses or escalates per §4 |")
    L.append("| Missing provenance / rights | Gate fails closed |")
    L.append("| Conflicting peer critique | Refinement ≤ max_refinement_count; else escalate |")
    L.append("| Proposal-only change | New version immutable; old version still readable |")
    L.append("")

    # ── 11 Source map ────────────────────────────────────────────
    L.append("## 11. Source map and provenance")
    L.append("")
    L.append("### 11.1 Local pack corpus (prefer these first)")
    L.append("")
    L.append("| Path | Trust tier |")
    L.append("|------|------------|")
    for rel, path, tier in local_sources:
        L.append(f"| `{rel}` | `{tier}` |")
    L.append("")
    if mapping:
        L.append("### 11.2 Mapping note")
        L.append("")
        L.append(_first_sentences(mapping, max_chars=800, max_sentences=8) or mapping[:800])
        L.append("")
        if len(mapping) > 900:
            L.append("<details><summary>Full mapping text</summary>")
            L.append("")
            L.append(mapping.strip())
            L.append("")
            L.append("</details>")
            L.append("")
    if provenance:
        L.append("### 11.3 Provenance record")
        L.append("")
        L.append("```json")
        L.append(json.dumps(provenance, indent=2, ensure_ascii=False)[:3000])
        L.append("```")
        L.append("")
    if provenance_sec:
        L.append("### 11.4 Provenance narrative (SPEC)")
        L.append("")
        L.append(_first_sentences(provenance_sec, max_chars=900, max_sentences=8))
        L.append("")
    if va_row:
        L.append("### 11.5 VA roster row (historical design)")
        L.append("")
        L.append(
            f"From `va-agent-swarm/study/agents.md` row **#{va_row['va_id']} {va_row['name']}** "
            "(design corpus — non-binding for activation)."
        )
        L.append("")
        L.append("| Dimension | Content |")
        L.append("|-----------|---------|")
        L.append(f"| Responsibility | {va_row['responsibility']} |")
        L.append(f"| Knowledge distillation | {va_row['knowledge']} |")
        L.append(f"| Self-quality | {va_row['quality']} |")
        L.append(f"| Surpass-human | {va_row['surpass']} |")
        L.append(f"| Accepts critique | {va_row['accepts_critique']} |")
        L.append(f"| Comments on | {va_row['comments_on']} |")
        L.append(f"| Tools (historical) | {va_row['tools']} |")
        L.append(f"| Architecture | {va_row['architecture']} |")
        L.append("")

    # ── 12 Related reading ───────────────────────────────────────
    L.append("## 12. Related design reading")
    L.append("")
    L.append(
        "Use these when deepening design fidelity. They do **not** override local `agent_spec.json`."
    )
    L.append("")
    if va_hits:
        L.append("### 12.1 Files under `C:\\Project\\va-agent-swarm`")
        L.append("")
        L.append("| File | Why it may matter |")
        L.append("|------|-------------------|")
        for path, head, score in va_hits:
            try:
                rel = path.relative_to(va_root)
            except ValueError:
                rel = path
            why = _first_sentences(head, max_chars=140, max_sentences=1) or "Keyword match in name/body"
            L.append(f"| `{rel.as_posix()}` | {why} (score {score}) |")
        L.append("")
    else:
        L.append("_No strong keyword matches under va-agent-swarm; rely on local SPEC and VA table row._")
        L.append("")

    if specials_path and specials_doc:
        L.append("### 12.2 Specials redesign document")
        L.append("")
        L.append(f"Historical design source: `{specials_path.as_posix()}`")
        L.append("")
        heads = re.findall(r"^#{1,3}\s+(.+)$", specials_doc, re.M)
        if heads:
            L.append("**Outline (for navigation):**")
            L.append("")
            for h in heads[:35]:
                L.append(f"- {h.strip()}")
            L.append("")
        # executive excerpt
        exec_m = re.search(
            r"(?:##\s*Executive Summary[^\n]*\n)(.*?)(?=\n##\s|\Z)",
            specials_doc,
            re.S | re.I,
        )
        if exec_m:
            L.append("**Executive summary excerpt:**")
            L.append("")
            L.append(_first_sentences(exec_m.group(1), max_chars=900, max_sentences=6))
            L.append("")
        # Keep excerpt free of top-level ## so TOC / renderers stay clean
        excerpt = specials_doc[:4500]
        excerpt = re.sub(r"(?m)^#{1,3}\s+", "#### ", excerpt)
        L.append("<details><summary>Longer redesign excerpt (truncated, untrusted)</summary>")
        L.append("")
        L.append(excerpt)
        L.append("")
        L.append("</details>")
        L.append("")

    if local_knowledge:
        L.append("### 12.3 Local knowledge index (SPEC)")
        L.append("")
        L.append(local_knowledge)
        L.append("")

    readme_sum = _readme_summary(readme)
    if readme_sum:
        L.append("### 12.4 Folder README (summary)")
        L.append("")
        L.append(readme_sum)
        L.append("")

    # ── 13 Appendix agent_spec ───────────────────────────────────
    L.append("## 13. Appendix — host contract (`agent_spec.json`)")
    L.append("")
    L.append("Authoritative fail-closed configuration for this agent on CASOPS:")
    L.append("")
    L.append("```json")
    L.append(json.dumps(spec, indent=2, ensure_ascii=False)[:5000])
    L.append("```")
    L.append("")
    if runtime_sec:
        L.append("<details><summary>SPEC runtime binding prose</summary>")
        L.append("")
        L.append(runtime_sec[:2500])
        L.append("")
        L.append("</details>")
        L.append("")

    # ── 14 Appendix responsibility excerpt ───────────────────────
    if responsibility_raw and len(responsibility_raw) > 80:
        L.append("## 14. Appendix — SPEC responsibility excerpt")
        L.append("")
        L.append("<details><summary>Expanded responsibility text from local SPEC.md</summary>")
        L.append("")
        L.append(responsibility_raw[:4000])
        L.append("")
        L.append("</details>")
        L.append("")

    # ── 15 Document control ──────────────────────────────────────
    L.append("## 15. Document control")
    L.append("")
    L.append("| Item | Value |")
    L.append("|------|-------|")
    L.append("| Generator | `scripts/business/generate_agent_user_guides.py` |")
    L.append(f"| Agent folder | `business/{pack}/agents/{agent_id}/` |")
    L.append("| Output | `docs/user_guide.md` |")
    L.append(f"| VA corpus root | `{va_root}` |")
    L.append("| Regeneration | `python scripts/business/generate_agent_user_guides.py` |")
    L.append("| Trust model | Design corpus = untrusted data; host config = fail-closed |")
    L.append("")
    L.append(
        f"*End of guide for **{title}**. Start from §1 Snapshot and §5 When to involve; "
        f"use §8–§10 for CASOPS operations and improvement; use §11–§12 only for deep design fidelity.*"
    )
    L.append("")
    return "\n".join(L)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--va-root",
        type=Path,
        default=_VA_ROOT,
        help="Path to va-agent-swarm repository",
    )
    parser.add_argument(
        "--only",
        action="append",
        default=[],
        help="Optional agent folder name filter (repeatable)",
    )
    args = parser.parse_args(argv)

    va_root: Path = args.va_root
    print(f"Loading VA table from {va_root} …")
    va_table = _load_va_agent_table(va_root)
    print(f"  indexed {len(va_table)} table keys")
    print("Indexing VA markdown corpus …")
    va_index = _index_va_markdown(va_root)
    print(f"  {len(va_index)} markdown files")

    written = 0
    missing_spec = 0
    only = set(args.only)

    for pack_root in _PACKS:
        if not pack_root.is_dir():
            continue
        pack = pack_root.parent.name  # video | specials
        for agent_dir in sorted(pack_root.iterdir()):
            if not agent_dir.is_dir():
                continue
            if only and agent_dir.name not in only:
                continue
            if not (agent_dir / "agent_spec.json").is_file():
                continue
            if not (agent_dir / "SPEC.md").is_file():
                missing_spec += 1
            docs = agent_dir / "docs"
            docs.mkdir(parents=True, exist_ok=True)
            content = generate_user_guide(
                agent_dir,
                pack=pack,
                va_table=va_table,
                va_index=va_index,
                va_root=va_root,
            )
            out = docs / "user_guide.md"
            out.write_text(content, encoding="utf-8", newline="\n")
            written += 1
            if written % 20 == 0:
                print(f"  wrote {written} …")

    print(
        json.dumps(
            {
                "written": written,
                "missing_spec_count": missing_spec,
                "va_root_exists": va_root.is_dir(),
                "va_table_keys": len(va_table),
                "va_md_files": len(va_index),
            },
            indent=2,
        )
    )
    return 0 if written else 1


if __name__ == "__main__":
    raise SystemExit(main())
