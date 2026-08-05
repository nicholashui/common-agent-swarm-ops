"""Host AgentLoopService — Plan→Act→Self-Review for any video pack agent.

Fail-closed product policy:
- Offline pack harness only (no network, no production media tools).
- Registered pack inventory only (closed world under business/video/agents).
- Real SaaS media activation is intentionally not enabled here.

This is the Host foundation for fleet-wide agent loops (all loadable pack agents).
"""

from __future__ import annotations

import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from app.api.v1.product_facade_store import ProductFacadeStore, persistence_enabled
from app.video.pack_runtime.critique import CritiqueBus, CritiqueSeverity
from app.video.pack_runtime.loader import PackAgentLoader
from app.video.pack_runtime.paths import AGENTS_ROOT
from app.video.pack_runtime.runner import PackAgentRunner, PackAgentRunResult
from app.video.tool_activation import get_host_tool_registry, media_live_enabled

ACTIVATION_POLICY: dict[str, Any] = {
    "production_tools": False,
    "network": False,
    "production_media": False,
    "registered_only": True,
    "mode": "offline_pack_harness",
    "media_live_env": False,
    "note": "Live media tools require CASOPS_MEDIA_LIVE=1 and separate Host go-live review.",
}


def current_activation_policy() -> dict[str, Any]:
    policy = dict(ACTIVATION_POLICY)
    policy["media_live_env"] = media_live_enabled()
    # Still false for agent-loop Act surface even if env set (see tool_activation)
    policy["production_media"] = False
    return policy


@dataclass(slots=True)
class AgentLoopInventoryEntry:
    agent_id: str
    loop_capable: bool
    status: str
    prompt_reference: str = ""
    rubric_reference: str = ""
    max_refinement_count: int = 0
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "loop_capable": self.loop_capable,
            "status": self.status,
            "prompt_reference": self.prompt_reference,
            "rubric_reference": self.rubric_reference,
            "max_refinement_count": self.max_refinement_count,
            "error": self.error,
            "activation_policy": current_activation_policy(),
        }


@dataclass(slots=True)
class AgentLoopRunRecord:
    run_id: str
    agent_id: str
    correlation_id: str
    organization_id: str
    goal: str
    result: dict[str, Any]
    created_at: str = field(
        default_factory=lambda: datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "agent_id": self.agent_id,
            "correlation_id": self.correlation_id,
            "organization_id": self.organization_id,
            "goal": self.goal[:500],
            "result": self.result,
            "created_at": self.created_at,
            "activation_policy": current_activation_policy(),
        }


class AgentLoopService:
    """Fleet agent loop runner over the closed-world video pack."""

    def __init__(
        self,
        *,
        agents_root: Path | None = None,
        runner: PackAgentRunner | None = None,
        persist: bool | None = None,
        store: ProductFacadeStore | None = None,
    ) -> None:
        self._agents_root = (agents_root or AGENTS_ROOT).resolve()
        self._loader = PackAgentLoader(self._agents_root)
        self._runner = runner or PackAgentRunner(loader=self._loader, critique_bus=CritiqueBus())
        self._lock = threading.RLock()
        self._inventory_cache: tuple[AgentLoopInventoryEntry, ...] | None = None
        self._runs: list[AgentLoopRunRecord] = []
        # Project memory + critique log (per org); durable when persist enabled
        self._project_memory: dict[str, list[dict[str, Any]]] = {}
        self._critique_log: dict[str, list[dict[str, Any]]] = {}
        self._tools = get_host_tool_registry()
        enabled = persistence_enabled() if persist is None else persist
        self._store: ProductFacadeStore | None = (
            store if store is not None else (ProductFacadeStore() if enabled else None)
        )
        if self._store is not None:
            self._hydrate_loop_state()

    def _hydrate_loop_state(self) -> None:
        assert self._store is not None
        state = self._store.load_state()
        mem = state.get("loop_memory")
        if isinstance(mem, dict):
            self._project_memory = {
                str(k): list(v) if isinstance(v, list) else []
                for k, v in mem.items()
            }
        crit = state.get("loop_critiques")
        if isinstance(crit, dict):
            self._critique_log = {
                str(k): list(v) if isinstance(v, list) else []
                for k, v in crit.items()
            }

    def _persist_loop_state(self) -> None:
        """Snapshot + durable write under the service lock.

        Parallel ``run_crew`` can interleave appends; releasing the lock
        between snapshot and full-file write allowed an older write to finish
        last and drop later agents' project_memory / critiques on rehydrate.
        """
        if self._store is None:
            return
        with self._lock:
            mem = {k: list(v) for k, v in self._project_memory.items()}
            crit = {k: list(v) for k, v in self._critique_log.items()}
            # Hold lock through store I/O so concurrent persists cannot race
            # two full-file replacements with stale in-memory copies.
            self._store.save_loop_memory(mem)
            self._store.save_loop_critiques(crit)

    def list_inventory(self, *, refresh: bool = False) -> list[dict[str, Any]]:
        """Enumerate all pack agent folders and whether offline loops can load."""
        with self._lock:
            if self._inventory_cache is not None and not refresh:
                return [e.to_dict() for e in self._inventory_cache]
            entries: list[AgentLoopInventoryEntry] = []
            if not self._agents_root.is_dir():
                self._inventory_cache = ()
                return []
            for path in sorted(self._agents_root.iterdir()):
                if not path.is_dir():
                    continue
                agent_id = path.name
                if not agent_id.startswith("video."):
                    continue
                try:
                    bundle = self._loader.load(agent_id)
                    entries.append(
                        AgentLoopInventoryEntry(
                            agent_id=agent_id,
                            loop_capable=True,
                            status="loop_ready",
                            prompt_reference=bundle.prompt_reference,
                            rubric_reference=bundle.rubric_reference,
                            max_refinement_count=bundle.max_refinement_count,
                        )
                    )
                except Exception as exc:  # noqa: BLE001 — inventory must not crash
                    entries.append(
                        AgentLoopInventoryEntry(
                            agent_id=agent_id,
                            loop_capable=False,
                            status="load_failed",
                            error=str(exc)[:300],
                        )
                    )
            self._inventory_cache = tuple(entries)
            return [e.to_dict() for e in self._inventory_cache]

    def inventory_summary(self) -> dict[str, Any]:
        items = self.list_inventory()
        capable = sum(1 for i in items if i.get("loop_capable"))
        return {
            "total_agents": len(items),
            "loop_capable": capable,
            "load_failed": len(items) - capable,
            "activation_policy": current_activation_policy(),
            "note": (
                "Offline Plan→Act→Self-Review for loadable pack agents. "
                "Not production media; not full SaaS tool activation."
            ),
        }

    def run(
        self,
        agent_id: str,
        *,
        organization_id: str,
        goal: str,
        correlation_id: str | None = None,
        inputs: dict[str, Any] | None = None,
        allow_production: bool = False,
        allow_network: bool = False,
    ) -> dict[str, Any]:
        """Run one agent loop. Refuses production/network activation flags."""
        policy = current_activation_policy()
        goal_s = (goal or "").strip()
        if not goal_s:
            return {
                "ok": False,
                "error": "goal is required",
                "activation_policy": policy,
            }
        if allow_production or allow_network:
            return {
                "ok": False,
                "error": (
                    "Production tools / network are not enabled on AgentLoopService. "
                    "Fail-closed until Host production activation."
                ),
                "activation_policy": policy,
            }

        corr = (correlation_id or "").strip() or f"loop_{uuid4().hex[:12]}"
        try:
            result: PackAgentRunResult = self._runner.run(
                agent_id,
                goal=goal_s,
                correlation_id=corr,
                inputs=inputs or {},
                constraints={
                    "network": False,
                    "production": False,
                    "production_media": False,
                },
                emit_self_critique_to=agent_id,
            )
        except Exception as exc:  # noqa: BLE001
            return {
                "ok": False,
                "agent_id": agent_id,
                "correlation_id": corr,
                "error": str(exc)[:500],
                "activation_policy": policy,
            }

        payload = result.to_dict()
        # Act phase: Host tool registry (stub invocations for pack allowlist)
        tool_invocations: list[dict[str, Any]] = []
        try:
            bundle = self._loader.load(agent_id)
            tool_invocations = self._tools.invoke_for_agent(
                agent_id,
                bundle.allowed_tools,
                arguments={"goal": goal_s[:200], "correlation_id": corr},
            )
        except Exception:  # noqa: BLE001
            tool_invocations = self._tools.invoke_for_agent(
                agent_id,
                ("media.stub",),
                arguments={"goal": goal_s[:200]},
            )

        # Attach loop phase labels (common-agent-structure)
        payload["phases"] = {
            "plan": "parse ticket/goal + select path (offline harness)",
            "act": "Host tool registry · stub by default · no production media",
            "self_review": "L1 pack checks + L2 rubric offline",
        }
        payload["tool_invocations"] = tool_invocations
        payload["activation_policy"] = policy
        ok = payload.get("status") == "ok" and not payload.get("needs_hitl")

        # Extra self-critique when not ok
        critiques = list(payload.get("critiques_emitted") or [])
        if not ok:
            try:
                msg = self._runner.critique_bus.send(
                    correlation_id=corr,
                    from_id=agent_id,
                    to_id=agent_id,
                    severity=CritiqueSeverity.MAJOR,
                    claim=f"Agent loop incomplete status={payload.get('status')}",
                    allowed_outputs=(agent_id,),
                    artifact_ref=f"loop:{agent_id}:{corr}",
                    kind="critique",
                )
                critiques.append(msg.to_dict())
                payload["critiques_emitted"] = critiques
            except (PermissionError, ValueError):
                pass

        run_id = f"alr_{uuid4().hex[:16]}"
        # Project memory + durable critique log for org
        mem_entry = {
            "run_id": run_id,
            "agent_id": agent_id,
            "correlation_id": corr,
            "summary": (payload.get("artifact") or {}).get("summary")
            or payload.get("status"),
            "handoff_ref": f"loop:{agent_id}:{run_id}",
            "created_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        # Append + durable full-file persist must share one critical section so
        # parallel crew workers never lose another worker's memory rows on disk.
        with self._lock:
            self._project_memory.setdefault(organization_id, []).append(mem_entry)
            if len(self._project_memory[organization_id]) > 2000:
                self._project_memory[organization_id] = self._project_memory[organization_id][
                    -1500:
                ]
            if critiques:
                bucket = self._critique_log.setdefault(organization_id, [])
                bucket.extend(critiques)
                if len(bucket) > 3000:
                    self._critique_log[organization_id] = bucket[-2000:]
            if self._store is not None:
                mem = {k: list(v) for k, v in self._project_memory.items()}
                crit = {k: list(v) for k, v in self._critique_log.items()}
                self._store.save_loop_memory(mem)
                self._store.save_loop_critiques(crit)
        # Append-only tool log is safe outside the full-file snapshot lock.
        if self._store is not None:
            for inv in tool_invocations:
                if isinstance(inv, dict):
                    self._store.append_tool_invocation(
                        {
                            "organization_id": organization_id,
                            "agent_id": agent_id,
                            "run_id": run_id,
                            "correlation_id": corr,
                            **inv,
                        }
                    )

        record = AgentLoopRunRecord(
            run_id=run_id,
            agent_id=agent_id,
            correlation_id=corr,
            organization_id=organization_id,
            goal=goal_s,
            result=payload,
        )
        with self._lock:
            self._runs.append(record)
            if len(self._runs) > 2000:
                self._runs = self._runs[-1500:]

        return {
            "ok": bool(ok),
            "run_id": run_id,
            "agent_id": agent_id,
            "correlation_id": corr,
            "status": payload.get("status"),
            "needs_hitl": bool(payload.get("needs_hitl")),
            "l1": payload.get("l1"),
            "l2": payload.get("l2"),
            "refinement_count": payload.get("refinement_count"),
            "critiques_emitted": payload.get("critiques_emitted") or [],
            "evidence_refs": payload.get("evidence_refs") or [],
            "tool_invocations": tool_invocations,
            "phases": payload.get("phases"),
            "artifact_summary": (payload.get("artifact") or {}).get("summary"),
            "notes": payload.get("notes"),
            "activation_policy": policy,
            "result": payload,
        }

    def project_memory(
        self, organization_id: str, *, limit: int = 50
    ) -> list[dict[str, Any]]:
        limit = max(1, min(limit, 200))
        with self._lock:
            rows = list(self._project_memory.get(organization_id) or [])
        return rows[-limit:]

    def critique_log(
        self, organization_id: str, *, limit: int = 50
    ) -> list[dict[str, Any]]:
        limit = max(1, min(limit, 200))
        with self._lock:
            rows = list(self._critique_log.get(organization_id) or [])
        return rows[-limit:]

    def tool_invocation_log(
        self, organization_id: str, *, limit: int = 50
    ) -> list[dict[str, Any]]:
        """Durable tool invocation history when façade persist is enabled."""
        if self._store is None:
            return []
        return self._store.list_tool_invocations(
            organization_id=organization_id, limit=limit
        )

    def run_crew(
        self,
        agent_ids: list[str],
        *,
        organization_id: str,
        goal: str,
        correlation_id: str | None = None,
        stop_on_failure: bool = False,
        parallel: bool = False,
        max_workers: int = 4,
    ) -> dict[str, Any]:
        """Run loops for many agents (closed-world IDs only).

        Sequential by default. When ``parallel=True``, uses a bounded
        ThreadPoolExecutor (max 16 workers). ``stop_on_failure`` applies
        only to sequential mode.
        """
        corr = (correlation_id or "").strip() or f"crew_{uuid4().hex[:12]}"
        unique: list[str] = []
        for aid in agent_ids:
            a = str(aid).strip()
            if a and a not in unique:
                unique.append(a)
        if not unique:
            return {"ok": False, "error": "agent_ids required", "results": []}

        results: list[dict[str, Any]] = []
        mode = "sequential"
        if parallel and len(unique) > 1:
            mode = "parallel_bounded"
            workers = max(1, min(int(max_workers or 4), 16, len(unique)))
            ordered: list[dict[str, Any] | None] = [None] * len(unique)
            with ThreadPoolExecutor(max_workers=workers) as pool:
                future_map = {
                    pool.submit(
                        self.run,
                        aid,
                        organization_id=organization_id,
                        goal=goal,
                        correlation_id=f"{corr}:{aid}",
                    ): idx
                    for idx, aid in enumerate(unique)
                }
                for fut in as_completed(future_map):
                    idx = future_map[fut]
                    aid = unique[idx]
                    try:
                        ordered[idx] = fut.result()
                    except Exception as exc:  # noqa: BLE001
                        ordered[idx] = {
                            "ok": False,
                            "agent_id": aid,
                            "error": str(exc)[:500],
                        }
            results = [r for r in ordered if r is not None]
        else:
            for aid in unique:
                row = self.run(
                    aid,
                    organization_id=organization_id,
                    goal=goal,
                    correlation_id=f"{corr}:{aid}",
                )
                results.append(row)
                if stop_on_failure and not row.get("ok"):
                    break

        ok_count = sum(1 for r in results if r.get("ok"))
        return {
            "ok": ok_count == len(results) and len(results) > 0,
            "correlation_id": corr,
            "requested": len(unique),
            "completed": len(results),
            "passed": ok_count,
            "failed": len(results) - ok_count,
            "mode": mode,
            "results": results,
            "activation_policy": current_activation_policy(),
            "note": (
                f"{'Bounded parallel' if mode == 'parallel_bounded' else 'Sequential'} "
                "offline loops · not concurrent production swarm · not production media"
            ),
        }

    def run_fleet_sample(
        self,
        *,
        organization_id: str,
        goal: str,
        limit: int = 12,
        only_capable: bool = True,
    ) -> dict[str, Any]:
        """Run offline loops for a sample of the pack fleet (CI-friendly bound)."""
        inv = self.list_inventory()
        ids = [
            str(i["agent_id"])
            for i in inv
            if (not only_capable or i.get("loop_capable")) and i.get("agent_id")
        ][: max(1, min(limit, 32))]
        return self.run_crew(
            ids,
            organization_id=organization_id,
            goal=goal,
            correlation_id=f"fleet_{uuid4().hex[:10]}",
            stop_on_failure=False,
        )

    def list_recent_runs(
        self, organization_id: str, *, limit: int = 50
    ) -> list[dict[str, Any]]:
        limit = max(1, min(limit, 200))
        with self._lock:
            rows = [r for r in self._runs if r.organization_id == organization_id]
        return [r.to_dict() for r in rows[-limit:]]


_SERVICE: AgentLoopService | None = None
_SERVICE_LOCK = threading.Lock()


def get_agent_loop_service() -> AgentLoopService:
    global _SERVICE
    with _SERVICE_LOCK:
        if _SERVICE is None:
            _SERVICE = AgentLoopService()
        return _SERVICE


def reset_agent_loop_service_for_tests() -> AgentLoopService:
    global _SERVICE
    with _SERVICE_LOCK:
        _SERVICE = AgentLoopService()
        return _SERVICE


__all__ = [
    "ACTIVATION_POLICY",
    "AgentLoopService",
    "get_agent_loop_service",
    "reset_agent_loop_service_for_tests",
]
