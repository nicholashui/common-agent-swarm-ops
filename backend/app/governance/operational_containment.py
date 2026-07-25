"""Fail-closed video release and operational capacity containment."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, replace
from datetime import datetime
from enum import StrEnum
from math import isfinite
from typing import cast

from app.models.common import SCHEMA_VERSION, RecordMetadata, utc_now
from app.models.contracts import ErrorCode, ErrorDetail, RepositoryError, Result
from app.models.control_plane import (
    ArtifactHandoff,
    AuditRecord,
    MaturityLevel,
    MaturityState,
    MaturityStateId,
    ReleaseReadinessDecision,
    ReleaseReadinessDecisionId,
    ReleaseReadinessStatus,
)
from app.models.identifiers import (
    ActorId,
    AgentId,
    CorrelationId,
    DomainPackId,
    OrganizationId,
    new_record_id,
)
from app.repositories.protocols import (
    AuditRecordRepository,
    MaturityStateRepository,
    ReleaseReadinessDecisionRepository,
)


class MandatoryVideoGate(StrEnum):
    """Every independent gate required before a video handoff can be released."""

    RIGHTS = "rights"
    CONSENT = "consent"
    CONTINUITY = "continuity"
    MEDIA_QUALITY = "media_quality"
    CHANNEL = "channel"
    APPROVAL = "approval"


@dataclass(frozen=True, slots=True)
class VideoReleaseGates:
    """The server-side representation of mandatory video release evidence.

    Values intentionally accept only simple evidence shapes.  A missing value,
    ``False``, an empty string/sequence, or a known negative status is never
    interpreted as a passed gate.
    """

    rights: bool | str | None = None
    consent: bool | str | None = None
    continuity: bool | str | None = None
    media_quality: bool | str | None = None
    channel: bool | str | Sequence[str] | None = None
    approval: bool | str | None = None

    @classmethod
    def from_handoff(cls, handoff: ArtifactHandoff) -> VideoReleaseGates:
        """Map the shared opaque handoff metadata to the six video gates."""
        return cls(
            rights=handoff.rights_and_consent_state,
            consent=handoff.rights_and_consent_state,
            continuity=handoff.continuity_state,
            media_quality=handoff.quality_control_state,
            channel=handoff.target_channels,
            approval=handoff.approval_reference,
        )

    @classmethod
    def from_mapping(cls, values: Mapping[str, object]) -> VideoReleaseGates:
        """Coerce a transport mapping without allowing unknown fields to pass."""
        allowed = {
            "rights",
            "consent",
            "continuity",
            "media_quality",
            "channel",
            "approval",
        }
        unknown = tuple(sorted(str(key) for key in values if str(key) not in allowed))
        if unknown:
            raise ValueError("Video release gates contain unsupported fields.")
        return cls(
            rights=_gate_value(values.get("rights")),
            consent=_gate_value(values.get("consent")),
            continuity=_gate_value(values.get("continuity")),
            media_quality=_gate_value(values.get("media_quality")),
            channel=_channel_value(values.get("channel")),
            approval=_gate_value(values.get("approval")),
        )

    def missing_gates(self) -> tuple[str, ...]:
        """Return all absent or explicitly failed gates in stable order."""
        values = (
            (MandatoryVideoGate.RIGHTS, self.rights),
            (MandatoryVideoGate.CONSENT, self.consent),
            (MandatoryVideoGate.CONTINUITY, self.continuity),
            (MandatoryVideoGate.MEDIA_QUALITY, self.media_quality),
            (MandatoryVideoGate.CHANNEL, self.channel),
            (MandatoryVideoGate.APPROVAL, self.approval),
        )
        return tuple(gate.value for gate, value in values if not _gate_passed(value))


# Descriptive alias used by callers that refer to the handoff as a gate set.
VideoReleaseGateSet = VideoReleaseGates


class CapacityAction(StrEnum):
    """The only policy-selected actions allowed at a capacity boundary."""

    THROTTLE = "throttle"
    DISABLE = "disable"


class PackOperationalStatus(StrEnum):
    """Operational status kept separate from each agent's maturity evidence."""

    ENABLED = "enabled"
    THROTTLED = "throttled"
    DISABLED = "disabled"


@dataclass(frozen=True, slots=True)
class CapacityActionResult:
    """Evidence of a capacity decision and the maturity retained with it."""

    organization_id: OrganizationId
    pack_id: DomainPackId
    action: CapacityAction
    operational_status: PackOperationalStatus
    observed_load: float
    approved_load_limit: float
    applied: bool
    maturity_states: tuple[MaturityState, ...]
    audit_recorded: bool | None
    correlation_id: CorrelationId
    reason: str | None = None

    @property
    def disabled(self) -> bool:
        """Return whether pack operations were disabled by this decision."""
        return self.operational_status is PackOperationalStatus.DISABLED

    @property
    def maturity(self) -> tuple[MaturityState, ...]:
        """Expose retained per-agent maturity using the concise API name."""
        return self.maturity_states


class OperationalContainmentService:
    """Enforce release gates and auditable, fail-closed capacity containment."""

    def __init__(
        self,
        release_repository: ReleaseReadinessDecisionRepository,
        maturity_repository: MaturityStateRepository,
        audit_repository: AuditRecordRepository,
        *,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._release_repository = release_repository
        self._maturity_repository = maturity_repository
        self._audit_repository = audit_repository
        self._clock = clock

    @staticmethod
    def maturity_levels() -> tuple[MaturityLevel, ...]:
        """Return the four distinct maturity states in operational order."""
        return (
            MaturityLevel.CATALOGED,
            MaturityLevel.REGISTERED,
            MaturityLevel.ACTIVE,
            MaturityLevel.PRODUCTION_PROVEN,
        )

    def report_maturity_state(self, state: MaturityState) -> Result[MaturityState, ErrorDetail]:
        """Persist one independent agent maturity record without pack activation."""
        if state.level not in self.maturity_levels():
            return Result.failure(
                ErrorDetail(
                    ErrorCode.VALIDATION_FAILED,
                    "Maturity_State value is not registered.",
                    state.metadata.correlation_id,
                )
            )
        try:
            persisted = self._maturity_repository.append(state)
        except Exception:
            return Result.failure(
                self._repository_failure(
                    state.metadata.correlation_id,
                    "Maturity_State persistence is unavailable.",
                )
            )
        if not persisted.is_success or persisted.value is None:
            return Result.failure(
                self._repository_failure(
                    state.metadata.correlation_id,
                    "Maturity_State persistence failed.",
                    persisted.error,
                )
            )
        return Result.success(persisted.value)

    def report_maturity(
        self,
        organization_id: OrganizationId,
        pack_id: DomainPackId,
        immutable_version: str,
        agent_id: AgentId,
        level: MaturityLevel | str,
        evidence_references: Iterable[str],
        *,
        correlation_id: CorrelationId | None = None,
        maturity_state_id: MaturityStateId | None = None,
        pack_operational: bool = True,
    ) -> Result[MaturityState, ErrorDetail]:
        """Build and persist an independently attributable maturity state."""
        correlation = correlation_id or CorrelationId("operational-containment")
        try:
            timestamp = self._clock()
            state = MaturityState(
                metadata=self._metadata(organization_id, correlation, timestamp),
                maturity_state_id=maturity_state_id or MaturityStateId(str(new_record_id())),
                pack_id=pack_id,
                immutable_version=immutable_version,
                agent_id=agent_id,
                level=MaturityLevel(level),
                evidence_references=tuple(evidence_references),
                pack_operational=pack_operational,
            )
        except (TypeError, ValueError) as error:
            return Result.failure(ErrorDetail(ErrorCode.VALIDATION_FAILED, str(error), correlation))
        return self.report_maturity_state(state)

    def evaluate_video_release(
        self,
        handoff: ArtifactHandoff,
        *,
        pack_id: DomainPackId | None = None,
        immutable_version: str | None = None,
        workflow_id: str | None = None,
        gates: VideoReleaseGates | Mapping[str, object] | None = None,
        evidence_references: Iterable[str] = (),
        organization_id: OrganizationId | None = None,
        correlation_id: CorrelationId | None = None,
    ) -> Result[ReleaseReadinessDecision, ErrorDetail]:
        """Persist an eligible or blocked terminal decision for a video handoff.

        The shared Artifact_Handoff stores rights and consent in one metadata
        reference and media quality as quality-control evidence.  This method
        expands those references into six independent checks and blocks when any
        check is absent or explicitly failed.
        """
        correlation = correlation_id or handoff.metadata.correlation_id
        owner = organization_id or handoff.metadata.organization_id
        if owner != handoff.metadata.organization_id:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.AUTHORIZATION_DENIED,
                    "Video handoff is outside the requested organization.",
                    correlation,
                )
            )
        missing_identity = tuple(
            name
            for name, value in (
                ("pack_id", pack_id),
                ("immutable_version", immutable_version),
                ("workflow_id", workflow_id),
            )
            if value is None or not str(value).strip()
        )
        if missing_identity:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.VALIDATION_FAILED,
                    "Video release requires pack, version, and workflow identity.",
                    correlation,
                )
            )
        try:
            resolved_gates = (
                gates
                if isinstance(gates, VideoReleaseGates)
                else VideoReleaseGates.from_mapping(gates)
                if gates is not None
                else VideoReleaseGates.from_handoff(handoff)
            )
            missing_gates = resolved_gates.missing_gates()
            references = _unique_references(
                (*tuple(evidence_references), f"handoff:{handoff.handoff_id}")
            )
            timestamp = self._clock()
            decision = ReleaseReadinessDecision(
                metadata=self._metadata(owner, correlation, timestamp),
                decision_id=ReleaseReadinessDecisionId(str(new_record_id())),
                pack_id=cast(DomainPackId, pack_id),
                immutable_version=cast(str, immutable_version),
                workflow_id=cast(str, workflow_id),
                status=(
                    ReleaseReadinessStatus.BLOCKED
                    if missing_gates
                    else ReleaseReadinessStatus.ELIGIBLE
                ),
                integration_coverage_complete=not missing_gates,
                evidence_references=references,
                unmet_gate_references=missing_gates,
            )
        except (TypeError, ValueError) as error:
            return Result.failure(ErrorDetail(ErrorCode.VALIDATION_FAILED, str(error), correlation))

        try:
            persisted = self._release_repository.append(decision)
        except Exception:
            return Result.failure(
                self._repository_failure(
                    correlation,
                    "Release readiness decision persistence is unavailable.",
                )
            )
        if not persisted.is_success or persisted.value is None:
            return Result.failure(
                self._repository_failure(
                    correlation,
                    "Release readiness decision persistence failed.",
                    persisted.error,
                )
            )
        if missing_gates:
            self._append_audit(
                owner,
                correlation,
                action="video.release.blocked",
                subject_reference=f"handoff:{handoff.handoff_id}",
                outcome="blocked",
                reason=",".join(missing_gates),
                source_references=references,
            )
        return Result.success(persisted.value)

    def apply_capacity_action(
        self,
        organization_id: OrganizationId,
        pack_id: DomainPackId,
        observed_load: float | int,
        approved_load_limit: float | int,
        action: CapacityAction | str,
        *,
        immutable_version: str | None = None,
        maturity_states: Iterable[MaturityState] = (),
        correlation_id: CorrelationId | None = None,
        actor_id: ActorId | None = None,
        reason: str = "approved capacity limit exceeded",
        force: bool = False,
    ) -> Result[CapacityActionResult, ErrorDetail]:
        """Apply exactly the declared throttle-or-disable action when over limit."""
        correlation = correlation_id or CorrelationId("capacity-containment")
        resolved_actor = actor_id or ActorId("governance-controller")
        try:
            resolved_action = CapacityAction(action)
        except (TypeError, ValueError):
            return Result.failure(
                ErrorDetail(
                    ErrorCode.VALIDATION_FAILED,
                    "Capacity action must be throttle or disable.",
                    correlation,
                )
            )
        if not _valid_load(observed_load) or not _valid_load(approved_load_limit):
            return Result.failure(
                ErrorDetail(
                    ErrorCode.VALIDATION_FAILED,
                    "Capacity values must be finite and non-negative.",
                    correlation,
                )
            )
        observed = float(observed_load)
        limit = float(approved_load_limit)
        states_result = self._resolve_maturity_states(
            organization_id, pack_id, immutable_version, tuple(maturity_states), correlation
        )
        if not states_result.is_success or states_result.value is None:
            return Result.failure(
                states_result.error
                or self._repository_failure(correlation, "Maturity_State lookup failed.")
            )
        states = states_result.value
        exceeded = force or observed > limit
        status = PackOperationalStatus.ENABLED
        retained_states = states
        if exceeded:
            status = (
                PackOperationalStatus.DISABLED
                if resolved_action is CapacityAction.DISABLE
                else PackOperationalStatus.THROTTLED
            )
            if resolved_action is CapacityAction.DISABLE:
                retained_states_result = self._retain_disabled_maturity(states, correlation)
                if not retained_states_result.is_success or retained_states_result.value is None:
                    return Result.failure(
                        retained_states_result.error
                        or self._repository_failure(
                            correlation, "Independent Maturity_State retention failed."
                        )
                    )
                retained_states = retained_states_result.value

        audit_recorded: bool | None = None
        if exceeded:
            audit_recorded = self._append_audit(
                organization_id,
                correlation,
                action="domain_pack.capacity_action",
                subject_reference=str(pack_id),
                outcome=resolved_action.value,
                reason=reason,
                actor_id=resolved_actor,
                source_references=tuple(
                    reference
                    for state in retained_states
                    for reference in state.evidence_references
                ),
            )
        return Result.success(
            CapacityActionResult(
                organization_id=organization_id,
                pack_id=pack_id,
                action=resolved_action,
                operational_status=status,
                observed_load=observed,
                approved_load_limit=limit,
                applied=exceeded,
                maturity_states=retained_states,
                audit_recorded=audit_recorded,
                correlation_id=correlation,
                reason=reason if exceeded else None,
            )
        )

    def disable_pack_for_provider_failure(
        self,
        organization_id: OrganizationId,
        pack_id: DomainPackId,
        *,
        immutable_version: str | None = None,
        maturity_states: Iterable[MaturityState] = (),
        failure_reference: str = "provider_adapter_failure",
        correlation_id: CorrelationId | None = None,
        actor_id: ActorId | None = None,
    ) -> Result[CapacityActionResult, ErrorDetail]:
        """Disable a failed pack while preserving every agent's maturity level."""
        return self.apply_capacity_action(
            organization_id,
            pack_id,
            observed_load=1,
            approved_load_limit=0,
            action=CapacityAction.DISABLE,
            immutable_version=immutable_version,
            maturity_states=maturity_states,
            correlation_id=correlation_id,
            actor_id=actor_id,
            reason=failure_reference,
            force=True,
        )

    # Discoverable aliases used by governance and verification callers.
    verify_video_release = evaluate_video_release
    verify_release = evaluate_video_release
    check_video_release = evaluate_video_release
    evaluate_release = evaluate_video_release
    block_video_release = evaluate_video_release
    record_maturity_state = report_maturity_state
    applyCapacityAction = apply_capacity_action  # noqa: N815
    enforce_capacity = apply_capacity_action
    disablePackForProviderFailure = disable_pack_for_provider_failure  # noqa: N815

    def _resolve_maturity_states(
        self,
        organization_id: OrganizationId,
        pack_id: DomainPackId,
        immutable_version: str | None,
        supplied: tuple[MaturityState, ...],
        correlation_id: CorrelationId,
    ) -> Result[tuple[MaturityState, ...], ErrorDetail]:
        states = supplied
        if not states:
            try:
                listed = self._maturity_repository.list_for_organization(organization_id)
            except Exception:
                return Result.failure(
                    self._repository_failure(
                        correlation_id, "Maturity_State lookup is unavailable."
                    )
                )
            if not listed.is_success or listed.value is None:
                return Result.failure(
                    self._repository_failure(
                        correlation_id, "Maturity_State lookup failed.", listed.error
                    )
                )
            states = tuple(
                state
                for state in listed.value
                if state.pack_id == pack_id
                and (immutable_version is None or state.immutable_version == immutable_version)
            )
        if any(
            state.metadata.organization_id != organization_id
            or state.pack_id != pack_id
            or (immutable_version is not None and state.immutable_version != immutable_version)
            for state in states
        ):
            return Result.failure(
                ErrorDetail(
                    ErrorCode.AUTHORIZATION_DENIED,
                    "Maturity_State is outside the capacity-action scope.",
                    correlation_id,
                )
            )
        if len({state.agent_id for state in states}) != len(states):
            return Result.failure(
                ErrorDetail(
                    ErrorCode.CONFLICT,
                    "Capacity actions require one independent maturity state per agent.",
                    correlation_id,
                )
            )
        return Result.success(states)

    def _retain_disabled_maturity(
        self, states: tuple[MaturityState, ...], correlation_id: CorrelationId
    ) -> Result[tuple[MaturityState, ...], ErrorDetail]:
        """Retain the same levels while recording pack disablement separately."""
        retained: list[MaturityState] = []
        replacer = getattr(self._maturity_repository, "replace", None)
        for state in states:
            disabled = replace(
                state,
                metadata=replace(
                    state.metadata,
                    version=state.metadata.version + 1,
                    updated_at=self._clock(),
                ),
                pack_operational=False,
            )
            if callable(replacer):
                try:
                    persisted = replacer(disabled)
                except Exception:
                    return Result.failure(
                        self._repository_failure(
                            correlation_id,
                            "Independent Maturity_State retention is unavailable.",
                        )
                    )
                if not persisted.is_success or persisted.value is None:
                    return Result.failure(
                        self._repository_failure(
                            correlation_id,
                            "Independent Maturity_State retention failed.",
                            persisted.error,
                        )
                    )
                retained.append(persisted.value)
            else:
                # The standard protocol is append-only: the original immutable
                # state remains retained, while this returned snapshot carries
                # the independent operational flag for the containment decision.
                retained.append(disabled)
        return Result.success(tuple(retained))

    def _append_audit(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        *,
        action: str,
        subject_reference: str,
        outcome: str,
        reason: str,
        actor_id: ActorId | None = None,
        source_references: Iterable[str] = (),
    ) -> bool:
        resolved_actor = actor_id or ActorId("governance-controller")
        timestamp = self._clock()
        audit = AuditRecord(
            metadata=self._metadata(organization_id, correlation_id, timestamp),
            audit_id=str(new_record_id()),
            action=action,
            subject_reference=subject_reference,
            outcome=outcome,
            recorded_at=timestamp,
            actor_id=resolved_actor,
            reason=reason,
            source_references=_unique_references(source_references),
        )
        try:
            result = self._audit_repository.append(audit)
        except Exception:
            return False
        return result.is_success and result.value is not None

    def _metadata(
        self, organization_id: OrganizationId, correlation_id: CorrelationId, timestamp: datetime
    ) -> RecordMetadata:
        return RecordMetadata(
            record_id=new_record_id(),
            organization_id=organization_id,
            correlation_id=correlation_id,
            schema_version=SCHEMA_VERSION,
            version=1,
            created_at=timestamp,
            updated_at=timestamp,
        )

    @staticmethod
    def _repository_failure(
        correlation_id: CorrelationId,
        fallback: str,
        error: RepositoryError | None = None,
    ) -> ErrorDetail:
        if error is None:
            return ErrorDetail(
                ErrorCode.REPOSITORY_UNAVAILABLE,
                fallback,
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


def _gate_value(value: object) -> bool | str | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value
    return None


def _channel_value(value: object) -> bool | str | Sequence[str] | None:
    if isinstance(value, bool | str):
        return value
    if isinstance(value, Sequence) and not isinstance(value, bytes | bytearray):
        return tuple(item for item in value if isinstance(item, str))
    return None


def _gate_passed(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().casefold()
        return bool(normalized) and normalized not in {
            "blocked",
            "denied",
            "failed",
            "missing",
            "pending",
            "rejected",
            "unsafe",
        }
    if isinstance(value, Sequence) and not isinstance(value, bytes | bytearray):
        return bool(value) and all(_gate_passed(item) for item in value)
    return False


def _valid_load(value: object) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and isfinite(value)
        and value >= 0
    )


def _unique_references(values: Iterable[str]) -> tuple[str, ...]:
    normalized: list[str] = []
    for value in values:
        if not isinstance(value, str) or not value.strip():
            continue
        if value not in normalized:
            normalized.append(value)
    return tuple(normalized)


# Specification terminology aliases.
OperationalContainment = OperationalContainmentService
CapacityActionDecision = CapacityActionResult
Maturity_State = MaturityState
