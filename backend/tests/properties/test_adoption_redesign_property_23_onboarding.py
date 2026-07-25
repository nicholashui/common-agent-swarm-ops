"""Property checks for new-domain onboarding admission evidence."""

from __future__ import annotations

from dataclasses import dataclass

from hypothesis import given, settings, strategies as st

from app.models.common import CompatibilityRange
from app.models.contracts import DomainPack, HostContract, PackContract
from app.models.control_plane import CompatibilityStatus
from app.models.identifiers import ActorId, AgentId, DomainPackId
from app.registry.compatibility import CompatibilityRegistry, InMemoryCompatibilityMatrixRepository

_PACK_CONTRACT_VERSION = "1.0.0"
_SUPPORTED_HOST_VERSION = "1.0.0"
_SUPPORTED_ALC_VERSION = "1.0.0"
_REQUIRED_PACK_FIELDS = PackContract(version=_PACK_CONTRACT_VERSION).required_fields


@dataclass(frozen=True, slots=True)
class OnboardingDeclaration:
    """Generated declaration inputs for one new-domain eligibility decision."""

    suffix: int
    pack_contract_version_matches: bool
    required_fields_complete: bool
    evaluation_references_declared: bool


@st.composite
def _onboarding_declarations(draw: st.DrawFn) -> OnboardingDeclaration:
    """Generate independent admission and evaluation evidence combinations."""
    return OnboardingDeclaration(
        suffix=draw(st.integers(min_value=0, max_value=9_999)),
        pack_contract_version_matches=draw(st.booleans()),
        required_fields_complete=draw(st.booleans()),
        evaluation_references_declared=draw(st.booleans()),
    )


def _domain_pack(declaration: OnboardingDeclaration) -> DomainPack:
    """Build a structurally valid pack with generated onboarding evidence variations."""
    version = _PACK_CONTRACT_VERSION if declaration.pack_contract_version_matches else "2.0.0"
    evaluation_references = (
        (f"evaluation:{declaration.suffix}",) if declaration.evaluation_references_declared else ()
    )
    return DomainPack(
        pack_id=DomainPackId(f"domain-{declaration.suffix}"),
        immutable_version="1.0.0",
        pack_contract_version=version,
        host_compatibility_range=CompatibilityRange.exact(_SUPPORTED_HOST_VERSION),
        alc_compatibility_range=CompatibilityRange.exact(_SUPPORTED_ALC_VERSION),
        content_digest=f"sha256:domain-{declaration.suffix}",
        signer_id=ActorId(f"signer-{declaration.suffix}"),
        agents=(AgentId(f"agent-{declaration.suffix}"),),
        workflows=(f"workflow-{declaration.suffix}",),
        capabilities=("declarative-capability",),
        data_classifications=("public",),
        evaluation_references=evaluation_references,
        required_alc_version=_SUPPORTED_ALC_VERSION,
    )


def _pack_contract(declaration: OnboardingDeclaration) -> PackContract:
    """Build a contract with generated validity evidence."""
    required_fields = (
        _REQUIRED_PACK_FIELDS
        if declaration.required_fields_complete
        else ("missing_onboarding_field",)
    )
    return PackContract(version=_PACK_CONTRACT_VERSION, required_fields=required_fields)


# Feature: adoption-redesign, Property 23: Domain onboarding requires admission evidence
# **Validates: Requirements 8.12**
@settings(max_examples=100, deadline=None)
@given(declaration=_onboarding_declarations())
def test_new_domain_activation_requires_pack_contract_and_evaluation_references(
    declaration: OnboardingDeclaration,
) -> None:
    """Activation eligibility requires both Pack_Contract and evaluation evidence."""
    pack = _domain_pack(declaration)
    pack_contract = _pack_contract(declaration)
    registry = CompatibilityRegistry(InMemoryCompatibilityMatrixRepository())
    supported_host = HostContract(
        version=_SUPPORTED_HOST_VERSION,
        supported_pack_range=CompatibilityRange.exact(_PACK_CONTRACT_VERSION),
        supported_alc_range=CompatibilityRange.exact(_SUPPORTED_ALC_VERSION),
    )

    eligibility = registry.evaluate_activation_eligibility(
        pack,
        pack_contract,
        host_contract=supported_host,
    )

    contract_is_valid = not pack_contract.validate(pack)
    references_are_present = declaration.evaluation_references_declared
    expected_eligibility = contract_is_valid and references_are_present

    assert eligibility.compatibility_status is CompatibilityStatus.COMPATIBLE
    assert eligibility.pack_contract_valid is contract_is_valid
    assert eligibility.evaluation_references_present is references_are_present
    assert eligibility.is_eligible is expected_eligibility
    assert eligibility.eligible is expected_eligibility
