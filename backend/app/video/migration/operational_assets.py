"""Fail-closed validation for local Video Pack operational assets.

This module validates workflow, process, knowledge-seed, and special-skill
*records*.  It never executes a workflow, loads corpus content as configuration,
or creates a second runtime.  The only optional mutation is publication of a
validated workflow definition as inert JSON beneath ``workflows/``; the safe
``pack_spine.json`` is never replaced or deleted by that operation.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Final, cast

from app.video.migration.canonical import (
    canonicalize_json,
    digest_json,
    redact_diagnostic,
    sort_findings,
)
from app.video.migration.common_contracts import validate_imported_configuration
from app.video.migration.contracts import (
    AdaptedWorkflowAssessment,
    HistoricalProvenance,
    ImportFinding,
    KnowledgeSeedRecord,
    MigrationResult,
    ReviewResult,
    SpecialSkillReview,
)
from app.video.migration.paths import (
    UnsafeLocalPathError,
    normalize_relative_path,
    resolve_under_root,
)
from app.workflows.validator import (
    MAX_HANDOFFS,
    MAX_NODES,
    MAX_TOOL_REQUESTS,
    MAX_WALL_CLOCK_SECONDS,
)

PACK_SPINE_PATH: Final[str] = "workflows/pack_spine.json"
DEFAULT_WORKFLOW_DIRECTORY: Final[str] = "workflows"
MAX_CRITIQUE_ITERATIONS: Final[int] = 10
_REVIEW_PLACEHOLDERS: Final[frozenset[str]] = frozenset(
    {"", "none", "unknown", "unreviewed", "pending", "todo", "tbd", "automation", "system", "bot"}
)
_SHA256: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True, slots=True)
class OperationalAssetIssue:
    """A stable, redaction-safe diagnostic for an operational asset."""

    code: str
    field: str = ""
    message: str = ""
    path: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "code", redact_diagnostic(self.code).casefold())
        object.__setattr__(self, "field", redact_diagnostic(self.field))
        object.__setattr__(self, "message", redact_diagnostic(self.message))
        object.__setattr__(self, "path", redact_diagnostic(self.path))

    def to_finding(self) -> ImportFinding:
        """Project the issue onto the common migration diagnostic contract."""
        return ImportFinding(
            code=self.code,
            path=self.path,
            field=self.field,
            message=self.message,
        )


@dataclass(frozen=True, slots=True)
class AssetValidationReport:
    """Result shared by process, knowledge-seed, and special-skill validators."""

    result: MigrationResult
    findings: tuple[ImportFinding, ...] = ()
    accepted_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "result", MigrationResult(self.result))
        object.__setattr__(self, "findings", sort_findings(tuple(self.findings)))
        object.__setattr__(self, "accepted_ids", tuple(sorted(set(self.accepted_ids))))

    @property
    def is_valid(self) -> bool:
        """Return whether the supplied assets may be registered."""
        return self.result is MigrationResult.PASS

    @property
    def issues(self) -> tuple[ImportFinding, ...]:
        """Compatibility alias used by existing validators."""
        return self.findings


@dataclass(frozen=True, slots=True)
class OperationalAssetReport:
    """Aggregate deterministic result for all operational asset categories."""

    result: MigrationResult
    findings: tuple[ImportFinding, ...] = ()
    workflow_assessments: tuple[AdaptedWorkflowAssessment, ...] = ()
    process_report: AssetValidationReport | None = None
    knowledge_report: AssetValidationReport | None = None
    special_skill_report: AssetValidationReport | None = None
    accepted_workflow_paths: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "result", MigrationResult(self.result))
        object.__setattr__(self, "findings", sort_findings(tuple(self.findings)))
        object.__setattr__(
            self,
            "workflow_assessments",
            tuple(sorted(self.workflow_assessments, key=lambda item: item.workflow_path)),
        )
        object.__setattr__(
            self, "accepted_workflow_paths", tuple(sorted(set(self.accepted_workflow_paths)))
        )

    @property
    def is_valid(self) -> bool:
        """Return whether every supplied operational asset passed validation."""
        return self.result is MigrationResult.PASS

    @property
    def issues(self) -> tuple[ImportFinding, ...]:
        """Compatibility alias used by existing migration reports."""
        return self.findings

    @property
    def assessments(self) -> tuple[AdaptedWorkflowAssessment, ...]:
        """Compatibility alias for workflow assessment consumers."""
        return self.workflow_assessments


# Names make the category reports discoverable without introducing separate,
# mutable result models for each asset kind.
ProcessCoverageReport = AssetValidationReport
KnowledgeSeedValidationReport = AssetValidationReport
SpecialSkillValidationReport = AssetValidationReport


def _mapping(value: object) -> Mapping[object, object] | None:
    if isinstance(value, Mapping):
        return cast(Mapping[object, object], value)
    return None


def _sequence(value: object) -> Sequence[object] | None:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return value
    return None


def _text(value: object) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _first(mapping: Mapping[object, object], *keys: str) -> tuple[str | None, object]:
    for key in keys:
        if key in mapping:
            return key, mapping[key]
    return None, None


def _issue(
    code: str,
    *,
    field: str = "",
    message: str,
    path: str = "",
) -> ImportFinding:
    return OperationalAssetIssue(code, field=field, message=message, path=path).to_finding()


def _sorted_findings(findings: Iterable[ImportFinding]) -> tuple[ImportFinding, ...]:
    return sort_findings(tuple(findings))


def _known_ids(value: object) -> frozenset[str]:
    """Extract Common Agent IDs from an inventory, manifest, or ID iterable."""
    if isinstance(value, Mapping):
        raw_entries: object = value.get("entries", value.get("agents", ()))
        entries = _sequence(raw_entries)
        if entries is None:
            return frozenset()
        found: set[str] = set()
        for entry in entries:
            if isinstance(entry, str) and entry.strip():
                found.add(entry.strip())
            else:
                entry_mapping = _mapping(entry)
                if entry_mapping is None:
                    continue
                for key in ("agent_id", "common_agent_id", "id"):
                    candidate = _text(entry_mapping.get(key))
                    if candidate is not None:
                        found.add(candidate)
                        break
        return frozenset(found)
    if isinstance(value, str):
        return frozenset({value.strip()}) if value.strip() else frozenset()
    if value is None:
        return frozenset()
    if isinstance(value, Iterable):
        return frozenset(item.strip() for item in value if isinstance(item, str) and item.strip())
    return frozenset()


def _candidate_digest(value: object) -> str:
    try:
        return digest_json(value)
    except (TypeError, ValueError):
        return digest_json({"invalid_asset_type": type(value).__name__})


def _contract_digest(value: object | None) -> str:
    if isinstance(value, str) and _SHA256.fullmatch(value.casefold()):
        return value.casefold()
    return _candidate_digest({"common_contract": value if value is not None else "local"})


def _workflow_path(value: object, fallback: str = "workflow.json") -> tuple[str, str | None]:
    candidate = _text(value) or fallback
    try:
        return normalize_relative_path(candidate), None
    except UnsafeLocalPathError as error:
        return fallback, error.code


def _text_values(value: object) -> tuple[str, ...] | None:
    values = _sequence(value)
    if values is None:
        return None
    result: list[str] = []
    for item in values:
        item_text = _text(item)
        if item_text is None:
            return None
        result.append(item_text)
    return tuple(result)


def _asset_mapping(value: object) -> Mapping[object, object] | None:
    if isinstance(value, (KnowledgeSeedRecord, SpecialSkillReview)):
        return cast(Mapping[object, object], value.to_dict())
    return _mapping(value)


class OperationalAssetValidator:
    """Validate local operational records against common, non-active contracts.

    ``known_agent_ids`` and ``allowed_tools`` are host-owned inputs.  A workflow's
    own declarations never extend those sets; they are only inspected for use.
    """

    def __init__(
        self,
        known_agent_ids: Iterable[str] | Mapping[object, object] | None = None,
        allowed_tools: Iterable[str] | None = None,
        *,
        inventory: object | None = None,
        common_agent_ids: Iterable[str] | Mapping[object, object] | None = None,
        allowed_tool_ids: Iterable[str] | None = None,
        common_contract_digest: str | None = None,
    ) -> None:
        source_ids = (
            inventory
            if inventory is not None
            else common_agent_ids
            if common_agent_ids is not None
            else known_agent_ids
        )
        self.known_agent_ids = _known_ids(source_ids)
        configured_tools = allowed_tools if allowed_tools is not None else allowed_tool_ids
        self.allowed_tools = (
            frozenset(
                tool.strip() for tool in configured_tools if isinstance(tool, str) and tool.strip()
            )
            if configured_tools is not None
            else None
        )
        self.common_contract_digest = common_contract_digest

    def validate_workflow(
        self,
        workflow: object,
        *,
        workflow_path: str = "workflow.json",
        known_agent_ids: Iterable[str] | Mapping[object, object] | None = None,
        common_agent_ids: Iterable[str] | Mapping[object, object] | None = None,
        allowed_tools: Iterable[str] | None = None,
        allowed_tool_ids: Iterable[str] | None = None,
        common_contract_digest: str | None = None,
    ) -> AdaptedWorkflowAssessment:
        """Validate one adapted workflow without executing or compiling it."""
        definition = _mapping(workflow)
        normalized_path, path_error = _workflow_path(
            workflow_path
            if workflow_path != "workflow.json"
            else (definition.get("workflow_path") if definition is not None else None),
            fallback="workflow.json",
        )
        findings: list[ImportFinding] = []
        if path_error is not None:
            findings.append(
                _issue(
                    "unsafe_workflow_path",
                    field="workflow_path",
                    path=normalized_path,
                    message="Adapted workflow paths must be safe local relative paths.",
                )
            )
        if definition is None:
            findings.append(
                _issue(
                    "invalid_workflow",
                    field="workflow",
                    path=normalized_path,
                    message="An adapted workflow must be a JSON object.",
                )
            )
            return self._workflow_assessment(
                normalized_path, workflow, findings, common_contract_digest
            )

        ids_source = common_agent_ids if common_agent_ids is not None else known_agent_ids
        ids = _known_ids(ids_source) if ids_source is not None else self.known_agent_ids
        effective_allowed_tools = allowed_tools if allowed_tools is not None else allowed_tool_ids
        if not ids:
            findings.append(
                _issue(
                    "missing_common_agent_inventory",
                    field="agents",
                    path=normalized_path,
                    message="Workflow validation requires the authoritative Common Agent ID set.",
                )
            )
        self._validate_workflow_agents(definition, ids, normalized_path, findings)
        self._validate_workflow_budgets(definition, normalized_path, findings)
        self._validate_workflow_tools(
            definition, normalized_path, findings, effective_allowed_tools
        )
        self._validate_required_controls(definition, normalized_path, findings)
        self._validate_common_contract(
            definition, normalized_path, findings, common_contract_digest
        )
        boundary = validate_imported_configuration(definition)
        findings.extend(boundary.findings)
        return self._workflow_assessment(
            normalized_path, workflow, findings, common_contract_digest
        )

    # Explicit aliases keep the API aligned with the design terminology.
    validate_adapted_workflow = validate_workflow
    assess_workflow = validate_workflow

    def validate_process(
        self,
        process: object,
        passing_workflows: object = (),
        *,
        known_agent_ids: Iterable[str] | Mapping[object, object] | None = None,
        video_root: Path | str | None = None,
    ) -> AssetValidationReport:
        """Validate one process record using only passing local workflows."""
        process_index = (
            process
            if isinstance(process, Mapping)
            and any(key in process for key in ("processes", "entries"))
            else (process,)
        )
        return self.validate_process_coverage(
            process_index,
            passing_workflows,
            known_agent_ids=known_agent_ids,
            video_root=video_root,
        )

    def validate_knowledge_seed(
        self,
        seed: object,
        *,
        video_root: Path | str | None = None,
        local_consumers: Iterable[str] = (),
    ) -> AssetValidationReport:
        """Validate one inert knowledge seed record."""
        seed_records = (
            seed
            if isinstance(seed, Mapping) and any(key in seed for key in ("seeds", "entries"))
            else (seed,)
        )
        return self.validate_knowledge_seeds(
            seed_records,
            video_root=video_root,
            local_consumers=local_consumers,
        )

    def validate_special_skill(
        self,
        skill: object,
        *,
        video_root: Path | str | None = None,
        local_consumers: Iterable[str] = (),
    ) -> AssetValidationReport:
        """Validate one special-skill review without registering it."""
        skill_records = (
            skill
            if isinstance(skill, Mapping) and any(key in skill for key in ("skills", "entries"))
            else (skill,)
        )
        return self.validate_special_skills(
            skill_records,
            video_root=video_root,
            local_consumers=local_consumers,
        )

    def _workflow_assessment(
        self,
        workflow_path: str,
        workflow: object,
        findings: Sequence[ImportFinding],
        contract_digest: str | None,
    ) -> AdaptedWorkflowAssessment:
        result = ReviewResult.PASS.value if not findings else ReviewResult.FAIL.value
        return AdaptedWorkflowAssessment(
            workflow_path=workflow_path,
            workflow_digest=_candidate_digest(workflow),
            common_contract_digest=_contract_digest(
                contract_digest if contract_digest is not None else self.common_contract_digest
            ),
            result=result,
            findings=_sorted_findings(findings),
        )

    @staticmethod
    def _workflow_agent_values(
        definition: Mapping[object, object],
    ) -> tuple[tuple[str, object], ...]:
        values: list[tuple[str, object]] = []
        for key in ("agent_ids", "common_agent_ids"):
            if key in definition:
                values.append((key, definition[key]))
        raw_nodes = definition.get("nodes", definition.get("steps"))
        nodes = _sequence(raw_nodes)
        if nodes is not None:
            for index, raw_node in enumerate(nodes):
                node = _mapping(raw_node)
                if node is None:
                    values.append((f"nodes[{index}]", None))
                    continue
                values.append(
                    (
                        f"nodes[{index}].agent_id",
                        node.get("agent_id", node.get("common_agent_id")),
                    )
                )
        raw_agents = definition.get("agents")
        agents = _sequence(raw_agents)
        if agents is not None:
            for index, raw_agent in enumerate(agents):
                agent = _mapping(raw_agent)
                values.append(
                    (
                        f"agents[{index}]",
                        agent.get("agent_id", agent.get("common_agent_id"))
                        if agent is not None
                        else raw_agent,
                    )
                )
        return tuple(values)

    @classmethod
    def _validate_workflow_agents(
        cls,
        definition: Mapping[object, object],
        known_ids: frozenset[str],
        path: str,
        findings: list[ImportFinding],
    ) -> None:
        values = cls._workflow_agent_values(definition)
        if not values:
            findings.append(
                _issue(
                    "missing_workflow_agents",
                    field="agents",
                    path=path,
                    message="An adapted workflow must declare Common Agent ID references.",
                )
            )
            return
        for field, raw_value in values:
            candidates: tuple[str, ...]
            if field.endswith("agent_id") or field.startswith("agents["):
                candidate = _text(raw_value)
                candidates = (candidate,) if candidate is not None else ()
            else:
                candidate_values = _text_values(raw_value)
                candidates = candidate_values or ()
                if candidate_values is None:
                    findings.append(
                        _issue(
                            "invalid_workflow_agents",
                            field=field,
                            path=path,
                            message="Workflow Common Agent IDs must be a list of strings.",
                        )
                    )
                    continue
            if not candidates:
                findings.append(
                    _issue(
                        "missing_workflow_agent",
                        field=field,
                        path=path,
                        message="Every workflow node must identify a Common Agent ID.",
                    )
                )
            for agent_id in candidates:
                if not agent_id.startswith("video.") or agent_id not in known_ids:
                    findings.append(
                        _issue(
                            "unknown_common_agent_id",
                            field=field,
                            path=path,
                            message=(
                                "Workflow references must use known authoritative Common Agent IDs."
                            ),
                        )
                    )

    @classmethod
    def _budget_values(
        cls, definition: Mapping[object, object]
    ) -> dict[str, tuple[object, str | None]]:
        containers: list[Mapping[object, object]] = []
        for key in ("execution_budget", "budgets", "budget"):
            candidate = definition.get(key)
            if candidate is not None:
                mapped = _mapping(candidate)
                if mapped is not None:
                    containers.append(mapped)
        containers.append(definition)
        aliases: dict[str, tuple[str, ...]] = {
            "max_node_visits": ("max_node_visits", "max_nodes", "node_budget", "nodes"),
            "max_handoffs": ("max_handoffs", "max_handoff_count", "handoff_budget", "handoffs"),
            "max_wall_clock_seconds": (
                "max_wall_clock_seconds",
                "max_time_seconds",
                "max_time",
                "time_budget",
            ),
            "max_tool_requests": (
                "max_tool_requests",
                "max_tool_calls",
                "max_tools",
                "tool_budget",
            ),
        }
        result: dict[str, tuple[object, str | None]] = {}
        for canonical, names in aliases.items():
            found = False
            value: object = None
            field: str | None = None
            for container in containers:
                for name in names:
                    if name in container:
                        value = container[name]
                        field = name
                        found = True
                        break
                if found:
                    break
            result[canonical] = (value, field)
        return result

    @classmethod
    def _validate_workflow_budgets(
        cls, definition: Mapping[object, object], path: str, findings: list[ImportFinding]
    ) -> None:
        limits = {
            "max_node_visits": (1, MAX_NODES),
            "max_handoffs": (0, MAX_HANDOFFS),
            "max_wall_clock_seconds": (1, MAX_WALL_CLOCK_SECONDS),
            "max_tool_requests": (0, MAX_TOOL_REQUESTS),
        }
        values = cls._budget_values(definition)
        for name, (minimum, maximum) in limits.items():
            value, supplied_field = values[name]
            field = f"execution_budget.{name}"
            if supplied_field is None:
                findings.append(
                    _issue(
                        "missing_workflow_budget",
                        field=field,
                        path=path,
                        message="Workflow node, handoff, time, and tool budgets are required.",
                    )
                )
                continue
            if (
                isinstance(value, bool)
                or not isinstance(value, int)
                or not minimum <= value <= maximum
            ):
                findings.append(
                    _issue(
                        "invalid_workflow_budget",
                        field=field,
                        path=path,
                        message=(
                            f"Workflow budget must be finite and between {minimum} and {maximum}."
                        ),
                    )
                )

        node_count = _sequence(definition.get("nodes", definition.get("steps")))
        if node_count is not None:
            node_limit = values["max_node_visits"][0]
            if (
                isinstance(node_limit, int)
                and not isinstance(node_limit, bool)
                and len(node_count) > node_limit
            ):
                findings.append(
                    _issue(
                        "workflow_node_budget_exceeded",
                        field="nodes",
                        path=path,
                        message="Workflow nodes exceed the declared finite node budget.",
                    )
                )
        handoffs = _sequence(definition.get("edges", definition.get("handoffs")))
        if handoffs is not None:
            handoff_limit = values["max_handoffs"][0]
            if (
                isinstance(handoff_limit, int)
                and not isinstance(handoff_limit, bool)
                and len(handoffs) > handoff_limit
            ):
                findings.append(
                    _issue(
                        "workflow_handoff_budget_exceeded",
                        field="handoffs",
                        path=path,
                        message="Workflow handoffs exceed the declared finite handoff budget.",
                    )
                )

    def _validate_workflow_tools(
        self,
        definition: Mapping[object, object],
        path: str,
        findings: list[ImportFinding],
        allowed_tools: Iterable[str] | None,
    ) -> None:
        used: list[tuple[str, str]] = []
        for key in ("tool_ids", "tools", "requested_tools"):
            if key in definition:
                values = _text_values(definition[key])
                if values is None:
                    findings.append(
                        _issue(
                            "invalid_workflow_tools",
                            field=key,
                            path=path,
                            message="Workflow tools must be an array of strings.",
                        )
                    )
                else:
                    used.extend((f"{key}[{index}]", value) for index, value in enumerate(values))
        for container_key in ("nodes", "steps"):
            nodes = _sequence(definition.get(container_key))
            if nodes is None:
                continue
            for index, raw_node in enumerate(nodes):
                node = _mapping(raw_node)
                if node is None:
                    continue
                for key in ("tool_ids", "tools", "requested_tools", "allowed_tools"):
                    if key not in node:
                        continue
                    values = _text_values(node[key])
                    field = f"{container_key}[{index}].{key}"
                    if values is None:
                        findings.append(
                            _issue(
                                "invalid_workflow_tools",
                                field=field,
                                path=path,
                                message="Workflow tools must be an array of strings.",
                            )
                        )
                    else:
                        used.extend(
                            (f"{field}[{item_index}]", value)
                            for item_index, value in enumerate(values)
                        )
        configured = (
            frozenset(
                tool.strip() for tool in allowed_tools if isinstance(tool, str) and tool.strip()
            )
            if allowed_tools is not None
            else self.allowed_tools
        )
        if configured is None:
            declared = definition.get("allowed_tools", definition.get("tool_allowlist"))
            declared_values = _text_values(declared) if declared is not None else ()
            configured = frozenset(declared_values or ())
        for field, tool in used:
            if tool not in configured:
                findings.append(
                    _issue(
                        "disallowed_workflow_tool",
                        field=field,
                        path=path,
                        message="Workflow tools must be present in the host allow-list.",
                    )
                )
        tool_limit = self._budget_values(definition)["max_tool_requests"][0]
        if (
            isinstance(tool_limit, int)
            and not isinstance(tool_limit, bool)
            and len(used) > tool_limit
        ):
            findings.append(
                _issue(
                    "workflow_tool_budget_exceeded",
                    field="tools",
                    path=path,
                    message="Workflow tool requests exceed the declared finite tool budget.",
                )
            )

    @classmethod
    def _validate_required_controls(
        cls, definition: Mapping[object, object], path: str, findings: list[ImportFinding]
    ) -> None:
        cls._require_control(
            definition,
            ("risk_gate_ids", "risk_gates", "risk_gate"),
            "missing_workflow_risk_gate",
            "invalid_workflow_risk_gate",
            "risk gates",
            path,
            findings,
        )
        cls._require_control(
            definition,
            ("compensation", "compensation_behavior", "rollback", "on_failure"),
            "missing_workflow_compensation",
            "invalid_workflow_compensation",
            "compensation behavior",
            path,
            findings,
        )
        cls._require_control(
            definition,
            ("critique_loops", "critique_loop", "critique", "critique_edges"),
            "missing_workflow_critique_loop",
            "invalid_workflow_critique_loop",
            "critique loops",
            path,
            findings,
            bounded=True,
        )
        cls._require_control(
            definition,
            ("human_interrupts", "human_interrupt", "interrupts", "human_gates"),
            "missing_workflow_human_interrupt",
            "invalid_workflow_human_interrupt",
            "human interrupts",
            path,
            findings,
        )

    @classmethod
    def _require_control(
        cls,
        definition: Mapping[object, object],
        keys: tuple[str, ...],
        missing_code: str,
        invalid_code: str,
        label: str,
        path: str,
        findings: list[ImportFinding],
        *,
        bounded: bool = False,
    ) -> None:
        key, value = _first(definition, *keys)
        if key is None:
            findings.append(
                _issue(
                    missing_code,
                    field=keys[0],
                    path=path,
                    message=f"Adapted workflows must declare {label}.",
                )
            )
            return
        valid = _control_present(value)
        if valid and bounded:
            valid = cls._critique_is_bounded(value)
        if not valid:
            findings.append(
                _issue(
                    invalid_code,
                    field=key,
                    path=path,
                    message=f"Adapted workflow {label} must be present and bounded.",
                )
            )

    @staticmethod
    def _critique_is_bounded(value: object) -> bool:
        if isinstance(value, Mapping):
            enabled = value.get("enabled", value.get("required", True))
            if enabled is False:
                return False
            raw_limit = value.get("max_iterations", value.get("max_rounds", value.get("limit")))
            if raw_limit is None:
                return True
            return (
                isinstance(raw_limit, int)
                and not isinstance(raw_limit, bool)
                and 1 <= raw_limit <= MAX_CRITIQUE_ITERATIONS
            )
        values = _sequence(value)
        if values is not None:
            for item in values:
                item_mapping = _mapping(item)
                if item_mapping is None:
                    continue
                raw_limit = item_mapping.get("max_iterations", item_mapping.get("max_rounds"))
                if raw_limit is not None and (
                    not isinstance(raw_limit, int)
                    or isinstance(raw_limit, bool)
                    or not 1 <= raw_limit <= MAX_CRITIQUE_ITERATIONS
                ):
                    return False
        return True

    @staticmethod
    def _validate_common_contract(
        definition: Mapping[object, object],
        path: str,
        findings: list[ImportFinding],
        expected_digest: str | None,
    ) -> None:
        expected = expected_digest
        if expected is None:
            return
        actual = definition.get("common_contract_digest")
        if not isinstance(actual, str) or actual.casefold() != _contract_digest(expected):
            findings.append(
                _issue(
                    "common_contract_mismatch",
                    field="common_contract_digest",
                    path=path,
                    message="Workflow must name the exact reviewed Common Pack Contract digest.",
                )
            )

    def validate_process_coverage(
        self,
        process_index: object,
        workflows: object = (),
        *,
        known_agent_ids: Iterable[str] | Mapping[object, object] | None = None,
        video_root: Path | str | None = None,
    ) -> AssetValidationReport:
        """Validate process references only against passing local workflows and IDs."""
        findings: list[ImportFinding] = []
        ids = _known_ids(known_agent_ids) if known_agent_ids is not None else self.known_agent_ids
        passing = self._passing_workflows(workflows, ids, findings)
        raw_processes: object = process_index
        if isinstance(process_index, Mapping):
            raw_processes = process_index.get("processes", process_index.get("entries", ()))
        processes = _sequence(raw_processes)
        if processes is None:
            findings.append(
                _issue(
                    "invalid_process_index",
                    field="processes",
                    message="The local process index must be an array of process records.",
                )
            )
            return AssetValidationReport(MigrationResult.FAIL, _sorted_findings(findings))
        accepted: list[str] = []
        for index, raw_process in enumerate(processes):
            field = f"processes[{index}]"
            process = _mapping(raw_process)
            if process is None:
                findings.append(
                    _issue(
                        "invalid_process", field=field, message="Process records must be objects."
                    )
                )
                continue
            workflow_value = process.get(
                "workflow_path",
                process.get(
                    "workflow", process.get("workflow_ref", process.get("adapted_workflow"))
                ),
            )
            if isinstance(workflow_value, Mapping):
                workflow_value = workflow_value.get("workflow_path", workflow_value.get("path"))
            normalized, path_error = _workflow_path(workflow_value, fallback="")
            if path_error is not None or not normalized:
                findings.append(
                    _issue(
                        "invalid_process_workflow_reference",
                        field=f"{field}.workflow_path",
                        message="Process workflows must be safe local relative paths.",
                    )
                )
            elif normalized not in passing:
                findings.append(
                    _issue(
                        "process_workflow_not_passing",
                        field=f"{field}.workflow_path",
                        path=normalized,
                        message="Processes may reference only passing local adapted workflows.",
                    )
                )
            if video_root is not None and normalized:
                self._check_local_file(video_root, normalized, f"{field}.workflow_path", findings)
            agent_values = process.get(
                "agent_ids", process.get("common_agent_ids", process.get("agents"))
            )
            agent_ids = _text_values(agent_values)
            if agent_ids is None or not agent_ids:
                findings.append(
                    _issue(
                        "missing_process_agent_ids",
                        field=f"{field}.agent_ids",
                        message="Process coverage requires Common Agent IDs.",
                    )
                )
            else:
                for agent_id in agent_ids:
                    if not agent_id.startswith("video.") or agent_id not in ids:
                        findings.append(
                            _issue(
                                "unknown_process_agent_id",
                                field=f"{field}.agent_ids",
                                message="Process coverage must use known Common Agent IDs.",
                            )
                        )
            if not any(finding.field.startswith(field) for finding in findings):
                accepted.append(normalized)
        return AssetValidationReport(
            MigrationResult.PASS if not findings else MigrationResult.FAIL,
            _sorted_findings(findings),
            tuple(accepted),
        )

    def validate_knowledge_seeds(
        self,
        seeds: object,
        *,
        video_root: Path | str | None = None,
        local_consumers: Iterable[str] = (),
    ) -> AssetValidationReport:
        """Require local provenance and a local consumer for every knowledge seed."""
        findings: list[ImportFinding] = []
        raw_seeds: object = seeds
        if isinstance(seeds, Mapping):
            raw_seeds = seeds.get("seeds", seeds.get("entries", ()))
        seed_values = _sequence(raw_seeds)
        if seed_values is None:
            findings.append(
                _issue(
                    "invalid_knowledge_seeds",
                    field="seeds",
                    message="Knowledge seeds must be an array.",
                )
            )
            return AssetValidationReport(MigrationResult.FAIL, _sorted_findings(findings))
        consumers = frozenset(item for item in local_consumers if isinstance(item, str))
        accepted: list[str] = []
        seen: set[str] = set()
        for index, raw_seed in enumerate(seed_values):
            field = f"seeds[{index}]"
            seed = _asset_mapping(raw_seed)
            if seed is None:
                findings.append(
                    _issue(
                        "invalid_knowledge_seed",
                        field=field,
                        message="Knowledge seed records must be objects.",
                    )
                )
                continue
            seed_path = _text(seed.get("seed_path", seed.get("path")))
            normalized_seed, path_error = _workflow_path(seed_path, fallback="")
            if path_error is not None or not normalized_seed:
                findings.append(
                    _issue(
                        "unsafe_knowledge_seed_path",
                        field=f"{field}.seed_path",
                        message="Knowledge seed paths must be local relative paths.",
                    )
                )
            elif normalized_seed in seen:
                findings.append(
                    _issue(
                        "duplicate_knowledge_seed",
                        field=f"{field}.seed_path",
                        path=normalized_seed,
                        message="Knowledge seed paths must be unique.",
                    )
                )
            else:
                seen.add(normalized_seed)
            provenance = seed.get("provenance")
            if not self._valid_provenance(provenance):
                findings.append(
                    _issue(
                        "missing_local_knowledge_provenance",
                        field=f"{field}.provenance",
                        message="Knowledge seeds require a local Historical Provenance record.",
                    )
                )
            consumer = _text(seed.get("consumer_ref", seed.get("consumer")))
            if consumer is None:
                findings.append(
                    _issue(
                        "missing_knowledge_consumer",
                        field=f"{field}.consumer_ref",
                        message="Every knowledge seed requires a local consumer reference.",
                    )
                )
            elif not self._valid_local_reference(consumer, video_root, consumers):
                findings.append(
                    _issue(
                        "invalid_knowledge_consumer",
                        field=f"{field}.consumer_ref",
                        message="Knowledge seed consumers must resolve to local Video Pack assets.",
                    )
                )
            review_status = seed.get("review_status", seed.get("result", "pass"))
            if review_status != ReviewResult.PASS.value:
                findings.append(
                    _issue(
                        "knowledge_seed_review_failed",
                        field=f"{field}.review_status",
                        message="Knowledge seed review status must pass.",
                    )
                )
            if video_root is not None and normalized_seed:
                self._check_local_file(video_root, normalized_seed, f"{field}.seed_path", findings)
            if not any(finding.field.startswith(field) for finding in findings):
                accepted.append(normalized_seed)
        return AssetValidationReport(
            MigrationResult.PASS if not findings else MigrationResult.FAIL,
            _sorted_findings(findings),
            tuple(accepted),
        )

    def validate_special_skills(
        self,
        skills: object,
        *,
        video_root: Path | str | None = None,
        local_consumers: Iterable[str] = (),
    ) -> AssetValidationReport:
        """Keep special skills absent unless every review dimension passes."""
        findings: list[ImportFinding] = []
        raw_skills: object = skills
        if isinstance(skills, Mapping):
            raw_skills = skills.get("skills", skills.get("entries", ()))
        skill_values = _sequence(raw_skills)
        if skill_values is None:
            findings.append(
                _issue(
                    "invalid_special_skills",
                    field="skills",
                    message="Special-skill proposals must be an array.",
                )
            )
            return AssetValidationReport(MigrationResult.FAIL, _sorted_findings(findings))
        consumers = frozenset(item for item in local_consumers if isinstance(item, str))
        accepted: list[str] = []
        for index, raw_skill in enumerate(skill_values):
            field = f"skills[{index}]"
            skill = _asset_mapping(raw_skill)
            if skill is None:
                findings.append(
                    _issue(
                        "invalid_special_skill",
                        field=field,
                        message="Special-skill reviews must be objects.",
                    )
                )
                continue
            skill_id = _text(skill.get("skill_id", skill.get("id")))
            if skill_id is None:
                findings.append(
                    _issue(
                        "missing_special_skill_id",
                        field=f"{field}.skill_id",
                        message="Special skills require a stable identifier.",
                    )
                )
                skill_id = f"{field}"
            review = _mapping(skill.get("review")) or skill
            for review_field in ("compatibility", "security", "overlap", "license"):
                if review.get(review_field) is not True:
                    findings.append(
                        _issue(
                            "special_skill_review_incomplete",
                            field=f"{field}.{review_field}",
                            message=(
                                "Compatibility, security, overlap, and license reviews "
                                "must all pass."
                            ),
                        )
                    )
            reviewer = _text(review.get("reviewer", review.get("reviewed_by")))
            if reviewer is None or reviewer.casefold() in _REVIEW_PLACEHOLDERS:
                findings.append(
                    _issue(
                        "special_skill_reviewer_missing",
                        field=f"{field}.reviewer",
                        message=(
                            "Special-skill inclusion requires a completed human reviewer record."
                        ),
                    )
                )
            reviewed_at = review.get("reviewed_at", review.get("timestamp"))
            if not _valid_timestamp(reviewed_at):
                findings.append(
                    _issue(
                        "special_skill_timestamp_missing",
                        field=f"{field}.reviewed_at",
                        message=(
                            "Special-skill inclusion requires a timezone-aware review timestamp."
                        ),
                    )
                )
            consumer = _text(review.get("consumer_ref", review.get("consumer")))
            if consumer is None or not self._valid_local_reference(
                consumer or "", video_root, consumers
            ):
                findings.append(
                    _issue(
                        "special_skill_consumer_missing",
                        field=f"{field}.consumer_ref",
                        message="Special skills require an identified local consumer.",
                    )
                )
            result = review.get("result", review.get("review_status", ReviewResult.PASS.value))
            if result != ReviewResult.PASS.value:
                findings.append(
                    _issue(
                        "special_skill_review_failed",
                        field=f"{field}.result",
                        message="Special-skill review result must pass.",
                    )
                )
            included = skill.get("included", skill.get("registered", skill.get("present", False)))
            if included is True:
                findings.append(
                    _issue(
                        "special_skill_must_remain_absent",
                        field=field,
                        message=(
                            "An unapproved special skill must remain absent from the Video Pack."
                        ),
                    )
                )
            if not any(finding.field.startswith(field) for finding in findings):
                accepted.append(skill_id)
        return AssetValidationReport(
            MigrationResult.PASS if not findings else MigrationResult.FAIL,
            _sorted_findings(findings),
            tuple(accepted),
        )

    def validate(
        self,
        workflows: object = (),
        process_index: object | None = None,
        knowledge_seeds: object = (),
        special_skills: object = (),
        *,
        video_root: Path | str | None = None,
    ) -> OperationalAssetReport:
        """Aggregate operational checks without registering or executing assets."""
        findings: list[ImportFinding] = []
        assessments: list[AdaptedWorkflowAssessment] = []
        for path, workflow in self._workflow_items(workflows):
            assessment = self.validate_workflow(workflow, workflow_path=path)
            assessments.append(assessment)
            findings.extend(assessment.findings)
        passing = {
            assessment.workflow_path: assessment
            for assessment in assessments
            if assessment.result == ReviewResult.PASS.value
        }
        process_report: AssetValidationReport | None = None
        if process_index is not None:
            process_report = self.validate_process_coverage(
                process_index, passing, video_root=video_root
            )
            findings.extend(process_report.findings)
        knowledge_report = self.validate_knowledge_seeds(knowledge_seeds, video_root=video_root)
        findings.extend(knowledge_report.findings)
        special_skill_report = self.validate_special_skills(special_skills, video_root=video_root)
        findings.extend(special_skill_report.findings)
        return OperationalAssetReport(
            MigrationResult.PASS if not findings else MigrationResult.FAIL,
            _sorted_findings(findings),
            tuple(assessments),
            process_report,
            knowledge_report,
            special_skill_report,
            tuple(passing),
        )

    validate_operational_assets = validate
    validate_assets = validate

    def register_adapted_workflow(
        self,
        video_root: Path | str,
        workflow: object,
        *,
        workflow_path: str | None = None,
        allowed_tools: Iterable[str] | None = None,
    ) -> OperationalAssetReport:
        """Publish one passing workflow as inert JSON without touching ``pack_spine``."""
        definition = _mapping(workflow)
        workflow_id = _text(definition.get("id")) if definition is not None else None
        requested_path = workflow_path or (
            f"{DEFAULT_WORKFLOW_DIRECTORY}/{workflow_id}.dna.json"
            if workflow_id is not None
            else "workflows/adapted-workflow.dna.json"
        )
        assessment = self.validate_workflow(
            workflow,
            workflow_path=requested_path,
            allowed_tools=allowed_tools,
        )
        if assessment.result != ReviewResult.PASS.value:
            return OperationalAssetReport(
                MigrationResult.BLOCKED, assessment.findings, (assessment,)
            )
        definition = _mapping(workflow)
        if definition is None:
            return OperationalAssetReport(
                MigrationResult.BLOCKED, assessment.findings, (assessment,)
            )
        try:
            normalized = normalize_relative_path(requested_path)
            if normalized == PACK_SPINE_PATH or not normalized.startswith(
                f"{DEFAULT_WORKFLOW_DIRECTORY}/"
            ):
                raise UnsafeLocalPathError("out_of_root", normalized)
            target = resolve_under_root(video_root, normalized)
            target.parent.mkdir(parents=True, exist_ok=True)
            payload = f"{canonicalize_json(definition)}\n"
            if target.exists() and target.read_text(encoding="utf-8") == payload:
                result = MigrationResult.NO_CHANGE
            else:
                target.write_text(payload, encoding="utf-8")
                result = MigrationResult.PASS
            # No code path writes or replaces the safe baseline.
            return OperationalAssetReport(
                result, (), (assessment,), accepted_workflow_paths=(normalized,)
            )
        except (OSError, UnicodeError, TypeError, ValueError, UnsafeLocalPathError):
            finding = _issue(
                "workflow_registration_blocked",
                field="workflow_path",
                path=requested_path,
                message=(
                    "Only passing workflows may be registered beneath the local "
                    "workflows directory."
                ),
            )
            return OperationalAssetReport(MigrationResult.BLOCKED, (finding,), (assessment,))

    register_workflow = register_adapted_workflow

    def _workflow_items(self, workflows: object) -> tuple[tuple[str, object], ...]:
        if isinstance(workflows, Mapping):
            if any(key in workflows for key in ("nodes", "steps", "agent_ids", "common_agent_ids")):
                return ((str(workflows.get("workflow_path", "workflow.json")), workflows),)
            items: list[tuple[str, object]] = []
            for key, value in workflows.items():
                if isinstance(key, str):
                    items.append((key, value))
            return tuple(items)
        values = _sequence(workflows)
        if values is None:
            return ()
        items = []
        for index, workflow in enumerate(values):
            definition = _mapping(workflow)
            path = (
                _text(definition.get("workflow_path", definition.get("path")))
                if definition
                else None
            )
            items.append((path or f"workflow-{index}.json", workflow))
        return tuple(items)

    def _passing_workflows(
        self,
        workflows: object,
        ids: frozenset[str],
        findings: list[ImportFinding],
    ) -> frozenset[str]:
        passing: set[str] = set()
        if isinstance(workflows, Mapping):
            items = tuple(workflows.items())
        else:
            values = _sequence(workflows) or ()
            items = tuple((None, item) for item in values)
        for key, raw in items:
            if isinstance(raw, AdaptedWorkflowAssessment):
                if raw.result == ReviewResult.PASS.value:
                    passing.add(raw.workflow_path)
                continue
            definition = _mapping(raw)
            path = _text(key) if isinstance(key, str) else None
            if definition is not None:
                path = path or _text(definition.get("workflow_path", definition.get("path")))
            normalized, error = _workflow_path(path, fallback="")
            if error is not None or not normalized:
                findings.append(
                    _issue(
                        "invalid_local_workflow_reference",
                        field="workflow_path",
                        message="Process coverage accepts local workflow paths only.",
                    )
                )
                continue
            assessment = self.validate_workflow(
                definition if definition is not None else raw,
                workflow_path=normalized,
                known_agent_ids=ids,
            )
            if assessment.result == ReviewResult.PASS.value:
                passing.add(normalized)
        return frozenset(passing)

    @staticmethod
    def _valid_provenance(value: object) -> bool:
        if isinstance(value, HistoricalProvenance):
            return bool(value.repository and value.commit and value.path and value.license_status)
        mapped = _mapping(value)
        if mapped is None:
            return False
        return all(
            _text(mapped.get(field)) for field in ("repository", "commit", "path", "license_status")
        ) and not _external_reference(_text(mapped.get("path")) or "")

    @staticmethod
    def _valid_local_reference(
        value: str,
        video_root: Path | str | None,
        known_consumers: frozenset[str],
    ) -> bool:
        if _external_reference(value):
            return False
        try:
            normalized = normalize_relative_path(value)
        except UnsafeLocalPathError:
            return False
        if normalized in known_consumers:
            return True
        if video_root is None:
            return True
        try:
            resolved = resolve_under_root(
                video_root, normalized, must_exist=True, require_readable=True
            )
        except (OSError, RuntimeError, UnsafeLocalPathError):
            return False
        return resolved.is_file()

    @staticmethod
    def _check_local_file(
        root: Path | str,
        relative: str,
        field: str,
        findings: list[ImportFinding],
    ) -> None:
        try:
            resolved = resolve_under_root(root, relative, must_exist=True, require_readable=True)
            if not resolved.is_file():
                raise UnsafeLocalPathError("not_a_file", relative)
        except (OSError, RuntimeError, UnsafeLocalPathError):
            findings.append(
                _issue(
                    "missing_local_asset",
                    field=field,
                    path=relative,
                    message=(
                        "Required operational asset references must resolve to local "
                        "readable files."
                    ),
                )
            )


def _control_present(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, Mapping):
        if not value:
            return False
        for key in ("enabled", "required", "active", "present"):
            if key in value and value[key] is False:
                return False
        return True
    values = _sequence(value)
    return values is not None and bool(values)


def _valid_timestamp(value: object) -> bool:
    if isinstance(value, datetime):
        return value.tzinfo is not None
    if not isinstance(value, str) or not value.strip():
        return False
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None


def _external_reference(value: str) -> bool:
    return "://" in value or bool(re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", value))


def validate_adapted_workflow(
    workflow: object,
    known_agent_ids: Iterable[str] | Mapping[object, object],
    allowed_tools: Iterable[str] = (),
    *,
    workflow_path: str = "workflow.json",
    common_contract_digest: str | None = None,
) -> AdaptedWorkflowAssessment:
    """Functional seam for callers that do not need to retain a validator instance."""
    return OperationalAssetValidator(
        known_agent_ids, allowed_tools, common_contract_digest=common_contract_digest
    ).validate_workflow(workflow, workflow_path=workflow_path)


def validate_process_coverage(
    process_index: object,
    workflows: object,
    known_agent_ids: Iterable[str] | Mapping[object, object],
    *,
    video_root: Path | str | None = None,
) -> AssetValidationReport:
    """Functional process-coverage validation seam."""
    return OperationalAssetValidator(known_agent_ids).validate_process_coverage(
        process_index, workflows, video_root=video_root
    )


def validate_knowledge_seeds(
    seeds: object,
    *,
    video_root: Path | str | None = None,
    local_consumers: Iterable[str] = (),
) -> AssetValidationReport:
    """Functional knowledge-seed validation seam."""
    return OperationalAssetValidator().validate_knowledge_seeds(
        seeds, video_root=video_root, local_consumers=local_consumers
    )


def validate_special_skills(
    skills: object,
    *,
    video_root: Path | str | None = None,
    local_consumers: Iterable[str] = (),
) -> AssetValidationReport:
    """Functional special-skill validation seam."""
    return OperationalAssetValidator().validate_special_skills(
        skills, video_root=video_root, local_consumers=local_consumers
    )


def validate_operational_assets(
    workflows: object = (),
    known_agent_ids: Iterable[str] | Mapping[object, object] | None = None,
    allowed_tools: Iterable[str] | None = None,
    *,
    process_index: object | None = None,
    knowledge_seeds: object = (),
    special_skills: object = (),
    video_root: Path | str | None = None,
    common_contract_digest: str | None = None,
) -> OperationalAssetReport:
    """Functional aggregate seam for local operational-asset validation."""
    validator = OperationalAssetValidator(
        known_agent_ids,
        allowed_tools,
        common_contract_digest=common_contract_digest,
    )
    return validator.validate(
        workflows,
        process_index,
        knowledge_seeds,
        special_skills,
        video_root=video_root,
    )


validate_assets = validate_operational_assets


def register_adapted_workflow(
    video_root: Path | str,
    workflow: object,
    known_agent_ids: Iterable[str] | Mapping[object, object],
    allowed_tools: Iterable[str] = (),
    *,
    workflow_path: str | None = None,
    common_contract_digest: str | None = None,
) -> OperationalAssetReport:
    """Functional seam for safe, inert workflow registration."""
    validator = OperationalAssetValidator(
        known_agent_ids, allowed_tools, common_contract_digest=common_contract_digest
    )
    return validator.register_adapted_workflow(video_root, workflow, workflow_path=workflow_path)


# Compatibility names used by callers that prefer a shorter validator name.
OperationalAssetsValidator = OperationalAssetValidator
OperationalValidationReport = OperationalAssetReport

__all__ = [
    "PACK_SPINE_PATH",
    "AssetValidationReport",
    "KnowledgeSeedValidationReport",
    "OperationalAssetIssue",
    "OperationalAssetReport",
    "OperationalAssetValidator",
    "OperationalAssetsValidator",
    "OperationalValidationReport",
    "ProcessCoverageReport",
    "SpecialSkillValidationReport",
    "register_adapted_workflow",
    "validate_adapted_workflow",
    "validate_assets",
    "validate_knowledge_seeds",
    "validate_operational_assets",
    "validate_process_coverage",
    "validate_special_skills",
]
