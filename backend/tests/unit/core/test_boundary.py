"""Focused fail-closed workspace-boundary unit tests."""

from pathlib import Path

import pytest

from app.core.boundary import WorkspaceBoundary
from app.core.errors import AdoptionAuthorizationError, BoundaryErrorCode, BoundaryViolationError


def _boundary(tmp_path: Path) -> tuple[WorkspaceBoundary, Path, Path]:
    target, reference = tmp_path / "target", tmp_path / "reference"
    target.mkdir()
    reference.mkdir()
    return WorkspaceBoundary(target, reference), target, reference


def test_path_traversal_write_is_refused_without_creating_an_outside_file(tmp_path: Path) -> None:
    """Traversal outside the target root is rejected before any filesystem mutation."""
    boundary, target, _ = _boundary(tmp_path)
    escaped_path = target / ".." / "outside" / "request.json"

    with pytest.raises(BoundaryViolationError) as error:
        boundary.authorize_write(escaped_path)

    assert error.value.code is BoundaryErrorCode.OUTSIDE_TARGET_WORKSPACE
    assert not (tmp_path / "outside" / "request.json").exists()


def test_unapproved_reference_adoption_leaves_source_and_destination_unchanged(
    tmp_path: Path,
) -> None:
    """An adoption refusal resolves paths only and does not copy reference material."""
    boundary, target, reference = _boundary(tmp_path)
    source = reference / "candidate.json"
    destination = target / "adopted.json"
    source.write_text('{"origin": "reference"}', encoding="utf-8")

    with pytest.raises(AdoptionAuthorizationError):
        boundary.authorize_adoption(source, destination, approval=None)

    assert source.read_text(encoding="utf-8") == '{"origin": "reference"}'
    assert not destination.exists()


def test_boundary_refusal_redacts_the_untrusted_requested_path(tmp_path: Path) -> None:
    """Public error details expose a stable reason without disclosing a rejected path."""
    boundary, _, _ = _boundary(tmp_path)
    secret_path = tmp_path / "credentials-super-secret.txt"

    with pytest.raises(BoundaryViolationError) as error:
        boundary.authorize_write(secret_path)

    assert error.value.to_public_detail() == {
        "code": BoundaryErrorCode.OUTSIDE_TARGET_WORKSPACE,
        "message": "The requested operation is outside the target workspace.",
    }
    assert str(secret_path) not in str(error.value.to_public_detail())
