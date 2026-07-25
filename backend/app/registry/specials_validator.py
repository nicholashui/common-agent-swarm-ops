"""Offline, data-only validation primitives for the ``specials`` pack.

This module deliberately contains no registry, runtime, provider, network, or
activation integration.  Source Markdown is treated as opaque bytes: the
validator may hash an explicitly allowlisted source file, but never interprets
its contents as configuration or executable instructions.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, replace
from datetime import datetime
from pathlib import Path, PurePosixPath, PureWindowsPath
from types import MappingProxyType
from typing import Final, Literal, cast

SPECIALS_PACK_ID: Final[str] = "specials"
SPECIALS_SCHEMA_VERSION: Final[str] = "1.0"
SPECIALS_PACK_ROOT: Final[str] = "business/specials"
SPECIALS_SCHEMA_PATH: Final[str] = "business/specials/schemas/special-agent-spec.schema.json"
SPECIALS_MANIFEST_PATH: Final[str] = "business/specials/manifest.json"
SPECIALS_INVENTORY_PATH: Final[str] = "business/specials/inventory.json"
SPECIALS_SOURCE_ROOT: Final[str] = "docs/special_agents_redesign/agents"
SPECIALS_SOURCE_RECORD_ROOT: Final[str] = "business/specials/governance/source-records"
SPECIALS_RISK_ASSESSMENT_ROOT: Final[str] = "business/specials/governance/risk-assessments"
SPECIALS_APPROVAL_ROOT: Final[str] = "business/specials/governance/approvals"
SPECIALS_VALIDATION_REPORT_ROOT: Final[str] = "business/specials/validation/reports"

GovernanceRecordKind = Literal["source_record", "risk_assessment", "approval"]
CanonicalAgentId = str
SpecialAgentAssetId = str
ValidationOutcome = Literal["pass", "fail"]
SchemaResult = Literal["pass", "fail"]
InventoryResult = Literal["not_required", "pass", "fail"]
ReportRetention = Literal["retained", "failed", "not_attempted"]
RegistrationEffect = Literal["none", "eligible_draft_representation"]
FindingCategory = Literal[
    "path", "schema", "asset_namespace", "integrity", "provenance", "risk_gate", "io"
]

_CANONICAL_AGENT_ID_RE: Final[re.Pattern[str]] = re.compile(r"^specials\.[a-z0-9]+(?:-[a-z0-9]+)*$")
_SPECIAL_AGENT_ASSET_ID_RE: Final[re.Pattern[str]] = re.compile(
    r"^spagent\.[a-z0-9]+(?:-[a-z0-9]+)*$"
)
_SHA256_RE: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{64}$")
_TIMESTAMP_RE: Final[re.Pattern[str]] = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$"
)
_RISK_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "sensitive_personal_data",
        "psychological_profiling_or_recommendation",
        "legal",
        "medical",
        "financial",
        "external_service",
        "credential",
        "external_write",
        "production_release",
    }
)
_EXTERNAL_EFFECTS: Final[frozenset[str]] = frozenset(
    {"external-service", "external-write", "production-release"}
)
_RISK_ASSESSMENT_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "schema_version",
        "configuration_sha256",
        "source_record_sha256",
        "potential_risks",
        "external_effect_potential",
        "requested_tool_authority",
        "requested_network_access",
        "requested_provider",
        "requested_production_activation",
        "requested_lifecycle_state",
    }
)
_SOURCE_RECORD_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "schema_version",
        "source_path",
        "source_sha256",
        "agent_id",
        "configuration_sha256",
        "reviewed_at",
        "approval_id",
    }
)
_APPROVAL_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "approval_id",
        "reviewer_identity",
        "decision_timestamp",
        "decision",
        "source_path",
        "source_sha256",
        "agent_id",
        "configuration_sha256",
        "source_record_sha256",
        "approved_risk_scope",
        "reason",
    }
)
_APPROVED_SCOPE_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "potential_risks",
        "external_effect_potential",
        "requested_tool_authority",
        "requested_network_access",
        "requested_provider",
        "requested_production_activation",
        "requested_lifecycle_state",
    }
)


@dataclass(frozen=True, slots=True)
class SpecialSourceEntry:
    """One fixed, untrusted source-to-canonical-ID mapping."""

    source_path: str
    agent_id: CanonicalAgentId

    @property
    def agent_name(self) -> str:
        """Return the canonical name without its namespace prefix."""
        return self.agent_id.removeprefix("specials.")

    @property
    def agent_spec_path(self) -> str:
        """Return the exact pack-relative specification path."""
        return canonical_agent_spec_path(self.agent_id)


# The tuple is deliberately written as a fixed catalog and sorted by canonical
# ID.  It is not derived from directory discovery or source contents.
SPECIAL_SOURCE_CATALOG: Final[tuple[SpecialSourceEntry, ...]] = (
    SpecialSourceEntry(
        "docs/special_agents_redesign/agents/aesthetics_agent.md",
        "specials.aesthetics-agent",
    ),
    SpecialSourceEntry(
        "docs/special_agents_redesign/agents/agent_loop_creator.md",
        "specials.agent-loop-creator",
    ),
    SpecialSourceEntry(
        "docs/special_agents_redesign/agents/agentic_rag_agent.md",
        "specials.agentic-rag-agent",
    ),
    SpecialSourceEntry(
        "docs/special_agents_redesign/agents/autotelic_agent.md",
        "specials.autotelic-agent",
    ),
    SpecialSourceEntry(
        "docs/special_agents_redesign/agents/complex_problem_solution_process_model.md",
        "specials.complex-problem-solution-process-model",
    ),
    SpecialSourceEntry(
        "docs/special_agents_redesign/agents/controller_agent.md",
        "specials.controller-agent",
    ),
    SpecialSourceEntry(
        "docs/special_agents_redesign/agents/general_creative_agent.md",
        "specials.general-creative-agent",
    ),
    SpecialSourceEntry(
        "docs/special_agents_redesign/agents/intent_analysis_agent.md",
        "specials.intent-analysis-agent",
    ),
    SpecialSourceEntry(
        "docs/special_agents_redesign/agents/knowledge_router_agent.md",
        "specials.knowledge-router-agent",
    ),
    SpecialSourceEntry(
        "docs/special_agents_redesign/agents/llm_usage.md",
        "specials.llm-usage",
    ),
    SpecialSourceEntry(
        "docs/special_agents_redesign/agents/optimization_agent.md",
        "specials.optimization-agent",
    ),
    SpecialSourceEntry(
        "docs/special_agents_redesign/agents/planner_agent.md",
        "specials.planner-agent",
    ),
    SpecialSourceEntry(
        "docs/special_agents_redesign/agents/podcast_agent.md",
        "specials.podcast-agent",
    ),
    SpecialSourceEntry(
        "docs/special_agents_redesign/agents/psychological_profile_agent.md",
        "specials.psychological-profile-agent",
    ),
    SpecialSourceEntry(
        "docs/special_agents_redesign/agents/psychological_recommendation_agent.md",
        "specials.psychological-recommendation-agent",
    ),
    SpecialSourceEntry(
        "docs/special_agents_redesign/agents/research_agent.md",
        "specials.research-agent",
    ),
    SpecialSourceEntry(
        "docs/special_agents_redesign/agents/screenwriter_strategic_goal_achievement_agent.md",
        "specials.screenwriter-strategic-goal-achievement-agent",
    ),
    SpecialSourceEntry(
        "docs/special_agents_redesign/agents/strategic_goal_achievement_agent.md",
        "specials.strategic-goal-achievement-agent",
    ),
    SpecialSourceEntry(
        "docs/special_agents_redesign/agents/techology_advisor_agent.md",
        "specials.techology-advisor-agent",
    ),
)

SPECIAL_AGENT_IDS: Final[tuple[CanonicalAgentId, ...]] = tuple(
    entry.agent_id for entry in SPECIAL_SOURCE_CATALOG
)
SPECIAL_SOURCE_PATHS: Final[tuple[str, ...]] = tuple(
    entry.source_path for entry in SPECIAL_SOURCE_CATALOG
)
SPECIAL_AGENT_SPEC_PATHS: Final[tuple[str, ...]] = tuple(
    f"{SPECIALS_PACK_ROOT}/agents/{entry.agent_id}/agent_spec.json"
    for entry in SPECIAL_SOURCE_CATALOG
)
SPECIALS_ALLOWLIST_PATHS: Final[frozenset[str]] = frozenset(
    {
        SPECIALS_SCHEMA_PATH,
        SPECIALS_MANIFEST_PATH,
        SPECIALS_INVENTORY_PATH,
        *SPECIAL_SOURCE_PATHS,
        *SPECIAL_AGENT_SPEC_PATHS,
    }
)
SPECIAL_SOURCE_BY_AGENT_ID: Final[Mapping[str, SpecialSourceEntry]] = MappingProxyType(
    {entry.agent_id: entry for entry in SPECIAL_SOURCE_CATALOG}
)
SPECIAL_SOURCE_BY_PATH: Final[Mapping[str, SpecialSourceEntry]] = MappingProxyType(
    {entry.source_path: entry for entry in SPECIAL_SOURCE_CATALOG}
)
# These aliases make the catalog name explicit for callers that use the
# terminology from the requirements document.
SOURCE_INVENTORY: Final[tuple[SpecialSourceEntry, ...]] = SPECIAL_SOURCE_CATALOG
CANONICAL_SPECIAL_AGENT_IDS: Final[tuple[CanonicalAgentId, ...]] = SPECIAL_AGENT_IDS
SPECIALS_SOURCE_CATALOG: Final[tuple[SpecialSourceEntry, ...]] = SPECIAL_SOURCE_CATALOG
SPECIALS_SOURCE_PATHS: Final[tuple[str, ...]] = SPECIAL_SOURCE_PATHS


class DuplicateJsonKeyError(ValueError):
    """Raised when a JSON object contains a key more than once."""


class InvalidRepositoryPathError(ValueError):
    """Raised when a path is not normalized repository-relative input."""


InvalidRepositoryPath = InvalidRepositoryPathError


def is_canonical_agent_id(value: object) -> bool:
    """Return whether *value* is an anchored ``specials.*`` canonical ID."""
    return isinstance(value, str) and _CANONICAL_AGENT_ID_RE.fullmatch(value) is not None


def is_special_agent_asset_id(value: object) -> bool:
    """Return whether *value* is an anchored ``spagent.*`` asset reference."""
    return isinstance(value, str) and _SPECIAL_AGENT_ASSET_ID_RE.fullmatch(value) is not None


def is_valid_canonical_agent_id(value: object) -> bool:
    """Descriptive alias for :func:`is_canonical_agent_id`."""
    return is_canonical_agent_id(value)


def is_valid_special_agent_asset_id(value: object) -> bool:
    """Descriptive alias for :func:`is_special_agent_asset_id`."""
    return is_special_agent_asset_id(value)


def canonical_agent_spec_path(agent_id: str) -> str:
    """Build the exact pack-relative path for a canonical agent ID.

    Invalid IDs are rejected instead of being interpolated into a path.  This
    keeps path construction itself a namespace and traversal boundary.
    """
    if not is_canonical_agent_id(agent_id):
        raise ValueError(f"Invalid Special_Agent canonical ID: {agent_id!r}")
    return f"agents/{agent_id}/agent_spec.json"


def canonical_spec_path(agent_id: str) -> str:
    """Compatibility alias for :func:`canonical_agent_spec_path`."""
    return canonical_agent_spec_path(agent_id)


def source_for_agent_id(agent_id: str) -> SpecialSourceEntry | None:
    """Look up a fixed source mapping without consulting the filesystem."""
    return SPECIAL_SOURCE_BY_AGENT_ID.get(agent_id)


def source_for_path(source_path: str | Path) -> SpecialSourceEntry | None:
    """Look up a fixed source mapping using a normalized relative path."""
    try:
        normalized = normalize_repository_relative_path(source_path)
    except (InvalidRepositoryPathError, TypeError):
        return None
    return SPECIAL_SOURCE_BY_PATH.get(normalized)


def normalize_repository_relative_path(value: str | Path) -> str:
    """Normalize a forward-slash repository-relative path or raise.

    Absolute paths, drive-qualified Windows paths, empty segments, ``.``
    segments, and traversal segments are rejected before filesystem access.
    """
    text = value.as_posix() if isinstance(value, Path) else value
    if not isinstance(text, str) or not text or "\\" in text:
        raise InvalidRepositoryPathError("Path must be a non-empty forward-slash string.")
    if PurePosixPath(text).is_absolute() or PureWindowsPath(text).is_absolute():
        raise InvalidRepositoryPathError("Absolute paths are not repository-relative.")
    if PureWindowsPath(text).drive:
        raise InvalidRepositoryPathError("Drive-qualified paths are not repository-relative.")
    parts = text.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise InvalidRepositoryPathError("Path contains an invalid segment.")
    normalized = str(PurePosixPath(*parts))
    if normalized != text:
        raise InvalidRepositoryPathError("Path is not normalized.")
    return normalized


def is_normalized_repository_relative_path(value: object) -> bool:
    """Return whether *value* passes the repository-relative path contract."""
    if not isinstance(value, (str, Path)):
        return False
    try:
        normalize_repository_relative_path(value)
    except (InvalidRepositoryPathError, TypeError):
        return False
    return True


def canonical_json_text(value: object) -> str:
    """Serialize JSON with stable keys, UTF-8-safe text, and no whitespace."""
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def canonical_json_bytes(value: object) -> bytes:
    """Serialize JSON to the canonical UTF-8 byte representation."""
    return canonical_json_text(value).encode("utf-8")


def serialize_canonical_json(value: object) -> bytes:
    """Descriptive alias for :func:`canonical_json_bytes`."""
    return canonical_json_bytes(value)


def _reject_duplicate_json_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateJsonKeyError(f"Duplicate JSON object key: {key}")
        result[key] = value
    return result


def decode_json_no_duplicates(payload: bytes | str) -> object:
    """Decode UTF-8 JSON while rejecting duplicate object keys."""
    text = payload.decode("utf-8") if isinstance(payload, bytes) else payload
    return json.loads(
        text,
        object_pairs_hook=_reject_duplicate_json_pairs,
        parse_constant=lambda value: (_ for _ in ()).throw(
            ValueError(f"Non-finite JSON constant is not permitted: {value}")
        ),
    )


def loads_rejecting_duplicate_keys(payload: bytes | str) -> object:
    """Compatibility alias for :func:`decode_json_no_duplicates`."""
    return decode_json_no_duplicates(payload)


def sha256_bytes(payload: bytes) -> str:
    """Return a lowercase SHA-256 digest for exact bytes."""
    return hashlib.sha256(payload).hexdigest()


def sha256_text(value: str) -> str:
    """Return a lowercase SHA-256 digest for UTF-8 text."""
    return sha256_bytes(value.encode("utf-8"))


def sha256_file(path: Path | str) -> str:
    """Hash a local file's bytes without interpreting its contents."""
    return sha256_bytes(Path(path).read_bytes())


def sha256_json(value: object) -> str:
    """Hash the canonical UTF-8 representation of a JSON value."""
    return sha256_bytes(canonical_json_bytes(value))


def is_sha256_digest(value: object) -> bool:
    """Return whether *value* is a lowercase 64-character SHA-256 digest."""
    return isinstance(value, str) and _SHA256_RE.fullmatch(value) is not None


@dataclass(frozen=True, slots=True)
class ValidationFinding:
    """Stable, non-secret validation evidence for one failed condition."""

    category: FindingCategory
    path: str
    code: str
    agent_id: str | None = None

    def as_dict(self) -> dict[str, str]:
        """Return the canonical JSON representation of this finding."""
        result = {"category": self.category, "path": self.path, "code": self.code}
        if self.agent_id is not None:
            result["agent_id"] = self.agent_id
        return result

    to_dict = as_dict


Finding = ValidationFinding


@dataclass(frozen=True, slots=True)
class FileValidationResult:
    """Digest and parse result for one explicitly allowlisted file."""

    path: str
    sha256: str
    schema: SchemaResult

    def as_dict(self) -> dict[str, str]:
        """Return the canonical JSON representation of this result."""
        return {"path": self.path, "sha256": self.sha256, "schema": self.schema}

    to_dict = as_dict


@dataclass(frozen=True, slots=True)
class SectionValidationResult:
    """Result and optional digest for a pack section."""

    result: Literal["pass", "fail"]
    digest: str = ""

    def as_dict(self) -> dict[str, str]:
        """Return the canonical JSON representation of this result."""
        return {"result": self.result, "digest": self.digest}

    to_dict = as_dict


@dataclass(frozen=True, slots=True)
class InventoryValidationResult:
    """Conditional inventory validation result."""

    required: bool
    result: InventoryResult

    def as_dict(self) -> dict[str, bool | str]:
        """Return the canonical JSON representation of this result."""
        return {"required": self.required, "result": self.result}

    to_dict = as_dict


@dataclass(frozen=True, slots=True)
class AcceptedSpecialAgent:
    """An immutable, previously accepted draft representation."""

    agent_id: CanonicalAgentId
    configuration_sha256: str = ""
    source_sha256: str = ""


@dataclass(frozen=True, slots=True)
class AcceptedSpecialsState:
    """Pure validator state; rejected proposals never replace this snapshot."""

    agents: tuple[AcceptedSpecialAgent, ...] = ()
    validation_report_digest: str = ""

    @property
    def agent_ids(self) -> tuple[CanonicalAgentId, ...]:
        """Return accepted IDs in lexical order."""
        return tuple(sorted(agent.agent_id for agent in self.agents))


SpecialsState = AcceptedSpecialsState
ValidatorState = AcceptedSpecialsState


@dataclass(frozen=True, slots=True)
class ValidationReport:
    """Deterministic validation output with no runtime or activation effect."""

    format_version: str
    validation_outcome: ValidationOutcome
    accepted_agent_ids: tuple[CanonicalAgentId, ...]
    rejected_agent_ids: tuple[CanonicalAgentId, ...]
    files: tuple[FileValidationResult, ...]
    manifest: SectionValidationResult
    inventory: InventoryValidationResult
    provenance: SectionValidationResult
    risk_gate: SectionValidationResult
    report_retention: ReportRetention
    registration_effect: RegistrationEffect
    findings: tuple[ValidationFinding, ...]
    configuration_set_digest: str
    accepted_state: AcceptedSpecialsState = AcceptedSpecialsState()

    @property
    def is_valid(self) -> bool:
        """Return whether the proposed pack passed all foundation checks."""
        return self.validation_outcome == "pass"

    def as_dict(self) -> dict[str, object]:
        """Return the report contract as canonical-JSON-compatible data."""
        ordered_files = tuple(sorted(self.files, key=lambda file_result: file_result.path))
        ordered_findings = _sort_findings(self.findings)
        return {
            "format_version": self.format_version,
            "validation_outcome": self.validation_outcome,
            "accepted_agent_ids": sorted(self.accepted_agent_ids),
            "rejected_agent_ids": sorted(self.rejected_agent_ids),
            "files": [file_result.as_dict() for file_result in ordered_files],
            "manifest": self.manifest.as_dict(),
            "inventory": self.inventory.as_dict(),
            "provenance": self.provenance.as_dict(),
            "risk_gate": self.risk_gate.as_dict(),
            "report_retention": self.report_retention,
            "registration_effect": self.registration_effect,
            "findings": [finding.as_dict() for finding in ordered_findings],
            "configuration_set_digest": self.configuration_set_digest,
        }

    to_dict = as_dict

    def canonical_bytes(self) -> bytes:
        """Return stable UTF-8 bytes suitable for local evidence retention."""
        return canonical_json_bytes(self.as_dict())

    def canonical_json(self) -> bytes:
        """Compatibility alias for :meth:`canonical_bytes`."""
        return self.canonical_bytes()


@dataclass(frozen=True, slots=True)
class _LoadedFile:
    path: str
    raw_bytes: bytes
    value: object | None
    schema: SchemaResult


def _display_invalid_path() -> str:
    """Use a stable redacted path for invalid input, never an absolute path."""
    return "<invalid-path>"


def _sort_findings(findings: Iterable[ValidationFinding]) -> tuple[ValidationFinding, ...]:
    return tuple(
        sorted(
            findings,
            key=lambda finding: (
                finding.category,
                finding.path,
                finding.code,
                finding.agent_id or "",
            ),
        )
    )


def _is_contained_regular_file(root: Path, relative_path: str) -> tuple[Path | None, str | None]:
    """Resolve an allowlisted path and return a stable path error code if unsafe."""
    try:
        root_resolved = root.resolve()
        candidate = root / Path(relative_path)
        if candidate.is_symlink():
            return None, "SYMLINK_PATH"

        current = root
        for part in PurePosixPath(relative_path).parts:
            current = current / part
            if current.is_symlink():
                return None, "SYMLINK_PATH"

        resolved = candidate.resolve(strict=False)
        try:
            resolved.relative_to(root_resolved)
        except ValueError:
            return None, "PATH_ESCAPE"
        if not resolved.exists():
            return None, "MISSING_FILE"
        if not resolved.is_file():
            return None, "NOT_REGULAR_FILE"
        return resolved, None
    except (OSError, RuntimeError, ValueError):
        return None, "PATH_ESCAPE"


def _is_governance_path_allowed(relative_path: str) -> bool:
    """Return whether *relative_path* is a supported governance-record path."""
    for root, suffix in (
        (SPECIALS_SOURCE_RECORD_ROOT, ".json"),
        (SPECIALS_RISK_ASSESSMENT_ROOT, ".json"),
        (SPECIALS_APPROVAL_ROOT, ".json"),
    ):
        prefix = f"{root}/"
        if relative_path.startswith(prefix) and relative_path.endswith(suffix):
            filename = relative_path.removeprefix(prefix)
            return filename != "" and "/" not in filename
    return False


def _path_is_allowed(relative_path: str) -> bool:
    """Return whether a normalized path belongs to the explicit specials allowlist."""
    return relative_path in SPECIALS_ALLOWLIST_PATHS or _is_governance_path_allowed(relative_path)


def _load_allowlisted_files(
    root: Path, allowlisted_paths: Iterable[Path | str]
) -> tuple[tuple[_LoadedFile, ...], list[ValidationFinding]]:
    """Preflight every path before reading any allowlisted file."""
    loaded: list[_LoadedFile] = []
    findings: list[ValidationFinding] = []
    seen: set[str] = set()
    candidates: list[tuple[str, Path]] = []

    for raw_path in allowlisted_paths:
        try:
            relative_path = normalize_repository_relative_path(raw_path)
        except (InvalidRepositoryPathError, TypeError):
            findings.append(ValidationFinding("path", _display_invalid_path(), "INVALID_PATH"))
            continue
        if relative_path in seen:
            findings.append(ValidationFinding("path", relative_path, "DUPLICATE_ALLOWLIST_PATH"))
            continue
        seen.add(relative_path)
        if not _path_is_allowed(relative_path):
            findings.append(ValidationFinding("path", relative_path, "UNALLOWLISTED_PATH"))
            continue

        resolved, error_code = _is_contained_regular_file(root, relative_path)
        if error_code is not None or resolved is None:
            category: FindingCategory = (
                "io" if error_code in {"MISSING_FILE", "NOT_REGULAR_FILE"} else "path"
            )
            findings.append(
                ValidationFinding(category, relative_path, error_code or "INVALID_PATH")
            )
            continue
        candidates.append((relative_path, resolved))

    # Path safety and allowlist membership are complete before any file bytes
    # are read.  Source Markdown is intentionally never parsed as JSON.
    for relative_path, resolved in candidates:
        try:
            raw_bytes = resolved.read_bytes()
        except (OSError, RuntimeError):
            findings.append(ValidationFinding("io", relative_path, "UNREADABLE_FILE"))
            continue

        value: object | None = None
        schema: SchemaResult = "pass"
        if relative_path.endswith(".json"):
            try:
                value = decode_json_no_duplicates(raw_bytes)
                if not isinstance(value, dict):
                    schema = "fail"
                    findings.append(
                        ValidationFinding("schema", relative_path, "JSON_ROOT_NOT_OBJECT")
                    )
            except (UnicodeDecodeError, json.JSONDecodeError, DuplicateJsonKeyError, ValueError):
                schema = "fail"
                findings.append(ValidationFinding("schema", relative_path, "MALFORMED_JSON"))
        loaded.append(_LoadedFile(relative_path, raw_bytes, value, schema))

    return tuple(sorted(loaded, key=lambda file: file.path)), findings


def _mapping_value(value: object | None) -> Mapping[str, object] | None:
    return value if isinstance(value, Mapping) else None


def _check_closed_object(
    value: Mapping[str, object],
    required: frozenset[str],
    path: str,
    findings: list[ValidationFinding],
) -> None:
    """Report missing and unsupported keys for a closed JSON object."""
    for key in sorted(required - set(value)):
        findings.append(ValidationFinding("schema", path, f"MISSING_{key.upper()}"))
    for key in sorted(set(value) - required):
        findings.append(ValidationFinding("schema", f"{path}.{key}", "UNSUPPORTED_FIELD"))


def _asset_namespace_finding(
    value: object,
    path: str,
    findings: list[ValidationFinding],
    agent_id: str | None = None,
) -> None:
    """Validate one declared Special_Agent_Asset value without coercion."""
    if is_special_agent_asset_id(value):
        return
    code = "NAMESPACE_CROSSOVER" if is_canonical_agent_id(value) else "INVALID_ASSET_ID"
    findings.append(ValidationFinding("asset_namespace", path, code, agent_id))


def _schema_profile_checks(
    schema_file: _LoadedFile | None, findings: list[ValidationFinding]
) -> None:
    """Validate the checked-in pack-local schema profile before specifications."""
    if schema_file is None:
        findings.append(ValidationFinding("integrity", SPECIALS_SCHEMA_PATH, "MISSING_SCHEMA"))
        return
    if schema_file.schema == "fail":
        findings.append(ValidationFinding("schema", SPECIALS_SCHEMA_PATH, "INVALID_SCHEMA"))
        return
    schema = _mapping_value(schema_file.value)
    if schema is None:
        findings.append(ValidationFinding("schema", SPECIALS_SCHEMA_PATH, "INVALID_SCHEMA"))
        return

    required_top_level = frozenset(
        {
            "$id",
            "title",
            "type",
            "required",
            "properties",
            "$defs",
            "additionalProperties",
        }
    )
    _check_closed_object(schema, required_top_level, SPECIALS_SCHEMA_PATH, findings)
    if schema.get("$id") != "special-agent-spec.schema.json":
        findings.append(ValidationFinding("schema", SPECIALS_SCHEMA_PATH, "INVALID_SCHEMA_ID"))
    if schema.get("type") != "object" or schema.get("additionalProperties") is not False:
        findings.append(ValidationFinding("schema", SPECIALS_SCHEMA_PATH, "INVALID_SCHEMA_OBJECT"))

    required_fields = {
        "schema_version",
        "agent_id",
        "status",
        "role",
        "allowed_tools",
        "model_policy",
        "budget_policy",
        "prompt_reference",
        "rubric_reference",
        "critique_edges",
        "max_refinement_count",
        "production_activation_requested",
    }
    raw_required = schema.get("required")
    raw_required_is_valid = isinstance(raw_required, list) and all(
        isinstance(item, str) for item in raw_required
    )
    if (
        not raw_required_is_valid
        or len(cast(list[str], raw_required)) != len(required_fields)
        or set(cast(list[str], raw_required)) != required_fields
    ):
        findings.append(
            ValidationFinding("schema", SPECIALS_SCHEMA_PATH, "INVALID_REQUIRED_FIELDS")
        )

    properties = _mapping_value(schema.get("properties"))
    if properties is None or set(properties) != required_fields:
        findings.append(
            ValidationFinding("schema", SPECIALS_SCHEMA_PATH, "INVALID_SCHEMA_PROPERTIES")
        )

    definitions = _mapping_value(schema.get("$defs"))
    if definitions is None:
        findings.append(
            ValidationFinding("schema", SPECIALS_SCHEMA_PATH, "MISSING_SCHEMA_DEFINITIONS")
        )
        return
    for definition_name, expected_pattern in (
        ("CanonicalAgentId", _CANONICAL_AGENT_ID_RE.pattern),
        ("SpecialAgentAssetId", _SPECIAL_AGENT_ASSET_ID_RE.pattern),
    ):
        definition = _mapping_value(definitions.get(definition_name))
        if definition is None:
            findings.append(
                ValidationFinding(
                    "schema",
                    f"{SPECIALS_SCHEMA_PATH}#/$defs/{definition_name}",
                    "MISSING_SCHEMA_DEFINITION",
                )
            )
            continue
        if definition.get("type") != "string" or definition.get("pattern") != expected_pattern:
            findings.append(
                ValidationFinding(
                    "schema",
                    f"{SPECIALS_SCHEMA_PATH}#/$defs/{definition_name}",
                    "INVALID_SCHEMA_DEFINITION",
                )
            )


def _manifest_checks(
    manifest_file: _LoadedFile | None,
    loaded_by_path: Mapping[str, _LoadedFile],
    findings: list[ValidationFinding],
) -> tuple[SectionValidationResult, InventoryValidationResult, set[str]]:
    if manifest_file is None:
        findings.append(ValidationFinding("integrity", SPECIALS_MANIFEST_PATH, "MISSING_MANIFEST"))
        return (
            SectionValidationResult("fail"),
            InventoryValidationResult(False, "not_required"),
            set(),
        )
    manifest = _mapping_value(manifest_file.value)
    if manifest is None or manifest_file.schema == "fail":
        findings.append(ValidationFinding("schema", SPECIALS_MANIFEST_PATH, "INVALID_MANIFEST"))
        return (
            SectionValidationResult("fail", sha256_bytes(manifest_file.raw_bytes)),
            InventoryValidationResult(False, "not_required"),
            set(),
        )

    manifest_path = SPECIALS_MANIFEST_PATH
    _check_closed_object(
        manifest,
        frozenset({"pack_id", "agents", "production_activation_requested", "inventory_required"}),
        manifest_path,
        findings,
    )
    if manifest.get("pack_id") != SPECIALS_PACK_ID:
        findings.append(ValidationFinding("integrity", manifest_path, "INVALID_PACK_ID"))
    if manifest.get("production_activation_requested") is not False:
        findings.append(
            ValidationFinding("schema", manifest_path, "PRODUCTION_ACTIVATION_REQUESTED")
        )

    raw_agents = manifest.get("agents")
    agent_ids: list[str] = []
    manifest_entries: dict[str, Mapping[str, object]] = {}
    if not isinstance(raw_agents, list):
        findings.append(ValidationFinding("schema", manifest_path, "INVALID_AGENT_LIST"))
    else:
        required_entry_fields = frozenset(
            {
                "agent_id",
                "status",
                "allowed_tools",
                "production_activation_requested",
                "agent_spec_path",
            }
        )
        for index, raw_agent in enumerate(raw_agents):
            agent_path = f"{manifest_path}#agents[{index}]"
            if not isinstance(raw_agent, Mapping):
                findings.append(ValidationFinding("schema", agent_path, "INVALID_AGENT_ENTRY"))
                continue
            entry = cast(Mapping[str, object], raw_agent)
            _check_closed_object(entry, required_entry_fields, agent_path, findings)
            raw_agent_id = entry.get("agent_id")
            if not is_canonical_agent_id(raw_agent_id):
                code = (
                    "NAMESPACE_CROSSOVER"
                    if is_special_agent_asset_id(raw_agent_id)
                    else "INVALID_AGENT_ID"
                )
                findings.append(ValidationFinding("asset_namespace", agent_path, code))
                continue
            agent_id = cast(str, raw_agent_id)
            agent_ids.append(agent_id)
            manifest_entries[agent_id] = entry
            if entry.get("status") != "draft":
                findings.append(ValidationFinding("schema", agent_path, "INVALID_STATUS", agent_id))
            if entry.get("allowed_tools") != []:
                findings.append(
                    ValidationFinding("schema", agent_path, "TOOLS_NOT_EMPTY", agent_id)
                )
            if entry.get("production_activation_requested") is not False:
                findings.append(
                    ValidationFinding(
                        "schema", agent_path, "PRODUCTION_ACTIVATION_REQUESTED", agent_id
                    )
                )

            raw_spec_path = entry.get("agent_spec_path")
            if not isinstance(raw_spec_path, str) or not is_normalized_repository_relative_path(
                raw_spec_path
            ):
                findings.append(ValidationFinding("path", agent_path, "INVALID_PATH", agent_id))
            elif raw_spec_path != canonical_agent_spec_path(agent_id):
                findings.append(
                    ValidationFinding("integrity", agent_path, "NON_CANONICAL_SPEC_PATH", agent_id)
                )
            else:
                expected_path = f"{SPECIALS_PACK_ROOT}/{raw_spec_path}"
                if expected_path not in loaded_by_path:
                    findings.append(
                        ValidationFinding(
                            "integrity", expected_path, "MISSING_AGENT_SPEC", agent_id
                        )
                    )

    if len(agent_ids) != len(set(agent_ids)):
        findings.append(ValidationFinding("integrity", manifest_path, "DUPLICATE_AGENT_ID"))
    if set(agent_ids) != set(SPECIAL_AGENT_IDS) or len(agent_ids) != len(SPECIAL_AGENT_IDS):
        findings.append(ValidationFinding("integrity", manifest_path, "CATALOG_MISMATCH"))

    expected_paths = set(SPECIAL_AGENT_SPEC_PATHS)
    for loaded_path in loaded_by_path:
        if (
            loaded_path.startswith(f"{SPECIALS_PACK_ROOT}/agents/")
            and loaded_path.endswith("/agent_spec.json")
            and loaded_path not in expected_paths
        ):
            findings.append(ValidationFinding("integrity", loaded_path, "EXTRA_AGENT_SPEC"))

    inventory_required = manifest.get("inventory_required")
    if not isinstance(inventory_required, bool):
        findings.append(ValidationFinding("schema", manifest_path, "INVALID_INVENTORY_FLAG"))
        inventory_required = False

    inventory_file = loaded_by_path.get(SPECIALS_INVENTORY_PATH)
    if not inventory_required:
        if inventory_file is not None:
            findings.append(
                ValidationFinding("integrity", SPECIALS_INVENTORY_PATH, "UNEXPECTED_INVENTORY")
            )
        manifest_result: Literal["pass", "fail"] = (
            "fail"
            if any(
                finding.path == manifest_path or finding.path.startswith(f"{manifest_path}#")
                for finding in findings
            )
            else "pass"
        )
        return (
            SectionValidationResult(manifest_result, sha256_bytes(manifest_file.raw_bytes)),
            InventoryValidationResult(False, "not_required"),
            set(agent_ids),
        )

    if inventory_file is None:
        findings.append(
            ValidationFinding("integrity", SPECIALS_INVENTORY_PATH, "MISSING_INVENTORY")
        )
        inventory_result: InventoryResult = "fail"
    elif inventory_file.schema == "fail":
        findings.append(ValidationFinding("schema", SPECIALS_INVENTORY_PATH, "INVALID_INVENTORY"))
        inventory_result = "fail"
    else:
        inventory = _mapping_value(inventory_file.value)
        if inventory is None:
            findings.append(
                ValidationFinding("schema", SPECIALS_INVENTORY_PATH, "INVALID_INVENTORY")
            )
            inventory_result = "fail"
        else:
            _check_closed_object(
                inventory, frozenset({"entries"}), SPECIALS_INVENTORY_PATH, findings
            )
            raw_entries = inventory.get("entries")
            inventory_ids: list[str] = []
            inventory_entries: dict[str, Mapping[str, object]] = {}
            if not isinstance(raw_entries, list):
                findings.append(
                    ValidationFinding("schema", SPECIALS_INVENTORY_PATH, "INVALID_INVENTORY")
                )
            else:
                entry_fields = frozenset({"agent_id", "status", "agent_spec_path"})
                for index, raw_entry in enumerate(raw_entries):
                    entry_path = f"{SPECIALS_INVENTORY_PATH}#entries[{index}]"
                    if not isinstance(raw_entry, Mapping):
                        findings.append(
                            ValidationFinding("schema", entry_path, "INVALID_INVENTORY_ENTRY")
                        )
                        continue
                    entry = cast(Mapping[str, object], raw_entry)
                    _check_closed_object(entry, entry_fields, entry_path, findings)
                    raw_id = entry.get("agent_id")
                    if not is_canonical_agent_id(raw_id):
                        code = (
                            "NAMESPACE_CROSSOVER"
                            if is_special_agent_asset_id(raw_id)
                            else "INVALID_INVENTORY_AGENT_ID"
                        )
                        findings.append(ValidationFinding("asset_namespace", entry_path, code))
                        continue
                    agent_id = cast(str, raw_id)
                    inventory_ids.append(agent_id)
                    inventory_entries[agent_id] = entry
                    if entry.get("status") != "draft":
                        findings.append(
                            ValidationFinding("schema", entry_path, "INVALID_STATUS", agent_id)
                        )
                    if entry.get("agent_spec_path") != canonical_agent_spec_path(agent_id):
                        findings.append(
                            ValidationFinding(
                                "integrity", entry_path, "NON_CANONICAL_SPEC_PATH", agent_id
                            )
                        )

                if len(inventory_ids) != len(set(inventory_ids)):
                    findings.append(
                        ValidationFinding(
                            "integrity", SPECIALS_INVENTORY_PATH, "DUPLICATE_AGENT_ID"
                        )
                    )
                if set(inventory_ids) != set(agent_ids) or len(inventory_ids) != len(agent_ids):
                    findings.append(
                        ValidationFinding(
                            "integrity", SPECIALS_INVENTORY_PATH, "INVENTORY_MISMATCH"
                        )
                    )
                for agent_id in set(agent_ids) & set(inventory_entries):
                    manifest_entry = manifest_entries[agent_id]
                    inventory_entry = inventory_entries[agent_id]
                    if inventory_entry.get("status") != manifest_entry.get(
                        "status"
                    ) or inventory_entry.get("agent_spec_path") != manifest_entry.get(
                        "agent_spec_path"
                    ):
                        findings.append(
                            ValidationFinding(
                                "integrity", SPECIALS_INVENTORY_PATH, "INVENTORY_MISMATCH", agent_id
                            )
                        )

            inventory_result = (
                "fail"
                if any(
                    finding.path == SPECIALS_INVENTORY_PATH
                    or finding.path.startswith(f"{SPECIALS_INVENTORY_PATH}#")
                    for finding in findings
                )
                else "pass"
            )

    manifest_result = (
        "fail"
        if any(
            finding.path == manifest_path or finding.path.startswith(f"{manifest_path}#")
            for finding in findings
        )
        else "pass"
    )
    return (
        SectionValidationResult(manifest_result, sha256_bytes(manifest_file.raw_bytes)),
        InventoryValidationResult(True, inventory_result),
        set(agent_ids),
    )


def _validate_agent_specification(
    relative_path: str,
    agent_id: str,
    data: Mapping[str, object],
    findings: list[ValidationFinding],
) -> None:
    """Validate one specification against the closed data-only profile."""
    _check_closed_object(
        data,
        frozenset(
            {
                "schema_version",
                "agent_id",
                "status",
                "role",
                "allowed_tools",
                "model_policy",
                "budget_policy",
                "prompt_reference",
                "rubric_reference",
                "critique_edges",
                "max_refinement_count",
                "production_activation_requested",
            }
        ),
        relative_path,
        findings,
    )
    if data.get("schema_version") != SPECIALS_SCHEMA_VERSION:
        findings.append(
            ValidationFinding("schema", relative_path, "INVALID_SCHEMA_VERSION", agent_id)
        )
    raw_spec_agent_id = data.get("agent_id")
    if raw_spec_agent_id != agent_id:
        code = (
            "NAMESPACE_CROSSOVER"
            if is_special_agent_asset_id(raw_spec_agent_id)
            else "AGENT_ID_PATH_MISMATCH"
        )
        category: FindingCategory = (
            "asset_namespace" if code == "NAMESPACE_CROSSOVER" else "integrity"
        )
        findings.append(ValidationFinding(category, relative_path, code, agent_id))
    if data.get("status") != "draft":
        findings.append(ValidationFinding("schema", relative_path, "INVALID_STATUS", agent_id))
    if not isinstance(data.get("role"), str) or not cast(str, data.get("role")).strip():
        findings.append(ValidationFinding("schema", relative_path, "INVALID_ROLE", agent_id))

    allowed_tools = data.get("allowed_tools")
    if allowed_tools != []:
        findings.append(ValidationFinding("schema", relative_path, "TOOLS_NOT_EMPTY", agent_id))
    if isinstance(allowed_tools, list):
        tool_values = [tool for tool in allowed_tools if isinstance(tool, str)]
        if len(tool_values) != len(set(tool_values)):
            findings.append(
                ValidationFinding("schema", relative_path, "DUPLICATE_ALLOWED_TOOL", agent_id)
            )
    else:
        findings.append(
            ValidationFinding("schema", relative_path, "INVALID_ALLOWED_TOOLS", agent_id)
        )

    model_policy = _mapping_value(data.get("model_policy"))
    if model_policy is None:
        findings.append(
            ValidationFinding("schema", relative_path, "INVALID_MODEL_POLICY", agent_id)
        )
    else:
        _check_closed_object(
            model_policy,
            frozenset({"provider", "model_id", "network_access"}),
            relative_path,
            findings,
        )
        if model_policy.get("provider") != "local_deterministic":
            findings.append(
                ValidationFinding("schema", relative_path, "INVALID_PROVIDER", agent_id)
            )
        if (
            not isinstance(model_policy.get("model_id"), str)
            or not cast(str, model_policy.get("model_id")).strip()
        ):
            findings.append(
                ValidationFinding("schema", relative_path, "INVALID_MODEL_ID", agent_id)
            )
        if model_policy.get("network_access") is not False:
            findings.append(
                ValidationFinding("schema", relative_path, "NETWORK_ACCESS_ENABLED", agent_id)
            )

    budget_policy = _mapping_value(data.get("budget_policy"))
    if budget_policy is None:
        findings.append(
            ValidationFinding("schema", relative_path, "INVALID_BUDGET_POLICY", agent_id)
        )
    else:
        _check_closed_object(
            budget_policy,
            frozenset({"max_input_tokens", "max_output_tokens", "max_tool_requests"}),
            relative_path,
            findings,
        )
        for field in ("max_input_tokens", "max_output_tokens"):
            value = budget_policy.get(field)
            if not isinstance(value, int) or isinstance(value, bool) or value < 1:
                findings.append(
                    ValidationFinding("schema", relative_path, f"INVALID_{field.upper()}", agent_id)
                )
        if budget_policy.get("max_tool_requests") != 0:
            findings.append(
                ValidationFinding("schema", relative_path, "TOOL_REQUESTS_NOT_ZERO", agent_id)
            )

    _asset_namespace_finding(data.get("prompt_reference"), relative_path, findings, agent_id)
    _asset_namespace_finding(data.get("rubric_reference"), relative_path, findings, agent_id)
    critique_edges = _mapping_value(data.get("critique_edges"))
    if critique_edges is None:
        findings.append(
            ValidationFinding("schema", relative_path, "INVALID_CRITIQUE_EDGES", agent_id)
        )
    else:
        _check_closed_object(
            critique_edges, frozenset({"inputs", "outputs"}), relative_path, findings
        )
        for edge_name in ("inputs", "outputs"):
            edges = critique_edges.get(edge_name)
            if not isinstance(edges, list) or not edges:
                findings.append(
                    ValidationFinding("schema", relative_path, "INVALID_CRITIQUE_EDGES", agent_id)
                )
                continue
            if not all(isinstance(edge, str) for edge in edges):
                findings.append(
                    ValidationFinding("schema", relative_path, "INVALID_CRITIQUE_EDGES", agent_id)
                )
            elif len(edges) != len(set(edges)):
                findings.append(
                    ValidationFinding("schema", relative_path, "DUPLICATE_CRITIQUE_EDGE", agent_id)
                )
            for edge in edges:
                _asset_namespace_finding(edge, relative_path, findings, agent_id)

    max_refinement_count = data.get("max_refinement_count")
    if (
        not isinstance(max_refinement_count, int)
        or isinstance(max_refinement_count, bool)
        or not 1 <= max_refinement_count <= 3
    ):
        findings.append(
            ValidationFinding("schema", relative_path, "INVALID_REFINEMENT_COUNT", agent_id)
        )
    if data.get("production_activation_requested") is not False:
        findings.append(
            ValidationFinding("schema", relative_path, "PRODUCTION_ACTIVATION_REQUESTED", agent_id)
        )


def _specification_checks(
    loaded_by_path: Mapping[str, _LoadedFile], findings: list[ValidationFinding]
) -> set[str]:
    """Validate all and only the fixed canonical specification projections."""
    specification_ids: set[str] = set()
    for agent_id in SPECIAL_AGENT_IDS:
        relative_path = f"{SPECIALS_PACK_ROOT}/{canonical_agent_spec_path(agent_id)}"
        specification = loaded_by_path.get(relative_path)
        if specification is None:
            findings.append(
                ValidationFinding("integrity", relative_path, "MISSING_AGENT_SPEC", agent_id)
            )
            continue
        if specification.schema == "fail":
            continue
        data = _mapping_value(specification.value)
        if data is None:
            findings.append(
                ValidationFinding("schema", relative_path, "INVALID_AGENT_SPEC", agent_id)
            )
            continue
        _validate_agent_specification(relative_path, agent_id, data, findings)
        if data.get("agent_id") == agent_id:
            specification_ids.add(agent_id)
    return specification_ids


def _governance_record_path(kind: GovernanceRecordKind, identifier: str) -> str:
    """Return the canonical repository-relative path for one governance record."""
    root = {
        "source_record": SPECIALS_SOURCE_RECORD_ROOT,
        "risk_assessment": SPECIALS_RISK_ASSESSMENT_ROOT,
        "approval": SPECIALS_APPROVAL_ROOT,
    }[kind]
    return f"{root}/{identifier}.json"


def _is_offset_timestamp(value: object) -> bool:
    """Return whether *value* is an ISO-8601 timestamp carrying an offset."""
    if not isinstance(value, str) or _TIMESTAMP_RE.fullmatch(value) is None:
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None and parsed.utcoffset() is not None


def _non_empty_text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _normalise_string_list(value: object, *, none_value: str = "none") -> tuple[str, ...] | None:
    """Normalize an explicit list or a ``none`` sentinel without coercion."""
    if value == none_value:
        return ()
    if not isinstance(value, list) or not all(_non_empty_text(item) for item in value):
        return None
    strings = tuple(cast(str, item) for item in value)
    return strings if len(strings) == len(set(strings)) else None


def _normalise_external_effects(value: object) -> tuple[str, ...] | None:
    """Normalize the external-effect enumeration used by governance records."""
    if value == "none" or value == [] or value == ["none"]:
        return ()
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        return None
    effects = tuple(cast(str, item) for item in value)
    if len(effects) != len(set(effects)) or any(
        effect not in _EXTERNAL_EFFECTS for effect in effects
    ):
        return None
    return effects


def _validate_source_record(
    record_path: str,
    record: Mapping[str, object],
    expected_agent_id: str,
    specification_digest: str,
    loaded_by_path: Mapping[str, _LoadedFile],
    allowlisted_paths: frozenset[str],
    manual_revalidation: bool,
    findings: list[ValidationFinding],
) -> tuple[str, str, str, bool] | None:
    """Validate one Source_Record and return its source/configuration/approval values."""
    if set(record) != _SOURCE_RECORD_FIELDS:
        missing = sorted(_SOURCE_RECORD_FIELDS - set(record))
        extra = sorted(set(record) - _SOURCE_RECORD_FIELDS)
        if missing:
            findings.append(
                ValidationFinding("provenance", record_path, f"MISSING_{missing[0].upper()}")
            )
        elif extra:
            findings.append(
                ValidationFinding("provenance", f"{record_path}.{extra[0]}", "UNSUPPORTED_FIELD")
            )
        return None
    if record.get("schema_version") != SPECIALS_SCHEMA_VERSION:
        findings.append(ValidationFinding("provenance", record_path, "INVALID_SCHEMA_VERSION"))
        return None

    source_path = record.get("source_path")
    source_entry = source_for_path(source_path) if isinstance(source_path, str) else None
    if source_entry is None or source_entry.agent_id != expected_agent_id:
        findings.append(ValidationFinding("provenance", record_path, "INVALID_SOURCE_PATH"))
        return None
    source_sha256 = record.get("source_sha256")
    if not is_sha256_digest(source_sha256):
        findings.append(ValidationFinding("provenance", record_path, "INVALID_SOURCE_DIGEST"))
        return None
    configuration_sha256 = record.get("configuration_sha256")
    if not is_sha256_digest(configuration_sha256):
        findings.append(
            ValidationFinding("provenance", record_path, "INVALID_CONFIGURATION_DIGEST")
        )
        return None
    if configuration_sha256 != specification_digest:
        findings.append(
            ValidationFinding("provenance", record_path, "CONFIGURATION_DIGEST_MISMATCH")
        )
        return None
    if record.get("agent_id") != expected_agent_id:
        findings.append(ValidationFinding("provenance", record_path, "AGENT_ID_MISMATCH"))
        return None
    if not _is_offset_timestamp(record.get("reviewed_at")):
        findings.append(ValidationFinding("provenance", record_path, "INVALID_REVIEW_TIMESTAMP"))
        return None
    approval_id = record.get("approval_id")
    if not _non_empty_text(approval_id) or any(
        separator in cast(str, approval_id) for separator in ("/", "\\")
    ):
        findings.append(ValidationFinding("provenance", record_path, "INVALID_APPROVAL_REFERENCE"))
        return None

    normalized_source_path = cast(str, source_path)
    current_source = loaded_by_path.get(normalized_source_path)
    if normalized_source_path in allowlisted_paths and current_source is None:
        findings.append(ValidationFinding("provenance", record_path, "SOURCE_NOT_READABLE"))
        return None
    if current_source is not None:
        current_digest = sha256_bytes(current_source.raw_bytes)
        if current_digest != source_sha256:
            if manual_revalidation:
                findings.append(
                    ValidationFinding(
                        "provenance", record_path, "STALE_SOURCE_REQUIRES_REVALIDATION"
                    )
                )
                return None
            # A changed source is deliberately tolerated until explicit manual
            # re-validation; the prior approved draft remains the accepted state.
            return (
                cast(str, source_sha256),
                cast(str, configuration_sha256),
                cast(str, approval_id),
                True,
            )

    return cast(str, source_sha256), cast(str, configuration_sha256), cast(str, approval_id), False


def _validate_risk_assessment(
    risk_path: str,
    risk: Mapping[str, object],
    findings: list[ValidationFinding],
) -> dict[str, object] | None:
    """Validate and normalize every Risk_Assessment field."""
    _check_closed_object(risk, _RISK_ASSESSMENT_FIELDS, risk_path, findings)
    valid = set(risk) == _RISK_ASSESSMENT_FIELDS
    if risk.get("schema_version") != SPECIALS_SCHEMA_VERSION:
        findings.append(ValidationFinding("risk_gate", risk_path, "INVALID_SCHEMA_VERSION"))
        valid = False
    for field in ("configuration_sha256", "source_record_sha256"):
        if not is_sha256_digest(risk.get(field)):
            findings.append(ValidationFinding("risk_gate", risk_path, f"INVALID_{field.upper()}"))
            valid = False

    potential_risks = _mapping_value(risk.get("potential_risks"))
    if potential_risks is None:
        findings.append(ValidationFinding("risk_gate", risk_path, "INVALID_POTENTIAL_RISKS"))
        valid = False
        normalized_risks: dict[str, bool] = {}
    else:
        _check_closed_object(potential_risks, _RISK_FIELDS, risk_path, findings)
        normalized_risks = {}
        if set(potential_risks) != _RISK_FIELDS:
            valid = False
        for field in sorted(_RISK_FIELDS):
            value = potential_risks.get(field)
            if not isinstance(value, bool):
                findings.append(
                    ValidationFinding("risk_gate", risk_path, f"INVALID_RISK_{field.upper()}")
                )
                valid = False
            else:
                normalized_risks[field] = value

    effects = _normalise_external_effects(risk.get("external_effect_potential"))
    if effects is None:
        findings.append(ValidationFinding("risk_gate", risk_path, "INVALID_EXTERNAL_EFFECTS"))
        valid = False
        effects = ()
    tools = _normalise_string_list(risk.get("requested_tool_authority"))
    if tools is None:
        findings.append(ValidationFinding("risk_gate", risk_path, "INVALID_REQUESTED_TOOLS"))
        valid = False
        tools = ()
    network_access = risk.get("requested_network_access")
    if not isinstance(network_access, bool):
        findings.append(ValidationFinding("risk_gate", risk_path, "INVALID_REQUESTED_NETWORK"))
        valid = False
        network_access = False
    provider = risk.get("requested_provider")
    if not _non_empty_text(provider):
        findings.append(ValidationFinding("risk_gate", risk_path, "INVALID_REQUESTED_PROVIDER"))
        valid = False
        provider = "none"
    production = risk.get("requested_production_activation")
    if not isinstance(production, bool):
        findings.append(ValidationFinding("risk_gate", risk_path, "INVALID_REQUESTED_PRODUCTION"))
        valid = False
        production = False
    lifecycle = risk.get("requested_lifecycle_state")
    if not _non_empty_text(lifecycle):
        findings.append(ValidationFinding("risk_gate", risk_path, "INVALID_REQUESTED_LIFECYCLE"))
        valid = False
        lifecycle = ""

    if not valid:
        return None
    return {
        "configuration_sha256": cast(str, risk["configuration_sha256"]),
        "source_record_sha256": cast(str, risk["source_record_sha256"]),
        "potential_risks": normalized_risks,
        "external_effect_potential": effects,
        "requested_tool_authority": tools,
        "requested_network_access": network_access,
        "requested_provider": cast(str, provider),
        "requested_production_activation": production,
        "requested_lifecycle_state": cast(str, lifecycle),
    }


def _validate_approval_scope(
    approval_path: str,
    scope: Mapping[str, object],
    risk_values: Mapping[str, object],
    findings: list[ValidationFinding],
) -> bool:
    """Require an approval scope to cover every risk and requested value."""
    _check_closed_object(scope, _APPROVED_SCOPE_FIELDS, approval_path, findings)
    valid = set(scope) == _APPROVED_SCOPE_FIELDS
    approved_risks = _mapping_value(scope.get("potential_risks"))
    expected_risks = _mapping_value(risk_values.get("potential_risks"))
    if approved_risks is None or expected_risks is None:
        findings.append(ValidationFinding("risk_gate", approval_path, "INVALID_APPROVED_RISKS"))
        valid = False
    else:
        _check_closed_object(approved_risks, _RISK_FIELDS, approval_path, findings)
        if set(approved_risks) != _RISK_FIELDS:
            valid = False
        for field, present in expected_risks.items():
            if present and approved_risks.get(field) is not True:
                findings.append(
                    ValidationFinding(
                        "risk_gate", approval_path, f"UNAPPROVED_RISK_{field.upper()}"
                    )
                )
                valid = False
            elif not isinstance(approved_risks.get(field), bool):
                findings.append(
                    ValidationFinding(
                        "risk_gate", approval_path, f"INVALID_APPROVED_RISK_{field.upper()}"
                    )
                )
                valid = False

    approved_effects = _normalise_external_effects(scope.get("external_effect_potential"))
    expected_effects = cast(tuple[str, ...], risk_values.get("external_effect_potential", ()))
    if approved_effects is None or not set(expected_effects).issubset(set(approved_effects or ())):
        findings.append(ValidationFinding("risk_gate", approval_path, "UNAPPROVED_EXTERNAL_EFFECT"))
        valid = False
    approved_tools = _normalise_string_list(scope.get("requested_tool_authority"))
    expected_tools = cast(tuple[str, ...], risk_values.get("requested_tool_authority", ()))
    if approved_tools is None or not set(expected_tools).issubset(set(approved_tools or ())):
        findings.append(ValidationFinding("risk_gate", approval_path, "UNAPPROVED_TOOL_AUTHORITY"))
        valid = False
    for field, code in (
        ("requested_network_access", "UNAPPROVED_NETWORK_ACCESS"),
        ("requested_production_activation", "UNAPPROVED_PRODUCTION_ACTIVATION"),
    ):
        approved_value = scope.get(field)
        expected_value = risk_values.get(field)
        if not isinstance(approved_value, bool) or approved_value != expected_value:
            findings.append(ValidationFinding("risk_gate", approval_path, code))
            valid = False
    for field, code in (
        ("requested_provider", "UNAPPROVED_PROVIDER"),
        ("requested_lifecycle_state", "UNAPPROVED_LIFECYCLE"),
    ):
        if scope.get(field) != risk_values.get(field):
            findings.append(ValidationFinding("risk_gate", approval_path, code))
            valid = False
    return valid


def _validate_approval_record(
    approval_path: str,
    approval: Mapping[str, object],
    expected_agent_id: str,
    source_path: str,
    source_sha256: str,
    configuration_sha256: str,
    source_record_sha256: str,
    risk_values: Mapping[str, object],
    findings: list[ValidationFinding],
) -> bool:
    """Validate human approval identity, bindings, reason, and complete scope."""
    _check_closed_object(approval, _APPROVAL_FIELDS, approval_path, findings)
    valid = set(approval) == _APPROVAL_FIELDS
    if not _non_empty_text(approval.get("approval_id")):
        findings.append(ValidationFinding("risk_gate", approval_path, "INVALID_APPROVAL_ID"))
        valid = False
    if not _non_empty_text(approval.get("reviewer_identity")):
        findings.append(ValidationFinding("risk_gate", approval_path, "INVALID_REVIEWER_IDENTITY"))
        valid = False
    if approval.get("decision") != "approved":
        findings.append(ValidationFinding("risk_gate", approval_path, "APPROVAL_NOT_GRANTED"))
        valid = False
    if not _is_offset_timestamp(approval.get("decision_timestamp")):
        findings.append(ValidationFinding("risk_gate", approval_path, "INVALID_DECISION_TIMESTAMP"))
        valid = False
    for field, expected, code in (
        ("source_path", source_path, "APPROVAL_SOURCE_PATH_MISMATCH"),
        ("source_sha256", source_sha256, "APPROVAL_SOURCE_DIGEST_MISMATCH"),
        ("agent_id", expected_agent_id, "APPROVAL_AGENT_ID_MISMATCH"),
        ("configuration_sha256", configuration_sha256, "APPROVAL_CONFIGURATION_DIGEST_MISMATCH"),
        ("source_record_sha256", source_record_sha256, "APPROVAL_SOURCE_RECORD_DIGEST_MISMATCH"),
    ):
        if approval.get(field) != expected:
            findings.append(ValidationFinding("risk_gate", approval_path, code))
            valid = False
    reason = approval.get("reason")
    if not isinstance(reason, str) or not 1 <= len(reason) <= 1024:
        findings.append(ValidationFinding("risk_gate", approval_path, "INVALID_APPROVAL_REASON"))
        valid = False
    scope = _mapping_value(approval.get("approved_risk_scope"))
    if scope is None or not _validate_approval_scope(approval_path, scope, risk_values, findings):
        if scope is None:
            findings.append(ValidationFinding("risk_gate", approval_path, "INVALID_APPROVED_SCOPE"))
        valid = False
    return valid


def _provenance_and_risk_checks(
    loaded_by_path: Mapping[str, _LoadedFile],
    allowlisted_paths: frozenset[str],
    specification_ids: set[str],
    findings: list[ValidationFinding],
    *,
    manual_revalidation: bool,
) -> tuple[SectionValidationResult, SectionValidationResult, bool]:
    """Validate explicit provenance/governance records without deriving authority."""
    governance_paths = tuple(
        path
        for path in loaded_by_path
        if path.startswith(f"{SPECIALS_SOURCE_RECORD_ROOT}/")
        or path.startswith(f"{SPECIALS_RISK_ASSESSMENT_ROOT}/")
        or path.startswith(f"{SPECIALS_APPROVAL_ROOT}/")
    )
    if not governance_paths:
        return SectionValidationResult("pass"), SectionValidationResult("pass"), False

    pending_revalidation = False
    provenance_start = len(findings)
    risk_start = len(findings)
    for agent_id in SPECIAL_AGENT_IDS:
        specification_path = f"{SPECIALS_PACK_ROOT}/{canonical_agent_spec_path(agent_id)}"
        specification_file = loaded_by_path.get(specification_path)
        specification = _mapping_value(specification_file.value) if specification_file else None
        if agent_id not in specification_ids or specification is None:
            findings.append(
                ValidationFinding(
                    "provenance", specification_path, "MISSING_SPECIFICATION", agent_id
                )
            )
            continue
        specification_digest = sha256_json(specification)
        source_record_path = _governance_record_path("source_record", agent_id)
        source_record_file = loaded_by_path.get(source_record_path)
        if source_record_file is None:
            findings.append(
                ValidationFinding(
                    "provenance", source_record_path, "MISSING_SOURCE_RECORD", agent_id
                )
            )
            continue
        if source_record_file.schema == "fail":
            findings.append(
                ValidationFinding(
                    "provenance", source_record_path, "INVALID_SOURCE_RECORD", agent_id
                )
            )
            continue
        source_record = _mapping_value(source_record_file.value)
        if source_record is None:
            findings.append(
                ValidationFinding(
                    "provenance", source_record_path, "INVALID_SOURCE_RECORD", agent_id
                )
            )
            continue
        source_values = _validate_source_record(
            source_record_path,
            source_record,
            agent_id,
            specification_digest,
            loaded_by_path,
            allowlisted_paths,
            manual_revalidation,
            findings,
        )
        if source_values is None:
            continue
        source_sha256, configuration_sha256, approval_id, source_is_stale = source_values
        pending_revalidation = pending_revalidation or source_is_stale
        source_record_sha256 = sha256_json(source_record)

        risk_path = _governance_record_path("risk_assessment", configuration_sha256)
        risk_file = loaded_by_path.get(risk_path)
        if risk_file is None:
            findings.append(
                ValidationFinding("risk_gate", risk_path, "MISSING_RISK_ASSESSMENT", agent_id)
            )
            continue
        if risk_file.schema == "fail":
            findings.append(
                ValidationFinding("risk_gate", risk_path, "INVALID_RISK_ASSESSMENT", agent_id)
            )
            continue
        risk = _mapping_value(risk_file.value)
        if risk is None:
            findings.append(
                ValidationFinding("risk_gate", risk_path, "INVALID_RISK_ASSESSMENT", agent_id)
            )
            continue
        risk_values = _validate_risk_assessment(risk_path, risk, findings)
        if risk_values is None:
            continue
        if (
            risk_values["configuration_sha256"] != configuration_sha256
            or risk_values["source_record_sha256"] != source_record_sha256
        ):
            findings.append(
                ValidationFinding("risk_gate", risk_path, "RISK_DIGEST_BINDING_MISMATCH", agent_id)
            )
            continue

        approval_path = _governance_record_path("approval", approval_id)
        approval_file = loaded_by_path.get(approval_path)
        if approval_file is None:
            findings.append(
                ValidationFinding("risk_gate", approval_path, "MISSING_APPROVAL_RECORD", agent_id)
            )
            continue
        if approval_file.schema == "fail":
            findings.append(
                ValidationFinding("risk_gate", approval_path, "INVALID_APPROVAL_RECORD", agent_id)
            )
            continue
        approval = _mapping_value(approval_file.value)
        if approval is None:
            findings.append(
                ValidationFinding("risk_gate", approval_path, "INVALID_APPROVAL_RECORD", agent_id)
            )
            continue
        _validate_approval_record(
            approval_path,
            approval,
            agent_id,
            cast(str, source_record["source_path"]),
            source_sha256,
            configuration_sha256,
            source_record_sha256,
            risk_values,
            findings,
        )

    provenance_findings = findings[provenance_start:]
    risk_findings = findings[risk_start:]
    provenance_result: Literal["pass", "fail"] = (
        "fail"
        if any(finding.category == "provenance" for finding in provenance_findings)
        else "pass"
    )
    risk_result: Literal["pass", "fail"] = (
        "fail" if any(finding.category == "risk_gate" for finding in risk_findings) else "pass"
    )
    governance_file_results = [
        FileValidationResult(file.path, sha256_bytes(file.raw_bytes), file.schema)
        for file in loaded_by_path.values()
        if file.path in governance_paths
    ]
    governance_digest = _configuration_set_digest(governance_file_results)
    return (
        SectionValidationResult(provenance_result, governance_digest),
        SectionValidationResult(risk_result, governance_digest),
        pending_revalidation,
    )


def _configuration_set_digest(files: Iterable[FileValidationResult]) -> str:
    ordered_files = sorted(files, key=lambda file_result: file_result.path)
    values = [file_result.as_dict() for file_result in ordered_files]
    return sha256_json({"files": values})


def _validation_report_path(repository_root: Path, configuration_set_digest: str) -> Path:
    """Return the digest-derived local evidence path for one report."""
    return repository_root / SPECIALS_VALIDATION_REPORT_ROOT / f"{configuration_set_digest}.json"


def _retain_validation_report(repository_root: Path, report: ValidationReport) -> bool:
    """Retain one completed report without exposing filesystem details."""
    target = _validation_report_path(repository_root, report.configuration_set_digest)
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(report.canonical_bytes())
    except (OSError, RuntimeError, ValueError):
        return False
    return True


def _state_for_report(report: ValidationReport) -> AcceptedSpecialsState:
    if report.validation_outcome != "pass":
        return report.accepted_state
    agents = tuple(AcceptedSpecialAgent(agent_id) for agent_id in report.accepted_agent_ids)
    return AcceptedSpecialsState(agents, sha256_bytes(report.canonical_bytes()))


def validate_specials_pack(
    repository_root: Path | str,
    allowlisted_paths: Iterable[Path | str],
    previous_state: AcceptedSpecialsState | None = None,
    *,
    manual_revalidation: bool = False,
) -> ValidationReport:
    """Validate and retain an explicitly allowlisted local data set.

    The function performs no discovery: only paths supplied by the caller are
    considered. A rejected proposal returns the supplied ``previous_state``
    unchanged in ``report.accepted_state``; no registration or activation is
    performed. A successful validation becomes eligible for draft
    representation only after its completed report is retained locally.
    """
    root = Path(repository_root)
    allowlisted_input = tuple(allowlisted_paths)
    loaded_files, findings = _load_allowlisted_files(root, allowlisted_input)
    normalized_allowlist: set[str] = set()
    for raw_path in allowlisted_input:
        try:
            normalized_allowlist.add(normalize_repository_relative_path(raw_path))
        except (InvalidRepositoryPathError, TypeError):
            continue
    loaded_by_path = {loaded.path: loaded for loaded in loaded_files}
    _schema_profile_checks(loaded_by_path.get(SPECIALS_SCHEMA_PATH), findings)
    manifest_file = loaded_by_path.get(SPECIALS_MANIFEST_PATH)
    manifest, inventory, manifest_ids = _manifest_checks(manifest_file, loaded_by_path, findings)
    specification_ids = _specification_checks(loaded_by_path, findings)
    provenance, risk_gate, pending_revalidation = _provenance_and_risk_checks(
        loaded_by_path,
        frozenset(normalized_allowlist),
        specification_ids,
        findings,
        manual_revalidation=manual_revalidation,
    )

    ordered_findings = _sort_findings(findings)
    if (
        not ordered_findings
        and manifest_ids == set(SPECIAL_AGENT_IDS)
        and specification_ids == set(SPECIAL_AGENT_IDS)
    ):
        outcome: ValidationOutcome = "pass"
        accepted_ids = tuple(sorted(SPECIAL_AGENT_IDS))
        rejected_ids: tuple[str, ...] = ()
    else:
        outcome = "fail"
        accepted_ids = ()
        rejected_ids = tuple(sorted(SPECIAL_AGENT_IDS))

    file_results = tuple(
        FileValidationResult(file.path, sha256_bytes(file.raw_bytes), file.schema)
        for file in loaded_files
    )
    configuration_digest = _configuration_set_digest(file_results)
    prior_state = previous_state or AcceptedSpecialsState()
    report = ValidationReport(
        format_version=SPECIALS_SCHEMA_VERSION,
        validation_outcome=outcome,
        accepted_agent_ids=accepted_ids,
        rejected_agent_ids=rejected_ids,
        files=file_results,
        manifest=manifest,
        inventory=inventory,
        provenance=provenance,
        risk_gate=risk_gate,
        report_retention="not_attempted",
        registration_effect="none",
        findings=ordered_findings,
        configuration_set_digest=configuration_digest,
        accepted_state=prior_state,
    )

    if outcome == "pass":
        completed_report = replace(
            report,
            report_retention="retained",
            registration_effect="eligible_draft_representation",
        )
        accepted_state = (
            previous_state
            if pending_revalidation and previous_state is not None
            else _state_for_report(completed_report)
        )
        completed_report = replace(completed_report, accepted_state=accepted_state)
    else:
        completed_report = replace(report, report_retention="retained")

    if _retain_validation_report(root, completed_report):
        return completed_report

    retention_failure = ValidationFinding(
        "io",
        f"{SPECIALS_VALIDATION_REPORT_ROOT}/{configuration_digest}.json",
        "REPORT_RETENTION_FAILED",
    )
    return replace(
        completed_report,
        report_retention="failed",
        registration_effect="none",
        findings=_sort_findings((*completed_report.findings, retention_failure)),
        accepted_state=prior_state,
    )


__all__ = [
    "CANONICAL_SPECIAL_AGENT_IDS",
    "SOURCE_INVENTORY",
    "SPECIALS_ALLOWLIST_PATHS",
    "SPECIALS_APPROVAL_ROOT",
    "SPECIALS_INVENTORY_PATH",
    "SPECIALS_MANIFEST_PATH",
    "SPECIALS_PACK_ID",
    "SPECIALS_PACK_ROOT",
    "SPECIALS_RISK_ASSESSMENT_ROOT",
    "SPECIALS_SCHEMA_PATH",
    "SPECIALS_SCHEMA_VERSION",
    "SPECIALS_SOURCE_CATALOG",
    "SPECIALS_SOURCE_PATHS",
    "SPECIALS_SOURCE_RECORD_ROOT",
    "SPECIALS_VALIDATION_REPORT_ROOT",
    "SPECIAL_AGENT_IDS",
    "SPECIAL_AGENT_SPEC_PATHS",
    "SPECIAL_SOURCE_BY_AGENT_ID",
    "SPECIAL_SOURCE_BY_PATH",
    "AcceptedSpecialAgent",
    "AcceptedSpecialsState",
    "DuplicateJsonKeyError",
    "FileValidationResult",
    "Finding",
    "InvalidRepositoryPathError",
    "SpecialSourceEntry",
    "SpecialsState",
    "ValidationFinding",
    "ValidationReport",
    "ValidatorState",
    "canonical_agent_spec_path",
    "canonical_json_bytes",
    "canonical_json_text",
    "canonical_spec_path",
    "decode_json_no_duplicates",
    "is_canonical_agent_id",
    "is_normalized_repository_relative_path",
    "is_sha256_digest",
    "is_special_agent_asset_id",
    "is_valid_canonical_agent_id",
    "is_valid_special_agent_asset_id",
    "loads_rejecting_duplicate_keys",
    "normalize_repository_relative_path",
    "serialize_canonical_json",
    "sha256_bytes",
    "sha256_file",
    "sha256_json",
    "sha256_text",
    "source_for_agent_id",
    "source_for_path",
    "validate_specials_pack",
]
