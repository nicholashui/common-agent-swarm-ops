"""Shared public-response serialization and redaction-safe FastAPI error mapping."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import Response

from app.api.v1.schemas import (
    PublicError,
    PublicErrorResponse,
    PublicResponse,
    PublicResponseMeta,
    ValidationIssueResponse,
)
from app.models.contracts import ErrorCode, ErrorDetail, Result
from app.models.identifiers import CorrelationId, new_correlation_id
from app.models.redaction import RedactionSurface, redact_value

if TYPE_CHECKING:
    from collections.abc import Sequence

PUBLIC_ENVELOPE_HEADER = "X-Internal-Public-Envelope"

_PUBLIC_MESSAGES: dict[ErrorCode, str] = {
    ErrorCode.AUTHENTICATION_REQUIRED: "Authentication is required for control-plane access.",
    ErrorCode.AUTHORIZATION_DENIED: "You are not authorized to perform this action.",
    ErrorCode.AUDIT_UNAVAILABLE: "The service is temporarily unavailable.",
    ErrorCode.CONFIGURATION_INVALID: "The requested service component is not configured.",
    ErrorCode.CONFLICT: "The requested change conflicts with the current resource state.",
    ErrorCode.HEALTH_UNAVAILABLE: "Operational health details are temporarily unavailable.",
    ErrorCode.INTERNAL_ERROR: "The service could not complete the request.",
    ErrorCode.INVALID_TRANSITION: "The requested change conflicts with the current resource state.",
    ErrorCode.METHOD_NOT_ALLOWED: "The requested method is not supported for this resource.",
    ErrorCode.NOT_FOUND: "The requested resource was not found.",
    ErrorCode.RATE_LIMITED: "Too many requests were received. Try again later.",
    ErrorCode.REPOSITORY_UNAVAILABLE: "The service is temporarily unavailable.",
    ErrorCode.SECRET_UNAVAILABLE: "The requested service component is temporarily unavailable.",
    ErrorCode.VALIDATION_FAILED: "The request could not be validated.",
}


class PublicApiException(Exception):  # noqa: N818 - FastAPI names this typed exception explicitly.
    """A typed public failure that is rendered only by the shared exception mapper."""

    def __init__(
        self,
        *,
        status_code: int,
        error: PublicError,
        headers: Mapping[str, str] | None = None,
    ) -> None:
        super().__init__(error.code)
        self.status_code = status_code
        self.error = error
        self.headers = headers


def require_value[T](result: Result[T, ErrorDetail]) -> T:
    """Return a service value or raise a typed, redaction-safe public API error."""
    if result.is_success and result.value is not None:
        return result.value
    error = result.error
    if error is None:
        error = ErrorDetail(
            ErrorCode.INTERNAL_ERROR,
            "A control-plane operation failed without an error detail.",
            CorrelationId("unavailable"),
        )
    if error.code in {ErrorCode.AUTHORIZATION_DENIED, ErrorCode.NOT_FOUND}:
        error = ErrorDetail(
            ErrorCode.AUTHORIZATION_DENIED,
            "Protected resource access is not permitted.",
            error.correlation_id,
        )
    raise PublicApiException(
        status_code=_status_for(error.code),
        error=public_error_from_detail(error),
    )


def public_error_from_detail(error: ErrorDetail) -> PublicError:
    """Translate a typed domain error without exposing its internal message or payload."""
    return PublicError(
        code=error.code.value,
        message=_PUBLIC_MESSAGES[error.code],
        correlation_id=str(error.correlation_id),
        retryable=error.retryable,
        fields=[
            ValidationIssueResponse(field=field.name, reason=field.reason) for field in error.fields
        ],
    )


def public_success_response(
    data: object,
    correlation_id: str | CorrelationId,
    *,
    status_code: int = status.HTTP_200_OK,
    headers: Mapping[str, str] | None = None,
) -> JSONResponse:
    """Serialize a response body in the stable public success envelope."""
    safe_data = jsonable_encoder(
        redact_value(jsonable_encoder(data), surface=RedactionSurface.PUBLIC_RESPONSE)
    )
    envelope = PublicResponse[object](
        data=safe_data,
        meta=PublicResponseMeta(correlation_id=str(correlation_id)),
    )
    response = JSONResponse(
        status_code=status_code,
        content=envelope.model_dump(mode="json"),
        headers=headers,
    )
    response.headers[PUBLIC_ENVELOPE_HEADER] = "1"
    return response


def public_empty_response(
    *, status_code: int = status.HTTP_204_NO_CONTENT, headers: Mapping[str, str] | None = None
) -> Response:
    """Return a successful status that intentionally has no response body."""
    return Response(status_code=status_code, headers=headers)


def public_error_response(
    error: PublicError,
    *,
    status_code: int,
    headers: Mapping[str, str] | None = None,
) -> JSONResponse:
    """Serialize a typed public error in the stable error envelope."""
    safe_content = jsonable_encoder(
        redact_value(
            PublicErrorResponse(error=error).model_dump(mode="json"),
            surface=RedactionSurface.ERROR_RESPONSE,
        )
    )
    response = JSONResponse(
        status_code=status_code,
        content=safe_content,
        headers=headers,
    )
    response.headers[PUBLIC_ENVELOPE_HEADER] = "1"
    return response


def install_public_api_exception_handlers(application: FastAPI) -> None:
    """Install one safe exception mapper for every documented versioned route."""
    application.add_exception_handler(PublicApiException, _handle_public_api_exception)
    application.add_exception_handler(RequestValidationError, _handle_validation_error)
    application.add_exception_handler(StarletteHTTPException, _handle_http_exception)
    application.add_exception_handler(Exception, _handle_unexpected_exception)


async def _handle_public_api_exception(
    request: Request, exception: Exception
) -> Response:
    assert isinstance(exception, PublicApiException)
    request.state.request_correlation_id = CorrelationId(exception.error.correlation_id)
    return public_error_response(
        exception.error,
        status_code=exception.status_code,
        headers=exception.headers,
    )


async def _handle_validation_error(request: Request, exception: Exception) -> Response:
    assert isinstance(exception, RequestValidationError)
    return public_error_response(
        _validation_error(exception.errors(), _request_correlation_id(request)),
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )


async def _handle_http_exception(request: Request, exception: Exception) -> Response:
    assert isinstance(exception, StarletteHTTPException)
    code = _http_error_code(exception.status_code)
    headers: Mapping[str, str] | None = None
    if code is ErrorCode.RATE_LIMITED and exception.headers is not None:
        retry_after = exception.headers.get("Retry-After")
        if retry_after is not None:
            headers = {"Retry-After": retry_after}
    return public_error_response(
        _public_error(
            code,
            _request_correlation_id(request),
            retryable=code is ErrorCode.RATE_LIMITED,
        ),
        status_code=exception.status_code,
        headers=headers,
    )


async def _handle_unexpected_exception(request: Request, exception: Exception) -> Response:
    return public_error_response(
        _public_error(ErrorCode.INTERNAL_ERROR, _request_correlation_id(request), retryable=True),
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def _validation_error(
    errors: Sequence[Mapping[str, object]], correlation_id: CorrelationId
) -> PublicError:
    """Produce field paths without echoing rejected values or validator internals."""
    fields: list[ValidationIssueResponse] = []
    for error in errors:
        location = error.get("loc", ())
        if not isinstance(location, tuple | list):
            continue
        parts = [str(part) for part in location if part != "body"]
        fields.append(
            ValidationIssueResponse(
                field=".".join(parts) if parts else "request",
                reason="Invalid value.",
            )
        )
    return _public_error(ErrorCode.VALIDATION_FAILED, correlation_id, fields=fields)


def _public_error(
    code: ErrorCode,
    correlation_id: CorrelationId,
    *,
    retryable: bool = False,
    fields: list[ValidationIssueResponse] | None = None,
) -> PublicError:
    return PublicError(
        code=code.value,
        message=_PUBLIC_MESSAGES[code],
        correlation_id=str(correlation_id),
        retryable=retryable,
        fields=fields or [],
    )


def _request_correlation_id(request: Request) -> CorrelationId:
    context = getattr(request.state, "authenticated_context", None)
    value = getattr(context, "correlation_id", None)
    if isinstance(value, str) and value.strip():
        return CorrelationId(value)
    value = getattr(request.state, "request_correlation_id", None)
    if isinstance(value, str) and value.strip():
        return CorrelationId(value)
    correlation_id = new_correlation_id()
    request.state.request_correlation_id = correlation_id
    return correlation_id


def _http_error_code(status_code: int) -> ErrorCode:
    if status_code == status.HTTP_401_UNAUTHORIZED:
        return ErrorCode.AUTHENTICATION_REQUIRED
    if status_code == status.HTTP_403_FORBIDDEN:
        return ErrorCode.AUTHORIZATION_DENIED
    if status_code == status.HTTP_404_NOT_FOUND:
        return ErrorCode.NOT_FOUND
    if status_code == status.HTTP_405_METHOD_NOT_ALLOWED:
        return ErrorCode.METHOD_NOT_ALLOWED
    if status_code == status.HTTP_409_CONFLICT:
        return ErrorCode.CONFLICT
    if status_code == status.HTTP_429_TOO_MANY_REQUESTS:
        return ErrorCode.RATE_LIMITED
    if status_code >= status.HTTP_500_INTERNAL_SERVER_ERROR:
        return ErrorCode.INTERNAL_ERROR
    return ErrorCode.VALIDATION_FAILED


def _status_for(code: ErrorCode) -> int:
    """Map stable typed errors to their public HTTP status codes."""
    if code is ErrorCode.AUTHENTICATION_REQUIRED:
        return status.HTTP_401_UNAUTHORIZED
    if code is ErrorCode.AUTHORIZATION_DENIED:
        return status.HTTP_403_FORBIDDEN
    if code is ErrorCode.NOT_FOUND:
        return status.HTTP_404_NOT_FOUND
    if code is ErrorCode.METHOD_NOT_ALLOWED:
        return status.HTTP_405_METHOD_NOT_ALLOWED
    if code in {ErrorCode.CONFLICT, ErrorCode.INVALID_TRANSITION}:
        return status.HTTP_409_CONFLICT
    if code is ErrorCode.RATE_LIMITED:
        return status.HTTP_429_TOO_MANY_REQUESTS
    if code in {
        ErrorCode.AUDIT_UNAVAILABLE,
        ErrorCode.HEALTH_UNAVAILABLE,
        ErrorCode.REPOSITORY_UNAVAILABLE,
        ErrorCode.SECRET_UNAVAILABLE,
    }:
        return status.HTTP_503_SERVICE_UNAVAILABLE
    if code is ErrorCode.INTERNAL_ERROR:
        return status.HTTP_500_INTERNAL_SERVER_ERROR
    return status.HTTP_422_UNPROCESSABLE_ENTITY
