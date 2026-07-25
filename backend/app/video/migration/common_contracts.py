"""Immutable common-contract snapshots and fail-closed configuration boundaries.

The migration imports untrusted corpus data, but common-owned configuration remains a
separate authority.  This module snapshots only the local common contract surface and
never reads the corpus.  A snapshot can therefore be compared before and after an
import without allowing imported bytes to become configuration.
"""

from __future__ import annotations

import json
import re
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Final

from app.video.migration.canonical import (
    canonical_json_bytes,
    digest_json,
    redact_diagnostic,
    sha256_digest,
    sort_findings,
)
from app.video.migration.contracts import (
    CanonicalRecord,
    ImportFinding,
    MigrationResult,
    ReviewResult,
)
from app.video.migration.paths import (
    PathInput,
    UnsafeLocalPathError,
    normalize_relative_path,
    read_local_bytes,
    resolve_under_root,
)

_SHA256_PATTERN: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{64}$")
_EMPTY_DIGEST: Final[str] = sha256_digest(b"")

INVENTORY_PATH: Final[str] = "inventory.json"
MANIFEST_PATH: Final[str] = "manifest.json"
AGENT_RUNTIME_PREFIX: Final[str] = "agents"
POLICY_PREFIX: Final[str] = "policies"
SCHEMA_PREFIX: Final[str] = "schemas"
SAFE_SPINE_PATH: Final[str] = "workflows/pack_spine.json"

CONTRACT_SECTION_INVENTORY: Final[str] = "inventory"
CONTRACT_SECTION_MANIFEST: Final[str] = "manifest"
CONTRACT_SECTION_AGENT_RUNTIME: Final[str] = "agent_runtime_bindings"
CONTRACT_SECTION_POLICIES: Final[str] = "policies"
CONTRACT_SECTION_SCHEMAS: Final[str] = "schemas"
CONTRACT_SECTION_SAFE_SPINE: Final[str] = "workflows/pack_spine.json"

ACTIVATION_REQUEST_CODES: Final[frozenset[str]] = frozenset(
    {
        "imported_provider_request",
        "imported_credential_request",
        "imported_network_request",
        "imported_production_activation_request",
        "imported_human_gate_bypass_request",
        "corpus_configuration_context",
    }
)


class CommonContractSnapshotError(ValueError):
    """A redaction-safe failure while reading the local contract surface."""

    def __init__(self, code: str, path: str = "") -> None:
        self.code = code
        self.path = redact_diagnostic(path)
        super().__init__(f"Common contract snapshot failed: {code}.")


class ConfigurationChangeRejectedError(ValueError):
    """Raised when imported data attempts to become active configuration."""

    def __init__(self, report: ConfigurationBoundaryReport) -> None:
        self.report = report
        super().__init__("Imported material contains a rejected configuration change.")


# Short compatibility name retained for callers that use the report terminology.
ConfigurationChangeRejected = ConfigurationChangeRejectedError


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


def _sha256(value: str, name: str = "sha256") -> str:
    normalized = _nonblank(value, name).casefold()
    if _SHA256_PATTERN.fullmatch(normalized) is None:
        raise ValueError(f"{name} must be a lowercase SHA-256 hexadecimal digest.")
    return normalized


def _timestamp(value: datetime, name: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None:
        raise ValueError(f"{name} must be a timezone-aware UTC timestamp.")
    return value.astimezone(UTC)


def _unique_paths(values: Iterable[str], name: str) -> tuple[str, ...]:
    paths = tuple(sorted({_safe_path(value, name) for value in values}))
    if len(paths) != len(tuple(values)):
        # The normal path is handled below; this branch is retained only for a
        # caller that supplied a one-shot iterator and is therefore not used.
        raise ValueError(f"{name} must not contain duplicate paths.")
    return paths


def _normalized_paths(values: Iterable[str], name: str) -> tuple[str, ...]:
    normalized = tuple(_safe_path(value, name) for value in values)
    if len(normalized) != len(set(normalized)):
        raise ValueError(f"{name} must not contain duplicate paths.")
    return tuple(sorted(normalized))


@dataclass(frozen=True, slots=True)
class ContractFileSnapshot(CanonicalRecord):
    """Digest and safe metadata for one common-owned contract file."""

    path: str
    sha256: str = _EMPTY_DIGEST
    size_bytes: int = 0
    present: bool = True
    content_type: str = "data"

    def __post_init__(self) -> None:
        object.__setattr__(self, "path", _safe_path(self.path, "path"))
        object.__setattr__(self, "sha256", _sha256(self.sha256))
        if isinstance(self.size_bytes, bool) or not isinstance(self.size_bytes, int):
            raise TypeError("size_bytes must be a non-negative integer.")
        if self.size_bytes < 0:
            raise ValueError("size_bytes must be a non-negative integer.")
        if not isinstance(self.present, bool):
            raise TypeError("present must be a boolean.")
        object.__setattr__(self, "content_type", _nonblank(self.content_type, "content_type"))
        if not self.present and (self.size_bytes != 0 or self.sha256 != _EMPTY_DIGEST):
            raise ValueError("Missing contract files must have empty digest and size.")


@dataclass(frozen=True, slots=True)
class AgentRuntimeBindingSnapshot(CanonicalRecord):
    """Safety-sensitive projection of one common video-agent runtime binding."""

    agent_id: str
    status: str | None
    allowed_tools: tuple[str, ...]
    model_policy_digest: str
    network_access: bool | None
    critique_edges_digest: str
    max_refinement_count: int | None
    production_activation_requested: bool | None

    def __post_init__(self) -> None:
        object.__setattr__(self, "agent_id", _nonblank(self.agent_id, "agent_id"))
        if self.status is not None:
            object.__setattr__(self, "status", _nonblank(self.status, "status"))
        tools = tuple(self.allowed_tools)
        if any(not isinstance(tool, str) or not tool.strip() for tool in tools):
            raise ValueError("allowed_tools must contain nonblank strings.")
        if len(tools) != len(set(tools)):
            raise ValueError("allowed_tools must not contain duplicates.")
        object.__setattr__(self, "allowed_tools", tuple(sorted(tools)))
        object.__setattr__(
            self, "model_policy_digest", _sha256(self.model_policy_digest, "model_policy_digest")
        )
        object.__setattr__(
            self,
            "critique_edges_digest",
            _sha256(self.critique_edges_digest, "critique_edges_digest"),
        )
        if self.network_access is not None and not isinstance(self.network_access, bool):
            raise TypeError("network_access must be a boolean or None.")
        if self.max_refinement_count is not None and (
            isinstance(self.max_refinement_count, bool)
            or not isinstance(self.max_refinement_count, int)
        ):
            raise TypeError("max_refinement_count must be an integer or None.")
        if self.production_activation_requested is not None and not isinstance(
            self.production_activation_requested, bool
        ):
            raise TypeError("production_activation_requested must be a boolean or None.")


@dataclass(frozen=True, slots=True)
class CommonPackContractSnapshot(CanonicalRecord):
    """An immutable, local-only snapshot of all common-owned Video Pack contracts."""

    inventory: ContractFileSnapshot
    manifest: ContractFileSnapshot
    agent_runtime_bindings: tuple[ContractFileSnapshot, ...]
    policies: tuple[ContractFileSnapshot, ...]
    schemas: tuple[ContractFileSnapshot, ...]
    pack_spine: ContractFileSnapshot
    inventory_agent_ids: tuple[str, ...] = ()
    manifest_agent_ids: tuple[str, ...] = ()
    inventory_safety_digest: str = _EMPTY_DIGEST
    manifest_safety_digest: str = _EMPTY_DIGEST
    runtime_safety_digest: str = _EMPTY_DIGEST

    def __post_init__(self) -> None:
        for field_name in ("inventory", "manifest", "pack_spine"):
            if not isinstance(getattr(self, field_name), ContractFileSnapshot):
                raise TypeError(f"{field_name} must be a ContractFileSnapshot.")
        for field_name in ("agent_runtime_bindings", "policies", "schemas"):
            records = tuple(getattr(self, field_name))
            if any(not isinstance(record, ContractFileSnapshot) for record in records):
                raise TypeError(f"{field_name} must contain ContractFileSnapshot records.")
            if len({record.path for record in records}) != len(records):
                raise ValueError(f"{field_name} must not contain duplicate paths.")
            object.__setattr__(self, field_name, tuple(sorted(records, key=lambda item: item.path)))
        ids = tuple(self.inventory_agent_ids)
        manifest_ids = tuple(self.manifest_agent_ids)
        if len(ids) != len(set(ids)) or len(manifest_ids) != len(set(manifest_ids)):
            raise ValueError("Common-agent identity projections must not contain duplicates.")
        object.__setattr__(self, "inventory_agent_ids", ids)
        object.__setattr__(self, "manifest_agent_ids", manifest_ids)
        for field_name in (
            "inventory_safety_digest",
            "manifest_safety_digest",
            "runtime_safety_digest",
        ):
            object.__setattr__(self, field_name, _sha256(getattr(self, field_name), field_name))

    @classmethod
    def capture(cls, video_root: PathInput) -> CommonPackContractSnapshot:
        """Capture only common contract paths beneath ``video_root``.

        The method intentionally enumerates fixed contract directories and never
        traverses or reads ``corpus/``.  Missing required files are represented by
        immutable absent records so a before/after comparison reports removal rather
        than silently accepting it.
        """
        root = Path(video_root)
        inventory_record, inventory_data = _snapshot_json_file(root, INVENTORY_PATH)
        manifest_record, manifest_data = _snapshot_json_file(root, MANIFEST_PATH)
        pack_spine_record, _ = _snapshot_json_file(root, SAFE_SPINE_PATH)
        agent_records = _snapshot_agent_runtime_files(root)
        policy_records = _snapshot_tree_files(root, POLICY_PREFIX)
        schema_records = _snapshot_tree_files(root, SCHEMA_PREFIX)
        return cls(
            inventory=inventory_record,
            manifest=manifest_record,
            agent_runtime_bindings=agent_records,
            policies=policy_records,
            schemas=schema_records,
            pack_spine=pack_spine_record,
            inventory_agent_ids=_agent_ids(inventory_data, "entries"),
            manifest_agent_ids=_agent_ids(manifest_data, "agents"),
            inventory_safety_digest=_safety_digest(_inventory_safety_projection(inventory_data)),
            manifest_safety_digest=_safety_digest(_manifest_safety_projection(manifest_data)),
            runtime_safety_digest=_safety_digest(_runtime_safety_projection(root, agent_records)),
        )

    @classmethod
    def from_directory(cls, video_root: PathInput) -> CommonPackContractSnapshot:
        """Compatibility constructor for :meth:`capture`."""
        return cls.capture(video_root)

    @property
    def contract_digest(self) -> str:
        """Return the digest of this snapshot without a filesystem-root identity."""
        return digest_json(self)

    @property
    def all_files(self) -> tuple[ContractFileSnapshot, ...]:
        """Return every snapshotted contract file in canonical path order."""
        return tuple(
            sorted(
                (
                    self.inventory,
                    self.manifest,
                    *self.agent_runtime_bindings,
                    *self.policies,
                    *self.schemas,
                    self.pack_spine,
                ),
                key=lambda item: item.path,
            )
        )


@dataclass(frozen=True, slots=True)
class CommonPackContractReview(CanonicalRecord):
    """Explicit human compatibility approval for one exact contract delta."""

    review_id: str
    changed_paths: tuple[str, ...]
    before_digest: str
    after_digest: str
    reviewed_by: str
    reviewed_at: datetime
    rationale: str
    result: ReviewResult = ReviewResult.PASS
    compatibility_confirmed: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "review_id", _nonblank(self.review_id, "review_id"))
        object.__setattr__(
            self, "changed_paths", _normalized_paths(self.changed_paths, "changed_paths")
        )
        object.__setattr__(self, "before_digest", _sha256(self.before_digest, "before_digest"))
        object.__setattr__(self, "after_digest", _sha256(self.after_digest, "after_digest"))
        object.__setattr__(self, "reviewed_by", _nonblank(self.reviewed_by, "reviewed_by"))
        object.__setattr__(self, "reviewed_at", _timestamp(self.reviewed_at, "reviewed_at"))
        object.__setattr__(self, "rationale", _nonblank(self.rationale, "rationale"))
        object.__setattr__(self, "result", ReviewResult(self.result))
        if not isinstance(self.compatibility_confirmed, bool):
            raise TypeError("compatibility_confirmed must be a boolean.")

    @property
    def changed_contracts(self) -> tuple[str, ...]:
        """Compatibility name for callers that refer to contract paths."""
        return self.changed_paths

    @property
    def before_contract_digest(self) -> str:
        """Compatibility name for the exact predecessor snapshot digest."""
        return self.before_digest

    @property
    def after_contract_digest(self) -> str:
        """Compatibility name for the exact successor snapshot digest."""
        return self.after_digest

    @property
    def contract_paths(self) -> tuple[str, ...]:
        """Compatibility name for the exact reviewed contract scope."""
        return self.changed_paths

    @property
    def is_approved(self) -> bool:
        """Return whether this record explicitly approves the exact compatible delta."""
        return self.result is ReviewResult.PASS and self.compatibility_confirmed


@dataclass(frozen=True, slots=True)
class CommonPackContractComparison(CanonicalRecord):
    """Deterministic before/after comparison and compatibility decision."""

    before: CommonPackContractSnapshot
    after: CommonPackContractSnapshot
    changed_sections: tuple[str, ...]
    changed_paths: tuple[str, ...]
    findings: tuple[ImportFinding, ...]
    result: MigrationResult
    review: CommonPackContractReview | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.before, CommonPackContractSnapshot):
            raise TypeError("before must be a CommonPackContractSnapshot.")
        if not isinstance(self.after, CommonPackContractSnapshot):
            raise TypeError("after must be a CommonPackContractSnapshot.")
        object.__setattr__(self, "changed_sections", tuple(sorted(set(self.changed_sections))))
        object.__setattr__(self, "changed_paths", tuple(sorted(set(self.changed_paths))))
        findings = tuple(self.findings)
        if any(not isinstance(finding, ImportFinding) for finding in findings):
            raise TypeError("findings must contain ImportFinding records.")
        object.__setattr__(self, "findings", sort_findings(findings))
        object.__setattr__(self, "result", MigrationResult(self.result))
        if self.review is not None and not isinstance(self.review, CommonPackContractReview):
            raise TypeError("review must be a CommonPackContractReview or None.")

    @property
    def changed_contracts(self) -> tuple[str, ...]:
        """Compatibility name for the changed common contract paths."""
        return self.changed_paths

    @property
    def is_compatible(self) -> bool:
        """Return whether the before/after state may be accepted."""
        return self.result is MigrationResult.PASS

    @property
    def is_valid(self) -> bool:
        """Compatibility alias for :attr:`is_compatible`."""
        return self.is_compatible


@dataclass(frozen=True, slots=True)
class ConfigurationBoundaryReport(CanonicalRecord):
    """Redaction-safe result for imported configuration and corpus-boundary checks."""

    result: MigrationResult
    findings: tuple[ImportFinding, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "result", MigrationResult(self.result))
        findings = tuple(self.findings)
        if any(not isinstance(finding, ImportFinding) for finding in findings):
            raise TypeError("findings must contain ImportFinding records.")
        object.__setattr__(self, "findings", sort_findings(findings))

    @property
    def is_safe(self) -> bool:
        """Compatibility alias for callers that use safety terminology."""
        return self.is_valid

    @property
    def is_rejected(self) -> bool:
        """Return whether a configuration boundary violation was found."""
        return not self.is_valid

    @property
    def is_valid(self) -> bool:
        """Return whether imported material contains no configuration boundary issue."""
        return self.result is MigrationResult.PASS


# Explicit aliases make the terminology usable at both design and implementation
# boundaries without creating mutable duplicate record types.
CommonContractSnapshot = CommonPackContractSnapshot
ContractSnapshot = CommonPackContractSnapshot
CommonContractReview = CommonPackContractReview
CompatibleContractReview = CommonPackContractReview
ContractComparison = CommonPackContractComparison


def snapshot_common_contracts(video_root: PathInput) -> CommonPackContractSnapshot:
    """Capture the local common-owned contract surface."""
    return CommonPackContractSnapshot.capture(video_root)


def capture_common_contracts(video_root: PathInput) -> CommonPackContractSnapshot:
    """Compatibility alias for :func:`snapshot_common_contracts`."""
    return snapshot_common_contracts(video_root)


def snapshot_common_pack_contracts(video_root: PathInput) -> CommonPackContractSnapshot:
    """Compatibility alias using the full Common Pack terminology."""
    return snapshot_common_contracts(video_root)


def compare_common_contracts(
    before: CommonPackContractSnapshot | PathInput,
    after: CommonPackContractSnapshot | PathInput,
    review: CommonPackContractReview | None = None,
) -> CommonPackContractComparison:
    """Compare common contracts and require exact review for allowed changes.

    Identity, runtime-safety, and safe-spine changes are never made compatible by a
    review.  Other contract deltas require an explicit passing review naming the exact
    changed paths and both snapshot digests.
    """
    before_snapshot = _as_snapshot(before)
    after_snapshot = _as_snapshot(after)
    before_files = {record.path: record for record in before_snapshot.all_files}
    after_files = {record.path: record for record in after_snapshot.all_files}
    all_paths = tuple(sorted(set(before_files) | set(after_files)))
    changed_paths = tuple(
        path for path in all_paths if before_files.get(path) != after_files.get(path)
    )
    changed_sections = tuple(sorted({_section_for_path(path) for path in changed_paths}))
    findings: list[ImportFinding] = []

    if before_snapshot.inventory_agent_ids != after_snapshot.inventory_agent_ids:
        findings.append(
            ImportFinding(
                "common_agent_identity_changed",
                path=INVENTORY_PATH,
                message="Authoritative Common Agent IDs must remain unchanged.",
            )
        )
    if before_snapshot.manifest_agent_ids != after_snapshot.manifest_agent_ids:
        findings.append(
            ImportFinding(
                "common_manifest_identity_changed",
                path=MANIFEST_PATH,
                message="Manifest Common Agent IDs must remain unchanged.",
            )
        )
    if before_snapshot.inventory_safety_digest != after_snapshot.inventory_safety_digest:
        findings.append(
            ImportFinding(
                "inventory_runtime_safety_changed",
                path=INVENTORY_PATH,
                message=(
                    "Inventory status, maturity, and local binding safety must remain unchanged."
                ),
            )
        )
    if before_snapshot.manifest_safety_digest != after_snapshot.manifest_safety_digest:
        findings.append(
            ImportFinding(
                "manifest_runtime_safety_changed",
                path=MANIFEST_PATH,
                message="Manifest activation and runtime safety fields must remain unchanged.",
            )
        )
    if before_snapshot.runtime_safety_digest != after_snapshot.runtime_safety_digest:
        findings.append(
            ImportFinding(
                "agent_runtime_safety_changed",
                path=AGENT_RUNTIME_PREFIX,
                message=(
                    "Agent model policy, network restriction, critique edges, refinement "
                    "limits, tools, and activation posture must remain unchanged."
                ),
            )
        )
    if SAFE_SPINE_PATH in changed_paths:
        findings.append(
            ImportFinding(
                "safe_baseline_workflow_changed",
                path=SAFE_SPINE_PATH,
                message=(
                    "pack_spine.json remains the safe baseline until an adapted "
                    "workflow is accepted."
                ),
            )
        )

    if changed_paths:
        if review is None:
            for path in changed_paths:
                findings.append(
                    ImportFinding(
                        "common_contract_change_requires_review",
                        path=path,
                        message="An explicit compatible Common Pack Contract review is required.",
                    )
                )
        else:
            if not review.is_approved:
                findings.append(
                    ImportFinding(
                        "common_contract_review_not_approved",
                        path=review.review_id,
                        message="The compatible contract review is not a passing approval.",
                    )
                )
            if review.before_digest != before_snapshot.contract_digest:
                findings.append(
                    ImportFinding(
                        "common_contract_review_before_mismatch",
                        path=review.review_id,
                        field="before_digest",
                        message="The review does not name this before snapshot.",
                    )
                )
            if review.after_digest != after_snapshot.contract_digest:
                findings.append(
                    ImportFinding(
                        "common_contract_review_after_mismatch",
                        path=review.review_id,
                        field="after_digest",
                        message="The review does not name this after snapshot.",
                    )
                )
            if review.changed_paths != changed_paths:
                findings.append(
                    ImportFinding(
                        "common_contract_review_scope_mismatch",
                        path=review.review_id,
                        field="changed_paths",
                        message="The review must name exactly the changed contract paths.",
                    )
                )

    result = MigrationResult.PASS if not findings else MigrationResult.BLOCKED
    return CommonPackContractComparison(
        before=before_snapshot,
        after=after_snapshot,
        changed_sections=changed_sections,
        changed_paths=changed_paths,
        findings=tuple(findings),
        result=result,
        review=review,
    )


def compare_common_contract_snapshots(
    before: CommonPackContractSnapshot,
    after: CommonPackContractSnapshot,
    review: CommonPackContractReview | None = None,
) -> CommonPackContractComparison:
    """Compatibility alias for comparing already captured snapshots."""
    return compare_common_contracts(before, after, review)


def compare_common_pack_contracts(
    before: CommonPackContractSnapshot | PathInput,
    after: CommonPackContractSnapshot | PathInput,
    review: CommonPackContractReview | None = None,
) -> CommonPackContractComparison:
    """Compatibility alias using the full Common Pack terminology."""
    return compare_common_contracts(before, after, review)


def validate_imported_configuration(
    imported_material: object,
    *,
    corpus_paths: Iterable[PathInput] = (),
) -> ConfigurationBoundaryReport:
    """Reject activation requests without reading or executing imported corpus data.

    Only structured configuration candidates are inspected.  Strings in a corpus
    remain inert data; a corpus path is rejected if it is presented as a configuration
    value or if the caller explicitly identifies it as one of ``corpus_paths``.
    """
    findings: list[ImportFinding] = []
    known_corpus_paths = _normalize_corpus_paths(corpus_paths, findings)
    _scan_configuration_value(imported_material, "", known_corpus_paths, findings)
    return ConfigurationBoundaryReport(
        result=MigrationResult.PASS if not findings else MigrationResult.BLOCKED,
        findings=tuple(findings),
    )


def reject_activation_requests(
    imported_material: object,
    *,
    corpus_paths: Iterable[PathInput] = (),
) -> ConfigurationBoundaryReport:
    """Return a fail-closed report for provider/credential/network/activation requests."""
    return validate_imported_configuration(imported_material, corpus_paths=corpus_paths)


def validate_activation_requests(
    imported_material: object,
    *,
    corpus_paths: Iterable[PathInput] = (),
) -> ConfigurationBoundaryReport:
    """Compatibility alias for validating imported activation requests."""
    return validate_imported_configuration(imported_material, corpus_paths=corpus_paths)


def reject_imported_configuration_changes(
    imported_material: object,
    *,
    corpus_paths: Iterable[PathInput] = (),
) -> ConfigurationBoundaryReport:
    """Compatibility alias for the fail-closed configuration boundary report."""
    return validate_imported_configuration(imported_material, corpus_paths=corpus_paths)


def assert_no_activation_requests(
    imported_material: object,
    *,
    corpus_paths: Iterable[PathInput] = (),
) -> None:
    """Compatibility alias for :func:`assert_configuration_context_safe`."""
    assert_configuration_context_safe(imported_material, corpus_paths=corpus_paths)


def assert_configuration_context_safe(
    imported_material: object,
    *,
    corpus_paths: Iterable[PathInput] = (),
) -> None:
    """Raise before a candidate can be admitted to a configuration context."""
    report = validate_imported_configuration(imported_material, corpus_paths=corpus_paths)
    if not report.is_valid:
        raise ConfigurationChangeRejectedError(report)


def load_configuration_context(
    imported_material: object,
    *,
    corpus_paths: Iterable[PathInput] = (),
) -> object:
    """Guard the configuration boundary and return only already-local data.

    This function does not open paths or deserialize corpus files.  It exists as a
    narrow seam for callers that need a checked value after validation.
    """
    assert_configuration_context_safe(imported_material, corpus_paths=corpus_paths)
    return imported_material


def _as_snapshot(value: CommonPackContractSnapshot | PathInput) -> CommonPackContractSnapshot:
    if isinstance(value, CommonPackContractSnapshot):
        return value
    return CommonPackContractSnapshot.capture(value)


def _snapshot_json_file(
    root: Path, relative_path: str
) -> tuple[ContractFileSnapshot, Mapping[str, object]]:
    record = _snapshot_file(root, relative_path, content_type="json")
    if not record.present:
        return record, {}
    try:
        parsed = json.loads(read_local_bytes(root, relative_path).decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise CommonContractSnapshotError("invalid_json", relative_path) from error
    if not isinstance(parsed, Mapping):
        raise CommonContractSnapshotError("json_object_required", relative_path)
    return record, {str(key): value for key, value in parsed.items()}


def _snapshot_file(
    root: Path,
    relative_path: str,
    *,
    content_type: str,
) -> ContractFileSnapshot:
    normalized = _safe_path(relative_path, "relative_path")
    try:
        payload = read_local_bytes(root, normalized)
    except UnsafeLocalPathError as error:
        if error.code == "missing_path":
            return ContractFileSnapshot(path=normalized, present=False, content_type=content_type)
        raise CommonContractSnapshotError(error.code, normalized) from error
    except (OSError, UnicodeError) as error:
        raise CommonContractSnapshotError("unreadable_path", normalized) from error
    if content_type == "json":
        try:
            payload = canonical_json_bytes(json.loads(payload.decode("utf-8")))
        except (UnicodeError, json.JSONDecodeError, TypeError, ValueError) as error:
            raise CommonContractSnapshotError("invalid_json", normalized) from error
    return ContractFileSnapshot(
        path=normalized,
        sha256=sha256_digest(payload),
        size_bytes=len(payload),
        present=True,
        content_type=content_type,
    )


def _snapshot_agent_runtime_files(root: Path) -> tuple[ContractFileSnapshot, ...]:
    return _snapshot_tree_files(root, AGENT_RUNTIME_PREFIX, filename="agent_spec.json")


def _snapshot_tree_files(
    root: Path,
    relative_prefix: str,
    *,
    filename: str | None = None,
) -> tuple[ContractFileSnapshot, ...]:
    try:
        directory = resolve_under_root(root, relative_prefix)
    except UnsafeLocalPathError as error:
        if error.code == "missing_path":
            return ()
        raise CommonContractSnapshotError(error.code, relative_prefix) from error
    if not directory.exists():
        return ()
    if not directory.is_dir():
        raise CommonContractSnapshotError("not_a_directory", relative_prefix)
    root_path = Path(root).resolve()
    records: list[ContractFileSnapshot] = []
    pending = [directory]
    while pending:
        current = pending.pop()
        try:
            children = sorted(current.iterdir(), key=lambda item: item.name, reverse=True)
        except OSError as error:
            raise CommonContractSnapshotError("unreadable_path", relative_prefix) from error
        for child in children:
            try:
                relative = child.resolve(strict=False).relative_to(root_path).as_posix()
            except (OSError, RuntimeError, ValueError) as error:
                raise CommonContractSnapshotError("out_of_root", relative_prefix) from error
            if relative == "corpus" or relative.startswith("corpus/"):
                continue
            if child.is_dir():
                pending.append(child)
                continue
            if not child.is_file():
                continue
            if filename is not None and child.name != filename:
                continue
            records.append(
                _snapshot_file(
                    root,
                    relative,
                    content_type="json" if child.suffix.casefold() == ".json" else "text",
                )
            )
    return tuple(sorted(records, key=lambda item: item.path))


def _agent_ids(data: Mapping[str, object], field: str) -> tuple[str, ...]:
    raw_entries = data.get(field, ())
    if not isinstance(raw_entries, Sequence) or isinstance(raw_entries, (str, bytes, bytearray)):
        return ()
    ids: list[str] = []
    for entry in raw_entries:
        if not isinstance(entry, Mapping):
            continue
        agent_id = entry.get("agent_id")
        if isinstance(agent_id, str):
            ids.append(agent_id)
    return tuple(ids)


def _inventory_safety_projection(data: Mapping[str, object]) -> object:
    raw_entries = data.get("entries", ())
    entries = []
    if isinstance(raw_entries, Sequence) and not isinstance(raw_entries, (str, bytes, bytearray)):
        for entry in raw_entries:
            if isinstance(entry, Mapping):
                entries.append(
                    {
                        "agent_id": entry.get("agent_id"),
                        "status": entry.get("status"),
                        "maturity_level": entry.get("maturity_level"),
                        "agent_spec_path": entry.get("agent_spec_path"),
                    }
                )
    return {"pack_id": data.get("pack_id"), "entries": entries}


def _manifest_safety_projection(data: Mapping[str, object]) -> object:
    raw_agents = data.get("agents", ())
    agents = []
    if isinstance(raw_agents, Sequence) and not isinstance(raw_agents, (str, bytes, bytearray)):
        for agent in raw_agents:
            if isinstance(agent, Mapping):
                agents.append(
                    {
                        "agent_id": agent.get("agent_id"),
                        "status": agent.get("status"),
                        "allowed_tools": agent.get("allowed_tools"),
                        "agent_spec_path": agent.get("agent_spec_path"),
                    }
                )
    return {
        "pack_id": data.get("pack_id"),
        "production_activation_requested": data.get("production_activation_requested"),
        "agents": agents,
    }


def _runtime_safety_projection(
    root: Path,
    records: Sequence[ContractFileSnapshot],
) -> object:
    projections: list[object] = []
    for record in records:
        if not record.present:
            projections.append({"path": record.path, "missing": True})
            continue
        try:
            relative_path = record.path
            data = json.loads(read_local_bytes(root, relative_path).decode("utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            raise CommonContractSnapshotError("invalid_json", record.path) from error
        if not isinstance(data, Mapping):
            raise CommonContractSnapshotError("json_object_required", record.path)
        model_policy = data.get("model_policy")
        critique_edges = data.get("critique_edges")
        projections.append(
            {
                "path": record.path,
                "agent_id": data.get("agent_id"),
                "status": data.get("status"),
                "allowed_tools": data.get("allowed_tools"),
                "model_policy": model_policy,
                "network_access": (
                    model_policy.get("network_access")
                    if isinstance(model_policy, Mapping)
                    else None
                ),
                "critique_edges": critique_edges,
                "max_refinement_count": data.get("max_refinement_count"),
                "production_activation_requested": data.get("production_activation_requested"),
            }
        )
    return projections


def _safety_digest(value: object) -> str:
    return digest_json(value)


def _section_for_path(path: str) -> str:
    if path == INVENTORY_PATH:
        return CONTRACT_SECTION_INVENTORY
    if path == MANIFEST_PATH:
        return CONTRACT_SECTION_MANIFEST
    if path == SAFE_SPINE_PATH:
        return CONTRACT_SECTION_SAFE_SPINE
    if path.startswith(f"{AGENT_RUNTIME_PREFIX}/"):
        return CONTRACT_SECTION_AGENT_RUNTIME
    if path.startswith(f"{POLICY_PREFIX}/"):
        return CONTRACT_SECTION_POLICIES
    if path.startswith(f"{SCHEMA_PREFIX}/"):
        return CONTRACT_SECTION_SCHEMAS
    return "unknown"


def _normalize_corpus_paths(
    corpus_paths: Iterable[PathInput], findings: list[ImportFinding]
) -> frozenset[str]:
    normalized: set[str] = set()
    for path in corpus_paths:
        try:
            candidate = normalize_relative_path(path)
        except UnsafeLocalPathError:
            findings.append(
                ImportFinding(
                    "corpus_configuration_context",
                    field="corpus_paths",
                    message=(
                        "Corpus paths must be safe relative paths and remain outside configuration."
                    ),
                )
            )
            continue
        normalized.add(candidate)
    return frozenset(normalized)


def _scan_configuration_value(
    value: object,
    field_path: str,
    known_corpus_paths: frozenset[str],
    findings: list[ImportFinding],
) -> None:
    if isinstance(value, str) and _contains_corpus_path(value, known_corpus_paths):
        findings.append(
            ImportFinding(
                "corpus_configuration_context",
                field=field_path,
                message="A corpus path cannot be loaded into a configuration context.",
            )
        )
        return
    if isinstance(value, Mapping):
        for raw_key, child in value.items():
            if not isinstance(raw_key, str):
                continue
            key = raw_key.strip()
            child_field = f"{field_path}.{key}" if field_path else key
            normalized_key = _normalized_key(key)
            if _is_corpus_field(normalized_key) or _contains_corpus_path(child, known_corpus_paths):
                findings.append(
                    ImportFinding(
                        "corpus_configuration_context",
                        field=child_field,
                        message=(
                            "Imported corpus remains inert reference data and cannot "
                            "enter configuration."
                        ),
                    )
                )
            category = _activation_category(normalized_key, child)
            if category is not None:
                findings.append(
                    ImportFinding(
                        f"imported_{category}_request",
                        field=child_field,
                        message=(
                            f"Imported {category.replace('_', ' ')} requests are "
                            "configuration changes."
                        ),
                    )
                )
            _scan_configuration_value(child, child_field, known_corpus_paths, findings)
        return
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            child_field = f"{field_path}[{index}]"
            if _contains_corpus_path(child, known_corpus_paths):
                findings.append(
                    ImportFinding(
                        "corpus_configuration_context",
                        field=child_field,
                        message=(
                            "Imported corpus remains inert reference data and cannot "
                            "enter configuration."
                        ),
                    )
                )
            _scan_configuration_value(child, child_field, known_corpus_paths, findings)
        return
    if isinstance(value, Path) and _looks_like_corpus_path(value.as_posix()):
        findings.append(
            ImportFinding(
                "corpus_configuration_context",
                field=field_path,
                message="A corpus path cannot be loaded into a configuration context.",
            )
        )


def _normalized_key(value: str) -> str:
    return value.casefold().replace("-", "_").replace(" ", "_")


def _activation_category(key: str, value: object) -> str | None:
    if key in {
        "provider",
        "provider_id",
        "provider_name",
        "provider_config",
        "provider_activation",
        "provider_activation_requested",
        "activate_provider",
        "enable_provider",
    }:
        return "provider" if _is_requested(value) else None
    if (
        "credential" in key
        or "secret" in key
        or "api_key" in key
        or "token" in key
        or "password" in key
        or "authorization" in key
        or "access_key" in key
    ):
        return "credential" if _is_requested(value) else None
    if key in {
        "network",
        "network_access",
        "network_access_requested",
        "network_request",
        "network_enabled",
        "allow_network",
        "internet_access",
        "enable_network",
        "request_network_access",
    } or key.startswith("enable_network"):
        return "network" if _is_requested(value) else None
    if "production_activation" in key or key in {
        "production_active",
        "production_agent_activation",
        "production_agent_activation_requested",
        "activate_production",
        "enable_production",
        "runtime_activation",
    }:
        return "production_activation" if _is_requested(value) else None
    if (
        "human_gate_bypass" in key
        or "human_approval_bypass" in key
        or key in {"bypass_gate", "skip_human_gate", "approval_bypass"}
    ):
        return "human_gate_bypass" if _is_requested(value) else None
    return None


def _is_requested(value: object) -> bool:
    if value is None or value is False:
        return False
    if isinstance(value, str):
        return value.strip().casefold() not in {"", "false", "disabled", "none", "null"}
    if isinstance(value, Mapping):
        if not value:
            return False
        for key in ("enabled", "active", "requested", "allow", "bypass"):
            if key in value:
                return _is_requested(value[key])
        return True
    return bool(value)


def _contains_corpus_path(value: object, known_corpus_paths: frozenset[str]) -> bool:
    if isinstance(value, Path):
        return _looks_like_corpus_path(value.as_posix())
    if isinstance(value, str):
        if _looks_like_corpus_path(value):
            return True
        try:
            normalized = normalize_relative_path(value)
        except UnsafeLocalPathError:
            return False
        return normalized in known_corpus_paths or _looks_like_corpus_path(normalized)
    return False


def _is_corpus_field(key: str) -> bool:
    return key in {"corpus", "corpus_path", "corpus_paths", "imported_corpus", "corpus_file"}


def _looks_like_corpus_path(value: str) -> bool:
    normalized = value.replace("\\", "/").casefold()
    stripped = normalized.lstrip("./")
    parts = tuple(part for part in stripped.split("/") if part)
    return (
        stripped == "corpus"
        or stripped.startswith("corpus/")
        or stripped.startswith("business/video/corpus/")
        or "business/video/corpus" in stripped
        or "corpus" in parts
    )


__all__ = [
    "ACTIVATION_REQUEST_CODES",
    "AGENT_RUNTIME_PREFIX",
    "CONTRACT_SECTION_AGENT_RUNTIME",
    "CONTRACT_SECTION_INVENTORY",
    "CONTRACT_SECTION_MANIFEST",
    "CONTRACT_SECTION_POLICIES",
    "CONTRACT_SECTION_SAFE_SPINE",
    "CONTRACT_SECTION_SCHEMAS",
    "INVENTORY_PATH",
    "MANIFEST_PATH",
    "SAFE_SPINE_PATH",
    "AgentRuntimeBindingSnapshot",
    "CommonContractReview",
    "CommonContractSnapshot",
    "CommonContractSnapshotError",
    "CommonPackContractComparison",
    "CommonPackContractReview",
    "CommonPackContractSnapshot",
    "CompatibleContractReview",
    "ConfigurationBoundaryReport",
    "ConfigurationChangeRejected",
    "ConfigurationChangeRejectedError",
    "ContractComparison",
    "ContractFileSnapshot",
    "ContractSnapshot",
    "assert_configuration_context_safe",
    "assert_no_activation_requests",
    "capture_common_contracts",
    "compare_common_contract_snapshots",
    "compare_common_contracts",
    "compare_common_pack_contracts",
    "load_configuration_context",
    "reject_activation_requests",
    "reject_imported_configuration_changes",
    "snapshot_common_contracts",
    "snapshot_common_pack_contracts",
    "validate_activation_requests",
    "validate_imported_configuration",
]
