"""Focused tests for centralized redaction and validated data lifecycle."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta

from app.api.v1.errors import public_error_response, public_success_response
from app.api.v1.schemas import PublicError
from app.core.configuration import ConfigurationService, StartupComponent
from app.core.retention import RetentionService
from app.models.common import RecordMetadata
from app.models.contracts import ErrorDetail, Result
from app.models.control_plane import (
    AuditRecord,
    DeploymentConfiguration,
    EventId,
    OperationalEvent,
)
from app.models.identifiers import CorrelationId, OrganizationId, RecordId
from app.models.redaction import (
    REDACTED,
    RedactionService,
    RedactionSurface,
    configure_deployment_secrets,
)
from app.models.retention import (
    PreservedRetentionEvidence,
    RetentionAction,
    RetentionCategory,
    RetentionRecord,
)

_NOW = datetime(2025, 1, 31, tzinfo=UTC)
_CORRELATION_ID = CorrelationId("redaction-retention-test")


def _metadata() -> RecordMetadata:
    return RecordMetadata(
        record_id=RecordId("record-1"),
        organization_id=OrganizationId("org-1"),
        correlation_id=_CORRELATION_ID,
        schema_version=1,
        version=1,
        created_at=_NOW,
        updated_at=_NOW,
    )


def _policy(
    action: str,
    *,
    preserve_authorization: bool = False,
    preserve_provenance: bool = False,
) -> dict[str, object]:
    return {
        "max_age_days": 10,
        "action": action,
        "preserve_authorization_evidence": preserve_authorization,
        "preserve_provenance_evidence": preserve_provenance,
    }

def _configuration(
    retention_policies: dict[str, object], *, secret_references: tuple[str, ...] = ()
) -> DeploymentConfiguration:
    return DeploymentConfiguration(
        metadata=_metadata(),
        configuration_id="deployment-v1",
        trusted_origins=("https://console.example",),
        identity_integration="oidc",
        persistence_adapter="postgres",
        dispatch_adapter="queue",
        retention_policies=retention_policies,
        rate_limits={"/api/v1": 10},
        feature_flags={},
        secret_references=secret_references,
        production_transport_enabled=True,
    )


@dataclass
class _RetentionRepository:
    records: list[RetentionRecord]
    applied: list[
        tuple[RetentionRecord, RetentionAction, PreservedRetentionEvidence]
    ] = field(default_factory=list)

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


def test_redaction_service_excludes_every_sensitive_class_from_every_surface() -> None:
    """Every required sensitive class is excluded from every named output surface."""
    deployment_secret = "deployment-value-123"
    redactor = RedactionService((deployment_secret,))
    payload = {
        "credential": "credential-value",
        "access_token": "token-value",
        "raw_prompt": "private prompt",
        "protected_artifact_content": "private artifact",
        "prohibited_tool_input": {"command": "dangerous"},
        "nested": {"deployment_secret_reference": "ENV_SECRET"},
        "summary": f"safe prefix {deployment_secret}",
        "message": "Bearer bearer-value",
        "allowed_reference": "artifact-ref-1",
    }

    for surface in RedactionSurface:
        safe = redactor.redact(payload, surface=surface)
        serialized = repr(safe)
        for sensitive in (
            "credential-value",
            "token-value",
            "private prompt",
            "private artifact",
            "dangerous",
            "ENV_SECRET",
            deployment_secret,
            "bearer-value",
        ):
            assert sensitive not in serialized
        assert isinstance(safe, Mapping)
        assert safe["allowed_reference"] == "artifact-ref-1"


def test_configured_deployment_secret_is_redacted_by_default_public_and_observability_paths(
) -> None:
    """A resolved deployment secret never crosses default public, error, audit, or event paths."""
    deployment_secret = "deployment-secret-value"
    configuration = ConfigurationService(environment={"DEPLOYMENT_SECRET": deployment_secret})
    configuration.initialize(
        _configuration(
            {"operational_events": _policy("archive")},
            secret_references=("DEPLOYMENT_SECRET",),
        )
    )

    try:
        response = public_success_response(
            {"summary": f"status: {deployment_secret}"}, _CORRELATION_ID
        )
        error_response = public_error_response(
            PublicError(
                code="internal_error",
                message=f"diagnostic: {deployment_secret}",
                correlation_id=str(_CORRELATION_ID),
                retryable=True,
                fields=[],
            ),
            status_code=500,
        )
        audit = AuditRecord(
            metadata=_metadata(),
            audit_id="audit-secret",
            action=f"operation: {deployment_secret}",
            subject_reference="run-1",
            outcome="completed",
            recorded_at=_NOW,
        )
        event = OperationalEvent(
            metadata=_metadata(),
            event_id=EventId("event-secret"),
            sequence=1,
            event_type="run.updated",
            subject_reference="run-1",
            occurred_at=_NOW,
            payload_schema_version=1,
            redacted_payload={"summary": f"status: {deployment_secret}"},
        )

        assert json.loads(bytes(response.body))["data"]["summary"] == f"status: {REDACTED}"
        assert deployment_secret not in json.dumps(json.loads(bytes(error_response.body)))
        assert audit.action == f"operation: {REDACTED}"
        assert event.redacted_payload["summary"] == f"status: {REDACTED}"
    finally:
        configure_deployment_secrets(())


def test_public_and_operational_event_boundaries_apply_central_redaction() -> None:
    """Direct route responses and retained events sanitize payloads even if callers forget."""
    response = public_success_response(
        {"raw_prompt": "do not expose", "summary": "safe"}, _CORRELATION_ID
    )
    body = json.loads(bytes(response.body))
    event = OperationalEvent(
        metadata=_metadata(),
        event_id=EventId("event-1"),
        sequence=1,
        event_type="run.updated",
        subject_reference="run-1",
        occurred_at=_NOW,
        payload_schema_version=1,
        redacted_payload={
            "protected_artifact": "artifact bytes",
            "prohibited_tool_input": "shell command",
            "summary": "safe",
        },
    )

    audit = AuditRecord(
        metadata=_metadata(),
        audit_id="audit-1",
        action="token=private-token",
        subject_reference="run-1",
        outcome="completed",
        recorded_at=_NOW,
    )

    assert body["data"] == {"raw_prompt": REDACTED, "summary": "safe"}
    assert audit.action == REDACTED
    assert event.redacted_payload == {
        "protected_artifact": REDACTED,
        "prohibited_tool_input": REDACTED,
        "summary": "safe",
    }


def test_retention_applies_archive_and_delete_with_exact_evidence_preservation() -> None:
    """Only expired records transition and evidence survives exactly when policy requires it."""
    old = _NOW - timedelta(days=20)
    repository = _RetentionRepository(
        [
            RetentionRecord(
                "event-old",
                RetentionCategory.OPERATIONAL_EVENTS,
                old,
                provenance_evidence={"run": "run-1"},
            ),
            RetentionRecord(
                "audit-old",
                RetentionCategory.AUDIT_RECORDS,
                old,
                authorization_evidence={"decision": "allow-1"},
                provenance_evidence={"ignored": "value"},
            ),
            RetentionRecord(
                "event-current",
                RetentionCategory.OPERATIONAL_EVENTS,
                _NOW - timedelta(days=2),
                provenance_evidence={"run": "run-2"},
            ),
        ]
    )
    configuration = ConfigurationService(environment={})
    configuration.initialize(
        _configuration(
            {
                "operational_events": _policy("archive", preserve_provenance=True),
                "audit_records": _policy("delete", preserve_authorization=True),
            }
        )
    )

    result = RetentionService(configuration, repository, clock=lambda: _NOW).apply_expired()

    assert result.is_success and result.value is not None
    assert {(outcome.record_id, outcome.action) for outcome in result.value} == {
        ("event-old", RetentionAction.ARCHIVE),
        ("audit-old", RetentionAction.DELETE),
    }
    applied = {record.record_id: evidence for record, _, evidence in repository.applied}
    assert applied["event-old"].authorization is None
    assert applied["event-old"].provenance == {"run": "run-1"}
    assert applied["audit-old"].authorization == {"decision": "allow-1"}
    assert applied["audit-old"].provenance is None


def test_invalid_or_evidence_incomplete_retention_policy_fails_before_lifecycle() -> None:
    """Unvalidated policy and missing required evidence cannot archive or delete a record."""
    old_record = RetentionRecord(
        "artifact-old", RetentionCategory.ARTIFACTS, _NOW - timedelta(days=20)
    )
    repository = _RetentionRepository([old_record])
    invalid_configuration = ConfigurationService(environment={})
    status = invalid_configuration.initialize(
        _configuration({"artifacts": {**_policy("purge"), "unknown": True}})
    )

    invalid = RetentionService(
        invalid_configuration, repository, clock=lambda: _NOW
    ).apply_expired()

    assert not status.is_enabled(StartupComponent.RETENTION)
    assert not invalid.is_success
    assert repository.applied == []

    missing_evidence_configuration = ConfigurationService(environment={})
    missing_evidence_configuration.initialize(
        _configuration({"artifacts": _policy("delete", preserve_provenance=True)})
    )
    missing = RetentionService(
        missing_evidence_configuration, repository, clock=lambda: _NOW
    ).apply_expired()

    assert not missing.is_success
    assert repository.applied == []
