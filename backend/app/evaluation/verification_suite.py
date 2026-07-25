"""Deterministic, fail-closed orchestration for adoption release verification."""

from __future__ import annotations

import hashlib
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol, cast

from app.evidence.release_evidence import (
    CompatibilityEvidenceRecord,
    InMemoryReleaseEvidenceRepository,
    InMemoryReleaseReadinessRepository,
    ReleaseEvidenceBundle,
    ReleaseEvidenceRepository,
    ReleasePolicy,
    UIProjectionEvidence,
    VerificationCheckResult,
    VerificationFailureRecord,
    VerificationLayer,
    VerificationOutcome,
    build_metadata,
)
from app.models.common import utc_now, validate_semantic_version
from app.models.contracts import (
    DomainPack,
    ErrorCode,
    ErrorDetail,
    PackContract,
    RepositoryError,
    Result,
)
from app.models.control_plane import (
    ArtifactHandoff,
    AuditRecord,
    CompatibilityStatus,
    ReleaseReadinessDecision,
    ReleaseReadinessDecisionId,
    ReleaseReadinessStatus,
    VerificationCoverageStatus,
    VerificationRun,
    VerificationRunId,
)
from app.models.identifiers import (
    CorrelationId,
    DomainPackId,
    EvidenceId,
    OrganizationId,
    new_record_id,
)
from app.registry.compatibility import CompatibilityMatrixEntry, CompatibilityMatrixRepository
from app.repositories.protocols import (
    AuditRecordRepository,
    ReleaseReadinessDecisionRepository,
    VerificationRunRepository,
)


class CheckEvaluator(Protocol):
    """Callable shape accepted by a deterministic verification check."""

    def __call__(self) -> object: ...


@dataclass(frozen=True, slots=True)
class VerificationCheck:
    """One named check, optionally evaluated lazily by the suite."""

    name: str
    layer: VerificationLayer
    outcome: object = True
    evaluator: CheckEvaluator | None = None
    evidence_reference: str | None = None

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Verification check names must be non-empty.")
        object.__setattr__(self, "layer", VerificationLayer(self.layer))
        if self.evidence_reference is not None and not self.evidence_reference.strip():
            raise ValueError("Verification evidence references must be non-empty.")

    def evaluate(self) -> object:
        """Evaluate the check without exposing its result payload."""
        return self.evaluator() if self.evaluator is not None else self.outcome


@dataclass(frozen=True, slots=True)
class _NormalizedCheck:
    """Internal check form with an explicit stable name and layer."""

    name: str
    layer: VerificationLayer
    evaluator: CheckEvaluator
    evidence_reference: str | None


class VerificationSuite:
    """Run all configured verification layers and retain a terminal release decision."""

    def __init__(
        self,
        verification_repository: VerificationRunRepository | None = None,
        release_repository: ReleaseReadinessDecisionRepository | None = None,
        *,
        evidence_repository: ReleaseEvidenceRepository | None = None,
        compatibility_repository: CompatibilityMatrixRepository | None = None,
        audit_repository: AuditRecordRepository | None = None,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._verification_repository = verification_repository
        self._release_repository: ReleaseReadinessDecisionRepository = (
            release_repository
            if release_repository is not None
            else cast(
                ReleaseReadinessDecisionRepository,
                InMemoryReleaseReadinessRepository(),
            )
        )
        self._evidence_repository: ReleaseEvidenceRepository = (
            evidence_repository
            if evidence_repository is not None
            else InMemoryReleaseEvidenceRepository()
        )
        self._compatibility_repository = compatibility_repository
        self._audit_repository = audit_repository
        self._clock = clock

    @property
    def evidence_repository(self) -> ReleaseEvidenceRepository:
        """Expose the append-only release evidence seam for authorized inspection."""
        return self._evidence_repository

    @property
    def release_repository(self) -> ReleaseReadinessDecisionRepository:
        """Expose the terminal-decision repository used by this suite."""
        return self._release_repository

    def run(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        *,
        pack_id: DomainPackId,
        immutable_version: str,
        pack_contract_version: str,
        host_contract_version: str,
        alc_version: str,
        workflow_id: str = "adoption-release",
        fixed_seed: str = "adoption-redesign-seed",
        fixture_digest: str = "adoption-redesign-fixtures",
        schema_checks: Iterable[VerificationCheck | object] = (),
        unit_checks: Iterable[VerificationCheck | object] = (),
        property_checks: Iterable[VerificationCheck | object] = (),
        integration_checks: Iterable[VerificationCheck | object] = (),
        post_coverage_checks: Iterable[VerificationCheck | object] = (),
        compatibility_results: Iterable[
            CompatibilityMatrixEntry | CompatibilityEvidenceRecord
        ] = (),
        audits: Iterable[AuditRecord] = (),
        ui_projections: Iterable[UIProjectionEvidence | str] = (),
        release_policy: ReleasePolicy | None = None,
        administrative_failure: bool = False,
        release_gate_references: Iterable[str] = (),
        integration_coverage_complete: bool | None = None,
        initial_vertical: bool = False,
        pack_contract: PackContract | None = None,
        pack: DomainPack | None = None,
        handoffs: Iterable[ArtifactHandoff] = (),
    ) -> Result[ReleaseEvidenceBundle, ErrorDetail]:
        """Execute every supplied check and retain immutable verification evidence.

        A failure before the integration boundary never creates a failed terminal
        release decision.  A failure after that boundary does, while a failure
        record write outage is isolated from the remaining checks.
        """
        validation_error = self._validate_request(
            organization_id,
            pack_id,
            immutable_version,
            pack_contract_version,
            host_contract_version,
            alc_version,
            workflow_id,
            fixed_seed,
            fixture_digest,
        )
        if validation_error is not None:
            return Result.failure(
                ErrorDetail(ErrorCode.VALIDATION_FAILED, validation_error, correlation_id)
            )

        policy = release_policy or ReleasePolicy()
        normalized_layers: list[tuple[VerificationLayer, tuple[_NormalizedCheck, ...]]] = []
        raw_layers = (
            (VerificationLayer.SCHEMA, schema_checks),
            (VerificationLayer.UNIT, unit_checks),
            (VerificationLayer.PROPERTY, property_checks),
            (VerificationLayer.INTEGRATION, integration_checks),
        )
        try:
            for layer, checks in raw_layers:
                normalized_layers.append((layer, self._normalize_checks(layer, checks)))
            normalized_post = self._normalize_checks(
                VerificationLayer.PROPERTY, post_coverage_checks
            )
        except (TypeError, ValueError) as error:
            return Result.failure(
                ErrorDetail(ErrorCode.VALIDATION_FAILED, str(error), correlation_id)
            )

        compatibility = self._retain_compatibility(
            organization_id,
            correlation_id,
            compatibility_results,
        )
        if not compatibility.is_success or compatibility.value is None:
            return Result.failure(
                compatibility.error or self._repository_error(None, correlation_id)
            )
        retained_compatibility = compatibility.value

        retained_audits = self._retain_audits(correlation_id, audits)
        if not retained_audits.is_success or retained_audits.value is None:
            return Result.failure(
                retained_audits.error or self._repository_error(None, correlation_id)
            )
        audit_records = retained_audits.value

        retained_projections = self._retain_ui_projections(
            organization_id,
            correlation_id,
            fixed_seed,
            ui_projections,
        )
        if not retained_projections.is_success or retained_projections.value is None:
            return Result.failure(
                retained_projections.error or self._repository_error(None, correlation_id)
            )
        projection_records = retained_projections.value

        generated_schema_checks = list(normalized_layers[0][1])
        if pack_contract is not None and pack is not None:
            generated_schema_checks.append(
                self._schema_check(
                    "schema.pack-contract",
                    lambda: not pack_contract.validate(pack),
                )
            )
        if handoffs:
            generated_schema_checks.append(
                self._schema_check(
                    "schema.artifact-handoff-lineage",
                    lambda: self.validate_artifact_handoff_lineage(tuple(handoffs)),
                )
            )
        normalized_layers[0] = (VerificationLayer.SCHEMA, tuple(generated_schema_checks))

        results: list[VerificationCheckResult] = []
        retained_failures: list[VerificationFailureRecord] = []
        failure_references: list[str] = []
        post_coverage_failure_references: list[str] = []
        failure_persistence_errors: list[str] = []
        integration_complete = False

        for layer, checks in normalized_layers:
            for check in checks:
                result, failure = self._evaluate_check(
                    organization_id,
                    correlation_id,
                    check,
                    fixed_seed,
                    fixture_digest,
                    after_integration_coverage=integration_complete,
                )
                persisted_result = self._evidence_repository.append_check_result(result)
                if not persisted_result.is_success or persisted_result.value is None:
                    return Result.failure(
                        self._repository_error(persisted_result.error, correlation_id)
                    )
                results.append(persisted_result.value)
                if failure is not None:
                    failure_references.append(failure.failure_reference)
                    if integration_complete:
                        post_coverage_failure_references.append(failure.failure_reference)
                    retained = self._evidence_repository.append_failure(failure)
                    if retained.is_success and retained.value is not None:
                        retained_failures.append(retained.value)
                    else:
                        failure_persistence_errors.append(
                            self._failure_persistence_reference(failure, retained.error)
                        )
            if layer is VerificationLayer.INTEGRATION:
                integration_complete = (
                    bool(integration_coverage_complete)
                    if integration_coverage_complete is not None
                    else bool(checks)
                    and all(
                        result.passed
                        for result in results
                        if result.layer is VerificationLayer.INTEGRATION
                    )
                )

        for check in normalized_post:
            result, failure = self._evaluate_check(
                organization_id,
                correlation_id,
                check,
                fixed_seed,
                fixture_digest,
                after_integration_coverage=integration_complete,
            )
            persisted_result = self._evidence_repository.append_check_result(result)
            if not persisted_result.is_success or persisted_result.value is None:
                return Result.failure(
                    self._repository_error(persisted_result.error, correlation_id)
                )
            results.append(persisted_result.value)
            if failure is not None:
                failure_references.append(failure.failure_reference)
                if integration_complete:
                    post_coverage_failure_references.append(failure.failure_reference)
                retained = self._evidence_repository.append_failure(failure)
                if retained.is_success and retained.value is not None:
                    retained_failures.append(retained.value)
                else:
                    failure_persistence_errors.append(
                        self._failure_persistence_reference(failure, retained.error)
                    )

        coverage_status = (
            VerificationCoverageStatus.COMPLETE
            if integration_complete
            else VerificationCoverageStatus.INCOMPLETE
        )
        run = self._build_verification_run(
            organization_id,
            correlation_id,
            pack_id,
            immutable_version,
            pack_contract_version,
            host_contract_version,
            alc_version,
            fixed_seed,
            fixture_digest,
            results,
            coverage_status,
            failure_references,
        )
        retained_run = self._append_verification_run(run, correlation_id)
        if not retained_run.is_success or retained_run.value is None:
            return Result.failure(
                retained_run.error or self._repository_error(None, correlation_id)
            )
        run = retained_run.value

        administrative_reference = policy.administrative_failure_reference
        if administrative_failure:
            if not policy.allow_administrative_failure or administrative_reference is None:
                return Result.failure(
                    ErrorDetail(
                        ErrorCode.AUTHORIZATION_DENIED,
                        "Release policy does not authorize an administrative failure decision.",
                        correlation_id,
                    )
                )
            failure_references.append(administrative_reference)

        release_decision = self._decision_for(
            organization_id,
            correlation_id,
            pack_id,
            immutable_version,
            workflow_id,
            run,
            results,
            integration_complete,
            initial_vertical,
            policy,
            administrative_failure,
            tuple(failure_references),
            tuple(post_coverage_failure_references),
            tuple(release_gate_references),
        )
        if release_decision is not None:
            persisted_decision = self._release_repository.append(release_decision)
            if not persisted_decision.is_success or persisted_decision.value is None:
                return Result.failure(
                    self._repository_error(persisted_decision.error, correlation_id)
                )
            release_decision = persisted_decision.value

        return Result.success(
            ReleaseEvidenceBundle(
                verification_run=run,
                check_results=tuple(results),
                failure_records=tuple(retained_failures),
                compatibility_results=tuple(retained_compatibility),
                audit_records=audit_records,
                ui_projections=projection_records,
                release_decision=release_decision,
                failure_persistence_errors=tuple(failure_persistence_errors),
            )
        )

    execute = run
    verify_release = run
    run_verification = run
    run_suite = run
    verify = run

    def record_compatibility_result(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        entry: CompatibilityMatrixEntry | CompatibilityEvidenceRecord,
    ) -> Result[CompatibilityEvidenceRecord, ErrorDetail]:
        """Retain one designated supported-version compatibility result."""
        retained = self._retain_compatibility(organization_id, correlation_id, (entry,))
        if not retained.is_success or retained.value is None:
            return Result.failure(retained.error or self._repository_error(None, correlation_id))
        return Result.success(retained.value[0])

    record_compatibility = record_compatibility_result

    @staticmethod
    def validate_pack_contract(contract: PackContract, pack: DomainPack) -> bool:
        """Return true only when every Pack_Contract category validates."""
        return not contract.validate(pack)

    @staticmethod
    def validate_artifact_handoff_lineage(handoffs: Sequence[ArtifactHandoff]) -> bool:
        """Return true when handoff parent references form an acyclic graph."""
        parents = {str(handoff.handoff_id): tuple(handoff.parent_lineage) for handoff in handoffs}
        if len(parents) != len(handoffs):
            return False
        if any(node_id in references for node_id, references in parents.items()):
            return False

        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(node_id: str) -> bool:
            if node_id in visiting:
                return False
            if node_id in visited:
                return True
            visiting.add(node_id)
            if any(parent in parents and not visit(parent) for parent in parents.get(node_id, ())):
                return False
            visiting.remove(node_id)
            visited.add(node_id)
            return True

        return all(visit(node_id) for node_id in parents)

    def _normalize_checks(
        self,
        layer: VerificationLayer,
        checks: Iterable[VerificationCheck | object],
    ) -> tuple[_NormalizedCheck, ...]:
        normalized: list[_NormalizedCheck] = []
        for index, candidate in enumerate(checks):
            if isinstance(candidate, VerificationCheck):
                check = candidate
                if check.layer is not layer:
                    check = VerificationCheck(
                        name=check.name,
                        layer=layer,
                        outcome=check.outcome,
                        evaluator=check.evaluator,
                        evidence_reference=check.evidence_reference,
                    )
                evaluator = check.evaluate
                normalized.append(
                    _NormalizedCheck(check.name, layer, evaluator, check.evidence_reference)
                )
                continue
            if isinstance(candidate, tuple) and len(candidate) == 2:
                name, outcome = candidate
                if not isinstance(name, str) or not name.strip():
                    raise ValueError("Tuple verification checks require a non-empty name.")
                normalized.append(_NormalizedCheck(name, layer, self._as_evaluator(outcome), None))
                continue
            normalized.append(
                _NormalizedCheck(
                    f"{layer.value}.{index + 1}",
                    layer,
                    self._as_evaluator(candidate),
                    None,
                )
            )
        return tuple(normalized)

    @staticmethod
    def _as_evaluator(value: object) -> CheckEvaluator:
        if callable(value):
            return value
        return lambda: value

    @staticmethod
    def _schema_check(name: str, evaluator: CheckEvaluator) -> _NormalizedCheck:
        return _NormalizedCheck(name, VerificationLayer.SCHEMA, evaluator, None)

    def _evaluate_check(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        check: _NormalizedCheck,
        fixed_seed: str,
        fixture_digest: str,
        *,
        after_integration_coverage: bool,
    ) -> tuple[VerificationCheckResult, VerificationFailureRecord | None]:
        passed = True
        try:
            value = check.evaluator()
            if isinstance(value, VerificationOutcome):
                passed = value is VerificationOutcome.PASS
            elif isinstance(value, bool):
                passed = value
            else:
                success = getattr(value, "is_success", None)
                allowed = getattr(value, "is_allowed", None)
                if isinstance(success, bool):
                    passed = success
                elif isinstance(allowed, bool):
                    passed = allowed
                else:
                    passed = bool(value)
        except Exception as error:  # pragma: no cover - exercised by resilience tests
            passed = False
            failure_digest = self._digest(f"{type(error).__name__}:{error!s}")
        else:
            failure_digest = self._digest(f"{check.layer.value}:{check.name}:{fixed_seed}")

        evidence_digest = check.evidence_reference or self._digest(
            f"{check.layer.value}:{check.name}:{fixed_seed}:{fixture_digest}:{passed}"
        )
        evidence_id = EvidenceId(str(new_record_id()))
        failure_reference = None
        failure = None
        if not passed:
            failure_reference = f"failure:{check.layer.value}:{check.name}:{failure_digest[:24]}"
            timestamp = self._clock()
            failure = VerificationFailureRecord(
                metadata=build_metadata(organization_id, correlation_id, timestamp),
                failure_id=EvidenceId(str(new_record_id())),
                verification_evidence_id=evidence_id,
                layer=check.layer,
                check_name=check.name,
                failure_reference=failure_reference,
                failure_digest=failure_digest,
                recorded_at=timestamp,
                after_integration_coverage=after_integration_coverage,
            )
        timestamp = self._clock()
        result = VerificationCheckResult(
            metadata=build_metadata(organization_id, correlation_id, timestamp),
            evidence_id=evidence_id,
            layer=check.layer,
            check_name=check.name,
            outcome=VerificationOutcome.PASS if passed else VerificationOutcome.FAIL,
            evidence_digest=evidence_digest,
            fixed_seed=fixed_seed,
            fixture_digest=fixture_digest,
            recorded_at=timestamp,
            supporting_references=(check.evidence_reference,) if check.evidence_reference else (),
            failure_reference=failure_reference,
        )
        return result, failure

    def _build_verification_run(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        pack_id: DomainPackId,
        immutable_version: str,
        pack_contract_version: str,
        host_contract_version: str,
        alc_version: str,
        fixed_seed: str,
        fixture_digest: str,
        results: Sequence[VerificationCheckResult],
        coverage_status: VerificationCoverageStatus,
        failure_references: Iterable[str],
    ) -> VerificationRun:
        references = {
            VerificationLayer.SCHEMA: tuple(
                str(result.evidence_id)
                for result in results
                if result.layer is VerificationLayer.SCHEMA
            ),
            VerificationLayer.UNIT: tuple(
                str(result.evidence_id)
                for result in results
                if result.layer is VerificationLayer.UNIT
            ),
            VerificationLayer.PROPERTY: tuple(
                str(result.evidence_id)
                for result in results
                if result.layer is VerificationLayer.PROPERTY
            ),
            VerificationLayer.INTEGRATION: tuple(
                str(result.evidence_id)
                for result in results
                if result.layer is VerificationLayer.INTEGRATION
            ),
        }
        return VerificationRun(
            metadata=build_metadata(organization_id, correlation_id, self._clock()),
            verification_run_id=VerificationRunId(str(new_record_id())),
            pack_id=pack_id,
            immutable_version=immutable_version,
            pack_contract_version=pack_contract_version,
            host_contract_version=host_contract_version,
            alc_version=alc_version,
            schema_evidence_references=references[VerificationLayer.SCHEMA],
            unit_evidence_references=references[VerificationLayer.UNIT],
            property_evidence_references=references[VerificationLayer.PROPERTY],
            integration_evidence_references=references[VerificationLayer.INTEGRATION],
            coverage_status=coverage_status,
            fixed_seed=fixed_seed,
            fixture_digest=fixture_digest,
            failure_evidence_references=tuple(dict.fromkeys(failure_references)),
        )

    def _decision_for(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        pack_id: DomainPackId,
        immutable_version: str,
        workflow_id: str,
        run: VerificationRun,
        results: Sequence[VerificationCheckResult],
        integration_complete: bool,
        initial_vertical: bool,
        policy: ReleasePolicy,
        administrative_failure: bool,
        failure_references: tuple[str, ...],
        post_coverage_failure_references: tuple[str, ...],
        release_gate_references: tuple[str, ...],
    ) -> ReleaseReadinessDecision | None:
        has_failures = any(result.failed for result in results)
        post_coverage_failure = bool(post_coverage_failure_references)
        if administrative_failure or post_coverage_failure:
            status = ReleaseReadinessStatus.FAILED
        elif has_failures:
            return None
        elif release_gate_references:
            status = ReleaseReadinessStatus.BLOCKED
        elif integration_complete or initial_vertical or policy.allow_incomplete_coverage:
            status = ReleaseReadinessStatus.ELIGIBLE
        else:
            status = ReleaseReadinessStatus.BLOCKED
            release_gate_references = (*release_gate_references, "gate:integration-coverage")

        evidence_references = tuple(
            dict.fromkeys(
                (
                    f"verification:{run.verification_run_id}",
                    *run.schema_evidence_references,
                    *run.unit_evidence_references,
                    *run.property_evidence_references,
                    *run.integration_evidence_references,
                )
            )
        )
        if not evidence_references:
            evidence_references = (f"verification:{run.verification_run_id}",)
        timestamp = self._clock()
        return ReleaseReadinessDecision(
            metadata=build_metadata(organization_id, correlation_id, timestamp),
            decision_id=ReleaseReadinessDecisionId(str(new_record_id())),
            pack_id=pack_id,
            immutable_version=immutable_version,
            workflow_id=workflow_id,
            status=status,
            integration_coverage_complete=integration_complete,
            evidence_references=evidence_references,
            unmet_gate_references=tuple(dict.fromkeys(release_gate_references)),
            failure_evidence_references=tuple(dict.fromkeys(failure_references)),
        )

    def _append_verification_run(
        self, run: VerificationRun, correlation_id: CorrelationId
    ) -> Result[VerificationRun, ErrorDetail]:
        if self._verification_repository is None:
            return Result.success(run)
        persisted = self._verification_repository.append(run)
        if not persisted.is_success or persisted.value is None:
            return Result.failure(self._repository_error(persisted.error, correlation_id))
        return Result.success(persisted.value)

    def _retain_compatibility(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        entries: Iterable[CompatibilityMatrixEntry | CompatibilityEvidenceRecord],
    ) -> Result[tuple[CompatibilityEvidenceRecord, ...], ErrorDetail]:
        retained: list[CompatibilityEvidenceRecord] = []
        for entry in entries:
            if isinstance(entry, CompatibilityEvidenceRecord):
                record = entry
            else:
                try:
                    status = CompatibilityStatus(entry.status)
                    record = CompatibilityEvidenceRecord(
                        metadata=build_metadata(organization_id, correlation_id, self._clock()),
                        evidence_id=EvidenceId(str(new_record_id())),
                        pack_contract_version=entry.pack_contract_version,
                        host_contract_version=entry.host_contract_version,
                        alc_version=entry.alc_version,
                        status=status,
                        designated=entry.designated,
                        evidence_reference=entry.evidence_reference
                        or (
                            f"compatibility:{entry.pack_contract_version}:"
                            f"{entry.host_contract_version}:{entry.alc_version}"
                        ),
                        recorded_at=self._clock(),
                        pack_id=entry.pack_id,
                        immutable_version=entry.immutable_version,
                    )
                except (AttributeError, TypeError, ValueError) as error:
                    return Result.failure(
                        ErrorDetail(ErrorCode.VALIDATION_FAILED, str(error), correlation_id)
                    )
                if self._compatibility_repository is not None:
                    matrix_result = self._compatibility_repository.append(entry)
                    if not matrix_result.is_success:
                        return Result.failure(
                            self._repository_error(matrix_result.error, correlation_id)
                        )
            persisted = self._evidence_repository.append_compatibility(record)
            if not persisted.is_success or persisted.value is None:
                return Result.failure(self._repository_error(persisted.error, correlation_id))
            retained.append(persisted.value)
        return Result.success(tuple(retained))

    def _retain_audits(
        self, correlation_id: CorrelationId, audits: Iterable[AuditRecord]
    ) -> Result[tuple[AuditRecord, ...], ErrorDetail]:
        retained: list[AuditRecord] = []
        for audit in audits:
            if self._audit_repository is not None:
                persisted = self._audit_repository.append(audit)
            else:
                persisted = self._evidence_repository.append_audit(audit)
            if not persisted.is_success or persisted.value is None:
                return Result.failure(self._repository_error(persisted.error, correlation_id))
            retained.append(persisted.value)
        return Result.success(tuple(retained))

    def _retain_ui_projections(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        fixed_seed: str,
        projections: Iterable[UIProjectionEvidence | str],
    ) -> Result[tuple[UIProjectionEvidence, ...], ErrorDetail]:
        retained: list[UIProjectionEvidence] = []
        for projection in projections:
            if isinstance(projection, str):
                record = UIProjectionEvidence(
                    metadata=build_metadata(organization_id, correlation_id, self._clock()),
                    projection_id=EvidenceId(str(new_record_id())),
                    projection_type="release",
                    projection_digest=self._digest(f"{fixed_seed}:{projection}"),
                    recorded_at=self._clock(),
                )
            else:
                record = projection
            if record.metadata.organization_id != organization_id:
                return Result.failure(
                    ErrorDetail(
                        ErrorCode.VALIDATION_FAILED,
                        "UI projection evidence belongs to another organization.",
                        correlation_id,
                    )
                )
            persisted = self._evidence_repository.append_ui_projection(record)
            if not persisted.is_success or persisted.value is None:
                return Result.failure(self._repository_error(persisted.error, correlation_id))
            retained.append(persisted.value)
        return Result.success(tuple(retained))

    @staticmethod
    def _validate_request(
        organization_id: OrganizationId,
        pack_id: DomainPackId,
        immutable_version: str,
        pack_contract_version: str,
        host_contract_version: str,
        alc_version: str,
        workflow_id: str,
        fixed_seed: str,
        fixture_digest: str,
    ) -> str | None:
        values = (
            (str(organization_id), "organization_id"),
            (str(pack_id), "pack_id"),
            (immutable_version, "immutable_version"),
            (pack_contract_version, "pack_contract_version"),
            (host_contract_version, "host_contract_version"),
            (alc_version, "alc_version"),
            (workflow_id, "workflow_id"),
            (fixed_seed, "fixed_seed"),
            (fixture_digest, "fixture_digest"),
        )
        for value, name in values:
            if not isinstance(value, str) or not value.strip():
                return f"{name} must be non-empty."
        for value, name in (
            (immutable_version, "immutable_version"),
            (pack_contract_version, "pack_contract_version"),
            (host_contract_version, "host_contract_version"),
            (alc_version, "alc_version"),
        ):
            try:
                validate_semantic_version(value, name)
            except ValueError as error:
                return str(error)
        return None

    @staticmethod
    def _digest(value: str) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()

    @staticmethod
    def _failure_persistence_reference(
        failure: VerificationFailureRecord, error: RepositoryError | None
    ) -> str:
        code = error.code.value if error is not None else ErrorCode.REPOSITORY_UNAVAILABLE.value
        return f"failure-persistence:{failure.failure_reference}:{code}"

    @staticmethod
    def _repository_error(
        error: RepositoryError | None, correlation_id: CorrelationId
    ) -> ErrorDetail:
        if error is None:
            return ErrorDetail(
                ErrorCode.REPOSITORY_UNAVAILABLE,
                "Verification evidence storage failed.",
                correlation_id,
                retryable=True,
            )
        return ErrorDetail(
            error.code,
            error.message,
            correlation_id,
            retryable=error.retryable,
            fields=error.fields,
        )


Verification_Suite = VerificationSuite
