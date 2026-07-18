"""Rendering for architecture decisions governed by the target contract."""

from __future__ import annotations

from dataclasses import dataclass

TARGET_WORKSPACE = r"C:\Project\common-agent-swarm-ops"
STRUCTURE_CONTRACT = rf"{TARGET_WORKSPACE}\structure.md"


@dataclass(frozen=True, slots=True)
class ArchitectureDecision:
    """A host architecture decision with non-overridable governing authority."""

    title: str
    rationale: str

    def render(self) -> str:
        """Render this decision with the required workspace and contract identity."""
        return render_architecture_decision(self.title, self.rationale)


def render_architecture_decision(title: str, rationale: str) -> str:
    """Render an architecture decision that declares its authoritative contract."""
    normalized_title = title.strip()
    normalized_rationale = rationale.strip()
    if not normalized_title:
        raise ValueError("Architecture decision title must not be empty.")
    if not normalized_rationale:
        raise ValueError("Architecture decision rationale must not be empty.")

    return "\n".join(
        (
            f"# Architecture Decision: {normalized_title}",
            "",
            "## Rationale",
            normalized_rationale,
            "",
            "## Governing Authority",
            f"- Target_Workspace: `{TARGET_WORKSPACE}`",
            f"- Structure_Contract: `{STRUCTURE_CONTRACT}` (`structure.md`)",
        )
    )
