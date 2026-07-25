"""Fail-closed Pack_Contract admission and declarative VA package checks."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol, TypeGuard, cast

from app.models.common import SCHEMA_VERSION, CompatibilityRange, RecordMetadata, utc_now
from app.models.contracts import (
    AgentLearningContract,
    DomainPack,
    ErrorCode,
    ErrorDetail,
    ErrorField,
    HostContract,
    PackContract,
    RepositoryError,
    Result,
)
from app.models.control_plane import (
    AuditRecord,
    CompatibilityStatus,
    Registration,
    RegistrationDecision,
    RegistrationId,
)
from app.models.identifiers import (
    ActorId,
    AgentId,
    CorrelationId,
    DomainPackId,
    OrganizationId,
    new_correlation_id,
    new_record_id,
)
from app.registry.pack_validator import DomainPackValidator
from app.repositories.pack_repository import InMemoryPackRepository, ValidationIssue

if TYPE_CHECKING:
    from app.repositories.protocols import AuditRecordRepository, RegistrationRepository


class RegistrationPolicy(Protocol):
    """Host admission policy evaluated after Pack_Contract validation."""

    def evaluate(self, pack: DomainPack) -> bool | PolicyDecision: ...


@dataclass(frozen=True, slots=True)
class PolicyDecision:
    """Small policy result that keeps a redaction-safe failure category."""

    passed: bool
    category: str = "registration_policy"
    reason: str = "Registration policy did not pass."


PolicyCallable = Callable[[DomainPack], bool | PolicyDecision]
Policy = RegistrationPolicy | PolicyCallable
_DEFAULT_ORGANIZATION_ID = OrganizationId("host")


@dataclass(frozen=True, slots=True)
class _AdmissionInput:
    pack: DomainPack | None
    issues: tuple[ValidationIssue, ...]


class PackAdmission:
    """Admit immutable domain packs without persisting incomplete decisions.

    A rejected submission is represented by a typed error and one best-effort audit
    record.  Only an approved, fully validated pack is appended to the registration
    repository; audit persistence can never turn a rejection into an approval.
    """

    def __init__(
        self,
        registration_repository: RegistrationRepository | InMemoryPackRepository,
        audit_repository: AuditRecordRepository | None = None,
        *,
        pack_contract: PackContract | None = None,
        policies: Iterable[Policy] = (),
        validator: DomainPackValidator | None = None,
        trusted_signers: Iterable[ActorId | str] = (),
    ) -> None:
        self._registration_repository = registration_repository
        self._audit_repository = audit_repository
        self._pack_contract = pack_contract or PackContract(version="1.0.0")
        self._policies = tuple(policies)
        self._validator = validator or DomainPackValidator(InMemoryPackRepository())
        self._trusted_signers = frozenset(str(signer) for signer in trusted_signers)

    def register(
        self,
        pack: object,
        signer: ActorId | str | None = None,
        correlation_id: CorrelationId | None = None,
        *,
        organization_id: OrganizationId = _DEFAULT_ORGANIZATION_ID,
        pack_contract: PackContract | None = None,
        policies: Iterable[Policy] | None = None,
        host_contract: HostContract | None = None,
        alc_contract: AgentLearningContract | str | None = None,
    ) -> Result[Registration, RepositoryError]:
        """Validate and append one approved Pack_Contract registration."""
        effective_correlation = correlation_id or new_correlation_id()
        contract = pack_contract or self._pack_contract
        admission_input = self._coerce_pack(pack)
        effective_pack = admission_input.pack
        issues = list(admission_input.issues)
        raw_code_locations = (
            DomainPackValidator.executable_code_locations(pack) if isinstance(pack, Mapping) else ()
        )

        if effective_pack is not None and raw_code_locations:
            existing = self._get_registration(
                organization_id, effective_pack.pack_id, effective_pack.immutable_version
            )
            if (
                existing.is_success
                and existing.value is not None
                and existing.value.decision is RegistrationDecision.APPROVED
            ):
                return Result.success(existing.value)

        if effective_pack is not None:
            issues.extend(
                self._validator.validate_pack(
                    effective_pack,
                    contract,
                    raw_manifest=pack if isinstance(pack, Mapping) else None,
                )
            )
            issues.extend(self._signer_issues(effective_pack, signer))
            issues.extend(self._policy_issues(effective_pack, policies))

        if issues or effective_pack is None:
            categories = self._categories(
                issues
                or [
                    ValidationIssue(
                        "manifest", "invalid_manifest", "Manifest could not be admitted."
                    )
                ]
            )
            self._best_effort_rejection_audit(
                effective_pack,
                categories,
                effective_correlation,
                organization_id,
                executable_code_locations=tuple(
                    issue.field for issue in issues if issue.code == "executable_code"
                ),
            )
            return Result.failure(
                ErrorDetail(
                    ErrorCode.VALIDATION_FAILED,
                    "Domain_Pack registration was rejected.",
                    effective_correlation,
                    fields=tuple(
                        ErrorField(category, "validation failed") for category in categories
                    ),
                )
            )

        registration = self._registration_for(
            effective_pack,
            organization_id=organization_id,
            correlation_id=effective_correlation,
            host_contract=host_contract,
            alc_contract=alc_contract,
        )
        return self._append_registration(registration)

    def admit(
        self,
        pack: object,
        signer: ActorId | str | None = None,
        correlation_id: CorrelationId | None = None,
        *,
        organization_id: OrganizationId = _DEFAULT_ORGANIZATION_ID,
        pack_contract: PackContract | None = None,
        policies: Iterable[Policy] | None = None,
        host_contract: HostContract | None = None,
        alc_contract: AgentLearningContract | str | None = None,
    ) -> Result[Registration, RepositoryError]:
        """Compatibility alias for callers that use the admission terminology."""
        return self.register(
            pack,
            signer,
            correlation_id,
            organization_id=organization_id,
            pack_contract=pack_contract,
            policies=policies,
            host_contract=host_contract,
            alc_contract=alc_contract,
        )

    def report_late_executable_code(
        self,
        pack_id: DomainPackId | str,
        immutable_version: str,
        code_location: str,
        *,
        organization_id: OrganizationId = _DEFAULT_ORGANIZATION_ID,
    ) -> Result[Registration, RepositoryError]:
        """Return an already-approved record without revoking its operations.

        Late scanning is observational for a registration that already succeeded.
        The immutable registration is intentionally not replaced or marked rejected.
        """
        existing = self._get_registration(
            organization_id, DomainPackId(str(pack_id)), immutable_version
        )
        if not existing.is_success:
            return existing
        record = existing.value
        assert record is not None
        return Result.success(record)

    # Descriptive aliases used by scanners and migration integrations.
    late_code_detection = report_late_executable_code
    detect_late_executable_code = report_late_executable_code

    def _coerce_pack(self, value: object) -> _AdmissionInput:
        if isinstance(value, DomainPack):
            return _AdmissionInput(value, ())
        if not isinstance(value, Mapping):
            return _AdmissionInput(
                None,
                (ValidationIssue("manifest", "invalid_type", "Domain_Pack must be an object."),),
            )
        try:
            pack = self._pack_from_manifest(value)
        except (TypeError, ValueError, KeyError) as error:
            return _AdmissionInput(
                None,
                (ValidationIssue("manifest", "invalid_manifest", str(error)),),
            )
        return _AdmissionInput(pack, ())

    @staticmethod
    def _pack_from_manifest(values: Mapping[str, object]) -> DomainPack:
        def required_text(name: str) -> str:
            value = values.get(name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} is required.")
            return value

        def required_values(name: str) -> tuple[str, ...]:
            value = values.get(name)
            if not isinstance(value, (list, tuple)):
                raise ValueError(f"{name} is required and must be an array.")
            result = tuple(
                str(item.get("agent_id"))
                if name == "agents" and isinstance(item, Mapping)
                else str(item)
                for item in value
            )
            if not result or any(not item.strip() for item in result):
                raise ValueError(f"{name} must contain non-empty values.")
            return result

        def compatibility_range(name: str, alias: str) -> CompatibilityRange:
            raw = values.get(name, values.get(alias))
            if isinstance(raw, CompatibilityRange):
                return raw
            if not isinstance(raw, Mapping):
                raise ValueError(f"{name} is required and must be a range object.")
            return CompatibilityRange(
                minimum=raw.get("minimum", raw.get("min_version")),
                maximum=raw.get("maximum", raw.get("max_version")),
                include_minimum=bool(raw.get("include_minimum", True)),
                include_maximum=bool(raw.get("include_maximum", True)),
            )

        raw_assets = values.get("asset_references", values.get("assets", ()))
        if not isinstance(raw_assets, (list, tuple)):
            raise ValueError("asset_references must be an array.")
        asset_references: list[str] = []
        for asset in raw_assets:
            if isinstance(asset, Mapping):
                reference = str(asset.get("reference", "")).strip()
                version = str(asset.get("version", "")).strip()
                digest = str(asset.get("digest", "")).strip()
                asset_references.append(f"{reference}@{version}#{digest}")
            else:
                asset_references.append(str(asset))

        return DomainPack(
            pack_id=DomainPackId(required_text("pack_id")),
            immutable_version=required_text("immutable_version"),
            pack_contract_version=str(values.get("pack_contract_version", "1.0.0")),
            host_compatibility_range=compatibility_range("host_compatibility_range", "host_range"),
            alc_compatibility_range=compatibility_range("alc_compatibility_range", "alc_range"),
            content_digest=required_text("content_digest"),
            signer_id=ActorId(required_text("signer_id")),
            agents=tuple(AgentId(value) for value in required_values("agents")),
            workflows=required_values("workflows"),
            capabilities=required_values("capabilities"),
            data_classifications=required_values("data_classifications"),
            evaluation_references=required_values("evaluation_references"),
            required_alc_version=required_text("required_alc_version"),
            asset_references=tuple(asset_references),
        )

    def _signer_issues(
        self, pack: DomainPack, supplied_signer: ActorId | str | None
    ) -> tuple[ValidationIssue, ...]:
        issues: list[ValidationIssue] = []
        if supplied_signer is not None and str(supplied_signer) != str(pack.signer_id):
            issues.append(
                ValidationIssue(
                    "signer_id",
                    "signer_mismatch",
                    "Submitted signer does not match the pack signer.",
                )
            )
        if self._trusted_signers and str(pack.signer_id) not in self._trusted_signers:
            issues.append(
                ValidationIssue(
                    "signer_id", "untrusted_signer", "Pack signer is not trusted by the host."
                )
            )
        return tuple(issues)

    def _policy_issues(
        self, pack: DomainPack, policies: Iterable[Policy] | None
    ) -> tuple[ValidationIssue, ...]:
        issues: list[ValidationIssue] = []
        for index, policy in enumerate(self._policies if policies is None else tuple(policies)):
            try:
                applies_to = getattr(policy, "applies_to", None)
                if callable(applies_to) and not bool(applies_to(pack)):
                    continue
                policy_value: object = policy
                outcome = (
                    policy_value(pack)
                    if callable(policy_value)
                    else cast(RegistrationPolicy, policy_value).evaluate(pack)
                )
                if isinstance(outcome, PolicyDecision):
                    decision = outcome
                elif isinstance(outcome, bool):
                    decision = PolicyDecision(outcome, f"registration_policy_{index}")
                else:
                    decision = PolicyDecision(bool(getattr(outcome, "passed", False)))
            except Exception:
                decision = PolicyDecision(
                    False, f"registration_policy_{index}", "Policy evaluation failed."
                )
            if not decision.passed:
                issues.append(
                    ValidationIssue("registration_policy", decision.category, decision.reason)
                )
        return tuple(issues)

    def _registration_for(
        self,
        pack: DomainPack,
        *,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        host_contract: HostContract | None,
        alc_contract: AgentLearningContract | str | None,
    ) -> Registration:
        host_version = host_contract.version if host_contract is not None else None
        if isinstance(alc_contract, AgentLearningContract):
            alc_version: str | None = alc_contract.version
        elif alc_contract is None:
            alc_version = pack.required_alc_version
        else:
            alc_version = str(alc_contract)
        prior = self._list_registrations(organization_id, pack.pack_id)
        reproduction: list[str] = []
        for record in prior:
            if record.decision is RegistrationDecision.APPROVED:
                reproduction.extend(
                    (
                        f"registration:{record.registration_id}",
                        f"pack:{record.pack_id}@{record.immutable_version}",
                    )
                )
                if record.host_contract_version:
                    reproduction.append(f"host-contract:{record.host_contract_version}")
                if record.alc_version:
                    reproduction.append(f"alc:{record.alc_version}")
        return Registration(
            metadata=RecordMetadata(
                record_id=new_record_id(),
                organization_id=organization_id,
                correlation_id=correlation_id,
                schema_version=SCHEMA_VERSION,
                version=1,
                created_at=utc_now(),
                updated_at=utc_now(),
            ),
            registration_id=RegistrationId(str(new_record_id())),
            pack_id=pack.pack_id,
            immutable_version=pack.immutable_version,
            content_digest=pack.content_digest,
            signer_id=pack.signer_id,
            host_compatibility_range=pack.host_range,
            alc_compatibility_range=pack.alc_range,
            validation_result=True,
            decision=RegistrationDecision.APPROVED,
            asset_references=pack.asset_references,
            policy_passed=True,
            compatibility_status=CompatibilityStatus.NOT_EVALUATED,
            host_contract_version=host_version,
            alc_version=alc_version,
            reproduction_references=tuple(dict.fromkeys(reproduction)),
        )

    def _append_registration(
        self, registration: Registration
    ) -> Result[Registration, RepositoryError]:
        append = getattr(self._registration_repository, "append", None)
        if not callable(append):
            return Result.failure(
                ErrorDetail(
                    ErrorCode.REPOSITORY_UNAVAILABLE,
                    "Registration persistence is unavailable.",
                    registration.metadata.correlation_id,
                    retryable=True,
                )
            )
        try:
            return cast(Result[Registration, RepositoryError], append(registration))
        except Exception:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.REPOSITORY_UNAVAILABLE,
                    "Registration persistence is unavailable.",
                    registration.metadata.correlation_id,
                    retryable=True,
                )
            )

    def _get_registration(
        self, organization_id: OrganizationId, pack_id: DomainPackId, version: str
    ) -> Result[Registration, RepositoryError]:
        getter = getattr(self._registration_repository, "get_by_pack_version", None)
        if not callable(getter):
            return Result.failure(
                ErrorDetail(
                    ErrorCode.NOT_FOUND, "Registered pack was not found.", new_correlation_id()
                )
            )
        return cast(
            Result[Registration, RepositoryError], getter(organization_id, pack_id, version)
        )

    def _list_registrations(
        self, organization_id: OrganizationId, pack_id: DomainPackId
    ) -> tuple[Registration, ...]:
        listing = getattr(self._registration_repository, "list_for_organization", None)
        if not callable(listing):
            return ()
        result = cast(Result[tuple[Registration, ...], RepositoryError], listing(organization_id))
        if not result.is_success or result.value is None:
            return ()
        return tuple(record for record in result.value if record.pack_id == pack_id)

    def _best_effort_rejection_audit(
        self,
        pack: DomainPack | None,
        categories: tuple[str, ...],
        correlation_id: CorrelationId,
        organization_id: OrganizationId,
        *,
        executable_code_locations: tuple[str, ...] = (),
    ) -> None:
        if self._audit_repository is None:
            return
        pack_reference = "unknown-pack"
        if pack is not None:
            pack_reference = f"{pack.pack_id}@{pack.immutable_version}"
        action = (
            "pack.registration.rejected.executable_code"
            if executable_code_locations
            else "pack.registration.rejected"
        )
        outcome = "rejected:" + ",".join(categories)
        if executable_code_locations:
            outcome += ";code_locations=" + ",".join(executable_code_locations)
        audit = AuditRecord(
            metadata=RecordMetadata(
                record_id=new_record_id(),
                organization_id=organization_id,
                correlation_id=correlation_id,
                schema_version=SCHEMA_VERSION,
                version=1,
                created_at=utc_now(),
                updated_at=utc_now(),
            ),
            audit_id=str(new_record_id()),
            action=action,
            subject_reference=pack_reference,
            outcome=outcome,
            recorded_at=utc_now(),
        )
        try:
            self._audit_repository.append(audit)
        except Exception:
            return

    @staticmethod
    def _categories(issues: Sequence[ValidationIssue]) -> tuple[str, ...]:
        return tuple(dict.fromkeys(issue.code or issue.field for issue in issues))


def is_registration_policy(value: object) -> TypeGuard[Policy]:
    """Return whether a value can be used as a callable or policy object."""
    return callable(value) or callable(getattr(value, "evaluate", None))


# Names used by different composition roots retain one implementation.
AdmissionService = PackAdmission
PackAdmissionService = PackAdmission
