"""Frozen, explicitly typed records for the local Video_Pack migration."""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum

from app.video.migration.canonical import (
    canonicalize_json,
    digest_json,
    redact_diagnostic,
    sort_findings,
    to_canonical_data,
)
from app.video.migration.paths import normalize_relative_path

_SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


class ImportMode(StrEnum):
    """Supported planner modes; neither mode grants network capability."""

    DRY_RUN = "dry_run"
    WRITE = "write"


class MigrationResult(StrEnum):
    """Stable result values used by migration reports and evidence."""

    PASS = "pass"
    FAIL = "fail"
    BLOCKED = "blocked"
    NO_CHANGE = "no_change"


class MappingStatus(StrEnum):
    """Reviewed relationship between a common agent and source roles."""

    EXACT = "exact"
    COMPOSITE = "composite"
    RELATED = "related"
    COMMON_ONLY = "common_only"


class ReviewResult(StrEnum):
    """Review outcomes accepted by local migration gates."""

    PASS = "pass"
    FAIL = "fail"
    BLOCKED = "blocked"


def _nonblank(value: str, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string.")
    if "\x00" in value or "\n" in value or "\r" in value:
        raise ValueError(f"{name} contains an invalid control character.")
    return value.strip()


def _safe_path(value: str, name: str) -> str:
    try:
        return normalize_relative_path(_nonblank(value, name))
    except (TypeError, ValueError) as error:
        raise ValueError(f"{name} must be a safe relative path.") from error


def _sequence(values: Iterable[str], name: str) -> tuple[str, ...]:
    normalized = tuple(_nonblank(value, name) for value in values)
    if len(normalized) != len(set(normalized)):
        raise ValueError(f"{name} must not contain duplicates.")
    return normalized


def _path_sequence(values: Iterable[str], name: str) -> tuple[str, ...]:
    normalized = tuple(_safe_path(value, name) for value in values)
    if len(normalized) != len(set(normalized)):
        raise ValueError(f"{name} must not contain duplicate paths.")
    return normalized


def _sha256(value: str, name: str = "sha256") -> str:
    normalized = _nonblank(value, name).casefold()
    if _SHA256_PATTERN.fullmatch(normalized) is None:
        raise ValueError(f"{name} must be a lowercase SHA-256 hexadecimal digest.")
    return normalized


def _size(value: int, name: str = "size_bytes") -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{name} must be a non-negative integer.")
    return value


def _timestamp(value: datetime, name: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None:
        raise ValueError(f"{name} must be a timezone-aware UTC timestamp.")
    return value.astimezone(UTC)


def _review_result(value: str) -> str:
    try:
        return ReviewResult(value).value
    except ValueError as error:
        raise ValueError("Review result must be pass, fail, or blocked.") from error


class CanonicalRecord:
    """Shared canonical projection methods for every migration record."""

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-compatible projection with no source-body fields."""
        projected = to_canonical_data(self)
        if not isinstance(projected, dict):
            raise TypeError("Migration records must project to JSON objects.")
        return projected

    def canonical_json(self) -> str:
        """Return the stable UTF-8 JSON text for this record."""
        return canonicalize_json(self)

    def digest(self) -> str:
        """Return the lowercase SHA-256 digest of this canonical record."""
        return digest_json(self)


@dataclass(frozen=True, slots=True)
class HistoricalProvenance(CanonicalRecord):
    """Minimal source metadata retained without copying source content."""

    repository: str
    commit: str
    path: str
    license_status: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "repository", _nonblank(self.repository, "repository"))
        object.__setattr__(self, "commit", _nonblank(self.commit, "commit"))
        object.__setattr__(self, "path", _safe_path(self.path, "path"))
        object.__setattr__(self, "license_status", _nonblank(self.license_status, "license_status"))


@dataclass(frozen=True, slots=True)
class SourceSnapshot(CanonicalRecord):
    """Pinned source revision recorded before any Video_Pack mutation."""

    source_repository: str
    source_commit: str
    source_root: str
    recorded_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "source_repository", _nonblank(self.source_repository, "source_repository")
        )
        object.__setattr__(self, "source_commit", _nonblank(self.source_commit, "source_commit"))
        object.__setattr__(self, "source_root", _nonblank(self.source_root, "source_root"))
        object.__setattr__(self, "recorded_at", _timestamp(self.recorded_at, "recorded_at"))


@dataclass(frozen=True, slots=True)
class ApprovedImportFile(CanonicalRecord):
    """One exact, reviewed source-to-corpus file admission."""

    source_path: str
    destination_path: str
    size_bytes: int
    sha256: str
    original_repository: str
    original_commit: str
    original_path: str
    license_status: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "source_path", _safe_path(self.source_path, "source_path"))
        object.__setattr__(
            self, "destination_path", _safe_path(self.destination_path, "destination_path")
        )
        object.__setattr__(self, "size_bytes", _size(self.size_bytes))
        object.__setattr__(self, "sha256", _sha256(self.sha256))
        object.__setattr__(
            self,
            "original_repository",
            _nonblank(self.original_repository, "original_repository"),
        )
        object.__setattr__(
            self, "original_commit", _nonblank(self.original_commit, "original_commit")
        )
        object.__setattr__(self, "original_path", _safe_path(self.original_path, "original_path"))
        object.__setattr__(self, "license_status", _nonblank(self.license_status, "license_status"))


@dataclass(frozen=True, slots=True)
class ApprovedImportSet(CanonicalRecord):
    """The exact file set named by a Human Import Gate."""

    snapshot: SourceSnapshot
    files: tuple[ApprovedImportFile, ...]
    total_bytes: int
    license_status: str
    approved_by: str
    approved_at: datetime
    approval_id: str

    def __post_init__(self) -> None:
        if not isinstance(self.snapshot, SourceSnapshot):
            raise TypeError("snapshot must be a SourceSnapshot.")
        files = tuple(self.files)
        if any(not isinstance(file, ApprovedImportFile) for file in files):
            raise TypeError("files must contain ApprovedImportFile records.")
        files = tuple(sorted(files, key=lambda item: (item.destination_path, item.source_path)))
        source_paths = tuple(file.source_path for file in files)
        destination_paths = tuple(file.destination_path for file in files)
        if len(source_paths) != len(set(source_paths)):
            raise ValueError("files must not contain duplicate source paths.")
        if len(destination_paths) != len(set(destination_paths)):
            raise ValueError("files must not contain duplicate destination paths.")
        object.__setattr__(self, "files", files)
        object.__setattr__(self, "total_bytes", _size(self.total_bytes, "total_bytes"))
        if self.total_bytes != sum(file.size_bytes for file in files):
            raise ValueError("total_bytes must equal the sum of approved file sizes.")
        object.__setattr__(self, "license_status", _nonblank(self.license_status, "license_status"))
        object.__setattr__(self, "approved_by", _nonblank(self.approved_by, "approved_by"))
        object.__setattr__(self, "approved_at", _timestamp(self.approved_at, "approved_at"))
        object.__setattr__(self, "approval_id", _nonblank(self.approval_id, "approval_id"))


@dataclass(frozen=True, slots=True)
class ImportCandidate(CanonicalRecord):
    """Redaction-safe metadata for one included or excluded source candidate."""

    source_path: str
    destination_path: str | None = None
    size_bytes: int | None = None
    sha256: str | None = None
    classification: str = "included"
    reason: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "source_path", _safe_path(self.source_path, "source_path"))
        if self.destination_path is not None:
            object.__setattr__(
                self, "destination_path", _safe_path(self.destination_path, "destination_path")
            )
        if self.size_bytes is not None:
            object.__setattr__(self, "size_bytes", _size(self.size_bytes))
        if self.sha256 is not None:
            object.__setattr__(self, "sha256", _sha256(self.sha256))
        object.__setattr__(self, "classification", _nonblank(self.classification, "classification"))
        object.__setattr__(self, "reason", redact_diagnostic(self.reason))


@dataclass(frozen=True, slots=True)
class ImportFinding(CanonicalRecord):
    """Stable diagnostic containing categories and metadata, never corpus bytes."""

    code: str
    path: str = ""
    field: str = ""
    message: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "code", _nonblank(self.code, "code").casefold())
        object.__setattr__(self, "path", redact_diagnostic(self.path))
        object.__setattr__(self, "field", redact_diagnostic(self.field))
        object.__setattr__(self, "message", redact_diagnostic(self.message))


@dataclass(frozen=True, slots=True)
class ImportDryRunReport(CanonicalRecord):
    """Complete deterministic report for a side-effect-free source scan."""

    snapshot: SourceSnapshot
    mode: ImportMode
    included: tuple[ImportCandidate, ...]
    excluded: tuple[ImportCandidate, ...]
    findings: tuple[ImportFinding, ...]
    total_bytes: int
    result: MigrationResult

    def __post_init__(self) -> None:
        if not isinstance(self.snapshot, SourceSnapshot):
            raise TypeError("snapshot must be a SourceSnapshot.")
        object.__setattr__(self, "mode", ImportMode(self.mode))
        included = tuple(self.included)
        excluded = tuple(self.excluded)
        if any(not isinstance(item, ImportCandidate) for item in (*included, *excluded)):
            raise TypeError("included and excluded must contain ImportCandidate records.")

        def candidate_key(item: ImportCandidate) -> tuple[str, str]:
            return item.source_path, item.destination_path or ""

        object.__setattr__(self, "included", tuple(sorted(included, key=candidate_key)))
        object.__setattr__(self, "excluded", tuple(sorted(excluded, key=candidate_key)))
        findings = tuple(self.findings)
        if any(not isinstance(item, ImportFinding) for item in findings):
            raise TypeError("findings must contain ImportFinding records.")
        object.__setattr__(self, "findings", sort_findings(findings))
        object.__setattr__(self, "total_bytes", _size(self.total_bytes, "total_bytes"))
        object.__setattr__(self, "result", MigrationResult(self.result))


@dataclass(frozen=True, slots=True)
class CorpusManifestEntry(CanonicalRecord):
    """One canonical destination file entry in the imported corpus manifest."""

    path: str
    size_bytes: int
    sha256: str
    original_repository: str
    original_commit: str
    original_path: str
    license_status: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "path", _safe_path(self.path, "path"))
        object.__setattr__(self, "size_bytes", _size(self.size_bytes))
        object.__setattr__(self, "sha256", _sha256(self.sha256))
        object.__setattr__(
            self,
            "original_repository",
            _nonblank(self.original_repository, "original_repository"),
        )
        object.__setattr__(
            self, "original_commit", _nonblank(self.original_commit, "original_commit")
        )
        object.__setattr__(self, "original_path", _safe_path(self.original_path, "original_path"))
        object.__setattr__(self, "license_status", _nonblank(self.license_status, "license_status"))


@dataclass(frozen=True, slots=True)
class AgentSourceMapEntry(CanonicalRecord):
    """One reviewed mapping from an authoritative common agent to source roles."""

    common_agent_id: str
    mapping_status: MappingStatus
    source_agent_ids: tuple[str, ...]
    source_documents: tuple[str, ...]
    rationale: str
    reviewed_by: str
    reviewed_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "common_agent_id", _nonblank(self.common_agent_id, "common_agent_id")
        )
        object.__setattr__(self, "mapping_status", MappingStatus(self.mapping_status))
        source_ids = _sequence(self.source_agent_ids, "source_agent_ids")
        source_documents = _path_sequence(self.source_documents, "source_documents")
        if self.mapping_status is MappingStatus.COMMON_ONLY and source_ids:
            raise ValueError("common_only mappings must have no source-agent IDs.")
        if self.mapping_status is not MappingStatus.COMMON_ONLY and not source_ids:
            raise ValueError("Non-common_only mappings require a source-agent ID.")
        object.__setattr__(self, "source_agent_ids", tuple(sorted(source_ids)))
        object.__setattr__(self, "source_documents", tuple(sorted(source_documents)))
        object.__setattr__(self, "rationale", _nonblank(self.rationale, "rationale"))
        object.__setattr__(self, "reviewed_by", _nonblank(self.reviewed_by, "reviewed_by"))
        object.__setattr__(self, "reviewed_at", _timestamp(self.reviewed_at, "reviewed_at"))


@dataclass(frozen=True, slots=True)
class AgentSpecificationReview(CanonicalRecord):
    """Human review required before accepting a critical local specification."""

    common_agent_id: str
    reviewer: str
    reviewed_at: datetime
    scope: str | tuple[str, ...]
    result: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "common_agent_id", _nonblank(self.common_agent_id, "common_agent_id")
        )
        object.__setattr__(self, "reviewer", _nonblank(self.reviewer, "reviewer"))
        object.__setattr__(self, "reviewed_at", _timestamp(self.reviewed_at, "reviewed_at"))
        scope = (self.scope,) if isinstance(self.scope, str) else tuple(self.scope)
        object.__setattr__(self, "scope", _sequence(scope, "scope"))
        object.__setattr__(self, "result", _review_result(self.result))


@dataclass(frozen=True, slots=True)
class AdaptedWorkflowAssessment(CanonicalRecord):
    """Deterministic assessment of one local adapted workflow."""

    workflow_path: str
    workflow_digest: str
    common_contract_digest: str
    result: str
    findings: tuple[ImportFinding, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "workflow_path", _safe_path(self.workflow_path, "workflow_path"))
        object.__setattr__(
            self, "workflow_digest", _sha256(self.workflow_digest, "workflow_digest")
        )
        object.__setattr__(
            self,
            "common_contract_digest",
            _sha256(self.common_contract_digest, "common_contract_digest"),
        )
        object.__setattr__(self, "result", _review_result(self.result))
        findings = tuple(self.findings)
        if any(not isinstance(finding, ImportFinding) for finding in findings):
            raise TypeError("findings must contain ImportFinding records.")
        object.__setattr__(self, "findings", sort_findings(findings))


@dataclass(frozen=True, slots=True)
class KnowledgeSeedRecord(CanonicalRecord):
    """Local provenance and consumer record for inert knowledge seed data."""

    seed_path: str
    provenance: HistoricalProvenance
    consumer_ref: str
    review_status: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "seed_path", _safe_path(self.seed_path, "seed_path"))
        if not isinstance(self.provenance, HistoricalProvenance):
            raise TypeError("provenance must be a HistoricalProvenance record.")
        object.__setattr__(self, "consumer_ref", _nonblank(self.consumer_ref, "consumer_ref"))
        object.__setattr__(self, "review_status", _review_result(self.review_status))


@dataclass(frozen=True, slots=True)
class SpecialSkillReview(CanonicalRecord):
    """Review vector controlling whether a special-skill integration may exist."""

    skill_id: str
    compatibility: bool
    security: bool
    overlap: bool
    license: bool
    consumer_ref: str
    reviewer: str
    reviewed_at: datetime
    result: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "skill_id", _nonblank(self.skill_id, "skill_id"))
        for field_name in ("compatibility", "security", "overlap", "license"):
            if not isinstance(getattr(self, field_name), bool):
                raise TypeError(f"{field_name} must be a boolean.")
        object.__setattr__(self, "consumer_ref", _nonblank(self.consumer_ref, "consumer_ref"))
        object.__setattr__(self, "reviewer", _nonblank(self.reviewer, "reviewer"))
        object.__setattr__(self, "reviewed_at", _timestamp(self.reviewed_at, "reviewed_at"))
        object.__setattr__(self, "result", _review_result(self.result))

    @property
    def is_approved(self) -> bool:
        """Return whether every review dimension and the recorded result pass."""
        return (
            self.compatibility
            and self.security
            and self.overlap
            and self.license
            and self.result == ReviewResult.PASS
        )


@dataclass(frozen=True, slots=True)
class MigrationEvidence(CanonicalRecord):
    """Append-only, redaction-safe evidence for one migration phase."""

    evidence_id: str
    phase: str
    result: MigrationResult
    commands: tuple[str, ...]
    results: tuple[str, ...]
    source_snapshot: SourceSnapshot
    correlation_id: str
    recorded_at: datetime
    blockers: tuple[str, ...]
    residual_risks: tuple[str, ...]
    change_set_ref: str
    pre_import_manifest_digest: str | None = None
    corpus_manifest_digest: str | None = None
    mapping_review_ref: str | None = None
    standalone_result: str | None = None
    documentation_check_result: str | None = None
    review_references: tuple[str, ...] = ()
    release_outcomes: tuple[str, ...] = ()
    change_set_digest: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "evidence_id", _nonblank(self.evidence_id, "evidence_id"))
        object.__setattr__(self, "phase", _nonblank(self.phase, "phase"))
        object.__setattr__(self, "result", MigrationResult(self.result))
        object.__setattr__(
            self, "commands", tuple(redact_diagnostic(value) for value in self.commands)
        )
        object.__setattr__(
            self, "results", tuple(redact_diagnostic(value) for value in self.results)
        )
        if any(not value for value in (*self.commands, *self.results)):
            raise ValueError("commands and results must contain non-empty values.")
        if not isinstance(self.source_snapshot, SourceSnapshot):
            raise TypeError("source_snapshot must be a SourceSnapshot.")
        object.__setattr__(self, "correlation_id", _nonblank(self.correlation_id, "correlation_id"))
        object.__setattr__(self, "recorded_at", _timestamp(self.recorded_at, "recorded_at"))
        object.__setattr__(
            self, "blockers", tuple(redact_diagnostic(value) for value in self.blockers)
        )
        object.__setattr__(
            self, "residual_risks", tuple(redact_diagnostic(value) for value in self.residual_risks)
        )
        if any(not value for value in (*self.blockers, *self.residual_risks)):
            raise ValueError("blockers and residual_risks must contain non-empty values.")
        object.__setattr__(self, "change_set_ref", _nonblank(self.change_set_ref, "change_set_ref"))
        review_references = tuple(redact_diagnostic(value) for value in self.review_references)
        release_outcomes = tuple(redact_diagnostic(value) for value in self.release_outcomes)
        if any(not value for value in (*review_references, *release_outcomes)):
            raise ValueError(
                "review_references and release_outcomes must contain non-empty values."
            )
        if len(review_references) != len(set(review_references)):
            raise ValueError("review_references must not contain duplicates.")
        if len(release_outcomes) != len(set(release_outcomes)):
            raise ValueError("release_outcomes must not contain duplicates.")
        object.__setattr__(self, "review_references", tuple(sorted(review_references)))
        object.__setattr__(self, "release_outcomes", tuple(sorted(release_outcomes)))
        for field_name in (
            "pre_import_manifest_digest",
            "corpus_manifest_digest",
            "change_set_digest",
        ):
            digest = getattr(self, field_name)
            if digest is not None:
                object.__setattr__(self, field_name, _sha256(digest, field_name))
        for field_name in (
            "mapping_review_ref",
            "standalone_result",
            "documentation_check_result",
        ):
            value = getattr(self, field_name)
            if value is not None:
                object.__setattr__(self, field_name, redact_diagnostic(value))


# Concise compatibility names used by callers that model an approved file directly.
ImportFile = ApprovedImportFile
ApprovedFile = ApprovedImportFile
Finding = ImportFinding
ReviewFinding = ImportFinding
