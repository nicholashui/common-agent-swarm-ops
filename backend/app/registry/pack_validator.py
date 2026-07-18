"""Root-confined, fail-closed validation and registration of domain-pack manifests."""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from app.core.boundary import WorkspaceBoundary
from app.core.errors import BoundaryErrorCode, BoundaryViolationError
from app.models.common import SCHEMA_VERSION, RecordMetadata, utc_now
from app.models.contracts import RepositoryError, Result
from app.models.identifiers import CorrelationId, OrganizationId, new_correlation_id, new_record_id
from app.repositories.pack_repository import (
    AgentLifecycleStatus,
    DomainPackRecord,
    InMemoryPackRepository,
    PackAgentRecord,
    PackRegistrationStatus,
    ValidationIssue,
    ValidationReport,
)

_IDENTIFIER_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$"
)
_PRODUCTION_ACTIVATION_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "production_activation_requested",
        "production_activation",
        "request_production_activation",
        "activate_in_production",
    }
)


class DuplicateJsonKeyError(ValueError):
    """Raised when a JSON object repeats a key that parsing would otherwise hide."""


@dataclass(frozen=True, slots=True)
class ManifestSourceError(Exception):
    """A redaction-safe source failure that is persisted as an inactive outcome."""

    code: str
    message: str


class DomainPackValidator:
    """Validate inline or business-root manifests and persist one complete outcome."""

    def __init__(
        self,
        repository: InMemoryPackRepository,
        boundary: WorkspaceBoundary | None = None,
    ) -> None:
        self._repository = repository
        self._boundary = boundary or WorkspaceBoundary()
        self._business_root = (self._boundary.target_workspace / "business").resolve()

    def validate(self, manifest: object) -> ValidationReport:
        """Return a full report without reading files or changing repository state."""
        if not isinstance(manifest, Mapping):
            return ValidationReport(
                is_valid=False,
                canonical_pack_id=None,
                agents=(),
                issues=(
                    ValidationIssue("manifest", "invalid_type", "Manifest must be a JSON object."),
                ),
            )

        issues: list[ValidationIssue] = []
        pack_id = self._canonical_identifier(manifest.get("pack_id"), "pack_id", issues)
        agent_records = self._validate_agents(manifest.get("agents"), issues)
        self._validate_production_activation(manifest, "manifest", issues)
        return ValidationReport(
            is_valid=not issues,
            canonical_pack_id=pack_id,
            agents=tuple(agent_records),
            issues=tuple(issues),
        )

    def register_inline(
        self,
        manifest: object,
        *,
        organization_id: OrganizationId | None = None,
        correlation_id: CorrelationId | None = None,
    ) -> Result[DomainPackRecord, RepositoryError]:
        """Validate and atomically persist an inline manifest as a non-active outcome."""
        effective_organization_id = organization_id or OrganizationId("host")
        return self._record_report(
            self.validate(manifest),
            manifest,
            organization_id=effective_organization_id,
            correlation_id=correlation_id or new_correlation_id(),
        )

    def register_from_path(
        self,
        manifest_path: Path | str,
        *,
        organization_id: OrganizationId | None = None,
        correlation_id: CorrelationId | None = None,
    ) -> Result[DomainPackRecord, RepositoryError]:
        """Load only a target-business JSON manifest, then persist its complete outcome."""
        effective_organization_id = organization_id or OrganizationId("host")
        effective_correlation_id = correlation_id or new_correlation_id()
        try:
            manifest = self._load_manifest(manifest_path)
        except ManifestSourceError as error:
            report = ValidationReport(
                is_valid=False,
                canonical_pack_id=None,
                agents=(),
                issues=(ValidationIssue("manifest", error.code, error.message),),
            )
            return self._record_report(
                report,
                {"source_error": error.code},
                organization_id=effective_organization_id,
                correlation_id=effective_correlation_id,
            )
        return self._record_report(
            self.validate(manifest),
            manifest,
            organization_id=effective_organization_id,
            correlation_id=effective_correlation_id,
        )

    def _validate_agents(
        self, raw_agents: object, issues: list[ValidationIssue]
    ) -> list[PackAgentRecord]:
        if not isinstance(raw_agents, list):
            issues.append(
                ValidationIssue("agents", "invalid_type", "Agents must be a JSON array.")
            )
            return []
        if not 1 <= len(raw_agents) <= 100:
            issues.append(
                ValidationIssue(
                    "agents",
                    "invalid_count",
                    "A domain pack must contain from 1 through 100 agents.",
                )
            )

        agent_records: list[PackAgentRecord] = []
        canonical_agent_ids: set[str] = set()
        for index, raw_agent in enumerate(raw_agents):
            field = f"agents[{index}]"
            if not isinstance(raw_agent, Mapping):
                issues.append(
                    ValidationIssue(field, "invalid_type", "Each agent must be a JSON object.")
                )
                agent_records.append(PackAgentRecord(None, None, None))
                continue

            agent_id = self._canonical_identifier(
                raw_agent.get("agent_id"), f"{field}.agent_id", issues
            )
            raw_status = raw_agent.get("status")
            status = self._agent_status(raw_status, f"{field}.status", issues)
            self._validate_agent_options(raw_agent, field, issues)
            self._validate_production_activation(raw_agent, field, issues)
            if agent_id is not None:
                if agent_id in canonical_agent_ids:
                    issues.append(
                        ValidationIssue(
                            f"{field}.agent_id",
                            "duplicate_canonical_agent_id",
                            "Agent identifiers must be unique after canonicalization.",
                        )
                    )
                canonical_agent_ids.add(agent_id)
            agent_records.append(
                PackAgentRecord(
                    agent_id=agent_id,
                    supplied_status=raw_status if isinstance(raw_status, str) else None,
                    status=status,
                )
            )
        return agent_records

    @staticmethod
    def _agent_status(
        value: object, field: str, issues: list[ValidationIssue]
    ) -> AgentLifecycleStatus | None:
        if not isinstance(value, str):
            issues.append(ValidationIssue(field, "invalid_type", "Agent status must be a string."))
            return None
        try:
            return AgentLifecycleStatus(value)
        except ValueError:
            issues.append(
                ValidationIssue(
                    field,
                    "invalid_status",
                    "Agent status must be draft or registered.",
                )
            )
            return None

    @staticmethod
    def _validate_agent_options(
        agent: Mapping[object, object], field: str, issues: list[ValidationIssue]
    ) -> None:
        if "requires_learning" in agent and not isinstance(agent["requires_learning"], bool):
            issues.append(
                ValidationIssue(
                    f"{field}.requires_learning",
                    "invalid_type",
                    "requires_learning must be a boolean when supplied.",
                )
            )
        if "allowed_tools" not in agent:
            return
        allowed_tools = agent["allowed_tools"]
        if (
            not isinstance(allowed_tools, list)
            or any(not isinstance(tool, str) or not tool.strip() for tool in allowed_tools)
            or len({tool for tool in allowed_tools if isinstance(tool, str)}) != len(allowed_tools)
        ):
            issues.append(
                ValidationIssue(
                    f"{field}.allowed_tools",
                    "invalid_tools",
                    "allowed_tools must be a unique array of non-empty strings when supplied.",
                )
            )

    @staticmethod
    def _validate_production_activation(
        values: Mapping[object, object], field: str, issues: list[ValidationIssue]
    ) -> None:
        for activation_field in _PRODUCTION_ACTIVATION_FIELDS:
            if activation_field not in values:
                continue
            requested = values[activation_field]
            if not isinstance(requested, bool):
                issues.append(
                    ValidationIssue(
                        f"{field}.{activation_field}",
                        "invalid_type",
                        "Production activation requests must be boolean values.",
                    )
                )
            elif requested:
                issues.append(
                    ValidationIssue(
                        f"{field}.{activation_field}",
                        "production_activation_requested",
                        "Domain-pack registration cannot request production activation.",
                    )
                )

    @staticmethod
    def _canonical_identifier(
        value: object, field: str, issues: list[ValidationIssue]
    ) -> str | None:
        if not isinstance(value, str):
            issues.append(ValidationIssue(field, "invalid_type", "Identifier must be a string."))
            return None
        canonical = unicodedata.normalize("NFKC", value).strip().casefold()
        if len(canonical) > 100 or not _IDENTIFIER_PATTERN.fullmatch(canonical):
            issues.append(
                ValidationIssue(
                    field,
                    "invalid_identifier",
                    (
                        "Identifier must normalize to lowercase letters, digits, dots, "
                        "underscores, or hyphens."
                    ),
                )
            )
            return None
        return canonical

    def _load_manifest(self, manifest_path: Path | str) -> object:
        authorized_path = self._boundary.authorize_access(manifest_path)
        try:
            authorized_path.relative_to(self._business_root)
        except ValueError as error:
            raise BoundaryViolationError(
                BoundaryErrorCode.OUTSIDE_TARGET_WORKSPACE,
                "read",
                "Domain-pack manifests must be inside the target business directory.",
            ) from error
        if authorized_path.suffix.lower() != ".json":
            raise ManifestSourceError(
                "invalid_extension", "Manifest files must use the .json extension."
            )
        try:
            if authorized_path.stat().st_size > 1_000_000:
                raise ManifestSourceError(
                    "manifest_too_large", "Manifest files must not exceed 1 MB."
                )
            content = authorized_path.read_text(encoding="utf-8")
        except ManifestSourceError:
            raise
        except (OSError, UnicodeError) as error:
            raise ManifestSourceError(
                "unreadable_manifest", "Manifest file cannot be read."
            ) from error
        try:
            return json.loads(content, object_pairs_hook=self._object_without_duplicate_keys)
        except DuplicateJsonKeyError as error:
            raise ManifestSourceError(
                "duplicate_json_key", "Manifest JSON cannot repeat object keys."
            ) from error
        except json.JSONDecodeError as error:
            raise ManifestSourceError(
                "invalid_json", "Manifest file must contain valid JSON."
            ) from error

    def _record_report(
        self,
        report: ValidationReport,
        manifest: object,
        *,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
    ) -> Result[DomainPackRecord, RepositoryError]:
        now = utc_now()
        status = (
            PackRegistrationStatus.REGISTERED
            if report.is_valid
            else PackRegistrationStatus.INACTIVE
        )
        agents = (
            report.agents
            if report.is_valid
            else tuple(agent.deny_production_activation() for agent in report.agents)
        )
        record = DomainPackRecord(
            metadata=RecordMetadata(
                record_id=new_record_id(),
                organization_id=organization_id,
                correlation_id=correlation_id,
                schema_version=SCHEMA_VERSION,
                version=1,
                created_at=now,
                updated_at=now,
            ),
            pack_id=report.canonical_pack_id,
            manifest_digest=self._manifest_digest(manifest),
            status=status,
            agents=agents,
            validation_report=report,
        )
        return self._repository.record_outcome(record)

    @staticmethod
    def _object_without_duplicate_keys(
        pairs: list[tuple[str, object]],
    ) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                raise DuplicateJsonKeyError(key)
            result[key] = value
        return result

    @staticmethod
    def _manifest_digest(manifest: object) -> str:
        try:
            serialized = json.dumps(
                manifest,
                ensure_ascii=True,
                separators=(",", ":"),
                sort_keys=True,
                default=lambda value: f"<{type(value).__name__}>",
            )
        except (TypeError, ValueError):
            serialized = f"<unserializable:{type(manifest).__name__}>"
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
