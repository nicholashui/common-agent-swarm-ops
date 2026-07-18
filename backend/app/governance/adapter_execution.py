"""Internal execution scope that prevents direct adapter invocation."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar


class BrokerOnlyAdapterError(PermissionError):
    """Raised when a local adapter is called outside HostToolBroker."""


_broker_invocation_depth: ContextVar[int] = ContextVar("broker_invocation_depth", default=0)


@contextmanager
def broker_invocation() -> Iterator[None]:
    """Mark the current call stack as an authorized broker invocation."""
    token = _broker_invocation_depth.set(_broker_invocation_depth.get() + 1)
    try:
        yield
    finally:
        _broker_invocation_depth.reset(token)


def require_broker_invocation() -> None:
    """Reject direct execution so adapters remain reachable only through the broker."""
    if _broker_invocation_depth.get() < 1:
        raise BrokerOnlyAdapterError("Local adapters may only execute through HostToolBroker")
