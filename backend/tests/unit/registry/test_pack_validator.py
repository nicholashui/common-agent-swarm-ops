"""Focused registration tests for DomainPackValidator."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.core.boundary import WorkspaceBoundary
from app.core.errors import BoundaryViolationError
from app.registry.pack_validator import DomainPackValidator
from app.repositories.pack_repository import (
    AgentLifecycleStatus,
    InMemoryPackRepository,
    PackRegistrationStatus,
)


def _validator(tmp_path: Path) -> tuple[DomainPackValidator, InMemoryPackRepository]:
    root = tmp_path / "target"
    repository = InMemoryPackRepository()
    return DomainPackValidator(repository, WorkspaceBoundary(root, None)), repository


def test_valid_manifest_is_canonicalized_and_registered_non_active(tmp_path: Path) -> None:
    validator, repository = _validator(tmp_path)

    result = validator.register_inline(
        {
            "pack_id": "Sales",
            "agents": [
                {"agent_id": "Sales.Writer", "status": "registered"},
                {"agent_id": "sales.reviewer", "status": "draft"},
            ],
        }
    )

    assert result.is_success
    record = result.value
    assert record is not None
    assert record.status is PackRegistrationStatus.REGISTERED
    assert record.pack_id == "sales"
    assert [agent.status for agent in record.agents] == [
        AgentLifecycleStatus.REGISTERED,
        AgentLifecycleStatus.DRAFT,
    ]
    assert not record.production_active
    assert all(not agent.production_active for agent in record.agents)
    assert repository.outcomes() == (record,)


def test_invalid_manifest_records_inactive_denied_agents(tmp_path: Path) -> None:
    validator, _ = _validator(tmp_path)

    result = validator.register_inline(
        {
            "pack_id": "sales",
            "production_activation_requested": True,
            "agents": [
                {"agent_id": "Sales.Writer", "status": "draft"},
                {"agent_id": "sales.writer", "status": "retired"},
            ],
        }
    )

    assert result.is_success
    record = result.value
    assert record is not None
    assert record.status is PackRegistrationStatus.INACTIVE
    assert not record.validation_report.is_valid
    assert {
        issue.code for issue in record.validation_report.issues
    } >= {"duplicate_canonical_agent_id", "invalid_status", "production_activation_requested"}
    assert all(agent.production_activation_denied for agent in record.agents)
    assert all(not agent.production_active for agent in record.agents)


def test_path_registration_rejects_outside_business_root(tmp_path: Path) -> None:
    validator, _ = _validator(tmp_path)
    outside_manifest = tmp_path / "outside.json"
    outside_manifest.write_text(json.dumps({"pack_id": "sales", "agents": []}), encoding="utf-8")

    with pytest.raises(BoundaryViolationError):
        validator.register_from_path(outside_manifest)


@pytest.mark.parametrize(
    ("pack_id", "agent_count"),
    (("sales.one", 1), ("sales.hundred", 100)),
)
def test_agent_count_boundaries_register_all_agents_non_active(
    tmp_path: Path, pack_id: str, agent_count: int
) -> None:
    validator, repository = _validator(tmp_path)

    result = validator.register_inline(
        {
            "pack_id": pack_id,
            "agents": [
                {"agent_id": f"sales.agent-{index}", "status": "registered"}
                for index in range(agent_count)
            ],
        }
    )

    assert result.is_success
    record = result.value
    assert record is not None
    assert record.status is PackRegistrationStatus.REGISTERED
    assert len(record.agents) == agent_count
    assert all(agent.status is AgentLifecycleStatus.REGISTERED for agent in record.agents)
    assert all(not agent.production_active for agent in record.agents)
    assert repository.outcomes() == (record,)


def test_duplicate_canonical_pack_id_records_an_inactive_denied_outcome(tmp_path: Path) -> None:
    validator, repository = _validator(tmp_path)

    first = validator.register_inline(
        {"pack_id": "Sales", "agents": [{"agent_id": "sales.writer", "status": "registered"}]}
    )
    duplicate = validator.register_inline(
        {
            "pack_id": " sales ",
            "agents": [{"agent_id": "sales.reviewer", "status": "registered"}],
        }
    )

    assert first.is_success
    assert first.value is not None
    assert first.value.status is PackRegistrationStatus.REGISTERED
    assert duplicate.is_success
    record = duplicate.value
    assert record is not None
    assert record.pack_id == "sales"
    assert record.status is PackRegistrationStatus.INACTIVE
    assert not record.validation_report.is_valid
    assert {issue.code for issue in record.validation_report.issues} == {
        "duplicate_registered_pack_id"
    }
    assert all(agent.production_activation_denied for agent in record.agents)
    assert all(not agent.production_active for agent in record.agents)
    assert repository.outcomes() == (first.value, record)


def test_duplicate_canonical_agent_ids_inactivate_and_deny_every_agent(tmp_path: Path) -> None:
    validator, _ = _validator(tmp_path)

    result = validator.register_inline(
        {
            "pack_id": "sales",
            "agents": [
                {"agent_id": "Sales.Writer", "status": "registered"},
                {"agent_id": " sales.writer ", "status": "draft"},
            ],
        }
    )

    assert result.is_success
    record = result.value
    assert record is not None
    assert record.status is PackRegistrationStatus.INACTIVE
    assert {issue.code for issue in record.validation_report.issues} == {
        "duplicate_canonical_agent_id"
    }
    assert all(agent.production_activation_denied for agent in record.agents)
    assert all(not agent.production_active for agent in record.agents)


@pytest.mark.parametrize(
    ("request_location", "request_field"),
    (("manifest", "production_activation_requested"), ("agent", "activate_in_production")),
)
def test_production_activation_request_inactivates_and_denies_every_agent(
    tmp_path: Path, request_location: str, request_field: str
) -> None:
    validator, _ = _validator(tmp_path)
    manifest: dict[str, object] = {
        "pack_id": "sales",
        "agents": [
            {"agent_id": "sales.writer", "status": "registered"},
            {"agent_id": "sales.reviewer", "status": "draft"},
        ],
    }
    if request_location == "manifest":
        manifest[request_field] = True
    else:
        agents = manifest["agents"]
        assert isinstance(agents, list)
        agents[0][request_field] = True

    result = validator.register_inline(manifest)

    assert result.is_success
    record = result.value
    assert record is not None
    assert record.status is PackRegistrationStatus.INACTIVE
    assert "production_activation_requested" in {
        issue.code for issue in record.validation_report.issues
    }
    assert all(agent.production_activation_denied for agent in record.agents)
    assert all(not agent.production_active for agent in record.agents)
