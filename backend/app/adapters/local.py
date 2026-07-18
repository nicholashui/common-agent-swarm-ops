"""Concrete deterministic local adapters used by the Host tool broker."""

from __future__ import annotations

from app.adapters.base import DeterministicLocalAdapter

LOCAL_ADAPTER_VERSION = "1.0.0"


class ContractParsingAdapter(DeterministicLocalAdapter):
    """Locally parse contract data into a deterministic effect digest."""

    def __init__(self) -> None:
        super().__init__("contract.parse", LOCAL_ADAPTER_VERSION, "contract_parsed")


class PolicyLookupAdapter(DeterministicLocalAdapter):
    """Locally resolve an allowlisted policy lookup deterministically."""

    def __init__(self) -> None:
        super().__init__("policy.lookup", LOCAL_ADAPTER_VERSION, "policy_resolved")


class CrmAdapter(DeterministicLocalAdapter):
    """Locally record a deterministic CRM lookup effect."""

    def __init__(self) -> None:
        super().__init__("crm.lookup", LOCAL_ADAPTER_VERSION, "crm_record_resolved")


class BillingAdapter(DeterministicLocalAdapter):
    """Locally prepare a deterministic billing effect without charging anyone."""

    def __init__(self) -> None:
        super().__init__("billing.preview", LOCAL_ADAPTER_VERSION, "billing_preview_created")


class EmailAdapter(DeterministicLocalAdapter):
    """Locally prepare a deterministic email preview without delivering mail."""

    def __init__(self) -> None:
        super().__init__("email.preview", LOCAL_ADAPTER_VERSION, "email_preview_created")


class AuditAdapter(DeterministicLocalAdapter):
    """Locally prepare deterministic audit evidence without an external sink."""

    def __init__(self) -> None:
        super().__init__("audit.log", LOCAL_ADAPTER_VERSION, "audit_event_recorded")


class StubMediaAdapter(DeterministicLocalAdapter):
    """Create a deterministic stub-media effect with no media-provider dependency."""

    def __init__(self) -> None:
        super().__init__("media.stub", LOCAL_ADAPTER_VERSION, "stub_media_created")


def default_local_adapters() -> tuple[DeterministicLocalAdapter, ...]:
    """Create the complete fixed v1 local adapter allow-list for Host startup."""
    return (
        ContractParsingAdapter(),
        PolicyLookupAdapter(),
        CrmAdapter(),
        BillingAdapter(),
        EmailAdapter(),
        AuditAdapter(),
        StubMediaAdapter(),
    )
