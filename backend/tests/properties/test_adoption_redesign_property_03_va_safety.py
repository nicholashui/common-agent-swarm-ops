"""Property checks for declarative, reference-only VA package safety."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal, cast

from hypothesis import given, settings, strategies as st

from app.artifacts.handoff_service import ArtifactHandoffService
from app.models.common import SCHEMA_VERSION, RecordMetadata
from app.models.contracts import ErrorCode
from app.models.control_plane import (
    ArtifactAvailabilityStatus,
    ArtifactHandoff,
    ArtifactHandoffId,
    RegistrationDecision,
    TaskId,
)
from app.models.identifiers import (
    ActorId,
    CorrelationId,
    OrganizationId,
    RecordId,
)
from app.registry.admission import PackAdmission
from app.registry.pack_validator import DomainPackValidator
from tests.fakes.adoption import DeterministicAdoptionRepositories

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_ORGANIZATION_ID = OrganizationId("va-property-organization")
_SIGNER_ID = ActorId("va-domain-owner")
_CORRELATION_ID = CorrelationId("adoption-redesign-property-03")
_EXTENSION_SCHEMA = {"asset_reference": str, "schema_version": "1.0.0"}

ExecutableSignal = Literal["none", "package_code", "nested_source_code", "script_path"]


@st.composite
def _va_assets(draw: st.DrawFn) -> list[dict[str, object]]:
    """Generate content-addressed VA asset declarations with non-retained content."""
    asset_ids = draw(
        st.lists(
            st.integers(min_value=0, max_value=10_000),
            min_size=1,
            max_size=4,
            unique=True,
        )
    )
    return [
        {
            "reference": f"va.asset.{asset_id}",
            "version": "1.0.0",
            "digest": f"sha256:va-asset-{asset_id}",
            "content": f"opaque-content-must-not-be-retained-{asset_id}",
        }
        for asset_id in asset_ids
    ]


@st.composite
def _metadata_extensions(draw: st.DrawFn) -> tuple[dict[str, object], bool]:
    """Generate valid and invalid metadata extensions for the registered VA schema."""
    extension_id = draw(st.integers(min_value=0, max_value=10_000))
    is_valid = draw(st.booleans())
    if is_valid:
        return (
            {
                "asset_reference": f"va.handoff.{extension_id}",
                "schema_version": "1.0.0",
            },
            True,
        )

    invalid_variant = draw(st.sampled_from(("missing_reference", "wrong_version", "wrong_type")))
    if invalid_variant == "missing_reference":
        return {"schema_version": "1.0.0"}, False
    if invalid_variant == "wrong_version":
        return {
            "asset_reference": f"va.handoff.{extension_id}",
            "schema_version": "2.0.0",
        }, False
    return {
        "asset_reference": extension_id,
        "schema_version": "1.0.0",
    }, False


def _va_manifest(
    assets: list[dict[str, object]], executable_signal: ExecutableSignal
) -> dict[str, object]:
    """Build a complete valid VA manifest, optionally adding one executable signal."""
    manifest: dict[str, object] = {
        "pack_id": "va-agent-swarm",
        "immutable_version": "1.0.0",
        "pack_contract_version": "1.0.0",
        "host_compatibility_range": {"minimum": "1.0.0", "maximum": "1.0.0"},
        "alc_compatibility_range": {"minimum": "1.0.0", "maximum": "1.0.0"},
        "content_digest": "sha256:va-pack-content",
        "signer_id": str(_SIGNER_ID),
        "agents": ["va.editor"],
        "workflows": ["va.production"],
        "capabilities": ["video-generation"],
        "data_classifications": ["customer-provided"],
        "required_alc_version": "1.0.0",
        "evaluation_references": ["evaluation:va-production-v1"],
        "asset_references": assets,
    }
    if executable_signal == "package_code":
        manifest["package_code"] = "declarative package must not contain executable code"
    elif executable_signal == "nested_source_code":
        assets[0]["source_code"] = "nested executable signal"
    elif executable_signal == "script_path":
        assets[0]["filename"] = "assets/render.py"
    return manifest


def _handoff(extension: dict[str, object], correlation_id: CorrelationId) -> ArtifactHandoff:
    """Build a complete opaque handoff whose extension is the only variable gate."""
    return ArtifactHandoff(
        metadata=RecordMetadata(
            record_id=RecordId("property-03-handoff-record"),
            organization_id=_ORGANIZATION_ID,
            correlation_id=correlation_id,
            schema_version=SCHEMA_VERSION,
            version=1,
            created_at=_NOW,
            updated_at=_NOW,
        ),
        handoff_id=ArtifactHandoffId("property-03-handoff"),
        artifact_identity="va-artifact",
        artifact_version="1.0.0",
        parent_lineage=(),
        source_task_id=TaskId("property-03-task"),
        source_run_reference="run:property-03",
        brief_scope="VA artifact handoff",
        technical_specification=extension,
        rights_and_consent_state="approved",
        continuity_state="complete",
        quality_control_state="passed",
        target_channels=("video-platform",),
        provenance_reference="provenance:property-03",
        owner_reference="va-agent-swarm",
        classification="customer-provided",
        integrity_reference="sha256:handoff-metadata",
        approval_reference="approval:property-03",
        availability=ArtifactAvailabilityStatus.PENDING,
        external=False,
        metadata_persisted=False,
    )


# Feature: adoption-redesign, Property 3: VA packages retain declarative, reference-only safety
# **Validates: Requirements 2.2, 2.4, 2.8, 2.9**
@settings(max_examples=100, deadline=None)
@given(
    assets=_va_assets(),
    executable_signal=st.sampled_from(
        ("none", "package_code", "nested_source_code", "script_path")
    ),
    extension_vector=_metadata_extensions(),
)
def test_property_03_va_packages_retain_declarative_reference_only_safety(
    assets: list[dict[str, object]],
    executable_signal: ExecutableSignal,
    extension_vector: tuple[dict[str, object], bool],
) -> None:
    """Executable VA declarations reject admission; valid extensions cross the handoff gate."""
    extension, extension_is_valid = extension_vector
    repositories = DeterministicAdoptionRepositories()
    admission = PackAdmission(
        repositories.registrations,
        repositories.audit,
        trusted_signers=(_SIGNER_ID,),
    )
    manifest = _va_manifest(assets, executable_signal)
    registration_result = admission.register(
        manifest,
        signer=_SIGNER_ID,
        correlation_id=_CORRELATION_ID,
        organization_id=_ORGANIZATION_ID,
        pack_contract=None,
    )

    if executable_signal != "none":
        assert not registration_result.is_success
        assert registration_result.error is not None
        assert registration_result.error.code is ErrorCode.VALIDATION_FAILED
        assert repositories.registrations.records() == ()
        return

    assert registration_result.is_success
    registration = registration_result.value
    assert registration is not None
    assert registration.decision is RegistrationDecision.APPROVED
    expected_references = tuple(
        (
            f"{cast(str, asset['reference'])}@{cast(str, asset['version'])}"
            f"#{cast(str, asset['digest'])}"
        )
        for asset in assets
    )
    assert registration.asset_references == expected_references
    assert all(
        DomainPackValidator.is_valid_asset_reference(reference)
        for reference in registration.asset_references
    )
    assert all(
        f"opaque-content-must-not-be-retained-{cast(str, asset['reference']).split('.')[-1]}"
        not in repr(registration)
        for asset in assets
    )

    handoff_service = ArtifactHandoffService(
        repositories.handoffs,
        repositories.audit,
        va_extension_schema=_EXTENSION_SCHEMA,
    )
    handoff_result = handoff_service.create_internal(
        _ORGANIZATION_ID,
        _handoff(extension, _CORRELATION_ID),
        correlation_id=_CORRELATION_ID,
    )

    if extension_is_valid:
        assert handoff_result.is_success
        persisted_handoff = handoff_result.value
        assert persisted_handoff is not None
        assert persisted_handoff.availability is ArtifactAvailabilityStatus.AVAILABLE
        assert persisted_handoff.metadata_persisted
        assert repositories.handoffs.available_for_downstream(_ORGANIZATION_ID).value == (
            persisted_handoff,
        )
    else:
        assert not handoff_result.is_success
        assert handoff_result.error is not None
        assert handoff_result.error.code is ErrorCode.VALIDATION_FAILED
        assert repositories.handoffs.records() == ()
        assert len(repositories.audit.records) == 1
        assert repositories.audit.records[0].action == "artifact_handoff.va_extension.blocked"
