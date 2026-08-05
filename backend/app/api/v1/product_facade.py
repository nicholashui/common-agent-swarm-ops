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

from app.api.v1.product_facade_store import (
    ProductFacadeStore,
    _parse_dt,
    persistence_enabled,
    serialize_activity,
    serialize_swarm,
)
from app.api.v1.video_brief_spine import (
    PHASE_1_AGENT_IDS,
    SPINE_WORKFLOW_ID,
    apply_stub_step,
    build_user_brief,
    decide_package,
    goal_looks_like_video_brief,
    init_spine_state,
    phase1_and_spine_member_ids,
    public_artifact_view,
    public_spine_view,
)
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
    goal_summary: str | None = None
    brief: dict[str, Any] | None = None
    spine: dict[str, Any] | None = None


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

    def __init__(
        self,
        *,
        persist: bool | None = None,
        store: ProductFacadeStore | None = None,
    ) -> None:
        self._lock = threading.RLock()
        self._catalog: tuple[PackAgentCatalogEntry, ...] | None = None
        self._actions: dict[str, ActionRefRecord] = {}
        self._proposals: dict[str, ProposalRecord] = {}
        self._rollouts: dict[str, RolloutRecord] = {}
        self._swarms: dict[str, SwarmRecord] = {}
        self._activity: list[ActivityRecord] = []
        # Package human gates for spine stub runs (durable when persist enabled).
        self._package_approvals: dict[str, dict[str, Any]] = {}
        # In-memory audit mirror (also appended to durable JSONL when enabled).
        self._audit: list[dict[str, Any]] = []
        enabled = persistence_enabled() if persist is None else persist
        self._store: ProductFacadeStore | None = (
            store if store is not None else (ProductFacadeStore() if enabled else None)
        )
        if self._store is not None:
            self._hydrate_from_store()
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

    def _hydrate_from_store(self) -> None:
        assert self._store is not None
        state = self._store.load_state()
        swarms_raw = state.get("swarms") if isinstance(state.get("swarms"), dict) else {}
        for sid, raw in swarms_raw.items():
            if not isinstance(raw, dict):
                continue
            try:
                record = SwarmRecord(
                    swarm_id=str(raw.get("swarm_id") or sid),
                    organization_id=str(raw.get("organization_id") or ""),
                    name=str(raw.get("name") or "Untitled"),
                    revision=int(raw.get("revision") or 0),
                    status=str(raw.get("status") or "draft"),
                    created_at=_parse_dt(raw.get("created_at")),
                    updated_at=_parse_dt(raw.get("updated_at")),
                    pattern_ref=raw.get("pattern_ref"),
                    nodes=list(raw.get("nodes") or []),
                    edges=list(raw.get("edges") or []),
                    policy=dict(raw.get("policy") or {}),
                    members=list(raw.get("members") or []),
                    pins=list(raw.get("pins") or []),
                    last_run_id=raw.get("last_run_id"),
                    goal_summary=raw.get("goal_summary"),
                    brief=raw.get("brief") if isinstance(raw.get("brief"), dict) else None,
                    spine=raw.get("spine") if isinstance(raw.get("spine"), dict) else None,
                )
            except (TypeError, ValueError):
                continue
            self._swarms[record.swarm_id] = record
        approvals = state.get("package_approvals")
        if isinstance(approvals, dict):
            self._package_approvals = {
                str(k): dict(v) for k, v in approvals.items() if isinstance(v, dict)
            }
        activity_raw = state.get("activity")
        if isinstance(activity_raw, list):
            for row in activity_raw:
                if not isinstance(row, dict):
                    continue
                try:
                    self._activity.append(
                        ActivityRecord(
                            activity_id=str(row.get("activity_id") or _new_id("acty")),
                            organization_id=str(row.get("organization_id") or ""),
                            category=str(row.get("category") or "ops"),
                            severity=str(row.get("severity") or "info"),
                            summary=str(row.get("summary") or ""),
                            subject_reference=str(row.get("subject_reference") or ""),
                            occurred_at=_parse_dt(row.get("occurred_at")),
                            correlation_id=str(row.get("correlation_id") or ""),
                            status=str(row.get("status") or "recorded"),
                        )
                    )
                except (TypeError, ValueError):
                    continue

    def _persist_state(self) -> None:
        if self._store is None:
            return
        with self._lock:
            swarms = {sid: serialize_swarm(s) for sid, s in self._swarms.items()}
            activity = [serialize_activity(a) for a in self._activity]
            approvals = dict(self._package_approvals)
        self._store.save_swarms(swarms)
        self._store.save_package_approvals(approvals)
        self._store.save_activity(activity)

    def _append_audit(
        self,
        *,
        organization_id: str,
        kind: str,
        subject_reference: str,
        summary: str,
        correlation_id: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        record = {
            "audit_id": _new_id("aud"),
            "organization_id": organization_id,
            "kind": kind,
            "subject_reference": subject_reference,
            "summary": summary,
            "correlation_id": correlation_id,
            "occurred_at": _utc_now().isoformat(),
            "payload": payload or {},
            "immutable": True,
        }
        with self._lock:
            self._audit.append(record)
            if len(self._audit) > 5000:
                self._audit = self._audit[-4000:]
        if self._store is not None:
            self._store.append_audit(record)
        return record

    def list_product_audit(
        self,
        organization_id: OrganizationId,
        *,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Immutable product audit entries (spine steps, package decisions, materialize)."""
        org = str(organization_id)
        limit = max(1, min(limit, 500))
        if self._store is not None:
            return self._store.list_audit(organization_id=org, limit=limit)
        with self._lock:
            rows = [r for r in self._audit if r.get("organization_id") == org]
        return rows[-limit:]

    def run_member_loops(
        self,
        *,
        organization_id: OrganizationId,
        swarm_id: str,
        action_reference_id: str,
        correlation_id: CorrelationId,
        goal: str | None = None,
        agent_ids: list[str] | None = None,
        stop_on_failure: bool = False,
    ) -> dict[str, Any] | None:
        """Run offline AgentLoopService for swarm members (fleet path seed)."""
        action = self.consume_action(
            organization_id=organization_id,
            action_reference_id=action_reference_id,
            expected_kind="run_member_loops",
            resource_ref=swarm_id,
        )
        if action is None:
            return None
        swarm = self.get_swarm(organization_id, swarm_id)
        if swarm is None:
            return None
        ids = list(agent_ids or [])
        if not ids:
            ids = [
                str(m.get("agent_id"))
                for m in swarm.members
                if isinstance(m, dict) and m.get("agent_id")
            ]
        goal_text = (goal or "").strip() or (swarm.goal_summary or swarm.name or "swarm run")
        if isinstance(swarm.brief, dict) and swarm.brief.get("text"):
            goal_text = str(swarm.brief["text"])

        from app.video.agent_loop_service import get_agent_loop_service

        service = get_agent_loop_service()
        crew = service.run_crew(
            ids,
            organization_id=str(organization_id),
            goal=goal_text,
            correlation_id=str(correlation_id),
            stop_on_failure=stop_on_failure,
        )
        self._append_audit(
            organization_id=str(organization_id),
            kind="member_loops",
            subject_reference=swarm_id,
            summary=(
                f"Member loops completed={crew.get('completed')} "
                f"passed={crew.get('passed')} failed={crew.get('failed')}"
            ),
            correlation_id=str(correlation_id),
            payload={
                "swarm_id": swarm_id,
                "requested": crew.get("requested"),
                "passed": crew.get("passed"),
                "failed": crew.get("failed"),
            },
        )
        self._persist_state()
        return {
            "ok": bool(crew.get("ok")),
            "swarm_id": swarm_id,
            "crew": crew,
            "note": "offline pack loops · not production media · not full concurrent production",
        }

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
            goal_summary=(goal_summary or None),
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
        self._append_audit(
            organization_id=str(organization_id),
            kind="swarm_created",
            subject_reference=record.swarm_id,
            summary=f"Swarm draft created: {record.name}",
            correlation_id=str(correlation_id),
            payload={"swarm_id": record.swarm_id, "name": record.name},
        )
        self._persist_state()
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
        actions = [
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
        if swarm.spine is not None:
            spine_status = str((swarm.spine or {}).get("status") or "")
            if spine_status not in {"waiting_for_approval", "completed", "denied", "failed"}:
                actions.append(
                    self.action_payload(
                        self.issue_action(
                            organization_id=organization_id,
                            kind="run_spine_step",
                            label="Run spine step (stub)",
                            resource_ref=swarm.swarm_id,
                        )
                    )
                )
                actions.append(
                    self.action_payload(
                        self.issue_action(
                            organization_id=organization_id,
                            kind="run_spine_to_package",
                            label="Dry-run spine to package (stub)",
                            resource_ref=swarm.swarm_id,
                        )
                    )
                )
            if spine_status == "waiting_for_approval":
                actions.append(
                    self.action_payload(
                        self.issue_action(
                            organization_id=organization_id,
                            kind="decide_package",
                            label="Decide package gate",
                            resource_ref=swarm.swarm_id,
                        )
                    )
                )
        if swarm.members:
            actions.append(
                self.action_payload(
                    self.issue_action(
                        organization_id=organization_id,
                        kind="run_member_loops",
                        label="Run offline loops for members",
                        resource_ref=swarm.swarm_id,
                    )
                )
            )
        return actions

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

    def list_swarms(self, organization_id: OrganizationId) -> list[dict[str, Any]]:
        """All organization-owned swarms (drafts, queued, running, etc.). In-memory façade only."""
        with self._lock:
            rows = [
                s
                for s in self._swarms.values()
                if s.organization_id == str(organization_id)
            ]
        rows_sorted = sorted(rows, key=lambda s: s.updated_at, reverse=True)
        return [
            {
                "id": s.swarm_id,
                "name": s.name,
                "status": s.status,
                "revision": s.revision,
                "member_count": len(s.members),
                "last_run_id": s.last_run_id,
                "updated_at": s.updated_at.isoformat(),
                "created_at": s.created_at.isoformat(),
                "has_spine": isinstance(s.spine, dict),
                "spine_status": (
                    str(s.spine.get("status"))
                    if isinstance(s.spine, dict)
                    else None
                ),
                "spine_workflow_id": (
                    str(s.spine.get("workflow_id"))
                    if isinstance(s.spine, dict)
                    else None
                ),
                "brief_id": (
                    str(s.brief.get("brief_id"))
                    if isinstance(s.brief, dict)
                    else None
                ),
            }
            for s in rows_sorted
        ]

    def recommend_composition(
        self,
        *,
        organization_id: OrganizationId,
        goal: str,
        max_slots: int = 8,
        human_resolutions: dict[str, str] | None = None,
        brief: dict[str, Any] | None = None,
        correlation_id: str | None = None,
    ) -> dict[str, Any]:
        """AI-pick composition from pack catalog (deterministic, fail-closed, no LLM network).

        Humans supply the goal/spec. Host selects pattern + agent slots.
        Human is required only when AI cannot resolve conflicts (needs_hitl).
        Optional human_resolutions answers open questions from a prior pass.
        Optional brief meta is validated and returned as brief_preview (no mint until materialize).
        """
        text = (goal or "").strip()
        if not text:
            return {
                "ok": False,
                "message": "Goal/spec is required for AI composition.",
            }
        brief_preview: dict[str, Any] | None = None
        if brief is not None or text:
            snap, brief_err = build_user_brief(
                text=text,
                brief_meta=brief,
                correlation_id=correlation_id or "recommend",
                mint_id=False,
            )
            if brief is not None and brief_err:
                return {"ok": False, "message": brief_err}
            if snap is not None and brief_err is None:
                brief_preview = snap
        g = text.lower()
        tokens = [t for t in re.split(r"[^a-z0-9]+", g) if len(t) >= 3]
        resolutions = {str(k): str(v).strip().lower() for k, v in (human_resolutions or {}).items()}

        # --- Conflict / ambiguity detection (HITL only when AI cannot decide) ---
        open_questions: list[dict[str, Any]] = []

        want_cheap = any(
            k in g for k in ("cheap", "lowest cost", "budget", "frugal", "minimal cost", "low cost")
        )
        want_premium = any(
            k in g
            for k in (
                "premium quality",
                "highest quality",
                "max quality",
                "cinematic quality",
                "broadcast quality",
                "no compromise",
            )
        )
        want_fast = any(k in g for k in ("asap", "urgent", "fastest", "realtime", "real-time", "same day"))
        want_thorough = any(
            k in g
            for k in (
                "thorough",
                "exhaustive",
                "deep research",
                "full pipeline",
                "feature film",
                "multi-phase",
            )
        )
        prefer_video = any(
            k in g
            for k in (
                "video",
                "youtube",
                "film",
                "cinematic",
                "shot",
                "script",
                "wuxia",
                "storyboard",
                "director",
                "editor",
            )
        )
        prefer_specials = any(
            k in g for k in ("cobol", "legacy", "software", "code", "devops", "api", "implementation")
        )
        explicit_conflict = any(
            k in g
            for k in (
                "conflict",
                "contradiction",
                "cannot decide",
                "either or",
                "either/or",
                "vs quality",
                "vs cost",
                "trade-off undecided",
                "tradeoff undecided",
            )
        )

        cost_res = resolutions.get("q_cost_quality", "")
        if want_cheap and want_premium and cost_res not in {"prefer_cost", "prefer_quality", "balanced"}:
            open_questions.append(
                {
                    "id": "q_cost_quality",
                    "kind": "requirement_conflict",
                    "severity": "blocker",
                    "question": (
                        "Spec asks for both lowest cost and premium/highest quality. "
                        "Which priority should AI optimize?"
                    ),
                    "options": [
                        {
                            "id": "prefer_cost",
                            "label": "Prefer cost (smaller crew, lighter verification)",
                        },
                        {
                            "id": "prefer_quality",
                            "label": "Prefer quality (heavier verification + specialists)",
                        },
                        {
                            "id": "balanced",
                            "label": "Balanced (default hierarchy with mid-size crew)",
                        },
                    ],
                }
            )
        elif cost_res in {"prefer_cost", "prefer_quality", "balanced"}:
            # Applied below
            pass

        speed_res = resolutions.get("q_speed_depth", "")
        if want_fast and want_thorough and speed_res not in {"prefer_speed", "prefer_depth", "phased"}:
            open_questions.append(
                {
                    "id": "q_speed_depth",
                    "kind": "requirement_conflict",
                    "severity": "blocker",
                    "question": (
                        "Spec asks for both maximum speed and thorough/full-depth work. "
                        "How should AI structure the workflow?"
                    ),
                    "options": [
                        {
                            "id": "prefer_speed",
                            "label": "Prefer speed (parallel, thinner gates)",
                        },
                        {
                            "id": "prefer_depth",
                            "label": "Prefer depth (sequential phases, full gates)",
                        },
                        {
                            "id": "phased",
                            "label": "Phased (fast MVP then depth refinement)",
                        },
                    ],
                }
            )

        domain_res = resolutions.get("q_domain", "")
        if (
            prefer_video
            and prefer_specials
            and domain_res not in {"video", "software", "hybrid"}
        ):
            open_questions.append(
                {
                    "id": "q_domain",
                    "kind": "requirement_conflict",
                    "severity": "blocker",
                    "question": (
                        "Spec mixes video/film signals with software/legacy signals. "
                        "Which domain inventory should AI draw agents from?"
                    ),
                    "options": [
                        {"id": "video", "label": "Video pack agents"},
                        {"id": "software", "label": "Specials / software agents"},
                        {"id": "hybrid", "label": "Hybrid (both packs)"},
                    ],
                }
            )

        if explicit_conflict and not open_questions and not resolutions:
            open_questions.append(
                {
                    "id": "q_explicit_conflict",
                    "kind": "requirement_conflict",
                    "severity": "blocker",
                    "question": (
                        "Spec explicitly flags a conflict or undecided trade-off. "
                        "State the winning constraint for AI to proceed."
                    ),
                    "options": [
                        {"id": "proceed_balanced", "label": "Proceed with balanced AI defaults"},
                        {"id": "pause", "label": "Keep paused — I will rewrite the spec"},
                    ],
                }
            )

        if open_questions:
            return {
                "ok": True,
                "mode": "ai_pick",
                "decision_status": "needs_hitl",
                "auto_materialize": False,
                "goal": text,
                "pattern": None,
                "slots": [],
                "open_questions": open_questions,
                "metrics": {
                    "slot_count": 0,
                    "selection": "blocked_on_human",
                    "production_activation": False,
                },
                "procedure_steps": [
                    "1. Ingest goal/spec.",
                    "2. AI detected requirement conflict(s) it cannot safely resolve.",
                    "3. Human answers only the open questions.",
                    "4. AI re-runs pick and materializes workflow.",
                ],
                "compose_action": self.issue_compose_action(organization_id),
                "brief_preview": brief_preview,
                "note": (
                    "Human input required only for unresolved conflicts. "
                    "AI does not invent a compromised plan without a choice."
                ),
            }

        # Apply human resolutions into scoring biases
        if cost_res == "prefer_cost":
            max_slots = min(max_slots, 5)
        elif cost_res == "prefer_quality":
            max_slots = max(max_slots, 8)
        if domain_res == "video":
            prefer_specials = False
            prefer_video = True
        elif domain_res == "software":
            prefer_video = False
            prefer_specials = True
        # hybrid / empty: leave prefer_* as detected

        # Pattern AI pick (may be steered by speed/depth resolution)
        if speed_res == "prefer_speed" or (
            want_fast and not want_thorough and any(k in g for k in ("parallel", "research", "market"))
        ):
            pattern_id = "parallel-research"
            pattern_why = "AI chose parallel pattern for speed / independent branches."
        elif any(k in g for k in ("verify", "verification", "quality", "critic", "loop", "rubric")) or (
            cost_res == "prefer_quality" or speed_res == "prefer_depth"
        ):
            pattern_id = "verification-loop"
            pattern_why = "AI chose verification loop for quality / depth gates."
        elif any(k in g for k in ("parallel", "research", "market", "intelligence", "multi-branch")):
            pattern_id = "parallel-research"
            pattern_why = "Goal signals independent parallel analysis branches."
        else:
            pattern_id = "hierarchical-supervisor"
            pattern_why = (
                "Default AI pick: Orchestrator→Planner→specialists (supervisor hierarchy)."
            )
        if speed_res == "phased":
            pattern_id = "hierarchical-supervisor"
            pattern_why = "Phased resolution: hierarchical pipeline for MVP then depth."
        if resolutions.get("q_explicit_conflict") == "pause":
            return {
                "ok": True,
                "mode": "ai_pick",
                "decision_status": "needs_hitl",
                "auto_materialize": False,
                "goal": text,
                "pattern": None,
                "slots": [],
                "open_questions": [
                    {
                        "id": "q_explicit_conflict",
                        "kind": "requirement_conflict",
                        "severity": "blocker",
                        "question": "You chose to pause. Rewrite the spec, then re-run AI pick.",
                        "options": [
                            {
                                "id": "proceed_balanced",
                                "label": "Proceed with balanced AI defaults after all",
                            }
                        ],
                    }
                ],
                "metrics": {
                    "slot_count": 0,
                    "selection": "paused_by_human",
                    "production_activation": False,
                },
                "procedure_steps": ["Human paused; awaiting rewritten spec."],
                "compose_action": self.issue_compose_action(organization_id),
                "note": "AI pick paused by human resolution.",
            }

        pattern = next((p for p in self._patterns if p["id"] == pattern_id), self._patterns[0])

        scored: list[tuple[float, PackAgentCatalogEntry]] = []
        for agent in self.catalog():
            hay = " ".join(
                [
                    agent.agent_id,
                    agent.name,
                    agent.role,
                    agent.description,
                    agent.pack,
                ]
            ).lower()
            score = 0.0
            for t in tokens:
                if t in hay:
                    score += 2.0
                if t in agent.agent_id.lower():
                    score += 1.5
            if prefer_video and agent.pack == "video":
                score += 1.0
            if prefer_specials and agent.pack == "specials":
                score += 1.0
            if prefer_video and not prefer_specials and agent.pack == "specials":
                score -= 0.5
            if prefer_specials and not prefer_video and agent.pack == "video":
                score -= 0.5
            if not prefer_specials and agent.pack == "video":
                score += 0.2
            if "orchestrat" in hay:
                score += 0.5
            if "planner" in hay:
                score += 0.5
            if cost_res == "prefer_cost" and any(
                k in hay for k in ("orchestrat", "planner", "editor", "director")
            ):
                score += 0.3
            if cost_res == "prefer_quality" and any(
                k in hay for k in ("judge", "gate", "qa", "compliance", "critic")
            ):
                score += 0.8
            if score > 0:
                scored.append((score, agent))
        scored.sort(key=lambda row: (-row[0], row[1].agent_id))

        core_ids: list[str] = []
        # Epic B: video briefs bind Phase-1 + spine-capable crew (closed world).
        video_brief = prefer_video or goal_looks_like_video_brief(text)
        if video_brief:
            for cid in phase1_and_spine_member_ids(
                prefer_video=True, max_slots=max_slots
            ):
                if self.get_agent(cid) is not None and cid not in core_ids:
                    core_ids.append(cid)
            pattern_id = "hierarchical-supervisor"
            pattern = next(
                (p for p in self._patterns if p["id"] == pattern_id), self._patterns[0]
            )
            pattern_why = (
                "AI chose Phase-1 Intent & Planning crew + video spine-capable members "
                f"(workflow {SPINE_WORKFLOW_ID}, stub-only)."
            )
        elif pattern_id == "hierarchical-supervisor":
            for cid in ("video.orchestrator", "video.planner", "video.producer"):
                if self.get_agent(cid) is not None:
                    core_ids.append(cid)
        if not video_brief and (
            pattern_id == "verification-loop" or cost_res == "prefer_quality"
        ):
            for cid in ("video.judge", "video.gatekeeper", "video.aiqaconsistency"):
                if self.get_agent(cid) is not None and cid not in core_ids:
                    core_ids.append(cid)
                    break

        picked: list[str] = list(core_ids)
        for _score, agent in scored:
            if agent.agent_id in picked:
                continue
            if video_brief and agent.pack != "video":
                continue
            picked.append(agent.agent_id)
            if len(picked) >= max(3, min(max_slots, 10)):
                break

        if len(picked) < 3:
            for fallback in (
                "video.orchestrator",
                "video.planner",
                "video.producer",
                "video.director",
                "video.screenwriter",
            ):
                if fallback not in picked and self.get_agent(fallback) is not None:
                    picked.append(fallback)
                if len(picked) >= 4:
                    break

        slots: list[dict[str, Any]] = []
        phase1_set = set(PHASE_1_AGENT_IDS)
        for idx, agent_id in enumerate(picked):
            entry = self.get_agent(agent_id)
            if entry is None:
                continue
            is_verify = any(
                k in agent_id for k in ("judge", "gate", "qa", "compliance", "verifier")
            )
            if agent_id in phase1_set:
                rationale = "Phase-1 Intent & Planning crew (closed-world template)."
            elif video_brief:
                rationale = f"Spine-capable agent for {SPINE_WORKFLOW_ID} stub dry-run."
            else:
                rationale = "AI-selected from pack catalog for goal match."
            slots.append(
                {
                    "id": f"slot_{idx}",
                    "agent_id": agent_id,
                    "label": entry.name,
                    "role": entry.role,
                    "version": entry.version_label,
                    "pack": entry.pack,
                    "verified": is_verify,
                    "rationale": rationale,
                    "phase": "intent_planning" if agent_id in phase1_set else None,
                }
            )

        applied = {k: v for k, v in resolutions.items() if v}
        return {
            "ok": True,
            "mode": "ai_pick",
            "decision_status": "ai_resolved",
            "auto_materialize": True,
            "goal": text,
            "pattern": {
                "id": pattern["id"],
                "name": pattern["name"],
                "version_label": pattern.get("version_label", "pattern · 1.0"),
                "when_to_use": pattern.get("when_to_use", ""),
                "rationale": pattern_why,
            },
            "slots": slots,
            "open_questions": [],
            "human_resolutions_applied": applied,
            "metrics": {
                "slot_count": len(slots),
                "selection": "deterministic_catalog_score",
                "production_activation": False,
            },
            "procedure_steps": [
                "1. Ingest goal/spec (human only when conflicts).",
                "2. AI select pattern from Host registry.",
                "3. AI score available pack agents (closed world).",
                "4. Emit workflow slots (Planner-like).",
                "5. Auto-materialize draft when decision_status=ai_resolved.",
                "6. Open Canvas for inspection (fail-closed run).",
            ],
            "compose_action": self.issue_compose_action(organization_id),
            "brief_preview": brief_preview,
            "note": (
                "AI-pick mainly. Human only for needs_hitl conflicts. "
                "Host-deterministic ranking; no production activation."
            ),
        }

    def materialize_ai_composition(
        self,
        *,
        organization_id: OrganizationId,
        actor_id: ActorId,
        correlation_id: CorrelationId,
        goal: str,
        swarm_name: str | None = None,
        max_slots: int = 8,
        human_resolutions: dict[str, str] | None = None,
        brief: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        """AI recommend + create draft + attach AI-picked members.

        Returns needs_hitl payload (no swarm) when AI cannot resolve conflicts.
        Attaches UserBriefV1 + spine stub state for video briefs (Epic A–C).
        """
        brief_snapshot, brief_err = build_user_brief(
            text=goal,
            brief_meta=brief,
            correlation_id=str(correlation_id),
        )
        if brief_err:
            return {
                "ok": False,
                "decision_status": "validation_failed",
                "message": brief_err,
                "swarm_id": None,
                "canvas_path": None,
            }
        assert brief_snapshot is not None

        rec = self.recommend_composition(
            organization_id=organization_id,
            goal=goal,
            max_slots=max_slots,
            human_resolutions=human_resolutions,
        )
        if not rec.get("ok"):
            return None
        if rec.get("decision_status") == "needs_hitl":
            return {
                "decision_status": "needs_hitl",
                "auto_materialize": False,
                "recommendation": rec,
                "swarm_id": None,
                "canvas_path": None,
                "message": "Human resolution required before AI can materialize a workflow.",
            }
        pattern_id = str(rec["pattern"]["id"])
        name = (swarm_name or "").strip() or f"AI · {rec['pattern']['name']}"
        if len(name) > 200:
            name = name[:200]
        action_id = self.issue_compose_action(organization_id)["id"]
        swarm = self.create_swarm(
            organization_id=organization_id,
            actor_id=actor_id,
            correlation_id=correlation_id,
            name=name,
            action_reference_id=action_id,
            pattern_ref=pattern_id,
            goal_summary=goal[:2000],
            initial_graph=None,
        )
        if swarm is None:
            return None
        # Attach brief + spine (video path always when goal looks like production brief)
        attach_spine = goal_looks_like_video_brief(goal) or any(
            str(s.get("agent_id", "")).startswith("video.") for s in rec.get("slots") or []
        )
        with self._lock:
            record = self._swarms.get(swarm.swarm_id)
            if record is not None:
                record.brief = brief_snapshot
                record.goal_summary = goal[:2000]
                if attach_spine:
                    record.spine = init_spine_state(brief_id=str(brief_snapshot["brief_id"]))
                record.updated_at = _utc_now()

        added: list[dict[str, Any]] = []
        for slot in rec["slots"]:
            agent_id = str(slot["agent_id"])
            add_action = self.issue_action(
                organization_id=organization_id,
                kind="add_to_swarm",
                label="Add to Swarm",
                resource_ref=agent_id,
                eligible=True,
            )
            member = self.add_member(
                organization_id=organization_id,
                swarm_id=swarm.swarm_id,
                action_reference_id=add_action.action_id,
                agent_id=agent_id,
                agent_version="current",
                pin_policy="exact",
            )
            if member is not None:
                added.append(member)
        fresh = self.get_swarm(organization_id, swarm.swarm_id)
        assert fresh is not None
        spine_view = public_spine_view(fresh.spine)
        self._append_audit(
            organization_id=str(organization_id),
            kind="composition_materialized",
            subject_reference=fresh.swarm_id,
            summary=(
                f"Materialized draft {fresh.name} with brief "
                f"{brief_snapshot['brief_id']} · members {len(fresh.members)}"
            ),
            correlation_id=str(correlation_id),
            payload={
                "swarm_id": fresh.swarm_id,
                "brief_id": brief_snapshot["brief_id"],
                "member_count": len(fresh.members),
                "spine_workflow_id": SPINE_WORKFLOW_ID if spine_view else None,
            },
        )
        self._persist_state()
        return {
            "decision_status": "ai_resolved",
            "auto_materialize": True,
            "swarm_id": fresh.swarm_id,
            "name": fresh.name,
            "revision": fresh.revision,
            "status": fresh.status,
            "pattern_ref": fresh.pattern_ref,
            "member_count": len(fresh.members),
            "members_added": len(added),
            "recommendation": rec,
            "canvas_path": f"/swarms/{fresh.swarm_id}/canvas",
            "brief_id": brief_snapshot["brief_id"],
            "brief": brief_snapshot,
            "spine_workflow_id": SPINE_WORKFLOW_ID if spine_view else None,
            "spine": spine_view,
        }

    def run_spine_step(
        self,
        *,
        organization_id: OrganizationId,
        swarm_id: str,
        action_reference_id: str,
        correlation_id: CorrelationId,
        step_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any] | None:
        """Advance one video spine stub step (fail-closed without action ref)."""
        action = self.consume_action(
            organization_id=organization_id,
            action_reference_id=action_reference_id,
            expected_kind="run_spine_step",
            resource_ref=swarm_id,
        )
        if action is None:
            return None
        with self._lock:
            swarm = self._swarms.get(swarm_id)
            if swarm is None or swarm.organization_id != str(organization_id):
                return None
            if not isinstance(swarm.spine, dict):
                return {
                    "ok": False,
                    "message": "Swarm has no spine attached. Materialize a video brief first.",
                }
            brief_text = ""
            if isinstance(swarm.brief, dict):
                brief_text = str(swarm.brief.get("text") or "")
            if not brief_text:
                brief_text = swarm.goal_summary or swarm.name
            updated, err = apply_stub_step(
                swarm.spine,
                step_id=step_id,
                brief_text=brief_text,
                idempotency_key=idempotency_key,
            )
            if err:
                return {"ok": False, "message": err, "spine": public_spine_view(swarm.spine)}
            assert updated is not None
            swarm.updated_at = _utc_now()
            # Register package approval when gate opens
            approval_id = swarm.spine.get("approval_id")
            if (
                str(swarm.spine.get("status")) == "waiting_for_approval"
                and approval_id
                and approval_id not in self._package_approvals
            ):
                self._package_approvals[str(approval_id)] = {
                    "approval_id": str(approval_id),
                    "organization_id": str(organization_id),
                    "swarm_id": swarm_id,
                    "run_id": swarm.last_run_id or f"spine:{swarm_id}",
                    "risk_tier": "tier_3_package_gate",
                    "gate_status": "paused",
                    "kind": "video_package",
                    "summary": f"Package gate for swarm {swarm.name} (stub · not production media)",
                    "created_at": _utc_now().isoformat(),
                    "correlation_id": str(correlation_id),
                    "decision": None,
                }
                self._activity.append(
                    ActivityRecord(
                        activity_id=_new_id("acty"),
                        organization_id=str(organization_id),
                        category="approval",
                        severity="warning",
                        summary=f"Package human gate opened for {swarm.name}",
                        subject_reference=str(approval_id),
                        occurred_at=_utc_now(),
                        correlation_id=str(correlation_id),
                        status="waiting_for_approval",
                    )
                )
            else:
                step_done = step_id or "next"
                self._activity.append(
                    ActivityRecord(
                        activity_id=_new_id("acty"),
                        organization_id=str(organization_id),
                        category="spine",
                        severity="info",
                        summary=f"Spine stub step advanced ({step_done}) on {swarm.name}",
                        subject_reference=swarm_id,
                        occurred_at=_utc_now(),
                        correlation_id=str(correlation_id),
                        status=str(swarm.spine.get("status") or "running"),
                    )
                )
            view = public_spine_view(swarm.spine)
            self._append_audit(
                organization_id=str(organization_id),
                kind="spine_step",
                subject_reference=swarm_id,
                summary=f"Spine stub step advanced on {swarm.name}",
                correlation_id=str(correlation_id),
                payload={
                    "swarm_id": swarm_id,
                    "spine_status": (view or {}).get("status"),
                    "approval_id": (view or {}).get("approval_id"),
                    "step_id": step_id,
                    "idempotency_key": idempotency_key,
                },
            )
            self._persist_state()
            return {
                "ok": True,
                "swarm_id": swarm_id,
                "spine": view,
                "approval_id": (view or {}).get("approval_id"),
                "note": "stub run · not production media",
            }

    def decide_package_gate(
        self,
        *,
        organization_id: OrganizationId,
        swarm_id: str,
        action_reference_id: str,
        correlation_id: CorrelationId,
        decision: str,
        reason: str,
    ) -> dict[str, Any] | None:
        """Human approve/deny package step; fail-closed, idempotent once decided."""
        action = self.consume_action(
            organization_id=organization_id,
            action_reference_id=action_reference_id,
            expected_kind="decide_package",
            resource_ref=swarm_id,
        )
        if action is None:
            return None
        with self._lock:
            swarm = self._swarms.get(swarm_id)
            if swarm is None or swarm.organization_id != str(organization_id):
                return None
            if not isinstance(swarm.spine, dict):
                return {"ok": False, "message": "Swarm has no spine."}
            # Already decided — idempotent return
            if swarm.spine.get("package_decision"):
                return {
                    "ok": True,
                    "idempotent": True,
                    "swarm_id": swarm_id,
                    "spine": public_spine_view(swarm.spine),
                    "approval_id": swarm.spine.get("approval_id"),
                }
            updated, err = decide_package(swarm.spine, decision=decision, reason=reason)
            if err:
                return {"ok": False, "message": err, "spine": public_spine_view(swarm.spine)}
            assert updated is not None
            swarm.updated_at = _utc_now()
            approval_id = str(swarm.spine.get("approval_id") or "")
            if approval_id and approval_id in self._package_approvals:
                rec = self._package_approvals[approval_id]
                rec["gate_status"] = (
                    "resumed" if decision.strip().lower() == "approved" else "denied"
                )
                rec["decision"] = {
                    "value": decision.strip().lower(),
                    "reason": reason.strip(),
                    "decided_at": _utc_now().isoformat(),
                    "correlation_id": str(correlation_id),
                }
            self._activity.append(
                ActivityRecord(
                    activity_id=_new_id("acty"),
                    organization_id=str(organization_id),
                    category="approval",
                    severity="info" if decision.strip().lower() == "approved" else "warning",
                    summary=(
                        f"Package {decision.strip().lower()} for {swarm.name}: {reason.strip()[:120]}"
                    ),
                    subject_reference=approval_id or swarm_id,
                    occurred_at=_utc_now(),
                    correlation_id=str(correlation_id),
                    status=str(swarm.spine.get("status")),
                )
            )
            decision_value = decision.strip().lower()
            self._append_audit(
                organization_id=str(organization_id),
                kind="package_decision",
                subject_reference=approval_id or swarm_id,
                summary=f"Package {decision_value} for {swarm.name}",
                correlation_id=str(correlation_id),
                payload={
                    "swarm_id": swarm_id,
                    "approval_id": approval_id,
                    "decision": decision_value,
                    "reason": reason.strip()[:500],
                    "spine_status": swarm.spine.get("status"),
                },
            )
            self._persist_state()
            return {
                "ok": True,
                "swarm_id": swarm_id,
                "spine": public_spine_view(swarm.spine),
                "approval_id": approval_id or None,
                "decision": swarm.spine.get("package_decision"),
            }

    def list_package_approvals(self, organization_id: OrganizationId) -> list[dict[str, Any]]:
        """Process-local package gates for Approvals inbox merge."""
        with self._lock:
            rows = [
                dict(v)
                for v in self._package_approvals.values()
                if v.get("organization_id") == str(organization_id)
            ]
        rows.sort(key=lambda r: str(r.get("created_at") or ""), reverse=True)
        return rows

    def get_package_approval(
        self,
        organization_id: OrganizationId,
        approval_id: str,
        *,
        issue_action: bool = True,
    ) -> dict[str, Any] | None:
        """Detail for a façade package gate; optionally issues decide_package when paused."""
        with self._lock:
            rec = self._package_approvals.get(approval_id)
            if rec is None or rec.get("organization_id") != str(organization_id):
                return None
            payload = dict(rec)
            swarm_id = str(rec.get("swarm_id") or "")
            swarm = self._swarms.get(swarm_id) if swarm_id else None
            payload["canvas_path"] = f"/swarms/{swarm_id}/canvas" if swarm_id else None
            payload["note"] = "stub package gate · not production media"
            if swarm is not None and isinstance(swarm.spine, dict):
                payload["spine_status"] = swarm.spine.get("status")
                payload["package_decision"] = swarm.spine.get("package_decision")
                payload["spine_workflow_id"] = swarm.spine.get("workflow_id", SPINE_WORKFLOW_ID)
            actions: list[dict[str, Any]] = []
            if (
                issue_action
                and str(rec.get("gate_status")) == "paused"
                and swarm_id
            ):
                actions.append(
                    self.action_payload(
                        self.issue_action(
                            organization_id=organization_id,
                            kind="decide_package",
                            label="Decide package gate",
                            resource_ref=swarm_id,
                        )
                    )
                )
            payload["actions"] = actions
            return payload

    def get_swarm_artifact(
        self,
        organization_id: OrganizationId,
        swarm_id: str,
        artifact_ref: str,
    ) -> dict[str, Any] | None:
        """Opaque artifact ref lookup (redacted stub summary only)."""
        swarm = self.get_swarm(organization_id, swarm_id)
        if swarm is None or not isinstance(swarm.spine, dict):
            return None
        arts = swarm.spine.get("artifacts")
        if not isinstance(arts, dict):
            return None
        art = arts.get(artifact_ref)
        return public_artifact_view(art if isinstance(art, dict) else None, swarm_id=swarm_id)

    def list_swarm_artifacts(
        self, organization_id: OrganizationId, swarm_id: str
    ) -> dict[str, Any] | None:
        """List redacted stub artifact handoffs for a spine draft."""
        swarm = self.get_swarm(organization_id, swarm_id)
        if swarm is None:
            return None
        if not isinstance(swarm.spine, dict):
            return {
                "swarm_id": swarm_id,
                "items": [],
                "note": "No spine attached.",
            }
        arts = swarm.spine.get("artifacts") if isinstance(swarm.spine.get("artifacts"), dict) else {}
        items = [
            public_artifact_view(art, swarm_id=swarm_id)
            for art in arts.values()
            if isinstance(art, dict)
        ]
        items = [i for i in items if i is not None]
        items.sort(key=lambda row: str(row.get("created_at") or ""))
        return {
            "swarm_id": swarm_id,
            "items": items,
            "count": len(items),
            "note": "stub run · not production media",
        }

    def run_spine_to_package(
        self,
        *,
        organization_id: OrganizationId,
        swarm_id: str,
        action_reference_id: str,
        correlation_id: CorrelationId,
        max_steps: int = 12,
    ) -> dict[str, Any] | None:
        """Dry-run advance stub steps until package gate or terminal (one action)."""
        action = self.consume_action(
            organization_id=organization_id,
            action_reference_id=action_reference_id,
            expected_kind="run_spine_to_package",
            resource_ref=swarm_id,
        )
        if action is None:
            return None
        steps_run = 0
        last: dict[str, Any] | None = None
        for i in range(max(1, min(max_steps, 16))):
            # Internal step actions issued+consumed for fail-closed step runner
            step_action = self.issue_action(
                organization_id=organization_id,
                kind="run_spine_step",
                label="Run spine step (stub)",
                resource_ref=swarm_id,
                eligible=True,
            )
            last = self.run_spine_step(
                organization_id=organization_id,
                swarm_id=swarm_id,
                action_reference_id=step_action.action_id,
                correlation_id=correlation_id,
                step_id=None,
                idempotency_key=f"to_package:{swarm_id}:{i}",
            )
            if last is None:
                return {
                    "ok": False,
                    "message": "Spine step denied mid dry-run.",
                    "steps_run": steps_run,
                }
            if last.get("ok") is False:
                # Waiting for package or terminal already
                spine = last.get("spine") if isinstance(last.get("spine"), dict) else {}
                status = str(spine.get("status") or "")
                if status == "waiting_for_approval":
                    break
                return {
                    **last,
                    "steps_run": steps_run,
                    "dry_run": True,
                }
            steps_run += 1
            spine = last.get("spine") if isinstance(last.get("spine"), dict) else {}
            status = str(spine.get("status") or "")
            if status in {"waiting_for_approval", "completed", "denied", "failed"}:
                break
        assert last is not None
        return {
            **last,
            "ok": True,
            "steps_run": steps_run,
            "dry_run": True,
            "note": "stub dry-run to package · not production media",
        }

    def decide_package_gate_host_issued(
        self,
        *,
        organization_id: OrganizationId,
        approval_id: str,
        correlation_id: CorrelationId,
        decision: str,
        reason: str,
    ) -> dict[str, Any] | None:
        """Decide package using Host-issued action (for control-plane style decision body)."""
        detail = self.get_package_approval(
            organization_id, approval_id, issue_action=False
        )
        if detail is None:
            return None
        swarm_id = str(detail.get("swarm_id") or "")
        if not swarm_id:
            return {"ok": False, "message": "Package approval has no swarm_id."}
        if str(detail.get("gate_status")) != "paused":
            # Idempotent read of already decided gate
            swarm = self.get_swarm(organization_id, swarm_id)
            return {
                "ok": True,
                "idempotent": True,
                "swarm_id": swarm_id,
                "approval_id": approval_id,
                "spine": public_spine_view(swarm.spine if swarm else None),
                "decision": (swarm.spine or {}).get("package_decision") if swarm else None,
            }
        action = self.issue_action(
            organization_id=organization_id,
            kind="decide_package",
            label="Decide package gate",
            resource_ref=swarm_id,
            eligible=True,
        )
        return self.decide_package_gate(
            organization_id=organization_id,
            swarm_id=swarm_id,
            action_reference_id=action.action_id,
            correlation_id=correlation_id,
            decision=decision,
            reason=reason,
        )

    def list_running_swarms(self, organization_id: OrganizationId) -> list[dict[str, Any]]:
        """Queued/running façade swarms plus spine package-waiting attention items."""
        with self._lock:
            rows = [
                s
                for s in self._swarms.values()
                if s.organization_id == str(organization_id)
                and (
                    s.status in {"queued", "running"}
                    or (
                        isinstance(s.spine, dict)
                        and str(s.spine.get("status"))
                        in {"running", "waiting_for_approval"}
                    )
                )
            ]
        rows_sorted = sorted(rows, key=lambda s: s.updated_at, reverse=True)
        out: list[dict[str, Any]] = []
        for s in rows_sorted:
            spine_status = (
                str(s.spine.get("status")) if isinstance(s.spine, dict) else None
            )
            display_status = spine_status or s.status
            out.append(
                {
                    "id": s.swarm_id,
                    "name": s.name,
                    "status": display_status,
                    "revision": s.revision,
                    "last_run_id": s.last_run_id,
                    "member_count": len(s.members),
                    "has_spine": isinstance(s.spine, dict),
                    "spine_status": spine_status,
                    "spine_workflow_id": (
                        str(s.spine.get("workflow_id"))
                        if isinstance(s.spine, dict)
                        else None
                    ),
                    "approval_id": (
                        s.spine.get("approval_id")
                        if isinstance(s.spine, dict)
                        else None
                    ),
                    "note": (
                        "stub run · not production media"
                        if isinstance(s.spine, dict)
                        else None
                    ),
                }
            )
        return out

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
    """Replace the process singleton (tests only; memory-only, no disk hydrate)."""
    global _FACADE
    with _FACADE_LOCK:
        _FACADE = ProductFacadeService(persist=False)
        return _FACADE
