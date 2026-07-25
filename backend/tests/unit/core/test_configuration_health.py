"""Focused deterministic tests for safe deployment configuration and health."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from app.core.configuration import (
    ConfigurationService,
    DependencyState,
    HealthDependency,
    HealthService,
    SecretSource,
    StartupComponent,
)
from app.models.common import RecordMetadata
from app.models.contracts import ErrorCode
from app.models.control_plane import DeploymentConfiguration
from app.models.identifiers import CorrelationId, OrganizationId, RecordId

_NOW = datetime(2025, 1, 1, tzinfo=UTC)


@dataclass
class _SecretManager:
    values: dict[str, str] = field(default_factory=dict)
    calls: list[str] = field(default_factory=list)

    def get_secret(self, reference: str) -> str | None:
        self.calls.append(reference)
        return self.values.get(reference)


def _configuration(
    *,
    trusted_origins: tuple[str, ...] = ("https://console.example",),
    secret_references: tuple[str, ...] = (),
    work_recovery_policy: dict[str, object] | None = None,
) -> DeploymentConfiguration:
    return DeploymentConfiguration(
        metadata=RecordMetadata(
            record_id=RecordId("deployment-record"),
            organization_id=OrganizationId("deployment"),
            correlation_id=CorrelationId("configuration-test"),
            schema_version=1,
            version=1,
            created_at=_NOW,
            updated_at=_NOW,
        ),
        configuration_id="deployment-v1",
        trusted_origins=trusted_origins,
        identity_integration="oidc",
        persistence_adapter="postgres",
        dispatch_adapter="local_queue",
        retention_policies={
            "audit_records": {
                "max_age_days": 365,
                "action": "archive",
                "preserve_authorization_evidence": True,
                "preserve_provenance_evidence": True,
            }
        },
        rate_limits={"/api/v1": 20},
        feature_flags={"events": True},
        secret_references=secret_references,
        production_transport_enabled=True,
        work_recovery_policy=(
            {
                "claim_expiry_decision": "reclaim",
                "worker_stop_decision": "manual_recovery",
                "max_attempts": 3,
                "retry_delay_seconds": 30,
            }
            if work_recovery_policy is None
            else work_recovery_policy
        ),
    )


def test_configuration_uses_environment_before_secret_manager_and_isolates_failures() -> None:
    """Environment secrets win, while an unavailable secret disables only its owner."""
    manager = _SecretManager({"SERVICE_SECRET": "manager-value"})
    service = ConfigurationService(
        environment={"SERVICE_SECRET": "environment-value"}, secret_manager=manager
    )
    status = service.initialize(
        _configuration(secret_references=("SERVICE_SECRET",)),
        required_secrets={StartupComponent.IDENTITY: ("SERVICE_SECRET",)},
    )

    assert status.is_enabled(StartupComponent.IDENTITY)
    assert manager.calls == []

    missing_reference = "VERY_SECRET_REFERENCE"
    missing_service = ConfigurationService(environment={}, secret_manager=_SecretManager())
    missing = missing_service.initialize(
        _configuration(secret_references=(missing_reference,)),
        required_secrets={StartupComponent.IDENTITY: (missing_reference,)},
    )
    failure = missing.failure_for(StartupComponent.IDENTITY)

    assert failure is not None and failure.code is ErrorCode.SECRET_UNAVAILABLE
    assert all(
        missing.is_enabled(component)
        for component in StartupComponent
        if component is not StartupComponent.IDENTITY
    )
    assert missing_reference not in failure.message
    assert missing_reference not in " ".join(field.name for field in failure.fields)


def test_secret_manager_fallback_resolves_required_secret_without_leaking_it() -> None:
    """Configured secret-manager values enable their component but remain absent from status."""
    secret_value = "manager-secret-value"
    manager = _SecretManager({"MANAGER_SECRET": secret_value})
    service = ConfigurationService(environment={}, secret_manager=manager)

    resolution = service.resolve_secret("MANAGER_SECRET", component=StartupComponent.IDENTITY)
    status = service.initialize(
        _configuration(secret_references=("MANAGER_SECRET",)),
        required_secrets={StartupComponent.IDENTITY: ("MANAGER_SECRET",)},
    )

    assert resolution.is_success and resolution.value is not None
    assert resolution.value.source is SecretSource.SECRET_MANAGER
    assert resolution.value.value == secret_value
    assert status.is_enabled(StartupComponent.IDENTITY)
    assert manager.calls
    assert secret_value not in repr(status)


def test_schema_validation_disables_only_the_invalid_startup_component() -> None:
    """Cross-domain validation reports a safe error without preventing independent components."""
    status = ConfigurationService(environment={}).initialize(
        _configuration(trusted_origins=("https://console.example/path",))
    )
    origin_failure = status.failure_for(StartupComponent.ORIGINS)

    assert origin_failure is not None and origin_failure.code is ErrorCode.CONFIGURATION_INVALID
    assert all(
        status.is_enabled(component)
        for component in StartupComponent
        if component is not StartupComponent.ORIGINS
    )
    assert "https://console.example/path" not in origin_failure.message


def test_invalid_work_recovery_policy_disables_dispatch() -> None:
    """Dispatch cannot start when bounded recovery decisions have not passed schema validation."""
    status = ConfigurationService(environment={}).initialize(
        _configuration(
            work_recovery_policy={
                "claim_expiry_decision": "unsafe",
                "worker_stop_decision": "dead_letter",
                "max_attempts": 0,
                "retry_delay_seconds": -1,
            }
        )
    )

    failure = status.failure_for(StartupComponent.DISPATCH)

    assert failure is not None and failure.code is ErrorCode.CONFIGURATION_INVALID


def test_liveness_skips_dependencies_and_readiness_maps_required_and_optional_states() -> None:
    """Liveness skips probes; readiness reports every configured and optional state exactly."""
    probe_calls: list[str] = []

    def required_usable() -> bool:
        probe_calls.append("required-usable")
        return True

    def required_unavailable() -> bool:
        probe_calls.append("required-unavailable")
        return False

    def optional_usable() -> bool:
        probe_calls.append("optional-usable")
        return True

    def optional_unavailable() -> bool:
        probe_calls.append("optional-unavailable")
        return False

    def unconfigured_probe() -> bool:
        probe_calls.append("optional-not-configured")
        return True

    configuration = ConfigurationService(environment={})
    health = HealthService(
        configuration,
        (
            HealthDependency("database", StartupComponent.PERSISTENCE, True, True, required_usable),
            HealthDependency("queue", StartupComponent.DISPATCH, True, True, required_unavailable),
            HealthDependency("cache", StartupComponent.FEATURE_FLAGS, False, True, optional_usable),
            HealthDependency(
                "search", StartupComponent.IDENTITY, False, True, optional_unavailable
            ),
            HealthDependency(
                "tracing", StartupComponent.IDENTITY, False, False, unconfigured_probe
            ),
        ),
        build_version="build-1",
        schema_version="schema-1",
        clock=lambda: _NOW,
    )

    assert health.liveness().alive
    assert probe_calls == []

    configuration.initialize(_configuration())
    readiness = health.readiness()
    states = {dependency.name: dependency.state for dependency in readiness.dependencies}
    operational = health.operational_health(authorized=True)

    assert probe_calls == [
        "required-usable",
        "required-unavailable",
        "optional-usable",
        "optional-unavailable",
    ]
    assert states == {
        "database": DependencyState.USABLE,
        "queue": DependencyState.UNAVAILABLE,
        "cache": DependencyState.USABLE,
        "search": DependencyState.UNAVAILABLE,
        "tracing": DependencyState.NOT_CONFIGURED,
    }
    assert not readiness.ready
    assert operational.is_success and operational.value is not None
    assert operational.value.build_version == "build-1"
    assert operational.value.schema_version == "schema-1"
    assert operational.value.readiness_timestamp == _NOW


def test_authorized_health_rejects_unsafe_required_metadata() -> None:
    """Operational health refuses a response when a required field cannot be safely emitted."""
    configuration = ConfigurationService(environment={})
    configuration.initialize(_configuration())
    health = HealthService(
        configuration,
        (),
        build_version="contains-secret-value",
        schema_version="schema-1",
        clock=lambda: _NOW,
    )

    health.readiness()
    result = health.operational_health(authorized=True)

    assert not result.is_success
    assert result.error is not None and result.error.code is ErrorCode.HEALTH_UNAVAILABLE
