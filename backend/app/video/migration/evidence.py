"""Append-only evidence, release-gate conjunctions, and rollback verification.

This module is deliberately a local decision recorder.  It never changes runtime
maturity or activation, executes a provider, or performs a Git revert.  A human
or a separately authorized Git process supplies the rollback result; this module
only proves that the result matches the recorded migration predecessor and
change-set digests.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from threading import RLock
from typing import Final, Protocol

from app.video.migration.canonical import canonicalize_json, redact_diagnostic, sort_findings
from app.video.migration.contracts import (
    CanonicalRecord,
    ImportFinding,
    MigrationEvidence,
    MigrationResult,
    SourceSnapshot,
)

EVIDENCE_SCHEMA_VERSION: Final[str] = "1.0"
REQUIRED_COMPLETION_GATES: Final[tuple[str, ...]] = (
    "source_intake",
    "corpus_integrity",
    "agent_mapping",
    "agent_specifications",
    "workflow_adaptation",
    "local_knowledge",
    "standalone_verification",
    "documentation",
    "migration_evidence",
)
BLOCKING_CATEGORIES: Final[tuple[str, ...]] = (
    "licensing",
    "mapping",
    "workflow",
    "security",
    "standalone",
)


class CompletionGateName(StrEnum):
    """The executable gates required before a Video Pack completion claim."""

    SOURCE_INTAKE = "source_intake"
    CORPUS_INTEGRITY = "corpus_integrity"
    AGENT_MAPPING = "agent_mapping"
    AGENT_SPECIFICATIONS = "agent_specifications"
    WORKFLOW_ADAPTATION = "workflow_adaptation"
    LOCAL_KNOWLEDGE = "local_knowledge"
    STANDALONE_VERIFICATION = "standalone_verification"
    DOCUMENTATION = "documentation"
    MIGRATION_EVIDENCE = "migration_evidence"


CompletionGate = CompletionGateName


class EvidenceAppendError(ValueError):
    """Raised when an append-only evidence store cannot retain a record."""


class CompletionClaimError(ValueError):
    """Raised when a completion claim is not an executable claim."""


class RollbackVerificationError(ValueError):
    """Raised for malformed rollback verification inputs."""


def _text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string.")
    return value.strip()


def _optional_text(value: object, name: str) -> str | None:
    if value is None:
        return None
    return _text(value, name)


def _texts(values: Iterable[object], name: str) -> tuple[str, ...]:
    normalized = tuple(redact_diagnostic(value) for value in values)
    if any(not value for value in normalized):
        raise ValueError(f"{name} must contain only non-empty strings.")
    if len(normalized) != len(set(normalized)):
        raise ValueError(f"{name} must not contain duplicates.")
    return normalized


def _sha256(value: object, name: str) -> str:
    normalized = _text(value, name).casefold()
    if len(normalized) != 64 or any(
        character not in "0123456789abcdef" for character in normalized
    ):
        raise ValueError(f"{name} must be a SHA-256 hexadecimal digest.")
    return normalized


def _optional_sha256(value: object, name: str) -> str | None:
    if value is None:
        return None
    return _sha256(value, name)


def _result(value: MigrationResult | str) -> MigrationResult:
    try:
        return MigrationResult(value)
    except ValueError as error:
        raise ValueError("result must be pass, fail, blocked, or no_change.") from error


@dataclass(frozen=True, slots=True)
class ExecutableGateResult(CanonicalRecord):
    """One named, machine-produced completion-gate result.

    A passing boolean without an evidence reference is intentionally insufficient:
    completion claims must point to an executable result rather than documentation
    prose.
    """

    gate: str
    result: MigrationResult
    evidence_ref: str = ""
    executable: bool = True
    blockers: tuple[str, ...] = ()
    findings: tuple[ImportFinding, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "gate", _text(self.gate, "gate").casefold())
        object.__setattr__(self, "result", _result(self.result))
        object.__setattr__(self, "evidence_ref", redact_diagnostic(self.evidence_ref))
        if not isinstance(self.executable, bool):
            raise TypeError("executable must be a boolean.")
        object.__setattr__(self, "blockers", _texts(self.blockers, "blockers"))
        findings = tuple(self.findings)
        if any(not isinstance(finding, ImportFinding) for finding in findings):
            raise TypeError("findings must contain ImportFinding records.")
        object.__setattr__(self, "findings", sort_findings(findings))

    @property
    def passed(self) -> bool:
        """Return true only for an executable, evidenced, unblocked pass."""
        return (
            self.result is MigrationResult.PASS
            and self.executable
            and bool(self.evidence_ref)
            and not self.blockers
        )

    @property
    def is_pass(self) -> bool:
        """Compatibility alias for callers using report-style terminology."""
        return self.passed


# Concise aliases for integrations that call these records gate or release results.
CompletionGateResult = ExecutableGateResult
ExecutableCompletionGate = ExecutableGateResult
ReleaseGateResult = ExecutableGateResult


@dataclass(frozen=True, slots=True)
class CompletionClaim(CanonicalRecord):
    """A published completion assertion linked to executable evidence."""

    claim_id: str
    statement: str
    executable_evidence: tuple[str, ...] = ()
    documentation_only: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "claim_id", _text(self.claim_id, "claim_id"))
        object.__setattr__(self, "statement", redact_diagnostic(_text(self.statement, "statement")))
        object.__setattr__(
            self, "executable_evidence", _texts(self.executable_evidence, "executable_evidence")
        )
        if not isinstance(self.documentation_only, bool):
            raise TypeError("documentation_only must be a boolean.")

    @property
    def is_executable(self) -> bool:
        """Return whether the claim names at least one executable evidence result."""
        return bool(self.executable_evidence) and not self.documentation_only


@dataclass(frozen=True, slots=True)
class CompletionClaimReport(CanonicalRecord):
    """Validation result for a completion claim independent of release gates."""

    result: MigrationResult
    claim: CompletionClaim
    findings: tuple[ImportFinding, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "result", _result(self.result))
        if not isinstance(self.claim, CompletionClaim):
            raise TypeError("claim must be a CompletionClaim.")
        findings = tuple(self.findings)
        if any(not isinstance(finding, ImportFinding) for finding in findings):
            raise TypeError("findings must contain ImportFinding records.")
        object.__setattr__(self, "findings", sort_findings(findings))

    @property
    def is_valid(self) -> bool:
        """Return whether the claim has executable supporting evidence."""
        return self.result is MigrationResult.PASS and not self.findings


def _coerce_claim(
    value: CompletionClaim | Mapping[str, object] | str | None,
) -> CompletionClaim | None:
    if value is None or isinstance(value, CompletionClaim):
        return value
    if isinstance(value, str):
        return CompletionClaim("completion-claim", value)
    if isinstance(value, Mapping):
        refs = value.get("executable_evidence", value.get("evidence_refs", ()))
        if isinstance(refs, str):
            refs = (refs,)
        if not isinstance(refs, Iterable):
            refs = ()
        return CompletionClaim(
            claim_id=str(value.get("claim_id", "completion-claim")),
            statement=str(value.get("statement", value.get("claim", ""))),
            executable_evidence=tuple(refs),
            documentation_only=bool(value.get("documentation_only", False)),
        )
    raise TypeError("completion_claim must be a CompletionClaim, mapping, string, or None.")


def validate_completion_claim(
    claim: CompletionClaim | Mapping[str, object] | str,
    available_evidence: Iterable[str] = (),
) -> CompletionClaimReport:
    """Reject prose-only claims and claims that cite no executable result."""
    normalized = _coerce_claim(claim)
    if normalized is None:
        raise CompletionClaimError("A completion claim is required.")
    available = set(_texts(available_evidence, "available_evidence"))
    findings: list[ImportFinding] = []
    if normalized.documentation_only:
        findings.append(
            ImportFinding(
                "completion_claim_documentation_only",
                field="documentation_only",
                message="Completion claims cannot rely only on documentation prose.",
            )
        )
    if not normalized.executable_evidence:
        findings.append(
            ImportFinding(
                "completion_claim_requires_executable_evidence",
                field="executable_evidence",
                message="Completion claims require executable evidence references.",
            )
        )
    if available:
        for reference in normalized.executable_evidence:
            if reference not in available:
                findings.append(
                    ImportFinding(
                        "completion_claim_unknown_evidence",
                        path=reference,
                        field="executable_evidence",
                        message="The completion claim references no retained executable result.",
                    )
                )
    return CompletionClaimReport(
        result=MigrationResult.PASS if not findings else MigrationResult.BLOCKED,
        claim=normalized,
        findings=tuple(findings),
    )


def _coerce_gate(value: object, name: str | None = None) -> ExecutableGateResult:
    if isinstance(value, ExecutableGateResult):
        return value
    if isinstance(value, Mapping):
        gate = str(value.get("gate", value.get("name", name or "")))
        raw_result = value.get("result")
        if raw_result is None:
            raw_result = (
                MigrationResult.PASS if value.get("passed") is True else MigrationResult.FAIL
            )
        raw_ref = value.get("evidence_ref", value.get("evidence", ""))
        raw_blockers = value.get("blockers", ())
        raw_findings = value.get("findings", ())
        if isinstance(raw_blockers, str):
            raw_blockers = (raw_blockers,)
        if not isinstance(raw_blockers, Iterable):
            raw_blockers = ()
        findings = tuple(raw_findings) if isinstance(raw_findings, Iterable) else ()
        return ExecutableGateResult(
            gate=gate,
            result=_result(raw_result),
            evidence_ref=str(raw_ref),
            executable=bool(value.get("executable", True)),
            blockers=tuple(raw_blockers),
            findings=findings,
        )
    if isinstance(value, bool):
        # A bare boolean has no executable evidence and therefore cannot complete.
        return ExecutableGateResult(
            gate=name or "",
            result=MigrationResult.PASS if value else MigrationResult.FAIL,
            executable=False,
        )
    raise TypeError("Completion gates must be ExecutableGateResult records or mappings.")


def _coerce_gates(
    gates: Mapping[str, object] | Iterable[ExecutableGateResult | Mapping[str, object]],
) -> tuple[ExecutableGateResult, ...]:
    if isinstance(gates, Mapping):
        normalized = tuple(_coerce_gate(value, str(name)) for name, value in gates.items())
    else:
        normalized = tuple(_coerce_gate(value) for value in gates)
    names = tuple(gate.gate for gate in normalized)
    if len(names) != len(set(names)):
        raise ValueError("Completion gates must contain one result per gate name.")
    return tuple(sorted(normalized, key=lambda gate: gate.gate))


@dataclass(frozen=True, slots=True)
class CompletionReport(CanonicalRecord):
    """The all-gates release decision; no runtime state is changed."""

    result: MigrationResult
    gates: tuple[ExecutableGateResult, ...]
    blockers: tuple[str, ...] = ()
    residual_risks: tuple[str, ...] = ()
    claim: CompletionClaimReport | None = None
    findings: tuple[ImportFinding, ...] = ()
    schema_version: str = EVIDENCE_SCHEMA_VERSION

    def __post_init__(self) -> None:
        object.__setattr__(self, "result", _result(self.result))
        gates = tuple(self.gates)
        if any(not isinstance(gate, ExecutableGateResult) for gate in gates):
            raise TypeError("gates must contain ExecutableGateResult records.")
        names = tuple(gate.gate for gate in gates)
        if len(names) != len(set(names)):
            raise ValueError("gates must contain unique names.")
        object.__setattr__(self, "gates", tuple(sorted(gates, key=lambda gate: gate.gate)))
        object.__setattr__(self, "blockers", _texts(self.blockers, "blockers"))
        object.__setattr__(self, "residual_risks", _texts(self.residual_risks, "residual_risks"))
        findings = tuple(self.findings)
        if any(not isinstance(finding, ImportFinding) for finding in findings):
            raise TypeError("findings must contain ImportFinding records.")
        object.__setattr__(self, "findings", sort_findings(findings))
        if self.claim is not None and not isinstance(self.claim, CompletionClaimReport):
            raise TypeError("claim must be a CompletionClaimReport or None.")
        if self.schema_version != EVIDENCE_SCHEMA_VERSION:
            raise ValueError("Unsupported completion report schema version.")

    @property
    def missing_gates(self) -> tuple[str, ...]:
        """Return required gates with no executable result."""
        present = {gate.gate for gate in self.gates}
        return tuple(name for name in REQUIRED_COMPLETION_GATES if name not in present)

    @property
    def failed_gates(self) -> tuple[str, ...]:
        """Return required gates that did not pass executable validation."""
        return tuple(
            name
            for name in REQUIRED_COMPLETION_GATES
            if next((gate for gate in self.gates if gate.gate == name), None) is not None
            and not next(gate for gate in self.gates if gate.gate == name).passed
        )

    @property
    def is_complete(self) -> bool:
        """Return true only for the complete executable conjunction."""
        return (
            self.result is MigrationResult.PASS
            and not self.missing_gates
            and not self.failed_gates
            and not self.blockers
            and not self.findings
            and (self.claim is None or self.claim.is_valid)
        )

    @property
    def completion_gate_passed(self) -> bool:
        """Compatibility alias used by refresh and documentation consumers."""
        return self.is_complete

    @property
    def runtime_activation_changed(self) -> bool:
        """Completion evidence never changes runtime activation."""
        return False

    def to_dict(self) -> dict[str, object]:
        """Return a stable machine-readable completion decision."""
        return {
            "schema_version": self.schema_version,
            "result": self.result.value,
            "gates": [gate.to_dict() for gate in self.gates],
            "missing_gates": list(self.missing_gates),
            "failed_gates": list(self.failed_gates),
            "blockers": list(self.blockers),
            "residual_risks": list(self.residual_risks),
            "findings": [finding.to_dict() for finding in self.findings],
            "claim": self.claim.to_dict() if self.claim is not None else None,
            "runtime_activation_changed": self.runtime_activation_changed,
        }


def evaluate_completion(
    gates: Mapping[str, object] | Iterable[ExecutableGateResult | Mapping[str, object]],
    *,
    blockers: Iterable[str] = (),
    residual_risks: Iterable[str] = (),
    completion_claim: CompletionClaim | Mapping[str, object] | str | None = None,
) -> CompletionReport:
    """Evaluate every release gate as a conjunction and retain all blockers."""
    normalized_gates = _coerce_gates(gates)
    findings: list[ImportFinding] = []
    known_gate_names = set(REQUIRED_COMPLETION_GATES)
    for gate in normalized_gates:
        if gate.gate not in known_gate_names:
            findings.append(
                ImportFinding(
                    "completion_gate_unknown",
                    path=gate.gate,
                    field="gate",
                    message="Completion vectors may contain only required release gates.",
                )
            )
    normalized_blockers = list(_texts(blockers, "blockers"))
    for name in REQUIRED_COMPLETION_GATES:
        candidate_gate = next(
            (candidate for candidate in normalized_gates if candidate.gate == name), None
        )
        if candidate_gate is None:
            findings.append(
                ImportFinding(
                    "completion_gate_missing",
                    field="gates",
                    message=f"Required executable completion gate is missing: {name}.",
                )
            )
            continue
        if not candidate_gate.executable:
            findings.append(
                ImportFinding(
                    "completion_gate_not_executable",
                    path=name,
                    field="executable",
                    message="Completion gates must be backed by executable evidence.",
                )
            )
        if not candidate_gate.evidence_ref:
            findings.append(
                ImportFinding(
                    "completion_gate_evidence_missing",
                    path=name,
                    field="evidence_ref",
                    message="A passing completion gate requires an evidence reference.",
                )
            )
        if candidate_gate.result is not MigrationResult.PASS or candidate_gate.blockers:
            findings.append(
                ImportFinding(
                    "completion_gate_failed",
                    path=name,
                    field="result",
                    message="Every required completion gate must pass without blockers.",
                )
            )
        if candidate_gate.findings:
            findings.extend(candidate_gate.findings)
            findings.append(
                ImportFinding(
                    "completion_gate_findings",
                    path=name,
                    field="findings",
                    message="A completion gate with diagnostics cannot establish completion.",
                )
            )
        normalized_blockers.extend(candidate_gate.blockers)
    claim_report: CompletionClaimReport | None = None
    if completion_claim is not None:
        available = tuple(gate.evidence_ref for gate in normalized_gates if gate.evidence_ref)
        claim_report = validate_completion_claim(completion_claim, available)
        findings.extend(claim_report.findings)
    if normalized_blockers:
        findings.extend(
            ImportFinding(
                f"completion_blocker_{_blocker_code(blocker)}",
                field="blockers",
                message="An unresolved migration blocker prevents completion.",
            )
            for blocker in normalized_blockers
        )
    findings = list(sort_findings(findings))
    ready = not findings and not normalized_blockers
    result = MigrationResult.PASS if ready else MigrationResult.BLOCKED
    return CompletionReport(
        result=result,
        gates=normalized_gates,
        blockers=tuple(normalized_blockers),
        residual_risks=_texts(residual_risks, "residual_risks"),
        claim=claim_report,
        findings=tuple(findings),
    )


def _blocker_code(blocker: str) -> str:
    normalized = blocker.casefold()
    for category in BLOCKING_CATEGORIES:
        if category in normalized:
            return category
    return "unresolved"


class MigrationEvidenceStore(Protocol):
    """Append-only persistence seam for local migration evidence."""

    def append(self, record: MigrationEvidence) -> MigrationEvidence:
        """Append a new immutable record without replacing prior records."""

    def records(self) -> tuple[MigrationEvidence, ...]:
        """Return records in append order."""


class InMemoryMigrationEvidenceStore:
    """Thread-safe append-only evidence store used by local tooling and tests."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._records: list[MigrationEvidence] = []
        self._ids: set[str] = set()

    def append(self, record: MigrationEvidence) -> MigrationEvidence:
        if not isinstance(record, MigrationEvidence):
            raise TypeError("Only MigrationEvidence records may be appended.")
        with self._lock:
            if record.evidence_id in self._ids:
                raise EvidenceAppendError("Migration evidence IDs are immutable and unique.")
            self._ids.add(record.evidence_id)
            self._records.append(record)
            return record

    def records(self) -> tuple[MigrationEvidence, ...]:
        with self._lock:
            return tuple(self._records)

    @property
    def latest(self) -> MigrationEvidence | None:
        """Return the newest record without permitting replacement."""
        with self._lock:
            return self._records[-1] if self._records else None


class JsonlMigrationEvidenceStore:
    """Canonical newline-delimited evidence log with append-only semantics."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self._lock = RLock()

    def append(self, record: MigrationEvidence) -> MigrationEvidence:
        """Append one canonical JSON object and reject malformed prior content."""
        if not isinstance(record, MigrationEvidence):
            raise TypeError("Only MigrationEvidence records may be appended.")
        with self._lock:
            existing = self.raw_records()
            if any(item.get("evidence_id") == record.evidence_id for item in existing):
                raise EvidenceAppendError("Migration evidence IDs are immutable and unique.")
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8", newline="\n") as stream:
                stream.write(canonicalize_json(record))
                stream.write("\n")
        return record

    def raw_records(self) -> tuple[dict[str, object], ...]:
        """Return canonical JSON objects without reconstructing mutable records."""
        if not self.path.exists():
            return ()
        records: list[dict[str, object]] = []
        try:
            lines = self.path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeError) as error:
            raise EvidenceAppendError("Migration evidence log is unreadable.") from error
        for line in lines:
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as error:
                raise EvidenceAppendError(
                    "Migration evidence log contains invalid JSON."
                ) from error
            if not isinstance(value, dict) or not isinstance(value.get("evidence_id"), str):
                raise EvidenceAppendError("Migration evidence log contains an invalid record.")
            records.append(value)
        return tuple(records)

    def records(self) -> tuple[MigrationEvidence, ...]:
        """Deserialize the canonical log into frozen typed records for inspection."""
        return tuple(_evidence_from_raw(value) for value in self.raw_records())

    @property
    def latest(self) -> MigrationEvidence | None:
        """Return the newest typed record without permitting replacement."""
        records = self.records()
        return records[-1] if records else None


def _raw_texts(value: object, name: str) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise EvidenceAppendError(f"Migration evidence field {name} must be a JSON array.")
    if any(not isinstance(item, str) for item in value):
        raise EvidenceAppendError(f"Migration evidence field {name} must contain strings.")
    return tuple(value)


def _evidence_from_raw(value: Mapping[str, object]) -> MigrationEvidence:
    """Reconstruct one immutable record from a validated canonical JSON object."""
    raw_snapshot = value.get("source_snapshot")
    if not isinstance(raw_snapshot, Mapping):
        raise EvidenceAppendError("Migration evidence source_snapshot is invalid.")
    raw_recorded_at = raw_snapshot.get("recorded_at")
    raw_phase_at = value.get("recorded_at")
    if not isinstance(raw_recorded_at, str) or not isinstance(raw_phase_at, str):
        raise EvidenceAppendError("Migration evidence timestamps are invalid.")
    try:
        snapshot_at = datetime.fromisoformat(raw_recorded_at.replace("Z", "+00:00"))
        phase_at = datetime.fromisoformat(raw_phase_at.replace("Z", "+00:00"))
    except ValueError as error:
        raise EvidenceAppendError("Migration evidence timestamps are invalid.") from error
    try:
        return MigrationEvidence(
            evidence_id=_text(value.get("evidence_id"), "evidence_id"),
            phase=_text(value.get("phase"), "phase"),
            result=_result(_text(value.get("result"), "result")),
            commands=_raw_texts(value.get("commands"), "commands"),
            results=_raw_texts(value.get("results"), "results"),
            source_snapshot=SourceSnapshot(
                source_repository=_text(raw_snapshot.get("source_repository"), "source_repository"),
                source_commit=_text(raw_snapshot.get("source_commit"), "source_commit"),
                source_root=_text(raw_snapshot.get("source_root"), "source_root"),
                recorded_at=snapshot_at,
            ),
            correlation_id=_text(value.get("correlation_id"), "correlation_id"),
            recorded_at=phase_at,
            blockers=_raw_texts(value.get("blockers"), "blockers"),
            residual_risks=_raw_texts(value.get("residual_risks"), "residual_risks"),
            change_set_ref=_text(value.get("change_set_ref"), "change_set_ref"),
            pre_import_manifest_digest=_optional_sha256(
                value.get("pre_import_manifest_digest"), "pre_import_manifest_digest"
            ),
            corpus_manifest_digest=_optional_sha256(
                value.get("corpus_manifest_digest"), "corpus_manifest_digest"
            ),
            mapping_review_ref=_optional_text(
                value.get("mapping_review_ref"), "mapping_review_ref"
            ),
            standalone_result=_optional_text(value.get("standalone_result"), "standalone_result"),
            documentation_check_result=_optional_text(
                value.get("documentation_check_result"), "documentation_check_result"
            ),
            review_references=_raw_texts(value.get("review_references", []), "review_references"),
            release_outcomes=_raw_texts(value.get("release_outcomes", []), "release_outcomes"),
            change_set_digest=_optional_sha256(value.get("change_set_digest"), "change_set_digest"),
        )
    except (TypeError, ValueError) as error:
        raise EvidenceAppendError("Migration evidence log contains an invalid record.") from error


FileMigrationEvidenceStore = JsonlMigrationEvidenceStore


class MigrationEvidenceRecorder:
    """Create and append immutable phase, completion, and rollback evidence."""

    def __init__(self, store: MigrationEvidenceStore) -> None:
        self.store = store

    def record_phase(
        self,
        *,
        evidence_id: str,
        phase: str,
        source_snapshot: SourceSnapshot,
        correlation_id: str,
        recorded_at: datetime,
        commands: Sequence[str],
        results: Sequence[str],
        change_set_ref: str,
        result: MigrationResult | str = MigrationResult.PASS,
        blockers: Sequence[str] = (),
        residual_risks: Sequence[str] = (),
        review_references: Sequence[str] = (),
        release_outcomes: Sequence[str] = (),
        pre_import_manifest_digest: str | None = None,
        corpus_manifest_digest: str | None = None,
        mapping_review_ref: str | None = None,
        standalone_result: str | None = None,
        documentation_check_result: str | None = None,
        change_set_digest: str | None = None,
    ) -> MigrationEvidence:
        """Append one phase; any unresolved blocker records the phase as blocked."""
        normalized_blockers = _texts(blockers, "blockers")
        phase_result = MigrationResult.BLOCKED if normalized_blockers else _result(result)
        record = MigrationEvidence(
            evidence_id=evidence_id,
            phase=phase,
            result=phase_result,
            commands=tuple(commands),
            results=tuple(results),
            source_snapshot=source_snapshot,
            correlation_id=correlation_id,
            recorded_at=recorded_at,
            blockers=normalized_blockers,
            residual_risks=_texts(residual_risks, "residual_risks"),
            change_set_ref=change_set_ref,
            pre_import_manifest_digest=pre_import_manifest_digest,
            corpus_manifest_digest=corpus_manifest_digest,
            mapping_review_ref=mapping_review_ref,
            standalone_result=standalone_result,
            documentation_check_result=documentation_check_result,
            review_references=_texts(review_references, "review_references"),
            release_outcomes=_texts(release_outcomes, "release_outcomes"),
            change_set_digest=change_set_digest,
        )
        return self.store.append(record)

    def record_completion(
        self,
        *,
        evidence_id: str,
        source_snapshot: SourceSnapshot,
        correlation_id: str,
        recorded_at: datetime,
        change_set_ref: str,
        completion: CompletionReport,
        commands: Sequence[str],
        results: Sequence[str],
        pre_import_manifest_digest: str | None = None,
        corpus_manifest_digest: str | None = None,
        review_references: Sequence[str] = (),
        change_set_digest: str | None = None,
    ) -> MigrationEvidence:
        """Append completion evidence, preserving a blocked conjunction as blocked."""
        if not isinstance(completion, CompletionReport):
            raise TypeError("completion must be a CompletionReport.")
        gate_outcomes = tuple(
            f"{gate.gate}:{gate.result.value}:{'pass' if gate.passed else 'blocked'}"
            for gate in completion.gates
        )
        blockers = completion.blockers or tuple(
            finding.code for finding in _completion_findings(completion)
        )
        return self.record_phase(
            evidence_id=evidence_id,
            phase="completion",
            source_snapshot=source_snapshot,
            correlation_id=correlation_id,
            recorded_at=recorded_at,
            commands=commands,
            results=results,
            change_set_ref=change_set_ref,
            result=completion.result,
            blockers=blockers,
            residual_risks=completion.residual_risks,
            review_references=review_references,
            release_outcomes=gate_outcomes,
            pre_import_manifest_digest=pre_import_manifest_digest,
            corpus_manifest_digest=corpus_manifest_digest,
            change_set_digest=change_set_digest,
        )

    def records(self) -> tuple[MigrationEvidence, ...]:
        """Expose the append-only typed store snapshot."""
        return self.store.records()


def _completion_findings(completion: CompletionReport) -> tuple[ImportFinding, ...]:
    findings: list[ImportFinding] = list(completion.findings)
    for name in completion.missing_gates:
        findings.append(ImportFinding("completion_gate_missing", path=name))
    for name in completion.failed_gates:
        findings.append(ImportFinding("completion_gate_failed", path=name))
    return tuple(sort_findings(findings))


@dataclass(frozen=True, slots=True)
class RuntimePosture(CanonicalRecord):
    """Runtime state captured only to prove rollback did not alter it."""

    maturity: str
    activation_enabled: bool

    def __post_init__(self) -> None:
        object.__setattr__(self, "maturity", _text(self.maturity, "maturity"))
        if not isinstance(self.activation_enabled, bool):
            raise TypeError("activation_enabled must be a boolean.")


@dataclass(frozen=True, slots=True)
class RollbackRequest(CanonicalRecord):
    """Human-authorized result supplied after a Git revert attempt."""

    change_set_ref: str
    predecessor_manifest_digest: str
    restored_manifest_digest: str
    authorization_ref: str
    authorized: bool = False
    authorized_by: str = ""
    git_revert_applied: bool = False
    revert_command: str = "git revert"
    change_set_digest: str | None = None
    current_manifest_digest: str | None = None
    runtime_before: RuntimePosture | None = None
    runtime_after: RuntimePosture | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "change_set_ref", _text(self.change_set_ref, "change_set_ref"))
        object.__setattr__(
            self,
            "predecessor_manifest_digest",
            _sha256(self.predecessor_manifest_digest, "predecessor_manifest_digest"),
        )
        object.__setattr__(
            self,
            "restored_manifest_digest",
            _sha256(self.restored_manifest_digest, "restored_manifest_digest"),
        )
        object.__setattr__(
            self, "authorization_ref", _text(self.authorization_ref, "authorization_ref")
        )
        if not isinstance(self.authorized, bool):
            raise TypeError("authorized must be a boolean.")
        object.__setattr__(self, "authorized_by", redact_diagnostic(self.authorized_by))
        if not isinstance(self.git_revert_applied, bool):
            raise TypeError("git_revert_applied must be a boolean.")
        object.__setattr__(self, "revert_command", _text(self.revert_command, "revert_command"))
        if self.change_set_digest is not None:
            object.__setattr__(
                self, "change_set_digest", _sha256(self.change_set_digest, "change_set_digest")
            )
        if self.current_manifest_digest is not None:
            object.__setattr__(
                self,
                "current_manifest_digest",
                _sha256(self.current_manifest_digest, "current_manifest_digest"),
            )
        if self.runtime_before is not None and not isinstance(self.runtime_before, RuntimePosture):
            raise TypeError("runtime_before must be RuntimePosture or None.")
        if self.runtime_after is not None and not isinstance(self.runtime_after, RuntimePosture):
            raise TypeError("runtime_after must be RuntimePosture or None.")


@dataclass(frozen=True, slots=True)
class RollbackVerificationReport(CanonicalRecord):
    """Read-only verification of an authorized, exact predecessor restoration."""

    result: MigrationResult
    evidence_id: str
    change_set_ref: str
    predecessor_manifest_digest: str
    restored_manifest_digest: str
    runtime_maturity_unchanged: bool
    runtime_activation_unchanged: bool
    findings: tuple[ImportFinding, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "result", _result(self.result))
        object.__setattr__(self, "evidence_id", _text(self.evidence_id, "evidence_id"))
        object.__setattr__(self, "change_set_ref", _text(self.change_set_ref, "change_set_ref"))
        object.__setattr__(
            self,
            "predecessor_manifest_digest",
            _sha256(self.predecessor_manifest_digest, "predecessor_manifest_digest"),
        )
        object.__setattr__(
            self,
            "restored_manifest_digest",
            _sha256(self.restored_manifest_digest, "restored_manifest_digest"),
        )
        if not isinstance(self.runtime_maturity_unchanged, bool):
            raise TypeError("runtime_maturity_unchanged must be a boolean.")
        if not isinstance(self.runtime_activation_unchanged, bool):
            raise TypeError("runtime_activation_unchanged must be a boolean.")
        findings = tuple(self.findings)
        if any(not isinstance(finding, ImportFinding) for finding in findings):
            raise TypeError("findings must contain ImportFinding records.")
        object.__setattr__(self, "findings", sort_findings(findings))

    @property
    def is_valid(self) -> bool:
        """Return true only when the exact authorized rollback was verified."""
        return self.result is MigrationResult.PASS and not self.findings

    @property
    def runtime_activation_changed(self) -> bool:
        """Expose the safety invariant in positive wording for callers."""
        return not self.runtime_activation_unchanged


def verify_authorized_rollback(
    evidence: MigrationEvidence,
    request: RollbackRequest,
) -> RollbackVerificationReport:
    """Verify Git-revert authorization and exact digest restoration without mutation."""
    if not isinstance(evidence, MigrationEvidence):
        raise RollbackVerificationError("evidence must be a MigrationEvidence record.")
    if not isinstance(request, RollbackRequest):
        raise RollbackVerificationError("request must be a RollbackRequest record.")
    findings: list[ImportFinding] = []
    if not request.authorized or not request.authorization_ref or not request.authorized_by:
        findings.append(
            ImportFinding(
                "rollback_authorization_required",
                field="authorization_ref",
                message="Rollback requires explicit human authorization and reviewer identity.",
            )
        )
    if request.revert_command.casefold() != "git revert":
        findings.append(
            ImportFinding(
                "rollback_git_revert_required",
                field="revert_command",
                message="Rollback must be an authorized Git revert of the recorded change set.",
            )
        )
    if not request.git_revert_applied:
        findings.append(
            ImportFinding(
                "rollback_not_applied",
                field="git_revert_applied",
                message="The authorized Git revert result was not recorded as applied.",
            )
        )
    if request.change_set_ref != evidence.change_set_ref:
        findings.append(
            ImportFinding(
                "rollback_change_set_mismatch",
                field="change_set_ref",
                message="Rollback must target the evidence-recorded migration change set.",
            )
        )
    if evidence.change_set_digest is None:
        findings.append(
            ImportFinding(
                "rollback_change_set_digest_missing",
                field="change_set_digest",
                message="Rollback requires a recorded migration change-set digest.",
            )
        )
    elif request.change_set_digest != evidence.change_set_digest:
        findings.append(
            ImportFinding(
                "rollback_change_set_digest_mismatch",
                field="change_set_digest",
                message="Rollback change-set digest does not match recorded evidence.",
            )
        )
    if evidence.pre_import_manifest_digest is None:
        findings.append(
            ImportFinding(
                "rollback_predecessor_digest_missing",
                field="pre_import_manifest_digest",
                message="Rollback requires the recorded pre-import manifest digest.",
            )
        )
    elif request.predecessor_manifest_digest != evidence.pre_import_manifest_digest:
        findings.append(
            ImportFinding(
                "rollback_predecessor_digest_mismatch",
                field="predecessor_manifest_digest",
                message="Rollback predecessor digest does not match recorded evidence.",
            )
        )
    if request.restored_manifest_digest != request.predecessor_manifest_digest:
        findings.append(
            ImportFinding(
                "rollback_restoration_digest_mismatch",
                field="restored_manifest_digest",
                message="Rollback must restore the exact recorded predecessor digest.",
            )
        )
    runtime_maturity_unchanged = (
        request.runtime_before is not None
        and request.runtime_after is not None
        and request.runtime_before.maturity == request.runtime_after.maturity
    )
    runtime_activation_unchanged = (
        request.runtime_before is not None
        and request.runtime_after is not None
        and request.runtime_before.activation_enabled == request.runtime_after.activation_enabled
    )
    if request.runtime_before is None and request.runtime_after is None:
        runtime_maturity_unchanged = True
        runtime_activation_unchanged = True
    elif request.runtime_before is None or request.runtime_after is None:
        findings.append(
            ImportFinding(
                "rollback_runtime_posture_missing",
                field="runtime_before",
                message="Rollback runtime posture must be captured before and after verification.",
            )
        )
    elif not runtime_maturity_unchanged or not runtime_activation_unchanged:
        findings.append(
            ImportFinding(
                "rollback_runtime_posture_changed",
                field="runtime",
                message="Rollback verification cannot change runtime maturity or activation.",
            )
        )
    return RollbackVerificationReport(
        result=MigrationResult.PASS if not findings else MigrationResult.BLOCKED,
        evidence_id=evidence.evidence_id,
        change_set_ref=evidence.change_set_ref,
        predecessor_manifest_digest=request.predecessor_manifest_digest,
        restored_manifest_digest=request.restored_manifest_digest,
        runtime_maturity_unchanged=runtime_maturity_unchanged,
        runtime_activation_unchanged=runtime_activation_unchanged,
        findings=tuple(findings),
    )


verify_rollback = verify_authorized_rollback
check_rollback = verify_authorized_rollback


def append_phase_evidence(
    store: MigrationEvidenceStore, record: MigrationEvidence
) -> MigrationEvidence:
    """Append a pre-built canonical phase record through the immutable store seam."""
    return store.append(record)


def append_rollback_evidence(
    recorder: MigrationEvidenceRecorder,
    *,
    evidence_id: str,
    original: MigrationEvidence,
    verification: RollbackVerificationReport,
    recorded_at: datetime,
    correlation_id: str,
    commands: Sequence[str] = ("git revert",),
) -> MigrationEvidence:
    """Append rollback verification evidence while retaining the original predecessor link."""
    return recorder.record_phase(
        evidence_id=evidence_id,
        phase="rollback",
        source_snapshot=original.source_snapshot,
        correlation_id=correlation_id,
        recorded_at=recorded_at,
        commands=commands,
        results=(verification.result.value,),
        change_set_ref=original.change_set_ref,
        result=verification.result,
        blockers=tuple(finding.code for finding in verification.findings),
        residual_risks=original.residual_risks,
        review_references=original.review_references,
        release_outcomes=("runtime_maturity_unchanged", "runtime_activation_unchanged"),
        pre_import_manifest_digest=original.pre_import_manifest_digest,
        corpus_manifest_digest=original.corpus_manifest_digest,
        change_set_digest=original.change_set_digest,
    )
