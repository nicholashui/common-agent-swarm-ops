"""Focused idempotency command-pipeline checks."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import UTC, datetime

from app.core.idempotency import IdempotencyService, request_digest
from app.models.contracts import ErrorCode, ErrorDetail, Result
from app.models.control_plane import IdempotencyStatus
from app.models.identifiers import ActorId, CorrelationId, OrganizationId
from app.repositories.control_plane import InMemoryControlPlaneDatabase

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_ORGANIZATION = OrganizationId("organization-a")
_ACTOR = ActorId("actor-a")
_CORRELATION = CorrelationId("correlation-a")


def _service(database: InMemoryControlPlaneDatabase) -> IdempotencyService:
    return IdempotencyService(database.unit_of_work, clock=lambda: _NOW)


def test_matching_actor_key_and_digest_replays_stored_response_without_second_effect() -> None:
    """A repeated command returns its retained result without invoking the command twice."""
    database = InMemoryControlPlaneDatabase()
    service = _service(database)
    calls = 0

    def command() -> Result[Mapping[str, object], ErrorDetail]:
        nonlocal calls
        calls += 1
        return Result.success({"run_id": "run-1", "status": "dispatching"})

    digest = request_digest("dispatch", {"run_id": "run-1", "confirm": True})
    first = service.execute(_ORGANIZATION, _ACTOR, _CORRELATION, "key-1", digest, command)
    duplicate = service.execute(_ORGANIZATION, _ACTOR, _CORRELATION, "key-1", digest, command)

    assert first.is_success and first.value is not None
    assert duplicate.is_success and duplicate.value is not None
    assert first.value.replayed is False
    assert duplicate.value.replayed is True
    assert duplicate.value.response_payload == first.value.response_payload
    assert calls == 1

    with database.unit_of_work() as unit_of_work:
        stored = unit_of_work.idempotency.get(_ORGANIZATION, _ACTOR, "key-1")
        assert stored.is_success and stored.value is not None
        assert stored.value.status is IdempotencyStatus.COMPLETED
        assert stored.value.response_reference == first.value.response_reference


def test_changed_digest_for_an_actor_key_is_conflict_without_another_effect() -> None:
    """A key cannot be substituted to dispatch a different subject for the same actor."""
    database = InMemoryControlPlaneDatabase()
    service = _service(database)
    calls = 0

    def command() -> Result[Mapping[str, object], ErrorDetail]:
        nonlocal calls
        calls += 1
        return Result.success({"run_id": "run-1"})

    first = service.execute(
        _ORGANIZATION,
        _ACTOR,
        _CORRELATION,
        "key-1",
        request_digest("dispatch", {"run_id": "run-1", "confirm": True}),
        command,
    )
    changed = service.execute(
        _ORGANIZATION,
        _ACTOR,
        _CORRELATION,
        "key-1",
        request_digest("dispatch", {"run_id": "run-2", "confirm": True}),
        command,
    )

    assert first.is_success
    assert not changed.is_success
    assert changed.error is not None and changed.error.code is ErrorCode.CONFLICT
    assert calls == 1


def test_blank_key_is_rejected_before_command_execution() -> None:
    """Missing or whitespace-only keys do not reserve a record or execute an effect."""
    database = InMemoryControlPlaneDatabase()
    service = _service(database)
    calls = 0

    def command() -> Result[Mapping[str, object], ErrorDetail]:
        nonlocal calls
        calls += 1
        return Result.success({"run_id": "run-1"})

    rejected = service.execute(
        _ORGANIZATION,
        _ACTOR,
        _CORRELATION,
        "  ",
        request_digest("dispatch", {"run_id": "run-1", "confirm": True}),
        command,
    )

    assert not rejected.is_success
    assert rejected.error is not None and rejected.error.code is ErrorCode.VALIDATION_FAILED
    assert calls == 0
