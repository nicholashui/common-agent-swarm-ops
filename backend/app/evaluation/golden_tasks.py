"""Target-local loading and validation for deterministic golden JSON tasks."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path

from app.evaluation.models import EvaluationOutcome, GoldenTask

DEFAULT_GOLDEN_TASK_DIRECTORY = (
    Path(__file__).resolve().parents[3] / "business" / "evals" / "golden-tasks"
)
MINIMUM_GOLDEN_TASK_COUNT = 20


class GoldenTaskLoader:
    """Loads only validated JSON fixtures retained in the target workspace."""

    def __init__(self, directory: Path = DEFAULT_GOLDEN_TASK_DIRECTORY) -> None:
        self._directory = directory.resolve()

    def load(self) -> tuple[GoldenTask, ...]:
        """Return the deterministically sorted retained task corpus."""
        if not self._directory.is_dir():
            raise ValueError("Golden task directory is unavailable.")
        tasks = tuple(self._load_file(path) for path in sorted(self._directory.glob("*.json")))
        if len(tasks) < MINIMUM_GOLDEN_TASK_COUNT:
            raise ValueError("At least 20 golden JSON tasks are required.")
        if len({task.task_id for task in tasks}) != len(tasks):
            raise ValueError("Golden task identifiers must be unique.")
        return tasks

    @classmethod
    def _load_file(cls, path: Path) -> GoldenTask:
        try:
            raw: object = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise ValueError(f"Golden task {path.name} could not be read.") from error
        document = cls._mapping(raw, path.name)
        if document.get("schema_version") != 1:
            raise ValueError(f"Golden task {path.name} has an unsupported schema version.")
        try:
            outcome = EvaluationOutcome(cls._string(document, "expected_outcome"))
        except ValueError as error:
            raise ValueError(f"Golden task {path.name} has an invalid expected outcome.") from error
        return GoldenTask(
            task_id=cls._string(document, "task_id"),
            scenario=cls._string(document, "scenario"),
            input_payload=cls._mapping(document.get("input"), "input"),
            expected_outcome=outcome,
        )


    @staticmethod
    def _mapping(value: object, field: str) -> Mapping[str, object]:
        if not isinstance(value, Mapping) or not all(isinstance(key, str) for key in value):
            raise ValueError(f"Golden task {field} must be an object.")
        return {key: item for key, item in value.items() if isinstance(key, str)}

    @staticmethod
    def _string(document: Mapping[str, object], field: str) -> str:
        value = document.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Golden task {field} must be a non-empty string.")
        return value
