"""Property tests for architecture-decision governing authority."""

from __future__ import annotations

import string

import pytest
from hypothesis import given, settings, strategies as st

from app.core.decisions import ArchitectureDecision

_NON_BLANK_DECISION_TEXT = st.text(
    alphabet=string.ascii_letters + string.digits + " -_",
    min_size=1,
    max_size=100,
).filter(str.strip)


# Feature: generic-swarm-business-os, Property 1: Architecture decisions declare their authority
@settings(max_examples=100)
@given(title=_NON_BLANK_DECISION_TEXT, rationale=_NON_BLANK_DECISION_TEXT)
def test_architecture_decisions_declare_target_and_structure_authority(
    title: str, rationale: str
) -> None:
    """Every valid Host architecture decision declares the fixed governing authority.

    **Validates: Requirements 1.1**
    """
    rendered_decision = ArchitectureDecision(title=title, rationale=rationale).render()

    assert "- Target_Workspace: `C:\\Project\\common-agent-swarm-ops`" in rendered_decision
    assert (
        "- Structure_Contract: `C:\\Project\\common-agent-swarm-ops\\structure.md` (`structure.md`)"
    ) in rendered_decision


@pytest.mark.parametrize(
    ("title", "rationale"),
    [
        (" \t\n", "Valid rationale"),
        ("Valid title", "\t\n "),
    ],
)
def test_architecture_decision_rejects_whitespace_only_text(
    title: str, rationale: str
) -> None:
    """Whitespace-only titles and rationales are rejected deterministically."""
    with pytest.raises(ValueError, match="must not be empty"):
        ArchitectureDecision(title=title, rationale=rationale).render()
