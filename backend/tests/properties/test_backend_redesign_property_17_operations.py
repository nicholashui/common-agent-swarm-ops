"""Property checks for correlation, safe health, and retention controls."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from itertools import count

from hypothesis import given, settings, strategies as st

from app.core.command_service import CommandService, WorkCommand, WorkKind
from app.core.configuration import (
    ConfigurationService,
    DependencyState,
    HealthDependency,
    HealthService,
    StartupComponent,
)
from app.core.retention import RetentionService
from app.models.common import RecordMetadata
from app.models.contracts import ErrorDetail, Result
from app.models.control_plane import DeploymentConfiguration
from app.models.identifiers import CorrelationId, OrganizationId, RecordId
from app.models.redaction import REDACTED, RedactionService, RedactionSurface
from app.models.retention import (
    PreservedRetentionEvidence,
    RetentionAction,
    RetentionCategory,
    RetentionRecord,
)
from app.repositories.control_plane import InMemoryControlPlaneDatabase

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_ORGANIZATION = OrganizationId("property-17-organization")
_CORRELATION = CorrelationId("property-17-correlation")
_SAFE_VALUES = st.text(alphabet="abcdefghijklmnopqrstuvwxyz0123456789", min_size=1, max_size=10)
_DEPENDENCY_MATRICES = st.lists(
    st.tuples(st.booleans(), st.booleans(), st.booleans()), min_size=1, max_size=4
)


@dataclass
class _RetentionRepositoryFake:
    """Deterministically records only lifecycle transitions the service authorizes."""

    records: tuple[RetentionRecord, ...]
    applied: list[tuple[RetentionRecord, RetentionAction, PreservedRetentionEvidence]] = field(
        default_factory=list
    )

    def find_expired(
        self, category: RetentionCategory, expired_before: datetime
    ) -> Result[tuple[RetentionRecord, ...], ErrorDetail]:
        return Result.success(
            tuple(
                record
                for record in self.records
                if record.category is category and record.created_at < expired_before
            )
        )

    def apply_lifecycle(
        self,
        record: RetentionRecord,
        action: RetentionAction,
        evidence: PreservedRetentionEvidence,
    ) -> Result[bool, ErrorDetail]:
        self.applied.append((record, action, evidence))
        return Result.success(True)


def _metadata(record_id: str) -> RecordMetadata:
    return RecordMetadata(
        record_id=RecordId(record_id),
        organization_id=_ORGANIZATION,
        correlation_id=_CORRELATION,
        schema_version=1,
        version=1,
        created_at=_NOW,
        updated_at=_NOW,
    )


def _policy(
    action: RetentionAction,
    preserve_authorization: bool,
    preserve_provenance: bool,
    *,
    valid: bool,
) -> dict[str, object]:
    policy: dict[str, object] = {
        "max_age_days": 10,
        "action": action.value,
        "preserve_authorization_evidence": preserve_authorization,
        "preserve_provenance_evidence": preserve_provenance,
    }
    if not valid:
        policy["unsupported"] = True
    return policy


def _configuration(
    category: RetentionCategory,
    policy: Mapping[str, object],
) -> DeploymentConfiguration:
    return DeploymentConfiguration(
        metadata=_metadata("property-17-configuration"),
        configuration_id="property-17-deployment",
        trusted_origins=("https://console.example",),
        identity_integration="oidc",
        persistence_adapter="postgres",
        dispatch_adapter="local_queue",
        retention_policies={category.value: policy},
        rate_limits={"/api/v1": 20},
        feature_flags={"events": True},
        secret_references=(),
        production_transport_enabled=True,
    )


def _dependencies(
    matrix: list[tuple[bool, bool, bool]], probe_calls: list[str]
) -> tuple[HealthDependency, ...]:
    dependencies: list[HealthDependency] = []
    for index, (required, configured, healthy) in enumerate(matrix):
        name = f"dependency-{index}"
        probe = None
        if configured:

            def probe(*, dependency_name: str = name, result: bool = healthy) -> bool:
                probe_calls.append(dependency_name)
                return result

        dependencies.append(
            HealthDependency(
                name,
                StartupComponent.PERSISTENCE,
                required,
                configured,
                probe,
            )
        )
    return tuple(dependencies)


def _expected_readiness(
    matrix: list[tuple[bool, bool, bool]],
) -> dict[str, DependencyState]:
    return {
        f"dependency-{index}": (
            DependencyState.UNAVAILABLE
            if not configured and required
            else DependencyState.NOT_CONFIGURED
            if not configured
            else DependencyState.USABLE
            if healthy
            else DependencyState.UNAVAILABLE
        )
        for index, (required, configured, healthy) in enumerate(matrix)
    }


# Feature: backend-redesign, Property 17
# **Validates: Requirements 12.2, 12.3, 12.4, 12.5, 12.6, 12.7, 12.8**
@settings(max_examples=100)
@given(
    value=_SAFE_VALUES,
    dependency_matrix=_DEPENDENCY_MATRICES,
    authorized=st.booleans(),
    safe_build_version=st.booleans(),
    safe_schema_version=st.booleans(),
    work_kind=st.sampled_from(tuple(WorkKind)),
    attempt=st.integers(min_value=0, max_value=3),
    valid_retention_configuration=st.booleans(),
    retention_category=st.sampled_from(tuple(RetentionCategory)),
    retention_action=st.sampled_from(tuple(RetentionAction)),
    preserve_authorization=st.booleans(),
    preserve_provenance=st.booleans(),
    has_authorization_evidence=st.booleans(),
    has_provenance_evidence=st.booleans(),
)
def test_property_17_operations_retain_correlation_safe_health_and_data_lifecycle(
    value: str,
    dependency_matrix: list[tuple[bool, bool, bool]],
    authorized: bool,
    safe_build_version: bool,
    safe_schema_version: bool,
    work_kind: WorkKind,
    attempt: int,
    valid_retention_configuration: bool,
    retention_category: RetentionCategory,
    retention_action: RetentionAction,
    preserve_authorization: bool,
    preserve_provenance: bool,
    has_authorization_evidence: bool,
    has_provenance_evidence: bool,
) -> None:
    """Operations expose only safe health and retain exactly the configured lifecycle evidence."""
    configuration_service = ConfigurationService(environment={})
    policy = _policy(
        retention_action,
        preserve_authorization,
        preserve_provenance,
        valid=valid_retention_configuration,
    )
    configuration = _configuration(retention_category, policy)
    probe_calls: list[str] = []
    build_version = f"build-{value}" if safe_build_version else f"build-secret-{value}"
    schema_version = f"schema-{value}" if safe_schema_version else f"schema-token-{value}"
    health = HealthService(
        configuration_service,
        _dependencies(dependency_matrix, probe_calls),
        build_version=build_version,
        schema_version=schema_version,
        clock=lambda: _NOW,
    )

    assert health.liveness().alive
    assert probe_calls == []
    initial_health = health.operational_health(authorized=True)
    assert not initial_health.is_success

    status = configuration_service.initialize(configuration)
    readiness = health.readiness()
    assert {item.name: item.state for item in readiness.dependencies} == _expected_readiness(
        dependency_matrix
    )
    assert probe_calls == [
        f"dependency-{index}"
        for index, (_, configured, _) in enumerate(dependency_matrix)
        if configured
    ]
    assert readiness.ready is all(
        state is DependencyState.USABLE
        for name, state in _expected_readiness(dependency_matrix).items()
        if dependency_matrix[int(name.removeprefix("dependency-"))][0]
    )

    operational = health.operational_health(authorized=authorized)
    if not authorized:
        assert not operational.is_success
        assert operational.error is not None
        assert "secret" not in repr(operational.error)
    elif safe_build_version and safe_schema_version:
        assert operational.is_success and operational.value is not None
        snapshot = operational.value
        assert snapshot.build_version == build_version
        assert snapshot.schema_version == schema_version
        assert snapshot.readiness_timestamp == _NOW
        assert {summary.component for summary in snapshot.components} == set(StartupComponent)
        assert all(
            summary.enabled is status.is_enabled(summary.component)
            for summary in snapshot.components
        )
    else:
        assert not operational.is_success
        assert operational.error is not None
        assert "secret" not in repr(operational.error)
        assert "token" not in repr(operational.error)

    database = InMemoryControlPlaneDatabase()
    event_sequences = count(1)
    command_service = CommandService(
        database.unit_of_work,
        clock=lambda: _NOW,
        next_event_sequence=lambda: next(event_sequences),
    )
    submission = command_service.submit(
        _ORGANIZATION,
        _CORRELATION,
        WorkCommand(
            kind=work_kind,
            subject_reference=f"{work_kind.value}:subject-{value}",
            idempotency_key=f"key-{value}",
            scheduled_at=_NOW,
            attempt=attempt,
        ),
    )
    assert submission.is_success and submission.value is not None
    command_outcome = submission.value
    assert command_outcome.work_item.metadata.correlation_id == _CORRELATION
    assert command_outcome.publication.event.metadata.correlation_id == _CORRELATION
    assert command_outcome.publication.outbox.metadata.correlation_id == _CORRELATION
    assert all(
        record.metadata.correlation_id == _CORRELATION for record in database._state.audits.values()
    )
    assert all(
        record.metadata.correlation_id == _CORRELATION for record in database._state.events.values()
    )
    assert all(
        record.metadata.correlation_id == _CORRELATION for record in database._state.outbox.values()
    )

    sensitive_sentinel = f"deployment-secret-{value}"
    observability_payload = {
        "credential": sensitive_sentinel,
        "access_token": sensitive_sentinel,
        "raw_prompt": sensitive_sentinel,
        "protected_artifact": sensitive_sentinel,
        "prohibited_tool_input": sensitive_sentinel,
        "summary": f"safe-status {sensitive_sentinel}",
        "reference": f"ref-{value}",
    }
    redactor = RedactionService((sensitive_sentinel,))
    for surface in RedactionSurface:
        safe_payload = redactor.redact(observability_payload, surface=surface)
        assert sensitive_sentinel not in repr(safe_payload)
        assert isinstance(safe_payload, Mapping)
        assert safe_payload["reference"] == f"ref-{value}"
        assert safe_payload["credential"] == REDACTED
        assert safe_payload["summary"] == f"safe-status {REDACTED}"

    authorization_evidence = {"decision": f"allow-{value}"} if has_authorization_evidence else None
    provenance_evidence = {"run": f"run-{value}"} if has_provenance_evidence else None
    expired = RetentionRecord(
        f"expired-{value}",
        retention_category,
        _NOW - timedelta(days=11),
        authorization_evidence=authorization_evidence,
        provenance_evidence=provenance_evidence,
    )
    current = RetentionRecord(
        f"current-{value}",
        retention_category,
        _NOW - timedelta(days=1),
        authorization_evidence=authorization_evidence,
        provenance_evidence=provenance_evidence,
    )
    retention_repository = _RetentionRepositoryFake((expired, current))
    retention = RetentionService(
        configuration_service,
        retention_repository,
        clock=lambda: _NOW,
    ).apply_expired()
    evidence_is_complete = (not preserve_authorization or authorization_evidence is not None) and (
        not preserve_provenance or provenance_evidence is not None
    )

    if valid_retention_configuration and evidence_is_complete:
        assert status.is_enabled(StartupComponent.RETENTION)
        assert retention.is_success and retention.value is not None
        assert [
            (outcome.record_id, outcome.category, outcome.action) for outcome in retention.value
        ] == [(expired.record_id, retention_category, retention_action)]
        assert len(retention_repository.applied) == 1
        record, action, preserved = retention_repository.applied[0]
        assert record == expired
        assert action is retention_action
        assert preserved.authorization == (
            authorization_evidence if preserve_authorization else None
        )
        assert preserved.provenance == (provenance_evidence if preserve_provenance else None)
    else:
        assert not retention.is_success
        assert retention_repository.applied == []
        if not valid_retention_configuration:
            assert not status.is_enabled(StartupComponent.RETENTION)
