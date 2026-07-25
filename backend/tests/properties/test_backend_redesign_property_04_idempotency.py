"""Property checks for idempotent state-changing command dispatch."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import UTC, datetime
from typing import cast

from hypothesis import given, settings, strategies as st

from app.core.idempotency import (
    IdempotencyOutcome,
    IdempotencyService,
    UnitOfWorkFactory,
    request_digest,
)
from app.models.contracts import ErrorCode, ErrorDetail, Result
from app.models.control_plane import IdempotencyStatus
from app.models.identifiers import ActorId, CorrelationId, OrganizationId
from app.repositories.control_plane import InMemoryControlPlaneDatabase

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_ORGANIZATION = OrganizationId("property-4-organization")
_CORRELATION = CorrelationId("property-4-correlation")
_SAFE_SUFFIXES = st.text(alphabet="abcdefghijklmnopqrstuvwxyz0123456789", min_size=1, max_size=12)
_BLANK_KEYS = st.sampled_from(("", " ", "\t", "\n", " \t "))
_KEYS = st.one_of(_BLANK_KEYS, st.builds(lambda suffix: f"key-{suffix}", _SAFE_SUFFIXES))


# **Validates: Requirements 2.5, 2.6, 2.7, 5.8**
# Feature: backend-redesign, Property 4
@settings(max_examples=100)
@given(
    actor_suffix=_SAFE_SUFFIXES,
    key=_KEYS,
    run_suffix=_SAFE_SUFFIXES,
    duplicate_dispatches=st.integers(min_value=2, max_value=5),
)
def test_property_4_state_changing_commands_are_idempotent(
    actor_suffix: str, key: str, run_suffix: str, duplicate_dispatches: int
) -> None:
    """Blank keys have no effect; matching duplicate dispatches replay one stored outcome."""
    database = InMemoryControlPlaneDatabase()
    service = IdempotencyService(cast(UnitOfWorkFactory, database.unit_of_work), clock=lambda: _NOW)
    actor = ActorId(f"actor-{actor_suffix}")
    digest = request_digest("dispatch", {"run_id": f"run-{run_suffix}", "confirm": True})
    mutation_count = 0

    def dispatch() -> Result[Mapping[str, object], ErrorDetail]:
        nonlocal mutation_count
        mutation_count += 1
        return Result.success({"run_id": f"run-{run_suffix}", "state": "dispatched"})

    outcomes: list[IdempotencyOutcome] = []
    for _ in range(duplicate_dispatches):
        result = service.execute(_ORGANIZATION, actor, _CORRELATION, key, digest, dispatch)
        if key.strip():
            assert result.is_success and result.value is not None
            outcomes.append(result.value)
        else:
            assert not result.is_success
            assert result.error is not None and result.error.code is ErrorCode.VALIDATION_FAILED

    if not key.strip():
        assert mutation_count == 0
        with database.unit_of_work() as unit_of_work:
            stored = unit_of_work.idempotency.get(_ORGANIZATION, actor, key)
            assert not stored.is_success
            assert stored.error is not None and stored.error.code is ErrorCode.NOT_FOUND
        return

    first = outcomes[0]
    assert mutation_count == 1
    assert first.replayed is False
    assert all(outcome.replayed for outcome in outcomes[1:])
    assert all(outcome.response_payload == first.response_payload for outcome in outcomes[1:])
    assert all(outcome.response_reference == first.response_reference for outcome in outcomes[1:])
    with database.unit_of_work() as unit_of_work:
        stored = unit_of_work.idempotency.get(_ORGANIZATION, actor, key)
        assert stored.is_success and stored.value is not None
        assert stored.value.status is IdempotencyStatus.COMPLETED
        assert stored.value.request_digest == digest
        assert stored.value.response_reference == first.response_reference
        assert stored.value.response_payload == first.response_payload
