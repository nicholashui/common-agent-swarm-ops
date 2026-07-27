"""Local-only drafting and validation of substantive Video Pack specifications.

The builder is deliberately data-only.  It reads the authoritative local inventory,
local ``agent_spec.json`` bindings, a reviewed local source map, and optional local
workflow/corpus metadata.  Upstream identifiers may be described as historical
relationships, but are never used as required inputs or runtime configuration.

Write mode has one mutation boundary: after the complete map and every candidate
specification have passed validation, it writes one ``SPEC.md`` beneath each
inventory-owned agent directory.  Common configuration JSON is never modified.
"""

from __future__ import annotations

import json
import re
import tempfile
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Final, cast

from app.video.migration.agent_mapping import (
    AgentMappingIssue,
    AgentMappingReport,
    AgentSourceMapValidator,
)
from app.video.migration.canonical import canonicalize_json, redact_diagnostic
from app.video.migration.contracts import (
    AgentSourceMapEntry,
    AgentSpecificationReview,
    MigrationResult,
)
from app.video.migration.paths import (
    UnsafeLocalPathError,
    normalize_relative_path,
    resolve_under_root,
)

SPEC_FILENAME: Final[str] = "SPEC.md"
SPEC_SCHEMA_VERSION: Final[str] = "1.0"
REQUIRED_HEADINGS: Final[tuple[str, ...]] = (
    "Identity",
    "Responsibility",
    "Boundaries and escalation",
    "Inputs and outputs",
    "Quality and critique",
    "Runtime binding",
    "Local knowledge sources",
    "Provenance",
)
_CRITICAL_ROLE_MARKERS: Final[tuple[str, ...]] = (
    "orchestrator",
    "compliance",
    "rights",
    "consent",
    "privacy",
    "legal",
    "safety",
    "provenance",
    "release",
    "judge",
    "human_review",
    "human review",
    "review_coordinator",
    "review coordinator",
)
_EXTERNAL_MARKERS: Final[tuple[str, ...]] = (
    "generic-swarm-ops",
    "va-agent-swarm",
)
_REVIEW_PLACEHOLDERS: Final[frozenset[str]] = frozenset(
    {"", "none", "unknown", "unreviewed", "pending", "todo", "tbd", "automation", "system", "bot"}
)
_HEADING_PATTERN: Final[re.Pattern[str]] = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
_LINK_PATTERN: Final[re.Pattern[str]] = re.compile(r"!?(?:\[[^\]]*\])\(([^)\s]+)(?:\s+[^)]*)?\)")
_JSON_FENCE_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"```(?:json)?\s*\n(?P<body>.*?)\n```", re.IGNORECASE | re.DOTALL
)
_EXTERNAL_URL_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"(?i)\b(?:https?|file|ssh)://|\b[A-Za-z][A-Za-z0-9+.-]*://"
)
_REQUIRED_EXTERNAL_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"(?is)(?:required|must\s+(?:read|resolve|use|load)|depends?\s+on).{0,100}"
    r"(?:https?://|generic-swarm-ops|va-agent-swarm)"
)


@dataclass(frozen=True, slots=True)
class SpecificationIssue:
    """A deterministic, redaction-safe specification validation diagnostic."""

    code: str
    agent_id: str = ""
    field: str = ""
    message: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "code", str(self.code).strip().casefold())
        object.__setattr__(self, "agent_id", redact_diagnostic(self.agent_id))
        object.__setattr__(self, "field", redact_diagnostic(self.field))
        object.__setattr__(self, "message", redact_diagnostic(self.message))

    def to_dict(self) -> dict[str, str]:
        """Return the canonical JSON-compatible issue representation."""
        return {
            "agent_id": self.agent_id,
            "code": self.code,
            "field": self.field,
            "message": self.message,
        }


@dataclass(frozen=True, slots=True)
class SpecificationDraft:
    """One candidate local specification and its owning inventory identity."""

    common_agent_id: str
    path: str
    document: str

    def to_dict(self) -> dict[str, str]:
        """Return metadata without copying the document body into reports."""
        return {"common_agent_id": self.common_agent_id, "path": self.path}


@dataclass(frozen=True, slots=True)
class SpecificationReport:
    """Aggregate result for all map and specification validation work."""

    is_valid: bool
    result: MigrationResult
    inventory_agent_ids: tuple[str, ...]
    drafts: tuple[SpecificationDraft, ...] = ()
    issues: tuple[SpecificationIssue, ...] = ()
    mapping_report: AgentMappingReport | None = None
    write_mode: bool = False

    @property
    def can_write(self) -> bool:
        """Return whether the report permits the controlled SPEC write boundary."""
        return self.is_valid and self.mapping_report is not None and self.mapping_report.is_valid

    @property
    def specifications(self) -> tuple[SpecificationDraft, ...]:
        """Compatibility view of candidate specifications."""
        return self.drafts

    @property
    def findings(self) -> tuple[SpecificationIssue, ...]:
        """Compatibility view of aggregate diagnostics."""
        return self.issues

    def to_dict(self) -> dict[str, object]:
        """Return a deterministic machine-readable result without source bodies."""
        return {
            "schema_version": SPEC_SCHEMA_VERSION,
            "mode": "write" if self.write_mode else "dry_run",
            "result": self.result.value,
            "is_valid": self.is_valid,
            "inventory_agent_ids": list(self.inventory_agent_ids),
            "specifications": [draft.to_dict() for draft in self.drafts],
            "findings": [issue.to_dict() for issue in self.issues],
        }

    def canonical_json(self) -> str:
        """Return canonical UTF-8 JSON for the aggregate result."""
        return canonicalize_json(self.to_dict())


class SpecificationWriteBlockedError(ValueError):
    """Raised when controlled SPEC write mode is attempted with invalid inputs."""

    def __init__(self, report: SpecificationReport) -> None:
        self.report = report
        codes = ", ".join(issue.code for issue in report.issues[:3]) or "invalid_specifications"
        super().__init__(f"Specification write mode is blocked: {codes}.")


# Concise aliases used by callers that refer to validation rather than drafting.
SpecificationValidationReport = SpecificationReport
SpecificationValidationIssue = SpecificationIssue


def build_specification_document(
    common_agent_id: str,
    runtime_binding: Mapping[str, object],
    mapping_entry: AgentSourceMapEntry,
    *,
    inventory_entry: Mapping[str, object] | None = None,
    pack_version: str = "unknown",
    workflow_entries: Sequence[Mapping[str, object]] = (),
    corpus_manifest_path: str | None = None,
) -> str:
    """Draft one substantive local SPEC from local runtime and reviewed metadata."""
    role = _text(runtime_binding.get("role")) or _humanize_agent_id(common_agent_id)
    role_name = _clean_role(role)
    inventory_status = _text(inventory_entry.get("status")) if inventory_entry is not None else None
    status = _text(runtime_binding.get("status")) or inventory_status or "registered"
    maturity = _text(inventory_entry.get("maturity_level")) if inventory_entry is not None else None
    maturity = maturity or "L0"
    critique_edges = _as_json_value(
        runtime_binding.get("critique_edges", {"inputs": [], "outputs": []})
    )
    prompt_reference = _text(runtime_binding.get("prompt_reference")) or "not declared"
    rubric_reference = _text(runtime_binding.get("rubric_reference")) or "not declared"
    max_refinement = runtime_binding.get("max_refinement_count", 0)
    source_links = list(mapping_entry.source_documents)
    if corpus_manifest_path is not None and corpus_manifest_path not in source_links:
        source_links.append(corpus_manifest_path)
    source_links = sorted(dict.fromkeys(source_links))
    local_source_lines = [
        "- [Common inventory](../../inventory.json) — authoritative identity and lifecycle.",
        "- [Runtime binding](agent_spec.json) — preserved local configuration contract.",
    ]
    local_source_lines.extend(
        f"- [Reviewed local source document]({_source_link(path)})" for path in source_links
    )
    if not source_links:
        local_source_lines.append("- [Local pack root](../../) — local contract context.")

    workflow_lines = _workflow_context_lines(workflow_entries)
    if workflow_lines:
        handoff_lines = workflow_lines
    else:
        handoff_lines = [
            "- Input artifact: an approved video brief, source context, or upstream "
            "typed production handoff.",
            "- Output artifact: a reviewable video-domain deliverable with acceptance "
            "criteria for the next local role.",
        ]

    inventory_id_line = f"- Common Agent ID: `{common_agent_id}`"
    source_ids = ", ".join(f"`{item}`" for item in mapping_entry.source_agent_ids) or "none"
    runtime_document = _runtime_projection(runtime_binding, common_agent_id)
    lines = [
        f"# {role_name}",
        "",
        "## Identity",
        inventory_id_line,
        f"- Status: `{status}`",
        f"- Maturity: `{maturity}`",
        f"- Pack version: `{pack_version}`",
        "",
        "## Responsibility",
        (
            f"Owns the video-domain {role_name.lower()} outcome by producing a reviewable video "
            "artifact, applying the approved pack rubric, recording acceptance criteria, and "
            "escalating rights, safety, or quality failures before downstream handoff."
        ),
        "",
        "## Boundaries and escalation",
        "- Operates only on approved local video-pack inputs and inert corpus references.",
        "- Does not activate providers, credentials, network access, production agents, "
        "or human-gate bypasses.",
        "- Escalates unresolved rights, consent, privacy, safety, provenance, compliance, "
        "and release findings to the required human gate.",
        "",
        "## Inputs and outputs",
        *handoff_lines,
        "- Acceptance condition: the output is traceable to its local inputs and passes "
        "the applicable quality and safety checks.",
        "",
        "## Quality and critique",
        f"- Local rubric reference: `{rubric_reference}`.",
        f"- Prompt reference: `{prompt_reference}`; references are inert local contract "
        "identifiers.",
        f"- Critique edges: `{canonicalize_json(critique_edges)}`.",
        f"- Refinement limit: `{max_refinement}`; unresolved critique or release findings "
        "escalate rather than bypass a gate.",
        "",
        "## Runtime binding",
        "The following local binding is copied as a read-only summary; it does not "
        "alter the common configuration:",
        "```json",
        canonicalize_json(runtime_document),
        "```",
        "",
        "## Local knowledge sources",
        *local_source_lines,
        "- All references in this section are required local references beneath the "
        "Common Repository root.",
        "",
        "## Provenance",
        f"- Mapping status: `{mapping_entry.mapping_status.value}`; source-agent IDs: "
        f"{source_ids}.",
        f"- Relationship rationale: {mapping_entry.rationale}",
        f"- Reviewed by `{mapping_entry.reviewed_by}` at "
        f"`{mapping_entry.reviewed_at.astimezone(UTC).isoformat().replace('+00:00', 'Z')}`.",
        "- Any upstream repository, commit, or source ID is retained as historical, "
        "non-binding provenance only; local contracts remain authoritative.",
        "",
    ]
    return "\n".join(lines)


def validate_specification_document(
    document: str,
    common_agent_id: str,
    runtime_binding: Mapping[str, object],
    *,
    video_root: Path | str,
    repository_root: Path | str | None = None,
    spec_path: Path | str | None = None,
    mapping_entry: AgentSourceMapEntry | None = None,
    critical_review: object | None = None,
    workflow_entries: Sequence[Mapping[str, object]] = (),
) -> tuple[SpecificationIssue, ...]:
    """Validate one SPEC document and return every discoverable issue in stable order."""
    issues: list[SpecificationIssue] = []
    if not isinstance(document, str) or not document.strip():
        return (
            SpecificationIssue(
                "empty_specification",
                common_agent_id,
                "document",
                "SPEC.md must contain local specification content.",
            ),
        )
    sections, heading_counts = _sections(document)
    for heading in REQUIRED_HEADINGS:
        count = heading_counts.get(heading, 0)
        if count == 0:
            issues.append(
                SpecificationIssue(
                    "missing_required_heading",
                    common_agent_id,
                    heading,
                    f"SPEC.md requires the {heading} section.",
                )
            )
        elif count > 1:
            issues.append(
                SpecificationIssue(
                    "duplicate_required_heading",
                    common_agent_id,
                    heading,
                    f"SPEC.md may contain the {heading} section only once.",
                )
            )
        elif not sections.get(heading, "").strip():
            issues.append(
                SpecificationIssue(
                    "empty_required_section",
                    common_agent_id,
                    heading,
                    f"The {heading} section must contain substantive content.",
                )
            )

    identity = sections.get("Identity", "")
    if common_agent_id not in identity:
        issues.append(
            SpecificationIssue(
                "identity_mismatch",
                common_agent_id,
                "Identity",
                "Identity must name the authoritative Common Agent ID.",
            )
        )
    responsibility = sections.get("Responsibility", "")
    if not _is_substantive_responsibility(responsibility):
        issues.append(
            SpecificationIssue(
                "generic_responsibility",
                common_agent_id,
                "Responsibility",
                "Responsibility must describe a concrete video-domain outcome or artifact.",
            )
        )

    _validate_external_required_references(document, common_agent_id, sections, issues)
    _validate_local_knowledge(
        sections.get("Local knowledge sources", ""),
        common_agent_id,
        video_root,
        repository_root,
        spec_path,
        issues,
    )
    _validate_provenance(sections.get("Provenance", ""), common_agent_id, issues)
    _validate_runtime_binding(
        sections.get("Runtime binding", ""), common_agent_id, runtime_binding, issues
    )
    if _is_critical_role(common_agent_id, runtime_binding):
        _validate_critical_review(common_agent_id, critical_review, issues)
    _validate_workflow_enrichment(common_agent_id, sections, workflow_entries, issues)
    return _sort_issues(issues)


def validate_specification(
    document: str,
    common_agent_id: str,
    runtime_binding: Mapping[str, object],
    *,
    video_root: Path | str,
    repository_root: Path | str | None = None,
    spec_path: Path | str | None = None,
    mapping_entry: AgentSourceMapEntry | None = None,
    critical_review: object | None = None,
    workflow_entries: Sequence[Mapping[str, object]] = (),
) -> tuple[SpecificationIssue, ...]:
    """Compatibility singular alias for :func:`validate_specification_document`."""
    return validate_specification_document(
        document,
        common_agent_id,
        runtime_binding,
        video_root=video_root,
        repository_root=repository_root,
        spec_path=spec_path,
        mapping_entry=mapping_entry,
        critical_review=critical_review,
        workflow_entries=workflow_entries,
    )


def build_specifications(
    video_root: Path | str,
    *,
    repository_root: Path | str | None = None,
    inventory: object | None = None,
    source_map: object | None = None,
    workflow_role_map: object | None = None,
    critical_reviews: object | None = None,
    corpus_manifest: object | None = None,
    write_mode: bool = False,
    use_existing_specs: bool = True,
) -> SpecificationReport:
    """Build and validate all inventory specifications, optionally publishing them.

    The function always validates every inventory identity that can be discovered.
    In write mode it publishes nothing unless the complete reviewed map and all
    candidate specifications pass.  Existing ``SPEC.md`` files are validated by
    default; missing files receive deterministic local drafts.
    """
    root = Path(video_root).resolve(strict=False)
    repository = (
        Path(repository_root).resolve(strict=False)
        if repository_root is not None
        else _repository_root_for(root)
    )
    issues: list[SpecificationIssue] = []
    inventory_value = (
        inventory
        if inventory is not None
        else _read_json(root / "inventory.json", "inventory", issues)
    )
    source_map_value = (
        source_map
        if source_map is not None
        else _read_json(root / "AGENT_SOURCE_MAP.json", "source_map", issues)
    )
    workflow_value = (
        workflow_role_map
        if workflow_role_map is not None
        else _read_optional_json(root / "WORKFLOW_ROLE_MAP.json", issues)
    )
    reviews_value = (
        critical_reviews
        if critical_reviews is not None
        else _read_optional_review_json(root, issues)
    )
    corpus_value = (
        corpus_manifest
        if corpus_manifest is not None
        else _read_optional_json(root / "corpus" / "MANIFEST.json", issues)
    )
    corpus_manifest_path = _validate_corpus_manifest(corpus_value, root, repository, issues)

    mapping_report = AgentSourceMapValidator().validate(
        inventory_value,
        source_map_value,
        video_root=root,
        repository_root=repository,
    )
    issues.extend(_mapping_issues(mapping_report.issues))
    inventory_ids = mapping_report.inventory_agent_ids
    workflow_entries = _workflow_entries(workflow_value, issues)
    entries_by_id = {entry.common_agent_id: entry for entry in mapping_report.entries}
    drafts: list[SpecificationDraft] = []
    for agent_id in inventory_ids:
        mapping_entry = entries_by_id.get(agent_id)
        if mapping_entry is None:
            issues.append(
                SpecificationIssue(
                    "missing_mapping_entry",
                    agent_id,
                    "AGENT_SOURCE_MAP.json",
                    "A reviewed mapping is required before drafting this specification.",
                )
            )
            continue
        runtime_path = root / "agents" / agent_id / "agent_spec.json"
        runtime = _read_json(runtime_path, f"agents/{agent_id}/agent_spec.json", issues)
        if not isinstance(runtime, Mapping):
            issues.append(
                SpecificationIssue(
                    "unreadable_runtime_binding",
                    agent_id,
                    "agent_spec.json",
                    "The local agent runtime binding must be a readable JSON object.",
                )
            )
            continue
        runtime_mapping = cast(Mapping[str, object], runtime)
        inventory_entry = _inventory_entry(inventory_value, agent_id)
        matching_workflows = tuple(
            item for item in workflow_entries if _workflow_agent_id(item) == agent_id
        )
        spec_path = runtime_path.with_name(SPEC_FILENAME)
        document: str | None = None
        if use_existing_specs and spec_path.is_file():
            try:
                document = spec_path.read_text(encoding="utf-8")
            except (OSError, UnicodeError):
                issues.append(
                    SpecificationIssue(
                        "unreadable_specification",
                        agent_id,
                        SPEC_FILENAME,
                        "The local SPEC.md must be readable UTF-8 text.",
                    )
                )
        if document is None:
            document = build_specification_document(
                agent_id,
                runtime_mapping,
                mapping_entry,
                inventory_entry=inventory_entry,
                pack_version=_pack_version(root),
                workflow_entries=matching_workflows,
                corpus_manifest_path=corpus_manifest_path,
            )
        candidate = SpecificationDraft(
            common_agent_id=agent_id,
            path=f"agents/{agent_id}/{SPEC_FILENAME}",
            document=document,
        )
        drafts.append(candidate)
        review = _review_for(
            critical_reviews if critical_reviews is not None else reviews_value, agent_id
        )
        issues.extend(
            validate_specification_document(
                document,
                agent_id,
                runtime_mapping,
                video_root=root,
                repository_root=repository,
                spec_path=spec_path,
                mapping_entry=mapping_entry,
                critical_review=review,
                workflow_entries=matching_workflows,
            )
        )

    ordered_issues = _sort_issues(issues)
    valid = not ordered_issues and mapping_report.is_valid and len(drafts) == len(inventory_ids)
    result = (
        MigrationResult.PASS
        if valid
        else (
            MigrationResult.BLOCKED
            if write_mode and not mapping_report.is_valid
            else MigrationResult.FAIL
        )
    )
    report = SpecificationReport(
        is_valid=valid,
        result=result,
        inventory_agent_ids=tuple(inventory_ids),
        drafts=tuple(drafts),
        issues=ordered_issues,
        mapping_report=mapping_report,
        write_mode=write_mode,
    )
    if write_mode and report.can_write:
        try:
            write_specifications(root, report)
        except (OSError, RuntimeError, UnsafeLocalPathError) as error:
            issue = SpecificationIssue(
                "specification_write_failed",
                "",
                "SPEC.md",
                f"The validated local specifications could not be published: {error}",
            )
            report = replace(
                report,
                is_valid=False,
                result=MigrationResult.FAIL,
                issues=_sort_issues((*report.issues, issue)),
            )
    return report


def validate_specifications(
    video_root: Path | str,
    *,
    repository_root: Path | str | None = None,
    inventory: object | None = None,
    source_map: object | None = None,
    workflow_role_map: object | None = None,
    critical_reviews: object | None = None,
    corpus_manifest: object | None = None,
    use_existing_specs: bool = True,
) -> SpecificationReport:
    """Validate local specifications without writing them."""
    return build_specifications(
        video_root,
        repository_root=repository_root,
        inventory=inventory,
        source_map=source_map,
        workflow_role_map=workflow_role_map,
        critical_reviews=critical_reviews,
        corpus_manifest=corpus_manifest,
        write_mode=False,
        use_existing_specs=use_existing_specs,
    )


def write_specifications(video_root: Path | str, report: SpecificationReport) -> tuple[Path, ...]:
    """Publish exactly one SPEC.md per inventory ID after complete validation."""
    if not report.can_write:
        raise SpecificationWriteBlockedError(report)
    root = Path(video_root).resolve(strict=True)
    expected_ids = tuple(report.inventory_agent_ids)
    drafts_by_id = {draft.common_agent_id: draft for draft in report.drafts}
    if tuple(drafts_by_id) != expected_ids or len(drafts_by_id) != len(expected_ids):
        raise SpecificationWriteBlockedError(report)
    output_paths: list[Path] = []
    with tempfile.TemporaryDirectory(prefix=".spec-build-", dir=str(root)) as staging_text:
        staging_root = Path(staging_text)
        staged_paths: list[tuple[Path, Path]] = []
        for agent_id in expected_ids:
            draft = drafts_by_id[agent_id]
            target = resolve_under_root(root, draft.path)
            agent_dir = target.parent
            if not agent_dir.is_dir():
                raise UnsafeLocalPathError("not_a_directory", draft.path)
            staged = staging_root / f"{len(staged_paths):03d}.SPEC.md"
            staged.write_text(draft.document, encoding="utf-8", newline="\n")
            staged_paths.append((staged, target))
        for staged, target in staged_paths:
            target.parent.mkdir(parents=False, exist_ok=True)
            staged.replace(target)
            output_paths.append(target)
    return tuple(output_paths)


def render_specification(document: str) -> str:
    """Return a normalized newline-terminated document for callers rendering drafts."""
    return document.rstrip("\r\n") + "\n"


def _sections(document: str) -> tuple[dict[str, str], dict[str, int]]:
    matches = list(_HEADING_PATTERN.finditer(document))
    sections: dict[str, str] = {}
    counts: dict[str, int] = {}
    for index, match in enumerate(matches):
        heading = match.group(1).strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(document)
        body = document[start:end].strip()
        counts[heading] = counts.get(heading, 0) + 1
        sections.setdefault(heading, body)
    return sections, counts


def _is_substantive_responsibility(value: str) -> bool:
    normalized = " ".join(value.casefold().split())
    if len(normalized) < 40:
        return False
    if not any(
        term in normalized
        for term in (
            "video",
            "shot",
            "scene",
            "footage",
            "storyboard",
            "script",
            "edit",
            "caption",
            "audio",
            "render",
            "release",
        )
    ):
        return False
    if not any(
        term in normalized
        for term in (
            "artifact",
            "deliverable",
            "outcome",
            "acceptance",
            "handoff",
            "quality",
            "reviewable",
        )
    ):
        return False
    if not any(
        term in normalized
        for term in (
            "produce",
            "producing",
            "create",
            "design",
            "plan",
            "review",
            "validate",
            "coordinate",
            "assemble",
            "deliver",
            "record",
            "escalat",
            "own",
        )
    ):
        return False
    generic_only = ("configuration specialist", "generic role", "video agent", "agent role")
    return not any(normalized == term or normalized.endswith(term) for term in generic_only)


def _validate_external_required_references(
    document: str, agent_id: str, sections: Mapping[str, str], issues: list[SpecificationIssue]
) -> None:
    for heading, body in sections.items():
        if heading == "Provenance":
            continue
        if _EXTERNAL_URL_PATTERN.search(body) or any(
            marker in body.casefold() for marker in _EXTERNAL_MARKERS
        ):
            issues.append(
                SpecificationIssue(
                    "external_required_reference",
                    agent_id,
                    heading,
                    "Required specification references must resolve locally; upstream "
                    "references belong only in historical provenance.",
                )
            )
    provenance = sections.get("Provenance", "")
    if _REQUIRED_EXTERNAL_PATTERN.search(provenance):
        issues.append(
            SpecificationIssue(
                "external_required_reference",
                agent_id,
                "Provenance",
                "An upstream reference may be historical provenance but cannot be "
                "required to understand or validate the role.",
            )
        )
    for target in _extract_links(sections.get("Local knowledge sources", "")):
        if _EXTERNAL_URL_PATTERN.search(target) or any(
            marker in target.casefold() for marker in _EXTERNAL_MARKERS
        ):
            issues.append(
                SpecificationIssue(
                    "external_local_reference",
                    agent_id,
                    "Local knowledge sources",
                    "Local knowledge sources must not use external or upstream references.",
                )
            )


def _validate_local_knowledge(
    body: str,
    agent_id: str,
    video_root: Path | str,
    repository_root: Path | str | None,
    spec_path: Path | str | None,
    issues: list[SpecificationIssue],
) -> None:
    links = _extract_links(body)
    if not links:
        issues.append(
            SpecificationIssue(
                "missing_local_knowledge_reference",
                agent_id,
                "Local knowledge sources",
                "At least one required local knowledge reference is required.",
            )
        )
        return
    root = Path(video_root).resolve(strict=False)
    repo = (
        Path(repository_root).resolve(strict=False)
        if repository_root is not None
        else _repository_root_for(root)
    )
    base = Path(spec_path).resolve(strict=False).parent if spec_path is not None else root
    for target in links:
        try:
            normalized = target.split("#", 1)[0]
            if normalized.startswith("business/video/"):
                path = resolve_under_root(repo, normalized, must_exist=True, require_readable=True)
            else:
                path = (base / normalized).resolve(strict=False)
                if not path.is_relative_to(repo):
                    raise UnsafeLocalPathError("out_of_root", target)
                if not path.exists():
                    raise UnsafeLocalPathError("missing_path", target)
                if not path.is_file() and path != root:
                    raise UnsafeLocalPathError("not_a_file", target)
        except (OSError, RuntimeError, ValueError, UnsafeLocalPathError):
            issues.append(
                SpecificationIssue(
                    "nonlocal_or_missing_knowledge_reference",
                    agent_id,
                    "Local knowledge sources",
                    "Every required local knowledge reference must resolve to a "
                    "readable repository-local file.",
                )
            )


def _validate_provenance(body: str, agent_id: str, issues: list[SpecificationIssue]) -> None:
    normalized = body.casefold()
    if "historical" not in normalized or (
        "non-binding" not in normalized and "non binding" not in normalized
    ):
        issues.append(
            SpecificationIssue(
                "non_historical_provenance",
                agent_id,
                "Provenance",
                "Provenance must explicitly identify upstream information as historical "
                "and non-binding.",
            )
        )


def _validate_runtime_binding(
    body: str,
    agent_id: str,
    runtime_binding: Mapping[str, object],
    issues: list[SpecificationIssue],
) -> None:
    parsed: Mapping[str, object] | None = None
    for match in _JSON_FENCE_PATTERN.finditer(body):
        try:
            candidate = json.loads(match.group("body"))
        except (TypeError, ValueError, json.JSONDecodeError):
            continue
        if isinstance(candidate, Mapping) and candidate.get("agent_id") == agent_id:
            parsed = cast(Mapping[str, object], candidate)
            break
    if parsed is None:
        issues.append(
            SpecificationIssue(
                "invalid_runtime_binding",
                agent_id,
                "Runtime binding",
                "Runtime binding must contain a readable local JSON binding.",
            )
        )
        return
    expected = _runtime_projection(runtime_binding, agent_id)
    for field in (
        "agent_id",
        "allowed_tools",
        "budget_policy",
        "critique_edges",
        "max_refinement_count",
        "model_policy",
        "production_activation_requested",
        "status",
    ):
        if parsed.get(field) != expected.get(field):
            issues.append(
                SpecificationIssue(
                    "runtime_binding_changed",
                    agent_id,
                    f"Runtime binding.{field}",
                    "SPEC.md runtime binding must preserve the common agent configuration exactly.",
                )
            )
    if parsed.get("production_activation_requested") is not False:
        production_ok = False
        try:
            from app.video.media_production import load_production_profile

            production_ok = load_production_profile().get("enabled") is True
        except Exception:
            production_ok = False
        if not production_ok:
            issues.append(
                SpecificationIssue(
                    "production_activation_requested",
                    agent_id,
                    "Runtime binding.production_activation_requested",
                    "Local specifications cannot request production activation "
                    "unless the pack production profile is enabled.",
                )
            )
    model_policy = parsed.get("model_policy")
    if isinstance(model_policy, Mapping) and model_policy.get("network_access") is not False:
        production_ok = False
        try:
            from app.video.media_production import load_production_profile

            production_ok = load_production_profile().get("enabled") is True
        except Exception:
            production_ok = False
        if not production_ok:
            issues.append(
                SpecificationIssue(
                    "network_access_requested",
                    agent_id,
                    "Runtime binding.model_policy.network_access",
                    "Local specification runtime binding cannot enable network access.",
                )
            )


def _validate_critical_review(
    agent_id: str, review: object | None, issues: list[SpecificationIssue]
) -> None:
    reviewer: str | None
    result: str | None
    timestamp: str | None
    if isinstance(review, AgentSpecificationReview):
        reviewer = review.reviewer
        result = review.result
        timestamp = review.reviewed_at.isoformat()
    elif isinstance(review, Mapping):
        reviewer = _text(review.get("reviewer", review.get("reviewed_by")))
        result = _text(review.get("result"))
        timestamp = _text(review.get("reviewed_at"))
    else:
        issues.append(
            SpecificationIssue(
                "missing_critical_review",
                agent_id,
                "critical_review",
                "Critical roles require a completed local human specification review.",
            )
        )
        return
    if reviewer is None or reviewer.casefold() in _REVIEW_PLACEHOLDERS:
        issues.append(
            SpecificationIssue(
                "missing_critical_review",
                agent_id,
                "critical_review.reviewer",
                "Critical specification review requires a real reviewer identity.",
            )
        )
    if result != "pass":
        issues.append(
            SpecificationIssue(
                "critical_review_not_passed",
                agent_id,
                "critical_review.result",
                "Critical specification review must have result=pass.",
            )
        )
    if timestamp is None or not _timestamp_is_utc(timestamp):
        issues.append(
            SpecificationIssue(
                "invalid_critical_review_timestamp",
                agent_id,
                "critical_review.reviewed_at",
                "Critical specification review requires a timezone-aware timestamp.",
            )
        )


def _validate_workflow_enrichment(
    agent_id: str,
    sections: Mapping[str, str],
    workflow_entries: Sequence[Mapping[str, object]],
    issues: list[SpecificationIssue],
) -> None:
    implemented = [
        entry for entry in workflow_entries if _text(entry.get("mapping_status")) == "implemented"
    ]
    if not implemented:
        return
    inputs = sections.get("Inputs and outputs", "").casefold()
    quality = sections.get("Quality and critique", "").casefold()
    if "handoff" not in inputs and "artifact" not in inputs:
        issues.append(
            SpecificationIssue(
                "missing_workflow_handoff",
                agent_id,
                "Inputs and outputs",
                "Implemented workflow roles require local handoff or artifact information.",
            )
        )
    if "critique" not in quality and "escalat" not in quality:
        issues.append(
            SpecificationIssue(
                "missing_workflow_critique",
                agent_id,
                "Quality and critique",
                "Implemented workflow roles require local critique or escalation information.",
            )
        )


def _runtime_projection(runtime_binding: Mapping[str, object], agent_id: str) -> dict[str, object]:
    fields = (
        "agent_id",
        "allowed_tools",
        "budget_policy",
        "critique_edges",
        "max_refinement_count",
        "model_policy",
        "production_activation_requested",
        "prompt_reference",
        "role",
        "rubric_reference",
        "schema_version",
        "status",
    )
    projection: dict[str, object] = {
        field: _as_json_value(runtime_binding.get(field))
        for field in fields
        if field in runtime_binding
    }
    projection["agent_id"] = agent_id
    projection.setdefault("allowed_tools", [])
    projection.setdefault("production_activation_requested", False)
    return projection


def _workflow_context_lines(entries: Sequence[Mapping[str, object]]) -> list[str]:
    lines: list[str] = []
    for entry in entries:
        workflow_id = _text(entry.get("workflow_id")) or "local workflow"
        phase_id = _text(entry.get("phase_id")) or "local phase"
        documented_role = _text(entry.get("documented_role")) or "mapped role"
        resolution = entry.get("resolution")
        resolution_id = ""
        if isinstance(resolution, Mapping):
            resolution_id = _text(resolution.get("common_agent_id")) or ""
        lines.append(
            f"- Workflow `{workflow_id}` phase `{phase_id}` role `{documented_role}` "
            f"uses typed video handoffs for `{resolution_id or 'this Common Agent ID'}`."
        )
    return lines


def _sections_heading_count(document: str) -> dict[str, int]:
    return _sections(document)[1]


def _extract_links(body: str) -> tuple[str, ...]:
    return tuple(match.group(1).strip().strip("<>") for match in _LINK_PATTERN.finditer(body))


def _mapping_issues(issues: Sequence[AgentMappingIssue]) -> tuple[SpecificationIssue, ...]:
    return tuple(
        SpecificationIssue(
            issue.code,
            issue.field if issue.field.startswith("video.") else "",
            issue.field,
            issue.message,
        )
        for issue in issues
    )


def _sort_issues(issues: Sequence[SpecificationIssue]) -> tuple[SpecificationIssue, ...]:
    return tuple(
        sorted(issues, key=lambda issue: (issue.agent_id, issue.code, issue.field, issue.message))
    )


def _read_json(path: Path, field: str, issues: list[SpecificationIssue]) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        issues.append(
            SpecificationIssue(
                "unreadable_local_input",
                "",
                field,
                "Local specification inputs must be readable valid JSON.",
            )
        )
        return {}


def _read_optional_json(path: Path, issues: list[SpecificationIssue]) -> object | None:
    if not path.exists():
        return None
    return _read_json(path, path.name, issues)


def _read_optional_review_json(root: Path, issues: list[SpecificationIssue]) -> object | None:
    for filename in ("SPEC_REVIEWS.json", "CRITICAL_REVIEWS.json"):
        candidate = root / filename
        if candidate.exists():
            return _read_json(candidate, filename, issues)
    return None


def _validate_corpus_manifest(
    value: object | None, root: Path, repository: Path, issues: list[SpecificationIssue]
) -> str | None:
    if value is None:
        return None
    if not isinstance(value, Mapping):
        issues.append(
            SpecificationIssue(
                "invalid_corpus_manifest",
                "",
                "corpus/MANIFEST.json",
                "The local corpus manifest must be a JSON object.",
            )
        )
        return None
    entries = value.get("entries")
    if not isinstance(entries, Sequence) or isinstance(entries, (str, bytes, bytearray)):
        issues.append(
            SpecificationIssue(
                "invalid_corpus_manifest",
                "",
                "corpus/MANIFEST.json.entries",
                "The local corpus manifest entries must be an array.",
            )
        )
        return None
    for index, entry in enumerate(entries):
        if not isinstance(entry, Mapping) or not isinstance(entry.get("path"), str):
            issues.append(
                SpecificationIssue(
                    "invalid_corpus_manifest_entry",
                    "",
                    f"corpus/MANIFEST.json.entries[{index}]",
                    "Corpus manifest entries require a destination-relative path.",
                )
            )
            continue
        try:
            path = normalize_relative_path(entry["path"])
            # Accept pack-relative paths (corpus/study/...) or corpus-root-relative (study/...).
            if path.startswith("corpus/"):
                resolve_under_root(
                    repository, f"business/video/{path}", must_exist=True, require_readable=True
                )
            else:
                corpus_root = root / "corpus" if (root / "corpus").is_dir() else root
                resolve_under_root(
                    corpus_root, path, must_exist=True, require_readable=True
                )
        except (TypeError, ValueError, OSError, RuntimeError, UnsafeLocalPathError):
            issues.append(
                SpecificationIssue(
                    "nonlocal_or_missing_corpus_reference",
                    "",
                    f"corpus/MANIFEST.json.entries[{index}].path",
                    "Corpus manifest paths must resolve to local readable corpus files.",
                )
            )
    return "corpus/MANIFEST.json"


def _workflow_entries(
    value: object | None, issues: list[SpecificationIssue]
) -> tuple[Mapping[str, object], ...]:
    if value is None:
        return ()
    raw: object = (
        value.get("entries", value.get("mappings", ())) if isinstance(value, Mapping) else value
    )
    if not isinstance(raw, Sequence) or isinstance(raw, (str, bytes, bytearray)):
        issues.append(
            SpecificationIssue(
                "invalid_workflow_role_map",
                "",
                "WORKFLOW_ROLE_MAP.json",
                "Local workflow-role mappings must contain an entries array.",
            )
        )
        return ()
    entries: list[Mapping[str, object]] = []
    for index, item in enumerate(raw):
        if not isinstance(item, Mapping):
            issues.append(
                SpecificationIssue(
                    "invalid_workflow_role_map_entry",
                    "",
                    f"WORKFLOW_ROLE_MAP.json.entries[{index}]",
                    "Each workflow-role mapping must be a JSON object.",
                )
            )
            continue
        serialized = canonicalize_json(item).casefold()
        if any(
            marker in serialized for marker in _EXTERNAL_MARKERS
        ) or _EXTERNAL_URL_PATTERN.search(serialized):
            issues.append(
                SpecificationIssue(
                    "external_workflow_reference",
                    _workflow_agent_id(item),
                    f"WORKFLOW_ROLE_MAP.json.entries[{index}]",
                    "Workflow-role mappings must remain local and historical provenance "
                    "cannot be a required input.",
                )
            )
        entries.append(item)
    return tuple(
        sorted(
            entries,
            key=lambda item: (
                _text(item.get("workflow_id")) or "",
                _text(item.get("phase_id")) or "",
                _text(item.get("documented_role")) or "",
            ),
        )
    )


def _workflow_agent_id(entry: Mapping[str, object]) -> str:
    direct = _text(entry.get("common_agent_id"))
    if direct:
        return direct
    resolution = entry.get("resolution")
    if isinstance(resolution, Mapping):
        return _text(resolution.get("common_agent_id")) or ""
    return ""


def _review_for(reviews: object | None, agent_id: str) -> object | None:
    if isinstance(reviews, AgentSpecificationReview):
        return reviews if reviews.common_agent_id == agent_id else None
    if isinstance(reviews, Mapping):
        direct = reviews.get(agent_id)
        if isinstance(direct, (Mapping, AgentSpecificationReview)):
            return direct
        raw = reviews.get("reviews")
        if isinstance(raw, Sequence) and not isinstance(raw, (str, bytes, bytearray)):
            return _review_for(raw, agent_id)
    if isinstance(reviews, Sequence) and not isinstance(reviews, (str, bytes, bytearray)):
        for item in reviews:
            if isinstance(item, AgentSpecificationReview) and item.common_agent_id == agent_id:
                return item
            if isinstance(item, Mapping):
                item_id = _text(item.get("common_agent_id")) or _text(item.get("agent_id"))
                if item_id == agent_id:
                    return item
    return None


def _inventory_entry(inventory: object, agent_id: str) -> Mapping[str, object] | None:
    if not isinstance(inventory, Mapping):
        return None
    entries = inventory.get("entries")
    if not isinstance(entries, Sequence) or isinstance(entries, (str, bytes, bytearray)):
        return None
    for item in entries:
        if isinstance(item, Mapping) and item.get("agent_id") == agent_id:
            return item
    return None


def _pack_version(root: Path) -> str:
    value = _read_json_quiet(root / "manifest.json")
    if not isinstance(value, Mapping):
        return "unknown"
    return _text(value.get("pack_version")) or "unknown"


def _read_json_quiet(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {}


def _repository_root_for(video_root: Path) -> Path:
    resolved = video_root.resolve(strict=False)
    if resolved.name == "video" and resolved.parent.name == "business":
        return resolved.parent.parent
    return resolved


def _text(value: object) -> str | None:
    return value.strip() if isinstance(value, str) and value.strip() else None


def _as_json_value(value: object) -> object:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Mapping):
        return {str(key): _as_json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_as_json_value(item) for item in value]
    return str(value)


def _humanize_agent_id(agent_id: str) -> str:
    return agent_id.removeprefix("video.").replace("_", " ").replace("-", " ").title()


def _clean_role(role: str) -> str:
    cleaned = re.sub(r"(?i)^video\s+", "", role).strip()
    cleaned = re.sub(r"(?i)\s+configuration specialist$", "", cleaned).strip()
    return cleaned or "Video Agent"


def _safe_render_path(path: str) -> str:
    try:
        return normalize_relative_path(path)
    except (TypeError, ValueError, UnsafeLocalPathError):
        return redact_diagnostic(path)


def _source_link(path: str) -> str:
    normalized = _safe_render_path(path)
    if normalized.startswith("business/video/"):
        return f"../../../{normalized}"
    return f"../../{normalized}"


def _is_critical_role(agent_id: str, runtime_binding: Mapping[str, object]) -> bool:
    text = f"{agent_id} {_text(runtime_binding.get('role')) or ''}".casefold()
    return any(marker in text for marker in _CRITICAL_ROLE_MARKERS)


def _timestamp_is_utc(value: str) -> bool:
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None and parsed.astimezone(UTC) is not None


def _typed_kwargs(values: Mapping[str, object]) -> dict[str, object]:
    return dict(values)


def _typed_build_kwargs(values: Mapping[str, object]) -> dict[str, object]:
    return dict(values)


class SpecificationValidator:
    """Object-oriented facade for singular and batch local SPEC validation."""

    def validate(
        self,
        document: str,
        common_agent_id: str,
        runtime_binding: Mapping[str, object],
        *,
        video_root: Path | str,
        repository_root: Path | str | None = None,
        spec_path: Path | str | None = None,
        mapping_entry: AgentSourceMapEntry | None = None,
        critical_review: object | None = None,
        workflow_entries: Sequence[Mapping[str, object]] = (),
    ) -> tuple[SpecificationIssue, ...]:
        """Validate one local SPEC document."""
        return validate_specification_document(
            document,
            common_agent_id,
            runtime_binding,
            video_root=video_root,
            repository_root=repository_root,
            spec_path=spec_path,
            mapping_entry=mapping_entry,
            critical_review=critical_review,
            workflow_entries=workflow_entries,
        )

    def validate_all(
        self,
        video_root: Path | str,
        *,
        repository_root: Path | str | None = None,
        inventory: object | None = None,
        source_map: object | None = None,
        workflow_role_map: object | None = None,
        critical_reviews: object | None = None,
        corpus_manifest: object | None = None,
        use_existing_specs: bool = True,
    ) -> SpecificationReport:
        """Validate every inventory-owned local SPEC document."""
        return validate_specifications(
            video_root,
            repository_root=repository_root,
            inventory=inventory,
            source_map=source_map,
            workflow_role_map=workflow_role_map,
            critical_reviews=critical_reviews,
            corpus_manifest=corpus_manifest,
            use_existing_specs=use_existing_specs,
        )


class SpecificationBuilder:
    """Object-oriented facade for controlled local SPEC drafting and writes."""

    def build(
        self,
        video_root: Path | str,
        *,
        repository_root: Path | str | None = None,
        inventory: object | None = None,
        source_map: object | None = None,
        workflow_role_map: object | None = None,
        critical_reviews: object | None = None,
        corpus_manifest: object | None = None,
        write_mode: bool = False,
        use_existing_specs: bool = True,
    ) -> SpecificationReport:
        """Build all local specifications and optionally publish validated output."""
        return build_specifications(
            video_root,
            repository_root=repository_root,
            inventory=inventory,
            source_map=source_map,
            workflow_role_map=workflow_role_map,
            critical_reviews=critical_reviews,
            corpus_manifest=corpus_manifest,
            write_mode=write_mode,
            use_existing_specs=use_existing_specs,
        )


AgentSpecificationValidator = SpecificationValidator
AgentSpecificationBuilder = SpecificationBuilder


# Friendly aliases for callers using the noun-first API names.
draft_specification = build_specification_document
draft_specifications = build_specifications
validate_specs = validate_specifications
write_specs = write_specifications
