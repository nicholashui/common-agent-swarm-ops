"""Fail-closed request ingress and quarantined import guards."""

from __future__ import annotations

import hashlib
import json
import re
import threading
import time
import unicodedata
from collections import defaultdict, deque
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field, replace
from datetime import datetime
from enum import StrEnum
from types import MappingProxyType
from typing import Protocol, runtime_checkable
from uuid import uuid4

from fastapi import Request, status

from app.api.v1.errors import PublicApiException
from app.api.v1.schemas import PublicError, ValidationIssueResponse
from app.models.common import RecordMetadata, utc_now
from app.models.contracts import ErrorCode, ErrorDetail, ErrorField, RepositoryError, Result
from app.models.control_plane import ImportId, ImportRecord, ImportScanState, SecurityEvidence
from app.models.identifiers import CorrelationId, OrganizationId, RecordId
from app.repositories.control_plane import ImportRepository

_PAGINATION_FIELDS = frozenset({"limit", "offset", "page", "page_size"})
_FILTER_FIELDS = frozenset({"filter", "filters"})
_SAFE_STORAGE_NAME = re.compile(r"[^a-z0-9._-]+")
_SHA256_HEX = re.compile(r"[0-9a-f]{64}")
_SAFE_EVIDENCE_CODE = re.compile(r"[a-z][a-z0-9_.-]{0,63}")


class UntrustedContentSource(StrEnum):
    """Sources that never carry operational authority into the control plane."""

    IMPORT = "import"
    RETRIEVAL = "retrieval"
    UPLOAD = "upload"
    THIRD_PARTY = "third_party"
    MODEL_OUTPUT = "model_output"


class ProhibitedInfluence(StrEnum):
    """Authority-bearing effects that untrusted data is never permitted to request."""

    GRANT_AUTHORITY = "authority_grant"
    SELECT_TOOL = "tool_selection"
    CHANGE_POLICY = "policy_change"
    BYPASS_VALIDATION = "validation_bypass"
    PRIVILEGED_EXECUTABLE_INSTRUCTION = "privileged_executable_instruction"


class SecurityIndicator(StrEnum):
    """Fixed, redaction-safe evidence codes; detector details are never retained."""

    PROMPT_INJECTION = "prompt_injection"
    PROHIBITED_CONTENT = "prohibited_content"
    SUSPICIOUS_TOOL_PROPOSAL = "suspicious_tool_proposal"
    ARTIFACT_MANIFEST_MISMATCH = "artifact_manifest_mismatch"
    AUTHORITY_INFLUENCE = "authority_influence"
    TOOL_SELECTION = "tool_selection"
    POLICY_MUTATION = "policy_mutation"
    VALIDATION_BYPASS = "validation_bypass"
    PRIVILEGED_INSTRUCTION = "privileged_instruction"
    PROTECTION_REJECTED = "protection_rejected"
    PROTECTION_ERROR = "protection_error"


_INFLUENCE_INDICATORS: Mapping[ProhibitedInfluence, SecurityIndicator] = MappingProxyType(
    {
        ProhibitedInfluence.GRANT_AUTHORITY: SecurityIndicator.AUTHORITY_INFLUENCE,
        ProhibitedInfluence.SELECT_TOOL: SecurityIndicator.TOOL_SELECTION,
        ProhibitedInfluence.CHANGE_POLICY: SecurityIndicator.POLICY_MUTATION,
        ProhibitedInfluence.BYPASS_VALIDATION: SecurityIndicator.VALIDATION_BYPASS,
        ProhibitedInfluence.PRIVILEGED_EXECUTABLE_INSTRUCTION: (
            SecurityIndicator.PRIVILEGED_INSTRUCTION
        ),
    }
)


@dataclass(frozen=True, slots=True)
class UntrustedContent:
    """Immutable data snapshot plus explicit non-authoritative influence observations."""

    metadata: RecordMetadata
    source: UntrustedContentSource
    payload: object
    import_id: ImportId | None = None
    influence_attempts: frozenset[ProhibitedInfluence] = frozenset()

    def __post_init__(self) -> None:
        if not isinstance(self.source, UntrustedContentSource):
            raise ValueError("A recognized untrusted-content source is required.")
        if any(not isinstance(item, ProhibitedInfluence) for item in self.influence_attempts):
            raise ValueError("A recognized prohibited influence is required.")
        object.__setattr__(self, "payload", _freeze_untrusted_value(self.payload))
        object.__setattr__(self, "influence_attempts", frozenset(self.influence_attempts))


@dataclass(frozen=True, slots=True)
class ProtectionOutcome:
    """A configured protection's safe outcome without raw detector output."""

    passed: bool
    indicators: tuple[SecurityIndicator, ...] = ()

    def __post_init__(self) -> None:
        if any(not isinstance(indicator, SecurityIndicator) for indicator in self.indicators):
            raise ValueError("Protection outcomes require recognized security indicators.")
        if self.passed and self.indicators:
            raise ValueError("A passing protection cannot report a security indicator.")
        object.__setattr__(self, "indicators", tuple(dict.fromkeys(self.indicators)))


@runtime_checkable
class UntrustedContentProtection(Protocol):
    """Trusted configured detector that can inspect data but receives no control state."""

    @property
    def protection_id(self) -> str:
        """Return a stable, non-sensitive identifier used in security evidence."""

    def inspect(self, content: UntrustedContent) -> ProtectionOutcome:
        """Inspect immutable untrusted data without applying any proposed effect."""


@dataclass(frozen=True, slots=True)
class GuardedUntrustedContent:
    """Data-only continuation token produced after every protection succeeds."""

    metadata: RecordMetadata
    source: UntrustedContentSource
    payload: object
    import_id: ImportId | None


class UntrustedContentGuard:
    """Fail complete unless every protection passes and no authority influence is attempted."""

    def __init__(
        self,
        repository: ImportRepository,
        protections: Iterable[UntrustedContentProtection],
        *,
        clock: Callable[[], datetime] = utc_now,
        evidence_id_factory: Callable[[], str] | None = None,
    ) -> None:
        configured = tuple(protections)
        protection_ids = tuple(protection.protection_id for protection in configured)
        if any(not _SAFE_EVIDENCE_CODE.fullmatch(identifier) for identifier in protection_ids):
            raise ValueError("Protection identifiers must be stable redaction-safe codes.")
        if len(set(protection_ids)) != len(protection_ids):
            raise ValueError("Configured protection identifiers must be unique.")
        self._repository = repository
        self._protections = configured
        self._clock = clock
        self._evidence_id_factory = evidence_id_factory or (lambda: str(uuid4()))

    def process(
        self, content: UntrustedContent
    ) -> Result[GuardedUntrustedContent, RepositoryError]:
        """Run every protection and expose no continuation on any prohibited outcome."""
        failures: list[tuple[str, SecurityIndicator]] = [
            ("untrusted-boundary", _INFLUENCE_INDICATORS[influence])
            for influence in sorted(content.influence_attempts, key=lambda item: item.value)
        ]

        for protection in self._protections:
            try:
                outcome = protection.inspect(content)
                if not outcome.passed:
                    indicators = outcome.indicators or (SecurityIndicator.PROTECTION_REJECTED,)
                    failures.extend(
                        (protection.protection_id, indicator) for indicator in indicators
                    )
            except Exception:  # A detector failure is denial, never a bypass.
                failures.append((protection.protection_id, SecurityIndicator.PROTECTION_ERROR))

        if not failures:
            return Result.success(
                GuardedUntrustedContent(
                    metadata=content.metadata,
                    source=content.source,
                    payload=content.payload,
                    import_id=content.import_id,
                )
            )

        for protection_id, indicator in failures:
            persisted = self._persist_failure(content, protection_id, indicator)
            if not persisted.is_success:
                return Result.failure(
                    persisted.error or self._evidence_failure(content.metadata.correlation_id)
                )
        return Result.failure(
            ErrorDetail(
                ErrorCode.VALIDATION_FAILED,
                "Untrusted content did not pass configured security protections.",
                content.metadata.correlation_id,
                fields=(ErrorField("content", "Further processing is prohibited."),),
            )
        )

    def _persist_failure(
        self,
        content: UntrustedContent,
        protection_id: str,
        indicator: SecurityIndicator,
    ) -> Result[SecurityEvidence, RepositoryError]:
        evidence_id = self._evidence_id_factory().strip()
        if not evidence_id:
            return Result.failure(self._evidence_failure(content.metadata.correlation_id))
        recorded_at = self._clock()
        evidence = SecurityEvidence(
            metadata=RecordMetadata(
                record_id=RecordId(f"security-evidence:{evidence_id}"),
                organization_id=content.metadata.organization_id,
                correlation_id=content.metadata.correlation_id,
                schema_version=content.metadata.schema_version,
                version=1,
                created_at=recorded_at,
                updated_at=recorded_at,
            ),
            security_evidence_id=evidence_id,
            import_id=content.import_id,
            indicator=indicator.value,
            protection=protection_id,
            passed=False,
            recorded_at=recorded_at,
        )
        try:
            return self._repository.append_security_evidence(evidence)
        except Exception:
            return Result.failure(self._evidence_failure(content.metadata.correlation_id))

    @staticmethod
    def _evidence_failure(correlation_id: CorrelationId) -> RepositoryError:
        return ErrorDetail(
            ErrorCode.REPOSITORY_UNAVAILABLE,
            "Security evidence could not be retained.",
            correlation_id,
            retryable=False,
        )


def _freeze_untrusted_value(value: object) -> object:
    """Copy supported data into immutable containers before protections inspect it."""
    if isinstance(value, Mapping):
        frozen: dict[str, object] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError("Untrusted content mappings require string keys.")
            frozen[key] = _freeze_untrusted_value(item)
        return MappingProxyType(frozen)
    if isinstance(value, list | tuple):
        return tuple(_freeze_untrusted_value(item) for item in value)
    if value is None or isinstance(value, str | bytes | int | float | bool):
        return value
    raise ValueError("Untrusted content must contain only immutable JSON-like data or bytes.")


@dataclass(frozen=True, slots=True)
class IngressPolicy:
    """Bounds evaluated before an API handler can process a request."""

    max_request_bytes: int = 1_048_576
    allowed_media_types: frozenset[str] = frozenset({"application/json", "multipart/form-data"})
    max_route_segment_length: int = 128
    max_body_depth: int = 8
    max_body_collection_items: int = 100
    max_body_string_length: int = 16_384
    max_page_size: int = 100
    max_page_offset: int = 10_000
    max_page_number: int = 1_000
    max_filter_count: int = 10
    max_filter_length: int = 1_024
    endpoint_rate_limits: Mapping[str, int] = field(default_factory=lambda: {"/api/v1": 120})
    rate_window_seconds: int = 60

    def __post_init__(self) -> None:
        if any(value <= 0 for value in self.endpoint_rate_limits.values()):
            raise ValueError("Endpoint rate limits must be positive.")
        if self.max_request_bytes <= 0 or self.rate_window_seconds <= 0:
            raise ValueError("Ingress request and rate bounds must be positive.")


class EndpointRateLimiter:
    """Thread-safe sliding-window limiter keyed by endpoint and remote peer."""

    def __init__(self, clock: Callable[[], float] = time.monotonic) -> None:
        self._clock = clock
        self._events: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def check(self, *, endpoint: str, subject: str, limit: int, window_seconds: int) -> int | None:
        """Record one request and return retry seconds only when its limit is reached."""
        now = self._clock()
        key = f"{endpoint}:{subject}"
        with self._lock:
            events = self._events[key]
            while events and now - events[0] >= window_seconds:
                events.popleft()
            if len(events) >= limit:
                return max(1, int(window_seconds - (now - events[0])))
            events.append(now)
        return None


class IngressGuard:
    """Validate public request structure and rate limits before handler execution."""

    def __init__(
        self, policy: IngressPolicy | None = None, rate_limiter: EndpointRateLimiter | None = None
    ) -> None:
        self._policy = policy or IngressPolicy()
        self._rate_limiter = rate_limiter or EndpointRateLimiter()

    async def validate_request(self, request: Request) -> None:
        """Reject malformed or over-limit input before routing reaches its handler."""
        body = await request.body()
        correlation_id = _request_correlation_id(request)
        declared_size = request.headers.get("content-length")
        if declared_size is not None and (
            not declared_size.isdecimal() or int(declared_size) > self._policy.max_request_bytes
        ):
            self._reject(correlation_id, "request", status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)
        if len(body) > self._policy.max_request_bytes:
            self._reject(correlation_id, "request", status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)
        self._validate_route_fields(request, correlation_id)
        self._validate_media_type(request, body, correlation_id)
        self._validate_query_bounds(request, correlation_id)
        self._validate_body_fields(request, body, correlation_id)
        self._validate_rate_limit(request, correlation_id)

    def _validate_route_fields(self, request: Request, correlation_id: CorrelationId) -> None:
        for segment in request.url.path.split("/"):
            if segment and (
                segment in {".", ".."} or len(segment) > self._policy.max_route_segment_length
            ):
                self._reject(correlation_id, "route")

    def _validate_media_type(
        self, request: Request, body: bytes, correlation_id: CorrelationId
    ) -> None:
        media_type = _media_type(request.headers.get("content-type", ""))
        if body and media_type not in self._policy.allowed_media_types:
            self._reject(correlation_id, "content_type", status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def _validate_query_bounds(self, request: Request, correlation_id: CorrelationId) -> None:
        filters = [
            item for item in request.query_params.multi_items() if item[0].lower() in _FILTER_FIELDS
        ]
        if len(filters) > self._policy.max_filter_count or any(
            len(value) > self._policy.max_filter_length for _, value in filters
        ):
            self._reject(correlation_id, "filter")
        for name, value in request.query_params.multi_items():
            if name.lower() in _PAGINATION_FIELDS:
                self._validate_pagination(name.lower(), value, correlation_id)

    def _validate_pagination(self, name: str, value: str, correlation_id: CorrelationId) -> None:
        if not value.isdecimal():
            self._reject(correlation_id, name)
        number = int(value)
        invalid = name in {"limit", "page_size"} and not 1 <= number <= self._policy.max_page_size
        invalid = invalid or (name == "offset" and not 0 <= number <= self._policy.max_page_offset)
        invalid = invalid or (name == "page" and not 1 <= number <= self._policy.max_page_number)
        if invalid:
            self._reject(correlation_id, name)

    def _validate_body_fields(
        self, request: Request, body: bytes, correlation_id: CorrelationId
    ) -> None:
        if not body or _media_type(request.headers.get("content-type", "")) != "application/json":
            return
        try:
            self._validate_body_value(json.loads(body), 0, correlation_id)
        except (TypeError, ValueError):
            self._reject(correlation_id, "body")

    def _validate_body_value(
        self, value: object, depth: int, correlation_id: CorrelationId
    ) -> None:
        if depth > self._policy.max_body_depth:
            self._reject(correlation_id, "body")
        if isinstance(value, str) and len(value) > self._policy.max_body_string_length:
            self._reject(correlation_id, "body")
        if isinstance(value, Mapping):
            if len(value) > self._policy.max_body_collection_items:
                self._reject(correlation_id, "body")
            for name, item in value.items():
                if not isinstance(name, str) or len(name) > self._policy.max_route_segment_length:
                    self._reject(correlation_id, "body")
                self._validate_body_value(item, depth + 1, correlation_id)
        elif isinstance(value, list):
            if len(value) > self._policy.max_body_collection_items:
                self._reject(correlation_id, "body")
            for item in value:
                self._validate_body_value(item, depth + 1, correlation_id)

    def _validate_rate_limit(self, request: Request, correlation_id: CorrelationId) -> None:
        matches = [
            prefix
            for prefix in self._policy.endpoint_rate_limits
            if request.url.path.startswith(prefix)
        ]
        if not matches:
            return
        endpoint = max(matches, key=len)
        client = request.client.host if request.client is not None else "unknown-client"
        retry_after = self._rate_limiter.check(
            endpoint=endpoint,
            subject=client,
            limit=self._policy.endpoint_rate_limits[endpoint],
            window_seconds=self._policy.rate_window_seconds,
        )
        if retry_after is not None:
            self._reject(
                correlation_id,
                "rate_limit",
                status.HTTP_429_TOO_MANY_REQUESTS,
                error_code=ErrorCode.RATE_LIMITED,
                headers={"Retry-After": str(retry_after)},
            )

    @staticmethod
    def _reject(
        correlation_id: CorrelationId,
        field: str,
        status_code: int = status.HTTP_422_UNPROCESSABLE_ENTITY,
        *,
        error_code: ErrorCode = ErrorCode.VALIDATION_FAILED,
        headers: Mapping[str, str] | None = None,
    ) -> None:
        raise PublicApiException(
            status_code=status_code,
            error=PublicError(
                code=error_code.value,
                message="The request could not be validated.",
                correlation_id=str(correlation_id),
                retryable=error_code is ErrorCode.RATE_LIMITED,
                fields=[ValidationIssueResponse(field=field, reason="Invalid value.")],
            ),
            headers=headers,
        )


@dataclass(frozen=True, slots=True)
class ImportPolicy:
    """Validated import limits and configured scanning policy."""

    max_import_bytes: int = 10_485_760
    allowed_media_types: frozenset[str] = frozenset(
        {"application/json", "text/plain", "application/pdf", "image/jpeg", "image/png"}
    )
    scanning_enabled: bool = True
    configured_scanners: frozenset[str] = frozenset({"default"})

    def __post_init__(self) -> None:
        if self.max_import_bytes <= 0:
            raise ValueError("Import size limit must be positive.")
        if self.scanning_enabled and not self.configured_scanners:
            raise ValueError("Configured scanning requires at least one scanner.")


class ScanDisposition(StrEnum):
    """The only scanner outcomes that can alter a quarantined import."""

    ALLOWED = "allowed"
    REJECTED = "rejected"


@dataclass(frozen=True, slots=True)
class ScanResult:
    """A result from a configured scanner; untrusted scan detail is deliberately absent."""

    scanner_name: str
    disposition: ScanDisposition

    def __post_init__(self) -> None:
        if not self.scanner_name.strip():
            raise ValueError("Scanner name must be non-empty.")


@dataclass(frozen=True, slots=True)
class ImportSubmission:
    """Untrusted bytes plus metadata checked before those bytes reach private storage."""

    metadata: RecordMetadata
    import_id: ImportId
    storage_name: str
    declared_type: str
    checksum: str
    content: bytes


@runtime_checkable
class ImportStorage(Protocol):
    """Private storage port addressed only by generated opaque references."""

    def quarantine(
        self, organization_id: OrganizationId, reference: str, content: bytes
    ) -> None: ...

    def release(self, organization_id: OrganizationId, reference: str) -> None: ...

    def discard(self, organization_id: OrganizationId, reference: str) -> None: ...


@runtime_checkable
class ContentTypeDetector(Protocol):
    """Trusted detector; a browser cannot select its detected media type."""

    def detect(self, content: bytes) -> str: ...


class BasicContentTypeDetector:
    """Deterministic detector for the safe import types supported by the façade."""

    def detect(self, content: bytes) -> str:
        if content.startswith(b"%PDF-"):
            return "application/pdf"
        if content.startswith(b"\x89PNG\r\n\x1a\n"):
            return "image/png"
        if content.startswith(b"\xff\xd8\xff"):
            return "image/jpeg"
        try:
            decoded = content.decode("utf-8")
        except UnicodeDecodeError:
            return "application/octet-stream"
        try:
            json.loads(decoded)
        except (TypeError, ValueError):
            return "text/plain"
        return "application/json"


class ImportGuard:
    """Validate imports before storage and disclose only scoped opaque references."""

    def __init__(
        self,
        repository: ImportRepository,
        storage: ImportStorage,
        *,
        policy: ImportPolicy | None = None,
        detector: ContentTypeDetector | None = None,
    ) -> None:
        self._repository = repository
        self._storage = storage
        self._policy = policy or ImportPolicy()
        self._detector = detector or BasicContentTypeDetector()

    def accept(
        self, organization_id: OrganizationId, submission: ImportSubmission
    ) -> Result[ImportRecord, RepositoryError]:
        """Validate every prerequisite before passing accepted bytes to private storage."""
        failure = self._validate_submission(organization_id, submission)
        if failure is not None:
            return Result.failure(failure)
        detected_type = _media_type(self._detector.detect(submission.content))
        failure = self._validate_detected_type(submission, detected_type)
        if failure is not None:
            return Result.failure(failure)
        reference = f"import:{uuid4()}"
        record = ImportRecord(
            metadata=submission.metadata,
            import_id=submission.import_id,
            declared_type=_media_type(submission.declared_type),
            detected_type=detected_type,
            size_bytes=len(submission.content),
            checksum=submission.checksum.lower(),
            normalized_storage_name=_normalize_storage_name(submission.storage_name),
            scan_state=(
                ImportScanState.QUARANTINED
                if self._policy.scanning_enabled
                else ImportScanState.ALLOWED
            ),
            opaque_storage_reference=reference,
        )
        try:
            self._storage.quarantine(organization_id, reference, submission.content)
            if not self._policy.scanning_enabled:
                self._storage.release(organization_id, reference)
        except OSError:
            return Result.failure(self._failure(submission.metadata, "storage"))
        persisted = self._repository.append_import(record)
        if not persisted.is_success:
            self._storage.discard(organization_id, reference)
        return persisted

    def record_scan_result(
        self,
        organization_id: OrganizationId,
        import_id: ImportId,
        result: ScanResult,
    ) -> Result[ImportRecord, RepositoryError]:
        """Release only a quarantined import after an allowed configured scanner result."""
        found = self._repository.get_import(organization_id, import_id)
        if not found.is_success or found.value is None:
            return Result.failure(found.error or self._lookup_failure())
        record = found.value
        if (
            not self._policy.scanning_enabled
            or result.scanner_name not in self._policy.configured_scanners
            or record.scan_state is not ImportScanState.QUARANTINED
            or record.opaque_storage_reference is None
        ):
            return Result.failure(self._failure(record.metadata, "scan"))
        reference = record.opaque_storage_reference
        try:
            if result.disposition is ScanDisposition.ALLOWED:
                self._storage.release(organization_id, reference)
                updated = replace(record, scan_state=ImportScanState.ALLOWED)
            else:
                self._storage.discard(organization_id, reference)
                updated = replace(
                    record,
                    scan_state=ImportScanState.REJECTED,
                    opaque_storage_reference=None,
                )
        except OSError:
            return Result.failure(self._failure(record.metadata, "storage"))
        return self._repository.replace_import(updated)

    def authorized_reference(
        self, organization_id: OrganizationId, import_id: ImportId
    ) -> Result[str, RepositoryError]:
        """Return a reference only after organization-scoped lookup and scan release."""
        found = self._repository.get_import(organization_id, import_id)
        if not found.is_success or found.value is None:
            return Result.failure(found.error or self._lookup_failure())
        record = found.value
        if (
            record.scan_state is not ImportScanState.ALLOWED
            or record.opaque_storage_reference is None
        ):
            return Result.failure(self._failure(record.metadata, "import"))
        return Result.success(record.opaque_storage_reference)

    def _validate_submission(
        self, organization_id: OrganizationId, submission: ImportSubmission
    ) -> RepositoryError | None:
        if submission.metadata.organization_id != organization_id:
            return ErrorDetail(
                ErrorCode.AUTHORIZATION_DENIED,
                "Import ownership validation failed.",
                submission.metadata.correlation_id,
            )
        if not submission.content or len(submission.content) > self._policy.max_import_bytes:
            return self._failure(submission.metadata, "size")
        if _media_type(submission.declared_type) not in self._policy.allowed_media_types:
            return self._failure(submission.metadata, "media_type")
        if hashlib.sha256(submission.content).hexdigest() != submission.checksum.lower():
            return self._failure(submission.metadata, "checksum")
        if not _SHA256_HEX.fullmatch(submission.checksum.lower()):
            return self._failure(submission.metadata, "checksum")
        try:
            _normalize_storage_name(submission.storage_name)
        except ValueError:
            return self._failure(submission.metadata, "storage_name")
        return None

    def _validate_detected_type(
        self, submission: ImportSubmission, detected: str
    ) -> RepositoryError | None:
        if (
            detected not in self._policy.allowed_media_types
            or _media_type(submission.declared_type) != detected
        ):
            return self._failure(submission.metadata, "media_type")
        return None

    @staticmethod
    def _failure(metadata: RecordMetadata, field: str) -> RepositoryError:
        return ErrorDetail(
            ErrorCode.VALIDATION_FAILED,
            "Import validation failed.",
            metadata.correlation_id,
            fields=(ErrorField(field, "Invalid value."),),
        )

    @staticmethod
    def _lookup_failure() -> RepositoryError:
        return ErrorDetail(
            ErrorCode.NOT_FOUND,
            "Import record was not found.",
            CorrelationId("import-guard"),
        )


def _media_type(value: str) -> str:
    """Normalize media types before policy comparison."""
    return value.split(";", 1)[0].strip().lower()


def _normalize_storage_name(value: str) -> str:
    """Reject traversal and normalize a single safe storage object name."""
    normalized = unicodedata.normalize("NFKC", value).strip().lower()
    if not normalized or "\x00" in normalized or "/" in normalized or "\\" in normalized:
        raise ValueError("Storage name must be a single safe filename.")
    normalized = _SAFE_STORAGE_NAME.sub("-", normalized).strip(".-")
    if not normalized or normalized in {".", ".."} or len(normalized) > 128:
        raise ValueError("Storage name exceeds configured bounds.")
    return normalized


def _request_correlation_id(request: Request) -> CorrelationId:
    """Preserve middleware correlation state without accepting browser input."""
    current = getattr(request.state, "request_correlation_id", None)
    if isinstance(current, str) and current.strip():
        return CorrelationId(current)
    correlation_id = CorrelationId(str(uuid4()))
    request.state.request_correlation_id = correlation_id
    return correlation_id
