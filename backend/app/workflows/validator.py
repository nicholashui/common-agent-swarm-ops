"""Fail-closed validation for portable, data-only WorkflowDNA definitions."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Final

from app.models.runs import WorkflowEngineKind

_IDENTIFIER: Final[re.Pattern[str]] = re.compile(r"^[a-z][a-z0-9_.-]{0,99}$")
_VERSION: Final[re.Pattern[str]] = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
MAX_NODES: Final[int] = 100
MAX_HANDOFFS: Final[int] = 12
MAX_WALL_CLOCK_SECONDS: Final[int] = 900
MAX_TOOL_REQUESTS: Final[int] = 50


@dataclass(frozen=True, slots=True)
class RegisteredReferences:
    """Host-owned registries available to a definition; payloads cannot extend them."""

    agent_ids: frozenset[str]
    tool_ids: frozenset[str]
    memory_scope_ids: frozenset[str]
    risk_gate_ids: frozenset[str]
    rollback_plan_ids: frozenset[str]
    authorization_ids: frozenset[str]


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    """A deterministic, redaction-safe definition validation failure."""

    field: str
    reason: str


@dataclass(frozen=True, slots=True)
class ValidationReport:
    """The complete result of validating an untrusted workflow definition."""

    issues: tuple[ValidationIssue, ...] = ()

    @property
    def is_valid(self) -> bool:
        """Return whether no validation failure was recorded."""
        return not self.issues


class DefinitionValidationError(ValueError):
    """Raised by the explicit reject gate before any execution operation."""


class WorkflowDefinitionValidator:
    """Validate an untrusted workflow before a Host lifecycle operation begins."""

    def __init__(self, registered_references: RegisteredReferences) -> None:
        self._registered_references = registered_references

    def validate(self, definition: Mapping[str, object]) -> ValidationReport:
        """Return all validation failures without creating a run or invoking any service."""
        if definition.get("definition_type") == "pack_graph":
            from app.workflows.graph_validator import GraphDefinitionValidator

            return GraphDefinitionValidator(self._registered_references).validate(definition)

        issues: list[ValidationIssue] = []
        declared_reads, declared_writes = self.validate_common_fields(
            definition, self._registered_references, issues, "workflow_dna"
        )
        self._reject_unknown_fields(
            definition,
            frozenset(
                {
                    "definition_type",
                    "id",
                    "version",
                    "owner_id",
                    "authorization_id",
                    "engine",
                    "execution_budget",
                    "memory",
                    "risk_gate_ids",
                    "rollback",
                    "steps",
                }
            ),
            issues,
        )
        step_ids = self._validate_steps(
            definition.get("steps"), declared_reads, declared_writes, issues
        )
        self._validate_rollback(
            definition.get("rollback"),
            step_ids,
            self._registered_references.rollback_plan_ids,
            issues,
        )
        return ValidationReport(tuple(issues))

    def validate_or_reject(self, definition: Mapping[str, object]) -> None:
        """Raise before run creation, compilation, dispatch, adapter calls, or effects."""
        report = self.validate(definition)
        if not report.is_valid:
            raise DefinitionValidationError(report)

    @classmethod
    def validate_common_fields(
        cls,
        definition: Mapping[str, object],
        references: RegisteredReferences,
        issues: list[ValidationIssue],
        expected_type: str,
    ) -> tuple[frozenset[str], frozenset[str]]:
        """Validate shared data-only fields using Host-owned reference registries."""
        if definition.get("definition_type") != expected_type:
            issues.append(ValidationIssue("definition_type", f"must be {expected_type}"))
        cls._validate_identifier(definition.get("id"), "id", issues)
        version = definition.get("version")
        if not isinstance(version, str) or _VERSION.fullmatch(version) is None:
            issues.append(ValidationIssue("version", "must be a semantic version"))
        cls._validate_identifier(definition.get("owner_id"), "owner_id", issues)
        cls._validate_registered_identifier(
            definition.get("authorization_id"),
            "authorization_id",
            references.authorization_ids,
            issues,
        )
        engine = definition.get("engine")
        if engine not in {kind.value for kind in WorkflowEngineKind}:
            issues.append(ValidationIssue("engine", "must select a Host-supported engine"))
        cls._validate_execution_budget(definition.get("execution_budget"), issues)
        declared_reads, declared_writes = cls._validate_memory(
            definition.get("memory"), references, issues
        )
        risk_gates = cls._string_list(definition.get("risk_gate_ids"), "risk_gate_ids", issues)
        if risk_gates is not None:
            if not risk_gates:
                issues.append(
                    ValidationIssue("risk_gate_ids", "must declare at least one risk gate")
                )
            cls._validate_registered_values(
                risk_gates, "risk_gate_ids", references.risk_gate_ids, issues
            )
        return declared_reads, declared_writes

    @classmethod
    def _validate_execution_budget(cls, value: object, issues: list[ValidationIssue]) -> None:
        budget = cls._mapping(value, "execution_budget", issues)
        if budget is None:
            return
        limits = {
            "max_node_visits": (1, MAX_NODES),
            "max_handoffs": (0, MAX_HANDOFFS),
            "max_wall_clock_seconds": (1, MAX_WALL_CLOCK_SECONDS),
            "max_tool_requests": (0, MAX_TOOL_REQUESTS),
        }
        cls._reject_unknown_fields(budget, frozenset(limits), issues, "execution_budget")
        for name, (minimum, maximum) in limits.items():
            value = budget.get(name)
            if (
                not isinstance(value, int)
                or isinstance(value, bool)
                or not minimum <= value <= maximum
            ):
                issues.append(
                    ValidationIssue(
                        f"execution_budget.{name}", f"must be {minimum} through {maximum}"
                    )
                )

    @classmethod
    def _validate_memory(
        cls,
        value: object,
        references: RegisteredReferences,
        issues: list[ValidationIssue],
    ) -> tuple[frozenset[str], frozenset[str]]:
        memory = cls._mapping(value, "memory", issues)
        if memory is None:
            return frozenset(), frozenset()
        cls._reject_unknown_fields(memory, frozenset({"reads", "writes"}), issues, "memory")
        reads = cls._string_list(memory.get("reads"), "memory.reads", issues)
        writes = cls._string_list(memory.get("writes"), "memory.writes", issues)
        if reads is not None:
            cls._validate_registered_values(
                reads, "memory.reads", references.memory_scope_ids, issues
            )
        if writes is not None:
            cls._validate_registered_values(
                writes, "memory.writes", references.memory_scope_ids, issues
            )
        return frozenset(reads or ()), frozenset(writes or ())

    def _validate_steps(
        self,
        value: object,
        declared_reads: frozenset[str],
        declared_writes: frozenset[str],
        issues: list[ValidationIssue],
    ) -> frozenset[str]:
        if not isinstance(value, list) or not 1 <= len(value) <= MAX_NODES:
            issues.append(ValidationIssue("steps", f"must contain 1 through {MAX_NODES} steps"))
            return frozenset()
        step_ids: set[str] = set()
        for index, raw_step in enumerate(value):
            field = f"steps[{index}]"
            if not isinstance(raw_step, Mapping):
                issues.append(ValidationIssue(field, "must be an object"))
                continue
            self._reject_unknown_fields(
                raw_step,
                frozenset({"id", "agent_id", "tool_ids", "memory_reads", "memory_writes"}),
                issues,
                field,
            )
            step_id = raw_step.get("id")
            self._validate_identifier(step_id, f"{field}.id", issues)
            if isinstance(step_id, str):
                if step_id in step_ids:
                    issues.append(ValidationIssue(f"{field}.id", "must be unique"))
                step_ids.add(step_id)
            self._validate_registered_identifier(
                raw_step.get("agent_id"),
                f"{field}.agent_id",
                self._registered_references.agent_ids,
                issues,
            )
            self._validate_step_access(
                raw_step,
                field,
                declared_reads,
                declared_writes,
                self._registered_references,
                issues,
            )
        return frozenset(step_ids)

    @classmethod
    def _validate_step_access(
        cls,
        step: Mapping[str, object],
        field: str,
        declared_reads: frozenset[str],
        declared_writes: frozenset[str],
        references: RegisteredReferences,
        issues: list[ValidationIssue],
    ) -> None:
        tool_ids = cls._string_list(step.get("tool_ids"), f"{field}.tool_ids", issues)
        if tool_ids is not None:
            cls._validate_registered_values(
                tool_ids, f"{field}.tool_ids", references.tool_ids, issues
            )
        read_scopes = cls._string_list(step.get("memory_reads"), f"{field}.memory_reads", issues)
        write_scopes = cls._string_list(step.get("memory_writes"), f"{field}.memory_writes", issues)
        if read_scopes is not None:
            cls._validate_registered_values(
                read_scopes, f"{field}.memory_reads", references.memory_scope_ids, issues
            )
            cls._validate_declared_scopes(
                read_scopes, f"{field}.memory_reads", declared_reads, issues
            )
        if write_scopes is not None:
            cls._validate_registered_values(
                write_scopes, f"{field}.memory_writes", references.memory_scope_ids, issues
            )
            cls._validate_declared_scopes(
                write_scopes, f"{field}.memory_writes", declared_writes, issues
            )

    @classmethod
    def _validate_rollback(
        cls,
        value: object,
        step_ids: frozenset[str],
        rollback_plan_ids: frozenset[str],
        issues: list[ValidationIssue],
    ) -> None:
        rollback = cls._mapping(value, "rollback", issues)
        if rollback is None:
            return
        cls._reject_unknown_fields(
            rollback, frozenset({"plan_id", "compensation_step_ids"}), issues, "rollback"
        )
        cls._validate_registered_identifier(
            rollback.get("plan_id"), "rollback.plan_id", rollback_plan_ids, issues
        )
        compensation_steps = cls._string_list(
            rollback.get("compensation_step_ids"), "rollback.compensation_step_ids", issues
        )
        if compensation_steps is not None:
            for step_id in compensation_steps:
                if step_id not in step_ids:
                    issues.append(
                        ValidationIssue(
                            "rollback.compensation_step_ids", "must reference a declared step"
                        )
                    )

    @classmethod
    def _validate_registered_identifier(
        cls,
        value: object,
        field: str,
        registered_values: frozenset[str],
        issues: list[ValidationIssue],
    ) -> None:
        cls._validate_identifier(value, field, issues)
        if isinstance(value, str) and value not in registered_values:
            issues.append(ValidationIssue(field, "must reference a registered value"))

    @staticmethod
    def _validate_identifier(value: object, field: str, issues: list[ValidationIssue]) -> None:
        if not isinstance(value, str) or _IDENTIFIER.fullmatch(value) is None:
            issues.append(ValidationIssue(field, "must be a canonical identifier"))

    @classmethod
    def _validate_registered_values(
        cls,
        values: Sequence[str],
        field: str,
        registered_values: frozenset[str],
        issues: list[ValidationIssue],
    ) -> None:
        for value in values:
            cls._validate_identifier(value, field, issues)
            if value not in registered_values:
                issues.append(ValidationIssue(field, "must reference registered values"))

    @staticmethod
    def _validate_declared_scopes(
        values: Sequence[str], field: str, declared: frozenset[str], issues: list[ValidationIssue]
    ) -> None:
        for value in values:
            if value not in declared:
                issues.append(
                    ValidationIssue(field, "must be declared by the workflow memory scope")
                )

    @staticmethod
    def _mapping(
        value: object, field: str, issues: list[ValidationIssue]
    ) -> Mapping[str, object] | None:
        if not isinstance(value, Mapping):
            issues.append(ValidationIssue(field, "must be an object"))
            return None
        return value

    @classmethod
    def _string_list(
        cls, value: object, field: str, issues: list[ValidationIssue]
    ) -> list[str] | None:
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            issues.append(ValidationIssue(field, "must be an array of identifiers"))
            return None
        if len(set(value)) != len(value):
            issues.append(ValidationIssue(field, "must not contain duplicates"))
        for item in value:
            cls._validate_identifier(item, field, issues)
        return value

    @staticmethod
    def _reject_unknown_fields(
        value: Mapping[str, object],
        allowed_fields: frozenset[str],
        issues: list[ValidationIssue],
        prefix: str = "",
    ) -> None:
        for field in value:
            if field not in allowed_fields:
                name = f"{prefix}.{field}" if prefix else field
                issues.append(ValidationIssue(name, "is not permitted in a data-only definition"))
