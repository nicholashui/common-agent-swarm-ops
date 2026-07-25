"""Property checks for the Special_Agent schema and least-privilege profile."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory

from hypothesis import given, settings, strategies as st

from app.registry.specials_validator import (
    SPECIAL_AGENT_IDS,
    SPECIALS_MANIFEST_PATH,
    SPECIALS_PACK_ROOT,
    SPECIALS_SCHEMA_PATH,
    AcceptedSpecialsState,
    ValidationReport,
    canonical_agent_spec_path,
    canonical_json_bytes,
    validate_specials_pack,
)
from tests.fakes.specials_governance import materialize_specials_governance

_REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
_INVALID_CANONICAL_IDS = (
    "spagent.not-an-agent",
    "specials.",
    "specials.Bad-Agent",
    "specials.agent_name",
    "other.agent",
    "specials.agent/escape",
)
_INVALID_ASSET_IDS = (
    "specials.not-an-asset",
    "spagent.",
    "spagent.Bad-Asset",
    "asset-reference",
    "spagent.asset_name",
    "spagent.asset/escape",
)
_AUTHORITY_MUTATIONS = (
    ("status", "registered", "INVALID_STATUS"),
    ("allowed_tools", ["tool.example"], "TOOLS_NOT_EMPTY"),
    ("max_tool_requests", 1, "TOOL_REQUESTS_NOT_ZERO"),
    ("provider", "remote_provider", "INVALID_PROVIDER"),
    ("network_access", True, "NETWORK_ACCESS_ENABLED"),
    (
        "production_activation_requested",
        True,
        "PRODUCTION_ACTIVATION_REQUESTED",
    ),
)


@dataclass(frozen=True, slots=True)
class _ProfileCase:
    """One generated valid profile or one deliberately invalid mutation."""

    mutation: str
    target_agent_id: str
    value: object | None = None
    asset_field: str | None = None
    expected_code: str | None = None


@st.composite
def _profile_cases(draw: st.DrawFn) -> _ProfileCase:
    """Generate valid specs and each required schema/profile violation class."""
    target_agent_id = draw(st.sampled_from(SPECIAL_AGENT_IDS))
    mutation = draw(
        st.sampled_from(
            (
                "valid",
                "canonical_id",
                "asset_id",
                "unsupported_field",
                "duplicate_tools",
                "authority",
            )
        )
    )
    if mutation == "valid":
        return _ProfileCase(mutation, target_agent_id)
    if mutation == "canonical_id":
        return _ProfileCase(
            mutation,
            target_agent_id,
            value=draw(st.sampled_from(_INVALID_CANONICAL_IDS)),
            expected_code="AGENT_ID_PATH_MISMATCH",
        )
    if mutation == "asset_id":
        return _ProfileCase(
            mutation,
            target_agent_id,
            value=draw(st.sampled_from(_INVALID_ASSET_IDS)),
            asset_field=draw(
                st.sampled_from(
                    ("prompt_reference", "rubric_reference", "critique_inputs", "critique_outputs")
                )
            ),
        )
    if mutation == "unsupported_field":
        return _ProfileCase(mutation, target_agent_id, value="untrusted_instruction")
    if mutation == "duplicate_tools":
        return _ProfileCase(mutation, target_agent_id)

    authority_field, authority_value, expected_code = draw(st.sampled_from(_AUTHORITY_MUTATIONS))
    return _ProfileCase(
        mutation,
        target_agent_id,
        value=authority_value,
        asset_field=authority_field,
        expected_code=expected_code,
    )


def _base_specification(agent_id: str) -> dict[str, object]:
    """Build one profile-valid specification using the pack-local asset namespace."""
    agent_name = agent_id.removeprefix("specials.")
    return {
        "schema_version": "1.0",
        "agent_id": agent_id,
        "status": "draft",
        "role": "Special_Agent data-only configuration",
        "allowed_tools": [],
        "model_policy": {
            "provider": "local_deterministic",
            "model_id": "specials-local-deterministic-v1",
            "network_access": False,
        },
        "budget_policy": {
            "max_input_tokens": 1,
            "max_output_tokens": 1,
            "max_tool_requests": 0,
        },
        "prompt_reference": f"spagent.{agent_name}-prompt",
        "rubric_reference": f"spagent.{agent_name}-rubric",
        "critique_edges": {
            "inputs": [f"spagent.{agent_name}-input"],
            "outputs": [f"spagent.{agent_name}-output"],
        },
        "max_refinement_count": 1,
        "production_activation_requested": False,
    }


def _manifest() -> dict[str, object]:
    """Build the exact local draft manifest required by the validator."""
    return {
        "pack_id": "specials",
        "agents": [
            {
                "agent_id": agent_id,
                "status": "draft",
                "allowed_tools": [],
                "production_activation_requested": False,
                "agent_spec_path": canonical_agent_spec_path(agent_id),
            }
            for agent_id in SPECIAL_AGENT_IDS
        ],
        "production_activation_requested": False,
        "inventory_required": False,
    }


def _write_json(path: Path, value: object) -> None:
    """Write deterministic UTF-8 JSON into a temporary local fixture."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json_bytes(value) + b"\n")


def _write_fixture(root: Path, case: _ProfileCase) -> tuple[str, ...]:
    """Write a complete 19-agent fixture and apply one generated mutation."""
    schema_source = _REPOSITORY_ROOT / SPECIALS_SCHEMA_PATH
    schema_path = root / SPECIALS_SCHEMA_PATH
    schema_path.parent.mkdir(parents=True, exist_ok=True)
    schema_path.write_bytes(schema_source.read_bytes())

    _write_json(root / SPECIALS_MANIFEST_PATH, _manifest())
    allowlisted_paths = [SPECIALS_SCHEMA_PATH, SPECIALS_MANIFEST_PATH]
    for agent_id in SPECIAL_AGENT_IDS:
        specification = _base_specification(agent_id)
        if agent_id == case.target_agent_id:
            _apply_mutation(specification, case)
        relative_path = f"{SPECIALS_PACK_ROOT}/{canonical_agent_spec_path(agent_id)}"
        _write_json(root / relative_path, specification)
        allowlisted_paths.append(relative_path)
    return materialize_specials_governance(root, allowlisted_paths)


def _apply_mutation(specification: dict[str, object], case: _ProfileCase) -> None:
    """Apply one schema, namespace, duplicate, or authority mutation."""
    if case.mutation == "canonical_id":
        specification["agent_id"] = case.value
    elif case.mutation == "asset_id":
        assert isinstance(case.value, str)
        assert case.asset_field is not None
        if case.asset_field in {"prompt_reference", "rubric_reference"}:
            specification[case.asset_field] = case.value
        else:
            critique_edges = specification["critique_edges"]
            assert isinstance(critique_edges, dict)
            edge_name = "inputs" if case.asset_field == "critique_inputs" else "outputs"
            critique_edges[edge_name] = [case.value]
    elif case.mutation == "unsupported_field":
        specification["unsupported_field"] = case.value
    elif case.mutation == "duplicate_tools":
        specification["allowed_tools"] = ["duplicate-tool", "duplicate-tool"]
    elif case.mutation == "authority":
        assert case.asset_field is not None
        if case.asset_field == "status":
            specification["status"] = case.value
        elif case.asset_field == "allowed_tools":
            specification["allowed_tools"] = case.value
        elif case.asset_field == "max_tool_requests":
            budget_policy = specification["budget_policy"]
            assert isinstance(budget_policy, dict)
            budget_policy["max_tool_requests"] = case.value
        elif case.asset_field == "provider":
            model_policy = specification["model_policy"]
            assert isinstance(model_policy, dict)
            model_policy["provider"] = case.value
        elif case.asset_field == "network_access":
            model_policy = specification["model_policy"]
            assert isinstance(model_policy, dict)
            model_policy["network_access"] = case.value
        elif case.asset_field == "production_activation_requested":
            specification["production_activation_requested"] = case.value
        else:
            raise AssertionError(f"Unhandled authority mutation: {case.asset_field}")
    elif case.mutation != "valid":
        raise AssertionError(f"Unhandled profile mutation: {case.mutation}")


def _finding_codes(report: ValidationReport) -> set[str]:
    """Return stable finding codes without coupling assertions to ordering."""
    findings = report.findings
    return {finding.code for finding in findings}


# Feature: special-business-agents, Property 2: Schema, asset namespace, and least-privilege closure
# **Validates: Requirements 2.1-2.5**
@settings(max_examples=100, derandomize=True, database=None, deadline=None)
@given(profile_case=_profile_cases())
def test_property_2_schema_and_least_privilege_closure(profile_case: _ProfileCase) -> None:
    """Valid drafts pass, while every generated unsafe profile mutation is fail-closed."""
    with TemporaryDirectory() as temporary_directory:
        fixture_root = Path(temporary_directory)
        allowlisted_paths = _write_fixture(
            fixture_root, _ProfileCase("valid", profile_case.target_agent_id)
        )
        baseline = validate_specials_pack(fixture_root, allowlisted_paths)

        assert baseline.validation_outcome == "pass"
        assert baseline.accepted_agent_ids == SPECIAL_AGENT_IDS
        assert baseline.registration_effect == "eligible_draft_representation"
        prior_state: AcceptedSpecialsState = baseline.accepted_state
        assert prior_state.agent_ids == SPECIAL_AGENT_IDS

        if profile_case.mutation == "valid":
            return

        _write_fixture(fixture_root, profile_case)
        rejected = validate_specials_pack(
            fixture_root, allowlisted_paths, previous_state=prior_state
        )

        assert rejected.validation_outcome == "fail"
        assert rejected.accepted_agent_ids == ()
        assert rejected.registration_effect == "none"
        assert rejected.accepted_state == prior_state
        assert rejected.rejected_agent_ids == SPECIAL_AGENT_IDS

        finding_codes = _finding_codes(rejected)
        if profile_case.mutation == "canonical_id":
            assert (
                profile_case.expected_code in finding_codes
                or "NAMESPACE_CROSSOVER" in finding_codes
            )
        elif profile_case.mutation == "asset_id":
            assert {"INVALID_ASSET_ID", "NAMESPACE_CROSSOVER"} & finding_codes
        elif profile_case.mutation == "unsupported_field":
            assert "UNSUPPORTED_FIELD" in finding_codes
        elif profile_case.mutation == "duplicate_tools":
            assert {"TOOLS_NOT_EMPTY", "DUPLICATE_ALLOWED_TOOL"} <= finding_codes
        else:
            assert profile_case.expected_code in finding_codes
