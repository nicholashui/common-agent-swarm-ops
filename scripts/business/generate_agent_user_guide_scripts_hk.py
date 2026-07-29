#!/usr/bin/env python3
"""Translate user_guide.script.en.txt → user_guide.script.hk.txt

Target style: Traditional Chinese for spoken Cantonese (粵語口語), pure narration.
Uses Google Translate public endpoint with language code `yue`.

Technical tokens (agent ids, paths, API routes, CamelCase agents) are protected
with placeholders so they are not mangled by machine translation.
"""

from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path

import httpx

_ROOT = Path(__file__).resolve().parents[2]
_PACKS = (
    _ROOT / "business" / "video" / "agents",
    _ROOT / "business" / "specials" / "agents",
)

_TRANSLATE_URL = "https://translate.googleapis.com/translate_a/single"
_MAX_CHUNK = 1200
_SLEEP_S = 0.08
_MAX_RETRIES = 6

# Pre-translate glossary: English phrase → Cantonese spoken Traditional Chinese
_GLOSSARY: list[tuple[str, str]] = [
    (r"\bfail-closed\b", "預設鎖死（fail-closed）"),
    (r"\bfail closed\b", "預設鎖死（fail-closed）"),
    (r"\bnon-activation\b", "未啟用"),
    (r"\bproduction activation\b", "生產啟用"),
    (r"\bcatalog\b", "目錄"),
    (r"\bcritique bus\b", "互評總線"),
    (r"\bcritique\b", "互評"),
    (r"\bswarm\b", "群組（swarm）"),
    (r"\bhandoff\b", "交接"),
    (r"\bhandoffs\b", "交接"),
    (r"\btakeaways\b", "要點"),
    (r"\btakeaway\b", "要點"),
    (r"\brubric\b", "評分準則"),
    (r"\bprompt\b", "提示詞"),
    (r"\bprovenance\b", "來源譜系"),
    (r"\boperator guide\b", "操作指南"),
    (r"\boperator\b", "操作人員"),
    (r"\bRegistry Hub\b", "註冊中心"),
    (r"\bregistry\b", "註冊表"),
    (r"\bDomain Pack\b", "領域包"),
    (r"\bSpecials pack\b", "Specials 包"),
    (r"\bVideo Domain Pack\b", "影片領域包"),
    (r"\bCommon Agent Swarm Ops\b", "Common Agent Swarm Ops"),
    (r"\bCASOPS\b", "CASOPS"),
    (r"\blocal_deterministic\b", "local_deterministic"),
    (r"\bnetwork access\b", "網絡存取"),
    (r"\ballowed tools\b", "允許工具"),
]

# Patterns protected from translation (order matters: longer first-ish)
_PROTECT_PATTERNS: list[re.Pattern[str]] = [
    # dotted technical ids first (agent ids, prompt/rubric refs, etc.)
    re.compile(r"\b[a-z][a-z0-9_]*(?:\.[a-z0-9_\-]+)+", re.I),
    re.compile(r"\b[A-Z][a-zA-Z0-9]+Agent(?:\s*/\s*[A-Z][a-zA-Z0-9]+)?\b"),
    re.compile(r"\b(?:POST|GET|PUT|PATCH|DELETE)\s+/api/v1/[^\s,.;]+"),
    re.compile(r"/api/v1/[^\s,.;]+"),
    re.compile(r"/registry(?:/agents/[^\s,.;]+)?"),
    re.compile(r"\bagent_spec\.json\b"),
    re.compile(r"\bSPEC\.md\b"),
    re.compile(r"\bREADME\.md\b"),
    re.compile(r"\buser_guide(?:\.md|\.script\.en\.txt|\.script\.hk\.txt)?\b"),
    re.compile(r"\bbusiness/(?:video|specials)/[^\s,.;]+"),
    re.compile(r"\bsources/[^\s,.;]+"),
    re.compile(r"\bgeneric-swarm-ops/[^\s,.;]+"),
    re.compile(r"C:\\\\Project\\\\[^\s,.;]+"),
    re.compile(r"\bva-agent-swarm(?:/[^\s,.;]+)?"),
    re.compile(r"\bdocs/special_agents_redesign/[^\s,.;]+"),
    re.compile(r"\bL0\b"),
    re.compile(r"\bWCAG\s*2\.2\b"),
    re.compile(r"\b10-Sup\b"),
    re.compile(r"\bJSON\b"),
    re.compile(r"\bAPI\b"),
    re.compile(r"\bMCP\b"),
    re.compile(r"\bDAG\b"),
    re.compile(r"\bCASOPS\b"),
    re.compile(r"\bVA\b"),
]


def _apply_glossary(text: str) -> str:
    for pat, repl in _GLOSSARY:
        text = re.sub(pat, repl, text, flags=re.I)
    return text


def _protect(text: str) -> tuple[str, dict[str, str]]:
    """Replace technical tokens with stable placeholders."""
    mapping: dict[str, str] = {}
    counter = 0

    def sub_one(match: re.Match[str]) -> str:
        nonlocal counter
        token = match.group(0)
        # de-dupe identical tokens to same placeholder
        for k, v in mapping.items():
            if v == token:
                return k
        key = f"XPROTECT{counter:04d}X"
        mapping[key] = token
        counter += 1
        return key

    # Longest-first by scanning with alternation would be complex; apply patterns in order
    # on non-overlapping spans via sequential substitution.
    for pat in _PROTECT_PATTERNS:
        text = pat.sub(sub_one, text)
    return text, mapping


def _unprotect(text: str, mapping: dict[str, str]) -> str:
    # Translators sometimes insert spaces inside placeholders
    def fix(m: re.Match[str]) -> str:
        k = f"XPROTECT{m.group(1)}X"
        return mapping.get(k, m.group(0))

    text = re.sub(r"X\s*PROTECT\s*(\d{4})\s*X", fix, text, flags=re.I)
    # Exact replacements (case variants)
    for key, val in mapping.items():
        text = text.replace(key, val)
        text = text.replace(key.lower(), val)
        text = text.replace(key.upper(), val)
    return text


def _chunk_paragraphs(text: str, max_chars: int = _MAX_CHUNK) -> list[str]:
    paras = re.split(r"\n\s*\n", text.strip())
    chunks: list[str] = []
    buf = ""

    def flush() -> None:
        nonlocal buf
        if buf.strip():
            chunks.append(buf.strip())
        buf = ""

    for para in paras:
        para = para.strip()
        if not para:
            continue
        if len(para) > max_chars:
            flush()
            sentences = re.split(r"(?<=[.!?])\s+", para)
            sbuf = ""
            for s in sentences:
                s = s.strip()
                if not s:
                    continue
                if len(s) > max_chars:
                    if sbuf:
                        chunks.append(sbuf.strip())
                        sbuf = ""
                    for i in range(0, len(s), max_chars):
                        chunks.append(s[i : i + max_chars])
                    continue
                if not sbuf:
                    sbuf = s
                elif len(sbuf) + 1 + len(s) <= max_chars:
                    sbuf = f"{sbuf} {s}"
                else:
                    chunks.append(sbuf.strip())
                    sbuf = s
            if sbuf.strip():
                chunks.append(sbuf.strip())
            continue
        if not buf:
            buf = para
        elif len(buf) + 2 + len(para) <= max_chars:
            buf = f"{buf}\n\n{para}"
        else:
            flush()
            buf = para
    flush()
    return chunks


def _translate_chunk(client: httpx.Client, text: str, *, tl: str = "yue") -> str:
    last_err: Exception | None = None
    for attempt in range(_MAX_RETRIES):
        try:
            resp = client.post(
                _TRANSLATE_URL,
                params={"client": "gtx", "sl": "en", "tl": tl, "dt": "t"},
                data={"q": text},
                timeout=90.0,
            )
            if resp.status_code in (429, 503):
                time.sleep(1.8 * (attempt + 1))
                continue
            resp.raise_for_status()
            data = resp.json()
            parts: list[str] = []
            if isinstance(data, list) and data and isinstance(data[0], list):
                for part in data[0]:
                    if part and isinstance(part, list) and part[0]:
                        parts.append(str(part[0]))
            out = "".join(parts).strip()
            if out:
                return out
            raise RuntimeError("empty translation")
        except Exception as exc:  # noqa: BLE001
            last_err = exc
            time.sleep(1.0 * (attempt + 1))
    raise RuntimeError(f"translate failed after retries: {last_err}")


def _postprocess(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"(?m)^\s*\[[^\]]+\]\s*$", "", text)
    text = re.sub(r"`+", "", text)
    text = re.sub(r"\*\*+", "", text)
    # Fix spaces inserted inside latin dotted identifiers: "video . accessibility"
    text = re.sub(r"(?<=[A-Za-z0-9])\s*\.\s*(?=[A-Za-z0-9])", ".", text)
    # Re-introduce Chinese full stop spacing: only collapse latin dotted ids already done
    # Undo over-aggressive period join for Chinese: if we joined "句.下" no — Chinese uses 。
    # Fix "false"/"true" spoken if left in EN
    text = text.replace("：false", "：否（false）").replace(": false", "：否（false）")
    text = text.replace("：true", "：是（true）").replace(": true", "：是（true）")
    # Clean double spaces
    lines_out: list[str] = []
    for ln in text.splitlines():
        s = ln.strip()
        if not s:
            lines_out.append("")
            continue
        low = s.lower()
        if low.startswith(("youtube script", "title:", "agent:", "pack:", "format:", "tone:")):
            continue
        if set(s) <= {"=", "-", "_"}:
            continue
        s = s.replace("\u3000", " ")
        s = re.sub(r"[ \t]{2,}", " ", s)
        # Remove spaces between CJK characters
        s = re.sub(r"(?<=[\u4e00-\u9fff])\s+(?=[\u4e00-\u9fff])", "", s)
        lines_out.append(s)
    out: list[str] = []
    blank = 0
    for ln in lines_out:
        if ln == "":
            blank += 1
            if blank <= 1:
                out.append("")
        else:
            blank = 0
            out.append(ln)
    return "\n".join(out).strip() + "\n"


def translate_script(client: httpx.Client, en_text: str) -> str:
    prepared = _apply_glossary(en_text)
    protected, mapping = _protect(prepared)
    chunks = _chunk_paragraphs(protected)
    translated: list[str] = []
    for i, chunk in enumerate(chunks):
        hk = _translate_chunk(client, chunk)
        translated.append(hk)
        if i + 1 < len(chunks):
            time.sleep(_SLEEP_S)
    body = "\n\n".join(translated)
    body = _unprotect(body, mapping)
    return _postprocess(body)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", action="append", default=[], help="Agent folder name filter")
    parser.add_argument("--force", action="store_true", help="Overwrite existing hk scripts")
    parser.add_argument("--limit", type=int, default=0, help="Max files to write (0=all)")
    args = parser.parse_args(argv)
    only = set(args.only)

    written = 0
    skipped = 0
    failed: list[str] = []

    with httpx.Client(headers={"User-Agent": "casops-script-translator/1.1"}) as client:
        for pack_root in _PACKS:
            if not pack_root.is_dir():
                continue
            for agent_dir in sorted(pack_root.iterdir()):
                if not agent_dir.is_dir():
                    continue
                if only and agent_dir.name not in only:
                    continue
                en_path = agent_dir / "docs" / "user_guide.script.en.txt"
                hk_path = agent_dir / "docs" / "user_guide.script.hk.txt"
                if not en_path.is_file():
                    skipped += 1
                    continue
                if hk_path.is_file() and not args.force:
                    skipped += 1
                    continue

                en_text = en_path.read_text(encoding="utf-8", errors="replace")
                try:
                    hk_text = translate_script(client, en_text)
                    hk_path.parent.mkdir(parents=True, exist_ok=True)
                    hk_path.write_text(hk_text, encoding="utf-8", newline="\n")
                    written += 1
                    print(f"  wrote {agent_dir.name} ({written})", flush=True)
                except Exception as exc:  # noqa: BLE001
                    failed.append(f"{agent_dir.name}: {exc}")
                    print(f"  FAIL {agent_dir.name}: {exc}", flush=True)
                if args.limit and written >= args.limit:
                    break
            if args.limit and written >= args.limit:
                break

    print(
        json.dumps(
            {
                "written": written,
                "skipped": skipped,
                "failed": failed[:30],
                "fail_count": len(failed),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if (written or skipped) and not (failed and not written) else 1


if __name__ == "__main__":
    raise SystemExit(main())
