"""Property tests for fail-closed workspace and adoption authorization."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from hypothesis import given, settings, strategies as st

from app.core.boundary import AdoptionApproval, BoundaryOperation, WorkspaceBoundary
from app.core.errors import BoundaryViolationError

# Feature: generic-swarm-business-os, Property 2: Workspace and adoption authorization is
# fail-closed.
# **Validates: Requirements 1.2, 1.3, 1.4, 1.5**

_SAFE_SEGMENT = st.text(
    alphabet=st.characters(whitelist_categories=("Ll", "Lu", "Nd")),
    min_size=1,
    max_size=8,
)
_BOUNDED_SEGMENTS = st.lists(_SAFE_SEGMENT, min_size=0, max_size=3).map(tuple)
_PATH_KINDS = st.sampled_from(("target", "reference", "outside", "traversal"))
_APPROVAL_STATES = st.sampled_from(("missing", "prior", "rejected", "late"))
_REQUESTED_AT = datetime(2025, 1, 2, tzinfo=UTC)


def _bounded_path(
    kind: str,
    target: Path,
    reference: Path,
    outside: Path,
    segments: tuple[str, ...],
) -> Path:
    roots = {"target": target, "reference": reference, "outside": outside}
    if kind == "traversal":
        return target.joinpath("..", "outside", *segments)
    return roots[kind].joinpath(*segments)


def _approval_for(state: str) -> AdoptionApproval | None:
    if state == "missing":
        return None
    recorded_at = _REQUESTED_AT - timedelta(seconds=1)
    if state == "late":
        recorded_at = _REQUESTED_AT + timedelta(seconds=1)
    return AdoptionApproval(
        record_id="approval-1",
        approved_by="operator-1",
        recorded_at=recorded_at,
        approved=state == "prior" or state == "late",
    )


def _snapshot(target: Path, reference: Path) -> tuple[bytes, bytes]:
    return ((target / "sentinel.txt").read_bytes(), (reference / "sentinel.txt").read_bytes())


def _boundary(tmp_path: Path) -> tuple[WorkspaceBoundary, Path, Path, Path]:
    target, reference, outside = (tmp_path / name for name in ("target", "reference", "outside"))
    for root in (target, reference, outside):
        root.mkdir(exist_ok=True)
    (target / "sentinel.txt").write_text("target", encoding="utf-8")
    (reference / "sentinel.txt").write_text("reference", encoding="utf-8")
    return WorkspaceBoundary(target, reference), target, reference, outside


@settings(max_examples=100)
@given(
    operation=st.sampled_from(
        (BoundaryOperation.ACCESS, BoundaryOperation.WRITE, BoundaryOperation.EXECUTE)
    ),
    path_kind=_PATH_KINDS,
    segments=_BOUNDED_SEGMENTS,
)
def test_workspace_operations_are_confined_and_read_only_for_reference(
    operation: BoundaryOperation,
    path_kind: str,
    segments: tuple[str, ...],
) -> None:
    with TemporaryDirectory() as temporary_directory:
        boundary, target, reference, outside = _boundary(Path(temporary_directory))
        requested_path = _bounded_path(path_kind, target, reference, outside, segments)
        before = _snapshot(target, reference)
        permitted = path_kind == "target" or (
            path_kind == "reference" and operation is BoundaryOperation.ACCESS
        )

        if permitted:
            assert boundary.authorize(operation, requested_path) == requested_path.resolve()
        else:
            with pytest.raises(BoundaryViolationError):
                boundary.authorize(operation, requested_path)

        assert _snapshot(target, reference) == before


@settings(max_examples=100)
@given(
    source_kind=_PATH_KINDS,
    destination_kind=_PATH_KINDS,
    source_segments=_BOUNDED_SEGMENTS,
    destination_segments=_BOUNDED_SEGMENTS,
    approval_state=_APPROVAL_STATES,
)
def test_adoption_is_target_confined_and_reference_sources_require_prior_approval(
    source_kind: str,
    destination_kind: str,
    source_segments: tuple[str, ...],
    destination_segments: tuple[str, ...],
    approval_state: str,
) -> None:
    with TemporaryDirectory() as temporary_directory:
        boundary, target, reference, outside = _boundary(Path(temporary_directory))
        source = _bounded_path(source_kind, target, reference, outside, source_segments)
        destination = _bounded_path(
            destination_kind, target, reference, outside, destination_segments
        )
        before = _snapshot(target, reference)
        permitted = destination_kind == "target" and (
            source_kind == "target" or (source_kind == "reference" and approval_state == "prior")
        )

        if permitted:
            assert boundary.authorize_adoption(
                source, destination, _approval_for(approval_state), requested_at=_REQUESTED_AT
            ) == (source.resolve(), destination.resolve())
        else:
            with pytest.raises(BoundaryViolationError):
                boundary.authorize_adoption(
                    source, destination, _approval_for(approval_state), requested_at=_REQUESTED_AT
                )

        assert _snapshot(target, reference) == before
