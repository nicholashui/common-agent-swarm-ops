"""Property checks for fail-closed Special_Agent provenance and approval gates."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Final, Literal, cast

from hypothesis import given, settings, strategies as st

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
    sha256_text,
    validate_specials_pack,
)

_REPOSITORY_ROOT: Final[Path] = Path(__file__).resolve().parents[3]
_SCHEMA_SOURCE_PATH: Final[Path] = (
    _REPOSITORY_ROOT / "business" / "specials" / "schemas" / "special-agent-spec.schema.json"
)

Availability = Literal["absent", "present", "unreadable"]
SourcePathMode = Literal["valid", "other_inventory", "traversal", "absolute"]
SourceDigestMode = Literal["matching", "drift", "malformed"]
ConfigurationDigestMode = Literal["matching", "mismatch", "malformed"]
ApprovalState = Literal["valid", "missing", "source_mismatch", "rejected"]


@dataclass(frozen=True, slots=True)
class ProvenanceCase:
    """One generated source, digest, availability, or approval mutation."""

    target_index: int
    source_path_mode: SourcePathMode
    source_digest_mode: SourceDigestMode
    configuration_digest_mode: ConfigurationDigestMode
    availability: Availability
    approval_state: ApprovalState
    manual_revalidation: bool


@st.composite
def _provenance_cases(draw: st.DrawFn) -> ProvenanceCase:
    """Generate valid and invalid provenance states across the fixed catalog."""
    availability = draw(st.sampled_from(("absent", "present", "unreadable")))
    if availability == "present":
        source_digest_mode = draw(st.sampled_from(("matching", "drift", "malformed")))
    else:
        source_digest_mode = draw(st.sampled_from(("matching", "malformed")))
    return ProvenanceCase(
        target_index=draw(st.integers(min_value=0, max_value=len(SPECIAL_AGENT_IDS) - 1)),
        source_path_mode=cast(
            SourcePathMode,
            draw(st.sampled_from(("valid", "other_inventory", "traversal", "absolute"))),
        ),
        source_digest_mode=cast(SourceDigestMode, source_digest_mode),
        configuration_digest_mode=cast(
            ConfigurationDigestMode,
            draw(st.sampled_from(("matching", "mismatch", "malformed"))),
        ),
        availability=cast(Availability, availability),
        approval_state=cast(
            ApprovalState,
            draw(st.sampled_from(("valid", "missing", "source_mismatch", "rejected"))),
        ),
        manual_revalidation=draw(st.booleans()),
    )


def _agent_spec(agent_id: str) -> dict[str, object]:
    """Build one valid immutable-profile specification without source ingestion."""
    agent_name = agent_id.removeprefix("specials.")
    return {
        "schema_version": "1.0",
        "agent_id": agent_id,
        "status": "draft",
        "role": f"Special_Agent provenance fixture for {agent_name}.",
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
    """Build the exact 19-member draft manifest for every provenance case."""
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
    """Return deterministic opaque bytes for one local source fixture."""
    return f"untrusted source fixture bytes for {agent_id}\n".encode()


def _source_record(
    agent_id: str,
    source_digest: str,
    configuration_digest: str,
) -> dict[str, object]:
    """Build one complete Source_Record bound to its specification digest."""
    agent_name = agent_id.removeprefix("specials.")
    entry = SPECIAL_SOURCE_CATALOG[SPECIAL_AGENT_IDS.index(agent_id)]
    return {
        "schema_version": "1.0",
        "source_path": entry.source_path,
        "source_sha256": source_digest,
        "agent_id": agent_id,
        "configuration_sha256": configuration_digest,
        "reviewed_at": "2025-01-01T00:00:00+00:00",
        "approval_id": f"approval-{agent_name}",
    }


def _risk_assessment(configuration_digest: str, source_record_digest: str) -> dict[str, object]:
    """Build a no-authority Risk_Assessment with every required field explicit."""
    return {
        "schema_version": "1.0",
        "configuration_sha256": configuration_digest,
        "source_record_sha256": source_record_digest,
        "potential_risks": {
            "sensitive_personal_data": False,
            "psychological_profiling_or_recommendation": False,
            "legal": False,
            "medical": False,
            "financial": False,
            "external_service": False,
            "credential": False,
            "external_write": False,
            "production_release": False,
        },
        "external_effect_potential": "none",
        "requested_tool_authority": "none",
        "requested_network_access": False,
        "requested_provider": "none",
        "requested_production_activation": False,
        "requested_lifecycle_state": "draft",
    }


def _approval_record(
    agent_id: str,
    source_record: dict[str, object],
    source_record_digest: str,
) -> dict[str, object]:
    """Build a matching human approval whose scope grants no authority."""
    return {
        "approval_id": source_record["approval_id"],
        "reviewer_identity": "human-provenance-reviewer",
        "decision_timestamp": "2025-01-01T00:00:00+00:00",
        "decision": "approved",
        "source_path": source_record["source_path"],
        "source_sha256": source_record["source_sha256"],
        "agent_id": agent_id,
        "configuration_sha256": source_record["configuration_sha256"],
        "source_record_sha256": source_record_digest,
        "approved_risk_scope": {
            "potential_risks": {
                "sensitive_personal_data": False,
                "psychological_profiling_or_recommendation": False,
                "legal": False,
                "medical": False,
                "financial": False,
                "external_service": False,
                "credential": False,
                "external_write": False,
                "production_release": False,
            },
            "external_effect_potential": "none",
            "requested_tool_authority": "none",
            "requested_network_access": False,
            "requested_provider": "none",
            "requested_production_activation": False,
            "requested_lifecycle_state": "draft",
        },
        "reason": "Approved data-only provenance evidence.",
    }


def _write_json(path: Path, value: object) -> None:
    """Write canonical UTF-8 JSON into a local temporary fixture."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json_bytes(value) + b"\n")


def _write_valid_fixture(root: Path) -> tuple[str, ...]:
    """Write an exact 19-agent pack with checked-in governance evidence."""
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
        source_record = _source_record(agent_id, source_digest, configuration_digest)
        source_record_path = f"{SPECIALS_SOURCE_RECORD_ROOT}/{agent_id}.json"
        _write_json(root / source_record_path, source_record)
        allowlisted_paths.append(source_record_path)

        source_record_digest = sha256_json(source_record)
        risk_assessment = _risk_assessment(configuration_digest, source_record_digest)
        risk_path = f"{SPECIALS_RISK_ASSESSMENT_ROOT}/{configuration_digest}.json"
        _write_json(root / risk_path, risk_assessment)
        allowlisted_paths.append(risk_path)

        approval = _approval_record(agent_id, source_record, source_record_digest)
        approval_path = f"{SPECIALS_APPROVAL_ROOT}/{source_record['approval_id']}.json"
        _write_json(root / approval_path, approval)
        allowlisted_paths.append(approval_path)

    return tuple(allowlisted_paths)


def _read_object(path: Path) -> dict[str, object]:
    """Read a local fixture object for one deliberate provenance mutation."""
    value: object = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"Expected object fixture at {path}.")
    return cast(dict[str, object], value)


def _target_source_path(case: ProvenanceCase, root: Path) -> str:
    """Return the generated normalized or invalid source-path variant."""
    entry = SPECIAL_SOURCE_CATALOG[case.target_index]
    if case.source_path_mode == "valid":
        return entry.source_path
    if case.source_path_mode == "other_inventory":
        return SPECIAL_SOURCE_CATALOG[
            (case.target_index + 1) % len(SPECIAL_SOURCE_CATALOG)
        ].source_path
    if case.source_path_mode == "traversal":
        return f"{SPECIALS_SOURCE_RECORD_ROOT}/../{entry.source_path.rsplit('/', 1)[-1]}"
    return str(root / "outside-source.md")


def _mutate_fixture(
    root: Path,
    allowlisted_paths: tuple[str, ...],
    case: ProvenanceCase,
) -> tuple[str, ...]:
    """Apply exactly one generated provenance/approval/availability mutation."""
    agent_id = SPECIAL_AGENT_IDS[case.target_index]
    entry = SPECIAL_SOURCE_CATALOG[case.target_index]
    source_record_path = root / f"{SPECIALS_SOURCE_RECORD_ROOT}/{agent_id}.json"
    source_record = _read_object(source_record_path)
    if case.source_path_mode != "valid":
        source_record["source_path"] = _target_source_path(case, root)

    baseline_source_digest = sha256_bytes(_source_bytes(agent_id))
    if case.source_digest_mode == "malformed":
        source_record["source_sha256"] = "A" * 64
    else:
        source_record["source_sha256"] = baseline_source_digest

    if case.configuration_digest_mode == "mismatch":
        source_record["configuration_sha256"] = sha256_text("different configuration evidence")
    elif case.configuration_digest_mode == "malformed":
        source_record["configuration_sha256"] = "not-a-sha256-digest"
    _write_json(source_record_path, source_record)

    approval_path = root / f"{SPECIALS_APPROVAL_ROOT}/{source_record['approval_id']}.json"
    if case.approval_state == "source_mismatch":
        approval = _read_object(approval_path)
        approval["source_sha256"] = sha256_text("approval bound to another source")
        _write_json(approval_path, approval)
    elif case.approval_state == "rejected":
        approval = _read_object(approval_path)
        approval["decision"] = "rejected"
        _write_json(approval_path, approval)

    source_path = root / entry.source_path
    mutated_allowlist = list(allowlisted_paths)
    if case.availability == "present":
        source_path.parent.mkdir(parents=True, exist_ok=True)
        source_bytes = _source_bytes(agent_id)
        if case.source_digest_mode == "drift":
            source_bytes += b"source changed after approval\n"
        source_path.write_bytes(source_bytes)
        mutated_allowlist.append(entry.source_path)
    elif case.availability == "unreadable":
        source_path.mkdir(parents=True, exist_ok=True)
        mutated_allowlist.append(entry.source_path)

    if case.approval_state == "missing":
        expected_approval_path = f"{SPECIALS_APPROVAL_ROOT}/{source_record['approval_id']}.json"
        mutated_allowlist.remove(expected_approval_path)
    return tuple(mutated_allowlist)


def _previous_state() -> AcceptedSpecialsState:
    """Return a sentinel accepted state to prove rejected proposals are retained."""
    return AcceptedSpecialsState(
        agents=tuple(),
        validation_report_digest="prior-accepted-provenance-state",
    )


def _finding_codes(report: ValidationReport) -> set[str]:
    """Return stable finding codes without coupling assertions to ordering."""
    findings = report.findings
    return {finding.code for finding in findings}


# Feature: special-business-agents, Property 4: Provenance invalidation is fail-closed
# **Validates: Requirements 4.1-4.6, 5.3-5.6**
@settings(max_examples=100, derandomize=True, database=None, deadline=None)
@given(case=_provenance_cases())
def test_property_04_provenance_invalidation_is_fail_closed(case: ProvenanceCase) -> None:
    """Digest drift is retained only before manual revalidation; all other gates fail closed."""
    with TemporaryDirectory() as temporary_directory:
        fixture_root = Path(temporary_directory)
        base_allowlist = _write_valid_fixture(fixture_root)
        baseline = validate_specials_pack(fixture_root, base_allowlist)

        assert baseline.validation_outcome == "pass"
        assert baseline.accepted_agent_ids == SPECIAL_AGENT_IDS
        assert baseline.provenance.result == "pass"
        assert baseline.risk_gate.result == "pass"
        prior_state = baseline.accepted_state
        assert prior_state.agent_ids == SPECIAL_AGENT_IDS

        allowlisted_paths = _mutate_fixture(fixture_root, base_allowlist, case)
        report = validate_specials_pack(
            fixture_root,
            allowlisted_paths,
            previous_state=prior_state,
            manual_revalidation=case.manual_revalidation,
        )

        source_drift = (
            case.availability == "present"
            and case.source_digest_mode == "drift"
            and case.source_path_mode == "valid"
        )
        invalid_provenance = (
            case.source_path_mode != "valid"
            or case.source_digest_mode == "malformed"
            or case.configuration_digest_mode != "matching"
            or case.availability == "unreadable"
            or case.approval_state != "valid"
        )
        expected_pass = not invalid_provenance and not (source_drift and case.manual_revalidation)

        if expected_pass:
            assert report.validation_outcome == "pass"
            assert report.accepted_agent_ids == SPECIAL_AGENT_IDS
            assert report.rejected_agent_ids == ()
            assert report.findings == ()
            assert report.registration_effect == "eligible_draft_representation"
            assert report.provenance.result == "pass"
            assert report.risk_gate.result == "pass"
            if source_drift:
                assert report.accepted_state is prior_state
        else:
            assert report.validation_outcome == "fail"
            assert report.accepted_agent_ids == ()
            assert report.registration_effect == "none"
            assert report.accepted_state is prior_state
            assert report.findings

        finding_codes = _finding_codes(report)
        if case.source_path_mode != "valid":
            assert "INVALID_SOURCE_PATH" in finding_codes
        elif case.source_digest_mode == "malformed":
            assert "INVALID_SOURCE_DIGEST" in finding_codes
        elif case.configuration_digest_mode == "malformed":
            assert "INVALID_CONFIGURATION_DIGEST" in finding_codes
        elif case.configuration_digest_mode == "mismatch":
            assert "CONFIGURATION_DIGEST_MISMATCH" in finding_codes
        elif case.availability == "unreadable":
            assert "SOURCE_NOT_READABLE" in finding_codes
        elif case.manual_revalidation and source_drift:
            assert "STALE_SOURCE_REQUIRES_REVALIDATION" in finding_codes
        elif case.approval_state == "missing":
            assert "MISSING_APPROVAL_RECORD" in finding_codes
        elif case.approval_state == "source_mismatch":
            assert "APPROVAL_SOURCE_DIGEST_MISMATCH" in finding_codes
        elif case.approval_state == "rejected":
            assert "APPROVAL_NOT_GRANTED" in finding_codes
