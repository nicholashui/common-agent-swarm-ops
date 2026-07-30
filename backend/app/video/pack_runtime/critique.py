"""In-process CritiqueMessage bus with edge allowlists and severity routing."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4


class CritiqueSeverity(StrEnum):
    BLOCKER = "blocker"
    MAJOR = "major"
    MINOR = "minor"
    NIT = "nit"


@dataclass(frozen=True, slots=True)
class CritiqueMessage:
    """Typed peer critique / instruction between pack agents."""

    message_id: str
    correlation_id: str
    from_id: str
    to_id: str
    severity: CritiqueSeverity
    claim: str
    artifact_ref: str = ""
    evidence_refs: tuple[str, ...] = ()
    kind: str = "critique"  # critique | instruction | dispute | resolution
    requires_hitl: bool = False
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "message_id": self.message_id,
            "correlation_id": self.correlation_id,
            "from_id": self.from_id,
            "to_id": self.to_id,
            "severity": self.severity.value,
            "claim": self.claim,
            "artifact_ref": self.artifact_ref,
            "evidence_refs": list(self.evidence_refs),
            "kind": self.kind,
            "requires_hitl": self.requires_hitl,
            "created_at": self.created_at,
        }


class CritiqueBus:
    """Fail-closed in-memory bus: only allowlisted critique_edges may send."""

    def __init__(self) -> None:
        self._by_correlation: dict[str, list[CritiqueMessage]] = {}
        self._acks: dict[str, str] = {}

    def send(
        self,
        *,
        correlation_id: str,
        from_id: str,
        to_id: str,
        severity: CritiqueSeverity | str,
        claim: str,
        allowed_outputs: tuple[str, ...] | list[str],
        artifact_ref: str = "",
        evidence_refs: tuple[str, ...] = (),
        kind: str = "critique",
    ) -> CritiqueMessage:
        if not correlation_id.strip():
            raise ValueError("correlation_id required")
        if not claim.strip():
            raise ValueError("claim required")
        if to_id not in set(allowed_outputs) and to_id != from_id:
            # self-notes allowed; otherwise must be on outputs allowlist
            raise PermissionError(
                f"critique edge denied: {from_id} → {to_id} not in outputs {list(allowed_outputs)}"
            )
        sev = (
            severity
            if isinstance(severity, CritiqueSeverity)
            else CritiqueSeverity(str(severity))
        )
        requires_hitl = sev is CritiqueSeverity.BLOCKER
        msg = CritiqueMessage(
            message_id=f"crit_{uuid4().hex[:12]}",
            correlation_id=correlation_id,
            from_id=from_id,
            to_id=to_id,
            severity=sev,
            claim=claim.strip(),
            artifact_ref=artifact_ref,
            evidence_refs=evidence_refs,
            kind=kind,
            requires_hitl=requires_hitl,
        )
        self._by_correlation.setdefault(correlation_id, []).append(msg)
        return msg

    def receive(
        self,
        *,
        correlation_id: str,
        to_id: str,
        allowed_inputs: tuple[str, ...] | list[str] | None = None,
    ) -> tuple[CritiqueMessage, ...]:
        messages = self._by_correlation.get(correlation_id, [])
        out: list[CritiqueMessage] = []
        allow = set(allowed_inputs) if allowed_inputs is not None else None
        for msg in messages:
            if msg.to_id != to_id:
                continue
            if allow is not None and msg.from_id not in allow and msg.from_id != to_id:
                continue
            out.append(msg)
        return tuple(out)

    def ack(self, message_id: str, by_agent_id: str) -> None:
        self._acks[message_id] = by_agent_id

    def unresolved_blockers(self, correlation_id: str) -> tuple[CritiqueMessage, ...]:
        return tuple(
            m
            for m in self._by_correlation.get(correlation_id, [])
            if m.severity is CritiqueSeverity.BLOCKER
            and m.kind != "resolution"
            and m.message_id not in self._acks
        )

    def resolve_dispute(
        self,
        *,
        correlation_id: str,
        judge_id: str,
        target_message_id: str,
        resolution: str,
        confirm_hitl: bool = False,
    ) -> CritiqueMessage:
        """Judge (or HiTL-confirmed path) emits a resolution message."""
        parent = None
        for msg in self._by_correlation.get(correlation_id, []):
            if msg.message_id == target_message_id:
                parent = msg
                break
        if parent is None:
            raise LookupError(f"critique not found: {target_message_id}")
        if parent.requires_hitl and not confirm_hitl:
            raise PermissionError("blocker requires HiTL confirm before resolution")
        resolution_msg = CritiqueMessage(
            message_id=f"res_{uuid4().hex[:12]}",
            correlation_id=correlation_id,
            from_id=judge_id,
            to_id=parent.from_id,
            severity=CritiqueSeverity.MINOR,
            claim=resolution,
            artifact_ref=parent.artifact_ref,
            evidence_refs=parent.evidence_refs + (parent.message_id,),
            kind="resolution",
            requires_hitl=False,
        )
        self._by_correlation.setdefault(correlation_id, []).append(resolution_msg)
        self._acks[parent.message_id] = judge_id
        return resolution_msg
