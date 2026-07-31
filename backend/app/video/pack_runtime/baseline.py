"""Human baseline protocols and surpass-gate evaluation (Q5).

Honesty rules:
- Protocol-only → not a surpass claim
- Synthetic CI fixtures never set gate.met for production claims
- gate.met requires human baseline + agent measurement + threshold check
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from app.video.pack_runtime.paths import EVALS_AGENTS_ROOT
from app.video.pack_runtime.runner import PackAgentRunner


def _utc_now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def protocol_path(agent_id: str, evals_root: Path = EVALS_AGENTS_ROOT) -> Path:
    return evals_root / agent_id / "human_baseline_protocol.json"


def evidence_path(agent_id: str, evals_root: Path = EVALS_AGENTS_ROOT) -> Path:
    return evals_root / agent_id / "human_baseline_evidence.json"


def infer_metric(surpass_signal: str) -> dict[str, Any]:
    """Heuristic metric schema from agents.md Surpass-Human Signal text."""
    text = surpass_signal or "Improve craft quality vs human baseline on frozen golden task"
    lower = text.lower()
    metric: dict[str, Any] = {
        "id": "craft_score",
        "name": "Craft score vs human baseline",
        "direction": "higher_is_better",
        "unit": "score_0_100",
        "threshold_expression": "agent_mean >= human_mean",
        "pairwise_win_rate_min": None,
        "raw_signal": text,
    }
    # Win rate patterns: Wins ≥55% ...
    m = re.search(r"(?:wins?|win rate)\s*≥\s*([0-9]+(?:\.[0-9]+)?)\s*%", lower)
    if not m:
        m = re.search(r"≥\s*([0-9]+(?:\.[0-9]+)?)\s*%", lower)
    if m and ("win" in lower or "pairwise" in lower or "arena" in lower or "blind" in lower):
        rate = float(m.group(1)) / 100.0
        metric.update(
            {
                "id": "pairwise_win_rate",
                "name": "Blind pairwise win rate vs human",
                "direction": "higher_is_better",
                "unit": "fraction",
                "pairwise_win_rate_min": rate,
                "threshold_expression": f"agent_pairwise_win_rate >= {rate}",
            }
        )
        return metric
    if "ttd" in lower or "faster" in lower or "turnaround" in lower or "hours vs" in lower:
        metric.update(
            {
                "id": "time_to_delivery",
                "name": "Time-to-delivery vs human",
                "direction": "lower_is_better",
                "unit": "relative_ratio",
                "threshold_expression": "agent_mean < human_mean",
            }
        )
        return metric
    if "cheaper" in lower or "cost" in lower or "0.6×" in lower or "0.6x" in lower:
        metric.update(
            {
                "id": "cost_efficiency",
                "name": "Cost efficiency vs human",
                "direction": "lower_is_better",
                "unit": "relative_cost",
                "threshold_expression": "agent_mean < human_mean",
            }
        )
        return metric
    if "κ" in text or "kappa" in lower or "agreement" in lower:
        metric.update(
            {
                "id": "agreement_kappa",
                "name": "Agreement κ vs human juror",
                "direction": "higher_is_better",
                "unit": "kappa",
                "threshold_expression": "agent_mean > human_mean",
            }
        )
        return metric
    if "accuracy" in lower or "pass rate" in lower or "coverage" in lower:
        metric.update(
            {
                "id": "accuracy_or_coverage",
                "name": "Accuracy/coverage vs human",
                "direction": "higher_is_better",
                "unit": "fraction_or_score",
                "threshold_expression": "agent_mean >= human_mean",
            }
        )
        return metric
    return metric


def build_protocol(
    agent_id: str,
    *,
    surpass_signal: str,
    self_quality: str = "",
    va_name: str = "",
) -> dict[str, Any]:
    metric = infer_metric(surpass_signal)
    return {
        "schema_version": "1.0",
        "agent_id": agent_id,
        "va_name": va_name,
        "status": "protocol_ready",
        "honesty": {
            "rule": "Never claim human-surpass in UI without gate.met=true and synthetic=false",
            "synthetic_ci_allowed": True,
            "synthetic_sets_met": False,
        },
        "surpass_signal_design": surpass_signal
        or "Meet or exceed human baseline on frozen golden task craft score",
        "self_quality_criteria": self_quality,
        "metric": metric,
        "protocol": {
            "n_human_trials_min": 5,
            "n_agent_trials_min": 5,
            "task_fixture": f"business/video/evals/agents/{agent_id}/golden.json",
            "blinding": "pairwise" if metric["id"] == "pairwise_win_rate" else "frozen_inputs",
            "frozen_inputs": True,
            "operators": ["human_rater", "pack_runtime_offline_agent"],
            "recording": [
                "trial_id",
                "rater_or_runner",
                "score_or_outcome",
                "notes",
                "timestamp",
            ],
        },
        "human_baseline": {
            "status": "pending",
            "trials": [],
            "aggregate": None,
            "captured_at": None,
        },
        "agent_measurement": {
            "status": "pending",
            "trials": [],
            "aggregate": None,
            "measured_at": None,
            "runner": "pack_runtime.offline",
        },
        "gate": {
            "status": "not_run",
            "met": False,
            "synthetic": False,
            "detail": "Awaiting human baseline + agent measurement",
            "evaluated_at": None,
            "evidence_path": f"business/video/evals/agents/{agent_id}/human_baseline_evidence.json",
        },
        "generated_by": "scaffold_human_baselines_v1",
        "generated_at": _utc_now(),
        "updated_at": _utc_now(),
    }


@dataclass(slots=True)
class GateResult:
    agent_id: str
    status: str
    met: bool
    detail: str
    protocol: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "status": self.status,
            "met": self.met,
            "detail": self.detail,
            "gate": self.protocol.get("gate"),
            "human_baseline_status": (self.protocol.get("human_baseline") or {}).get("status"),
            "agent_measurement_status": (self.protocol.get("agent_measurement") or {}).get(
                "status"
            ),
        }


class HumanBaselineService:
    """Load/update baseline protocols and evaluate surpass gates."""

    def __init__(
        self,
        evals_root: Path = EVALS_AGENTS_ROOT,
        runner: PackAgentRunner | None = None,
    ) -> None:
        self._evals_root = evals_root.resolve()
        self._runner = runner or PackAgentRunner()

    def load(self, agent_id: str) -> dict[str, Any]:
        path = protocol_path(agent_id, self._evals_root)
        if not path.is_file():
            raise FileNotFoundError(f"No baseline protocol for {agent_id}")
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("protocol must be object")
        return data

    def save(self, protocol: dict[str, Any]) -> Path:
        agent_id = str(protocol.get("agent_id") or "")
        if not agent_id:
            raise ValueError("agent_id required")
        path = protocol_path(agent_id, self._evals_root)
        path.parent.mkdir(parents=True, exist_ok=True)
        protocol["updated_at"] = _utc_now()
        path.write_text(json.dumps(protocol, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return path

    def clear_human_trials(self, agent_id: str, *, only_synthetic: bool = False) -> dict[str, Any]:
        """Remove human trials (optionally only synthetic) so real raters start clean."""
        proto = self.load(agent_id)
        hb = proto.setdefault("human_baseline", {"trials": []})
        trials = list(hb.get("trials") or [])
        if only_synthetic:
            trials = [t for t in trials if not bool(t.get("synthetic"))]
        else:
            trials = []
        hb["trials"] = trials
        if trials:
            scores = [float(t["score"]) for t in trials]
            hb["aggregate"] = {
                "n": len(scores),
                "mean": round(sum(scores) / len(scores), 4),
                "min": min(scores),
                "max": max(scores),
                "synthetic_any": any(bool(t.get("synthetic")) for t in trials),
            }
            min_n = int((proto.get("protocol") or {}).get("n_human_trials_min") or 5)
            hb["status"] = "captured" if len(scores) >= min_n else "partial"
        else:
            hb["aggregate"] = None
            hb["status"] = "pending"
            hb["captured_at"] = None
        proto["gate"] = {
            "status": "not_run",
            "met": False,
            "synthetic": False,
            "detail": "Human trials cleared; re-record and evaluate",
            "evaluated_at": None,
            "evidence_path": f"business/video/evals/agents/{agent_id}/human_baseline_evidence.json",
        }
        proto["status"] = (
            "measured"
            if (proto.get("agent_measurement") or {}).get("status") == "measured"
            else "protocol_ready"
        )
        self.save(proto)
        return proto

    def record_human_trial(
        self,
        agent_id: str,
        *,
        score: float,
        rater_id: str = "human_rater",
        notes: str = "",
        synthetic: bool = False,
    ) -> dict[str, Any]:
        proto = self.load(agent_id)
        trial = {
            "trial_id": f"human_{uuid4().hex[:10]}",
            "rater_id": rater_id,
            "score": float(score),
            "notes": notes,
            "synthetic": synthetic,
            "timestamp": _utc_now(),
        }
        hb = proto.setdefault("human_baseline", {"trials": []})
        trials = list(hb.get("trials") or [])
        trials.append(trial)
        hb["trials"] = trials
        scores = [float(t["score"]) for t in trials]
        hb["aggregate"] = {
            "n": len(scores),
            "mean": round(sum(scores) / len(scores), 4),
            "min": min(scores),
            "max": max(scores),
            "synthetic_any": any(bool(t.get("synthetic")) for t in trials),
        }
        min_n = int((proto.get("protocol") or {}).get("n_human_trials_min") or 5)
        hb["status"] = "captured" if len(scores) >= min_n else "partial"
        hb["captured_at"] = _utc_now()
        if proto.get("status") == "protocol_ready":
            proto["status"] = (
                "baseline_captured" if hb["status"] == "captured" else "protocol_ready"
            )
        self.save(proto)
        return proto

    def measure_agent_offline(
        self,
        agent_id: str,
        *,
        trials: int | None = None,
        goal: str | None = None,
    ) -> dict[str, Any]:
        proto = self.load(agent_id)
        min_n = int((proto.get("protocol") or {}).get("n_agent_trials_min") or 5)
        n = trials or min_n
        goal = goal or f"Baseline measurement task for {agent_id} (offline frozen golden)"
        recorded = []
        for i in range(n):
            run = self._runner.run(
                agent_id,
                goal=f"{goal} [trial {i + 1}/{n}]",
                correlation_id=f"base_{agent_id}_{uuid4().hex[:8]}",
                constraints={"network": False, "production": False},
            )
            score = float((run.l2 or {}).get("score") or 0)
            recorded.append(
                {
                    "trial_id": f"agent_{uuid4().hex[:10]}",
                    "score": score,
                    "status": run.status,
                    "l1_passed": bool((run.l1 or {}).get("passed")),
                    "refinement_count": run.refinement_count,
                    "timestamp": _utc_now(),
                    "synthetic": False,
                    "offline": True,
                }
            )
        scores = [float(t["score"]) for t in recorded]
        am = proto.setdefault("agent_measurement", {})
        am["trials"] = recorded
        am["aggregate"] = {
            "n": len(scores),
            "mean": round(sum(scores) / len(scores), 4) if scores else 0,
            "min": min(scores) if scores else 0,
            "max": max(scores) if scores else 0,
        }
        am["status"] = "measured" if len(scores) >= min_n else "partial"
        am["measured_at"] = _utc_now()
        am["runner"] = "pack_runtime.offline"
        if proto.get("status") in {"protocol_ready", "baseline_captured"}:
            proto["status"] = "measured"
        self.save(proto)
        return proto

    def evaluate_gate(self, agent_id: str) -> GateResult:
        proto = self.load(agent_id)
        metric = proto.get("metric") or {}
        hb = proto.get("human_baseline") or {}
        am = proto.get("agent_measurement") or {}
        gate = proto.setdefault("gate", {})

        human_agg = hb.get("aggregate") or {}
        agent_agg = am.get("aggregate") or {}
        human_n = int(human_agg.get("n") or 0)
        agent_n = int(agent_agg.get("n") or 0)
        min_h = int((proto.get("protocol") or {}).get("n_human_trials_min") or 5)
        min_a = int((proto.get("protocol") or {}).get("n_agent_trials_min") or 5)
        synthetic = bool(human_agg.get("synthetic_any"))

        if human_n < min_h or agent_n < min_a:
            gate.update(
                {
                    "status": "incomplete",
                    "met": False,
                    "synthetic": synthetic,
                    "detail": f"Need human_n>={min_h} (have {human_n}) and agent_n>={min_a} (have {agent_n})",
                    "evaluated_at": _utc_now(),
                }
            )
            proto["status"] = "protocol_ready" if human_n == 0 else "baseline_partial"
            self.save(proto)
            self._write_evidence(agent_id, proto)
            return GateResult(agent_id, gate["status"], False, gate["detail"], proto)

        human_mean = float(human_agg.get("mean") or 0)
        agent_mean = float(agent_agg.get("mean") or 0)
        direction = str(metric.get("direction") or "higher_is_better")
        win_min = metric.get("pairwise_win_rate_min")

        if win_min is not None:
            # interpret agent_mean as win-rate fraction if unit fraction, else score/100
            unit = str(metric.get("unit") or "")
            agent_rate = agent_mean if unit == "fraction" else agent_mean / 100.0
            met = agent_rate >= float(win_min)
            detail = f"pairwise/agent_rate={agent_rate:.4f} min={float(win_min):.4f}"
        elif direction == "lower_is_better":
            met = agent_mean < human_mean
            detail = f"agent_mean={agent_mean} < human_mean={human_mean}"
        else:
            met = agent_mean >= human_mean
            detail = f"agent_mean={agent_mean} >= human_mean={human_mean}"

        # Synthetic human data may never claim production met
        if synthetic:
            met_claim = False
            detail = f"SYNTHETIC human data — pipeline check only; not a surpass claim. ({detail})"
            status = "synthetic_checked"
        else:
            met_claim = met
            status = "met" if met else "not_met"
            detail = ("MET: " if met else "NOT MET: ") + detail

        gate.update(
            {
                "status": status,
                "met": met_claim,
                "synthetic": synthetic,
                "detail": detail,
                "evaluated_at": _utc_now(),
                "comparison": {
                    "human_mean": human_mean,
                    "agent_mean": agent_mean,
                    "direction": direction,
                    "raw_met": met,
                },
            }
        )
        proto["status"] = status
        self.save(proto)
        self._write_evidence(agent_id, proto)
        return GateResult(agent_id, status, met_claim, detail, proto)

    def _write_evidence(self, agent_id: str, protocol: dict[str, Any]) -> Path:
        path = evidence_path(agent_id, self._evals_root)
        path.parent.mkdir(parents=True, exist_ok=True)
        bundle = {
            "schema_version": "1.0",
            "agent_id": agent_id,
            "recorded_at": _utc_now(),
            "protocol_snapshot": protocol,
            "claim_allowed_in_ui": bool((protocol.get("gate") or {}).get("met"))
            and not bool((protocol.get("gate") or {}).get("synthetic")),
        }
        path.write_text(json.dumps(bundle, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return path

    def readiness(self, agent_id: str) -> str:
        """protocol_missing | protocol_ready | baseline_partial | measured | met | not_met | synthetic_checked"""
        path = protocol_path(agent_id, self._evals_root)
        if not path.is_file():
            return "protocol_missing"
        proto = self.load(agent_id)
        return str(proto.get("status") or "protocol_ready")
