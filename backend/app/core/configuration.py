"""Safe deployment configuration and operational health services."""

from __future__ import annotations

import os
import re
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Protocol
from urllib.parse import urlparse

from app.models.contracts import ErrorCode, ErrorDetail, ErrorField, Result
from app.models.control_plane import DeploymentConfiguration, SessionModel
from app.models.identifiers import CorrelationId
from app.models.redaction import configure_deployment_secrets
from app.models.retention import parse_retention_policies


class StartupComponent(StrEnum):
    """Deployment domains that may be independently enabled or disabled."""

    ORIGINS = "origins"
    IDENTITY = "identity"
    PERSISTENCE = "persistence"
    DISPATCH = "dispatch"
    RETENTION = "retention"
    RATE_LIMITS = "rate_limits"
    FEATURE_FLAGS = "feature_flags"


class SecretSource(StrEnum):
    """The controlled source used to resolve an operational secret."""

    ENVIRONMENT = "environment"
    SECRET_MANAGER = "secret_manager"


class DependencyState(StrEnum):
    """Public-safe readiness states for configured dependencies."""

    USABLE = "usable"
    UNAVAILABLE = "unavailable"
    NOT_CONFIGURED = "not_configured"


class SecretManager(Protocol):
    """Configured manager port; it receives a reference and never exposes diagnostics."""

    def get_secret(self, reference: str) -> str | None:
        """Resolve one secret by deployment-owned reference."""


@dataclass(frozen=True, slots=True)
class SecretResolution:
    """An in-memory secret value and the controlled source that supplied it."""

    value: str = field(repr=False)
    source: SecretSource


@dataclass(frozen=True, slots=True)
class ComponentStartupStatus:
    """Secret-free result for one independently validated startup component."""

    component: StartupComponent
    enabled: bool
    error: ErrorDetail | None = None

    def __post_init__(self) -> None:
        if self.enabled == (self.error is not None):
            raise ValueError("A startup component must be enabled exactly when it has no error.")


@dataclass(frozen=True, slots=True)
class StartupConfigurationStatus:
    """Retained safe startup state; it intentionally contains no configuration values."""

    components: tuple[ComponentStartupStatus, ...]

    def __post_init__(self) -> None:
        if {status.component for status in self.components} != set(StartupComponent):
            raise ValueError("Startup status must include every startup component exactly once.")

    def is_enabled(self, component: StartupComponent) -> bool:
        """Return whether a validated component can become usable."""
        return next(status.enabled for status in self.components if status.component is component)

    def failure_for(self, component: StartupComponent) -> ErrorDetail | None:
        """Return a retained typed failure without configuration or secret values."""
        return next(status.error for status in self.components if status.component is component)


@dataclass(frozen=True, slots=True)
class LivenessSnapshot:
    """Dependency-free indication that this process can answer liveness checks."""

    alive: bool = True


@dataclass(frozen=True, slots=True)
class DependencyReadiness:
    """Redaction-safe readiness state for one dependency."""

    name: str
    required: bool
    state: DependencyState


@dataclass(frozen=True, slots=True)
class ReadinessSnapshot:
    """A readiness report produced after probing only configured dependencies."""

    dependencies: tuple[DependencyReadiness, ...]
    checked_at: datetime

    def __post_init__(self) -> None:
        if self.checked_at.tzinfo is None:
            raise ValueError("Readiness timestamps must be timezone-aware.")

    @property
    def ready(self) -> bool:
        """Return whether every required dependency is currently usable."""
        return all(
            dependency.state is DependencyState.USABLE
            for dependency in self.dependencies
            if dependency.required
        )


@dataclass(frozen=True, slots=True)
class HealthDependency:
    """A configured dependency probe and the startup component that owns it."""

    name: str
    component: StartupComponent
    required: bool
    configured: bool
    probe: Callable[[], bool] | None = field(default=None, repr=False, compare=False)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Dependency names must be non-empty.")
        if self.configured and self.probe is None:
            raise ValueError("Configured dependencies require a probe.")


@dataclass(frozen=True, slots=True)
class ComponentHealthSummary:
    """Authorized safe component availability without internal configuration details."""

    component: StartupComponent
    enabled: bool
    failure_code: ErrorCode | None


@dataclass(frozen=True, slots=True)
class OperationalHealthSnapshot:
    """Authorized operational-health payload with every required safe field present."""

    components: tuple[ComponentHealthSummary, ...]
    build_version: str
    schema_version: str
    readiness_timestamp: datetime

    def __post_init__(self) -> None:
        if self.readiness_timestamp.tzinfo is None:
            raise ValueError("Readiness timestamps must be timezone-aware.")


_COMPONENTS = tuple(StartupComponent)
_CONFIGURATION_CORRELATION_ID = CorrelationId("configuration")
_HEALTH_CORRELATION_ID = CorrelationId("health")
_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")
_SAFE_HEALTH_VALUE = re.compile(r"^[A-Za-z0-9._+-]{1,128}$")


class ConfigurationService:
    """Validate startup domains and resolve configured secrets without exposing their values."""

    def __init__(
        self,
        *,
        environment: Mapping[str, str] | None = None,
        secret_manager: SecretManager | None = None,
        correlation_id: CorrelationId = _CONFIGURATION_CORRELATION_ID,
    ) -> None:
        self._environment = dict(os.environ if environment is None else environment)
        self._secret_manager = secret_manager
        self._correlation_id = correlation_id
        self._status: StartupConfigurationStatus | None = None
        self._validated_configuration: DeploymentConfiguration | None = None

    @property
    def status(self) -> StartupConfigurationStatus | None:
        """Return the most recent secret-free startup status, if validation has run."""
        return self._status

    @property
    def validated_configuration(self) -> DeploymentConfiguration | None:
        """Return the configuration whose component validation produced current status."""
        return self._validated_configuration

    def initialize(
        self,
        configuration: DeploymentConfiguration,
        *,
        required_secrets: Mapping[StartupComponent, tuple[str, ...]] | None = None,
    ) -> StartupConfigurationStatus:
        """Validate every startup domain and disable only components with invalid dependencies."""
        failures = self._schema_failures(configuration)
        configured_references = {
            reference for reference in configuration.secret_references if _is_identifier(reference)
        }
        for component, references in (required_secrets or {}).items():
            if not isinstance(component, StartupComponent):
                raise ValueError("Required secrets must be assigned to a startup component.")
            if component in failures:
                continue
            for reference in references:
                if reference not in configured_references:
                    failures[component] = self._configuration_failure(component)
                    break
                resolution = self.resolve_secret(reference, component=component)
                if not resolution.is_success:
                    failures[component] = resolution.error or self._secret_failure(component)
                    break

        self._validated_configuration = configuration
        self._status = StartupConfigurationStatus(
            tuple(
                ComponentStartupStatus(
                    component,
                    component not in failures,
                    failures.get(component),
                )
                for component in _COMPONENTS
            )
        )
        configure_deployment_secrets(
            self._resolved_deployment_secrets(configuration.secret_references)
        )
        return self._status

    def _resolved_deployment_secrets(self, references: tuple[str, ...]) -> tuple[str, ...]:
        """Collect resolved deployment values only for central output redaction."""
        resolved_values: list[str] = []
        for reference in references:
            resolution = self.resolve_secret(reference)
            if resolution.is_success and resolution.value is not None:
                resolved_values.append(resolution.value.value)
        return tuple(resolved_values)

    def resolve_secret(
        self, reference: str, *, component: StartupComponent | None = None
    ) -> Result[SecretResolution, ErrorDetail]:
        """Resolve a secret from environment first, then the configured manager."""
        safe_component = component or StartupComponent.IDENTITY
        if not _is_identifier(reference):
            return Result.failure(self._configuration_failure(safe_component))
        environment_value = self._environment.get(reference)
        if isinstance(environment_value, str) and environment_value:
            return Result.success(SecretResolution(environment_value, SecretSource.ENVIRONMENT))
        if self._secret_manager is not None:
            try:
                manager_value = self._secret_manager.get_secret(reference)
            except Exception:
                manager_value = None
            if isinstance(manager_value, str) and manager_value:
                return Result.success(SecretResolution(manager_value, SecretSource.SECRET_MANAGER))
        return Result.failure(self._secret_failure(safe_component))

    def _schema_failures(
        self, configuration: DeploymentConfiguration
    ) -> dict[StartupComponent, ErrorDetail]:
        failures: dict[StartupComponent, ErrorDetail] = {}
        if (
            not _valid_origins(configuration.trusted_origins)
            or not _valid_transport(configuration)
        ):
            failures[StartupComponent.ORIGINS] = self._configuration_failure(
                StartupComponent.ORIGINS
            )
        if not _is_identifier(configuration.identity_integration):
            failures[StartupComponent.IDENTITY] = self._configuration_failure(
                StartupComponent.IDENTITY
            )
        if not _is_identifier(configuration.persistence_adapter):
            failures[StartupComponent.PERSISTENCE] = self._configuration_failure(
                StartupComponent.PERSISTENCE
            )
        if not _is_identifier(configuration.dispatch_adapter):
            failures[StartupComponent.DISPATCH] = self._configuration_failure(
                StartupComponent.DISPATCH
            )
        if not _valid_retention_policies(configuration.retention_policies):
            failures[StartupComponent.RETENTION] = self._configuration_failure(
                StartupComponent.RETENTION
            )
        if not _valid_rate_limits(configuration.rate_limits):
            failures[StartupComponent.RATE_LIMITS] = self._configuration_failure(
                StartupComponent.RATE_LIMITS
            )
        if not _valid_feature_flags(configuration.feature_flags):
            failures[StartupComponent.FEATURE_FLAGS] = self._configuration_failure(
                StartupComponent.FEATURE_FLAGS
            )
        if not _valid_work_recovery_policy(configuration.work_recovery_policy):
            failures[StartupComponent.DISPATCH] = self._configuration_failure(
                StartupComponent.DISPATCH
            )
        return failures

    def _configuration_failure(self, component: StartupComponent) -> ErrorDetail:
        return ErrorDetail(
            ErrorCode.CONFIGURATION_INVALID,
            "The affected component could not be configured.",
            self._correlation_id,
            fields=(ErrorField(component.value, "Invalid configuration."),),
        )

    def _secret_failure(self, component: StartupComponent) -> ErrorDetail:
        return ErrorDetail(
            ErrorCode.SECRET_UNAVAILABLE,
            "The affected component could not obtain a required secret.",
            self._correlation_id,
            retryable=True,
            fields=(ErrorField(component.value, "Required secret unavailable."),),
        )


class HealthService:
    """Expose dependency-free liveness and separately authorized safe operational health."""

    def __init__(
        self,
        configuration_service: ConfigurationService,
        dependencies: tuple[HealthDependency, ...],
        *,
        build_version: str,
        schema_version: str,
        clock: Callable[[], datetime] = lambda: datetime.now(UTC),
        correlation_id: CorrelationId = _HEALTH_CORRELATION_ID,
    ) -> None:
        self._configuration_service = configuration_service
        self._dependencies = dependencies
        self._build_version = build_version
        self._schema_version = schema_version
        self._clock = clock
        self._correlation_id = correlation_id
        self._latest_readiness: ReadinessSnapshot | None = None

    def liveness(self) -> LivenessSnapshot:
        """Return process liveness without reading configuration or contacting a dependency."""
        return LivenessSnapshot()

    def readiness(self) -> ReadinessSnapshot:
        """Report required availability and optional unconfigured dependencies distinctly."""
        configuration = self._configuration_service.status
        statuses: list[DependencyReadiness] = []
        for dependency in self._dependencies:
            if not dependency.configured:
                state = (
                    DependencyState.UNAVAILABLE
                    if dependency.required
                    else DependencyState.NOT_CONFIGURED
                )
            elif configuration is None or not configuration.is_enabled(dependency.component):
                state = DependencyState.UNAVAILABLE
            else:
                state = self._probe(dependency)
            statuses.append(DependencyReadiness(dependency.name, dependency.required, state))
        self._latest_readiness = ReadinessSnapshot(tuple(statuses), self._timestamp())
        return self._latest_readiness

    def operational_health(
        self, *, authorized: bool
    ) -> Result[OperationalHealthSnapshot, ErrorDetail]:
        """Return authorized health only after safe startup and readiness evidence exists."""
        if not authorized:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.AUTHORIZATION_DENIED,
                    "Authorization is required for operational health.",
                    self._correlation_id,
                )
            )
        configuration = self._configuration_service.status
        readiness = self._latest_readiness
        if (
            configuration is None
            or readiness is None
            or not _is_safe_health_value(self._build_version)
            or not _is_safe_health_value(self._schema_version)
        ):
            return Result.failure(self._health_failure())
        components = tuple(
            ComponentHealthSummary(
                status.component,
                status.enabled,
                status.error.code if status.error is not None else None,
            )
            for status in configuration.components
        )
        return Result.success(
            OperationalHealthSnapshot(
                components,
                self._build_version,
                self._schema_version,
                readiness.checked_at,
            )
        )

    def _probe(self, dependency: HealthDependency) -> DependencyState:
        try:
            healthy = dependency.probe is not None and dependency.probe()
        except Exception:
            healthy = False
        return DependencyState.USABLE if healthy else DependencyState.UNAVAILABLE

    def _timestamp(self) -> datetime:
        timestamp = self._clock()
        if timestamp.tzinfo is None:
            raise ValueError("Health clocks must return timezone-aware timestamps.")
        return timestamp

    def _health_failure(self) -> ErrorDetail:
        return ErrorDetail(
            ErrorCode.HEALTH_UNAVAILABLE,
            "Required operational health fields are unavailable.",
            self._correlation_id,
            retryable=True,
        )


def _is_identifier(value: object) -> bool:
    return isinstance(value, str) and _IDENTIFIER.fullmatch(value) is not None


def _valid_origins(origins: tuple[str, ...]) -> bool:
    return all(
        isinstance(origin, str)
        and (parsed := urlparse(origin)).scheme in {"http", "https"}
        and bool(parsed.netloc)
        and parsed.path in {"", "/"}
        and not parsed.params
        and not parsed.query
        and not parsed.fragment
        and "*" not in origin
        for origin in origins
    )


def _valid_transport(configuration: DeploymentConfiguration) -> bool:
    """Require an explicit session model and HTTPS origins for production transport."""
    return isinstance(configuration.session_model, SessionModel) and (
        not configuration.production_transport_enabled
        or (
            bool(configuration.trusted_origins)
            and all(urlparse(origin).scheme == "https" for origin in configuration.trusted_origins)
        )
    )


def _valid_retention_policies(policies: Mapping[str, object]) -> bool:
    try:
        parse_retention_policies(policies)
    except (TypeError, ValueError):
        return False
    return True


def _valid_rate_limits(rate_limits: Mapping[str, object]) -> bool:
    return bool(rate_limits) and all(
        isinstance(route, str)
        and route.strip()
        and isinstance(limit, int)
        and not isinstance(limit, bool)
        and limit > 0
        for route, limit in rate_limits.items()
    )


def _valid_feature_flags(flags: Mapping[str, object]) -> bool:
    return all(
        _is_identifier(name) and isinstance(enabled, bool)
        for name, enabled in flags.items()
    )


def _valid_work_recovery_policy(policy: Mapping[str, object]) -> bool:
    decisions = {"reclaim", "manual_recovery", "dead_letter"}
    max_attempts = policy.get("max_attempts")
    retry_delay_seconds = policy.get("retry_delay_seconds")
    return (
        set(policy) == {
            "claim_expiry_decision",
            "worker_stop_decision",
            "max_attempts",
            "retry_delay_seconds",
        }
        and policy.get("claim_expiry_decision") in decisions
        and policy.get("worker_stop_decision") in decisions
        and isinstance(max_attempts, int)
        and not isinstance(max_attempts, bool)
        and max_attempts > 0
        and isinstance(retry_delay_seconds, int)
        and not isinstance(retry_delay_seconds, bool)
        and retry_delay_seconds >= 0
    )


def _is_safe_health_value(value: str) -> bool:
    normalized = value.casefold()
    return bool(_SAFE_HEALTH_VALUE.fullmatch(value)) and not any(
        marker in normalized for marker in ("secret", "token", "password", "credential")
    )
