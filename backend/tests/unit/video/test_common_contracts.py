"""Focused tests for immutable common-contract and configuration boundaries."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from app.video.migration.common_contracts import (
    CommonPackContractReview,
    CommonPackContractSnapshot,
    compare_common_contracts,
    validate_imported_configuration,
)
from app.video.migration.contracts import MigrationResult

NOW = datetime(2025, 1, 1, 12, 0, tzinfo=UTC)


def _write_contract_tree(root: Path) -> None:
    (root / "agents" / "video.editor").mkdir(parents=True)
    (root / "policies").mkdir()
    (root / "schemas").mkdir()
    (root / "workflows").mkdir()
    (root / "inventory.json").write_text(
        json.dumps(
            {
                "pack_id": "video",
                "entries": [
                    {
                        "agent_id": "video.editor",
                        "status": "registered",
                        "maturity_level": "L0",
                        "agent_spec_path": "agents/video.editor/agent_spec.json",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    (root / "manifest.json").write_text(
        json.dumps(
            {
                "pack_id": "video",
                "production_activation_requested": False,
                "agents": [
                    {
                        "agent_id": "video.editor",
                        "status": "registered",
                        "allowed_tools": [],
                        "agent_spec_path": "agents/video.editor/agent_spec.json",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    (root / "agents" / "video.editor" / "agent_spec.json").write_text(
        json.dumps(
            {
                "agent_id": "video.editor",
                "status": "registered",
                "allowed_tools": [],
                "model_policy": {
                    "provider": "local_deterministic",
                    "model_id": "local-video-config-v1",
                    "network_access": False,
                },
                "critique_edges": {"inputs": [], "outputs": []},
                "max_refinement_count": 3,
                "production_activation_requested": False,
            }
        ),
        encoding="utf-8",
    )
    (root / "policies" / "release.md").write_text("release policy", encoding="utf-8")
    (root / "schemas" / "video.json").write_text('{"version": 1}', encoding="utf-8")
    (root / "workflows" / "pack_spine.json").write_text(
        '{"id":"video.pack-spine","version":"1.0.0"}', encoding="utf-8"
    )


def test_contract_change_requires_exact_compatible_review(tmp_path: Path) -> None:
    _write_contract_tree(tmp_path)
    before = CommonPackContractSnapshot.capture(tmp_path)
    (tmp_path / "schemas" / "video.json").write_text('{"version": 2}', encoding="utf-8")
    after = CommonPackContractSnapshot.capture(tmp_path)

    blocked = compare_common_contracts(before, after)
    assert blocked.result is MigrationResult.BLOCKED
    assert "schemas/video.json" in blocked.changed_paths
    assert any(
        finding.code == "common_contract_change_requires_review" for finding in blocked.findings
    )

    review = CommonPackContractReview(
        review_id="review-schema-1",
        changed_paths=("schemas/video.json",),
        before_digest=before.contract_digest,
        after_digest=after.contract_digest,
        reviewed_by="reviewer-1",
        reviewed_at=NOW,
        rationale="Schema version remains compatible with the common extension boundary.",
    )
    approved = compare_common_contracts(before, after, review)
    assert approved.result is MigrationResult.PASS
    assert approved.findings == ()


def test_runtime_network_change_is_blocked_even_with_compatible_review(tmp_path: Path) -> None:
    _write_contract_tree(tmp_path)
    before = CommonPackContractSnapshot.capture(tmp_path)
    agent_path = tmp_path / "agents" / "video.editor" / "agent_spec.json"
    agent = json.loads(agent_path.read_text(encoding="utf-8"))
    agent["model_policy"]["network_access"] = True
    agent_path.write_text(json.dumps(agent), encoding="utf-8")
    after = CommonPackContractSnapshot.capture(tmp_path)
    review = CommonPackContractReview(
        review_id="review-runtime-1",
        changed_paths=("agents/video.editor/agent_spec.json",),
        before_digest=before.contract_digest,
        after_digest=after.contract_digest,
        reviewed_by="reviewer-1",
        reviewed_at=NOW,
        rationale="This review must not weaken the network restriction.",
    )

    comparison = compare_common_contracts(before, after, review)
    assert comparison.result is MigrationResult.BLOCKED
    assert any(finding.code == "agent_runtime_safety_changed" for finding in comparison.findings)


def test_activation_requests_and_corpus_paths_are_rejected_as_configuration() -> None:
    report = validate_imported_configuration(
        {
            "provider": "external-provider",
            "credential": "secret-reference",
            "network_access": True,
            "production_activation_requested": True,
            "human_gate_bypass": True,
            "knowledge_source": "corpus/reference.md",
        }
    )

    assert report.result is MigrationResult.BLOCKED
    codes = {finding.code for finding in report.findings}
    assert codes == {
        "corpus_configuration_context",
        "imported_credential_request",
        "imported_human_gate_bypass_request",
        "imported_network_request",
        "imported_production_activation_request",
        "imported_provider_request",
    }


def test_safe_imported_reference_data_is_not_loaded_into_configuration() -> None:
    report = validate_imported_configuration(
        {"reference_note": "provider advice is inert corpus text", "network_access": False}
    )

    assert report.result is MigrationResult.PASS
    assert report.findings == ()
