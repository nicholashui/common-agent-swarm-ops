"""Fail-closed validation and local projections for the reviewed Agent Source Map.

The common inventory is the only authority for video-agent identity.  Source IDs
are relationship/provenance data and never become roster identities.  This module
has no network or runtime capabilities; its write helpers only publish the two
local projections derived from an already-valid map.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Final

from app.video.inventory import EXPECTED_VIDEO_AGENT_COUNT
from app.video.migration.canonical import canonicalize_json, digest_json, redact_diagnostic
from app.video.migration.contracts import AgentSourceMapEntry, MappingStatus
from app.video.migration.paths import (
    UnsafeLocalPathError,
    normalize_relative_path,
    resolve_under_root,
)

MAP_FILENAME: Final[str] = "AGENT_SOURCE_MAP.json"
ROSTER_FILENAME: Final[str] = "ROSTER.json"
MAP_DOCUMENT_FILENAME: Final[str] = "MAP.md"
MAP_SCHEMA_VERSION: Final[str] = "1.0"
_MAPPING_STATUSES: Final[frozenset[str]] = frozenset(status.value for status in MappingStatus)
_REVIEW_PLACEHOLDERS: Final[frozenset[str]] = frozenset(
    {"", "none", "unknown", "unreviewed", "pending", "todo", "tbd", "automation", "system", "bot"}
)
_SOURCE_REPOSITORY_PREFIXES: Final[tuple[str, ...]] = (
    "generic-swarm-ops/",
    "va-agent-swarm/",
)


@dataclass(frozen=True, slots=True)
class AgentMappingIssue:
    """A deterministic, redaction-safe mapping validation diagnostic."""

    code: str
    field: str = ""
    message: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "code", str(self.code).strip().casefold())
        object.__setattr__(self, "field", redact_diagnostic(self.field))
        object.__setattr__(self, "message", redact_diagnostic(self.message))


@dataclass(frozen=True, slots=True)
class AgentMappingProjections:
    """Canonical local projections derived only from a valid reviewed map."""

    roster: dict[str, object]
    map_markdown: str

    @property
    def roster_json(self) -> str:
        """Return canonical JSON text for ``ROSTER.json``."""
        return canonicalize_json(self.roster)


class MappingWriteBlockedError(ValueError):
    """Raised when a write-mode specification/projection operation lacks a valid map."""

    def __init__(self, issues: Sequence[AgentMappingIssue]) -> None:
        self.issues = tuple(issues)
        codes = ", ".join(issue.code for issue in self.issues[:3]) or "invalid_agent_source_map"
        super().__init__(f"Mapping prerequisites block write mode: {codes}.")


@dataclass(frozen=True, slots=True)
class AgentMappingReport:
    """Complete result of validating one local Agent Source Map."""

    is_valid: bool
    inventory_agent_ids: tuple[str, ...]
    map_agent_ids: tuple[str, ...]
    entries: tuple[AgentSourceMapEntry, ...]
    issues: tuple[AgentMappingIssue, ...] = ()
    inventory_digest: str = ""

    @property
    def can_write_specifications(self) -> bool:
        """Return whether write-mode specification generation is permitted."""
        return self.is_valid

    @property
    def reviewed_entries(self) -> tuple[AgentSourceMapEntry, ...]:
        """Return entries in authoritative inventory order."""
        return self.entries

    def require_write_mode(self, write_mode: bool = True) -> None:
        """Fail closed for every write-mode consumer when mapping validation fails."""
        if write_mode and not self.is_valid:
            raise MappingWriteBlockedError(self.issues)

    def projections(self) -> AgentMappingProjections:
        """Build deterministic local projections, refusing invalid reviewed maps."""
        self.require_write_mode(True)
        return build_projections(self)


@dataclass(frozen=True, slots=True)
class ProjectionValidationReport:
    """Result of comparing checked-in projections with a reviewed map."""

    is_valid: bool
    issues: tuple[AgentMappingIssue, ...] = ()


class AgentSourceMapValidator:
    """Validate the exact reviewed mapping against a local authoritative inventory."""

    def validate(
        self,
        inventory: object,
        source_map: object,
        *,
        video_root: Path | str | None = None,
        repository_root: Path | str | None = None,
    ) -> AgentMappingReport:
        """Validate inventory identity, reviewed mapping fields, and source locality.

        ``video_root`` is optional for in-memory validation.  When supplied,
        source documents must resolve to existing readable files beneath that
        root (or beneath the same root when a repository-relative
        ``business/video/...`` path is supplied).  No source document contents
        are read.
        """
        issues: list[AgentMappingIssue] = []
        inventory_ids = _inventory_ids(inventory, issues)
        expected_digest = inventory_digest(inventory_ids)
        raw_entries = _map_entries(source_map, issues)
        declared_digest = _declared_inventory_digest(source_map, issues)
        if declared_digest is not None and declared_digest != expected_digest:
            issues.append(
                AgentMappingIssue(
                    "inventory_digest_mismatch",
                    "inventory_digest",
                    "Agent Source Map inventory digest must match the authoritative inventory.",
                )
            )

        parsed_entries: list[AgentSourceMapEntry] = []
        map_ids: list[str] = []
        source_rationales: defaultdict[str, list[tuple[str, str]]] = defaultdict(list)
        for index, raw_entry in enumerate(raw_entries):
            field = f"entries[{index}]"
            parsed = self._parse_entry(
                raw_entry,
                field,
                video_root=video_root,
                repository_root=repository_root,
                issues=issues,
            )
            if parsed is None:
                continue
            parsed_entries.append(parsed)
            map_ids.append(parsed.common_agent_id)
            for source_id in parsed.source_agent_ids:
                source_rationales[source_id].append((parsed.common_agent_id, parsed.rationale))

        self._validate_inventory_cardinality(inventory_ids, issues)
        self._validate_map_identity(inventory_ids, map_ids, issues)
        self._validate_reused_source_rationales(source_rationales, issues)
        ordered_entries = _order_entries(parsed_entries, inventory_ids)
        return AgentMappingReport(
            is_valid=not issues,
            inventory_agent_ids=tuple(inventory_ids),
            map_agent_ids=tuple(map_ids),
            entries=ordered_entries,
            issues=_sort_issues(issues),
            inventory_digest=expected_digest,
        )

    def validate_directory(
        self,
        video_root: Path | str,
        *,
        source_map_path: Path | str | None = None,
        repository_root: Path | str | None = None,
    ) -> AgentMappingReport:
        """Validate the checked-in inventory and map without mutating the pack."""
        root = Path(video_root).resolve()
        inventory_path = root / "inventory.json"
        issues: list[AgentMappingIssue] = []
        map_path = _resolve_map_input(root, source_map_path, issues)
        inventory = _read_json(inventory_path, "inventory", issues)
        source_map = _read_json(map_path, "source_map", issues) if map_path is not None else {}
        report = self.validate(
            inventory,
            source_map,
            video_root=root,
            repository_root=repository_root,
        )
        return _with_issues(report, (*issues, *report.issues))

    def validate_for_specification_write(
        self,
        inventory: object,
        source_map: object,
        *,
        write_mode: bool,
        video_root: Path | str | None = None,
        repository_root: Path | str | None = None,
    ) -> AgentMappingReport:
        """Validate a map and enforce the specification write boundary."""
        report = self.validate(
            inventory,
            source_map,
            video_root=video_root,
            repository_root=repository_root,
        )
        report.require_write_mode(write_mode)
        return report

    @staticmethod
    def _parse_entry(
        raw_entry: object,
        field: str,
        *,
        video_root: Path | str | None,
        repository_root: Path | str | None,
        issues: list[AgentMappingIssue],
    ) -> AgentSourceMapEntry | None:
        if not isinstance(raw_entry, Mapping):
            issues.append(
                AgentMappingIssue(
                    "invalid_mapping_entry", field, "Each mapping entry must be an object."
                )
            )
            return None

        common_agent_id = _required_text(
            raw_entry.get("common_agent_id"), f"{field}.common_agent_id", issues
        )
        if common_agent_id is not None and (
            common_agent_id != common_agent_id.strip() or not _looks_like_common_id(common_agent_id)
        ):
            issues.append(
                AgentMappingIssue(
                    "invalid_common_agent_id",
                    f"{field}.common_agent_id",
                    "Common Agent IDs must be exact nonblank video identifiers.",
                )
            )
        mapping_status = _mapping_status(
            raw_entry.get("mapping_status"), f"{field}.mapping_status", issues
        )
        source_agent_ids = _text_sequence(
            raw_entry.get("source_agent_ids"), f"{field}.source_agent_ids", issues, allow_empty=True
        )
        source_documents = _path_sequence(
            raw_entry.get("source_documents"), f"{field}.source_documents", issues
        )
        rationale = _required_review_text(raw_entry.get("rationale"), f"{field}.rationale", issues)
        reviewed_by = _required_review_text(
            raw_entry.get("reviewed_by"), f"{field}.reviewed_by", issues
        )
        reviewed_at = _timestamp(raw_entry.get("reviewed_at"), f"{field}.reviewed_at", issues)
        _validate_ambiguity(raw_entry, field, issues)

        if mapping_status == MappingStatus.COMMON_ONLY:
            if source_agent_ids:
                issues.append(
                    AgentMappingIssue(
                        "common_only_has_source_agents",
                        f"{field}.source_agent_ids",
                        "common_only mappings must have an empty source-agent-ID list.",
                    )
                )
        elif mapping_status is not None and not source_agent_ids:
            issues.append(
                AgentMappingIssue(
                    "missing_source_agent",
                    f"{field}.source_agent_ids",
                    "Non-common_only mappings require at least one source-agent ID.",
                )
            )

        if source_documents is not None:
            _validate_source_document_locality(
                source_documents,
                field,
                video_root=video_root,
                repository_root=repository_root,
                issues=issues,
            )

        if (
            common_agent_id is None
            or mapping_status is None
            or source_agent_ids is None
            or source_documents is None
            or rationale is None
            or reviewed_by is None
            or reviewed_at is None
        ):
            return None
        try:
            return AgentSourceMapEntry(
                common_agent_id=common_agent_id,
                mapping_status=mapping_status,
                source_agent_ids=tuple(source_agent_ids),
                source_documents=tuple(source_documents),
                rationale=rationale,
                reviewed_by=reviewed_by,
                reviewed_at=reviewed_at,
            )
        except (TypeError, ValueError) as error:
            issues.append(
                AgentMappingIssue(
                    "invalid_mapping_record",
                    field,
                    f"Mapping record does not satisfy the local contract: {error}",
                )
            )
            return None

    @staticmethod
    def _validate_inventory_cardinality(
        inventory_ids: Sequence[str], issues: list[AgentMappingIssue]
    ) -> None:
        if len(inventory_ids) != EXPECTED_VIDEO_AGENT_COUNT:
            issues.append(
                AgentMappingIssue(
                    "invalid_inventory_count",
                    "inventory.entries",
                    (
                        "The authoritative inventory must contain exactly "
                        f"{EXPECTED_VIDEO_AGENT_COUNT} Common Agent IDs."
                    ),
                )
            )
        if len(set(inventory_ids)) != len(inventory_ids):
            issues.append(
                AgentMappingIssue(
                    "duplicate_inventory_agent_id",
                    "inventory.entries",
                    "The authoritative inventory must contain unique Common Agent IDs.",
                )
            )

    @staticmethod
    def _validate_map_identity(
        inventory_ids: Sequence[str], map_ids: Sequence[str], issues: list[AgentMappingIssue]
    ) -> None:
        if len(map_ids) != len(set(map_ids)):
            issues.append(
                AgentMappingIssue(
                    "duplicate_common_agent_id",
                    "entries",
                    "Agent Source Map Common Agent IDs must be unique.",
                )
            )
        inventory_set = set(inventory_ids)
        map_set = set(map_ids)
        for agent_id in sorted(inventory_set - map_set):
            issues.append(
                AgentMappingIssue(
                    "missing_common_agent_id",
                    agent_id,
                    "Every authoritative Common Agent ID requires one reviewed mapping.",
                )
            )
        for agent_id in sorted(map_set - inventory_set):
            issues.append(
                AgentMappingIssue(
                    "extra_common_agent_id",
                    agent_id,
                    "Agent Source Map entries must use authoritative Common Agent IDs.",
                )
            )

    @staticmethod
    def _validate_reused_source_rationales(
        source_rationales: Mapping[str, Sequence[tuple[str, str]]],
        issues: list[AgentMappingIssue],
    ) -> None:
        for source_id, relationships in sorted(source_rationales.items()):
            if len(relationships) < 2:
                continue
            rationales = [rationale for _, rationale in relationships]
            if len(set(rationales)) == len(rationales):
                continue
            affected_ids = ", ".join(sorted(agent_id for agent_id, _ in relationships))
            issues.append(
                AgentMappingIssue(
                    "reused_source_rationale_not_distinct",
                    source_id,
                    (
                        "Reused source-agent IDs require distinct rationale for each "
                        f"mapping ({affected_ids})."
                    ),
                )
            )


def inventory_digest(inventory_agent_ids: Sequence[str]) -> str:
    """Return the canonical digest declared by ``AGENT_SOURCE_MAP.json``."""
    return digest_json({"agent_ids": list(inventory_agent_ids)})


def build_projections(report: AgentMappingReport) -> AgentMappingProjections:
    """Build ROSTER and MAP projections from a valid report only."""
    report.require_write_mode(True)
    roster: dict[str, object] = {
        "schema_version": MAP_SCHEMA_VERSION,
        "inventory_digest": report.inventory_digest,
        "entries": [{"agent_id": agent_id} for agent_id in report.inventory_agent_ids],
    }
    return AgentMappingProjections(roster=roster, map_markdown=_render_map(report.entries))


def build_roster(report: AgentMappingReport) -> dict[str, object]:
    """Return the Common-ID-only roster projection."""
    return build_projections(report).roster


def render_map_markdown(report: AgentMappingReport) -> str:
    """Return the human-readable mapping projection for a valid reviewed map."""
    return build_projections(report).map_markdown


def write_projections(
    video_root: Path | str, report: AgentMappingReport
) -> AgentMappingProjections:
    """Write only the valid map's local ROSTER.json and MAP.md projections."""
    report.require_write_mode(True)
    root = Path(video_root).resolve()
    roster_path = resolve_under_root(root, ROSTER_FILENAME)
    map_document_path = resolve_under_root(root, MAP_DOCUMENT_FILENAME)
    projections = build_projections(report)
    roster_path.write_text(f"{projections.roster_json}\n", encoding="utf-8")
    map_document_path.write_text(projections.map_markdown, encoding="utf-8")
    return projections


def validate_roster_projection(
    roster: object, inventory_agent_ids: Sequence[str]
) -> ProjectionValidationReport:
    """Validate that a roster contains exactly the ordered Common Agent IDs."""
    issues: list[AgentMappingIssue] = []
    raw_entries: object = roster
    if isinstance(roster, Mapping):
        raw_entries = roster.get("entries", roster.get("agents"))
    if not isinstance(raw_entries, Sequence) or isinstance(raw_entries, (str, bytes, bytearray)):
        return ProjectionValidationReport(
            False,
            (
                AgentMappingIssue(
                    "invalid_roster", "ROSTER.json", "Roster entries must be an array."
                ),
            ),
        )
    roster_ids: list[str] = []
    for index, raw_entry in enumerate(raw_entries):
        field = f"ROSTER.json.entries[{index}]"
        if isinstance(raw_entry, str):
            agent_id = raw_entry
        elif isinstance(raw_entry, Mapping):
            agent_id_value = raw_entry.get("agent_id", raw_entry.get("common_agent_id"))
            agent_id = agent_id_value if isinstance(agent_id_value, str) else ""
            source_fields = {"source_agent_ids", "source_agent_id", "va_source", "source_id"}
            if source_fields.intersection(raw_entry):
                issues.append(
                    AgentMappingIssue(
                        "roster_contains_source_identity",
                        field,
                        "ROSTER.json may contain Common Agent IDs only, not source identities.",
                    )
                )
        else:
            agent_id = ""
        if not agent_id:
            issues.append(
                AgentMappingIssue(
                    "invalid_roster_entry", field, "Roster entries require a Common Agent ID."
                )
            )
            continue
        roster_ids.append(agent_id)
    expected = tuple(inventory_agent_ids)
    if tuple(roster_ids) != expected:
        issues.append(
            AgentMappingIssue(
                "roster_identity_mismatch",
                "ROSTER.json.entries",
                "ROSTER.json must preserve the authoritative inventory order and IDs exactly.",
            )
        )
    return ProjectionValidationReport(not issues, _sort_issues(issues))


def validate_projection_files(
    video_root: Path | str, report: AgentMappingReport
) -> ProjectionValidationReport:
    """Check checked-in projections against the exact reviewed map."""
    issues: list[AgentMappingIssue] = []
    report.require_write_mode(True)
    root = Path(video_root).resolve()
    projections = build_projections(report)
    try:
        roster_path = resolve_under_root(
            root, ROSTER_FILENAME, must_exist=True, require_readable=True
        )
        map_path = resolve_under_root(
            root, MAP_DOCUMENT_FILENAME, must_exist=True, require_readable=True
        )
        roster = json.loads(roster_path.read_text(encoding="utf-8"))
        roster_report = validate_roster_projection(roster, report.inventory_agent_ids)
        issues.extend(roster_report.issues)
        if roster != projections.roster:
            issues.append(
                AgentMappingIssue(
                    "roster_projection_drift",
                    ROSTER_FILENAME,
                    "ROSTER.json is not the canonical projection of the reviewed map.",
                )
            )
        if map_path.read_text(encoding="utf-8") != projections.map_markdown:
            issues.append(
                AgentMappingIssue(
                    "map_projection_drift",
                    MAP_DOCUMENT_FILENAME,
                    "MAP.md is not the canonical projection of the reviewed map.",
                )
            )
    except (OSError, UnicodeError, json.JSONDecodeError, UnsafeLocalPathError) as error:
        issues.append(
            AgentMappingIssue(
                "unreadable_projection",
                "projections",
                f"Local map projections must be readable valid files: {error}",
            )
        )
    return ProjectionValidationReport(not issues, _sort_issues(issues))


def assert_mapping_ready(report: AgentMappingReport, *, write_mode: bool) -> None:
    """Public write-boundary guard for SPEC builders and other write consumers."""
    report.require_write_mode(write_mode)


def _inventory_ids(inventory: object, issues: list[AgentMappingIssue]) -> list[str]:
    if not isinstance(inventory, Mapping):
        issues.append(
            AgentMappingIssue(
                "invalid_inventory", "inventory", "Authoritative inventory must be an object."
            )
        )
        return []
    raw_entries = inventory.get("entries")
    if not isinstance(raw_entries, Sequence) or isinstance(raw_entries, (str, bytes, bytearray)):
        issues.append(
            AgentMappingIssue(
                "invalid_inventory_entries",
                "inventory.entries",
                "Authoritative inventory entries must be an array.",
            )
        )
        return []
    agent_ids: list[str] = []
    for index, raw_entry in enumerate(raw_entries):
        field = f"inventory.entries[{index}].agent_id"
        if not isinstance(raw_entry, Mapping) or not isinstance(raw_entry.get("agent_id"), str):
            issues.append(
                AgentMappingIssue(
                    "invalid_inventory_agent_id",
                    field,
                    "Every inventory entry requires a Common Agent ID.",
                )
            )
            continue
        agent_id = raw_entry["agent_id"]
        if agent_id != agent_id.strip() or not _looks_like_common_id(agent_id):
            issues.append(
                AgentMappingIssue(
                    "invalid_inventory_agent_id",
                    field,
                    "Inventory IDs must be exact video identifiers.",
                )
            )
            continue
        agent_ids.append(agent_id)
    return agent_ids


def _map_entries(source_map: object, issues: list[AgentMappingIssue]) -> Sequence[object]:
    if not isinstance(source_map, Mapping):
        issues.append(
            AgentMappingIssue(
                "invalid_source_map", "source_map", "Agent Source Map must be an object."
            )
        )
        return ()
    raw_entries = source_map.get("entries")
    if not isinstance(raw_entries, Sequence) or isinstance(raw_entries, (str, bytes, bytearray)):
        issues.append(
            AgentMappingIssue(
                "invalid_source_map_entries",
                "source_map.entries",
                "Agent Source Map entries must be an array.",
            )
        )
        return ()
    return raw_entries


def _declared_inventory_digest(source_map: object, issues: list[AgentMappingIssue]) -> str | None:
    if not isinstance(source_map, Mapping):
        return None
    value = source_map.get("inventory_digest")
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
        issues.append(
            AgentMappingIssue(
                "invalid_inventory_digest",
                "inventory_digest",
                "Agent Source Map requires a lowercase SHA-256 inventory digest.",
            )
        )
        return None
    return value


def _required_text(value: object, field: str, issues: list[AgentMappingIssue]) -> str | None:
    if not isinstance(value, str) or not value.strip():
        issues.append(
            AgentMappingIssue(
                "missing_required_field", field, "Required mapping field must be a nonblank string."
            )
        )
        return None
    return value


def _required_review_text(value: object, field: str, issues: list[AgentMappingIssue]) -> str | None:
    text = _required_text(value, field, issues)
    if text is not None and text.strip().casefold() in _REVIEW_PLACEHOLDERS:
        issues.append(
            AgentMappingIssue(
                "missing_human_review",
                field,
                "Mapping review fields cannot use an unreviewed placeholder.",
            )
        )
        return None
    return text


def _looks_like_common_id(value: str) -> bool:
    return value.startswith("video.") and len(value) > len("video.") and " " not in value


def _mapping_status(
    value: object, field: str, issues: list[AgentMappingIssue]
) -> MappingStatus | None:
    if not isinstance(value, str) or value not in _MAPPING_STATUSES:
        issues.append(
            AgentMappingIssue(
                "invalid_mapping_status",
                field,
                "Mapping status must be exact, composite, related, or common_only.",
            )
        )
        return None
    return MappingStatus(value)


def _text_sequence(
    value: object,
    field: str,
    issues: list[AgentMappingIssue],
    *,
    allow_empty: bool,
) -> list[str] | None:
    if not isinstance(value, list):
        issues.append(
            AgentMappingIssue(
                "invalid_string_list", field, "Mapping field must be an array of strings."
            )
        )
        return None
    values: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            issues.append(
                AgentMappingIssue(
                    "invalid_string_list_item",
                    f"{field}[{index}]",
                    "Mapping list items must be nonblank strings.",
                )
            )
            continue
        if item != item.strip():
            issues.append(
                AgentMappingIssue(
                    "invalid_string_list_item",
                    f"{field}[{index}]",
                    "Mapping list items must not contain surrounding whitespace.",
                )
            )
            continue
        values.append(item)
    if len(values) != len(set(values)):
        issues.append(
            AgentMappingIssue(
                "duplicate_mapping_value", field, "Mapping list values must be unique."
            )
        )
    if not allow_empty and not values:
        issues.append(
            AgentMappingIssue(
                "missing_mapping_value", field, "Mapping field must contain at least one value."
            )
        )
    return values


def _path_sequence(value: object, field: str, issues: list[AgentMappingIssue]) -> list[str] | None:
    values = _text_sequence(value, field, issues, allow_empty=False)
    if values is None:
        return None
    normalized: list[str] = []
    for index, value_item in enumerate(values):
        if "://" in value_item or re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", value_item):
            issues.append(
                AgentMappingIssue(
                    "external_source_document",
                    f"{field}[{index}]",
                    "Source documents must be local paths, not URLs or URI references.",
                )
            )
            continue
        try:
            normalized.append(normalize_relative_path(value_item))
        except UnsafeLocalPathError:
            issues.append(
                AgentMappingIssue(
                    "unsafe_source_document",
                    f"{field}[{index}]",
                    "Source documents must be safe relative paths.",
                )
            )
    if len(normalized) != len(set(normalized)):
        issues.append(
            AgentMappingIssue(
                "duplicate_source_document",
                field,
                "Source documents must be unique after normalization.",
            )
        )
    return normalized


def _timestamp(value: object, field: str, issues: list[AgentMappingIssue]) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        issues.append(
            AgentMappingIssue(
                "missing_review_timestamp", field, "Mapping review requires an ISO-8601 timestamp."
            )
        )
        return None
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError:
        parsed = None
    if parsed is None or parsed.tzinfo is None:
        issues.append(
            AgentMappingIssue(
                "invalid_review_timestamp", field, "Review timestamp must include a timezone."
            )
        )
        return None
    return parsed.astimezone(UTC)


def _validate_ambiguity(
    raw_entry: Mapping[object, object], field: str, issues: list[AgentMappingIssue]
) -> None:
    ambiguous = raw_entry.get("ambiguous", False)
    if not isinstance(ambiguous, bool):
        issues.append(
            AgentMappingIssue(
                "invalid_ambiguity", f"{field}.ambiguous", "The ambiguity flag must be boolean."
            )
        )
    elif ambiguous:
        issues.append(
            AgentMappingIssue(
                "ambiguous_mapping",
                f"{field}.ambiguous",
                "Ambiguous relationships cannot be accepted for specification write mode.",
            )
        )
    ambiguity = raw_entry.get("ambiguity")
    if ambiguity not in (None, False, "", "none", "None", [], {}):
        issues.append(
            AgentMappingIssue(
                "ambiguous_mapping",
                f"{field}.ambiguity",
                "Ambiguous relationships cannot be accepted for specification write mode.",
            )
        )


def _validate_source_document_locality(
    source_documents: Sequence[str],
    field: str,
    *,
    video_root: Path | str | None,
    repository_root: Path | str | None,
    issues: list[AgentMappingIssue],
) -> None:
    for index, document in enumerate(source_documents):
        if "://" in document or document.startswith(_SOURCE_REPOSITORY_PREFIXES):
            issues.append(
                AgentMappingIssue(
                    "external_source_document",
                    f"{field}.source_documents[{index}]",
                    "Source documents must be local paths, not upstream references.",
                )
            )
            continue
        if video_root is None:
            continue
        candidate_root = Path(video_root).resolve()
        candidate_path: Path | None = None
        try:
            if document.startswith("business/video/"):
                local_repository_root = (
                    Path(repository_root).resolve()
                    if repository_root is not None
                    else candidate_root.parent.parent
                )
                candidate_path = resolve_under_root(
                    local_repository_root,
                    document,
                    must_exist=True,
                    require_readable=True,
                )
                if not candidate_path.is_relative_to(candidate_root):
                    raise UnsafeLocalPathError("out_of_root", document)
            else:
                candidate_path = resolve_under_root(
                    candidate_root,
                    document,
                    must_exist=True,
                    require_readable=True,
                )
        except (OSError, RuntimeError, UnsafeLocalPathError):
            issues.append(
                AgentMappingIssue(
                    "nonlocal_or_missing_source_document",
                    f"{field}.source_documents[{index}]",
                    "Every source document must resolve to a readable local Video Pack file.",
                )
            )


def _order_entries(
    entries: Sequence[AgentSourceMapEntry], inventory_ids: Sequence[str]
) -> tuple[AgentSourceMapEntry, ...]:
    by_id: dict[str, AgentSourceMapEntry] = {}
    for entry in entries:
        by_id.setdefault(entry.common_agent_id, entry)
    return tuple(by_id[agent_id] for agent_id in inventory_ids if agent_id in by_id)


def _sort_issues(issues: Sequence[AgentMappingIssue]) -> tuple[AgentMappingIssue, ...]:
    return tuple(sorted(issues, key=lambda issue: (issue.code, issue.field, issue.message)))


def _with_issues(
    report: AgentMappingReport, issues: Sequence[AgentMappingIssue]
) -> AgentMappingReport:
    ordered = _sort_issues(issues)
    return AgentMappingReport(
        is_valid=not ordered,
        inventory_agent_ids=report.inventory_agent_ids,
        map_agent_ids=report.map_agent_ids,
        entries=report.entries,
        issues=ordered,
        inventory_digest=report.inventory_digest,
    )


def _resolve_map_input(
    root: Path,
    requested_path: Path | str | None,
    issues: list[AgentMappingIssue],
) -> Path | None:
    """Resolve a map input beneath the video root, including absolute in-root paths."""
    candidate = Path(MAP_FILENAME if requested_path is None else requested_path)
    try:
        if candidate.is_absolute():
            candidate = candidate.resolve().relative_to(root)
        return resolve_under_root(root, candidate)
    except (OSError, RuntimeError, ValueError, UnsafeLocalPathError):
        issues.append(
            AgentMappingIssue(
                "unsafe_source_map_path",
                "source_map",
                "AGENT_SOURCE_MAP.json must resolve beneath the Video Pack root.",
            )
        )
        return None


def _read_json(path: Path, field: str, issues: list[AgentMappingIssue]) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        issues.append(
            AgentMappingIssue(
                "unreadable_json", field, "Local mapping inputs must be readable valid JSON."
            )
        )
        return {}


def _render_map(entries: Sequence[AgentSourceMapEntry]) -> str:
    lines = [
        "# Agent Source Map",
        "",
        "This document is a deterministic projection of the reviewed `AGENT_SOURCE_MAP.json`.",
        "Common Agent IDs remain authoritative; source IDs are relationship provenance only.",
        "",
        "| Common Agent ID | Status | Source Agent IDs | Source Documents | "
        "Rationale | Reviewer | Reviewed At |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for entry in entries:
        lines.append(
            "| "
            + " | ".join(
                (
                    _markdown_cell(entry.common_agent_id),
                    _markdown_cell(entry.mapping_status.value),
                    _markdown_cell(", ".join(entry.source_agent_ids) or "—"),
                    _markdown_cell(", ".join(entry.source_documents)),
                    _markdown_cell(entry.rationale),
                    _markdown_cell(entry.reviewed_by),
                    _markdown_cell(
                        entry.reviewed_at.astimezone(UTC).isoformat().replace("+00:00", "Z")
                    ),
                )
            )
            + " |"
        )
    return "\n".join(lines) + "\n"


def _markdown_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").replace("\r", " ")


# Compatibility aliases for callers that use shorter names.
AgentMappingValidator = AgentSourceMapValidator
MappingValidationReport = AgentMappingReport
ProjectionReport = ProjectionValidationReport
