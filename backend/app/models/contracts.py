"""Typed, serializable success and failure contracts."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Generic, TypeVar

from app.models.identifiers import CorrelationId

T_co = TypeVar("T_co", covariant=True)
E_co = TypeVar("E_co", covariant=True)


class ErrorCode(StrEnum):
    """Stable codes safe to expose through the public control plane."""

    AUTHORIZATION_DENIED = "authorization_denied"
    AUDIT_UNAVAILABLE = "audit_unavailable"
    CONFLICT = "conflict"
    INVALID_TRANSITION = "invalid_transition"
    NOT_FOUND = "not_found"
    REPOSITORY_UNAVAILABLE = "repository_unavailable"
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
