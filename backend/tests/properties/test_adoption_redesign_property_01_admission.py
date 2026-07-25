"""Property checks for complete, fail-closed Domain_Pack admission."""

from __future__ import annotations

from typing import Final

from hypothesis import given, settings, strategies as st

from app.models.common import CompatibilityRange
from app.models.contracts import DomainPack, PackContract
from app.models.control_plane import RegistrationDecision
from app.models.identifiers import ActorId, AgentId, CorrelationId, DomainPackId
from app.registry.admission import PackAdmission
from tests.fakes.adoption import (
    DeterministicAuditRepository,
    DeterministicRegistrationRepository,
)

_CORRELATION_ID: Final = CorrelationId("property-1-admission")
_PACK_CONTRACT_FIELDS: Final = (
    "pack_id",
    "immutable_version",
    "host_compatibility_range",
    "alc_compatibility_range",
    "content_digest",
    "signer_id",
    "agents",
    "workflows",
    "capabilities",
    "data_classifications",
    "required_alc_version",
    "evaluation_references",
    "asset_references",
)
_REQUIRED_FIELD_VALUES: Final = st.one_of(
    st.sampled_from(_PACK_CONTRACT_FIELDS), st.just("unknown_required_field")
)


class DeterministicPolicy:
    """A generated, side-effect-free registration policy fake."""

    def __init__(self, passed: bool) -> None:
        self._passed = passed

    def __call__(self, pack: DomainPack) -> bool:
        del pack
        return self._passed


def _pack(*, digest_valid: bool, asset_reference_valid: bool) -> DomainPack:
    return DomainPack(
        pack_id=DomainPackId("property-admission-pack"),
        immutable_version="1.0.0",
        pack_contract_version="1.0.0",
        host_compatibility_range=CompatibilityRange.exact("1.0.0"),
        alc_compatibility_range=CompatibilityRange.exact("1.0.0"),
        content_digest="sha256:property-pack" if digest_valid else "not-a-content-digest",
        signer_id=ActorId("property-owner"),
        agents=(AgentId("property-agent"),),
        workflows=("workflow:property",),
        capabilities=("capability:property",),
        data_classifications=("public",),
        evaluation_references=("evaluation:property",),
        required_alc_version="1.0.0",
        asset_references=(
            "asset:property@1.0.0#sha256:property-asset"
            if asset_reference_valid
            else "asset-without-content-digest",
        ),
    )


def _value_is_present(value: object) -> bool:
    return value is not None and value != "" and value != ()


# **Validates: Requirements 1.2, 1.3, 1.4, 1.7**
# Feature: adoption-redesign, Property 1: Admission is a complete, fail-closed decision
@settings(max_examples=100, deadline=None)
@given(
    contract_version=st.sampled_from(("1.0.0", "2.0.0")),
    required_fields=st.lists(_REQUIRED_FIELD_VALUES, min_size=0, max_size=4, unique=True),
    policy_results=st.lists(st.booleans(), min_size=0, max_size=4),
    digest_valid=st.booleans(),
    asset_reference_valid=st.booleans(),
    signer_matches=st.booleans(),
    trusted_signer=st.booleans(),
)
def test_admission_is_complete_and_fail_closed(
    contract_version: str,
    required_fields: list[str],
    policy_results: list[bool],
    digest_valid: bool,
    asset_reference_valid: bool,
    signer_matches: bool,
    trusted_signer: bool,
) -> None:
    """Admission persists exactly one complete record only for an all-pass vector."""
    pack = _pack(digest_valid=digest_valid, asset_reference_valid=asset_reference_valid)
    contract = PackContract(
        version=contract_version,
        required_fields=tuple(required_fields),
    )
    supplied_signer = ActorId("property-owner" if signer_matches else "other-signer")
    trusted_signers = (ActorId("property-owner"),) if trusted_signer else (ActorId("other-owner"),)
    registration_repository = DeterministicRegistrationRepository()
    audit_repository = DeterministicAuditRepository()
    admission = PackAdmission(
        registration_repository,
        audit_repository,
        pack_contract=contract,
        policies=tuple(DeterministicPolicy(result) for result in policy_results),
        trusted_signers=trusted_signers,
    )

    result = admission.register(
        pack,
        signer=supplied_signer,
        correlation_id=_CORRELATION_ID,
    )

    contract_fields_passed = contract_version == pack.pack_contract_version and all(
        field_name in _PACK_CONTRACT_FIELDS and _value_is_present(getattr(pack, field_name, None))
        for field_name in required_fields
    )
    expected_approval = (
        contract_fields_passed
        and digest_valid
        and asset_reference_valid
        and signer_matches
        and trusted_signer
        and all(policy_results)
    )

    assert result.is_success is expected_approval
    if expected_approval:
        registration = result.value
        assert registration is not None
        assert registration.pack_id == pack.pack_id
        assert registration.immutable_version == pack.immutable_version
        assert registration.content_digest == pack.content_digest
        assert registration.signer_id == pack.signer_id
        assert registration.host_compatibility_range == pack.host_range
        assert registration.alc_compatibility_range == pack.alc_range
        assert registration.validation_result is True
        assert registration.decision is RegistrationDecision.APPROVED
        assert registration.policy_passed is True
        assert registration.metadata.correlation_id == _CORRELATION_ID
        assert registration_repository.records() == (registration,)
        assert audit_repository.records == ()
    else:
        assert result.value is None
        assert registration_repository.records() == ()
        assert len(audit_repository.records) == 1
