"""Scaffold-level package checks."""

from app import __version__


def test_host_package_has_deterministic_version() -> None:
    """The foundation package exposes one stable local version."""
    assert __version__ == "0.1.0"
