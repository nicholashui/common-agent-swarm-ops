"""Deterministic governance evidence for Special_Agent test fixtures."""

from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path
from typing import Final, cast

from app.registry.specials_validator import (
    SPECIAL_AGENT_SPEC_PATHS,
    SPECIAL_SOURCE_CATALOG,
    SPECIALS_APPROVAL_ROOT,
    SPECIALS_RISK_ASSESSMENT_ROOT,
    SPECIALS_SOURCE_RECORD_ROOT,
    canonical_json_bytes,
    sha256_bytes,
    sha256_json,
)

_REVIEW_TIMESTAMP: Final[str] = "2025-01-01T00:00:00+00:00"
_REVIEWER_IDENTITY: Final[str] = "human-specials-fixture-reviewer"
_RISK_FIELDS: Final[tuple[str, ...]] = (
    "sensitive_personal_data",
    "psychological_profiling_or_recommendation",
    "legal",
    "medical",
    "financial",
    "external_service",
    "credential",
    "external_write",
    "production_release",
)


def _write_json(path: Path, value: object) -> None:
    """Write one canonical local JSON fixture file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json_bytes(value) + b"\n")


def _source_bytes(root: Path, source_path: str, agent_id: str) -> bytes:
    """Preserve an existing opaque source or create inert deterministic bytes."""
    source_target = root / source_path
    if source_target.exists():
        if not source_target.is_file():
            raise AssertionError(f"Expected source fixture file at {source_target}.")
        return source_target.read_bytes()

    source_bytes = f"deterministic opaque source fixture bytes for {agent_id}\n".encode()
    source_target.parent.mkdir(parents=True, exist_ok=True)
    source_target.write_bytes(source_bytes)
    return source_bytes


def _source_record(
    agent_id: str,
    source_path: str,
    source_digest: str,
    configuration_digest: str,
    approval_id: str,
) -> dict[str, object]:
    """Build a source record bound to one fixture specification."""
    return {
        "schema_version": "1.0",
        "source_path": source_path,
        "source_sha256": source_digest,
        "agent_id": agent_id,
        "configuration_sha256": configuration_digest,
        "reviewed_at": _REVIEW_TIMESTAMP,
        "approval_id": approval_id,
    }


def _risk_assessment(configuration_digest: str, source_record_digest: str) -> dict[str, object]:
    """Build an explicit zero-authority risk assessment."""
    return {
        "schema_version": "1.0",
        "configuration_sha256": configuration_digest,
        "source_record_sha256": source_record_digest,
        "potential_risks": {risk_name: False for risk_name in _RISK_FIELDS},
        "external_effect_potential": "none",
        "requested_tool_authority": "none",
        "requested_network_access": False,
        "requested_provider": "none",
        "requested_production_activation": False,
        "requested_lifecycle_state": "draft",
    }


def _approval_record(
    agent_id: str,
    source_record: dict[str, object],
    source_record_digest: str,
    risk_assessment: dict[str, object],
) -> dict[str, object]:
    """Build a fixed human approval for the zero-authority fixture scope."""
    approved_risk_scope = {
        key: value
        for key, value in risk_assessment.items()
        if key not in {"schema_version", "configuration_sha256", "source_record_sha256"}
    }
    return {
        "approval_id": source_record["approval_id"],
        "reviewer_identity": _REVIEWER_IDENTITY,
        "decision_timestamp": _REVIEW_TIMESTAMP,
        "decision": "approved",
        "source_path": source_record["source_path"],
        "source_sha256": source_record["source_sha256"],
        "agent_id": agent_id,
        "configuration_sha256": source_record["configuration_sha256"],
        "source_record_sha256": source_record_digest,
        "approved_risk_scope": approved_risk_scope,
        "reason": "Approved deterministic data-only fixture evidence.",
    }


def materialize_specials_governance(
    root: Path,
    allowlisted_paths: Iterable[str] = (),
) -> tuple[str, ...]:
    """Add deterministic source, risk, and approval evidence to a test fixture.

    Source bytes are opaque to this helper and are never parsed into
    configuration.  Existing source files are preserved; absent sources use
    inert deterministic bytes so the resulting Source_Record can be checked
    independently by the production validator.
    """
    paths = set(allowlisted_paths)
    for entry, specification_relative_path in zip(
        SPECIAL_SOURCE_CATALOG,
        SPECIAL_AGENT_SPEC_PATHS,
        strict=True,
    ):
        specification_path = root / specification_relative_path
        if not specification_path.is_file():
            continue

        source_bytes = _source_bytes(root, entry.source_path, entry.agent_id)
        paths.add(entry.source_path)

        specification_value: object = json.loads(specification_path.read_text(encoding="utf-8"))
        if not isinstance(specification_value, dict):
            raise AssertionError(f"Expected specification object at {specification_path}.")
        configuration_digest = sha256_json(cast(dict[str, object], specification_value))

        approval_id = f"fixture-approval-{entry.agent_id.removeprefix('specials.')}"
        source_record = _source_record(
            entry.agent_id,
            entry.source_path,
            sha256_bytes(source_bytes),
            configuration_digest,
            approval_id,
        )
        source_record_path = f"{SPECIALS_SOURCE_RECORD_ROOT}/{entry.agent_id}.json"
        _write_json(root / source_record_path, source_record)
        paths.add(source_record_path)

        source_record_digest = sha256_json(source_record)
        risk_assessment = _risk_assessment(configuration_digest, source_record_digest)
        risk_path = f"{SPECIALS_RISK_ASSESSMENT_ROOT}/{configuration_digest}.json"
        _write_json(root / risk_path, risk_assessment)
        paths.add(risk_path)

        approval = _approval_record(
            entry.agent_id,
            source_record,
            source_record_digest,
            risk_assessment,
        )
        approval_path = f"{SPECIALS_APPROVAL_ROOT}/{approval_id}.json"
        _write_json(root / approval_path, approval)
        paths.add(approval_path)

    return tuple(sorted(paths))


__all__ = ["materialize_specials_governance"]
