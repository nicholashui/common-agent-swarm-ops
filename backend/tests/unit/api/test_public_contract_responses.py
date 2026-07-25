"""Deterministic unit tests for the shared v1 public response contract."""

from __future__ import annotations

import json

import pytest
from fastapi import status

from app.api.v1.errors import (
    PUBLIC_ENVELOPE_HEADER,
    _validation_error,
    public_empty_response,
    public_error_from_detail,
    public_error_response,
    public_success_response,
)
from app.models.contracts import ErrorCode, ErrorDetail
from app.models.identifiers import CorrelationId

ERROR_CASES: tuple[tuple[ErrorCode, int, bool], ...] = (
    (ErrorCode.AUTHENTICATION_REQUIRED, status.HTTP_401_UNAUTHORIZED, False),
    (ErrorCode.AUTHORIZATION_DENIED, status.HTTP_403_FORBIDDEN, False),
    (ErrorCode.NOT_FOUND, status.HTTP_404_NOT_FOUND, False),
    (ErrorCode.METHOD_NOT_ALLOWED, status.HTTP_405_METHOD_NOT_ALLOWED, False),
    (ErrorCode.CONFLICT, status.HTTP_409_CONFLICT, False),
    (ErrorCode.VALIDATION_FAILED, status.HTTP_422_UNPROCESSABLE_ENTITY, False),
    (ErrorCode.RATE_LIMITED, status.HTTP_429_TOO_MANY_REQUESTS, True),
    (ErrorCode.INTERNAL_ERROR, status.HTTP_500_INTERNAL_SERVER_ERROR, True),
    (ErrorCode.REPOSITORY_UNAVAILABLE, status.HTTP_503_SERVICE_UNAVAILABLE, True),
)


def test_success_response_preserves_status_and_propagates_correlation_id() -> None:
    """Successful body responses use the documented envelope for 200 and 201 outcomes."""
    for status_code in (status.HTTP_200_OK, status.HTTP_201_CREATED):
        response = public_success_response(
            {"resource_id": "resource-1"},
            CorrelationId("correlation-success"),
            status_code=status_code,
        )

        assert response.status_code == status_code
        assert json.loads(bytes(response.body)) == {
            "data": {"resource_id": "resource-1"},
            "meta": {"correlation_id": "correlation-success"},
        }
        assert response.headers[PUBLIC_ENVELOPE_HEADER] == "1"


@pytest.mark.parametrize(("code", "status_code", "retryable"), ERROR_CASES)
def test_error_response_serializes_one_safe_envelope_for_each_documented_status(
    code: ErrorCode, status_code: int, retryable: bool
) -> None:
    """Each documented error status returns stable code, safe message, and correlation metadata."""
    error = public_error_from_detail(
        ErrorDetail(
            code=code,
            message="internal secret: never expose this diagnostic",
            correlation_id=CorrelationId("correlation-error"),
            retryable=retryable,
        )
    )
    response = public_error_response(error, status_code=status_code)
    envelope = json.loads(bytes(response.body))

    assert response.status_code == status_code
    assert envelope["error"]["code"] == code.value
    assert envelope["error"]["correlation_id"] == "correlation-error"
    assert envelope["error"]["retryable"] is retryable
    assert "internal secret" not in envelope["error"]["message"]
    assert response.headers[PUBLIC_ENVELOPE_HEADER] == "1"


def test_validation_and_conflict_responses_expose_only_safe_details() -> None:
    """Invalid input and optimistic conflicts never echo validator or service diagnostics."""
    validation = _validation_error(
        ({"loc": ("body", "expected_revision"), "input": "secret-value"},),
        CorrelationId("correlation-validation"),
    )
    conflict = public_error_from_detail(
        ErrorDetail(
            code=ErrorCode.CONFLICT,
            message="revision secret-value conflicted with resource 123",
            correlation_id=CorrelationId("correlation-conflict"),
        )
    )

    validation_body = json.loads(
        bytes(
            public_error_response(
                validation, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
            ).body
        )
    )
    conflict_body = json.loads(
        bytes(public_error_response(conflict, status_code=status.HTTP_409_CONFLICT).body)
    )

    assert validation_body == {
        "error": {
            "code": "validation_failed",
            "message": "The request could not be validated.",
            "correlation_id": "correlation-validation",
            "retryable": False,
            "fields": [{"field": "expected_revision", "reason": "Invalid value."}],
        }
    }
    assert conflict_body["error"]["message"] == (
        "The requested change conflicts with the current resource state."
    )
    assert "secret-value" not in json.dumps(conflict_body)


def test_empty_success_response_keeps_status_and_has_no_body() -> None:
    """An intentionally empty success response does not receive the body envelope."""
    response = public_empty_response(
        status_code=status.HTTP_204_NO_CONTENT, headers={"X-Request-Mode": "delete"}
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.body == b""
    assert response.headers["X-Request-Mode"] == "delete"
    assert PUBLIC_ENVELOPE_HEADER not in response.headers
