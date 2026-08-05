"""Taste-Keeper — process-local versioned AestheticProfile store (spec §10)."""

from __future__ import annotations

import threading
from typing import Any

from app.aesthetics.models import (
    AESTHETIC_DIMENSIONS,
    ACTIVATION_POLICY,
    AestheticProfileCreate,
    AestheticProfileRecord,
)

NEUTRAL_PROFILE_ID = "neutral_baseline_v1"

_DEFAULT_WEIGHTS: dict[str, float] = {d: 1.0 for d in AESTHETIC_DIMENSIONS}


class TasteKeeper:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._profiles: dict[str, AestheticProfileRecord] = {}
        self._seed_neutral()

    def _seed_neutral(self) -> None:
        rec = AestheticProfileRecord(
            profile_id=NEUTRAL_PROFILE_ID,
            owner="system",
            profile_type="neutral_baseline",
            consent={
                "scope": "global_baseline",
                "expires": None,
                "c2pa_signed": False,
                "note": "Explicit taste-agnostic baseline (spec §3.3).",
            },
            weights=dict(_DEFAULT_WEIGHTS),
            exemplars=[],
            anti_exemplars=[],
            elicited_criteria=["neutral baseline — no personal taste encoded"],
            version=1,
            lineage=["v1"],
            activation_policy=dict(ACTIVATION_POLICY),
        )
        self._profiles[NEUTRAL_PROFILE_ID] = rec

    def list_profiles(self) -> list[dict[str, Any]]:
        with self._lock:
            return [p.model_dump() for p in self._profiles.values()]

    def get(self, profile_id: str | None) -> AestheticProfileRecord:
        with self._lock:
            if not profile_id or not str(profile_id).strip():
                return self._profiles[NEUTRAL_PROFILE_ID]
            pid = str(profile_id).strip()
            if pid in self._profiles:
                return self._profiles[pid]
            # Unknown id → neutral + flag handled by caller
            return self._profiles[NEUTRAL_PROFILE_ID]

    def resolve_profile_id(self, profile_id: str | None) -> tuple[str, bool]:
        """Return (profile_id_used, used_neutral_fallback)."""
        if not profile_id or not str(profile_id).strip():
            return NEUTRAL_PROFILE_ID, True
        pid = str(profile_id).strip()
        with self._lock:
            if pid in self._profiles:
                return pid, False
        return NEUTRAL_PROFILE_ID, True

    def upsert(self, body: AestheticProfileCreate) -> AestheticProfileRecord:
        pid = body.profile_id.strip()
        weights = dict(_DEFAULT_WEIGHTS)
        for k, v in (body.weights or {}).items():
            if k in weights:
                try:
                    weights[k] = max(0.0, min(5.0, float(v)))
                except (TypeError, ValueError):
                    continue
        with self._lock:
            existing = self._profiles.get(pid)
            version = 1 if existing is None else existing.version + 1
            lineage = list(existing.lineage) if existing else []
            lineage.append(f"v{version}")
            rec = AestheticProfileRecord(
                profile_id=pid,
                owner=body.owner.strip() or "local",
                profile_type=body.profile_type,
                consent={
                    "scope": body.consent_scope,
                    "expires": None,
                    "c2pa_signed": False,
                    "note": "Process-local profile; not production consent registry.",
                },
                weights=weights,
                exemplars=list(body.exemplars or [])[:64],
                anti_exemplars=list(body.anti_exemplars or [])[:64],
                elicited_criteria=list(body.elicited_criteria or [])[:64],
                version=version,
                lineage=lineage[-32:],
                activation_policy=dict(ACTIVATION_POLICY),
            )
            self._profiles[pid] = rec
            return rec

    def compose(
        self,
        *,
        base_profile_id: str,
        overlay_profile_id: str,
        new_profile_id: str,
        owner: str = "local",
        precedence: str = "overlay",
    ) -> AestheticProfileRecord:
        """Compose two profiles (e.g. brand ⊕ genre_prior) into a new versioned profile.

        precedence:
          - overlay: overlay weights win where set above default
          - average: mean of both weights
        """
        base = self.get(base_profile_id)
        overlay = self.get(overlay_profile_id)
        weights = dict(_DEFAULT_WEIGHTS)
        if precedence == "average":
            for d in AESTHETIC_DIMENSIONS:
                weights[d] = round(
                    (float(base.weights.get(d, 1.0)) + float(overlay.weights.get(d, 1.0)))
                    / 2.0,
                    4,
                )
        else:
            # Start from base, overlay wins for non-default (≠1.0) dimensions
            for d in AESTHETIC_DIMENSIONS:
                bw = float(base.weights.get(d, 1.0))
                ow = float(overlay.weights.get(d, 1.0))
                weights[d] = ow if abs(ow - 1.0) > 1e-6 else bw

        criteria = list(dict.fromkeys(
            list(base.elicited_criteria or [])
            + list(overlay.elicited_criteria or [])
            + [f"composed:{base.profile_id}+{overlay.profile_id}"]
        ))[:64]
        body = AestheticProfileCreate(
            profile_id=new_profile_id.strip(),
            owner=owner or "local",
            profile_type=overlay.profile_type
            if overlay.profile_type != "neutral_baseline"
            else base.profile_type,
            weights=weights,
            exemplars=list(dict.fromkeys(list(base.exemplars) + list(overlay.exemplars)))[
                :64
            ],
            anti_exemplars=list(
                dict.fromkeys(list(base.anti_exemplars) + list(overlay.anti_exemplars))
            )[:64],
            elicited_criteria=criteria,
            consent_scope=f"compose:{base.profile_id}+{overlay.profile_id}",
        )
        return self.upsert(body)

    def ratchet(
        self,
        *,
        profile_id: str,
        decision: str,
        top_failing_dimensions: list[str] | None = None,
        aesthetic_quality: float | None = None,
    ) -> AestheticProfileRecord | None:
        """Nudge profile weights from accept/reject episodic memory (offline §7.4).

        - accepted: slightly raise weights of non-failing dimensions when AQ high
        - rejected: slightly raise weights of failing dimensions (care more next time)
        Returns updated profile or None if profile is neutral baseline / missing.
        """
        pid = (profile_id or "").strip()
        if not pid or pid == NEUTRAL_PROFILE_ID:
            return None
        with self._lock:
            existing = self._profiles.get(pid)
            if existing is None:
                return None
            weights = dict(existing.weights)
            failing = list(top_failing_dimensions or [])
            dec = decision.strip().lower()
            delta = 0.05
            if dec == "accepted":
                # Reinforce strengths: bump dims that were not failing
                for d in AESTHETIC_DIMENSIONS:
                    if d not in failing:
                        weights[d] = min(5.0, float(weights.get(d, 1.0)) + delta * 0.5)
                if aesthetic_quality is not None and aesthetic_quality >= 0.7:
                    for d in AESTHETIC_DIMENSIONS:
                        if d not in failing:
                            weights[d] = min(5.0, float(weights.get(d, 1.0)) + delta * 0.25)
            elif dec == "rejected":
                for d in failing[:4]:
                    if d in weights:
                        weights[d] = min(5.0, float(weights.get(d, 1.0)) + delta)
            else:
                return existing

            version = existing.version + 1
            lineage = list(existing.lineage) + [f"v{version}"]
            criteria = list(existing.elicited_criteria)
            note = f"ratchet:{dec}:{','.join(failing[:3]) or 'none'}"
            if note not in criteria:
                criteria = (criteria + [note])[:64]
            rec = AestheticProfileRecord(
                profile_id=existing.profile_id,
                owner=existing.owner,
                profile_type=existing.profile_type,
                consent=dict(existing.consent),
                weights=weights,
                exemplars=list(existing.exemplars),
                anti_exemplars=list(existing.anti_exemplars),
                elicited_criteria=criteria,
                version=version,
                lineage=lineage[-32:],
                activation_policy=dict(ACTIVATION_POLICY),
            )
            self._profiles[pid] = rec
            return rec
