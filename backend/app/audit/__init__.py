"""Append-only, fail-closed audit recording for Host governance."""

from app.audit.writer import AuditWriter, AuditWriteResult

__all__ = ["AuditWriteResult", "AuditWriter"]
