"""Focused behavior checks for broker-only deterministic local adapters."""

from __future__ import annotations

import pytest

from app.adapters import (
    LOCAL_ADAPTER_VERSION,
    BrokerOnlyAdapterError,
    ContractParsingAdapter,
    default_local_adapters,
)
from app.audit import AuditWriter
from app.governance.tool_broker import HostToolBroker, ToolRequest
from tests.fakes.broker import InMemoryAuditRepository, authorized_context


def test_default_local_adapters_cover_every_required_local_operation() -> None:
    """Every required capability has a unique fixed-version local adapter."""
    adapters = default_local_adapters()

    assert tuple(adapter.adapter_id for adapter in adapters) == (
        "contract.parse",
        "policy.lookup",
        "crm.lookup",
        "billing.preview",
        "email.preview",
        "audit.log",
        "media.stub",
    )
    assert all(adapter.version == LOCAL_ADAPTER_VERSION for adapter in adapters)
    assert all(adapter.local_only for adapter in adapters)


def test_adapter_execution_is_rejected_outside_the_host_tool_broker() -> None:
    """Concrete adapters cannot be called directly by workflow or agent code."""
    with pytest.raises(BrokerOnlyAdapterError):
        ContractParsingAdapter().execute({"document": "terms"})


def test_broker_execution_is_deterministic_and_retains_each_tool_effect() -> None:
    """Broker-only execution yields stable versioned effects retained by the adapter."""
    adapters = default_local_adapters()
    broker = HostToolBroker(adapters, AuditWriter(InMemoryAuditRepository()))
    context = authorized_context(tuple(adapter.adapter_id for adapter in adapters))

    first_results = tuple(
        broker.request_tool(ToolRequest(adapter.adapter_id, {"case_id": "case-1"}), context)
        for adapter in adapters
    )
    second = broker.request_tool(ToolRequest("contract.parse", {"case_id": "case-1"}), context)

    assert all(result.allowed and result.effect is not None for result in first_results)
    assert second.effect is not None
    assert first_results[0].effect is not None
    assert second.effect.effect_digest == first_results[0].effect.effect_digest
    assert adapters[0].retained_effects == (first_results[0].effect, second.effect)
