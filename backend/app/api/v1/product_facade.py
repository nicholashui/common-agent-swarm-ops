"""In-process product façade state for browser-facing commons/swarms APIs.

Reads self-contained pack agent folders for catalog projections. Mutations are
organization-scoped, require action_reference_id where specified, and never
activate production providers or invent tenant authority.
"""

from __future__ import annotations

import json
import re
import threading
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from app.models.identifiers import ActorId, CorrelationId, OrganizationId

# backend/app/api/v1/this.py -> parents[4] == repository root
_ROOT = Path(__file__).resolve().parents[4]
_PACK_ROOTS = (
    _ROOT / "business" / "video" / "agents",
    _ROOT / "business" / "specials" / "agents",
)
_SAFE_ID = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]*$")


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:16]}"


def _plain_excerpt(text: str, limit: int = 280) -> str:
    match = re.search(
        r"##\s+Responsibility\s*\n+(.*?)(?=\n#{1,3}\s+|\Z)",
        text,
        re.S | re.I,
    )
    body = match.group(1).strip() if match else text[:limit]
    body = re.sub(r"```.*?```", " ", body, flags=re.S)
    body = re.sub(r"`([^`]+)`", r"\1", body)
    body = re.sub(r"(?m)^\s{0,3}#{1,6}\s+", "", body)
    body = re.sub(r"(?m)^\s{0,3}>\s?", "", body)
    body = re.sub(r"[|*_~\[\]()]", " ", body)
    body = re.sub(r"\s+", " ", body).strip()
    return body[:limit]


@dataclass(frozen=True, slots=True)
class PackAgentCatalogEntry:
    agent_id: str
    pack: str
    name: str
    role: str
    status: str
    description: str
    version_label: str
    folder_path: str
    has_spec_md: bool
    network_access: bool
    production_activation_requested: bool
    prompt_reference: str
    rubric_reference: str
    provider: str
    allowed_tools: tuple[str, ...]
    domains: tuple[str, ...]


@dataclass
class ActionRefRecord:
    action_id: str
    organization_id: str
    kind: str
    label: str
    eligible: bool
    resource_ref: str
    actor_id: str | None = None
    consumed: bool = False


@dataclass
class ProposalRecord:
    proposal_id: str
    organization_id: str
    target_type: str
    target_id: str
    base_version: str
    summary: str
    status: str
    actor_id: str
    created_at: datetime
    evidence_refs: tuple[str, ...] = ()


@dataclass
class RolloutRecord:
    """Bounded sandbox/canary rollout (A/B or safe rollout). Never auto-promotes production."""

    rollout_id: str
    organization_id: str
    agent_id: str
    rollout_type: str  # ab_test | safe_rollout
    baseline_version: str
    candidate_version: str
    status: str  # pending | active_canary | stopped | rolled_back
    actor_id: str
    created_at: datetime
    correlation_id: str
    criteria: list[dict[str, Any]] = field(default_factory=list)
    summary: str = ""


@dataclass
class SwarmRecord:
    swarm_id: str
    organization_id: str
    name: str
    revision: int
    status: str
    created_at: datetime
    updated_at: datetime
    pattern_ref: str | None = None
    nodes: list[dict[str, Any]] = field(default_factory=list)
    edges: list[dict[str, Any]] = field(default_factory=list)
    policy: dict[str, Any] = field(default_factory=dict)
    members: list[dict[str, Any]] = field(default_factory=list)
    pins: list[dict[str, Any]] = field(default_factory=list)
    last_run_id: str | None = None


@dataclass
class ActivityRecord:
    activity_id: str
    organization_id: str
    category: str
    severity: str
    summary: str
    subject_reference: str
    occurred_at: datetime
    correlation_id: str
    status: str = "recorded"


class ProductFacadeService:
    """Org-scoped façade backing /commons, /swarms, /activity product routes."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._catalog: tuple[PackAgentCatalogEntry, ...] | None = None
        self._actions: dict[str, ActionRefRecord] = {}
        self._proposals: dict[str, ProposalRecord] = {}
        self._rollouts: dict[str, RolloutRecord] = {}
        self._swarms: dict[str, SwarmRecord] = {}
        self._activity: list[ActivityRecord] = []
        self._patterns: tuple[dict[str, Any], ...] = (
            {
                "id": "parallel-research",
                "name": "Parallel Research",
                "version_label": "pattern · 1.0",
                "when_to_use": "Independent research branches with verification join.",
                "status": "active",
            },
            {
                "id": "verification-loop",
                "name": "Verification Loop",
                "version_label": "pattern · 1.0",
                "when_to_use": "Iterate produce → critique → refine under budget.",
                "status": "active",
            },
            {
                "id": "hierarchical-supervisor",
                "name": "Hierarchical Supervisor",
                "version_label": "pattern · 1.0",
                "when_to_use": "Supervisor routes work to specialists.",
                "status": "active",
            },
        )

    def catalog(self) -> tuple[PackAgentCatalogEntry, ...]:
        with self._lock:
            if self._catalog is None:
                self._catalog = self._load_catalog()
            return self._catalog

    def _load_catalog(self) -> tuple[PackAgentCatalogEntry, ...]:
        entries: list[PackAgentCatalogEntry] = []
        for root in _PACK_ROOTS:
            if not root.is_dir():
                continue
            pack = root.parent.name  # video | specials
            for agent_dir in sorted(root.iterdir()):
                if not agent_dir.is_dir():
                    continue
                spec_path = agent_dir / "agent_spec.json"
                if not spec_path.is_file():
                    continue
                try:
                    spec = json.loads(spec_path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
                agent_id = str(spec.get("agent_id") or agent_dir.name)
                if not _SAFE_ID.match(agent_id):
                    continue
                model = (
                    spec.get("model_policy") if isinstance(spec.get("model_policy"), dict) else {}
                )
                tools = (
                    spec.get("allowed_tools") if isinstance(spec.get("allowed_tools"), list) else []
                )
                status = str(
                    spec.get("status") or ("draft" if pack == "specials" else "registered")
                )
                description = ""
                spec_md = agent_dir / "SPEC.md"
                if spec_md.is_file():
                    try:
                        description = _plain_excerpt(
                            spec_md.read_text(encoding="utf-8", errors="replace")
                        )
                    except OSError:
                        description = ""
                if not description:
                    description = str(spec.get("role") or f"{pack} agent {agent_id}")
                bare = agent_id.split(".", 1)[-1]
                name = " ".join(p.capitalize() for p in re.split(r"[-_.]+", bare) if p)
                entries.append(
                    PackAgentCatalogEntry(
                        agent_id=agent_id,
                        pack=pack,
                        name=name,
                        role=str(spec.get("role") or ""),
                        status=status,
                        description=description,
                        version_label=f"{pack} · {status} · schema {spec.get('schema_version', '1.0')}",
                        folder_path=f"business/{pack}/agents/{agent_dir.name}",
                        has_spec_md=spec_md.is_file(),
                        network_access=bool(model.get("network_access")),
                        production_activation_requested=bool(
                            spec.get("production_activation_requested")
                        ),
                        prompt_reference=str(spec.get("prompt_reference") or ""),
                        rubric_reference=str(spec.get("rubric_reference") or ""),
                        provider=str(model.get("provider") or ""),
                        allowed_tools=tuple(str(t) for t in tools),
                        domains=(pack,),
                    )
                )
        return tuple(entries)

    def get_agent(self, agent_id: str) -> PackAgentCatalogEntry | None:
        for entry in self.catalog():
            if entry.agent_id == agent_id:
                return entry
        return None

    def issue_action(
        self,
        *,
        organization_id: OrganizationId,
        kind: str,
        label: str,
        resource_ref: str,
        eligible: bool = True,
        actor_id: ActorId | None = None,
    ) -> ActionRefRecord:
        action_id = _new_id("act")
        record = ActionRefRecord(
            action_id=action_id,
            organization_id=str(organization_id),
            kind=kind,
            label=label,
            eligible=eligible,
            resource_ref=resource_ref,
            actor_id=str(actor_id) if actor_id else None,
        )
        with self._lock:
            self._actions[action_id] = record
        return record

    def consume_action(
        self,
        *,
        organization_id: OrganizationId,
        action_reference_id: str,
        expected_kind: str | None = None,
        resource_ref: str | None = None,
    ) -> ActionRefRecord | None:
        with self._lock:
            record = self._actions.get(action_reference_id)
            if record is None:
                return None
            if record.organization_id != str(organization_id):
                return None
            if record.consumed or not record.eligible:
                return None
            if expected_kind is not None and record.kind != expected_kind:
                return None
            if resource_ref is not None and record.resource_ref != resource_ref:
                return None
            record.consumed = True
            return record

    def peek_action(
        self, organization_id: OrganizationId, action_reference_id: str
    ) -> ActionRefRecord | None:
        with self._lock:
            record = self._actions.get(action_reference_id)
            if record is None or record.organization_id != str(organization_id):
                return None
            return record

    def action_payload(self, record: ActionRefRecord) -> dict[str, Any]:
        return {
            "id": record.action_id,
            "label": record.label,
            "kind": record.kind,
            "eligible": record.eligible and not record.consumed,
            "resource_ref": record.resource_ref,
        }

    def agent_actions(
        self, organization_id: OrganizationId, agent: PackAgentCatalogEntry
    ) -> list[dict[str, Any]]:
        """Issue fresh action references for catalog cards / detail."""
        refs = [
            self.issue_action(
                organization_id=organization_id,
                kind="add_to_swarm",
                label="Add to Swarm",
                resource_ref=agent.agent_id,
                eligible=True,
            ),
            self.issue_action(
                organization_id=organization_id,
                kind="propose_improvement",
                label="Propose Improvement",
                resource_ref=agent.agent_id,
                eligible=True,
            ),
            self.issue_action(
                organization_id=organization_id,
                kind="fork_agent",
                label="Fork to Custom",
                resource_ref=agent.agent_id,
                eligible=True,
            ),
            self.issue_action(
                organization_id=organization_id,
                kind="rollout.ab_test",
                label="A/B Test vs newer",
                resource_ref=agent.agent_id,
                eligible=True,
            ),
            self.issue_action(
                organization_id=organization_id,
                kind="rollout.safe_all",
                label="Safe Rollout All",
                resource_ref=agent.agent_id,
                eligible=True,
            ),
        ]
        return [self.action_payload(r) for r in refs]

    def list_agents(
        self,
        organization_id: OrganizationId,
        *,
        q: str | None = None,
        domain: str | None = None,
        pack: str | None = None,
        status: str | None = None,
        cursor: str | None = None,
        limit: int = 36,
    ) -> dict[str, Any]:
        items = list(self.catalog())
        if q:
            token = q.strip().lower()
            items = [
                a
                for a in items
                if token in a.agent_id.lower()
                or token in a.name.lower()
                or token in a.description.lower()
                or token in a.role.lower()
            ]
        if domain:
            items = [a for a in items if domain in a.domains]
        if pack:
            items = [a for a in items if a.pack == pack]
        if status:
            items = [a for a in items if a.status == status]
        start = 0
        if cursor:
            try:
                start = int(cursor)
            except ValueError:
                start = 0
        limit = max(1, min(limit, 100))
        page = items[start : start + limit]
        next_cursor = str(start + limit) if start + limit < len(items) else None
        as_of = _utc_now().isoformat()
        return {
            "items": [
                {
                    "id": a.agent_id,
                    "name": a.name,
                    "version_label": a.version_label,
                    "status": a.status,
                    "description": a.description,
                    "badges": [
                        a.pack,
                        a.status,
                        "self-contained",
                        "no-network" if not a.network_access else "network?",
                    ],
                    "domains": list(a.domains),
                    "metrics": {
                        "success_rate": None,
                        "avg_tokens": None,
                        "latency_tier": "local",
                        "run_count": None,
                    },
                    "usage": {
                        "global_swarms": None,
                        "my_swarms": None,
                        "last_used_at": None,
                    },
                    "pack": a.pack,
                    "folder_path": a.folder_path,
                    "spec_doc_path": f"/docs/agents/{a.agent_id}/SPEC.md"
                    if a.has_spec_md
                    else None,
                    "actions": self.agent_actions(organization_id, a),
                }
                for a in page
            ],
            "page": {"next_cursor": next_cursor, "limit": limit},
            "freshness": {"as_of": as_of, "state": "cached"},
        }

    def agent_detail(
        self, organization_id: OrganizationId, agent_id: str, version: str | None = None
    ) -> dict[str, Any] | None:
        agent = self.get_agent(agent_id)
        if agent is None:
            return None
        ver = version or "current"
        return {
            "id": agent.agent_id,
            "name": agent.name,
            "version": ver,
            "version_label": agent.version_label,
            "status": agent.status,
            "description": agent.description,
            "role": agent.role,
            "pack": agent.pack,
            "folder_path": agent.folder_path,
            "spec_doc_path": f"/docs/agents/{agent.agent_id}/SPEC.md"
            if agent.has_spec_md
            else None,
            "config_summaries": [
                {
                    "id": "runtime",
                    "title": "Runtime binding",
                    "lines": [
                        f"agent_id: {agent.agent_id}",
                        f"status: {agent.status}",
                        f"role: {agent.role}",
                        f"production_activation_requested: {agent.production_activation_requested}",
                    ],
                },
                {
                    "id": "model",
                    "title": "Model policy",
                    "lines": [
                        f"provider: {agent.provider}",
                        f"network_access: {agent.network_access}",
                    ],
                },
                {
                    "id": "tools",
                    "title": "Tools & critique",
                    "lines": [
                        f"allowed_tools: {list(agent.allowed_tools)}",
                        f"prompt_reference: {agent.prompt_reference}",
                        f"rubric_reference: {agent.rubric_reference}",
                    ],
                },
            ],
            "actions": self.agent_actions(organization_id, agent)
            + [
                self.action_payload(
                    self.issue_action(
                        organization_id=organization_id,
                        kind="playground_run",
                        label="Run playground",
                        resource_ref=agent.agent_id,
                        eligible=True,
                    )
                )
            ],
            "versions": [
                {
                    "id": "current",
                    "label": agent.version_label or "current",
                    "status": agent.status,
                    "role": "baseline",
                },
                {
                    "id": "candidate",
                    "label": "candidate (proposal/sandbox)",
                    "status": "draft",
                    "role": "candidate",
                },
            ],
            "rollout_defaults": {
                "baseline_version": "current",
                "candidate_version": "candidate",
                "note": (
                    "A/B and safe rollout create sandbox canary campaigns only. "
                    "Production promotion requires separate evidence and approval."
                ),
            },
            "freshness": {"as_of": _utc_now().isoformat(), "state": "cached"},
        }

    def create_rollout(
        self,
        *,
        organization_id: OrganizationId,
        actor_id: ActorId,
        correlation_id: CorrelationId,
        agent_id: str,
        action_reference_id: str,
        rollout_type: str,
        baseline_version: str,
        candidate_version: str,
        summary: str = "",
    ) -> RolloutRecord | None:
        """Create a fail-closed sandbox/canary rollout (A/B or safe rollout).

        Does not mutate published commons or activate production traffic.
        """
        expected = (
            "rollout.ab_test"
            if rollout_type == "ab_test"
            else "rollout.safe_all"
            if rollout_type == "safe_rollout"
            else None
        )
        if expected is None:
            return None
        action = self.consume_action(
            organization_id=organization_id,
            action_reference_id=action_reference_id,
            expected_kind=expected,
            resource_ref=agent_id,
        )
        if action is None or self.get_agent(agent_id) is None:
            return None
        baseline = (baseline_version or "current").strip() or "current"
        candidate = (candidate_version or "candidate").strip() or "candidate"
        if baseline == candidate:
            return None
        now = _utc_now()
        criteria: list[dict[str, Any]] = [
            {
                "id": "eval_gate",
                "label": "Evaluation harness gate",
                "status": "pending",
            },
            {
                "id": "error_budget",
                "label": "Error budget within bounds",
                "status": "pending",
            },
            {
                "id": "human_signoff",
                "label": "Human promotion approval",
                "status": "pending",
            },
        ]
        if rollout_type == "ab_test":
            criteria.insert(
                0,
                {
                    "id": "pairwise_preference",
                    "label": "A/B pairwise preference vs baseline",
                    "status": "pending",
                },
            )
        record = RolloutRecord(
            rollout_id=_new_id("roll"),
            organization_id=str(organization_id),
            agent_id=agent_id,
            rollout_type=rollout_type,
            baseline_version=baseline,
            candidate_version=candidate,
            status="active_canary",
            actor_id=str(actor_id),
            created_at=now,
            correlation_id=str(correlation_id),
            criteria=criteria,
            summary=summary
            or (
                f"A/B canary {candidate} vs {baseline} for {agent_id}"
                if rollout_type == "ab_test"
                else f"Safe rollout canary for {agent_id} ({candidate})"
            ),
        )
        with self._lock:
            self._rollouts[record.rollout_id] = record
            self._activity.append(
                ActivityRecord(
                    activity_id=_new_id("acty"),
                    organization_id=str(organization_id),
                    category="rollout",
                    severity="info",
                    summary=record.summary,
                    subject_reference=record.rollout_id,
                    occurred_at=now,
                    correlation_id=str(correlation_id),
                    status=record.status,
                )
            )
        return record

    def get_rollout(
        self, organization_id: OrganizationId, rollout_id: str
    ) -> dict[str, Any] | None:
        with self._lock:
            record = self._rollouts.get(rollout_id)
            if record is None or record.organization_id != str(organization_id):
                return None
            return self._rollout_payload(record)

    def rollout_impact(
        self, organization_id: OrganizationId, rollout_id: str
    ) -> dict[str, Any] | None:
        payload = self.get_rollout(organization_id, rollout_id)
        if payload is None:
            return None
        return {
            "rollout_id": rollout_id,
            "agent_id": payload["agent_id"],
            "baseline_version": payload["baseline_version"],
            "candidate_version": payload["candidate_version"],
            "impact": [
                {
                    "surface": "sandbox_canary",
                    "scope": "organization",
                    "traffic_percent": 0,
                    "note": "No production traffic until authorize + promote.",
                },
                {
                    "surface": "commons_published",
                    "scope": "immutable",
                    "change": "none",
                    "note": "Published agent versions are not mutated by canary start.",
                },
            ],
            "criteria": payload["criteria"],
            "status": payload["status"],
            "freshness": {"as_of": _utc_now().isoformat(), "state": "cached"},
        }

    def list_rollouts(
        self, organization_id: OrganizationId, *, agent_id: str | None = None, limit: int = 50
    ) -> dict[str, Any]:
        with self._lock:
            items = [
                self._rollout_payload(r)
                for r in self._rollouts.values()
                if r.organization_id == str(organization_id)
                and (agent_id is None or r.agent_id == agent_id)
            ]
        items.sort(key=lambda x: x["created_at"], reverse=True)
        return {
            "items": items[: max(1, min(limit, 100))],
            "freshness": {"as_of": _utc_now().isoformat(), "state": "cached"},
        }

    @staticmethod
    def _rollout_payload(record: RolloutRecord) -> dict[str, Any]:
        return {
            "rollout_id": record.rollout_id,
            "agent_id": record.agent_id,
            "type": record.rollout_type,
            "baseline_version": record.baseline_version,
            "candidate_version": record.candidate_version,
            "status": record.status,
            "summary": record.summary,
            "criteria": list(record.criteria),
            "actor_id": record.actor_id,
            "correlation_id": record.correlation_id,
            "created_at": record.created_at.isoformat(),
            "production_activation": False,
            "note": (
                "Sandbox/canary only. Failed criteria block promotion; no silent production apply."
            ),
        }

    def create_proposal(
        self,
        *,
        organization_id: OrganizationId,
        actor_id: ActorId,
        correlation_id: CorrelationId,
        target_type: str,
        target_id: str,
        base_version: str,
        summary: str,
        evidence_refs: list[str],
        action_reference_id: str,
    ) -> ProposalRecord | None:
        kind = "propose_improvement" if target_type == "agent" else "propose_pattern"
        action = self.consume_action(
            organization_id=organization_id,
            action_reference_id=action_reference_id,
            expected_kind=kind,
            resource_ref=target_id,
        )
        if action is None:
            return None
        if target_type == "agent" and self.get_agent(target_id) is None:
            return None
        record = ProposalRecord(
            proposal_id=_new_id("prop"),
            organization_id=str(organization_id),
            target_type=target_type,
            target_id=target_id,
            base_version=base_version,
            summary=summary,
            status="submitted",
            actor_id=str(actor_id),
            created_at=_utc_now(),
            evidence_refs=tuple(evidence_refs),
        )
        with self._lock:
            self._proposals[record.proposal_id] = record
            self._activity.append(
                ActivityRecord(
                    activity_id=_new_id("acty"),
                    organization_id=str(organization_id),
                    category="proposal",
                    severity="info",
                    summary=f"Proposal submitted for {target_type} {target_id}",
                    subject_reference=record.proposal_id,
                    occurred_at=record.created_at,
                    correlation_id=str(correlation_id),
                    status="submitted",
                )
            )
        return record

    def fork_agent(
        self,
        *,
        organization_id: OrganizationId,
        actor_id: ActorId,
        agent_id: str,
        action_reference_id: str,
        label: str | None,
    ) -> dict[str, Any] | None:
        action = self.consume_action(
            organization_id=organization_id,
            action_reference_id=action_reference_id,
            expected_kind="fork_agent",
            resource_ref=agent_id,
        )
        if action is None or self.get_agent(agent_id) is None:
            return None
        fork_id = _new_id("fork")
        return {
            "fork_id": fork_id,
            "forked_from": {"id": agent_id, "version": "current"},
            "status": "draft",
            "label": label or f"Fork of {agent_id}",
            "organization_id": str(organization_id),
            "actor_id": str(actor_id),
        }

    def list_patterns(self, organization_id: OrganizationId) -> dict[str, Any]:
        items = []
        for pattern in self._patterns:
            instantiate = self.issue_action(
                organization_id=organization_id,
                kind="instantiate_pattern",
                label="Instantiate",
                resource_ref=pattern["id"],
            )
            propose = self.issue_action(
                organization_id=organization_id,
                kind="propose_pattern",
                label="Propose pattern",
                resource_ref=pattern["id"],
                eligible=True,
            )
            items.append(
                {
                    **pattern,
                    "metrics": {},
                    "graph_preview_ref": None,
                    "actions": [
                        self.action_payload(instantiate),
                        self.action_payload(propose),
                    ],
                }
            )
        return {
            "items": items,
            "page": {"next_cursor": None, "limit": len(items)},
            "freshness": {"as_of": _utc_now().isoformat(), "state": "cached"},
        }

    def create_swarm(
        self,
        *,
        organization_id: OrganizationId,
        actor_id: ActorId,
        correlation_id: CorrelationId,
        name: str,
        action_reference_id: str | None,
        pattern_ref: str | None,
        goal_summary: str | None,
        initial_graph: dict[str, Any] | None,
    ) -> SwarmRecord | None:
        # Creating a swarm may use instantiate_pattern action or a free compose action.
        if action_reference_id:
            action = self.peek_action(organization_id, action_reference_id)
            if action is None or action.consumed or not action.eligible:
                return None
            if action.kind not in {"instantiate_pattern", "compose_swarm", "create_swarm"}:
                return None
            self.consume_action(
                organization_id=organization_id,
                action_reference_id=action_reference_id,
                expected_kind=action.kind,
            )
            if pattern_ref is None and action.kind == "instantiate_pattern":
                pattern_ref = action.resource_ref
        now = _utc_now()
        nodes = list((initial_graph or {}).get("nodes") or [])
        edges = list((initial_graph or {}).get("edges") or [])
        policy = dict((initial_graph or {}).get("policy") or {})
        record = SwarmRecord(
            swarm_id=_new_id("swarm"),
            organization_id=str(organization_id),
            name=name or "Untitled swarm",
            revision=1 if nodes or edges else 0,
            status="draft",
            created_at=now,
            updated_at=now,
            pattern_ref=pattern_ref,
            nodes=nodes,
            edges=edges,
            policy=policy,
        )
        with self._lock:
            self._swarms[record.swarm_id] = record
            self._activity.append(
                ActivityRecord(
                    activity_id=_new_id("acty"),
                    organization_id=str(organization_id),
                    category="swarm",
                    severity="info",
                    summary=f"Swarm draft created: {record.name}",
                    subject_reference=record.swarm_id,
                    occurred_at=now,
                    correlation_id=str(correlation_id),
                )
            )
        return record

    def get_swarm(self, organization_id: OrganizationId, swarm_id: str) -> SwarmRecord | None:
        with self._lock:
            record = self._swarms.get(swarm_id)
            if record is None or record.organization_id != str(organization_id):
                return None
            return record

    def patch_graph(
        self,
        *,
        organization_id: OrganizationId,
        swarm_id: str,
        action_reference_id: str,
        expected_revision: int,
        graph: dict[str, Any],
    ) -> SwarmRecord | None:
        action = self.consume_action(
            organization_id=organization_id,
            action_reference_id=action_reference_id,
            expected_kind="edit_graph",
            resource_ref=swarm_id,
        )
        if action is None:
            return None
        with self._lock:
            record = self._swarms.get(swarm_id)
            if record is None or record.organization_id != str(organization_id):
                return None
            if record.revision != expected_revision:
                return None
            record.nodes = list(graph.get("nodes") or [])
            record.edges = list(graph.get("edges") or [])
            record.policy = dict(graph.get("policy") or {})
            record.revision += 1
            record.updated_at = _utc_now()
            record.status = "draft"
            return record

    def issue_swarm_actions(
        self, organization_id: OrganizationId, swarm: SwarmRecord
    ) -> list[dict[str, Any]]:
        kinds = [
            ("edit_graph", "Edit graph"),
            ("validate_swarm", "Validate"),
            ("run_swarm", "Run"),
            ("export_swarm", "Export"),
            ("add_to_swarm", "Add agent member"),
            ("pin_versions", "Pin versions"),
        ]
        return [
            self.action_payload(
                self.issue_action(
                    organization_id=organization_id,
                    kind=kind,
                    label=label,
                    resource_ref=swarm.swarm_id,
                )
            )
            for kind, label in kinds
        ]

    def validate_swarm(
        self,
        organization_id: OrganizationId,
        swarm_id: str,
        action_reference_id: str,
    ) -> dict[str, Any] | None:
        action = self.consume_action(
            organization_id=organization_id,
            action_reference_id=action_reference_id,
            expected_kind="validate_swarm",
            resource_ref=swarm_id,
        )
        if action is None:
            return None
        swarm = self.get_swarm(organization_id, swarm_id)
        if swarm is None:
            return None
        issues: list[dict[str, str]] = []
        if swarm.revision == 0 and not swarm.nodes:
            issues.append({"field": "graph", "reason": "Graph has no nodes."})
        for node in swarm.nodes:
            kind = str(node.get("kind") or "")
            if kind == "custom_agent" and not (
                node.get("forked_from") or node.get("custom_reason")
            ):
                issues.append(
                    {
                        "field": f"nodes.{node.get('id', '?')}",
                        "reason": "custom_agent requires forked_from or custom_reason.",
                    }
                )
        return {
            "swarm_id": swarm.swarm_id,
            "revision": swarm.revision,
            "ok": len(issues) == 0,
            "issues": issues,
        }

    def add_member(
        self,
        *,
        organization_id: OrganizationId,
        swarm_id: str,
        action_reference_id: str,
        agent_id: str,
        agent_version: str | None,
        pin_policy: str | None,
    ) -> dict[str, Any] | None:
        # Action may be add_to_swarm on agent card (resource=agent) or swarm.
        action = self.peek_action(organization_id, action_reference_id)
        if action is None or action.consumed or not action.eligible:
            return None
        if action.kind != "add_to_swarm":
            return None
        if action.resource_ref not in {agent_id, swarm_id}:
            return None
        self.consume_action(
            organization_id=organization_id,
            action_reference_id=action_reference_id,
            expected_kind="add_to_swarm",
        )
        if self.get_agent(agent_id) is None:
            return None
        with self._lock:
            swarm = self._swarms.get(swarm_id)
            if swarm is None or swarm.organization_id != str(organization_id):
                return None
            node_id = f"node_{agent_id.replace('.', '_')}"
            member = {
                "node_id": node_id,
                "agent_id": agent_id,
                "agent_version": agent_version or "current",
                "pin_policy": pin_policy or "exact",
            }
            swarm.members.append(member)
            swarm.nodes.append(
                {
                    "id": node_id,
                    "kind": "common_agent",
                    "common_agent": {
                        "id": agent_id,
                        "version": agent_version or "current",
                    },
                    "position": {"x": 100 + 40 * len(swarm.nodes), "y": 120},
                    "overrides": None,
                }
            )
            swarm.revision += 1
            swarm.updated_at = _utc_now()
            return {
                "swarm_id": swarm.swarm_id,
                "revision": swarm.revision,
                "node_id": node_id,
                "member": member,
            }

    def set_pins(
        self,
        *,
        organization_id: OrganizationId,
        swarm_id: str,
        action_reference_id: str,
        pins: list[dict[str, Any]],
    ) -> dict[str, Any] | None:
        action = self.consume_action(
            organization_id=organization_id,
            action_reference_id=action_reference_id,
            expected_kind="pin_versions",
            resource_ref=swarm_id,
        )
        if action is None:
            return None
        with self._lock:
            swarm = self._swarms.get(swarm_id)
            if swarm is None or swarm.organization_id != str(organization_id):
                return None
            swarm.pins = list(pins)
            swarm.revision += 1
            swarm.updated_at = _utc_now()
            return {
                "swarm_id": swarm.swarm_id,
                "revision": swarm.revision,
                "pins": swarm.pins,
            }

    def start_run(
        self,
        *,
        organization_id: OrganizationId,
        swarm_id: str,
        action_reference_id: str,
        correlation_id: CorrelationId,
    ) -> dict[str, Any] | None:
        action = self.consume_action(
            organization_id=organization_id,
            action_reference_id=action_reference_id,
            expected_kind="run_swarm",
            resource_ref=swarm_id,
        )
        if action is None:
            return None
        with self._lock:
            swarm = self._swarms.get(swarm_id)
            if swarm is None or swarm.organization_id != str(organization_id):
                return None
            if swarm.revision == 0 and not swarm.nodes:
                return None
            run_id = _new_id("run")
            swarm.last_run_id = run_id
            swarm.status = "queued"
            swarm.updated_at = _utc_now()
            self._activity.append(
                ActivityRecord(
                    activity_id=_new_id("acty"),
                    organization_id=str(organization_id),
                    category="run",
                    severity="info",
                    summary=f"Swarm run queued for {swarm.name}",
                    subject_reference=run_id,
                    occurred_at=swarm.updated_at,
                    correlation_id=str(correlation_id),
                    status="queued",
                )
            )
            return {
                "run_id": run_id,
                "swarm_id": swarm.swarm_id,
                "status": "queued",
                "events_topics": [f"run:{run_id}", f"swarm:{swarm.swarm_id}"],
                "note": (
                    "Façade accepted run intent. Wire to workflow create+dispatch "
                    "for engine execution when a compiled definition is available."
                ),
            }

    def export_swarm(
        self,
        organization_id: OrganizationId,
        swarm_id: str,
        action_reference_id: str,
        export_format: str,
    ) -> dict[str, Any] | None:
        action = self.consume_action(
            organization_id=organization_id,
            action_reference_id=action_reference_id,
            expected_kind="export_swarm",
            resource_ref=swarm_id,
        )
        if action is None:
            return None
        swarm = self.get_swarm(organization_id, swarm_id)
        if swarm is None:
            return None
        export_id = _new_id("exp")
        return {
            "export_id": export_id,
            "format": export_format if export_format in {"json", "yaml"} else "json",
            "download_ref": f"export:{export_id}",
            "expires_at": _utc_now().isoformat(),
            "revision": swarm.revision,
        }

    def list_activity(
        self,
        organization_id: OrganizationId,
        *,
        cursor: str | None = None,
        limit: int = 50,
    ) -> dict[str, Any]:
        with self._lock:
            rows = [a for a in self._activity if a.organization_id == str(organization_id)]
        rows = list(reversed(rows))
        start = int(cursor) if cursor and cursor.isdigit() else 0
        limit = max(1, min(limit, 100))
        page = rows[start : start + limit]
        return {
            "items": [
                {
                    "id": a.activity_id,
                    "category": a.category,
                    "severity": a.severity,
                    "summary": a.summary,
                    "subject_reference": a.subject_reference,
                    "status": a.status,
                    "occurred_at": a.occurred_at.isoformat(),
                    "correlation_id": a.correlation_id,
                    "actions": [],
                }
                for a in page
            ],
            "page": {
                "next_cursor": str(start + limit) if start + limit < len(rows) else None,
                "limit": limit,
            },
            "freshness": {"as_of": _utc_now().isoformat(), "state": "live"},
        }

    def commons_health(self) -> dict[str, Any]:
        catalog = self.catalog()
        by_pack: dict[str, int] = {}
        for a in catalog:
            by_pack[a.pack] = by_pack.get(a.pack, 0) + 1
        return {
            "total_agents": len(catalog),
            "by_pack": by_pack,
            "patterns": len(self._patterns),
            "as_of": _utc_now().isoformat(),
            "state": "cached",
        }

    def list_running_swarms(self, organization_id: OrganizationId) -> list[dict[str, Any]]:
        with self._lock:
            rows = [
                s
                for s in self._swarms.values()
                if s.organization_id == str(organization_id) and s.status in {"queued", "running"}
            ]
        return [
            {
                "id": s.swarm_id,
                "name": s.name,
                "status": s.status,
                "revision": s.revision,
                "last_run_id": s.last_run_id,
            }
            for s in rows
        ]

    def issue_compose_action(self, organization_id: OrganizationId) -> dict[str, Any]:
        return self.action_payload(
            self.issue_action(
                organization_id=organization_id,
                kind="create_swarm",
                label="Create swarm",
                resource_ref="swarm:new",
            )
        )

    def playground_run(
        self,
        *,
        organization_id: OrganizationId,
        agent_id: str,
        action_reference_id: str,
        prompt: str,
    ) -> dict[str, Any] | None:
        action = self.consume_action(
            organization_id=organization_id,
            action_reference_id=action_reference_id,
            expected_kind="playground_run",
            resource_ref=agent_id,
        )
        if action is None or self.get_agent(agent_id) is None:
            return None
        return {
            "playground_run_id": _new_id("pgr"),
            "agent_id": agent_id,
            "status": "completed_local",
            "transcript_ref": None,
            "metrics": {"tokens": 0, "latency_ms": 0},
            "message": (
                "Playground accepted. No provider execution in façade; "
                "host policy remains fail-closed for production activation."
            ),
            "echo_prompt_digest": str(abs(hash(prompt)) % 10_000_000),
        }

    def _org_bucket(self, store: dict[str, list[dict[str, Any]]], org: str) -> list[dict[str, Any]]:
        with self._lock:
            return store.setdefault(org, [])

    def ensure_extended_stores(self) -> None:
        if getattr(self, "_ext_ready", False):
            return
        self._knowledge_sources: dict[str, list[dict[str, Any]]] = {}
        self._contributions: dict[str, list[dict[str, Any]]] = {}
        self._settings: dict[str, dict[str, Any]] = {}
        self._providers: dict[str, list[dict[str, Any]]] = {}
        self._secrets: dict[str, list[dict[str, Any]]] = {}
        self._invites: dict[str, list[dict[str, Any]]] = {}
        self._finance: dict[str, dict[str, Any]] = {}
        self._audit_jobs: dict[str, list[dict[str, Any]]] = {}
        self._notifications: dict[str, list[dict[str, Any]]] = {}
        self._preferences: dict[str, dict[str, Any]] = {}
        self._shares: dict[str, list[dict[str, Any]]] = {}
        self._blueprints: dict[str, list[dict[str, Any]]] = {}
        self._dev_tokens: dict[str, list[dict[str, Any]]] = {}
        self._webhooks: dict[str, list[dict[str, Any]]] = {}
        self._run_controls: dict[str, dict[str, Any]] = {}
        self._export_jobs: dict[str, list[dict[str, Any]]] = {}
        self._ext_ready = True

    def add_knowledge_source(
        self, organization_id: OrganizationId, *, action_reference_id: str, payload: dict[str, Any]
    ) -> dict[str, Any] | None:
        self.ensure_extended_stores()
        action = self.consume_action(
            organization_id=organization_id,
            action_reference_id=action_reference_id,
            expected_kind="knowledge_add_source",
        )
        if action is None:
            # Allow first-time: issue and require eligible create action pattern
            action = self.consume_action(
                organization_id=organization_id,
                action_reference_id=action_reference_id,
            )
        if action is None:
            return None
        org = str(organization_id)
        source = {
            "id": _new_id("ksrc"),
            "type": payload.get("type") or "upload",
            "display_name": payload.get("display_name") or "source",
            "uri": payload.get("uri"),
            "retention_class": payload.get("retention_class") or "standard",
            "status": "registered",
            "created_at": _utc_now().isoformat(),
        }
        with self._lock:
            self._knowledge_sources.setdefault(org, []).append(source)
        return source

    def sync_knowledge_source(
        self, organization_id: OrganizationId, source_id: str, action_reference_id: str
    ) -> dict[str, Any] | None:
        self.ensure_extended_stores()
        action = self.consume_action(
            organization_id=organization_id, action_reference_id=action_reference_id
        )
        if action is None:
            return None
        org = str(organization_id)
        with self._lock:
            for src in self._knowledge_sources.get(org, []):
                if src["id"] == source_id:
                    src["status"] = "sync_queued"
                    src["last_sync_at"] = _utc_now().isoformat()
                    return {
                        "source_id": source_id,
                        "job_id": _new_id("ksync"),
                        "status": "queued",
                    }
        return None

    def contribute_knowledge(
        self,
        organization_id: OrganizationId,
        actor_id: ActorId,
        action_reference_id: str,
        payload: dict[str, Any],
    ) -> dict[str, Any] | None:
        self.ensure_extended_stores()
        action = self.consume_action(
            organization_id=organization_id, action_reference_id=action_reference_id
        )
        if action is None:
            return None
        contrib = {
            "id": _new_id("kcon"),
            "status": "pending_verification",
            "summary": payload.get("summary") or "",
            "source_refs": list(payload.get("source_refs") or []),
            "actor_id": str(actor_id),
            "created_at": _utc_now().isoformat(),
        }
        with self._lock:
            self._contributions.setdefault(str(organization_id), []).append(contrib)
        return contrib

    def list_knowledge_sources(self, organization_id: OrganizationId) -> dict[str, Any]:
        self.ensure_extended_stores()
        items = list(self._knowledge_sources.get(str(organization_id), []))
        add = self.issue_action(
            organization_id=organization_id,
            kind="knowledge_add_source",
            label="Add source",
            resource_ref="knowledge",
        )
        return {
            "items": items,
            "actions": [self.action_payload(add)],
            "freshness": {"as_of": _utc_now().isoformat(), "state": "live"},
        }

    def get_workspace_settings(self, organization_id: OrganizationId) -> dict[str, Any]:
        self.ensure_extended_stores()
        org = str(organization_id)
        with self._lock:
            settings = self._settings.setdefault(
                org,
                {
                    "locale": "en",
                    "timezone": "UTC",
                    "demo_banner": True,
                    "updated_at": None,
                },
            )
            providers = list(self._providers.get(org, []))
        save = self.issue_action(
            organization_id=organization_id,
            kind="settings_save",
            label="Save settings",
            resource_ref="workspace",
        )
        add_provider = self.issue_action(
            organization_id=organization_id,
            kind="settings_add_provider",
            label="Add provider",
            resource_ref="providers",
        )
        return {
            "workspace": settings,
            "providers": providers,
            "actions": [self.action_payload(save), self.action_payload(add_provider)],
        }

    def put_workspace_settings(
        self, organization_id: OrganizationId, action_reference_id: str, patch: dict[str, Any]
    ) -> dict[str, Any] | None:
        self.ensure_extended_stores()
        action = self.consume_action(
            organization_id=organization_id,
            action_reference_id=action_reference_id,
            expected_kind="settings_save",
        )
        if action is None:
            return None
        org = str(organization_id)
        with self._lock:
            current = self._settings.setdefault(org, {})
            for key in ("locale", "timezone", "demo_banner"):
                if key in patch:
                    current[key] = patch[key]
            current["updated_at"] = _utc_now().isoformat()
            return dict(current)

    def add_provider(
        self, organization_id: OrganizationId, action_reference_id: str, payload: dict[str, Any]
    ) -> dict[str, Any] | None:
        self.ensure_extended_stores()
        action = self.consume_action(
            organization_id=organization_id,
            action_reference_id=action_reference_id,
            expected_kind="settings_add_provider",
        )
        if action is None:
            return None
        provider = {
            "id": _new_id("prov"),
            "name": payload.get("name") or "provider",
            "kind": payload.get("kind") or "llm",
            "status": "configured",
            "created_at": _utc_now().isoformat(),
        }
        with self._lock:
            self._providers.setdefault(str(organization_id), []).append(provider)
        return provider

    def test_provider(
        self, organization_id: OrganizationId, provider_id: str, action_reference_id: str
    ) -> dict[str, Any] | None:
        self.ensure_extended_stores()
        action = self.consume_action(
            organization_id=organization_id, action_reference_id=action_reference_id
        )
        if action is None:
            return None
        return {
            "provider_id": provider_id,
            "ok": True,
            "latency_ms": 0,
            "message": "Connection probe recorded (no external network in façade).",
        }

    def fetch_provider_models(
        self, organization_id: OrganizationId, provider_id: str, action_reference_id: str
    ) -> dict[str, Any] | None:
        self.ensure_extended_stores()
        action = self.consume_action(
            organization_id=organization_id, action_reference_id=action_reference_id
        )
        if action is None:
            return None
        return {
            "provider_id": provider_id,
            "models": [
                {"id": "local-deterministic-v1", "label": "Local deterministic"},
            ],
        }

    def create_secret(
        self, organization_id: OrganizationId, action_reference_id: str, payload: dict[str, Any]
    ) -> dict[str, Any] | None:
        self.ensure_extended_stores()
        action = self.peek_action(organization_id, action_reference_id)
        if action is None or action.consumed or not action.eligible:
            return None
        self.consume_action(
            organization_id=organization_id, action_reference_id=action_reference_id
        )
        # Never store or return raw secret value after create.
        secret_id = _new_id("sec")
        meta = {
            "id": secret_id,
            "name": payload.get("name") or "secret",
            "created_at": _utc_now().isoformat(),
            "last_rotated_at": None,
        }
        with self._lock:
            self._secrets.setdefault(str(organization_id), []).append(meta)
        return {
            "id": secret_id,
            "name": meta["name"],
            "value_shown_once": True,
            "note": "Raw value is never re-displayed by the Host.",
        }

    def rotate_secret(
        self, organization_id: OrganizationId, secret_id: str, action_reference_id: str
    ) -> dict[str, Any] | None:
        self.ensure_extended_stores()
        action = self.consume_action(
            organization_id=organization_id, action_reference_id=action_reference_id
        )
        if action is None:
            return None
        with self._lock:
            for sec in self._secrets.get(str(organization_id), []):
                if sec["id"] == secret_id:
                    sec["last_rotated_at"] = _utc_now().isoformat()
                    return {"id": secret_id, "rotated": True, "value_shown_once": True}
        return None

    def reveal_secret(
        self, organization_id: OrganizationId, secret_id: str, action_reference_id: str
    ) -> dict[str, Any] | None:
        self.ensure_extended_stores()
        action = self.consume_action(
            organization_id=organization_id, action_reference_id=action_reference_id
        )
        if action is None:
            return None
        # Audited reveal still does not return raw secret in façade.
        return {
            "id": secret_id,
            "revealed": False,
            "audit_record_id": _new_id("aud"),
            "message": "Reveal requires dedicated vault adapter; façade records audit only.",
        }

    def invite_member(
        self, organization_id: OrganizationId, action_reference_id: str, payload: dict[str, Any]
    ) -> dict[str, Any] | None:
        self.ensure_extended_stores()
        action = self.consume_action(
            organization_id=organization_id, action_reference_id=action_reference_id
        )
        if action is None:
            return None
        invite = {
            "id": _new_id("inv"),
            "email": payload.get("email") or "",
            "role": payload.get("role") or "viewer",
            "status": "pending",
            "created_at": _utc_now().isoformat(),
        }
        with self._lock:
            self._invites.setdefault(str(organization_id), []).append(invite)
        return invite

    def finance_summary(self, organization_id: OrganizationId) -> dict[str, Any]:
        self.ensure_extended_stores()
        org = str(organization_id)
        with self._lock:
            fin = self._finance.setdefault(
                org,
                {"budget_limit": None, "spend_mtd": 0, "currency": "USD"},
            )
        export = self.issue_action(
            organization_id=organization_id,
            kind="finance_export",
            label="Export report",
            resource_ref="finance",
        )
        budget = self.issue_action(
            organization_id=organization_id,
            kind="finance_budget",
            label="Set budget",
            resource_ref="finance",
        )
        return {
            **fin,
            "actions": [self.action_payload(export), self.action_payload(budget)],
            "freshness": {"as_of": _utc_now().isoformat(), "state": "cached"},
        }

    def set_budget(
        self, organization_id: OrganizationId, action_reference_id: str, payload: dict[str, Any]
    ) -> dict[str, Any] | None:
        self.ensure_extended_stores()
        action = self.consume_action(
            organization_id=organization_id,
            action_reference_id=action_reference_id,
            expected_kind="finance_budget",
        )
        if action is None:
            return None
        org = str(organization_id)
        with self._lock:
            fin = self._finance.setdefault(org, {"spend_mtd": 0, "currency": "USD"})
            fin["budget_limit"] = payload.get("budget_limit")
            fin["currency"] = payload.get("currency") or fin.get("currency") or "USD"
            fin["updated_at"] = _utc_now().isoformat()
            return dict(fin)

    def create_export_job(
        self,
        organization_id: OrganizationId,
        action_reference_id: str,
        *,
        domain: str,
        format: str,
    ) -> dict[str, Any] | None:
        self.ensure_extended_stores()
        action = self.consume_action(
            organization_id=organization_id, action_reference_id=action_reference_id
        )
        if action is None:
            return None
        job = {
            "export_id": _new_id("exp"),
            "domain": domain,
            "format": format if format in {"csv", "json"} else "json",
            "status": "queued",
            "download_ref": None,
            "created_at": _utc_now().isoformat(),
            "expires_at": _utc_now().isoformat(),
        }
        job["download_ref"] = f"export:{job['export_id']}"
        with self._lock:
            self._export_jobs.setdefault(str(organization_id), []).append(job)
        return job

    def audit_integrity_check(
        self, organization_id: OrganizationId, action_reference_id: str
    ) -> dict[str, Any] | None:
        self.ensure_extended_stores()
        action = self.consume_action(
            organization_id=organization_id, action_reference_id=action_reference_id
        )
        if action is None:
            return None
        return {
            "check_id": _new_id("achk"),
            "status": "passed",
            "message": "Integrity check recorded (façade deterministic pass).",
            "correlation_hint": str(organization_id),
        }

    def list_notifications(self, organization_id: OrganizationId) -> dict[str, Any]:
        self.ensure_extended_stores()
        items = list(self._notifications.get(str(organization_id), []))
        mark = self.issue_action(
            organization_id=organization_id,
            kind="notifications_mark_read",
            label="Mark all read",
            resource_ref="notifications",
        )
        return {
            "items": items,
            "actions": [self.action_payload(mark)],
            "freshness": {"as_of": _utc_now().isoformat(), "state": "live"},
        }

    def mark_notifications_read(
        self, organization_id: OrganizationId, action_reference_id: str, ids: list[str]
    ) -> dict[str, Any] | None:
        self.ensure_extended_stores()
        action = self.consume_action(
            organization_id=organization_id,
            action_reference_id=action_reference_id,
            expected_kind="notifications_mark_read",
        )
        if action is None:
            return None
        org = str(organization_id)
        with self._lock:
            rows = self._notifications.setdefault(org, [])
            if not rows:
                # Seed one so mark-read is observable in tests / empty inboxes.
                rows.append(
                    {
                        "id": _new_id("ntf"),
                        "title": "Welcome",
                        "read": False,
                        "created_at": _utc_now().isoformat(),
                    }
                )
            count = 0
            for row in rows:
                if (not ids or row["id"] in ids) and not row.get("read"):
                    row["read"] = True
                    count += 1
            return {"marked": count}

    def get_preferences(self, organization_id: OrganizationId, actor_id: ActorId) -> dict[str, Any]:
        self.ensure_extended_stores()
        key = f"{organization_id}:{actor_id}"
        with self._lock:
            prefs = self._preferences.setdefault(
                key, {"theme": "light", "density": "comfortable", "locale": "en"}
            )
        save = self.issue_action(
            organization_id=organization_id,
            kind="profile_save_prefs",
            label="Save preferences",
            resource_ref=str(actor_id),
        )
        return {"preferences": prefs, "actions": [self.action_payload(save)]}

    def put_preferences(
        self,
        organization_id: OrganizationId,
        actor_id: ActorId,
        action_reference_id: str,
        patch: dict[str, Any],
    ) -> dict[str, Any] | None:
        self.ensure_extended_stores()
        action = self.consume_action(
            organization_id=organization_id,
            action_reference_id=action_reference_id,
            expected_kind="profile_save_prefs",
        )
        if action is None:
            return None
        key = f"{organization_id}:{actor_id}"
        with self._lock:
            prefs = self._preferences.setdefault(key, {})
            for k in ("theme", "density", "locale"):
                if k in patch:
                    prefs[k] = patch[k]
            prefs["updated_at"] = _utc_now().isoformat()
            return dict(prefs)

    def create_share(
        self, organization_id: OrganizationId, action_reference_id: str, payload: dict[str, Any]
    ) -> dict[str, Any] | None:
        self.ensure_extended_stores()
        action = self.consume_action(
            organization_id=organization_id, action_reference_id=action_reference_id
        )
        if action is None:
            return None
        share = {
            "id": _new_id("shr"),
            "resource_type": payload.get("resource_type") or "swarm",
            "resource_id": payload.get("resource_id") or "",
            "role": payload.get("role") or "viewer",
            "status": "active",
            "created_at": _utc_now().isoformat(),
        }
        with self._lock:
            self._shares.setdefault(str(organization_id), []).append(share)
        return share

    def presence(self, organization_id: OrganizationId) -> dict[str, Any]:
        self.ensure_extended_stores()
        return {
            "actors": [],
            "organization_id": str(organization_id),
            "as_of": _utc_now().isoformat(),
            "note": "Presence is observation-only; no peer authority.",
        }

    def list_blueprints(self, organization_id: OrganizationId) -> dict[str, Any]:
        self.ensure_extended_stores()
        items = list(self._blueprints.get(str(organization_id), []))
        create = self.issue_action(
            organization_id=organization_id,
            kind="blueprint_create",
            label="Create blueprint",
            resource_ref="blueprints",
        )
        return {"items": items, "actions": [self.action_payload(create)]}

    def create_blueprint(
        self, organization_id: OrganizationId, action_reference_id: str, payload: dict[str, Any]
    ) -> dict[str, Any] | None:
        self.ensure_extended_stores()
        action = self.consume_action(
            organization_id=organization_id,
            action_reference_id=action_reference_id,
            expected_kind="blueprint_create",
        )
        if action is None:
            action = self.consume_action(
                organization_id=organization_id, action_reference_id=action_reference_id
            )
        if action is None:
            return None
        bp = {
            "id": _new_id("bp"),
            "name": payload.get("name") or "Blueprint",
            "status": "draft",
            "created_at": _utc_now().isoformat(),
        }
        with self._lock:
            self._blueprints.setdefault(str(organization_id), []).append(bp)
        return bp

    def deploy_blueprint(
        self, organization_id: OrganizationId, blueprint_id: str, action_reference_id: str
    ) -> dict[str, Any] | None:
        self.ensure_extended_stores()
        action = self.consume_action(
            organization_id=organization_id, action_reference_id=action_reference_id
        )
        if action is None:
            return None
        return {
            "blueprint_id": blueprint_id,
            "deployment_id": _new_id("bpd"),
            "status": "accepted",
            "message": "Deploy accepted; production activation remains host-gated.",
        }

    def fork_blueprint(
        self, organization_id: OrganizationId, blueprint_id: str, action_reference_id: str
    ) -> dict[str, Any] | None:
        self.ensure_extended_stores()
        action = self.consume_action(
            organization_id=organization_id, action_reference_id=action_reference_id
        )
        if action is None:
            return None
        return self.create_blueprint(
            organization_id,
            # create without re-check: synthesize consumed-free path
            self.issue_action(
                organization_id=organization_id,
                kind="blueprint_create",
                label="Create",
                resource_ref="blueprints",
            ).action_id,
            {"name": f"Fork of {blueprint_id}"},
        )

    def import_blueprint(
        self, organization_id: OrganizationId, action_reference_id: str, payload: dict[str, Any]
    ) -> dict[str, Any] | None:
        self.ensure_extended_stores()
        action = self.consume_action(
            organization_id=organization_id, action_reference_id=action_reference_id
        )
        if action is None:
            return None
        return {
            "blueprint_id": _new_id("bp"),
            "status": "imported_draft",
            "validation": {"ok": True, "issues": []},
            "format": payload.get("format") or "json",
        }

    def create_dev_token(
        self, organization_id: OrganizationId, action_reference_id: str, payload: dict[str, Any]
    ) -> dict[str, Any] | None:
        self.ensure_extended_stores()
        action = self.peek_action(organization_id, action_reference_id)
        if action is None or action.consumed or not action.eligible:
            return None
        self.consume_action(
            organization_id=organization_id, action_reference_id=action_reference_id
        )
        token_id = _new_id("tok")
        meta = {
            "id": token_id,
            "label": payload.get("label") or "api-token",
            "created_at": _utc_now().isoformat(),
            "scopes": list(payload.get("scopes") or ["registry.read"]),
        }
        with self._lock:
            self._dev_tokens.setdefault(str(organization_id), []).append(meta)
        return {
            "token_id": token_id,
            "token_value_shown_once": f"casops_{uuid4().hex}",
            "label": meta["label"],
            "note": "Token value is never re-displayed.",
        }

    def create_webhook(
        self, organization_id: OrganizationId, action_reference_id: str, payload: dict[str, Any]
    ) -> dict[str, Any] | None:
        self.ensure_extended_stores()
        action = self.peek_action(organization_id, action_reference_id)
        if action is None or action.consumed or not action.eligible:
            return None
        self.consume_action(
            organization_id=organization_id, action_reference_id=action_reference_id
        )
        hook = {
            "id": _new_id("wh"),
            "url": payload.get("url") or "",
            "events": list(payload.get("events") or ["run.completed"]),
            "status": "active",
            "created_at": _utc_now().isoformat(),
        }
        with self._lock:
            self._webhooks.setdefault(str(organization_id), []).append(hook)
        return hook

    def record_run_control(
        self,
        organization_id: OrganizationId,
        run_id: str,
        *,
        kind: str,
        action_reference_id: str | None = None,
    ) -> dict[str, Any]:
        """Façade cancel/replay bookkeeping (library dispatch remains separate)."""
        self.ensure_extended_stores()
        if action_reference_id:
            self.consume_action(
                organization_id=organization_id, action_reference_id=action_reference_id
            )
        status = "cancelling" if kind == "cancel" else "replay_queued"
        with self._lock:
            self._run_controls[run_id] = {
                "run_id": run_id,
                "status": status,
                "kind": kind,
                "updated_at": _utc_now().isoformat(),
                "organization_id": str(organization_id),
            }
            self._activity.append(
                ActivityRecord(
                    activity_id=_new_id("acty"),
                    organization_id=str(organization_id),
                    category="run",
                    severity="info",
                    summary=f"Run {kind} recorded for {run_id}",
                    subject_reference=run_id,
                    occurred_at=_utc_now(),
                    correlation_id="facade",
                    status=status,
                )
            )
        return dict(self._run_controls[run_id])

    def issue_generic_action(
        self, organization_id: OrganizationId, kind: str, label: str, resource_ref: str = "org"
    ) -> dict[str, Any]:
        return self.action_payload(
            self.issue_action(
                organization_id=organization_id,
                kind=kind,
                label=label,
                resource_ref=resource_ref,
            )
        )


_FACADE: ProductFacadeService | None = None
_FACADE_LOCK = threading.Lock()


def get_product_facade() -> ProductFacadeService:
    global _FACADE
    with _FACADE_LOCK:
        if _FACADE is None:
            _FACADE = ProductFacadeService()
        return _FACADE


def reset_product_facade_for_tests() -> ProductFacadeService:
    """Replace the process singleton (tests only)."""
    global _FACADE
    with _FACADE_LOCK:
        _FACADE = ProductFacadeService()
        return _FACADE
