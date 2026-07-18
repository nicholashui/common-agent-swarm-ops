"""Broker-only deterministic local adapters with no network dependency."""

from app.adapters.base import DeterministicLocalAdapter
from app.adapters.local import (
    LOCAL_ADAPTER_VERSION,
    AuditAdapter,
    BillingAdapter,
    ContractParsingAdapter,
    CrmAdapter,
    EmailAdapter,
    PolicyLookupAdapter,
    StubMediaAdapter,
    default_local_adapters,
)
from app.governance.adapter_execution import BrokerOnlyAdapterError

__all__ = [
    "LOCAL_ADAPTER_VERSION",
    "AuditAdapter",
    "BillingAdapter",
    "BrokerOnlyAdapterError",
    "ContractParsingAdapter",
    "CrmAdapter",
    "DeterministicLocalAdapter",
    "EmailAdapter",
    "PolicyLookupAdapter",
    "StubMediaAdapter",
    "default_local_adapters",
]
