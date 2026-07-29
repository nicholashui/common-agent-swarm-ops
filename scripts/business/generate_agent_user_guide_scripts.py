#!/usr/bin/env python3
"""Generate professional YouTube English narration scripts from agent user guides.

Reads:
  business/{video|specials}/agents/<id>/docs/user_guide.md

Writes:
  business/{video|specials}/agents/<id>/docs/user_guide.script.en.txt

Style:
  - Pure spoken English for professional technical YouTube voice-over
  - No Markdown, no [tags], no Title/Agent/Pack metadata headers
  - Natural chapter transitions a host can read on camera
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_PACKS = (
    _ROOT / "business" / "video" / "agents",
    _ROOT / "business" / "specials" / "agents",
)

_SECTION_RE = re.compile(r"^##\s+(\d+)\.\s+(.+?)\s*$", re.M)
_SUBSECTION_RE = re.compile(r"^###\s+(.+?)\s*$", re.M)


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _strip_md_inline(text: str) -> str:
    """Remove markdown decorations while keeping readable words."""
    if not text:
        return ""
    # HTML / details
    text = re.sub(r"<details>.*?</details>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    # Fenced code → short spoken skip
    text = re.sub(
        r"```(?:json|markdown|text|bash|python)?\n(.*?)```",
        lambda m: _spoken_code_summary(m.group(1)),
        text,
        flags=re.S | re.I,
    )
    text = re.sub(r"`([^`]+)`", r"\1", text)
    # Bold / italic (do NOT strip underscores inside identifiers like production_activation)
    text = re.sub(r"\*\*\*(.+?)\*\*\*", r"\1", text)
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"(?<!\w)\*(?!\s)(.+?)(?<!\s)\*(?!\w)", r"\1", text)
    # Links / images
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", text)
    # Blockquotes / headings / rules / bullets
    text = re.sub(r"(?m)^\s*>\s?", "", text)
    text = re.sub(r"(?m)^#{1,6}\s+", "", text)
    text = re.sub(r"(?m)^\s*---+\s*$", "", text)
    text = re.sub(r"(?m)^\s*[-*+]\s+", "", text)
    text = re.sub(r"(?m)^\s*\d+\.\s+", "", text)
    # Speakability cleanup
    text = text.replace("\u00a0", " ")
    text = text.replace("—", " — ")
    text = text.replace("–", " — ")
    text = text.replace("→", " to ")
    text = text.replace("§", "section ")
    text = text.replace("→", " to ")
    text = re.sub(r"\bFalse\b", "false", text)
    text = re.sub(r"\bTrue\b", "true", text)
    text = re.sub(r"\[\]", "none", text)
    text = re.sub(r"\['([^']+)'\]", r"\1", text)
    text = re.sub(r"\[\"([^\"]+)\"\]", r"\1", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def _spoken_code_summary(code: str) -> str:
    code = (code or "").strip()
    if not code:
        return ""
    # Prefer one-line summary rather than reading JSON aloud
    first = code.splitlines()[0].strip()[:120]
    if first.startswith("{") or first.startswith("["):
        return (
            " On screen, you would see the host configuration JSON. "
            "I will not read raw code line by line. "
        )
    return f" On screen reference: {_strip_md_inline(first)}. "


def _parse_table_rows(table_block: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for ln in table_block.splitlines():
        ln = ln.strip()
        if not ln.startswith("|"):
            continue
        raw_cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        # separator rows like |---|---| or | --- | --- |
        if raw_cells and all(re.fullmatch(r":?-+:?", (c or "").replace(" ", "")) for c in raw_cells):
            continue
        if re.fullmatch(r"[\|\s:\-]+", ln):
            continue
        cells = [_strip_md_inline(c) for c in raw_cells]
        if not any(cells):
            continue
        rows.append(cells)
    return rows


def _is_header_label_row(row: list[str]) -> bool:
    """True if row looks like column headers rather than a data / key-value row."""
    if not row:
        return True
    labels = {
        "field",
        "item",
        "question",
        "guidance",
        "direction",
        "agents / topics",
        "agents",
        "topics",
        "path",
        "trust tier",
        "trust",
        "role",
        "layer",
        "step",
        "what to do",
        "why",
        "why it matters",
        "seed",
        "pass condition",
        "dimension",
        "content",
        "file",
        "why it may matter",
        "value",
    }
    nonempty = [c.strip() for c in row if c and c.strip()]
    if not nonempty:
        return True
    lowered = [c.lower() for c in nonempty]
    if all(c in labels for c in lowered):
        return True
    return False


def _table_to_spoken(table_block: str) -> str:
    rows = _parse_table_rows(table_block)
    if not rows:
        return ""

    # Normalize width
    width = max(len(r) for r in rows)
    rows = [r + [""] * (width - len(r)) for r in rows]

    # Two-column tables → always "Key: value" (our guides are mostly this shape)
    if width == 2:
        data = rows
        if _is_header_label_row(rows[0]) or not rows[0][0]:
            data = rows[1:] if len(rows) > 1 else rows
        spoken = []
        for k, v in data:
            k, v = k.strip(), v.strip()
            if not k and not v:
                continue
            if not k or k in {"—", "-"}:
                continue
            if not v or v in {"—", "-"}:
                spoken.append(f"{k}.")
            else:
                spoken.append(f"{k}: {v}.")
        return " ".join(spoken)

    # Three-column process tables: Step / What / Why
    header = rows[0]
    body = rows[1:]
    if _is_header_label_row(header):
        keys = [c if c else f"field {i+1}" for i, c in enumerate(header)]
    else:
        # first row is data; invent neutral labels
        keys = [f"field {i+1}" for i in range(width)]
        body = rows

    h0 = keys[0].lower() if keys else ""
    if width >= 3 and ("step" in h0 or keys[0] in {"", "Step"}):
        spoken = []
        for row in body:
            step = row[0] or "Step"
            what = row[1] if len(row) > 1 else ""
            why = row[2] if len(row) > 2 else ""
            bit = f"{step}: {what}."
            if why:
                bit += f" Why it matters: {why}."
            spoken.append(bit)
        return " ".join(spoken)

    # Generic multi-column
    spoken = []
    for row in body:
        parts = []
        for i, cell in enumerate(row):
            if not cell or cell in {"—", "-"}:
                continue
            label = keys[i] if i < len(keys) and keys[i] else ""
            if label and label.lower() not in {"field 1", "field 2", "field 3"}:
                parts.append(f"{label}: {cell}")
            else:
                parts.append(cell)
        if parts:
            spoken.append("; ".join(parts) + ".")
    return " ".join(spoken)


def _md_block_to_spoken(block: str) -> str:
    """Convert a markdown section body to spoken prose."""
    if not block.strip():
        return ""

    pieces: list[str] = []
    lines = block.splitlines()
    i = 0
    prose_buf: list[str] = []

    def flush_prose() -> None:
        nonlocal prose_buf
        if not prose_buf:
            return
        text = "\n".join(prose_buf)
        prose_buf = []
        # Drop noisy workflow dump lines (better in written guide than spoken)
        kept_lines = []
        for raw in text.splitlines():
            s = raw.strip()
            if not s:
                kept_lines.append("")
                continue
            low = s.lower()
            if low.startswith("**mentions in local") or low.startswith("mentions in local"):
                continue
            if "mentions in local" in low and "workflow" in low:
                continue
            kept_lines.append(s)
        text = "\n".join(kept_lines)
        text = _strip_md_inline(text)
        paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
        for p in paras:
            p = re.sub(r"\s+", " ", p).strip()
            if len(p) < 3:
                continue
            if p.startswith("Pack path:"):
                continue
            if "Generated by" in p and "scripts/business" in p:
                continue
            if p.startswith("End of guide"):
                continue
            # Skip leftover pure path inventories if huge
            if p.count("/") > 12 and p.count("sources/") > 4:
                pieces.append(
                    "The written guide lists the full local source inventory. "
                    "Prefer agent_spec.json and SPEC.md first; treat excerpts as historical."
                )
                continue
            pieces.append(p if p.endswith((".", "!", "?", ":", '"', "'")) else p + ".")

    while i < len(lines):
        ln = lines[i]
        if ln.strip().startswith("|"):
            flush_prose()
            table_lines = []
            while i < len(lines) and (lines[i].strip().startswith("|") or not lines[i].strip()):
                if lines[i].strip():
                    table_lines.append(lines[i])
                i += 1
                if i < len(lines) and not lines[i].strip():
                    j = i
                    while j < len(lines) and not lines[j].strip():
                        j += 1
                    if j < len(lines) and not lines[j].strip().startswith("|"):
                        break
            spoken_table = _table_to_spoken("\n".join(table_lines))
            if spoken_table:
                pieces.append(spoken_table)
            continue
        if ln.strip().startswith("```"):
            flush_prose()
            i += 1
            code = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code.append(lines[i])
                i += 1
            if i < len(lines):
                i += 1
            summary = _spoken_code_summary("\n".join(code)).strip()
            if summary:
                pieces.append(summary)
            continue
        if ln.strip().startswith("### "):
            flush_prose()
            sub = _strip_md_inline(ln.strip()[4:])
            # Drop numeric prefixes like "7.1 "
            sub = re.sub(r"^\d+(\.\d+)*\s+", "", sub)
            if sub:
                pieces.append(f"Now, {sub[0].lower() + sub[1:] if len(sub) > 1 else sub}.")
            i += 1
            continue
        prose_buf.append(ln)
        i += 1
    flush_prose()

    out = []
    for p in pieces:
        p = re.sub(r"\s+", " ", p).strip()
        p = re.sub(r"\s+([,.;:!?])", r"\1", p)
        p = re.sub(r"([.!?]){2,}", r"\1", p)
        p = re.sub(r"\s+—\s+", " — ", p)
        if p:
            out.append(p)
    return " ".join(out)


def _parse_sections(md: str) -> tuple[str, list[tuple[str, str]]]:
    """Return (title, [(section_title, body), ...]). Skip appendices-heavy noise lightly."""
    title = "Agent Operator Guide"
    m = re.search(r"^#\s+(.+?)\s*$", md, re.M)
    if m:
        title = _strip_md_inline(m.group(1))
        # Drop "Operator & Design Guide" for spoken title variety
        title = title.replace(" — Operator & Design Guide", "").replace(" - Operator & Design Guide", "").strip()

    matches = list(_SECTION_RE.finditer(md))
    sections: list[tuple[str, str]] = []
    for idx, match in enumerate(matches):
        num = match.group(1)
        name = match.group(2).strip()
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(md)
        body = md[start:end].strip()
        # Skip pure document control appendix in main spoken flow later by flagging
        sections.append((f"{num}. {name}", body))
    return title, sections


def _spoken_section_title(name: str) -> str:
    """Turn section headings into natural host transitions."""
    # strip leading "N. "
    bare = re.sub(r"^\d+\.\s*", "", name).strip()
    mapping = {
        "Snapshot": "First, a quick snapshot of what this agent is.",
        "Why this role exists": "Next, why this role exists.",
        "What good looks like": "Now, what good looks like when this agent does its job well.",
        "Scope: owns, shares, and refuses": "Let's clarify scope — what it owns, what it shares, and what it refuses.",
        "When to involve this agent": "When should you involve this agent?",
        "Collaboration map": "Here is the collaboration map — who critiques whom.",
        "Where it sits in production": "Where does this agent sit in production?",
        "Operating this agent on CASOPS today": "How do you operate this agent on CASOPS today?",
        "Safety, trust, and non-activation rules": "Safety, trust, and non-activation rules — this part matters.",
        "Raising quality over time": "How do we raise quality over time?",
        "Source map and provenance": "A short tour of sources and provenance.",
        "Related design reading": "If you want deeper design reading, here is where to look.",
        "Appendix — host contract (`agent_spec.json`)": "Appendix: the host contract, without reading code line by line.",
        "Appendix — host contract (agent_spec.json)": "Appendix: the host contract, without reading code line by line.",
        "Appendix — SPEC responsibility excerpt": "Appendix: a short responsibility excerpt from the local specification.",
        "Document control": "Finally, document control notes for the archive.",
    }
    # normalize backticks in name for lookup
    bare_key = bare.replace("`", "")
    for k, v in mapping.items():
        if bare_key.lower() == k.lower().replace("`", "") or bare.lower().startswith(k.lower()[:20]):
            return v
    return f"Next section: {bare}."


def _is_appendix(name: str) -> bool:
    n = name.lower()
    return "appendix" in n or "document control" in n


def _final_script_cleanup(text: str) -> str:
    """Last-pass: pure spoken text only — no tags, headers, or markdown residue."""
    # Convert any leftover pipe tables that leaked into prose
    def repl_table(match: re.Match[str]) -> str:
        return _table_to_spoken(match.group(0)) or " "

    text = re.sub(
        r"(?:\|[^\n]*\|\s*\n)+(?:\|[\s:\-|]+\|\s*\n)?(?:\|[^\n]*\|\s*\n?)+",
        repl_table,
        text,
    )
    text = re.sub(r"(?:\s*\|[^|\n]+){2,}\s*\|", " ", text)
    text = re.sub(r"\|-{3,}(?:\|-{3,})*\|?", " ", text)
    text = re.sub(r"`+", "", text)
    text = re.sub(r"\*\*+", "", text)
    text = re.sub(r"(?<!\w)\*(?!\s)", "", text)
    text = re.sub(r"(?<!\s)\*(?!\w)", "", text)
    text = re.sub(r"__+", "", text)
    text = re.sub(r"(?m)^#{1,6}\s*", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\s+→\s+", " to ", text)
    text = re.sub(r"§(\d+)", r"section \1", text)

    # Drop production tags like [COLD OPEN], [SECTION: ...], [END]
    text = re.sub(r"(?m)^\s*\[[^\]]+\]\s*$", "", text)
    # Drop any leftover bracket tags mid-line that are pure markers
    text = re.sub(
        r"\[(?:COLD OPEN|INTRO|OUTRO|END|APPENDIX NOTE|SECTION:[^\]]+)\]\s*",
        "",
        text,
        flags=re.I,
    )

    # Drop remark / metadata header lines if present
    meta_prefixes = (
        "youtube script",
        "spoken narration",
        "title:",
        "agent:",
        "pack:",
        "format:",
        "tone:",
        "channel:",
        "duration:",
        "notes:",
    )
    cleaned_lines: list[str] = []
    for ln in text.splitlines():
        raw = ln.strip()
        if not raw:
            cleaned_lines.append("")
            continue
        if set(raw) <= {"=", "-", "_", "*"}:
            continue
        low = raw.lower()
        if any(low.startswith(p) for p in meta_prefixes):
            continue
        if raw.startswith("[") and raw.endswith("]") and len(raw) < 100:
            continue
        ln = re.sub(r"[ \t]{2,}", " ", raw)
        cleaned_lines.append(ln)

    # Collapse 3+ blank lines → max 1 blank between paragraphs
    out: list[str] = []
    blank = 0
    for ln in cleaned_lines:
        if ln == "":
            blank += 1
            if blank <= 1:
                out.append("")
        else:
            blank = 0
            out.append(ln)
    return "\n".join(out).strip() + "\n"


def generate_script_from_user_guide(md: str, *, agent_id: str, pack: str) -> str:
    title, sections = _parse_sections(md)
    if not sections and not title:
        return (
            f"Welcome. This is a short overview of agent {agent_id} in the {pack} pack. "
            "The full operator guide was not available at generation time.\n"
        )

    main_sections = [(n, b) for n, b in sections if not _is_appendix(n)]
    appendix_sections = [(n, b) for n, b in sections if _is_appendix(n)]

    lines: list[str] = []

    # Pure spoken narration only — no tags, no metadata headers
    lines.append(
        f"If you are building multi-agent systems, you need more than a name on a roster. "
        f"You need to know what {title} actually owns, when to call it, who critiques it, "
        f"and how to improve it without breaking host safety. That is what this walkthrough covers."
    )
    lines.append("")

    pack_label = "Video Domain Pack" if pack == "video" else "Specials pack"
    lines.append(
        f"Welcome. In this video, we walk through the operator and design guide for {title}, "
        f"agent identifier {agent_id}, in the {pack_label} on Common Agent Swarm Ops, also called CASOPS."
    )
    lines.append("")
    lines.append(
        "This is not a license to flip on production providers or open the network. "
        "On this host, the binding contract stays fail-closed. Design text is reference material. "
        "Think of this video as the human map: mission, quality bar, collaboration, operations, and improvement."
    )
    lines.append("")
    lines.append(
        "By the end, you should know when to involve this agent, how it fits a human or multi-agent workflow, "
        "and how to propose better quality over time without mutating published definitions in place."
    )
    lines.append("")

    for name, body in main_sections:
        spoken_body = _md_block_to_spoken(body)
        if not spoken_body or len(spoken_body) < 20:
            continue
        bare = re.sub(r"^\d+\.\s*", "", name).lower()
        if "related design reading" in bare and len(spoken_body) > 1800:
            spoken_body = spoken_body[:1800].rsplit(".", 1)[0] + ". More files are listed in the written guide."
        if "source map" in bare and len(spoken_body) > 2200:
            spoken_body = spoken_body[:2200].rsplit(".", 1)[0] + ". Full provenance tables stay in the written guide."

        lines.append(_spoken_section_title(name))
        lines.append("")
        lines.extend(_wrap_spoken_paragraphs(spoken_body))
        lines.append("")

    if appendix_sections:
        lines.append(
            "The written guide also includes appendices for the host contract and specification excerpts. "
            "On camera, we summarize rather than read JSON. "
            "The authority remains the local agent specification file on the host: fail-closed tools, "
            "no network by default, and production activation off unless a separate governance gate changes that."
        )
        lines.append("")
        for name, body in appendix_sections:
            if "document control" in name.lower():
                continue
            spoken_body = _md_block_to_spoken(body)
            if spoken_body:
                short = spoken_body[:900]
                if len(spoken_body) > 900:
                    short = short.rsplit(".", 1)[0] + "."
                lines.append(_spoken_section_title(name))
                lines.append("")
                lines.extend(_wrap_spoken_paragraphs(short))
                lines.append("")

    lines.append(
        f"That is the operator walkthrough for {title}. "
        "Remember three takeaways. One: know the mission and quality bar before you score any output. "
        "Two: place the agent on the critique bus with clear handoffs, not as a lone chatbot. "
        "Three: improve through versioned proposals and evidence, not hot patches, and keep safety gates human where risk is high."
    )
    lines.append("")
    lines.append(
        "If you are following along in the repo, open the agent folder under the business pack, "
        "read the written user guide beside this script, and use the registry to inspect status before you propose changes."
    )
    lines.append("")
    lines.append(
        "Thanks for watching. Use this guide to design cleaner swarms, safer reviews, and clearer ownership — "
        "one agent at a time."
    )
    lines.append("")
    return _final_script_cleanup("\n".join(lines))


def _wrap_spoken_paragraphs(text: str, *, max_chars: int = 420) -> list[str]:
    """Break spoken text into script-friendly paragraphs without markdown."""
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    # Split on sentence boundaries
    sentences = re.split(r"(?<=[.!?])\s+", text)
    paras: list[str] = []
    buf = ""
    for s in sentences:
        s = s.strip()
        if not s:
            continue
        if not buf:
            buf = s
        elif len(buf) + 1 + len(s) <= max_chars:
            buf = f"{buf} {s}"
        else:
            paras.append(buf)
            buf = s
    if buf:
        paras.append(buf)
    return paras


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--only",
        action="append",
        default=[],
        help="Optional agent folder name filter (repeatable)",
    )
    args = parser.parse_args(argv)
    only = set(args.only)

    written = 0
    skipped = 0
    for pack_root in _PACKS:
        if not pack_root.is_dir():
            continue
        pack = pack_root.parent.name
        for agent_dir in sorted(pack_root.iterdir()):
            if not agent_dir.is_dir():
                continue
            if only and agent_dir.name not in only:
                continue
            guide = agent_dir / "docs" / "user_guide.md"
            if not guide.is_file():
                skipped += 1
                continue
            md = _read(guide)
            script = generate_script_from_user_guide(md, agent_id=agent_dir.name, pack=pack)
            out = agent_dir / "docs" / "user_guide.script.en.txt"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(script, encoding="utf-8", newline="\n")
            written += 1
            if written % 20 == 0:
                print(f"  wrote {written} …")

    print(f'{{"written": {written}, "skipped_missing_guide": {skipped}}}')
    return 0 if written else 1


if __name__ == "__main__":
    raise SystemExit(main())
