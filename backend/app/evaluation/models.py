"""Immutable records for deterministic, local evaluation suites."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from app.models.common import RecordMetadata
from app.models.identifiers import EvaluationResultId, EvaluationRunId


class EvaluationOutcome(StrEnum):
    """A retained pass or fail outcome for one evaluation cell."""

    PASS = "pass"
    FAIL = "fail"


class EvaluationCheckKind(StrEnum):
    """Named deterministic evaluation families."""

    REGRESSION = "regression"
    ADVERSARIAL = "adversarial"
    HISTORICAL_REPLAY = "historical-replay"
    COST = "cost"
    LATENCY = "latency"
    SAFETY = "safety"
    COMPLIANCE = "compliance"


@dataclass(frozen=True, slots=True)
class NamedEvaluationCheck:
    """A suite check with an explicit transition-blocking policy."""

    name: str
    kind: EvaluationCheckKind
    blocking: bool


DEFAULT_NAMED_CHECKS = (
    NamedEvaluationCheck("regression.golden-output", EvaluationCheckKind.REGRESSION, True),
    NamedEvaluationCheck("adversarial.untrusted-input", EvaluationCheckKind.ADVERSARIAL, True),
    NamedEvaluationCheck(
        "historical-replay.recorded-case", EvaluationCheckKind.HISTORICAL_REPLAY, True
    ),
    NamedEvaluationCheck("cost.local-budget", EvaluationCheckKind.COST, False),
    NamedEvaluationCheck("latency.local-budget", EvaluationCheckKind.LATENCY, False),
    NamedEvaluationCheck("safety.policy-gate", EvaluationCheckKind.SAFETY, True),
    NamedEvaluationCheck("compliance.provenance", EvaluationCheckKind.COMPLIANCE, True),
)


@dataclass(frozen=True, slots=True)
class GoldenTask:
    """A validated, deterministic JSON task retained within the target workspace."""

    task_id: str
    scenario: str
    input_payload: Mapping[str, object]
    expected_outcome: EvaluationOutcome


@dataclass(frozen=True, slots=True)
class EvaluationCellResult:
    """One immutable result for a task and named suite check."""

    result_id: EvaluationResultId
    task_id: str
    check_name: str
    check_kind: EvaluationCheckKind
    blocking: bool
    outcome: EvaluationOutcome
    recorded_at: datetime
    evidence_digest: str


@dataclass(frozen=True, slots=True)
class EvaluationRun:
    """A separately retained evaluation execution and its complete task/check matrix."""

    metadata: RecordMetadata
    evaluation_run_id: EvaluationRunId
    configuration_digest: str
    task_ids: tuple[str, ...]
    checks: tuple[NamedEvaluationCheck, ...]
    results: tuple[EvaluationCellResult, ...]
    completed: bool
    transition_permitted: bool
