"""Exact, configuration-only inventory validation for the Video_Pack."""

from __future__ import annotations

import json
import re
import unicodedata
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Final

EXPECTED_VIDEO_AGENT_COUNT: Final[int] = 114
_IDENTIFIER_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$"
)
_ALLOWED_STATUSES: Final[frozenset[str]] = frozenset({"draft", "registered"})


@dataclass(frozen=True, slots=True)
class InventoryIssue:
    """A deterministic, redaction-safe reason the Video_Pack inventory is invalid."""

    code: str
    message: str
    field: str


@dataclass(frozen=True, slots=True)
class VideoAgentEntry:
    """One normalized, non-active manifest or inventory entry."""

    agent_id: str
    status: str | None
    agent_spec_path: str | None
    allowed_tools: tuple[str, ...] | None


@dataclass(frozen=True, slots=True)
class VideoInventoryReport:
    """The complete result of validating Video_Pack configuration records."""

    is_valid: bool
    manifest_agent_ids: tuple[str, ...]
    inventory_agent_ids: tuple[str, ...]
    agent_spec_ids: tuple[str, ...]
    issues: tuple[InventoryIssue, ...] = ()


class VideoInventoryValidator:
    """Validate data-only Video_Pack configuration without registration or activation."""

    def validate(
        self,
        manifest: object,
        inventory: object,
        agent_specs: Mapping[str, object] | None = None,
    ) -> VideoInventoryReport:
        """Accept only the exact non-active manifest, inventory, and supplied records."""
        issues: list[InventoryIssue] = []
        manifest_mapping = self._mapping(manifest, "manifest", issues)
        inventory_mapping = self._mapping(inventory, "inventory", issues)
        self._validate_pack_metadata(manifest_mapping, inventory_mapping, issues)
        manifest_agents = self._extract_agent_entries(
            manifest_mapping.get("agents"), "agents", issues, is_manifest=True
        )
        inventory_agents = self._extract_agent_entries(
            inventory_mapping.get("entries"), "entries", issues, is_manifest=False
        )
        manifest_ids = [entry.agent_id for entry in manifest_agents]
        inventory_ids = [entry.agent_id for entry in inventory_agents]
        self._validate_exact_count(manifest_ids, "agents", issues)
        self._validate_exact_count(inventory_ids, "entries", issues)
        self._validate_bijection(manifest_ids, inventory_ids, issues)
        self._validate_entry_alignment(manifest_agents, inventory_agents, issues)
        agent_spec_ids: tuple[str, ...] = ()
        if agent_specs is not None:
            agent_spec_ids = self._validate_agent_specs(
                manifest_agents, agent_specs, issues
            )
        return VideoInventoryReport(
            is_valid=not issues,
            manifest_agent_ids=tuple(manifest_ids),
            inventory_agent_ids=tuple(inventory_ids),
            agent_spec_ids=agent_spec_ids,
            issues=tuple(issues),
        )

    def validate_directory(self, video_root: Path | str) -> VideoInventoryReport:
        """Load target-local configuration and every materialized agent specification."""
        root = Path(video_root).resolve()
        try:
            manifest = self._load_json(root / "manifest.json")
            inventory = self._load_json(root / "inventory.json")
            agent_specs, load_issues = self._load_agent_specs(root)
        except (OSError, UnicodeError, json.JSONDecodeError):
            issue = InventoryIssue(
                code="unreadable_configuration",
                message="Video inventory configuration must be readable valid JSON.",
                field="configuration",
            )
            return VideoInventoryReport(False, (), (), (), (issue,))

        report = self.validate(manifest, inventory, agent_specs)
        issues = (*load_issues, *report.issues)
        return VideoInventoryReport(
            is_valid=not issues,
            manifest_agent_ids=report.manifest_agent_ids,
            inventory_agent_ids=report.inventory_agent_ids,
            agent_spec_ids=report.agent_spec_ids,
            issues=issues,
        )

    def _load_agent_specs(
        self, root: Path
    ) -> tuple[dict[str, object], tuple[InventoryIssue, ...]]:
        agents_root = (root / "agents").resolve()
        agent_specs: dict[str, object] = {}
        issues: list[InventoryIssue] = []
        for candidate in sorted(agents_root.iterdir(), key=lambda path: path.name):
            if not candidate.is_dir():
                continue
            spec_path = candidate / "agent_spec.json"
            try:
                if not spec_path.resolve().is_relative_to(agents_root):
                    issues.append(
                        InventoryIssue(
                            code="unsafe_agent_spec_path",
                            message="Agent specifications must remain within the Video_Pack.",
                            field=candidate.name,
                        )
                    )
                    continue
                agent_specs[candidate.name] = self._load_json(spec_path)
            except (OSError, UnicodeError, json.JSONDecodeError):
                agent_specs[candidate.name] = None
                issues.append(
                    InventoryIssue(
                        code="unreadable_agent_spec",
                        message="Every Video_Pack agent specification must be readable valid JSON.",
                        field=candidate.name,
                    )
                )
        return agent_specs, tuple(issues)

    @staticmethod
    def _load_json(path: Path) -> object:
        parsed: object = json.loads(path.read_text(encoding="utf-8"))
        return parsed

    @staticmethod
    def _mapping(
        value: object, field: str, issues: list[InventoryIssue]
    ) -> Mapping[object, object]:
        if isinstance(value, Mapping):
            return value
        issues.append(
            InventoryIssue(
                code="invalid_object",
                message="Video inventory configuration must use JSON objects.",
                field=field,
            )
        )
        return {}

    @staticmethod
    def _validate_pack_metadata(
        manifest: Mapping[object, object],
        inventory: Mapping[object, object],
        issues: list[InventoryIssue],
    ) -> None:
        pack_id = manifest.get("pack_id")
        if not isinstance(pack_id, str) or pack_id.strip().casefold() != "video":
            issues.append(
                InventoryIssue(
                    code="invalid_pack_id",
                    message="The exact-inventory validator only accepts the video pack.",
                    field="pack_id",
                )
            )
        if inventory.get("pack_id") != "video":
            issues.append(
                InventoryIssue(
                    code="invalid_inventory_pack_id",
                    message="Video inventory must identify the video pack.",
                    field="inventory.pack_id",
                )
            )
        if manifest.get("production_activation_requested", False) is not False:
            issues.append(
                InventoryIssue(
                    code="production_activation_requested",
                    message="Video inventory configuration cannot request production activation.",
                    field="production_activation_requested",
                )
            )
        validation = manifest.get("validation")
        if not isinstance(validation, Mapping) or validation.get(
            "expected_agent_count"
        ) != EXPECTED_VIDEO_AGENT_COUNT:
            issues.append(
                InventoryIssue(
                    code="invalid_manifest_validation",
                    message="Video manifest must declare the exact 114-agent validation rule.",
                    field="validation.expected_agent_count",
                )
            )

    def _extract_agent_entries(
        self,
        raw_agents: object,
        field: str,
        issues: list[InventoryIssue],
        *,
        is_manifest: bool,
    ) -> list[VideoAgentEntry]:
        if not isinstance(raw_agents, Sequence) or isinstance(
            raw_agents, (str, bytes, bytearray)
        ):
            issues.append(
                InventoryIssue(
                    code="invalid_agent_collection",
                    message="Agents and inventory entries must be JSON arrays.",
                    field=field,
                )
            )
            return []

        agent_entries: list[VideoAgentEntry] = []
        seen_ids: set[str] = set()
        for index, raw_agent in enumerate(raw_agents):
            item_field = f"{field}[{index}]"
            if not isinstance(raw_agent, Mapping):
                issues.append(
                    InventoryIssue(
                        code="invalid_agent_entry",
                        message="Each agent and inventory entry must be a JSON object.",
                        field=item_field,
                    )
                )
                continue
            agent_id = self._canonical_identifier(
                raw_agent.get("agent_id"), item_field, issues
            )
            status = self._validate_status(raw_agent.get("status"), item_field, issues)
            spec_path = self._validate_agent_spec_path(
                raw_agent.get("agent_spec_path"), agent_id, item_field, issues
            )
            allowed_tools: tuple[str, ...] | None = None
            if is_manifest:
                allowed_tools = self._validate_allowed_tools(
                    raw_agent.get("allowed_tools"), item_field, issues
                )
                if raw_agent.get("production_active") is True:
                    issues.append(
                        InventoryIssue(
                            code="production_activation_requested",
                            message="Video agents must remain non-active configuration records.",
                            field=f"{item_field}.production_active",
                        )
                    )
            else:
                if raw_agent.get("maturity_level") != "L0":
                    issues.append(
                        InventoryIssue(
                            code="invalid_maturity_level",
                            message=(
    "Materialized configuration-only agents must be cataloged at L0."
),
                            field=f"{item_field}.maturity_level",
                        )
                    )
            if agent_id is None:
                continue
            if agent_id in seen_ids:
                issues.append(
                    InventoryIssue(
                        code=(
                            "duplicate_manifest_agent"
                            if is_manifest
                            else "duplicate_inventory_entry"
                        ),
                        message="Video agent identifiers must be unique after canonicalization.",
                        field=f"{item_field}.agent_id",
                    )
                )
            seen_ids.add(agent_id)
            agent_entries.append(
                VideoAgentEntry(agent_id, status, spec_path, allowed_tools)
            )
        return agent_entries

    @staticmethod
    def _canonical_identifier(
        value: object, field: str, issues: list[InventoryIssue]
    ) -> str | None:
        if not isinstance(value, str):
            issues.append(
                InventoryIssue(
                    "invalid_agent_identifier", "Agent identifiers must be strings.", field
                )
            )
            return None
        identifier = unicodedata.normalize("NFKC", value).strip().casefold()
        if (
            len(identifier) > 100
            or not _IDENTIFIER_PATTERN.fullmatch(identifier)
            or not identifier.startswith("video.")
        ):
            issues.append(
                InventoryIssue(
                    "invalid_agent_identifier",
                    "Agent identifiers must normalize to video-namespaced lowercase identifiers.",
                    field,
                )
            )
            return None
        return identifier

    @staticmethod
    def _validate_status(
        value: object, field: str, issues: list[InventoryIssue]
    ) -> str | None:
        if not isinstance(value, str) or value not in _ALLOWED_STATUSES:
            issues.append(
                InventoryIssue(
                    code="invalid_lifecycle_status",
                    message="Video agent status must be draft or registered.",
                    field=f"{field}.status",
                )
            )
            return None
        return value

    @staticmethod
    def _validate_agent_spec_path(
        value: object,
        agent_id: str | None,
        field: str,
        issues: list[InventoryIssue],
    ) -> str | None:
        expected_path = (
            f"agents/{agent_id}/agent_spec.json" if agent_id is not None else None
        )
        if not isinstance(value, str) or value != expected_path:
            issues.append(
                InventoryIssue(
                    code="invalid_agent_spec_path",
                    message="Each entry must use its exact target-local agent specification path.",
                    field=f"{field}.agent_spec_path",
                )
            )
            return None
        return value

    @staticmethod
    def _validate_allowed_tools(
        value: object, field: str, issues: list[InventoryIssue]
    ) -> tuple[str, ...] | None:
        if not isinstance(value, list) or any(
            not isinstance(tool, str) or not tool.strip() for tool in value
        ):
            issues.append(
                InventoryIssue(
                    code="invalid_allowed_tools",
                    message="Allowed tools must be an array of nonblank tool identifiers.",
                    field=f"{field}.allowed_tools",
                )
            )
            return None
        tools = tuple(value)
        if len(set(tools)) != len(tools):
            issues.append(
                InventoryIssue(
                    code="duplicate_allowed_tool",
                    message="Allowed tools must be unique.",
                    field=f"{field}.allowed_tools",
                )
            )
        return tools

    @staticmethod
    def _validate_exact_count(
        agent_ids: list[str], field: str, issues: list[InventoryIssue]
    ) -> None:
        if len(agent_ids) != EXPECTED_VIDEO_AGENT_COUNT:
            issues.append(
                InventoryIssue(
                    code="invalid_agent_count",
                    message=(
    f"Video inventory requires exactly {EXPECTED_VIDEO_AGENT_COUNT} entries."
),
                    field=field,
                )
            )

    @staticmethod
    def _validate_bijection(
        manifest_agent_ids: list[str],
        inventory_agent_ids: list[str],
        issues: list[InventoryIssue],
    ) -> None:
        manifest_set = set(manifest_agent_ids)
        inventory_set = set(inventory_agent_ids)
        for agent_id in sorted(manifest_set - inventory_set):
            issues.append(
                InventoryIssue(
                    code="missing_inventory_entry",
                    message="Every Video_Pack agent requires one inventory entry.",
                    field=agent_id,
                )
            )
        for agent_id in sorted(inventory_set - manifest_set):
            issues.append(
                InventoryIssue(
                    code="extra_inventory_entry",
                    message="Inventory entries must correspond to a Video_Pack agent.",
                    field=agent_id,
                )
            )

    @staticmethod
    def _validate_entry_alignment(
        manifest_agents: list[VideoAgentEntry],
        inventory_agents: list[VideoAgentEntry],
        issues: list[InventoryIssue],
    ) -> None:
        manifest_by_id = {entry.agent_id: entry for entry in manifest_agents}
        inventory_by_id = {entry.agent_id: entry for entry in inventory_agents}
        for agent_id in sorted(manifest_by_id.keys() & inventory_by_id.keys()):
            manifest_entry = manifest_by_id[agent_id]
            inventory_entry = inventory_by_id[agent_id]
            if manifest_entry.status != inventory_entry.status:
                issues.append(
                    InventoryIssue(
                        code="inventory_status_mismatch",
                        message="Inventory status must equal the canonical manifest status.",
                        field=agent_id,
                    )
                )
            if manifest_entry.agent_spec_path != inventory_entry.agent_spec_path:
                issues.append(
                    InventoryIssue(
                        code="inventory_spec_path_mismatch",
                        message="Inventory and manifest must name the same agent specification.",
                        field=agent_id,
                    )
                )

    def _validate_agent_specs(
        self,
        manifest_agents: list[VideoAgentEntry],
        agent_specs: Mapping[str, object],
        issues: list[InventoryIssue],
    ) -> tuple[str, ...]:
        specs_by_id: dict[str, object] = {}
        for supplied_id, spec in agent_specs.items():
            canonical_id = self._canonical_identifier(
                supplied_id, f"agent_specs[{supplied_id!r}]", issues
            )
            if canonical_id is None:
                continue
            if canonical_id in specs_by_id:
                issues.append(
                    InventoryIssue(
                        code="duplicate_agent_spec",
                        message="Agent specification identifiers must be unique.",
                        field=canonical_id,
                    )
                )
            specs_by_id[canonical_id] = spec

        expected_by_id = {entry.agent_id: entry for entry in manifest_agents}
        for agent_id in sorted(expected_by_id.keys() - specs_by_id.keys()):
            issues.append(
                InventoryIssue(
                    code="missing_agent_spec",
                    message="Every manifest agent requires a target-local agent specification.",
                    field=agent_id,
                )
            )
        for agent_id in sorted(specs_by_id.keys() - expected_by_id.keys()):
            issues.append(
                InventoryIssue(
                    code="extra_agent_spec",
                    message="Agent specifications must correspond to a canonical manifest agent.",
                    field=agent_id,
                )
            )
        known_agent_ids = set(expected_by_id)
        for agent_id in sorted(expected_by_id.keys() & specs_by_id.keys()):
            self._validate_agent_spec(
                expected_by_id[agent_id],
                specs_by_id[agent_id],
                known_agent_ids,
                issues,
            )
        return tuple(sorted(specs_by_id))

    def _validate_agent_spec(
        self,
        manifest_entry: VideoAgentEntry,
        raw_spec: object,
        known_agent_ids: set[str],
        issues: list[InventoryIssue],
    ) -> None:
        field = f"agent_specs[{manifest_entry.agent_id!r}]"
        spec = self._mapping(raw_spec, field, issues)
        spec_agent_id = self._canonical_identifier(spec.get("agent_id"), field, issues)
        if spec_agent_id != manifest_entry.agent_id:
            issues.append(
                InventoryIssue(
                    code="agent_spec_identifier_mismatch",
                    message="Agent specification identity must equal the manifest agent identity.",
                    field=f"{field}.agent_id",
                )
            )
        status = self._validate_status(spec.get("status"), field, issues)
        if status != manifest_entry.status:
            issues.append(
                InventoryIssue(
                    code="agent_spec_status_mismatch",
                    message="Agent specification status must equal the manifest status.",
                    field=f"{field}.status",
                )
            )
        role = spec.get("role")
        if not isinstance(role, str) or not role.strip():
            issues.append(
                InventoryIssue(
                    code="invalid_agent_role",
                    message="Agent specifications require a nonblank role.",
                    field=f"{field}.role",
                )
            )
        allowed_tools = self._validate_allowed_tools(
            spec.get("allowed_tools"), field, issues
        )
        if allowed_tools != manifest_entry.allowed_tools:
            issues.append(
                InventoryIssue(
                    code="agent_spec_tools_mismatch",
                    message="Agent specification tools must equal the manifest tool policy.",
                    field=f"{field}.allowed_tools",
                )
            )
        self._validate_model_policy(spec.get("model_policy"), field, issues)
        self._validate_budget_policy(spec.get("budget_policy"), field, issues)
        self._validate_reference(spec.get("prompt_reference"), "prompt", field, issues)
        self._validate_reference(spec.get("rubric_reference"), "rubric", field, issues)
        self._validate_critique_edges(
            spec.get("critique_edges"), field, known_agent_ids, issues
        )
        refinement_count = spec.get("max_refinement_count")
        if (
            isinstance(refinement_count, bool)
            or not isinstance(refinement_count, int)
            or not 1 <= refinement_count <= 3
        ):
            issues.append(
                InventoryIssue(
                    code="invalid_refinement_bound",
                    message="Maximum refinement count must be an integer from 1 through 3.",
                    field=f"{field}.max_refinement_count",
                )
            )
        if spec.get("production_activation_requested", False) is not False:
            issues.append(
                InventoryIssue(
                    code="production_activation_requested",
                    message="Agent specifications cannot request production activation.",
                    field=f"{field}.production_activation_requested",
                )
            )

    def _validate_model_policy(
        self, value: object, field: str, issues: list[InventoryIssue]
    ) -> None:
        policy = self._mapping(value, f"{field}.model_policy", issues)
        if policy.get("provider") != "local_deterministic":
            issues.append(
                InventoryIssue(
                    code="invalid_model_policy",
                    message="Video agent model policy must use the local deterministic provider.",
                    field=f"{field}.model_policy.provider",
                )
            )
        model_id = policy.get("model_id")
        if not isinstance(model_id, str) or not model_id.strip():
            issues.append(
                InventoryIssue(
                    code="invalid_model_policy",
                    message="Video agent model policy requires a local model identifier.",
                    field=f"{field}.model_policy.model_id",
                )
            )
        if policy.get("network_access") is not False:
            issues.append(
                InventoryIssue(
                    code="external_access_requested",
                    message="Video agent model policy cannot enable network access.",
                    field=f"{field}.model_policy.network_access",
                )
            )

    def _validate_budget_policy(
        self, value: object, field: str, issues: list[InventoryIssue]
    ) -> None:
        policy = self._mapping(value, f"{field}.budget_policy", issues)
        minimums = {
            "max_input_tokens": 1,
            "max_output_tokens": 1,
            "max_tool_requests": 0,
        }
        for policy_field, minimum in minimums.items():
            policy_value = policy.get(policy_field)
            if (
                isinstance(policy_value, bool)
                or not isinstance(policy_value, int)
                or policy_value < minimum
            ):
                issues.append(
                    InventoryIssue(
                        code="invalid_budget_policy",
                        message="Video agent budget policy must define nonnegative local limits.",
                        field=f"{field}.budget_policy.{policy_field}",
                    )
                )

    @staticmethod
    def _validate_reference(
        value: object, kind: str, field: str, issues: list[InventoryIssue]
    ) -> None:
        prefix = f"video.{kind}."
        if not isinstance(value, str) or not value.startswith(prefix) or "/" in value:
            issues.append(
                InventoryIssue(
                    code=f"invalid_{kind}_reference",
                    message=(
    f"{kind.capitalize()} references must be local video configuration IDs."
),
                    field=f"{field}.{kind}_reference",
                )
            )

    def _validate_critique_edges(
        self,
        value: object,
        field: str,
        known_agent_ids: set[str],
        issues: list[InventoryIssue],
    ) -> None:
        edges = self._mapping(value, f"{field}.critique_edges", issues)
        for edge_name in ("inputs", "outputs"):
            raw_edges = edges.get(edge_name)
            edge_field = f"{field}.critique_edges.{edge_name}"
            if not isinstance(raw_edges, list) or not raw_edges:
                issues.append(
                    InventoryIssue(
                        code="invalid_critique_edges",
                        message="Critique inputs and outputs must be nonempty arrays.",
                        field=edge_field,
                    )
                )
                continue
            canonical_edges: list[str] = []
            for raw_edge in raw_edges:
                canonical_edge = self._canonical_identifier(raw_edge, edge_field, issues)
                if canonical_edge is not None:
                    canonical_edges.append(canonical_edge)
                    if canonical_edge not in known_agent_ids:
                        issues.append(
                            InventoryIssue(
                                code="unknown_critique_edge",
                                message=(
    "Critique edges must reference canonical Video_Pack agents."
),
                                field=edge_field,
                            )
                        )
            if len(set(canonical_edges)) != len(canonical_edges):
                issues.append(
                    InventoryIssue(
                        code="duplicate_critique_edge",
                        message="Critique edges must be unique.",
                        field=edge_field,
                    )
                )
