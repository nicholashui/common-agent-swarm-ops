"""Typed HTTP error translation shared by versioned resource routes."""

from __future__ import annotations

from fastapi import HTTPException, status

from app.models.contracts import ErrorCode, ErrorDetail, Result


def require_value[T](result: Result[T, ErrorDetail]) -> T:
    """Return a successful service value or raise a safe mapped HTTP error."""
    if result.is_success and result.value is not None:
        return result.value
    error = result.error
    if error is None:
        raise RuntimeError("A failed control-plane result did not provide an error.")
    raise HTTPException(status_code=_status_for(error.code), detail=_detail(error))


def _status_for(code: ErrorCode) -> int:
    """Map stable domain error codes to public HTTP status codes."""
    if code is ErrorCode.NOT_FOUND:
        return status.HTTP_404_NOT_FOUND
    if code is ErrorCode.AUTHORIZATION_DENIED:
        return status.HTTP_403_FORBIDDEN
    if code in {ErrorCode.CONFLICT, ErrorCode.INVALID_TRANSITION}:
        return status.HTTP_409_CONFLICT
    if code in {ErrorCode.REPOSITORY_UNAVAILABLE, ErrorCode.AUDIT_UNAVAILABLE}:
        return status.HTTP_503_SERVICE_UNAVAILABLE
    return status.HTTP_422_UNPROCESSABLE_ENTITY


def _detail(error: ErrorDetail) -> dict[str, object]:
    """Serialize only the stable, redaction-safe part of a domain error."""
    return {
        "code": error.code,
        "message": error.message,
        "correlation_id": error.correlation_id,
        "retryable": error.retryable,
        "fields": [{"field": field.name, "reason": field.reason} for field in error.fields],
    }
