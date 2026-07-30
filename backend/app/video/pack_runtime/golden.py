"""Run pack agent golden fixtures under business/video/evals/agents/."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.video.pack_runtime.paths import EVALS_AGENTS_ROOT, SPINE_AGENT_IDS
from app.video.pack_runtime.runner import PackAgentRunner, PackAgentRunResult


@dataclass(slots=True)
class PackGoldenCaseResult:
    agent_id: str
    passed: bool
    run: PackAgentRunResult | None
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "passed": self.passed,
            "errors": self.errors,
            "run": self.run.to_dict() if self.run else None,
        }


@dataclass(slots=True)
class PackGoldenSuiteResult:
    total: int
    passed: int
    failed: int
    results: list[PackGoldenCaseResult]

    def to_dict(self) -> dict[str, Any]:
        return {
            "total": self.total,
            "passed": self.passed,
            "failed": self.failed,
            "results": [r.to_dict() for r in self.results],
        }


class PackGoldenRunner:
    """Offline golden suite for materialized pack agents."""

    def __init__(
        self,
        evals_root: Path = EVALS_AGENTS_ROOT,
        runner: PackAgentRunner | None = None,
    ) -> None:
        self._evals_root = evals_root.resolve()
        self._runner = runner or PackAgentRunner()

    def run_agent(self, agent_id: str) -> PackGoldenCaseResult:
        golden_path = self._evals_root / agent_id / "golden.json"
        if not golden_path.is_file():
            return PackGoldenCaseResult(
                agent_id=agent_id,
                passed=False,
                run=None,
                errors=[f"missing golden: {golden_path}"],
            )
        try:
            doc = json.loads(golden_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            return PackGoldenCaseResult(
                agent_id=agent_id, passed=False, run=None, errors=[str(error)]
            )
        if not isinstance(doc, dict):
            return PackGoldenCaseResult(
                agent_id=agent_id, passed=False, run=None, errors=["golden not object"]
            )

        input_block = doc.get("input") if isinstance(doc.get("input"), dict) else {}
        expect = doc.get("expect") if isinstance(doc.get("expect"), dict) else {}
        goal = str(input_block.get("goal") or f"golden task for {agent_id}")
        constraints = input_block.get("constraints")
        if not isinstance(constraints, dict):
            constraints = {"network": False, "production": False}
        inputs = input_block.get("inputs")
        if not isinstance(inputs, dict):
            inputs = {}

        errors: list[str] = []
        try:
            run = self._runner.run(
                agent_id,
                goal=goal,
                inputs=inputs,
                constraints=constraints,
            )
        except Exception as exc:  # noqa: BLE001 — suite continues
            return PackGoldenCaseResult(
                agent_id=agent_id, passed=False, run=None, errors=[str(exc)]
            )

        allowed_status = expect.get("output_status_in") or ["ok", "needs_refine", "needs_hitl"]
        if run.status not in set(allowed_status):
            errors.append(f"status {run.status} not in {allowed_status}")
        if expect.get("l1_passed", True) and not run.l1.get("passed"):
            errors.append("L1 not passed")
        if expect.get("artifact_required", True):
            if not run.artifact or not run.artifact.get("summary"):
                errors.append("artifact missing")
        if not run.skill_loaded:
            errors.append("skill not loaded")
        if not run.prompt_reference:
            errors.append("prompt_reference missing")

        return PackGoldenCaseResult(
            agent_id=agent_id,
            passed=len(errors) == 0,
            run=run,
            errors=errors,
        )

    def run_many(self, agent_ids: list[str] | tuple[str, ...]) -> PackGoldenSuiteResult:
        results = [self.run_agent(aid) for aid in agent_ids]
        passed = sum(1 for r in results if r.passed)
        return PackGoldenSuiteResult(
            total=len(results),
            passed=passed,
            failed=len(results) - passed,
            results=results,
        )

    def run_spine(self) -> PackGoldenSuiteResult:
        return self.run_many(SPINE_AGENT_IDS)

    def run_all_with_goldens(self) -> PackGoldenSuiteResult:
        if not self._evals_root.is_dir():
            return PackGoldenSuiteResult(total=0, passed=0, failed=0, results=[])
        ids = sorted(
            p.parent.name
            for p in self._evals_root.glob("*/golden.json")
            if p.is_file()
        )
        return self.run_many(ids)
