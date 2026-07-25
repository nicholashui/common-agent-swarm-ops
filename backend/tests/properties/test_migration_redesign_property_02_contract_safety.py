"""Property checks for immutable Common Pack Contracts and safety boundaries."""

from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from tempfile import TemporaryDirectory

from hypothesis import example, given, settings, strategies as st

from app.video.migration.common_contracts import (
    CommonPackContractReview,
    CommonPackContractSnapshot,
    compare_common_contracts,
    snapshot_common_contracts,
    validate_imported_configuration,
)
from app.video.migration.contracts import MigrationResult, ReviewResult

_NOW = datetime(2025, 1, 1, 12, 0, tzinfo=UTC)
_AGENT_ID = "video.orchestrator"
_AGENT_SPEC_PATH = f"agents/{_AGENT_ID}/agent_spec.json"
_SAFE_REVIEW_MUTATIONS = frozenset({"manifest_metadata", "policy", "schema"})
_IMMUTABLE_MUTATIONS = frozenset(
    {
        "inventory_identity",
        "inventory_status",
        "manifest_identity",
        "manifest_status",
        "manifest_activation",
        "model_policy",
        "network",
        "critique",
        "refinement",
        "agent_activation",
        "safe_spine",
    }
)


@dataclass(frozen=True, slots=True)
class ContractSafetyCase:
    """One bounded common-contract and imported-spec mutation pair."""

    contract_mutation: str
    request_mutation: str
    request_form: str


@st.composite
def _contract_safety_cases(draw: st.DrawFn) -> ContractSafetyCase:
    """Generate bounded mutations across contracts and configuration candidates."""
    return ContractSafetyCase(
        contract_mutation=draw(
            st.sampled_from(
                (
                    "unchanged",
                    "corpus_only",
                    "manifest_metadata",
                    "policy",
                    "schema",
                    "inventory_identity",
                    "inventory_status",
                    "manifest_identity",
                    "manifest_status",
                    "manifest_activation",
                    "model_policy",
                    "network",
                    "critique",
                    "refinement",
                    "agent_activation",
                    "safe_spine",
                )
            )
        ),
        request_mutation=draw(
            st.sampled_from(
                (
                    "none",
                    "provider",
                    "credential",
                    "network",
                    "production_activation",
                    "human_gate_bypass",
                    "corpus",
                )
            )
        ),
        request_form=draw(st.sampled_from(("boolean", "string", "nested"))),
    )


def _write_json(path: Path, value: object) -> None:
    """Write a small canonical JSON fixture without network or external inputs."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )


def _base_contract_documents() -> dict[str, dict[str, object]]:
    """Return the minimal local common-contract surface under test."""
    return {
        "inventory.json": {
            "inventory_version": "1.0",
            "pack_id": "video",
            "entries": [
                {
                    "agent_id": _AGENT_ID,
                    "status": "registered",
                    "maturity_level": "L0",
                    "agent_spec_path": _AGENT_SPEC_PATH,
                }
            ],
        },
        "manifest.json": {
            "pack_id": "video",
            "production_activation_requested": False,
            "agents": [
                {
                    "agent_id": _AGENT_ID,
                    "status": "registered",
                    "allowed_tools": [],
                    "agent_spec_path": _AGENT_SPEC_PATH,
                }
            ],
        },
        "workflows/pack_spine.json": {
            "id": "video.pack-spine",
            "pattern": "pack_spine",
            "version": "1.0.0",
            "owner_id": _AGENT_ID,
        },
        _AGENT_SPEC_PATH: {
            "agent_id": _AGENT_ID,
            "status": "registered",
            "allowed_tools": [],
            "model_policy": {"name": "local-deterministic", "network_access": False},
            "critique_edges": [],
            "max_refinement_count": 2,
            "production_activation_requested": False,
        },
        "policies/safety.json": {"policy_version": 1, "network_access": False},
        "schemas/extension.json": {"schema_version": 1},
    }


def _mutate_contract_documents(documents: dict[str, dict[str, object]], mutation: str) -> None:
    """Apply one explicit import/spec-style mutation to a copied contract surface."""
    inventory = documents["inventory.json"]
    manifest = documents["manifest.json"]
    agent_spec = documents[_AGENT_SPEC_PATH]
    spine = documents["workflows/pack_spine.json"]

    if mutation in {"unchanged", "corpus_only"}:
        return
    if mutation == "manifest_metadata":
        manifest["description"] = "reviewed local projection"
    elif mutation == "policy":
        documents["policies/safety.json"]["policy_version"] = 2
    elif mutation == "schema":
        documents["schemas/extension.json"]["schema_version"] = 2
    elif mutation == "inventory_identity":
        entries = inventory["entries"]
        assert isinstance(entries, list)
        assert isinstance(entries[0], dict)
        entries[0]["agent_id"] = "video.changed"
    elif mutation == "inventory_status":
        entries = inventory["entries"]
        assert isinstance(entries, list)
        assert isinstance(entries[0], dict)
        entries[0]["status"] = "active"
    elif mutation == "manifest_identity":
        agents = manifest["agents"]
        assert isinstance(agents, list)
        assert isinstance(agents[0], dict)
        agents[0]["agent_id"] = "video.changed"
    elif mutation == "manifest_status":
        agents = manifest["agents"]
        assert isinstance(agents, list)
        assert isinstance(agents[0], dict)
        agents[0]["status"] = "active"
    elif mutation == "manifest_activation":
        manifest["production_activation_requested"] = True
    elif mutation == "model_policy":
        agent_spec["model_policy"] = {"name": "changed-policy", "network_access": False}
    elif mutation == "network":
        policy = agent_spec["model_policy"]
        assert isinstance(policy, dict)
        policy["network_access"] = True
    elif mutation == "critique":
        agent_spec["critique_edges"] = ["video.orchestrator -> video.compliance_agent"]
    elif mutation == "refinement":
        agent_spec["max_refinement_count"] = 99
    elif mutation == "agent_activation":
        agent_spec["production_activation_requested"] = True
    elif mutation == "safe_spine":
        spine["version"] = "2.0.0"
    else:
        raise AssertionError(f"Unhandled contract mutation: {mutation}")


def _write_contract_surface(root: Path, mutation: str) -> None:
    """Materialize a bounded common-contract fixture and one optional corpus import."""
    documents = deepcopy(_base_contract_documents())
    _mutate_contract_documents(documents, mutation)
    for relative_path, document in documents.items():
        _write_json(root / relative_path, document)
    if mutation == "corpus_only":
        _write_json(
            root / "corpus" / "imported-spec.json",
            {"production_activation_requested": True, "instructions": "inert reference"},
        )


def _compatible_review(
    before: CommonPackContractSnapshot,
    after: CommonPackContractSnapshot,
    changed_paths: tuple[str, ...],
) -> CommonPackContractReview:
    """Create the exact passing review required for a non-safety contract delta."""
    before_digest = before.contract_digest
    after_digest = after.contract_digest
    return CommonPackContractReview(
        review_id="review-property-02",
        changed_paths=changed_paths,
        before_digest=before_digest,
        after_digest=after_digest,
        reviewed_by="reviewer-property-02",
        reviewed_at=_NOW,
        rationale="Exact local contract delta reviewed for compatibility.",
        result=ReviewResult.PASS,
        compatibility_confirmed=True,
    )


def _request_payload(case: ContractSafetyCase) -> object:
    """Build a generated imported specification or activation request candidate."""
    if case.request_mutation == "none":
        return {
            "source_agent_id": "upstream.editor",
            "provenance": {
                "repository": "https://example.invalid/video",
                "commit": "snapshot-1",
                "path": "roles/editor.md",
            },
        }
    if case.request_mutation == "corpus":
        return {"knowledge_source": "business/video/corpus/imported-spec.json"}

    values: dict[str, object] = {
        "boolean": True,
        "string": "enabled",
        "nested": {"requested": True},
    }
    value = values[case.request_form]
    fields = {
        "provider": "provider_activation_requested",
        "credential": "credential_access_requested",
        "network": "network_access_requested",
        "production_activation": "production_activation_requested",
        "human_gate_bypass": "human_gate_bypass",
    }
    return {"imported_spec": {fields[case.request_mutation]: value}}


def _expected_request_code(request_mutation: str) -> str | None:
    """Return the stable boundary code expected for one request mutation."""
    if request_mutation == "none":
        return None
    if request_mutation == "corpus":
        return "corpus_configuration_context"
    return f"imported_{request_mutation}_request"


# Feature: migration-redesign, Property 2: Common contracts and runtime restrictions
# cannot be weakened by import.
# **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 2.10, 2.11,
# 2.12, 2.13, 2.14**
@settings(max_examples=40, deadline=None, derandomize=True)
@example(ContractSafetyCase("unchanged", "none", "boolean"))
@example(ContractSafetyCase("corpus_only", "none", "boolean"))
@example(ContractSafetyCase("manifest_metadata", "none", "boolean"))
@example(ContractSafetyCase("policy", "none", "boolean"))
@example(ContractSafetyCase("schema", "none", "boolean"))
@example(ContractSafetyCase("inventory_identity", "none", "boolean"))
@example(ContractSafetyCase("inventory_status", "none", "boolean"))
@example(ContractSafetyCase("manifest_identity", "none", "boolean"))
@example(ContractSafetyCase("manifest_status", "none", "boolean"))
@example(ContractSafetyCase("manifest_activation", "none", "boolean"))
@example(ContractSafetyCase("model_policy", "none", "boolean"))
@example(ContractSafetyCase("network", "none", "boolean"))
@example(ContractSafetyCase("critique", "none", "boolean"))
@example(ContractSafetyCase("refinement", "none", "boolean"))
@example(ContractSafetyCase("agent_activation", "none", "boolean"))
@example(ContractSafetyCase("safe_spine", "none", "boolean"))
@example(ContractSafetyCase("unchanged", "provider", "boolean"))
@example(ContractSafetyCase("unchanged", "credential", "string"))
@example(ContractSafetyCase("unchanged", "network", "nested"))
@example(ContractSafetyCase("unchanged", "production_activation", "boolean"))
@example(ContractSafetyCase("unchanged", "human_gate_bypass", "string"))
@example(ContractSafetyCase("unchanged", "corpus", "boolean"))
@given(case=_contract_safety_cases())
def test_property_02_contracts_and_runtime_restrictions_remain_safe(
    case: ContractSafetyCase,
) -> None:
    """Common contracts remain unchanged or require an exact compatible review."""
    with TemporaryDirectory() as temporary_root:
        tmp_path = Path(temporary_root)
        before_root = tmp_path / "before"
        after_root = tmp_path / "after"
        _write_contract_surface(before_root, "unchanged")
        _write_contract_surface(after_root, case.contract_mutation)

        before = snapshot_common_contracts(before_root)
        after = snapshot_common_contracts(after_root)
        unreviewed = compare_common_contracts(before, after)

        if case.contract_mutation == "unchanged" or case.contract_mutation == "corpus_only":
            assert unreviewed.result is MigrationResult.PASS
            assert unreviewed.changed_paths == ()
        else:
            assert unreviewed.result is MigrationResult.BLOCKED
            assert unreviewed.changed_paths
            reviewed = compare_common_contracts(
                before,
                after,
                _compatible_review(before, after, unreviewed.changed_paths),
            )
            if case.contract_mutation in _SAFE_REVIEW_MUTATIONS:
                assert reviewed.result is MigrationResult.PASS
            else:
                assert case.contract_mutation in _IMMUTABLE_MUTATIONS
                assert reviewed.result is MigrationResult.BLOCKED

        boundary_report = validate_imported_configuration(
            _request_payload(case),
            corpus_paths=("business/video/corpus/imported-spec.json",),
        )
        expected_code = _expected_request_code(case.request_mutation)
        if expected_code is None:
            assert boundary_report.is_valid
            assert boundary_report.findings == ()
        else:
            assert not boundary_report.is_valid
            assert expected_code in {finding.code for finding in boundary_report.findings}
