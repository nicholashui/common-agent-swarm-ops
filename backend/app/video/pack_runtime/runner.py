"""Offline deterministic pack agent runner (no live LLM/provider calls)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from app.video.pack_runtime.critique import CritiqueBus, CritiqueSeverity
from app.video.pack_runtime.knowledge import build_knowledge_usage
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
    """Full inventory of knowledge bound/enforced on this run (all sources, not only RETHINK)."""
    knowledge_usage: dict[str, Any] = field(default_factory=dict)

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
            "knowledge_usage": self.knowledge_usage,
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
        layers: dict[str, Any] = bundle.rubric.get("layers") or {}
        l2_rubric: dict[str, Any] = layers.get("L2_rubric") or {}
        l2_pass_threshold = int(l2_rubric.get("pass_threshold", 85))

        # L1 checks — artifact presence of pack materials
        l1_checks = self._l1_checks(bundle, goal)
        l1_passed = all(c.get("passed") for c in l1_checks)

        # Knowledge enforced by L1 harness checks
        enforced = {
            f"prompt:{bundle.prompt_reference}",
            f"rubric:{bundle.rubric_reference}",
            f"skill:{bundle.agent_id}",
            f"spec:{bundle.agent_id}",
        }
        if bundle.has_source_catalog:
            enforced.add(f"source_catalog:{bundle.agent_id}")
        if bundle.has_distillation_plan:
            enforced.add(f"distillation_plan:{bundle.agent_id}")

        if not l1_passed:
            knowledge = build_knowledge_usage(bundle, correlation_id=corr, enforced=enforced)
            return PackAgentRunResult(
                agent_id=agent_id,
                correlation_id=corr,
                status="failed",
                artifact={
                    "type": "empty",
                    "payload": {"knowledge_usage_summary": knowledge.get("summary")},
                    "summary": "L1 failed",
                },
                l1={"passed": False, "checks": l1_checks},
                l2={"score": 0, "dimensions": [], "passed": False},
                evidence_refs=self._evidence_refs(bundle, knowledge),
                prompt_reference=bundle.prompt_reference,
                rubric_reference=bundle.rubric_reference,
                skill_loaded=True,
                notes="L1 pack artifact validation failed",
                knowledge_usage=knowledge,
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
            if blockers and refinement >= 1:
                pass

        # Rubric scoring enforced this run
        enforced.add(f"rubric:{bundle.rubric_reference}")
        enforced.add(f"critique_edges:{bundle.agent_id}")

        critiques_emitted: list[dict[str, Any]] = []
        needs_hitl = status == "needs_hitl" or bool(blockers and status != "ok")

        if emit_self_critique_to:
            try:
                msg = self._bus.send(
                    correlation_id=corr,
                    from_id=agent_id,
                    to_id=emit_self_critique_to,
                    severity=CritiqueSeverity.MAJOR if status != "ok" else CritiqueSeverity.NIT,
                    claim=f"{agent_id} completed status={status} for goal",
                    allowed_outputs=bundle.critique_edges.get("outputs", ()),
                    artifact_ref=f"artifact:{agent_id}:{corr}",
                    evidence_refs=(f"prompt:{bundle.prompt_reference}",),
                )
                critiques_emitted.append(msg.to_dict())
            except PermissionError as error:
                notes_extra = str(error)
            else:
                notes_extra = ""
        else:
            notes_extra = ""

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

        knowledge = build_knowledge_usage(bundle, correlation_id=corr, enforced=enforced)
        # Attach compact knowledge summary onto artifact for easy UAT inspection
        if isinstance(artifact.get("payload"), dict):
            artifact = {
                **artifact,
                "payload": {
                    **artifact["payload"],
                    "knowledge_usage_summary": knowledge.get("summary"),
                    "knowledge_index": knowledge.get("index"),
                },
            }

        return PackAgentRunResult(
            agent_id=agent_id,
            correlation_id=corr,
            status=status if not needs_hitl else ("needs_hitl" if status != "ok" else status),
            artifact=artifact,
            l1={"passed": True, "checks": l1_checks},
            l2=l2,
            critiques_emitted=critiques_emitted,
            handoffs=handoffs,
            evidence_refs=self._evidence_refs(bundle, knowledge),
            refinement_count=refinement,
            notes=notes_extra
            or (
                f"Offline run using pack harness; inbound_critiques={len(inbound)}; "
                f"knowledge_bound={knowledge.get('summary', {}).get('bound_count')}; "
                f"rethink_items={knowledge.get('summary', {}).get('rethink_item_count')}"
            ),
            prompt_reference=bundle.prompt_reference,
            rubric_reference=bundle.rubric_reference,
            skill_loaded=True,
            needs_hitl=needs_hitl,
            knowledge_usage=knowledge,
        )

    def _failed(self, bundle: PackAgentBundle, corr: str, notes: str) -> PackAgentRunResult:
        enforced = {
            f"spec:{bundle.agent_id}",
            f"prompt:{bundle.prompt_reference}",
        }
        knowledge = build_knowledge_usage(bundle, correlation_id=corr, enforced=enforced)
        return PackAgentRunResult(
            agent_id=bundle.agent_id,
            correlation_id=corr,
            status="failed",
            artifact={
                "type": "empty",
                "payload": {"knowledge_usage_summary": knowledge.get("summary")},
                "summary": notes,
            },
            l1={
                "passed": False,
                "checks": [{"id": "fail_closed", "passed": False, "detail": notes}],
            },
            l2={"score": 0, "dimensions": [], "passed": False},
            evidence_refs=self._evidence_refs(bundle, knowledge),
            prompt_reference=bundle.prompt_reference,
            rubric_reference=bundle.rubric_reference,
            skill_loaded=True,
            notes=notes,
            knowledge_usage=knowledge,
        )

    @staticmethod
    def _evidence_refs(bundle: PackAgentBundle, knowledge: dict[str, Any]) -> list[str]:
        refs = [
            f"prompt:{bundle.prompt_reference}",
            f"rubric:{bundle.rubric_reference}",
            f"skill:{bundle.agent_id}",
            f"knowledge_usage:{knowledge.get('schema_version', 'v1')}",
        ]
        index = knowledge.get("index") if isinstance(knowledge.get("index"), dict) else {}
        rethink_ids = index.get("rethink_item_ids") or []
        if rethink_ids:
            refs.append("rethink_items:" + ",".join(str(i) for i in rethink_ids[:40]))
        bound = index.get("bound_asset_ids") or []
        refs.append(f"knowledge_bound_count:{len(bound)}")
        return refs

    @staticmethod
    def _l1_checks(bundle: PackAgentBundle, goal: str) -> list[dict[str, Any]]:
        return [
            {
                "id": "prompt_loaded",
                "passed": len(bundle.prompt_text) > 50 and "Responsibility" in bundle.prompt_text,
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
        raw_layers = bundle.rubric.get("layers")
        layers: dict[str, Any] = raw_layers if isinstance(raw_layers, dict) else {}
        raw_l2 = layers.get("L2_rubric")
        l2: dict[str, Any] = raw_l2 if isinstance(raw_l2, dict) else {}
        raw_dimensions = l2.get("dimensions")
        dims_spec: list[Any] = raw_dimensions if isinstance(raw_dimensions, list) else []
        threshold = int(l2.get("pass_threshold") or 85)
        base = 40.0 if force_fail else 90.0 if artifact.get("summary") and artifact.get("payload") else 50.0
        dimensions: list[dict[str, Any]] = []
        for dim in dims_spec:
            if not isinstance(dim, dict):
                continue
            dimensions.append(
                {
                    "id": dim.get("id"),
                    "name": dim.get("name"),
                    "score": base,
                    "weight": dim.get("weight"),
                    "source": dim.get("source"),
                }
            )
        if not dimensions:
            dimensions = [{"id": "d1", "name": "default", "score": base, "weight": 1.0}]
        total_weight = sum(
            float(weight) if isinstance(weight, (int, float)) else 0.0
            for dimension in dimensions
            for weight in (dimension.get("weight"),)
        ) or 1.0
        weighted_score = sum(
            float(dimension["score"])
            * (
                float(dimension["weight"])
                if isinstance(dimension.get("weight"), (int, float))
                else 0.0
            )
            for dimension in dimensions
        )
        score = round(weighted_score / total_weight, 2)
        return {
            "score": score,
            "dimensions": dimensions,
            "passed": score >= threshold and not force_fail,
            "threshold": threshold,
        }
