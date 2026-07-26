"""Deterministic, read-only standalone verification for the local Video Pack.

Standalone verification is deliberately explicit about its isolation boundary.  The
network and both historical upstream repositories must be unavailable before this
module reads a pack asset or invokes a content validator.  Once that precondition
passes, every local validator is run and its redaction-safe findings are aggregated
in stable order.
"""

from __future__ import annotations

import json
import os
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Final, cast

from app.video.inventory import EXPECTED_VIDEO_AGENT_COUNT, VideoInventoryValidator
from app.video.migration.agent_mapping import (
    AgentMappingReport,
    AgentSourceMapValidator,
    validate_projection_files,
    validate_roster_projection,
)
from app.video.migration.canonical import canonicalize_json, sort_findings
from app.video.migration.contracts import CanonicalRecord, ImportFinding, MigrationResult
from app.video.migration.corpus import validate_corpus_integrity
from app.video.migration.operational_assets import OperationalAssetValidator
from app.video.migration.paths import UnsafeLocalPathError, resolve_under_root
from app.video.migration.specifications import validate_specifications
from app.workflows.validator import RegisteredReferences, WorkflowDefinitionValidator

DEFAULT_UPSTREAM_REPOSITORIES: Final[tuple[str, str]] = (
    "generic-swarm-ops",
    "va-agent-swarm",
)
STANDALONE_SCHEMA_VERSION: Final[str] = "1.0"


@dataclass(frozen=True, slots=True)
class StandalonePreconditions(CanonicalRecord):
    """Explicit environment claims supplied by the standalone caller."""

    network_disabled: bool
    upstream_repositories: tuple[str, ...] = DEFAULT_UPSTREAM_REPOSITORIES
    unavailable_upstreams: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.network_disabled, bool):
            raise TypeError("network_disabled must be a boolean.")
        repositories = _unique_text(self.upstream_repositories, "upstream_repositories")
        unavailable = _unique_text(
            self.unavailable_upstreams, "unavailable_upstreams", allow_empty=True
        )
        object.__setattr__(self, "upstream_repositories", repositories)
        object.__setattr__(self, "unavailable_upstreams", unavailable)

    @property
    def is_satisfied(self) -> bool:
        """Return whether network and every configured upstream are unavailable."""
        return self.network_disabled and set(self.upstream_repositories) == set(
            self.unavailable_upstreams
        )


@dataclass(frozen=True, slots=True)
class StandaloneCheck(CanonicalRecord):
    """One named local check and its deterministic findings."""

    name: str
    result: MigrationResult
    findings: tuple[ImportFinding, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("Standalone check names must be nonblank.")
        object.__setattr__(self, "name", self.name.strip())
        object.__setattr__(self, "result", MigrationResult(self.result))
        findings = tuple(self.findings)
        if any(not isinstance(finding, ImportFinding) for finding in findings):
            raise TypeError("Standalone check findings must be ImportFinding records.")
        object.__setattr__(self, "findings", sort_findings(findings))

    @property
    def is_valid(self) -> bool:
        """Return whether this local check passed."""
        return self.result is MigrationResult.PASS


@dataclass(frozen=True, slots=True)
class StandaloneReport(CanonicalRecord):
    """Aggregate machine-readable result for one standalone verification run."""

    result: MigrationResult
    preconditions: StandalonePreconditions
    checks: tuple[StandaloneCheck, ...] = ()
    findings: tuple[ImportFinding, ...] = ()
    content_validation_started: bool = False
    schema_version: str = STANDALONE_SCHEMA_VERSION

    def __post_init__(self) -> None:
        object.__setattr__(self, "result", MigrationResult(self.result))
        if not isinstance(self.preconditions, StandalonePreconditions):
            raise TypeError("preconditions must be StandalonePreconditions.")
        checks = tuple(self.checks)
        if any(not isinstance(check, StandaloneCheck) for check in checks):
            raise TypeError("checks must contain StandaloneCheck records.")
        object.__setattr__(self, "checks", tuple(sorted(checks, key=lambda item: item.name)))
        findings = tuple(self.findings)
        if any(not isinstance(finding, ImportFinding) for finding in findings):
            raise TypeError("findings must contain ImportFinding records.")
        object.__setattr__(self, "findings", sort_findings(findings))
        if self.schema_version != STANDALONE_SCHEMA_VERSION:
            raise ValueError("Unsupported standalone report schema version.")
        if not isinstance(self.content_validation_started, bool):
            raise TypeError("content_validation_started must be a boolean.")

    @property
    def is_valid(self) -> bool:
        """Return whether every precondition and local check passed."""
        return self.result is MigrationResult.PASS

    @property
    def is_success(self) -> bool:
        """Compatibility alias for callers that use success terminology."""
        return self.is_valid

    def to_dict(self) -> dict[str, object]:
        """Return a canonical JSON-compatible report projection."""
        return {
            "schema_version": self.schema_version,
            "result": self.result.value,
            "preconditions": self.preconditions.to_dict(),
            "content_validation_started": self.content_validation_started,
            "checks": [
                {
                    "name": check.name,
                    "result": check.result.value,
                    "findings": [finding.to_dict() for finding in check.findings],
                }
                for check in self.checks
            ],
            "findings": [finding.to_dict() for finding in self.findings],
        }

    def canonical_json(self) -> str:
        """Return stable machine-readable standalone output."""
        return canonicalize_json(self.to_dict())


class StandaloneVerificationBlockedError(ValueError):
    """Raised only by callers that request an exception-style fail-closed gate."""

    def __init__(self, report: StandaloneReport) -> None:
        self.report = report
        super().__init__("Standalone verification did not pass its isolation preconditions.")


def _unique_text(values: Iterable[str], name: str, *, allow_empty: bool = False) -> tuple[str, ...]:
    normalized = tuple(
        sorted({value.strip() for value in values if isinstance(value, str) and value.strip()})
    )
    if not normalized and not allow_empty:
        raise ValueError(f"{name} must contain at least one nonblank value.")
    return normalized


def _finding(
    code: str,
    *,
    path: str = "",
    field: str = "",
    message: str,
) -> ImportFinding:
    return ImportFinding(code=code, path=path, field=field, message=message)


def _coerce_unavailable(
    value: bool | str | Iterable[str] | Mapping[str, object], repositories: Sequence[str]
) -> tuple[str, ...]:
    if isinstance(value, bool):
        return tuple(repositories) if value else ()
    if isinstance(value, str):
        return (value.strip(),) if value.strip() else ()
    if isinstance(value, Mapping):
        return tuple(sorted(key for key, unavailable in value.items() if unavailable is True))
    return tuple(value)


def _precondition_findings(preconditions: StandalonePreconditions) -> tuple[ImportFinding, ...]:
    findings: list[ImportFinding] = []
    if not preconditions.network_disabled:
        findings.append(
            _finding(
                "standalone_network_enabled",
                field="network_disabled",
                message="Standalone verification requires network access to be disabled.",
            )
        )
    configured = set(preconditions.upstream_repositories)
    unavailable = set(preconditions.unavailable_upstreams)
    for repository in sorted(configured - unavailable):
        findings.append(
            _finding(
                "standalone_upstream_available",
                path=repository,
                field="unavailable_upstreams",
                message="Every configured upstream repository must be unavailable.",
            )
        )
    for repository in sorted(unavailable - configured):
        findings.append(
            _finding(
                "standalone_unknown_upstream",
                path=repository,
                field="unavailable_upstreams",
                message="The unavailable-upstream declaration names an unknown repository.",
            )
        )
    return sort_findings(findings)


def _as_mapping(value: object) -> Mapping[object, object]:
    return value if isinstance(value, Mapping) else {}


def _read_json(path: Path, findings: list[ImportFinding], field: str) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        findings.append(
            _finding(
                "missing_local_input",
                path=path.name,
                field=field,
                message="The required local standalone input does not exist.",
            )
        )
    except (OSError, UnicodeError, json.JSONDecodeError):
        findings.append(
            _finding(
                "unreadable_local_input",
                path=path.name,
                field=field,
                message="The local standalone input is not readable valid JSON.",
            )
        )
    return {}


def _read_optional_json(path: Path, findings: list[ImportFinding], field: str) -> object | None:
    if not path.exists():
        return None
    return _read_json(path, findings, field)


def _inventory_ids(value: object) -> tuple[str, ...]:
    entries = _as_mapping(value).get("entries", ())
    if not isinstance(entries, Sequence) or isinstance(entries, (str, bytes, bytearray)):
        return ()
    ids: list[str] = []
    for entry in entries:
        if not isinstance(entry, Mapping):
            continue
        agent_id = entry.get("agent_id")
        if isinstance(agent_id, str):
            ids.append(agent_id)
    return tuple(ids)


def _manifest_ids(value: object) -> tuple[str, ...]:
    entries = _as_mapping(value).get("agents", ())
    if not isinstance(entries, Sequence) or isinstance(entries, (str, bytes, bytearray)):
        return ()
    ids: list[str] = []
    for entry in entries:
        if not isinstance(entry, Mapping):
            continue
        agent_id = entry.get("agent_id")
        if isinstance(agent_id, str):
            ids.append(agent_id)
    return tuple(ids)


def _load_agent_specs(
    video_root: Path, findings: list[ImportFinding]
) -> tuple[dict[str, object], tuple[str, ...]]:
    agents_root = video_root / "agents"
    if not agents_root.is_dir():
        findings.append(
            _finding(
                "missing_agent_directory",
                path="agents",
                message="The local Video Pack agents directory is required.",
            )
        )
        return {}, ()
    specifications: dict[str, object] = {}
    directories: list[str] = []
    for candidate in sorted(agents_root.iterdir(), key=lambda item: item.name):
        if not candidate.is_dir():
            continue
        directories.append(candidate.name)
        specification_path = candidate / "agent_spec.json"
        if not specification_path.exists():
            specifications[candidate.name] = None
            continue
        specifications[candidate.name] = _read_json(
            specification_path,
            findings,
            f"agents/{candidate.name}/agent_spec.json",
        )
    return specifications, tuple(directories)


def _load_workflows(
    video_root: Path, findings: list[ImportFinding]
) -> tuple[dict[str, object], tuple[str, ...]]:
    workflows_root = video_root / "workflows"
    workflows: dict[str, object] = {}
    paths: list[str] = []
    if not workflows_root.is_dir():
        findings.append(
            _finding(
                "missing_safe_baseline_workflow",
                path="workflows/pack_spine.json",
                message="The safe baseline workflow must remain present.",
            )
        )
        return workflows, ()
    for candidate in sorted(workflows_root.rglob("*.dna.json"), key=lambda item: item.as_posix()):
        relative = candidate.relative_to(video_root).as_posix()
        paths.append(relative)
        if not candidate.is_file():
            findings.append(
                _finding(
                    "unsafe_registration_path",
                    path=relative,
                    message="Registered workflow paths must resolve to regular local files.",
                )
            )
            continue
        workflows[relative] = _read_json(candidate, findings, relative)
    return workflows, tuple(paths)


def _load_process_index(video_root: Path, findings: list[ImportFinding]) -> object | None:
    for relative in ("process_coverage.json", "PROCESSES.json", "processes.json"):
        candidate = video_root / relative
        if candidate.exists():
            return _read_json(candidate, findings, relative)
    return None


def _load_operational_records(
    video_root: Path, findings: list[ImportFinding], relative_paths: Sequence[str]
) -> object:
    for relative in relative_paths:
        candidate = video_root / relative
        if candidate.exists():
            value = _read_json(candidate, findings, relative)
            return value if value != {} else {"entries": []}
    return {"entries": []}


def _extract_allowed_tools(manifest: object) -> tuple[str, ...]:
    values: set[str] = set()
    raw_agents = _as_mapping(manifest).get("agents", ())
    if isinstance(raw_agents, Sequence) and not isinstance(raw_agents, (str, bytes, bytearray)):
        for agent in raw_agents:
            if not isinstance(agent, Mapping):
                continue
            raw_tools = agent.get("allowed_tools", ())
            if isinstance(raw_tools, Sequence) and not isinstance(
                raw_tools, (str, bytes, bytearray)
            ):
                values.update(tool for tool in raw_tools if isinstance(tool, str) and tool.strip())
    return tuple(sorted(values))


def _workflow_definition_findings(
    workflow: object,
    path: str,
    inventory_ids: Iterable[str],
    allowed_tools: Iterable[str],
) -> tuple[ImportFinding, ...]:
    definition = _as_mapping(workflow)
    if not definition:
        return (_finding("invalid_workflow", path=path, message="Workflow must be a JSON object."),)
    raw_risk_gates = definition.get("risk_gate_ids", ())
    risk_gates: set[str] = set()
    if isinstance(raw_risk_gates, Sequence) and not isinstance(
        raw_risk_gates, (str, bytes, bytearray)
    ):
        for gate in raw_risk_gates:
            if isinstance(gate, str):
                risk_gates.add(gate)
    rollback = definition.get("rollback")
    rollback_ids: set[str] = set()
    if isinstance(rollback, Mapping):
        plan_id = rollback.get("plan_id")
        if isinstance(plan_id, str):
            rollback_ids.add(plan_id)
    authorization_ids: set[str] = set()
    authorization_id = definition.get("authorization_id")
    if isinstance(authorization_id, str):
        authorization_ids.add(authorization_id)
    references = RegisteredReferences(
        agent_ids=frozenset(inventory_ids),
        tool_ids=frozenset(allowed_tools),
        memory_scope_ids=frozenset(),
        risk_gate_ids=frozenset(risk_gates),
        rollback_plan_ids=frozenset(rollback_ids),
        authorization_ids=frozenset(authorization_ids),
    )
    report = WorkflowDefinitionValidator(references).validate(
        cast(Mapping[str, object], definition)
    )
    return tuple(
        _finding(
            "workflow_definition_invalid",
            path=path,
            field=issue.field,
            message="The safe baseline workflow failed local data-only validation.",
        )
        for issue in report.issues
    )


def _finding_from_inventory(issue: object) -> ImportFinding:
    return _finding(
        str(getattr(issue, "code", "inventory_validation_failure")),
        field=str(getattr(issue, "field", "")),
        message=str(getattr(issue, "message", "The local inventory is invalid.")),
    )


def _finding_from_mapping(issue: object) -> ImportFinding:
    return _finding(
        str(getattr(issue, "code", "mapping_validation_failure")),
        field=str(getattr(issue, "field", "")),
        message=str(getattr(issue, "message", "The local Agent Source Map is invalid.")),
    )


def _finding_from_specification(issue: object) -> ImportFinding:
    agent_id = str(getattr(issue, "agent_id", ""))
    return _finding(
        str(getattr(issue, "code", "specification_validation_failure")),
        path=f"agents/{agent_id}/SPEC.md" if agent_id else "",
        field=str(getattr(issue, "field", "")),
        message=str(getattr(issue, "message", "The local specification is invalid.")),
    )


def _ids_agreement_findings(
    inventory_ids: tuple[str, ...],
    manifest_ids: tuple[str, ...],
    directory_ids: tuple[str, ...],
    mapping_report: AgentMappingReport,
    roster: object,
    specification_ids: tuple[str, ...],
) -> tuple[ImportFinding, ...]:
    expected = set(inventory_ids)
    sources: tuple[tuple[str, tuple[str, ...]], ...] = (
        ("manifest", manifest_ids),
        ("agent_directories", directory_ids),
        ("source_map", mapping_report.map_agent_ids),
        ("specifications", specification_ids),
    )
    findings: list[ImportFinding] = []
    for name, values in sources:
        value_set = set(values)
        if len(values) != EXPECTED_VIDEO_AGENT_COUNT or value_set != expected:
            findings.append(
                _finding(
                    "standalone_agent_id_agreement_failure",
                    field=name,
                    message=(
                        f"{name} must contain exactly the authoritative "
                        f"{EXPECTED_VIDEO_AGENT_COUNT} Common Agent IDs."
                    ),
                )
            )
    roster_values: list[str] = []
    raw_entries = roster.get("entries", ()) if isinstance(roster, Mapping) else ()
    if isinstance(raw_entries, Sequence) and not isinstance(raw_entries, (str, bytes, bytearray)):
        for entry in raw_entries:
            if isinstance(entry, str):
                roster_values.append(entry)
            elif isinstance(entry, Mapping) and isinstance(entry.get("agent_id"), str):
                roster_values.append(entry["agent_id"])
    if len(roster_values) != EXPECTED_VIDEO_AGENT_COUNT or set(roster_values) != expected:
        findings.append(
            _finding(
                "standalone_agent_id_agreement_failure",
                field="roster",
                message=(
                    f"roster must contain exactly the authoritative {EXPECTED_VIDEO_AGENT_COUNT} "
                    "Common Agent IDs."
                ),
            )
        )
    if len(inventory_ids) != EXPECTED_VIDEO_AGENT_COUNT:
        findings.append(
            _finding(
                "standalone_authoritative_inventory_count",
                field="inventory.entries",
                message=(
                    "The authoritative inventory must contain exactly "
                    f"{EXPECTED_VIDEO_AGENT_COUNT} IDs."
                ),
            )
        )
    return tuple(findings)


def _required_reference_findings(
    video_root: Path,
    inventory: object,
    manifest: object,
) -> tuple[ImportFinding, ...]:
    findings: list[ImportFinding] = []
    for source_name, value, collection_name in (
        ("inventory", inventory, "entries"),
        ("manifest", manifest, "agents"),
    ):
        raw_entries = _as_mapping(value).get(collection_name, ())
        if not isinstance(raw_entries, Sequence) or isinstance(
            raw_entries, (str, bytes, bytearray)
        ):
            continue
        for index, entry in enumerate(raw_entries):
            if not isinstance(entry, Mapping):
                continue
            reference = entry.get("agent_spec_path")
            if not isinstance(reference, str):
                continue
            try:
                resolved = resolve_under_root(
                    video_root, reference, must_exist=True, require_readable=True
                )
                if not resolved.is_file():
                    raise UnsafeLocalPathError("not_a_file", reference)
            except (OSError, RuntimeError, UnsafeLocalPathError):
                findings.append(
                    _finding(
                        "nonlocal_or_missing_required_reference",
                        path=reference,
                        field=f"{source_name}.{collection_name}[{index}].agent_spec_path",
                        message=(
                            "Required local references must resolve beneath the Video Pack root."
                        ),
                    )
                )
    return tuple(findings)


def _safe_registration_findings(
    video_root: Path,
    workflow_paths: Sequence[str],
    inventory_ids: Sequence[str],
) -> tuple[ImportFinding, ...]:
    required = [
        "inventory.json",
        "manifest.json",
        "AGENT_SOURCE_MAP.json",
        "ROSTER.json",
        "MAP.md",
        "workflows/pack_spine.json",
        *workflow_paths,
        *(f"agents/{agent_id}/agent_spec.json" for agent_id in inventory_ids),
        *(f"agents/{agent_id}/SPEC.md" for agent_id in inventory_ids),
    ]
    findings: list[ImportFinding] = []
    for relative in sorted(set(required)):
        try:
            resolved = resolve_under_root(
                video_root, relative, must_exist=True, require_readable=True
            )
            if not resolved.is_file():
                raise UnsafeLocalPathError("not_a_file", relative)
        except (OSError, RuntimeError, UnsafeLocalPathError):
            findings.append(
                _finding(
                    "unsafe_registration_path" if ".." in relative else "missing_registered_asset",
                    path=relative,
                    message="Registered Video Pack paths must remain local readable files.",
                )
            )
    for root, directory_names, file_names in os.walk(video_root, followlinks=False):
        current = Path(root)
        for name in sorted((*directory_names, *file_names)):
            candidate = current / name
            if not candidate.is_symlink():
                continue
            try:
                candidate.resolve(strict=True).relative_to(video_root.resolve(strict=True))
            except (OSError, RuntimeError, ValueError):
                findings.append(
                    _finding(
                        "unsafe_registration_path",
                        path=candidate.relative_to(video_root).as_posix(),
                        message="Registered Video Pack links must resolve beneath the pack root.",
                    )
                )
    return tuple(findings)


def _run_check(
    name: str,
    callback: object,
) -> StandaloneCheck:
    try:
        result = callback()  # type: ignore[operator]
        findings = tuple(result)
    except (OSError, RuntimeError, TypeError, ValueError, UnicodeError, json.JSONDecodeError):
        findings = (
            _finding(
                "standalone_validator_error",
                field=name,
                message="A local standalone validator could not complete safely.",
            ),
        )
    return StandaloneCheck(
        name=name,
        result=MigrationResult.PASS if not findings else MigrationResult.FAIL,
        findings=findings,
    )


def verify_standalone(
    video_root: str | os.PathLike[str],
    *,
    repository_root: str | os.PathLike[str] | None = None,
    network_disabled: bool = False,
    upstreams_unavailable: bool | str | Iterable[str] | Mapping[str, object] = False,
    upstream_available: Iterable[str] = (),
    upstream_repositories: Iterable[str] = DEFAULT_UPSTREAM_REPOSITORIES,
) -> StandaloneReport:
    """Run all local standalone checks after isolation preconditions pass.

    ``upstreams_unavailable`` is either ``True`` for all configured repositories,
    or an explicit iterable/mapping naming the unavailable repositories.  The
    default is fail-closed: callers must make both isolation claims explicitly.
    """
    repositories = _unique_text(upstream_repositories, "upstream_repositories")
    unavailable = set(_coerce_unavailable(upstreams_unavailable, repositories))
    available = {
        name.strip() for name in upstream_available if isinstance(name, str) and name.strip()
    }
    configured_repositories = set(repositories)
    unavailable.difference_update(available & configured_repositories)
    unavailable.update(available - configured_repositories)
    preconditions = StandalonePreconditions(
        network_disabled=network_disabled,
        upstream_repositories=repositories,
        unavailable_upstreams=tuple(sorted(unavailable)),
    )
    precondition_findings = _precondition_findings(preconditions)
    if precondition_findings:
        return StandaloneReport(
            result=MigrationResult.FAIL,
            preconditions=preconditions,
            findings=precondition_findings,
            content_validation_started=False,
        )

    root = Path(video_root).resolve(strict=False)
    repository = (
        Path(repository_root).resolve(strict=False)
        if repository_root is not None
        else _repository_root_for(root)
    )
    input_findings: list[ImportFinding] = []
    inventory = _read_json(root / "inventory.json", input_findings, "inventory")
    manifest = _read_json(root / "manifest.json", input_findings, "manifest")
    source_map = _read_json(root / "AGENT_SOURCE_MAP.json", input_findings, "source_map")
    roster = _read_json(root / "ROSTER.json", input_findings, "roster")
    agent_specs, directory_ids = _load_agent_specs(root, input_findings)
    workflows, workflow_paths = _load_workflows(root, input_findings)
    process_index = _load_process_index(root, input_findings)
    knowledge_seeds = _load_operational_records(
        root,
        input_findings,
        ("KNOWLEDGE_SEEDS.json", "knowledge_seeds.json", "knowledge/seeds/index.json"),
    )
    special_skills = _load_operational_records(
        root,
        input_findings,
        ("SPECIAL_SKILLS.json", "special_skills.json", "special_skills/index.json"),
    )

    checks: list[StandaloneCheck] = []
    checks.append(
        StandaloneCheck(
            name="local_inputs",
            result=MigrationResult.PASS if not input_findings else MigrationResult.FAIL,
            findings=tuple(input_findings),
        )
    )

    # Pack-level corpus is optional (redo_migration.md v2). When absent, pass;
    # when present, still enforce integrity.
    corpus_root = root / "corpus"
    if not corpus_root.exists():
        checks.append(
            StandaloneCheck(
                name="corpus_integrity",
                result=MigrationResult.PASS,
                findings=(),
            )
        )
    else:
        corpus_report = validate_corpus_integrity(corpus_root)
        checks.append(
            StandaloneCheck(
                name="corpus_integrity",
                result=corpus_report.result,
                findings=corpus_report.findings,
            )
        )

    inventory_report = VideoInventoryValidator().validate(manifest, inventory, agent_specs)
    inventory_findings = tuple(_finding_from_inventory(issue) for issue in inventory_report.issues)
    checks.append(
        StandaloneCheck(
            name="common_inventory_manifest",
            result=MigrationResult.PASS if inventory_report.is_valid else MigrationResult.FAIL,
            findings=inventory_findings,
        )
    )

    mapping_report = AgentSourceMapValidator().validate(
        inventory,
        source_map,
        video_root=root,
        repository_root=repository,
    )
    mapping_findings = tuple(_finding_from_mapping(issue) for issue in mapping_report.issues)
    if mapping_report.is_valid:
        mapping_findings += tuple(
            _finding_from_mapping(issue)
            for issue in validate_projection_files(root, mapping_report).issues
        )
    checks.append(
        StandaloneCheck(
            name="agent_source_map",
            result=MigrationResult.PASS if not mapping_findings else MigrationResult.FAIL,
            findings=mapping_findings,
        )
    )

    inventory_ids = _inventory_ids(inventory)
    manifest_ids = _manifest_ids(manifest)
    specification_ids = tuple(
        sorted(
            candidate.parent.name
            for candidate in (root / "agents").glob("*/SPEC.md")
            if candidate.is_file()
        )
    )
    roster_projection_findings: tuple[ImportFinding, ...] = ()
    if mapping_report.is_valid:
        roster_report = validate_roster_projection(roster, inventory_ids)
        roster_projection_findings = tuple(
            _finding_from_mapping(issue) for issue in roster_report.issues
        )
    agreement_findings = (
        *roster_projection_findings,
        *_ids_agreement_findings(
            inventory_ids,
            manifest_ids,
            directory_ids,
            mapping_report,
            roster,
            specification_ids,
        ),
    )
    checks.append(
        StandaloneCheck(
            name="agent_id_agreement",
            result=MigrationResult.PASS if not agreement_findings else MigrationResult.FAIL,
            findings=agreement_findings,
        )
    )

    checks.append(
        StandaloneCheck(
            name="required_local_references",
            result=MigrationResult.PASS
            if not _required_reference_findings(root, inventory, manifest)
            else MigrationResult.FAIL,
            findings=_required_reference_findings(root, inventory, manifest),
        )
    )

    specification_report = validate_specifications(
        root,
        repository_root=repository,
        inventory=inventory,
        source_map=source_map,
        use_existing_specs=True,
    )
    specification_findings = tuple(
        _finding_from_specification(issue) for issue in specification_report.issues
    )
    checks.append(
        StandaloneCheck(
            name="specifications",
            result=MigrationResult.PASS if specification_report.is_valid else MigrationResult.FAIL,
            findings=specification_findings,
        )
    )

    operational_validator = OperationalAssetValidator(
        known_agent_ids=inventory_ids,
        allowed_tools=_extract_allowed_tools(manifest),
    )
    operational_findings: list[ImportFinding] = []
    for path, workflow in sorted(workflows.items()):
        assessment = operational_validator.validate_workflow(workflow, workflow_path=path)
        operational_findings.extend(assessment.findings)
    if process_index is not None:
        process_report = operational_validator.validate_process_coverage(
            process_index,
            workflows,
            known_agent_ids=inventory_ids,
            video_root=root,
        )
        operational_findings.extend(process_report.findings)
    knowledge_report = operational_validator.validate_knowledge_seeds(
        knowledge_seeds, video_root=root
    )
    special_skill_report = operational_validator.validate_special_skills(
        special_skills, video_root=root
    )
    operational_findings.extend(knowledge_report.findings)
    operational_findings.extend(special_skill_report.findings)
    checks.append(
        StandaloneCheck(
            name="operational_assets",
            result=MigrationResult.PASS if not operational_findings else MigrationResult.FAIL,
            findings=tuple(operational_findings),
        )
    )

    baseline_findings: tuple[ImportFinding, ...] = ()
    baseline_path = root / "workflows" / "pack_spine.json"
    if baseline_path.is_file():
        baseline_value = _read_json(baseline_path, [], "pack_spine")
        baseline_findings = _workflow_definition_findings(
            baseline_value,
            "workflows/pack_spine.json",
            inventory_ids,
            _extract_allowed_tools(manifest),
        )
    else:
        baseline_findings = (
            _finding(
                "missing_safe_baseline_workflow",
                path="workflows/pack_spine.json",
                message="The safe baseline workflow must remain present.",
            ),
        )
    checks.append(
        StandaloneCheck(
            name="safe_baseline_workflow",
            result=MigrationResult.PASS if not baseline_findings else MigrationResult.FAIL,
            findings=baseline_findings,
        )
    )

    registration_findings = _safe_registration_findings(root, workflow_paths, inventory_ids)
    checks.append(
        StandaloneCheck(
            name="safe_registration_paths",
            result=MigrationResult.PASS if not registration_findings else MigrationResult.FAIL,
            findings=registration_findings,
        )
    )

    findings = sort_findings(tuple(finding for check in checks for finding in check.findings))
    return StandaloneReport(
        result=MigrationResult.PASS if not findings else MigrationResult.FAIL,
        preconditions=preconditions,
        checks=tuple(checks),
        findings=findings,
        content_validation_started=True,
    )


def _repository_root_for(video_root: Path) -> Path:
    resolved = video_root.resolve(strict=False)
    if resolved.name == "video" and resolved.parent.name == "business":
        return resolved.parent.parent
    return resolved


# Compatibility aliases for callers that use validation terminology.
validate_standalone = verify_standalone
check_standalone = verify_standalone
verify_domain_standalone = verify_standalone


class StandaloneVerifier:
    """Object-oriented facade for the read-only standalone verification seam."""

    def __init__(
        self,
        video_root: str | os.PathLike[str] | None = None,
        *,
        repository_root: str | os.PathLike[str] | None = None,
        network_disabled: bool = False,
        upstreams_unavailable: bool | str | Iterable[str] | Mapping[str, object] = False,
        upstream_available: Iterable[str] = (),
        upstream_repositories: Iterable[str] = DEFAULT_UPSTREAM_REPOSITORIES,
    ) -> None:
        self.video_root = video_root
        self.repository_root = repository_root
        self.network_disabled = network_disabled
        self.upstreams_unavailable = upstreams_unavailable
        self.upstream_available = tuple(upstream_available)
        self.upstream_repositories = tuple(upstream_repositories)

    def verify(
        self,
        video_root: str | os.PathLike[str] | None = None,
        *,
        repository_root: str | os.PathLike[str] | None = None,
        network_disabled: bool | None = None,
        upstreams_unavailable: bool | str | Iterable[str] | Mapping[str, object] | None = None,
        upstream_available: Iterable[str] | None = None,
        upstream_repositories: Iterable[str] | None = None,
    ) -> StandaloneReport:
        """Run verification using constructor values and optional call overrides."""
        root = video_root or self.video_root
        if root is None:
            raise ValueError("video_root is required for standalone verification.")
        return verify_standalone(
            root,
            repository_root=self.repository_root if repository_root is None else repository_root,
            network_disabled=(
                self.network_disabled if network_disabled is None else network_disabled
            ),
            upstreams_unavailable=(
                self.upstreams_unavailable
                if upstreams_unavailable is None
                else upstreams_unavailable
            ),
            upstream_available=(
                self.upstream_available if upstream_available is None else upstream_available
            ),
            upstream_repositories=(
                self.upstream_repositories
                if upstream_repositories is None
                else upstream_repositories
            ),
        )

    validate = verify
    check = verify


__all__ = [
    "DEFAULT_UPSTREAM_REPOSITORIES",
    "STANDALONE_SCHEMA_VERSION",
    "AgentSourceMapValidator",
    "OperationalAssetValidator",
    "StandaloneCheck",
    "StandalonePreconditions",
    "StandaloneReport",
    "StandaloneVerificationBlockedError",
    "StandaloneVerifier",
    "VideoInventoryValidator",
    "check_standalone",
    "validate_standalone",
    "verify_domain_standalone",
    "verify_standalone",
]
