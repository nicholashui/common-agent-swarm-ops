"""Typed, serializable success and failure contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Generic, TypeVar

from app.models.common import CompatibilityRange, validate_semantic_version
from app.models.identifiers import (
    ActorId,
    AgentId,
    AgentLearningContractId,
    CorrelationId,
    DomainPackId,
    EvidenceId,
    HostContractId,
    PackContractId,
    new_correlation_id,
)

T_co = TypeVar("T_co", covariant=True)
E_co = TypeVar("E_co", covariant=True)


class ErrorCode(StrEnum):
    """Stable codes safe to expose through the public control plane."""

    AUTHENTICATION_REQUIRED = "authentication_required"
    AUTHORIZATION_DENIED = "authorization_denied"
    AUDIT_UNAVAILABLE = "audit_unavailable"
    CONFIGURATION_INVALID = "configuration_invalid"
    CONFLICT = "conflict"
    HEALTH_UNAVAILABLE = "health_unavailable"
    INTERNAL_ERROR = "internal_error"
    INVALID_TRANSITION = "invalid_transition"
    METHOD_NOT_ALLOWED = "method_not_allowed"
    NOT_FOUND = "not_found"
    RATE_LIMITED = "rate_limited"
    REPOSITORY_UNAVAILABLE = "repository_unavailable"
    SECRET_UNAVAILABLE = "secret_unavailable"
    VALIDATION_FAILED = "validation_failed"


@dataclass(frozen=True, slots=True)
class ErrorField:
    """A safe validation-field failure detail."""

    name: str
    reason: str


@dataclass(frozen=True, slots=True)
class ErrorDetail:
    """A redaction-safe, correlation-bearing operational error."""

    code: ErrorCode
    message: str
    correlation_id: CorrelationId
    retryable: bool = False
    fields: tuple[ErrorField, ...] = ()


@dataclass(frozen=True, slots=True, init=False)
class Result(Generic[T_co, E_co]):  # noqa: UP046 - explicit variance is required by mypy.
    """A typed result that has exactly one of a value or an error."""

    _value: T_co | None
    _error: E_co | None

    def __init__(self, value: T_co | None = None, error: E_co | None = None) -> None:
        if (value is None) == (error is None):
            raise ValueError("Result requires exactly one of value or error")
        object.__setattr__(self, "_value", value)
        object.__setattr__(self, "_error", error)

    @property
    def value(self) -> T_co | None:
        """Return the successful value when present."""
        return self._value

    @property
    def error(self) -> E_co | None:
        """Return the failure value when present."""
        return self._error

    @property
    def is_success(self) -> bool:
        """Return whether this result holds a value."""
        return self.error is None

    @classmethod
    def success[T, E](cls: type[Result[T, E]], value: T) -> Result[T, E]:
        """Build a successful typed result."""
        return cls(value=value)

    @classmethod
    def failure[T, E](cls: type[Result[T, E]], error: E) -> Result[T, E]:
        """Build a failed typed result."""
        return cls(error=error)


RepositoryError = ErrorDetail


class CommandOutcomeKind(StrEnum):
    """The complete set of command outcomes exposed by the control plane."""

    ALLOWED = "allowed"
    DENIED = "denied"
    BLOCKED = "blocked"
    FAILED_RECOVERABLE = "failed_recoverable"


def _require_text(value: str, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be non-empty.")


def _require_unique(values: tuple[str, ...], name: str) -> None:
    if len(values) != len(set(values)):
        raise ValueError(f"{name} must not contain duplicate values.")


def _reason_text(reason: str | ErrorDetail) -> str:
    if isinstance(reason, ErrorDetail):
        return reason.message
    _require_text(reason, "reason")
    return reason


@dataclass(frozen=True, slots=True)
class Allowed[T_co]:
    """An explicitly authorized command outcome backed by evidence."""

    value: T_co
    evidence: tuple[EvidenceId, ...]
    correlation_id: CorrelationId = field(default_factory=new_correlation_id)
    kind: CommandOutcomeKind = field(default=CommandOutcomeKind.ALLOWED, init=False)

    def __post_init__(self) -> None:
        if not self.evidence:
            raise ValueError("Allowed outcomes require at least one evidence reference.")
        _require_unique(tuple(str(item) for item in self.evidence), "evidence")
        if any(not str(item).strip() for item in self.evidence):
            raise ValueError("Allowed outcome evidence references must be non-empty.")

    @property
    def is_allowed(self) -> bool:
        """Return whether this outcome authorizes the command."""
        return True

    def __bool__(self) -> bool:
        return True


@dataclass(frozen=True, slots=True)
class Denied:
    """A policy or authorization denial; callers must not retry it as an allow."""

    reason: str | ErrorDetail
    correlation_id: CorrelationId = field(default_factory=new_correlation_id)
    kind: CommandOutcomeKind = field(default=CommandOutcomeKind.DENIED, init=False)

    def __post_init__(self) -> None:
        _reason_text(self.reason)

    @property
    def is_allowed(self) -> bool:
        """Return whether this outcome authorizes the command."""
        return False

    def __bool__(self) -> bool:
        return False


@dataclass(frozen=True, slots=True)
class Blocked:
    """A command held by an unmet gate or incomplete required evidence."""

    reason: str | ErrorDetail
    correlation_id: CorrelationId = field(default_factory=new_correlation_id)
    kind: CommandOutcomeKind = field(default=CommandOutcomeKind.BLOCKED, init=False)

    def __post_init__(self) -> None:
        _reason_text(self.reason)

    @property
    def is_allowed(self) -> bool:
        """Return whether this outcome authorizes the command."""
        return False

    def __bool__(self) -> bool:
        return False


@dataclass(frozen=True, slots=True)
class FailedRecoverable:
    """A dependency or persistence failure that requires recovery before retry."""

    reason: str | ErrorDetail
    correlation_id: CorrelationId = field(default_factory=new_correlation_id)
    kind: CommandOutcomeKind = field(default=CommandOutcomeKind.FAILED_RECOVERABLE, init=False)

    def __post_init__(self) -> None:
        _reason_text(self.reason)

    @property
    def is_allowed(self) -> bool:
        """Return whether this outcome authorizes the command."""
        return False

    def __bool__(self) -> bool:
        return False


type CommandOutcome[T] = Allowed[T] | Denied | Blocked | FailedRecoverable


@dataclass(frozen=True, slots=True)
class HostContract:
    """An independently versioned host API and its supported contract ranges."""

    version: str
    supported_pack_range: CompatibilityRange
    supported_alc_range: CompatibilityRange
    contract_id: HostContractId | None = None
    api_name: str = "adoption-platform"

    def __post_init__(self) -> None:
        validate_semantic_version(self.version, "Host_Contract version")
        _require_text(self.api_name, "Host_Contract api_name")

    @property
    def api_version(self) -> str:
        """Return the independently versioned host API version."""
        return self.version


@dataclass(frozen=True, slots=True)
class AgentLearningContract:
    """An independently versioned, agent-scoped learning policy declaration."""

    agent_id: AgentId
    version: str
    memory_scopes: tuple[str, ...]
    retrieval_policy: str
    reflection_policy: str
    evaluation_references: tuple[str, ...]
    retention_policy: str
    human_promotion_policy: str
    contract_id: AgentLearningContractId | None = None
    content_digest: str | None = None

    def __post_init__(self) -> None:
        _require_text(str(self.agent_id), "Agent_Learning_Contract agent_id")
        validate_semantic_version(self.version, "Agent_Learning_Contract version")
        for value, name in (
            (self.retrieval_policy, "retrieval_policy"),
            (self.reflection_policy, "reflection_policy"),
            (self.retention_policy, "retention_policy"),
            (self.human_promotion_policy, "human_promotion_policy"),
        ):
            _require_text(value, name)
        scopes = tuple(self.memory_scopes)
        references = tuple(self.evaluation_references)
        if not scopes:
            raise ValueError("Agent_Learning_Contract requires a memory scope.")
        if any(not item.strip() for item in scopes):
            raise ValueError("Agent_Learning_Contract memory scopes must be non-empty.")
        if any(not item.strip() for item in references):
            raise ValueError("Agent_Learning_Contract evaluation references must be non-empty.")
        _require_unique(scopes, "memory_scopes")
        _require_unique(references, "evaluation_references")
        object.__setattr__(self, "memory_scopes", scopes)
        object.__setattr__(self, "evaluation_references", references)
        if self.content_digest is not None:
            _require_text(self.content_digest, "content_digest")


@dataclass(frozen=True, slots=True)
class DomainPack:
    """An immutable, declarative domain package consumed by one Pack_Contract."""

    pack_id: DomainPackId
    immutable_version: str
    pack_contract_version: str
    host_compatibility_range: CompatibilityRange
    alc_compatibility_range: CompatibilityRange
    content_digest: str
    signer_id: ActorId
    agents: tuple[AgentId, ...]
    workflows: tuple[str, ...]
    capabilities: tuple[str, ...]
    data_classifications: tuple[str, ...]
    evaluation_references: tuple[str, ...]
    required_alc_version: str | None = None
    asset_references: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _require_text(str(self.pack_id), "Domain_Pack pack_id")
        validate_semantic_version(self.immutable_version, "Domain_Pack immutable_version")
        validate_semantic_version(self.pack_contract_version, "Pack_Contract version")
        _require_text(self.content_digest, "content_digest")
        _require_text(str(self.signer_id), "signer_id")
        collections = (
            (self.agents, "agents"),
            (self.workflows, "workflows"),
            (self.capabilities, "capabilities"),
            (self.data_classifications, "data_classifications"),
            (self.evaluation_references, "evaluation_references"),
            (self.asset_references, "asset_references"),
        )
        for values, name in collections:
            normalized = tuple(str(item) for item in values)
            if any(not item.strip() for item in normalized):
                raise ValueError(f"Domain_Pack {name} must contain non-empty values.")
            _require_unique(normalized, name)
            object.__setattr__(self, name, normalized)
        if not self.agents:
            raise ValueError("Domain_Pack requires at least one declared agent.")
        if not self.workflows:
            raise ValueError("Domain_Pack requires at least one declared workflow.")
        if self.required_alc_version is not None:
            validate_semantic_version(self.required_alc_version, "required_alc_version")
            if not self.alc_compatibility_range.contains(self.required_alc_version):
                raise ValueError("required_alc_version must be inside the ALC compatibility range.")

    @property
    def version(self) -> str:
        """Return the immutable package version."""
        return self.immutable_version

    @property
    def host_range(self) -> CompatibilityRange:
        """Return the declared Host_Contract compatibility range."""
        return self.host_compatibility_range

    @property
    def alc_range(self) -> CompatibilityRange:
        """Return the declared ALC compatibility range."""
        return self.alc_compatibility_range


@dataclass(frozen=True, slots=True)
class PackContract:
    """The versioned, domain-neutral schema required by every Domain_Pack."""

    version: str
    contract_id: PackContractId | None = None
    required_fields: tuple[str, ...] = (
        "pack_id",
        "immutable_version",
        "host_compatibility_range",
        "content_digest",
        "signer_id",
        "agents",
        "workflows",
        "capabilities",
        "data_classifications",
        "required_alc_version",
        "evaluation_references",
    )

    def __post_init__(self) -> None:
        validate_semantic_version(self.version, "Pack_Contract version")
        fields = tuple(self.required_fields)
        if any(not item.strip() for item in fields):
            raise ValueError("Pack_Contract required fields must be non-empty.")
        _require_unique(fields, "required_fields")
        object.__setattr__(self, "required_fields", fields)

    @property
    def contract_version(self) -> str:
        """Return the independently versioned Pack_Contract version."""
        return self.version

    def validate(self, pack: DomainPack) -> tuple[str, ...]:
        """Return failed Pack_Contract categories without partially accepting a pack."""
        failures: list[str] = []
        if pack.pack_contract_version != self.version:
            failures.append("pack_contract_version")
        if pack.required_alc_version is None:
            failures.append("required_alc_version")
        for field_name in self.required_fields:
            value = getattr(pack, field_name, None)
            if value is None or value == () or value == "":
                failures.append(field_name)
        return tuple(dict.fromkeys(failures))


# Specification terminology aliases retain the repository's CamelCase Python API.
Host_Contract = HostContract
Pack_Contract = PackContract
Agent_Learning_Contract = AgentLearningContract
Domain_Pack = DomainPack
