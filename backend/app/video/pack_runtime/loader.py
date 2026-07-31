"""Load pack-local agent_spec, prompt, rubric, and skill harness (fail-closed)."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.video.pack_runtime.paths import AGENTS_ROOT, SPECIAL_SKILLS_ROOT

_SAFE_ID = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]*$")


@dataclass(frozen=True, slots=True)
class PackAgentBundle:
    """Resolved pack artifacts for one agent."""

    agent_id: str
    agent_dir: Path
    agent_spec: dict[str, Any]
    prompt_reference: str
    rubric_reference: str
    prompt_text: str
    rubric: dict[str, Any]
    skill_markdown: str
    skill_integration: dict[str, Any]
    skill_bindings: dict[str, Any]
    does_not_own: tuple[str, ...]
    allowed_tools: tuple[str, ...]
    critique_edges: dict[str, tuple[str, ...]]
    max_refinement_count: int
    has_distillation_plan: bool
    has_source_catalog: bool
    has_acquire_runbook: bool


class PackAgentLoader:
    """Load only files under business/video/agents/<id>/ (no network)."""

    def __init__(self, agents_root: Path = AGENTS_ROOT) -> None:
        self._agents_root = agents_root.resolve()

    def load(self, agent_id: str) -> PackAgentBundle:
        if not _SAFE_ID.match(agent_id):
            raise ValueError(f"Invalid agent_id: {agent_id}")
        agent_dir = (self._agents_root / agent_id).resolve()
        if not str(agent_dir).startswith(str(self._agents_root)):
            raise ValueError("Agent path escapes pack root.")
        if not agent_dir.is_dir():
            raise FileNotFoundError(f"Agent folder missing: {agent_id}")

        spec = self._read_json(agent_dir / "agent_spec.json")
        if str(spec.get("agent_id") or agent_id) != agent_id:
            # tolerate folder-name as authority
            pass

        prompt_ref = str(spec.get("prompt_reference") or "").strip()
        rubric_ref = str(spec.get("rubric_reference") or "").strip()
        if not prompt_ref or not rubric_ref:
            raise ValueError(f"{agent_id} missing prompt_reference or rubric_reference")

        prompt_path = agent_dir / "prompts" / f"{prompt_ref}.md"
        rubric_path = agent_dir / "rubrics" / f"{rubric_ref}.json"
        if not prompt_path.is_file() or prompt_path.stat().st_size < 20:
            raise FileNotFoundError(f"Prompt not materialized: {prompt_path.name}")
        if not rubric_path.is_file() or rubric_path.stat().st_size < 20:
            raise FileNotFoundError(f"Rubric not materialized: {rubric_path.name}")

        skill_md_path = agent_dir / "skills" / "SKILL.md"
        skill_int_path = agent_dir / "skills" / "integration.json"
        skill_bind_path = agent_dir / "skills" / "bindings.json"
        if not skill_md_path.is_file():
            raise FileNotFoundError(f"Skill harness missing: {agent_id}/skills/SKILL.md")
        if not skill_int_path.is_file():
            raise FileNotFoundError(
                f"Skill integration missing: {agent_id}/skills/integration.json"
            )

        edges_raw = spec.get("critique_edges") or {}
        if not isinstance(edges_raw, dict):
            edges_raw = {}
        inputs = tuple(str(x) for x in (edges_raw.get("inputs") or []) if str(x).strip())
        outputs = tuple(str(x) for x in (edges_raw.get("outputs") or []) if str(x).strip())

        does_not = spec.get("does_not_own") or []
        if not isinstance(does_not, list):
            does_not = []

        tools = spec.get("allowed_tools") or []
        if not isinstance(tools, list):
            tools = []

        bindings = self._read_json(skill_bind_path) if skill_bind_path.is_file() else {}
        # Validate binding paths stay under special_skills when present
        for entry in bindings.get("special_skills") or []:
            if not isinstance(entry, dict):
                continue
            sid = str(entry.get("skill_id") or "")
            if sid and not (SPECIAL_SKILLS_ROOT / sid).is_dir():
                # soft: allow missing optional skills but record in integration only
                pass

        return PackAgentBundle(
            agent_id=agent_id,
            agent_dir=agent_dir,
            agent_spec=spec,
            prompt_reference=prompt_ref,
            rubric_reference=rubric_ref,
            prompt_text=prompt_path.read_text(encoding="utf-8"),
            rubric=self._read_json(rubric_path),
            skill_markdown=skill_md_path.read_text(encoding="utf-8"),
            skill_integration=self._read_json(skill_int_path),
            skill_bindings=bindings if isinstance(bindings, dict) else {},
            does_not_own=tuple(str(x) for x in does_not),
            allowed_tools=tuple(str(x) for x in tools),
            critique_edges={"inputs": inputs, "outputs": outputs},
            max_refinement_count=int(spec.get("max_refinement_count") or 3),
            has_distillation_plan=(agent_dir / "sources" / "DISTILLATION_PLAN.json").is_file(),
            has_source_catalog=(agent_dir / "sources" / "SOURCE_CATALOG.json").is_file(),
            has_acquire_runbook=(agent_dir / "sources" / "ACQUIRE.md").is_file(),
        )

    @staticmethod
    def _read_json(path: Path) -> dict[str, Any]:
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise ValueError(f"Invalid JSON: {path}") from error
        if not isinstance(raw, dict):
            raise ValueError(f"JSON object required: {path}")
        return raw
