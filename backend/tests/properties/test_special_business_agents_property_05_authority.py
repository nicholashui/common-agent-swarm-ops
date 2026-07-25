"""Property checks for governed authority escalation in the ``specials`` pack."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Final, Literal, cast

from hypothesis import example, given, settings, strategies as st

from app.registry.specials_validator import (
    SPECIAL_AGENT_IDS,
    SPECIAL_AGENT_SPEC_PATHS,
    SPECIAL_SOURCE_CATALOG,
    SPECIALS_APPROVAL_ROOT,
    SPECIALS_MANIFEST_PATH,
    SPECIALS_PACK_ROOT,
    SPECIALS_RISK_ASSESSMENT_ROOT,
    SPECIALS_SCHEMA_PATH,
    SPECIALS_SOURCE_RECORD_ROOT,
    AcceptedSpecialsState,
    ValidationReport,
    canonical_agent_spec_path,
    canonical_json_bytes,
    sha256_bytes,
    sha256_json,
    validate_specials_pack,
)

_REPOSITORY_ROOT: Final[Path] = Path(__file__).resolve().parents[3]
_SCHEMA_SOURCE_PATH: Final[Path] = (
    _REPOSITORY_ROOT / "business" / "specials" / "schemas" / "special-agent-spec.schema.json"
)

AuthorityKind = Literal[
    "non_empty_tools",
    "positive_tool_budget",
    "network_access",
    "non_local_provider",
    "non_draft_status",
    "production_request",
]


@dataclass(frozen=True, slots=True)
class AuthorityCase:
    """One authority-increasing mutation applied to one canonical agent."""

    kind: AuthorityKind
    target_index: int

    @property
    def agent_id(self) -> str:
        """Return the canonical target ID selected by the case."""
        return SPECIAL_AGENT_IDS[self.target_index]


@dataclass(frozen=True, slots=True)
class MutatedFixture:
    """Digest and paths for a changed specification and its renewed evidence."""

    allowlisted_paths: tuple[str, ...]
    configuration_digest: str
    source_record: dict[str, object]
    source_record_digest: str
    risk_path: str
    approval_path: str
    old_risk_path: str
    old_approval_path: str


@st.composite
def _authority_cases(draw: st.DrawFn) -> AuthorityCase:
    """Generate every authority-increasing mutation over the fixed catalog."""
    return AuthorityCase(
        kind=cast(
            AuthorityKind,
            draw(
                st.sampled_from(
                    (
                        "non_empty_tools",
                        "positive_tool_budget",
                        "network_access",
                        "non_local_provider",
                        "non_draft_status",
                        "production_request",
                    )
                )
            ),
        ),
        target_index=draw(st.integers(min_value=0, max_value=len(SPECIAL_AGENT_IDS) - 1)),
    )


def _agent_spec(agent_id: str) -> dict[str, object]:
    """Build one approved draft specification without reading source content."""
    agent_name = agent_id.removeprefix("specials.")
    return {
        "schema_version": "1.0",
        "agent_id": agent_id,
        "status": "draft",
        "role": f"Special_Agent authority fixture for {agent_name}.",
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
    """Build the exact 19-member draft manifest."""
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


def _source_bytes(agent_id: str) -> bytes:
    """Return opaque, deterministic source bytes for one provenance record."""
    return f"untrusted source fixture bytes for {agent_id}\n".encode()


def _source_record(
    agent_id: str,
    source_digest: str,
    configuration_digest: str,
    approval_id: str,
) -> dict[str, object]:
    """Build a complete source record bound to one specification digest."""
    entry = SPECIAL_SOURCE_CATALOG[SPECIAL_AGENT_IDS.index(agent_id)]
    return {
        "schema_version": "1.0",
        "source_path": entry.source_path,
        "source_sha256": source_digest,
        "agent_id": agent_id,
        "configuration_sha256": configuration_digest,
        "reviewed_at": "2025-01-01T00:00:00+00:00",
        "approval_id": approval_id,
    }


def _risk_assessment(
    configuration_digest: str,
    source_record_digest: str,
    case: AuthorityCase,
) -> dict[str, object]:
    """Build a complete assessment that records the generated request exactly."""
    external_effect_kind = {
        "non_empty_tools": "external-service",
        "positive_tool_budget": None,
        "network_access": "external-service",
        "non_local_provider": "external-service",
        "non_draft_status": "production-release",
        "production_request": "production-release",
    }[case.kind]
    requested_tool_authority: object = "none"
    if case.kind == "non_empty_tools":
        requested_tool_authority = ["specials-property-tool"]
    elif case.kind == "positive_tool_budget":
        requested_tool_authority = ["specials-property-budget"]

    potential_risks = {
        "sensitive_personal_data": False,
        "psychological_profiling_or_recommendation": False,
        "legal": False,
        "medical": False,
        "financial": False,
        "external_service": case.kind
        in {
            "non_empty_tools",
            "network_access",
            "non_local_provider",
        },
        "credential": False,
        "external_write": False,
        "production_release": case.kind in {"non_draft_status", "production_request"},
    }
    return {
        "schema_version": "1.0",
        "configuration_sha256": configuration_digest,
        "source_record_sha256": source_record_digest,
        "potential_risks": potential_risks,
        "external_effect_potential": (
            "none" if external_effect_kind is None else [external_effect_kind]
        ),
        "requested_tool_authority": requested_tool_authority,
        "requested_network_access": case.kind == "network_access",
        "requested_provider": ("remote_provider" if case.kind == "non_local_provider" else "none"),
        "requested_production_activation": case.kind == "production_request",
        "requested_lifecycle_state": ("registered" if case.kind == "non_draft_status" else "draft"),
    }


def _approval_record(
    agent_id: str,
    source_record: dict[str, object],
    source_record_digest: str,
    risk_assessment: dict[str, object],
) -> dict[str, object]:
    """Build a renewed approval whose scope covers every assessed request."""
    approved_scope = {
        key: value
        for key, value in risk_assessment.items()
        if key not in {"schema_version", "configuration_sha256", "source_record_sha256"}
    }
    return {
        "approval_id": source_record["approval_id"],
        "reviewer_identity": "human-authority-reviewer",
        "decision_timestamp": "2025-01-01T00:00:00+00:00",
        "decision": "approved",
        "source_path": source_record["source_path"],
        "source_sha256": source_record["source_sha256"],
        "agent_id": agent_id,
        "configuration_sha256": source_record["configuration_sha256"],
        "source_record_sha256": source_record_digest,
        "approved_risk_scope": approved_scope,
        "reason": "Approved renewed authority scope for validator-gate testing.",
    }


def _write_json(path: Path, value: object) -> None:
    """Write canonical UTF-8 JSON into a local fixture."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json_bytes(value) + b"\n")


def _read_object(path: Path) -> dict[str, object]:
    """Read one fixture object for a deliberate authority mutation."""
    value: object = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"Expected object fixture at {path}.")
    return cast(dict[str, object], value)


def _write_approved_fixture(root: Path) -> tuple[str, ...]:
    """Write a fully approved 19-agent draft pack and its governance evidence."""
    schema_path = root / SPECIALS_SCHEMA_PATH
    schema_path.parent.mkdir(parents=True, exist_ok=True)
    schema_path.write_bytes(_SCHEMA_SOURCE_PATH.read_bytes())
    _write_json(root / SPECIALS_MANIFEST_PATH, _manifest())

    allowlisted_paths: list[str] = [SPECIALS_SCHEMA_PATH, SPECIALS_MANIFEST_PATH]
    for agent_id, spec_path in zip(SPECIAL_AGENT_IDS, SPECIAL_AGENT_SPEC_PATHS, strict=True):
        specification = _agent_spec(agent_id)
        configuration_digest = sha256_json(specification)
        _write_json(
            root / f"{SPECIALS_PACK_ROOT}/{canonical_agent_spec_path(agent_id)}", specification
        )
        allowlisted_paths.append(spec_path)

        source_digest = sha256_bytes(_source_bytes(agent_id))
        approval_id = f"approval-{agent_id.removeprefix('specials.')}"
        source_record = _source_record(agent_id, source_digest, configuration_digest, approval_id)
        source_record_path = f"{SPECIALS_SOURCE_RECORD_ROOT}/{agent_id}.json"
        _write_json(root / source_record_path, source_record)
        allowlisted_paths.append(source_record_path)

        source_record_digest = sha256_json(source_record)
        baseline_case = AuthorityCase("positive_tool_budget", SPECIAL_AGENT_IDS.index(agent_id))
        risk = _risk_assessment(configuration_digest, source_record_digest, baseline_case)
        risk["external_effect_potential"] = "none"
        risk["requested_tool_authority"] = "none"
        risk["requested_network_access"] = False
        risk["requested_provider"] = "none"
        risk["requested_production_activation"] = False
        risk["requested_lifecycle_state"] = "draft"
        potential_risks = risk["potential_risks"]
        assert isinstance(potential_risks, dict)
        for risk_name in potential_risks:
            potential_risks[risk_name] = False
        risk_path = f"{SPECIALS_RISK_ASSESSMENT_ROOT}/{configuration_digest}.json"
        _write_json(root / risk_path, risk)
        allowlisted_paths.append(risk_path)

        approval = _approval_record(agent_id, source_record, source_record_digest, risk)
        approval_path = f"{SPECIALS_APPROVAL_ROOT}/{approval_id}.json"
        _write_json(root / approval_path, approval)
        allowlisted_paths.append(approval_path)

    return tuple(allowlisted_paths)


def _apply_authority_mutation(specification: dict[str, object], kind: AuthorityKind) -> None:
    """Apply exactly one immutable-profile violation to a specification."""
    if kind == "non_empty_tools":
        specification["allowed_tools"] = ["specials-property-tool"]
    elif kind == "positive_tool_budget":
        budget_policy = specification["budget_policy"]
        assert isinstance(budget_policy, dict)
        budget_policy["max_tool_requests"] = 1
    elif kind == "network_access":
        model_policy = specification["model_policy"]
        assert isinstance(model_policy, dict)
        model_policy["network_access"] = True
    elif kind == "non_local_provider":
        model_policy = specification["model_policy"]
        assert isinstance(model_policy, dict)
        model_policy["provider"] = "remote_provider"
    elif kind == "non_draft_status":
        specification["status"] = "registered"
    elif kind == "production_request":
        specification["production_activation_requested"] = True
    else:
        raise AssertionError(f"Unhandled authority mutation: {kind}")


def _mutate_fixture(
    root: Path,
    base_allowlisted_paths: tuple[str, ...],
    case: AuthorityCase,
) -> MutatedFixture:
    """Change one specification and point its source record at renewed evidence."""
    agent_id = case.agent_id
    specification_path = root / f"{SPECIALS_PACK_ROOT}/{canonical_agent_spec_path(agent_id)}"
    specification = _read_object(specification_path)
    old_configuration_digest = sha256_json(specification)
    _apply_authority_mutation(specification, case.kind)
    configuration_digest = sha256_json(specification)
    _write_json(specification_path, specification)

    source_record_path = root / f"{SPECIALS_SOURCE_RECORD_ROOT}/{agent_id}.json"
    source_record = _read_object(source_record_path)
    old_approval_id = source_record["approval_id"]
    assert isinstance(old_approval_id, str)
    old_risk_path = f"{SPECIALS_RISK_ASSESSMENT_ROOT}/{old_configuration_digest}.json"
    old_approval_path = f"{SPECIALS_APPROVAL_ROOT}/{old_approval_id}.json"
    source_record["configuration_sha256"] = configuration_digest
    source_record["approval_id"] = f"renewed-{case.kind}-{agent_id.removeprefix('specials.')}"
    _write_json(source_record_path, source_record)

    mutated_paths = list(base_allowlisted_paths)
    mutated_paths.remove(old_risk_path)
    mutated_paths.remove(old_approval_path)
    new_risk_path = f"{SPECIALS_RISK_ASSESSMENT_ROOT}/{configuration_digest}.json"
    new_approval_id = source_record["approval_id"]
    assert isinstance(new_approval_id, str)
    new_approval_path = f"{SPECIALS_APPROVAL_ROOT}/{new_approval_id}.json"
    source_record_digest = sha256_json(source_record)
    return MutatedFixture(
        tuple(mutated_paths),
        configuration_digest,
        source_record,
        source_record_digest,
        new_risk_path,
        new_approval_path,
        old_risk_path,
        old_approval_path,
    )


def _add_renewed_governance(
    root: Path,
    fixture: MutatedFixture,
    case: AuthorityCase,
) -> tuple[str, ...]:
    """Add the new digest-bound assessment and complete approval scope."""
    risk = _risk_assessment(fixture.configuration_digest, fixture.source_record_digest, case)
    _write_json(root / fixture.risk_path, risk)
    approval = _approval_record(
        case.agent_id,
        fixture.source_record,
        fixture.source_record_digest,
        risk,
    )
    _write_json(root / fixture.approval_path, approval)
    return (*fixture.allowlisted_paths, fixture.risk_path, fixture.approval_path)


def _finding_codes(report: ValidationReport) -> set[str]:
    """Return stable finding codes without coupling assertions to ordering."""
    findings = report.findings
    return {finding.code for finding in findings}


# Feature: special-business-agents, Property 5: Authority escalation requires renewed approval
# **Validates: Requirements 2.2-2.5, 5.1-5.6**
@settings(max_examples=100, derandomize=True, database=None, deadline=None)
@example(AuthorityCase("non_empty_tools", 0))
@example(AuthorityCase("positive_tool_budget", 0))
@example(AuthorityCase("network_access", 0))
@example(AuthorityCase("non_local_provider", 0))
@example(AuthorityCase("non_draft_status", 0))
@example(AuthorityCase("production_request", 0))
@given(case=_authority_cases())
def test_property_05_authority_escalation_requires_renewed_approval(
    case: AuthorityCase,
) -> None:
    """Renewed governance can pass only its gate; the immutable profile still rejects it."""
    with TemporaryDirectory() as temporary_directory:
        fixture_root = Path(temporary_directory)
        base_allowlisted_paths = _write_approved_fixture(fixture_root)
        baseline = validate_specials_pack(fixture_root, base_allowlisted_paths)

        assert baseline.validation_outcome == "pass"
        assert baseline.accepted_agent_ids == SPECIAL_AGENT_IDS
        assert baseline.provenance.result == "pass"
        assert baseline.risk_gate.result == "pass"
        prior_state: AcceptedSpecialsState = baseline.accepted_state
        assert prior_state.agent_ids == SPECIAL_AGENT_IDS

        mutated = _mutate_fixture(fixture_root, base_allowlisted_paths, case)
        without_renewed_evidence = validate_specials_pack(
            fixture_root,
            mutated.allowlisted_paths,
            previous_state=prior_state,
        )

        assert without_renewed_evidence.validation_outcome == "fail"
        assert without_renewed_evidence.risk_gate.result == "fail"
        assert "MISSING_RISK_ASSESSMENT" in _finding_codes(without_renewed_evidence)
        assert without_renewed_evidence.accepted_agent_ids == ()
        assert without_renewed_evidence.registration_effect == "none"
        assert without_renewed_evidence.accepted_state is prior_state

        renewed_allowlisted_paths = _add_renewed_governance(fixture_root, mutated, case)
        report = validate_specials_pack(
            fixture_root,
            renewed_allowlisted_paths,
            previous_state=prior_state,
        )

        assert report.validation_outcome == "fail"
        assert report.provenance.result == "pass"
        assert report.risk_gate.result == "pass"
        assert report.accepted_agent_ids == ()
        assert report.rejected_agent_ids == SPECIAL_AGENT_IDS
        assert report.registration_effect == "none"
        assert report.accepted_state is prior_state
        assert report.accepted_state == prior_state
        assert report.findings

        expected_profile_code = {
            "non_empty_tools": "TOOLS_NOT_EMPTY",
            "positive_tool_budget": "TOOL_REQUESTS_NOT_ZERO",
            "network_access": "NETWORK_ACCESS_ENABLED",
            "non_local_provider": "INVALID_PROVIDER",
            "non_draft_status": "INVALID_STATUS",
            "production_request": "PRODUCTION_ACTIVATION_REQUESTED",
        }[case.kind]
        assert expected_profile_code in _finding_codes(report)
        assert mutated.risk_path != mutated.old_risk_path
        assert mutated.approval_path != mutated.old_approval_path
