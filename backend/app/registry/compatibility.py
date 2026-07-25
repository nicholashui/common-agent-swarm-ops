"""Intersection-based contract compatibility and fail-closed use guards.

The compatibility registry deliberately keeps compatibility evidence separate from
registration and execution records.  A pack may be registered while incompatible,
but neither activation nor invocation can use it until a compatible evaluation has
been retained.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from threading import RLock
from typing import Protocol

from app.models.common import CompatibilityRange, validate_semantic_version
from app.models.contracts import (
    AgentLearningContract,
    Allowed,
    CommandOutcome,
    Denied,
    DomainPack,
    ErrorCode,
    ErrorDetail,
    HostContract,
    PackContract,
    RepositoryError,
    Result,
)
from app.models.control_plane import (
    CompatibilityStatus,
    Registration,
    RegistrationDecision,
    WorkflowActivation,
)
from app.models.identifiers import (
    CorrelationId,
    DomainPackId,
    EvidenceId,
    new_correlation_id,
)


@dataclass(frozen=True, slots=True)
class DeclaredCompatibilityRanges:
    """The independently declared Host_Contract and ALC ranges of a pack."""

    host_range: CompatibilityRange
    alc_range: CompatibilityRange
    pack_id: DomainPackId | None = None
    immutable_version: str | None = None

    def __post_init__(self) -> None:
        if self.immutable_version is not None:
            validate_semantic_version(self.immutable_version, "immutable_version")


@dataclass(frozen=True, slots=True)
class CompatibilityEvaluation:
    """Immutable evidence for one comparison of declared and supported ranges."""

    status: CompatibilityStatus
    declared_host_intersects: bool
    declared_alc_intersects: bool
    pack_id: DomainPackId | None = None
    immutable_version: str | None = None
    pack_contract_version: str | None = None
    host_contract_version: str | None = None
    alc_version: str | None = None
    failure_reasons: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "status", CompatibilityStatus(self.status))
        if self.immutable_version is not None:
            validate_semantic_version(self.immutable_version, "immutable_version")
        for value, name in (
            (self.pack_contract_version, "pack_contract_version"),
            (self.host_contract_version, "host_contract_version"),
            (self.alc_version, "alc_version"),
        ):
            if value is not None:
                validate_semantic_version(value, name)
        reasons = tuple(dict.fromkeys(str(reason) for reason in self.failure_reasons))
        if any(not reason.strip() for reason in reasons):
            raise ValueError("Compatibility failure reasons must be non-empty.")
        object.__setattr__(self, "failure_reasons", reasons)
        if self.status is CompatibilityStatus.COMPATIBLE and (
            not self.declared_host_intersects or not self.declared_alc_intersects or reasons
        ):
            raise ValueError("Compatible evidence requires both range intersections to pass.")

    @property
    def compatible(self) -> bool:
        """Return whether both independently evaluated ranges intersect."""
        return self.status is CompatibilityStatus.COMPATIBLE

    @property
    def is_compatible(self) -> bool:
        """Descriptive alias for callers that use a predicate-style name."""
        return self.compatible

    def __bool__(self) -> bool:
        return self.compatible


@dataclass(frozen=True, slots=True)
class CompatibilityMatrixEntry:
    """A Verification_Suite-designated supported contract combination."""

    pack_contract_version: str
    host_contract_version: str
    alc_version: str
    status: CompatibilityStatus
    designated: bool = True
    pack_id: DomainPackId | None = None
    immutable_version: str | None = None
    evidence_reference: str | None = None

    def __post_init__(self) -> None:
        for value, name in (
            (self.pack_contract_version, "pack_contract_version"),
            (self.host_contract_version, "host_contract_version"),
            (self.alc_version, "alc_version"),
        ):
            validate_semantic_version(value, name)
        if self.immutable_version is not None:
            validate_semantic_version(self.immutable_version, "immutable_version")
        object.__setattr__(self, "status", CompatibilityStatus(self.status))
        if self.evidence_reference is not None and not self.evidence_reference.strip():
            raise ValueError("Compatibility matrix evidence references must be non-empty.")
        if not self.designated:
            raise ValueError("Compatibility matrix entries must be designated combinations.")

    @property
    def identity_key(self) -> tuple[str, str, str, DomainPackId | None, str | None]:
        """Return the immutable matrix identity."""
        return (
            self.pack_contract_version,
            self.host_contract_version,
            self.alc_version,
            self.pack_id,
            self.immutable_version,
        )


SupportedCombination = CompatibilityMatrixEntry


class CompatibilityMatrixRepository(Protocol):
    """Persistence seam for Verification_Suite compatibility evidence."""

    def append(
        self, entry: CompatibilityMatrixEntry
    ) -> Result[CompatibilityMatrixEntry, RepositoryError]:
        """Append one designated combination without replacing prior evidence."""

    def entries(self) -> tuple[CompatibilityMatrixEntry, ...]:
        """Return designated combinations in insertion order."""


class InMemoryCompatibilityMatrixRepository:
    """Deterministic append-only matrix repository for local and test execution."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._entries: dict[
            tuple[str, str, str, DomainPackId | None, str | None], CompatibilityMatrixEntry
        ] = {}

    def append(
        self, entry: CompatibilityMatrixEntry
    ) -> Result[CompatibilityMatrixEntry, RepositoryError]:
        """Append one matrix entry, preserving immutable combination identity."""
        with self._lock:
            if entry.identity_key in self._entries:
                return Result.failure(
                    ErrorDetail(
                        ErrorCode.CONFLICT,
                        "Compatibility matrix combination already exists.",
                        CorrelationId("compatibility-matrix"),
                    )
                )
            self._entries[entry.identity_key] = entry
            return Result.success(entry)

    def entries(self) -> tuple[CompatibilityMatrixEntry, ...]:
        """Return immutable matrix snapshots in deterministic insertion order."""
        with self._lock:
            return tuple(self._entries.values())

    @property
    def records(self) -> tuple[CompatibilityMatrixEntry, ...]:
        """Convenient repository alias used by verification assertions."""
        return self.entries()

    def contains(
        self,
        pack_contract_version: str,
        host_contract_version: str,
        alc_version: str,
    ) -> bool:
        """Return whether a designated version combination has been recorded."""
        with self._lock:
            return any(
                entry.pack_contract_version == pack_contract_version
                and entry.host_contract_version == host_contract_version
                and entry.alc_version == alc_version
                for entry in self._entries.values()
            )


CompatibilityMatrix = InMemoryCompatibilityMatrixRepository


@dataclass(frozen=True, slots=True)
class ActivationEligibility:
    """The complete, fail-closed activation decision for a new domain pack."""

    pack_id: DomainPackId
    immutable_version: str
    compatibility_status: CompatibilityStatus
    pack_contract_valid: bool
    evaluation_references_present: bool
    eligible: bool
    failure_reasons: tuple[str, ...] = ()
    compatibility_evaluation: CompatibilityEvaluation | None = None

    def __post_init__(self) -> None:
        validate_semantic_version(self.immutable_version, "immutable_version")
        object.__setattr__(
            self, "compatibility_status", CompatibilityStatus(self.compatibility_status)
        )
        reasons = tuple(dict.fromkeys(str(reason) for reason in self.failure_reasons))
        if any(not reason.strip() for reason in reasons):
            raise ValueError("Activation failure reasons must be non-empty.")
        object.__setattr__(self, "failure_reasons", reasons)
        expected = (
            self.pack_contract_valid
            and self.evaluation_references_present
            and self.compatibility_status is CompatibilityStatus.COMPATIBLE
        )
        if self.eligible != expected:
            raise ValueError("Activation eligibility must include every required gate.")

    @property
    def is_eligible(self) -> bool:
        """Return whether the pack may enter an activation-eligible state."""
        return self.eligible


class CompatibilityRegistry:
    """Evaluate independent contract ranges and guard activation and invocation use."""

    def __init__(
        self,
        matrix_repository: CompatibilityMatrixRepository | None = None,
    ) -> None:
        self._matrix_repository = matrix_repository or InMemoryCompatibilityMatrixRepository()
        self._lock = RLock()
        self._evaluations: dict[tuple[DomainPackId, str], tuple[CompatibilityEvaluation, ...]] = {}
        self._activation_guard = ActivationGuard(self)
        self._invocation_guard = InvocationGuard(self)

    @property
    def matrix_repository(self) -> CompatibilityMatrixRepository:
        """Expose the Verification_Suite evidence seam without exposing mutable state."""
        return self._matrix_repository

    @property
    def compatibility_matrix(self) -> tuple[CompatibilityMatrixEntry, ...]:
        """Return all designated supported combinations."""
        return self._matrix_repository.entries()

    @property
    def activation_guard(self) -> ActivationGuard:
        """Return the activation guard bound to this registry."""
        return self._activation_guard

    @property
    def invocation_guard(self) -> InvocationGuard:
        """Return the invocation-submission guard bound to this registry."""
        return self._invocation_guard

    def evaluate(
        self,
        declared: DomainPack | DeclaredCompatibilityRanges | CompatibilityRange,
        supported_host: HostContract | CompatibilityRange,
        supported_alc: AgentLearningContract | CompatibilityRange | None = None,
        *,
        pack_alc_range: CompatibilityRange | None = None,
    ) -> CompatibilityStatus:
        """Evaluate and retain status; compatibility requires both intersections.

        ``declared`` normally is a :class:`DomainPack`.  The range form is kept
        for callers that already have normalized declarations; in that form
        ``pack_alc_range`` supplies the independent ALC range and defaults to
        the declared Host range only for backwards-compatible two-range callers.
        """
        return self.evaluate_detailed(
            declared,
            supported_host,
            supported_alc,
            pack_alc_range=pack_alc_range,
        ).status

    def evaluate_detailed(
        self,
        declared: DomainPack | DeclaredCompatibilityRanges | CompatibilityRange,
        supported_host: HostContract | CompatibilityRange,
        supported_alc: AgentLearningContract | CompatibilityRange | None = None,
        *,
        pack_alc_range: CompatibilityRange | None = None,
    ) -> CompatibilityEvaluation:
        """Return and retain complete compatibility evidence for a declaration."""
        declared_host, declared_alc, pack_id, pack_version, pack_contract_version = (
            self._declared_ranges(declared, pack_alc_range)
        )
        (
            supported_host_range,
            supported_alc_range,
            host_contract_version,
            actual_alc_version,
        ) = self._supported_ranges(supported_host, supported_alc)
        host_intersects = declared_host.intersects(supported_host_range)
        alc_intersects = declared_alc.intersects(supported_alc_range)
        reasons: list[str] = []
        if not host_intersects:
            reasons.append("host_contract_range")
        if not alc_intersects:
            reasons.append("alc_range")
        if actual_alc_version is not None:
            if not declared_alc.contains(actual_alc_version):
                reasons.append("alc_version_not_declared")
            if not supported_alc_range.contains(actual_alc_version):
                reasons.append("alc_version_not_supported")
        status = CompatibilityStatus.COMPATIBLE if not reasons else CompatibilityStatus.INCOMPATIBLE
        evaluation = CompatibilityEvaluation(
            status=status,
            declared_host_intersects=host_intersects,
            declared_alc_intersects=alc_intersects,
            pack_id=pack_id,
            immutable_version=pack_version,
            pack_contract_version=pack_contract_version,
            host_contract_version=host_contract_version,
            alc_version=actual_alc_version,
            failure_reasons=tuple(reasons),
        )
        if pack_id is not None and pack_version is not None:
            with self._lock:
                key = (pack_id, pack_version)
                self._evaluations[key] = (*self._evaluations.get(key, ()), evaluation)
        return evaluation

    def status_for(self, pack_id: DomainPackId, immutable_version: str) -> CompatibilityStatus:
        """Return the latest retained status, failing closed when none was evaluated."""
        with self._lock:
            evaluations = self._evaluations.get((pack_id, immutable_version), ())
            if not evaluations:
                return CompatibilityStatus.NOT_EVALUATED
            return evaluations[-1].status

    def evaluation_for(
        self, pack_id: DomainPackId, immutable_version: str
    ) -> CompatibilityEvaluation | None:
        """Return the latest detailed evaluation for one immutable pack version."""
        with self._lock:
            evaluations = self._evaluations.get((pack_id, immutable_version), ())
            return evaluations[-1] if evaluations else None

    def evaluations(self) -> tuple[CompatibilityEvaluation, ...]:
        """Return all retained evaluations in deterministic key/insertion order."""
        with self._lock:
            return tuple(
                evaluation for values in self._evaluations.values() for evaluation in values
            )

    def evaluate_activation_eligibility(
        self,
        pack: DomainPack,
        pack_contract: PackContract | None = None,
        *,
        host_contract: HostContract | None = None,
        alc_contract: AgentLearningContract | None = None,
        evaluation_references: Iterable[str] | None = None,
    ) -> ActivationEligibility:
        """Require Pack_Contract validity, evaluations, and compatibility before eligibility."""
        contract = pack_contract or PackContract(version=pack.pack_contract_version)
        contract_failures = contract.validate(pack)
        references = tuple(evaluation_references or pack.evaluation_references)
        references_present = bool(references) and all(
            bool(reference.strip()) for reference in references
        )
        evaluation = self.evaluation_for(pack.pack_id, pack.immutable_version)
        if host_contract is not None:
            evaluation = self.evaluate_detailed(pack, host_contract, alc_contract)
        status = evaluation.status if evaluation is not None else CompatibilityStatus.NOT_EVALUATED
        reasons = list(contract_failures)
        if not references_present:
            reasons.append("evaluation_references")
        if status is not CompatibilityStatus.COMPATIBLE:
            reasons.append("compatibility")
        return ActivationEligibility(
            pack_id=pack.pack_id,
            immutable_version=pack.immutable_version,
            compatibility_status=status,
            pack_contract_valid=not contract_failures,
            evaluation_references_present=references_present,
            eligible=not reasons,
            failure_reasons=tuple(reasons),
            compatibility_evaluation=evaluation,
        )

    # Descriptive aliases used by migration and onboarding callers.
    check_activation_eligibility = evaluate_activation_eligibility
    activation_eligibility = evaluate_activation_eligibility

    def guard_activation(
        self,
        subject: DomainPack | Registration | WorkflowActivation | DomainPackId | str,
        immutable_version: str | None = None,
        *,
        pack_contract: PackContract | None = None,
        host_contract: HostContract | None = None,
        alc_contract: AgentLearningContract | None = None,
        evaluation_references: Iterable[str] | None = None,
        correlation_id: CorrelationId | None = None,
    ) -> CommandOutcome[object]:
        """Deny activation unless compatibility and onboarding evidence are complete."""
        correlation = correlation_id or new_correlation_id()
        if isinstance(subject, DomainPack):
            eligibility = self.evaluate_activation_eligibility(
                subject,
                pack_contract,
                host_contract=host_contract,
                alc_contract=alc_contract,
                evaluation_references=evaluation_references,
            )
            if not eligibility.eligible:
                return Denied(self._activation_reason(eligibility), correlation)
            return Allowed(
                value=subject,
                evidence=(
                    self._compatibility_evidence(subject.pack_id, subject.immutable_version),
                ),
                correlation_id=correlation,
            )

        if isinstance(subject, Registration) and (
            subject.decision is not RegistrationDecision.APPROVED
            or not subject.validation_result
            or not subject.policy_passed
            or bool(subject.failed_validation_categories)
        ):
            return Denied(
                "Domain_Pack activation is denied until Pack_Contract admission succeeds.",
                correlation,
            )

        pack_id, version, status = self._subject_identity(subject, immutable_version)
        if status is not CompatibilityStatus.COMPATIBLE:
            return Denied(
                "Domain_Pack activation is denied until compatibility is compatible.",
                correlation,
            )
        return Allowed(
            value=subject,
            evidence=(self._compatibility_evidence(pack_id, version),),
            correlation_id=correlation,
        )

    def guard_invocation(
        self,
        subject: DomainPack | Registration | WorkflowActivation | DomainPackId | str,
        immutable_version: str | None = None,
        *,
        correlation_id: CorrelationId | None = None,
    ) -> CommandOutcome[object]:
        """Deny every invocation submission unless the pack version is compatible."""
        correlation = correlation_id or new_correlation_id()
        pack_id, version, status = self._subject_identity(subject, immutable_version)
        if status is not CompatibilityStatus.COMPATIBLE:
            return Denied(
                "Invocation submission is denied until Domain_Pack compatibility is compatible.",
                correlation,
            )
        return Allowed(
            value=subject,
            evidence=(self._compatibility_evidence(pack_id, version),),
            correlation_id=correlation,
        )

    # Short aliases make the guards convenient at submission boundaries.
    check_activation = guard_activation
    check_invocation = guard_invocation
    check_invocation_submission = guard_invocation

    def can_activate(
        self,
        subject: DomainPack | Registration | WorkflowActivation | DomainPackId | str,
        immutable_version: str | None = None,
        *,
        pack_contract: PackContract | None = None,
        host_contract: HostContract | None = None,
        alc_contract: AgentLearningContract | None = None,
        evaluation_references: Iterable[str] | None = None,
        correlation_id: CorrelationId | None = None,
    ) -> bool:
        """Return whether the activation guard explicitly allows the subject."""
        return bool(
            self.guard_activation(
                subject,
                immutable_version,
                pack_contract=pack_contract,
                host_contract=host_contract,
                alc_contract=alc_contract,
                evaluation_references=evaluation_references,
                correlation_id=correlation_id,
            )
        )

    def can_submit_invocation(
        self,
        subject: DomainPack | Registration | WorkflowActivation | DomainPackId | str,
        immutable_version: str | None = None,
        *,
        correlation_id: CorrelationId | None = None,
    ) -> bool:
        """Return whether an invocation submission may proceed."""
        return bool(
            self.guard_invocation(
                subject,
                immutable_version,
                correlation_id=correlation_id,
            )
        )

    def record_supported_combination(
        self,
        host_contract: HostContract | str,
        pack_contract: PackContract | str,
        alc_contract: AgentLearningContract | str,
        *,
        pack: DomainPack | None = None,
    ) -> Result[CompatibilityMatrixEntry, RepositoryError]:
        """Record a designated combination after validating its supported status."""
        host_version = self._version_of(host_contract, "host_contract_version")
        pack_contract_version = self._version_of(pack_contract, "pack_contract_version")
        alc_version = self._version_of(alc_contract, "alc_version")
        if isinstance(host_contract, HostContract):
            supported = host_contract.supported_pack_range.contains(pack_contract_version) and (
                host_contract.supported_alc_range.contains(alc_version)
            )
        else:
            supported = True
        status = CompatibilityStatus.COMPATIBLE if supported else CompatibilityStatus.INCOMPATIBLE
        if pack is not None:
            if not isinstance(host_contract, HostContract) or not isinstance(
                alc_contract, AgentLearningContract
            ):
                raise ValueError(
                    "A DomainPack evaluation requires HostContract and "
                    "AgentLearningContract objects."
                )
            evaluation = self.evaluate_detailed(pack, host_contract, alc_contract)
            status = evaluation.status
        entry = CompatibilityMatrixEntry(
            pack_contract_version=pack_contract_version,
            host_contract_version=host_version,
            alc_version=alc_version,
            status=status,
            pack_id=pack.pack_id if pack is not None else None,
            immutable_version=pack.immutable_version if pack is not None else None,
            evidence_reference=(
                f"compatibility:{pack.pack_id}:{pack.immutable_version}"
                if pack is not None
                else f"compatibility:{pack_contract_version}:{host_version}:{alc_version}"
            ),
        )
        return self._matrix_repository.append(entry)

    designate_supported_combination = record_supported_combination
    record_designated_combination = record_supported_combination

    @staticmethod
    def _declared_ranges(
        declared: DomainPack | DeclaredCompatibilityRanges | CompatibilityRange,
        pack_alc_range: CompatibilityRange | None,
    ) -> tuple[CompatibilityRange, CompatibilityRange, DomainPackId | None, str | None, str | None]:
        if isinstance(declared, DomainPack):
            return (
                declared.host_range,
                declared.alc_range,
                declared.pack_id,
                declared.immutable_version,
                declared.pack_contract_version,
            )
        if isinstance(declared, DeclaredCompatibilityRanges):
            return (
                declared.host_range,
                declared.alc_range,
                declared.pack_id,
                declared.immutable_version,
                None,
            )
        return declared, pack_alc_range or declared, None, None, None

    @staticmethod
    def _supported_ranges(
        supported_host: HostContract | CompatibilityRange,
        supported_alc: AgentLearningContract | CompatibilityRange | None,
    ) -> tuple[CompatibilityRange, CompatibilityRange, str | None, str | None]:
        alc_range: CompatibilityRange | None
        if isinstance(supported_host, HostContract):
            host_range = CompatibilityRange.exact(supported_host.version)
            alc_range = supported_host.supported_alc_range
            host_version = supported_host.version
        else:
            host_range = supported_host
            alc_range = supported_alc if isinstance(supported_alc, CompatibilityRange) else None
            host_version = None
        actual_alc = (
            supported_alc.version if isinstance(supported_alc, AgentLearningContract) else None
        )
        if alc_range is None:
            assert actual_alc is not None
            alc_range = CompatibilityRange.exact(actual_alc)
        return host_range, alc_range, host_version, actual_alc

    def _subject_identity(
        self,
        subject: DomainPack | Registration | WorkflowActivation | DomainPackId | str,
        immutable_version: str | None,
    ) -> tuple[DomainPackId, str, CompatibilityStatus]:
        if isinstance(subject, DomainPack):
            return (
                subject.pack_id,
                subject.immutable_version,
                self.status_for(subject.pack_id, subject.immutable_version),
            )
        if isinstance(subject, Registration):
            return subject.pack_id, subject.immutable_version, subject.compatibility_status
        if isinstance(subject, WorkflowActivation):
            return subject.pack_id, subject.immutable_version, subject.compatibility_status
        if immutable_version is None:
            raise ValueError("An immutable pack version is required for a compatibility guard.")
        return DomainPackId(str(subject)), immutable_version, CompatibilityStatus.NOT_EVALUATED

    @staticmethod
    def _version_of(
        value: HostContract | PackContract | AgentLearningContract | str, name: str
    ) -> str:
        if isinstance(value, (HostContract, PackContract, AgentLearningContract)):
            return value.version
        return validate_semantic_version(value, name)

    @staticmethod
    def _compatibility_evidence(pack_id: DomainPackId, version: str) -> EvidenceId:
        return EvidenceId(f"compatibility:{pack_id}:{version}")

    @staticmethod
    def _activation_reason(eligibility: ActivationEligibility) -> str:
        if eligibility.failure_reasons:
            return (
                "Domain_Pack activation is denied: " + ", ".join(eligibility.failure_reasons) + "."
            )
        return "Domain_Pack activation is denied until all compatibility and onboarding gates pass."


class ActivationGuard:
    """Callable activation boundary backed by one compatibility registry."""

    def __init__(self, registry: CompatibilityRegistry) -> None:
        self._registry = registry

    def check(
        self,
        subject: DomainPack | Registration | WorkflowActivation | DomainPackId | str,
        immutable_version: str | None = None,
        *,
        pack_contract: PackContract | None = None,
        host_contract: HostContract | None = None,
        alc_contract: AgentLearningContract | None = None,
        evaluation_references: Iterable[str] | None = None,
        correlation_id: CorrelationId | None = None,
    ) -> CommandOutcome[object]:
        """Return an explicit allow or denial for activation."""
        return self._registry.guard_activation(
            subject,
            immutable_version,
            pack_contract=pack_contract,
            host_contract=host_contract,
            alc_contract=alc_contract,
            evaluation_references=evaluation_references,
            correlation_id=correlation_id,
        )

    __call__ = check


class InvocationGuard:
    """Callable invocation-submission boundary backed by one compatibility registry."""

    def __init__(self, registry: CompatibilityRegistry) -> None:
        self._registry = registry

    def check(
        self,
        subject: DomainPack | Registration | WorkflowActivation | DomainPackId | str,
        immutable_version: str | None = None,
        *,
        correlation_id: CorrelationId | None = None,
    ) -> CommandOutcome[object]:
        """Return an explicit allow or denial for invocation submission."""
        return self._registry.guard_invocation(
            subject,
            immutable_version,
            correlation_id=correlation_id,
        )

    __call__ = check


# Compatibility aliases for callers that use the shorter registry terminology.
CompatibilityService = CompatibilityRegistry
InMemoryCompatibilityMatrix = InMemoryCompatibilityMatrixRepository
