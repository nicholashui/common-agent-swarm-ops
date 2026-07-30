"""Offline deterministic pack agent runner (no live LLM/provider calls)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from app.video.pack_runtime.critique import CritiqueBus, CritiqueSeverity
from app.video.pack_runtime.loader import PackAgentBundle, PackAgentLoader


@dataclass(slots=True)
class PackAgentRunResult:
    agent_id: str
    correlation_id: str
    status: str
    artifact: dict[str, Any]
    l1: dict[str, Any]
    l2: dict[str, Any]
    critiques_emitted: list[dict[str, Any]] = field(default_factory=list)
    handoffs: list[dict[str, Any]] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    refinement_count: int = 0
    notes: str = ""
    prompt_reference: str = ""
    rubric_reference: str = ""
    skill_loaded: bool = False
    needs_hitl: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "correlation_id": self.correlation_id,
            "status": self.status,
            "artifact": self.artifact,
            "l1": self.l1,
            "l2": self.l2,
            "critiques_emitted": self.critiques_emitted,
            "handoffs": self.handoffs,
            "evidence_refs": self.evidence_refs,
            "refinement_count": self.refinement_count,
            "notes": self.notes,
            "prompt_reference": self.prompt_reference,
            "rubric_reference": self.rubric_reference,
            "skill_loaded": self.skill_loaded,
            "needs_hitl": self.needs_hitl,
        }


class PackAgentRunner:
    """Execute a pack agent offline using materialized prompt/rubric/skill artifacts."""

    def __init__(
        self,
        loader: PackAgentLoader | None = None,
        critique_bus: CritiqueBus | None = None,
    ) -> None:
        self._loader = loader or PackAgentLoader()
        self._bus = critique_bus or CritiqueBus()

    @property
    def critique_bus(self) -> CritiqueBus:
        return self._bus

    def run(
        self,
        agent_id: str,
        *,
        goal: str,
        correlation_id: str | None = None,
        inputs: dict[str, Any] | None = None,
        constraints: dict[str, Any] | None = None,
        emit_self_critique_to: str | None = None,
        force_l2_fail_once: bool = False,
    ) -> PackAgentRunResult:
        bundle = self._loader.load(agent_id)
        corr = correlation_id or f"corr_{uuid4().hex[:12]}"
        constraints = constraints or {}
        inputs = inputs or {}

        # Fail closed on production/network when offline golden constraints say so
        if constraints.get("network") is True:
            # still offline runner — reject explicit network requirement
            return self._failed(
                bundle,
                corr,
                "Offline runner refuses network=true constraints (fail-closed).",
            )
        if constraints.get("production") is True:
            return self._failed(
                bundle,
                corr,
                "Offline runner refuses production=true without live production path.",
            )

        inbound = self._bus.receive(
            correlation_id=corr,
            to_id=agent_id,
            allowed_inputs=bundle.critique_edges.get("inputs", ()),
        )

        refinement = 0
        max_ref = bundle.max_refinement_count
        l2_pass_threshold = int(
            ((bundle.rubric.get("layers") or {}).get("L2_rubric") or {}).get(
                "pass_threshold", 85
            )
        )

        # L1 checks — artifact presence of pack materials
        l1_checks = self._l1_checks(bundle, goal)
        l1_passed = all(c.get("passed") for c in l1_checks)
        if not l1_passed:
            return PackAgentRunResult(
                agent_id=agent_id,
                correlation_id=corr,
                status="failed",
                artifact={"type": "empty", "payload": {}, "summary": "L1 failed"},
                l1={"passed": False, "checks": l1_checks},
                l2={"score": 0, "dimensions": [], "passed": False},
                prompt_reference=bundle.prompt_reference,
                rubric_reference=bundle.rubric_reference,
                skill_loaded=True,
                notes="L1 pack artifact validation failed",
            )

        # Ingest blockers → may force refine path
        blockers = [m for m in inbound if m.severity is CritiqueSeverity.BLOCKER]
        force_fail = force_l2_fail_once

        while True:
            artifact = self._build_artifact(bundle, goal, inputs, refinement)
            l2 = self._score_l2(bundle, artifact, force_fail=force_fail and refinement == 0)
            if l2["passed"] and l2["score"] >= l2_pass_threshold and not blockers:
                status = "ok"
                break
            if refinement >= max_ref:
                status = "needs_hitl" if blockers else "needs_refine"
                break
            refinement += 1
            force_fail = False
            # treat refine as consuming one inbound blocker cycle
            if blockers and refinement >= 1:
                # after one refine attempt, open dispute to judge if still blocked
                pass

        critiques_emitted: list[dict[str, Any]] = []
        needs_hitl = status == "needs_hitl" or bool(blockers and status != "ok")

        # Optional self/outbound critique for collab proof
        target = emit_self_critique_to
        if target is None and bundle.critique_edges.get("outputs"):
            # only emit when explicitly asked or when needs refine for major issues
            target = None
        if emit_self_critique_to:
            try:
                msg = self._bus.send(
                    correlation_id=corr,
                    from_id=agent_id,
                    to_id=emit_self_critique_to,
                    severity=CritiqueSeverity.MAJOR
                    if status != "ok"
                    else CritiqueSeverity.NIT,
                    claim=f"{agent_id} completed status={status} for goal",
                    allowed_outputs=bundle.critique_edges.get("outputs", ()),
                    artifact_ref=f"artifact:{agent_id}:{corr}",
                    evidence_refs=(f"prompt:{bundle.prompt_reference}",),
                )
                critiques_emitted.append(msg.to_dict())
            except PermissionError as error:
                # edge not allowed — surface in notes, do not crash offline suite
                notes_extra = str(error)
            else:
                notes_extra = ""
        else:
            notes_extra = ""

        # Dispute path: unresolved blockers → judge if configured
        if blockers and status != "ok":
            judge = "video.judge"
            outputs = bundle.critique_edges.get("outputs", ())
            if judge in outputs or agent_id == "video.judge":
                try:
                    dispute = self._bus.send(
                        correlation_id=corr,
                        from_id=agent_id,
                        to_id=judge if agent_id != "video.judge" else agent_id,
                        severity=CritiqueSeverity.BLOCKER,
                        claim=f"Unresolved blocker after {refinement} refinements",
                        allowed_outputs=outputs if agent_id != "video.judge" else (agent_id,),
                        kind="dispute",
                    )
                    critiques_emitted.append(dispute.to_dict())
                    needs_hitl = True
                except PermissionError:
                    needs_hitl = True

        handoffs = [
            {
                "from_id": agent_id,
                "to_id": out_id,
                "correlation_id": corr,
                "artifact_ref": f"artifact:{agent_id}:{corr}",
            }
            for out_id in (bundle.critique_edges.get("outputs") or ())[:3]
        ]

        return PackAgentRunResult(
            agent_id=agent_id,
            correlation_id=corr,
            status=status if not needs_hitl else ("needs_hitl" if status != "ok" else status),
            artifact=artifact,
            l1={"passed": True, "checks": l1_checks},
            l2=l2,
            critiques_emitted=critiques_emitted,
            handoffs=handoffs,
            evidence_refs=[
                f"prompt:{bundle.prompt_reference}",
                f"rubric:{bundle.rubric_reference}",
                f"skill:{agent_id}",
            ],
            refinement_count=refinement,
            notes=notes_extra
            or f"Offline run using pack harness; inbound_critiques={len(inbound)}",
            prompt_reference=bundle.prompt_reference,
            rubric_reference=bundle.rubric_reference,
            skill_loaded=True,
            needs_hitl=needs_hitl,
        )

    def _failed(
        self, bundle: PackAgentBundle, corr: str, notes: str
    ) -> PackAgentRunResult:
        return PackAgentRunResult(
            agent_id=bundle.agent_id,
            correlation_id=corr,
            status="failed",
            artifact={"type": "empty", "payload": {}, "summary": notes},
            l1={"passed": False, "checks": [{"id": "fail_closed", "passed": False, "detail": notes}]},
            l2={"score": 0, "dimensions": [], "passed": False},
            prompt_reference=bundle.prompt_reference,
            rubric_reference=bundle.rubric_reference,
            skill_loaded=True,
            notes=notes,
        )

    @staticmethod
    def _l1_checks(bundle: PackAgentBundle, goal: str) -> list[dict[str, Any]]:
        return [
            {
                "id": "prompt_loaded",
                "passed": len(bundle.prompt_text) > 50
                and "Responsibility" in bundle.prompt_text,
                "detail": bundle.prompt_reference,
            },
            {
                "id": "rubric_loaded",
                "passed": bool(bundle.rubric.get("layers")),
                "detail": bundle.rubric_reference,
            },
            {
                "id": "skill_harness",
                "passed": "agent_id" in bundle.skill_markdown
                or bundle.agent_id in bundle.skill_markdown,
                "detail": "skills/SKILL.md",
            },
            {
                "id": "goal_present",
                "passed": bool(goal and goal.strip()),
                "detail": "task goal non-empty",
            },
            {
                "id": "distillation_scaffold",
                "passed": bundle.has_distillation_plan and bundle.has_source_catalog,
                "detail": "SOURCE_CATALOG + DISTILLATION_PLAN",
            },
        ]

    @staticmethod
    def _build_artifact(
        bundle: PackAgentBundle,
        goal: str,
        inputs: dict[str, Any],
        refinement: int,
    ) -> dict[str, Any]:
        return {
            "type": f"{bundle.agent_id}.offline_artifact",
            "payload": {
                "goal": goal,
                "inputs": inputs,
                "refinement": refinement,
                "does_not_own": list(bundle.does_not_own),
                "allowed_tools": list(bundle.allowed_tools),
                "mode": "offline_mock",
            },
            "summary": f"{bundle.agent_id} offline result for: {goal[:160]}",
        }

    @staticmethod
    def _score_l2(
        bundle: PackAgentBundle,
        artifact: dict[str, Any],
        *,
        force_fail: bool = False,
    ) -> dict[str, Any]:
        layers = bundle.rubric.get("layers") or {}
        l2 = layers.get("L2_rubric") or {}
        dims_spec = l2.get("dimensions") or []
        threshold = int(l2.get("pass_threshold") or 85)
        if force_fail:
            base = 40
        else:
            base = 90 if artifact.get("summary") and artifact.get("payload") else 50
        dimensions = []
        for dim in dims_spec:
            if not isinstance(dim, dict):
                continue
            score = base
            dimensions.append(
                {
                    "id": dim.get("id"),
                    "name": dim.get("name"),
                    "score": score,
                    "weight": dim.get("weight"),
                }
            )
        if not dimensions:
            dimensions = [{"id": "d1", "name": "default", "score": base, "weight": 1.0}]
        # weighted average
        total_w = sum(float(d.get("weight") or 0) for d in dimensions) or 1.0
        score = sum(float(d["score"]) * float(d.get("weight") or 0) for d in dimensions)
        score = round(score / total_w, 2)
        return {
            "score": score,
            "dimensions": dimensions,
            "passed": score >= threshold and not force_fail,
            "threshold": threshold,
        }
