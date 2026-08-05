"""Process-local hierarchical Markdown index (offline — not Chroma/LightRAG)."""

from __future__ import annotations

import re
import threading
from hashlib import sha256
from typing import Any
from uuid import uuid4

_TOKEN = re.compile(r"[a-z0-9]+", re.I)
_HEADER = re.compile(r"^(#{1,4})\s+(.+)$", re.M)


def _tokens(text: str) -> list[str]:
    return [t.lower() for t in _TOKEN.findall(text or "") if len(t) > 1]


def _chunk_id(seed: str) -> str:
    return f"rag_{sha256(seed.encode('utf-8', errors='replace')).hexdigest()[:16]}"


class LocalDocumentIndex:
    """Hierarchical parent/child chunks with token-overlap retrieval."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._docs: dict[str, dict[str, Any]] = {}
        self._chunks: list[dict[str, Any]] = []
        self._seed_baseline()

    def _seed_baseline(self) -> None:
        """Seed a tiny offline corpus so empty deploys still answer Host questions."""
        seeds = [
            (
                "CASOPS Host memory retrieval",
                (
                    "# Memory retrieval\n\n"
                    "The Host provides scoped memory retrieve via POST /api/v1/memory/retrieve. "
                    "Retrieval is tiered: tier-0 semantic (default), tier-1 relationship lite, "
                    "tier-2 synthesis (optional, off by default). Results always carry provenance. "
                    "Full commercial LightRAG and Chroma are non-goals for the product bar.\n\n"
                    "## Fail-closed\n\n"
                    "Unknown scopes return no_knowledge rather than broadening access."
                ),
                "host://memory/retrieve",
                ["memory", "retrieval"],
            ),
            (
                "Agentic RAG Host foundation",
                (
                    "# Agentic RAG offline foundation\n\n"
                    "Four agentic patterns: Reflection, Planning, Tool Use, Multi-Agent Collaboration. "
                    "Seven elements include adaptive retrieval, stateful memory, hybrid knowledge lite, "
                    "iterative refinement, and evaluation-aware traces.\n\n"
                    "## Offline mode\n\n"
                    "This Host foundation uses a process-local hierarchical Markdown index. "
                    "It does not enable live web search, OpenSearch LightRAG, or 65k production ingest."
                ),
                "host://rag/foundation",
                ["rag", "agentic"],
            ),
            (
                "Video spine and package gates",
                (
                    "# Video pipeline spine\n\n"
                    "wf_video_spine_v1 is the DNA workflow for brief to package. "
                    "Package HITL never auto-approves. production_ready stays false on the exposed "
                    "spine until human package gate. Agent loops run Plan→Act→Self-Review offline.\n\n"
                    "## Aesthetics\n\n"
                    "specials.aesthetics-agent Host API scores D1–D10 offline without live vision."
                ),
                "host://video/spine",
                ["video", "spine"],
            ),
        ]
        for title, content, ref, tags in seeds:
            self.ingest(title=title, content=content, source_ref=ref, tags=tags)

    def stats(self) -> dict[str, Any]:
        with self._lock:
            parents = sum(1 for c in self._chunks if c.get("chunk_type") == "parent")
            children = sum(1 for c in self._chunks if c.get("chunk_type") == "child")
            return {
                "documents": len(self._docs),
                "chunks": len(self._chunks),
                "parents": parents,
                "children": children,
                "backend": "process_local_hierarchical",
                "chroma": False,
                "lightrag": False,
            }

    def list_documents(self, *, limit: int = 50) -> list[dict[str, Any]]:
        limit = max(1, min(limit, 200))
        with self._lock:
            rows = list(self._docs.values())
        return rows[-limit:]

    def ingest(
        self,
        *,
        title: str,
        content: str,
        source_ref: str = "",
        tags: list[str] | None = None,
    ) -> dict[str, Any]:
        title = (title or "").strip() or "untitled"
        content = (content or "").strip()
        if not content:
            raise ValueError("content must be non-empty")
        doc_id = f"doc_{uuid4().hex[:12]}"
        source = (source_ref or "").strip() or f"local://{doc_id}"
        parents, children = self._split_hierarchical(title, content, source)
        with self._lock:
            self._docs[doc_id] = {
                "doc_id": doc_id,
                "title": title,
                "source_ref": source,
                "tags": list(tags or [])[:32],
                "parent_count": len(parents),
                "child_count": len(children),
            }
            self._chunks.extend(parents)
            self._chunks.extend(children)
            if len(self._chunks) > 20_000:
                self._chunks = self._chunks[-16_000:]
        return {
            "ok": True,
            "doc_id": doc_id,
            "title": title,
            "source_ref": source,
            "parents": len(parents),
            "children": len(children),
        }

    def _split_hierarchical(
        self, title: str, content: str, source: str
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """Header-aware parent chunks + recursive-ish child windows."""
        sections: list[tuple[list[str], str]] = []
        matches = list(_HEADER.finditer(content))
        if not matches:
            sections.append(([title], content))
        else:
            # Preamble before first header
            if matches[0].start() > 0:
                pre = content[: matches[0].start()].strip()
                if pre:
                    sections.append(([title], pre))
            for i, m in enumerate(matches):
                start = m.end()
                end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
                header = m.group(2).strip()
                body = content[start:end].strip()
                level = len(m.group(1))
                headers = [title] + [header] if level >= 1 else [title, header]
                if body:
                    sections.append((headers, body))

        parents: list[dict[str, Any]] = []
        children: list[dict[str, Any]] = []
        for headers, body in sections:
            parent_id = _chunk_id(f"p|{source}|{'/'.join(headers)}|{body[:80]}")
            parents.append(
                {
                    "chunk_id": parent_id,
                    "parent_id": parent_id,
                    "title": headers[-1] if headers else title,
                    "content": body[:8000],
                    "source_ref": source,
                    "chunk_type": "parent",
                    "headers": headers,
                    "tokens": _tokens(body),
                }
            )
            # Child windows ~400 chars with overlap
            window, step = 400, 300
            if len(body) <= window:
                child_body = body
                cid = _chunk_id(f"c|{parent_id}|0")
                children.append(
                    {
                        "chunk_id": cid,
                        "parent_id": parent_id,
                        "title": headers[-1] if headers else title,
                        "content": child_body,
                        "source_ref": source,
                        "chunk_type": "child",
                        "headers": headers,
                        "tokens": _tokens(child_body),
                    }
                )
            else:
                for offset in range(0, len(body), step):
                    child_body = body[offset : offset + window]
                    if len(child_body.strip()) < 40:
                        continue
                    cid = _chunk_id(f"c|{parent_id}|{offset}")
                    children.append(
                        {
                            "chunk_id": cid,
                            "parent_id": parent_id,
                            "title": headers[-1] if headers else title,
                            "content": child_body,
                            "source_ref": source,
                            "chunk_type": "child",
                            "headers": headers,
                            "tokens": _tokens(child_body),
                        }
                    )
        return parents, children

    def search(
        self,
        query: str,
        *,
        top_k: int = 8,
        prefer_children: bool = True,
        relationship_boost: bool = False,
    ) -> list[dict[str, Any]]:
        q_tokens = set(_tokens(query))
        if not q_tokens:
            return []
        top_k = max(1, min(top_k, 32))
        with self._lock:
            pool = list(self._chunks)

        scored: list[dict[str, Any]] = []
        for chunk in pool:
            if prefer_children and chunk.get("chunk_type") != "child":
                # still allow parents when few children
                pass
            c_tokens = set(chunk.get("tokens") or [])
            if not c_tokens:
                continue
            overlap = len(q_tokens & c_tokens)
            if overlap == 0:
                continue
            union = len(q_tokens | c_tokens) or 1
            jaccard = overlap / union
            coverage = overlap / max(1, len(q_tokens))
            score = 0.55 * coverage + 0.45 * jaccard
            # Prefer child granularity for answer excerpts
            if chunk.get("chunk_type") == "child":
                score += 0.03
            if relationship_boost:
                rel_markers = {
                    "depend",
                    "relation",
                    "connect",
                    "who",
                    "which",
                    "between",
                    "tier",
                    "memory",
                    "retrieve",
                }
                if c_tokens & rel_markers:
                    score += 0.05
            score = min(0.99, score)
            if score < 0.08:
                continue
            row = {
                "chunk_id": chunk["chunk_id"],
                "parent_id": chunk["parent_id"],
                "title": chunk["title"],
                "content": chunk["content"],
                "source_ref": chunk["source_ref"],
                "chunk_type": chunk["chunk_type"],
                "headers": list(chunk.get("headers") or []),
                "relevance_score": round(score, 4),
            }
            scored.append(row)

        scored.sort(key=lambda r: r["relevance_score"], reverse=True)
        # Deduplicate by parent_id keeping best child
        seen_parents: set[str] = set()
        out: list[dict[str, Any]] = []
        for row in scored:
            pid = str(row.get("parent_id") or row["chunk_id"])
            if pid in seen_parents and row.get("chunk_type") == "child":
                continue
            if row.get("chunk_type") == "child":
                seen_parents.add(pid)
            out.append(row)
            if len(out) >= top_k:
                break
        return out
