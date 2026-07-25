"""Property checks for intersection-based compatibility and use guards."""

# The required specification comment exceeds the repository's line-length limit.
# ruff: noqa: E501
from __future__ import annotations

from hypothesis import given, settings, strategies as st

from app.models.common import CompatibilityRange, semantic_version_key
from app.models.contracts import (
    AgentLearningContract,
    DomainPack,
    HostContract,
    PackContract,
)
from app.models.identifiers import ActorId, AgentId, DomainPackId
from app.registry.compatibility import (
    CompatibilityMatrixEntry,
    CompatibilityRegistry,
    InMemoryCompatibilityMatrixRepository,
)

_PACK_CONTRACT_VERSION = "1.0.0"
_PACK_VERSION = "1.0.0"
_AGENT_ID = AgentId("property-20-agent")
_PACK_ID = DomainPackId("property-20-pack")


def _version(value: int) -> str:
    """Return a bounded semantic version used by the generated ranges."""
    return f"0.0.{value}"


@st.composite
def _bounded_range(draw: st.DrawFn) -> CompatibilityRange:
    """Generate a non-empty, bounded semantic-version range."""
    lower = draw(st.integers(min_value=0, max_value=20))
    width = draw(st.integers(min_value=0, max_value=10))
    upper = lower + width
    include_minimum = draw(st.booleans())
    include_maximum = draw(st.booleans())

    if width == 0:
        include_minimum = True
        include_maximum = True
    elif width == 1 and not include_minimum and not include_maximum:
        # Adjacent semantic versions have no value between them.
        include_minimum = True

    return CompatibilityRange(
        minimum=_version(lower),
        maximum=_version(upper),
        include_minimum=include_minimum,
        include_maximum=include_maximum,
    )


def _next_version(value: tuple[int, int, int]) -> tuple[int, int, int]:
    """Return the next bounded semantic version in the generated domain."""
    return value[0], value[1], value[2] + 1


def _intersection_witness(left: CompatibilityRange, right: CompatibilityRange) -> str | None:
    """Find a semantic-version witness for two generated ranges, if one exists."""
    assert left.minimum is not None and left.maximum is not None
    assert right.minimum is not None and right.maximum is not None
    left_minimum = semantic_version_key(left.minimum)
    right_minimum = semantic_version_key(right.minimum)
    if left_minimum > right_minimum:
        lower = left_minimum
        lower_inclusive = left.include_minimum
    elif right_minimum > left_minimum:
        lower = right_minimum
        lower_inclusive = right.include_minimum
    else:
        lower = left_minimum
        lower_inclusive = left.include_minimum and right.include_minimum

    left_maximum = semantic_version_key(left.maximum)
    right_maximum = semantic_version_key(right.maximum)
    if left_maximum < right_maximum:
        upper = left_maximum
        upper_inclusive = left.include_maximum
    elif right_maximum < left_maximum:
        upper = right_maximum
        upper_inclusive = right.include_maximum
    else:
        upper = left_maximum
        upper_inclusive = left.include_maximum and right.include_maximum

    if lower > upper or (lower == upper and not (lower_inclusive and upper_inclusive)):
        return None
    candidate = lower if lower_inclusive else _next_version(lower)
    if candidate > upper or (candidate == upper and not upper_inclusive):
        return None
    return ".".join(str(part) for part in candidate)


def _contained_version(version_range: CompatibilityRange) -> str:
    """Return a version contained by one generated range."""
    assert version_range.minimum is not None and version_range.maximum is not None
    minimum = semantic_version_key(version_range.minimum)
    maximum = semantic_version_key(version_range.maximum)
    candidate = minimum if version_range.include_minimum else _next_version(minimum)
    if candidate > maximum or (candidate == maximum and not version_range.include_maximum):
        candidate = maximum
    assert version_range.contains(".".join(str(part) for part in candidate))
    return ".".join(str(part) for part in candidate)


def _domain_pack(host_range: CompatibilityRange, alc_range: CompatibilityRange) -> DomainPack:
    """Build the same valid declarative pack for every isolated registry run."""
    return DomainPack(
        pack_id=_PACK_ID,
        immutable_version=_PACK_VERSION,
        pack_contract_version=_PACK_CONTRACT_VERSION,
        host_compatibility_range=host_range,
        alc_compatibility_range=alc_range,
        content_digest="sha256:property-20-pack",
        signer_id=ActorId("property-20-signer"),
        agents=(_AGENT_ID,),
        workflows=("property-20-workflow",),
        capabilities=("property-20-capability",),
        data_classifications=("property-20-classification",),
        evaluation_references=("evaluation:property-20",),
        required_alc_version=_contained_version(alc_range),
        asset_references=("asset:property-20",),
    )


def _learning_contract(version: str) -> AgentLearningContract:
    """Build a deterministic ALC for matrix and guard evaluation."""
    return AgentLearningContract(
        agent_id=_AGENT_ID,
        version=version,
        memory_scopes=("property-20-memory",),
        retrieval_policy="enabled",
        reflection_policy="enabled",
        evaluation_references=("evaluation:property-20",),
        retention_policy="retain",
        human_promotion_policy="required",
    )


# Feature: adoption-redesign, Property 20: Compatibility is intersection-based and blocks use when incompatible
# **Validates: Requirements 7.12, 8.2, 8.3, 8.4, 8.5**
@settings(max_examples=100, deadline=None)
@given(
    pack_host_range=_bounded_range(),
    supported_host_range=_bounded_range(),
    pack_alc_range=_bounded_range(),
    supported_alc_range=_bounded_range(),
)
def test_property_20_compatibility_is_intersection_based_and_blocks_incompatible_use(
    pack_host_range: CompatibilityRange,
    supported_host_range: CompatibilityRange,
    pack_alc_range: CompatibilityRange,
    supported_alc_range: CompatibilityRange,
) -> None:
    """Compatibility, both use guards, and matrix evidence share one range decision."""
    pack = _domain_pack(pack_host_range, pack_alc_range)
    pack_contract = PackContract(version=_PACK_CONTRACT_VERSION)
    expected_compatible = pack_host_range.intersects(
        supported_host_range
    ) and pack_alc_range.intersects(supported_alc_range)

    matrix_repository = InMemoryCompatibilityMatrixRepository()
    registry = CompatibilityRegistry(matrix_repository)
    evaluation = registry.evaluate_detailed(pack, supported_host_range, supported_alc_range)

    assert evaluation.compatible is expected_compatible
    assert registry.status_for(_PACK_ID, _PACK_VERSION) is evaluation.status
    assert registry.evaluation_for(_PACK_ID, _PACK_VERSION) == evaluation

    host_version = (
        _intersection_witness(pack_host_range, supported_host_range)
        if pack_host_range.intersects(supported_host_range)
        else _contained_version(supported_host_range)
    )
    alc_version = (
        _intersection_witness(pack_alc_range, supported_alc_range)
        if pack_alc_range.intersects(supported_alc_range)
        else _contained_version(supported_alc_range)
    )
    assert host_version is not None and alc_version is not None
    host_contract = HostContract(
        version=host_version,
        supported_pack_range=CompatibilityRange.exact(_PACK_CONTRACT_VERSION),
        supported_alc_range=supported_alc_range,
    )
    alc_contract = _learning_contract(alc_version)

    activation = registry.guard_activation(
        pack,
        pack_contract=pack_contract,
        host_contract=host_contract,
        alc_contract=alc_contract,
        evaluation_references=pack.evaluation_references,
    )
    invocation = registry.guard_invocation(pack)
    assert activation.is_allowed is expected_compatible
    assert invocation.is_allowed is expected_compatible

    matrix_result = registry.record_supported_combination(
        host_contract,
        pack_contract,
        alc_contract,
        pack=pack,
    )
    assert matrix_result.is_success
    matrix_entry = matrix_result.value
    assert isinstance(matrix_entry, CompatibilityMatrixEntry)
    assert matrix_entry.designated
    assert matrix_entry.status.value == evaluation.status.value
    assert matrix_entry.pack_contract_version == _PACK_CONTRACT_VERSION
    assert matrix_entry.host_contract_version == host_contract.version
    assert matrix_entry.alc_version == alc_contract.version
    assert matrix_repository.contains(
        _PACK_CONTRACT_VERSION,
        host_contract.version,
        alc_contract.version,
    )
