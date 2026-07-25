"""Property checks for executable migration completion gates."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from hypothesis import example, given, settings, strategies as st

from app.video.migration.contracts import MigrationResult
from app.video.migration.evidence import (
    BLOCKING_CATEGORIES,
    REQUIRED_COMPLETION_GATES,
    CompletionClaim,
    ExecutableGateResult,
    evaluate_completion,
    validate_completion_claim,
)

_REQUIRED_GATES: Final[tuple[str, ...]] = REQUIRED_COMPLETION_GATES
_EVIDENCE_REFS: Final[tuple[str, ...]] = tuple(
    f"property-13-evidence-{index}" for index in range(len(_REQUIRED_GATES))
)
_BLOCKER_EXAMPLES: Final[tuple[str, ...]] = (
    "licensing uncertainty remains",
    "unreviewed semantic mapping remains",
    "incomplete workflow adaptation remains",
    "security finding remains",
    "standalone verification failed",
)
_CLAIM_MUTATIONS: Final[tuple[str, ...]] = (
    "documentation_only_with_evidence",
    "missing_evidence",
    "unknown_evidence",
)


@dataclass(frozen=True, slots=True)
class CompletionGateVector:
    """Bounded executable attributes for every required release gate."""

    results: tuple[bool, ...]
    executable: tuple[bool, ...]
    evidenced: tuple[bool, ...]
    blockers: tuple[bool, ...]

    @property
    def expects_completion(self) -> bool:
        """Return the conjunction required by an executable completion decision."""
        return all(
            result and executable and evidenced and not blocker
            for result, executable, evidenced, blocker in zip(
                self.results,
                self.executable,
                self.evidenced,
                self.blockers,
                strict=True,
            )
        )


@st.composite
def _completion_gate_vectors(draw: st.DrawFn) -> CompletionGateVector:
    """Generate small evidence vectors while retaining every required gate."""
    return CompletionGateVector(
        results=tuple(draw(st.booleans()) for _ in _REQUIRED_GATES),
        executable=tuple(draw(st.booleans()) for _ in _REQUIRED_GATES),
        evidenced=tuple(draw(st.booleans()) for _ in _REQUIRED_GATES),
        blockers=tuple(draw(st.booleans()) for _ in _REQUIRED_GATES),
    )


@st.composite
def _blocker_combinations(draw: st.DrawFn) -> tuple[str, ...]:
    """Generate bounded combinations of the five completion-blocking categories."""
    selected = draw(
        st.sets(
            st.sampled_from(_BLOCKER_EXAMPLES),
            min_size=0,
            max_size=len(_BLOCKER_EXAMPLES),
        )
    )
    return tuple(sorted(selected))


def _gates_for(vector: CompletionGateVector) -> dict[str, ExecutableGateResult]:
    """Build typed gate records from one generated vector."""
    gates: dict[str, ExecutableGateResult] = {}
    for index, gate_name in enumerate(_REQUIRED_GATES):
        gates[gate_name] = ExecutableGateResult(
            gate=gate_name,
            result=MigrationResult.PASS if vector.results[index] else MigrationResult.FAIL,
            evidence_ref=_EVIDENCE_REFS[index] if vector.evidenced[index] else "",
            executable=vector.executable[index],
            blockers=(f"property-13-{gate_name}-blocker",) if vector.blockers[index] else (),
        )
    return gates


def _passing_gates() -> dict[str, ExecutableGateResult]:
    """Return a complete vector with one executable result for each gate."""
    return _gates_for(
        CompletionGateVector(
            results=(True,) * len(_REQUIRED_GATES),
            executable=(True,) * len(_REQUIRED_GATES),
            evidenced=(True,) * len(_REQUIRED_GATES),
            blockers=(False,) * len(_REQUIRED_GATES),
        )
    )


# Feature: migration-redesign, Property 13: Completion is a conjunction of
# executable release gates.
# **Validates: Requirements 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7, 9.8, 9.9,
# 9.13, 9.14**
@settings(max_examples=32, deadline=None, derandomize=True)
@example(
    CompletionGateVector(
        results=(True,) * len(_REQUIRED_GATES),
        executable=(True,) * len(_REQUIRED_GATES),
        evidenced=(True,) * len(_REQUIRED_GATES),
        blockers=(False,) * len(_REQUIRED_GATES),
    )
)
@example(
    CompletionGateVector(
        results=(False,) + (True,) * (len(_REQUIRED_GATES) - 1),
        executable=(True,) * len(_REQUIRED_GATES),
        evidenced=(True,) * len(_REQUIRED_GATES),
        blockers=(False,) * len(_REQUIRED_GATES),
    )
)
@example(
    CompletionGateVector(
        results=(True,) * len(_REQUIRED_GATES),
        executable=(True,) * len(_REQUIRED_GATES),
        evidenced=(True,) * len(_REQUIRED_GATES),
        blockers=(True,) + (False,) * (len(_REQUIRED_GATES) - 1),
    )
)
@given(vector=_completion_gate_vectors())
def test_property_13_completion_requires_every_executable_evidenced_gate(
    vector: CompletionGateVector,
) -> None:
    """Completion passes exactly when every required gate satisfies its contract."""
    report = evaluate_completion(_gates_for(vector))
    repeat = evaluate_completion(_gates_for(vector))

    assert report.missing_gates == ()
    assert report.is_complete is vector.expects_completion
    assert report.completion_gate_passed is vector.expects_completion
    assert report.result is (
        MigrationResult.PASS if vector.expects_completion else MigrationResult.BLOCKED
    )
    assert report.runtime_activation_changed is False
    assert report.canonical_json() == repeat.canonical_json()

    expected_failed = {
        gate_name
        for index, gate_name in enumerate(_REQUIRED_GATES)
        if not (
            vector.results[index]
            and vector.executable[index]
            and vector.evidenced[index]
            and not vector.blockers[index]
        )
    }
    assert set(report.failed_gates) == expected_failed


@settings(max_examples=24, deadline=None, derandomize=True)
@example(())
@example(_BLOCKER_EXAMPLES)
@example((_BLOCKER_EXAMPLES[0], _BLOCKER_EXAMPLES[2]))
@given(blockers=_blocker_combinations())
def test_property_13_known_blocker_combinations_always_block_completion(
    blockers: tuple[str, ...],
) -> None:
    """Unresolved licensing, mapping, workflow, security, or standalone blockers remain blocking."""
    report = evaluate_completion(_passing_gates(), blockers=blockers)

    expected_blocker_codes = {
        f"completion_blocker_{category}"
        for category in BLOCKING_CATEGORIES
        if any(category in blocker.casefold() for blocker in blockers)
    }
    actual_codes = {finding.code for finding in report.findings}

    assert report.blockers == blockers
    assert report.is_complete is not bool(blockers)
    assert report.result is (MigrationResult.PASS if not blockers else MigrationResult.BLOCKED)
    assert expected_blocker_codes <= actual_codes
    assert (
        report.canonical_json()
        == evaluate_completion(_passing_gates(), blockers=blockers).canonical_json()
    )


def _claim_for_mutation(mutation: str) -> CompletionClaim:
    """Build one explicit invalid completion claim shape."""
    if mutation == "documentation_only_with_evidence":
        return CompletionClaim(
            claim_id="property-13-prose-only",
            statement="Migration completion is established by documentation prose.",
            executable_evidence=(_EVIDENCE_REFS[0],),
            documentation_only=True,
        )
    if mutation == "missing_evidence":
        return CompletionClaim(
            claim_id="property-13-no-evidence",
            statement="Migration completion is asserted without executable evidence.",
        )
    if mutation == "unknown_evidence":
        return CompletionClaim(
            claim_id="property-13-unknown-evidence",
            statement="Migration completion cites an unretained result.",
            executable_evidence=("property-13-unretained-prose",),
        )
    raise AssertionError(f"Unhandled completion claim mutation: {mutation}")


@settings(max_examples=12, deadline=None, derandomize=True)
@example("documentation_only_with_evidence")
@example("missing_evidence")
@example("unknown_evidence")
@given(mutation=st.sampled_from(_CLAIM_MUTATIONS))
def test_property_13_prose_only_or_unretained_claims_cannot_complete(
    mutation: str,
) -> None:
    """A claim must name retained executable evidence and cannot rely on prose alone."""
    claim = _claim_for_mutation(mutation)
    available_evidence = _EVIDENCE_REFS

    claim_report = validate_completion_claim(claim, available_evidence)
    completion_report = evaluate_completion(
        _passing_gates(),
        completion_claim=claim,
    )

    assert not claim_report.is_valid
    assert claim_report.result is MigrationResult.BLOCKED
    assert not completion_report.is_complete
    assert completion_report.result is MigrationResult.BLOCKED
    assert completion_report.claim is not None
    assert not completion_report.claim.is_valid

    claim_codes = {finding.code for finding in claim_report.findings}
    completion_codes = {finding.code for finding in completion_report.findings}
    if mutation == "documentation_only_with_evidence":
        assert "completion_claim_documentation_only" in claim_codes
    elif mutation == "missing_evidence":
        assert "completion_claim_requires_executable_evidence" in claim_codes
    else:
        assert "completion_claim_unknown_evidence" in claim_codes
    assert claim_codes <= completion_codes
