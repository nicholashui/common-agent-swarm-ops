"""Immutable common-contract publication, draft editing, and migration orchestration."""

from __future__ import annotations

from collections.abc import Callable

from app.models.contracts import ErrorCode, ErrorDetail, Result
from app.models.control_plane import (
    AgentVersionId,
    CommonAgentVersion,
    CommonContractKind,
    CommonPatternVersion,
    CommonPatternVersionId,
    ContractStatus,
    VulnerabilityMigration,
)
from app.models.identifiers import CorrelationId, OrganizationId
from app.repositories.control_plane import ControlPlaneUnitOfWork


class RegistryService:
    """Manage organization-scoped immutable contract versions and mutable drafts."""

    def __init__(self, unit_of_work_factory: Callable[[], ControlPlaneUnitOfWork]) -> None:
        self._unit_of_work_factory = unit_of_work_factory

    def publish_agent(
        self, organization_id: OrganizationId, record: CommonAgentVersion
    ) -> Result[CommonAgentVersion, ErrorDetail]:
        """Append a complete immutable published agent contract."""
        mismatch = self._organization_mismatch(
            organization_id,
            record.metadata.organization_id,
            record.metadata.correlation_id,
        )
        if mismatch is not None:
            return Result.failure(mismatch)
        if record.status is not ContractStatus.PUBLISHED:
            return Result.failure(
                self._invalid_status(
                    "Published agent contracts must use published status.",
                    record.metadata.correlation_id,
                )
            )
        with self._unit_of_work_factory() as unit_of_work:
            return unit_of_work.common_contracts.append_agent_version(record)

    def publish_pattern(
        self, organization_id: OrganizationId, record: CommonPatternVersion
    ) -> Result[CommonPatternVersion, ErrorDetail]:
        """Append a complete immutable published pattern contract."""
        mismatch = self._organization_mismatch(
            organization_id,
            record.metadata.organization_id,
            record.metadata.correlation_id,
        )
        if mismatch is not None:
            return Result.failure(mismatch)
        if record.status is not ContractStatus.PUBLISHED:
            return Result.failure(
                self._invalid_status(
                    "Published pattern contracts must use published status.",
                    record.metadata.correlation_id,
                )
            )
        with self._unit_of_work_factory() as unit_of_work:
            return unit_of_work.common_contracts.append_pattern_version(record)

    def create_agent_draft(
        self,
        organization_id: OrganizationId,
        source_version_id: AgentVersionId,
        draft: CommonAgentVersion,
    ) -> Result[CommonAgentVersion, ErrorDetail]:
        """Fork a published agent into a separately identified, mutable draft."""
        mismatch = self._organization_mismatch(
            organization_id, draft.metadata.organization_id, draft.metadata.correlation_id
        )
        if mismatch is not None:
            return Result.failure(mismatch)
        if draft.status is not ContractStatus.DRAFT:
            return Result.failure(
                self._invalid_status(
                    "Agent forks must be created as drafts.",
                    draft.metadata.correlation_id,
                )
            )
        if draft.agent_version_id == source_version_id:
            return Result.failure(
                self._conflict(
                    "A draft must have a distinct agent version identifier.",
                    draft.metadata.correlation_id,
                )
            )
        with self._unit_of_work_factory() as unit_of_work:
            source = unit_of_work.common_contracts.get_agent_version(
                organization_id, source_version_id
            )
            if not source.is_success:
                return Result.failure(self._repository_error(source))
            source_record = source.value
            assert source_record is not None
            if source_record.status is not ContractStatus.PUBLISHED:
                return Result.failure(
                    self._invalid_status(
                        "Only published agent contracts can be forked.",
                        draft.metadata.correlation_id,
                    )
                )
            return unit_of_work.common_contracts.append_agent_version(draft)

    def create_pattern_draft(
        self,
        organization_id: OrganizationId,
        source_version_id: CommonPatternVersionId,
        draft: CommonPatternVersion,
    ) -> Result[CommonPatternVersion, ErrorDetail]:
        """Fork a published pattern into a separately identified, mutable draft."""
        mismatch = self._organization_mismatch(
            organization_id, draft.metadata.organization_id, draft.metadata.correlation_id
        )
        if mismatch is not None:
            return Result.failure(mismatch)
        if draft.status is not ContractStatus.DRAFT:
            return Result.failure(
                self._invalid_status(
                    "Pattern forks must be created as drafts.",
                    draft.metadata.correlation_id,
                )
            )
        if draft.pattern_version_id == source_version_id:
            return Result.failure(
                self._conflict(
                    "A draft must have a distinct pattern version identifier.",
                    draft.metadata.correlation_id,
                )
            )
        with self._unit_of_work_factory() as unit_of_work:
            source = unit_of_work.common_contracts.get_pattern_version(
                organization_id, source_version_id
            )
            if not source.is_success:
                return Result.failure(self._repository_error(source))
            source_record = source.value
            assert source_record is not None
            if source_record.status is not ContractStatus.PUBLISHED:
                return Result.failure(
                    self._invalid_status(
                        "Only published pattern contracts can be forked.",
                        draft.metadata.correlation_id,
                    )
                )
            return unit_of_work.common_contracts.append_pattern_version(draft)

    def update_agent_draft(
        self, organization_id: OrganizationId, draft: CommonAgentVersion
    ) -> Result[CommonAgentVersion, ErrorDetail]:
        """Replace a draft snapshot while refusing any published-version mutation."""
        mismatch = self._organization_mismatch(
            organization_id, draft.metadata.organization_id, draft.metadata.correlation_id
        )
        if mismatch is not None:
            return Result.failure(mismatch)
        if draft.status is not ContractStatus.DRAFT:
            return Result.failure(
                self._invalid_status(
                    "Only draft agent contracts can be updated.",
                    draft.metadata.correlation_id,
                )
            )
        with self._unit_of_work_factory() as unit_of_work:
            return unit_of_work.common_contracts.replace_agent_draft(draft)

    def update_pattern_draft(
        self, organization_id: OrganizationId, draft: CommonPatternVersion
    ) -> Result[CommonPatternVersion, ErrorDetail]:
        """Replace a draft snapshot while refusing any published-version mutation."""
        mismatch = self._organization_mismatch(
            organization_id, draft.metadata.organization_id, draft.metadata.correlation_id
        )
        if mismatch is not None:
            return Result.failure(mismatch)
        if draft.status is not ContractStatus.DRAFT:
            return Result.failure(
                self._invalid_status(
                    "Only draft pattern contracts can be updated.",
                    draft.metadata.correlation_id,
                )
            )
        with self._unit_of_work_factory() as unit_of_work:
            return unit_of_work.common_contracts.replace_pattern_draft(draft)

    def record_agent_vulnerability(
        self,
        organization_id: OrganizationId,
        source_version_id: AgentVersionId,
        patched_version: CommonAgentVersion,
        migration: VulnerabilityMigration,
    ) -> Result[VulnerabilityMigration, ErrorDetail]:
        """Create an immutable migration target for a vulnerable published agent."""
        invalid = self._migration_issue(
            organization_id,
            CommonContractKind.AGENT,
            str(source_version_id),
            str(patched_version.agent_version_id),
            patched_version.status,
            patched_version.metadata.organization_id,
            migration,
        )
        if invalid is not None:
            return Result.failure(invalid)
        with self._unit_of_work_factory() as unit_of_work:
            source = unit_of_work.common_contracts.get_agent_version(
                organization_id, source_version_id
            )
            if not source.is_success:
                return Result.failure(self._repository_error(source))
            if source.value is None or source.value.status is not ContractStatus.PUBLISHED:
                return Result.failure(
                    self._invalid_status(
                        "Vulnerability migration requires a published source agent.",
                        migration.metadata.correlation_id,
                    )
                )
            target = unit_of_work.common_contracts.append_agent_version(patched_version)
            if not target.is_success:
                return Result.failure(self._repository_error(target))
            recorded = unit_of_work.common_contracts.append_vulnerability_migration(migration)
            if not recorded.is_success:
                unit_of_work.rollback()
                return Result.failure(self._repository_error(recorded))
            return recorded

    def record_pattern_vulnerability(
        self,
        organization_id: OrganizationId,
        source_version_id: CommonPatternVersionId,
        patched_version: CommonPatternVersion,
        migration: VulnerabilityMigration,
    ) -> Result[VulnerabilityMigration, ErrorDetail]:
        """Create an immutable migration target for a vulnerable published pattern."""
        invalid = self._migration_issue(
            organization_id,
            CommonContractKind.PATTERN,
            str(source_version_id),
            str(patched_version.pattern_version_id),
            patched_version.status,
            patched_version.metadata.organization_id,
            migration,
        )
        if invalid is not None:
            return Result.failure(invalid)
        with self._unit_of_work_factory() as unit_of_work:
            source = unit_of_work.common_contracts.get_pattern_version(
                organization_id, source_version_id
            )
            if not source.is_success:
                return Result.failure(self._repository_error(source))
            if source.value is None or source.value.status is not ContractStatus.PUBLISHED:
                return Result.failure(
                    self._invalid_status(
                        "Vulnerability migration requires a published source pattern.",
                        migration.metadata.correlation_id,
                    )
                )
            target = unit_of_work.common_contracts.append_pattern_version(patched_version)
            if not target.is_success:
                return Result.failure(self._repository_error(target))
            recorded = unit_of_work.common_contracts.append_vulnerability_migration(migration)
            if not recorded.is_success:
                unit_of_work.rollback()
                return Result.failure(self._repository_error(recorded))
            return recorded

    @staticmethod
    def _migration_issue(
        organization_id: OrganizationId,
        contract_kind: CommonContractKind,
        source_version_id: str,
        target_version_id: str,
        target_status: ContractStatus,
        target_organization_id: OrganizationId,
        migration: VulnerabilityMigration,
    ) -> ErrorDetail | None:
        mismatch = RegistryService._organization_mismatch(
            organization_id, target_organization_id, migration.metadata.correlation_id
        )
        if mismatch is not None:
            return mismatch
        migration_mismatch = RegistryService._organization_mismatch(
            organization_id, migration.metadata.organization_id, migration.metadata.correlation_id
        )
        if migration_mismatch is not None:
            return migration_mismatch
        if target_status is not ContractStatus.PUBLISHED:
            return RegistryService._invalid_status(
                "A vulnerability migration target must be a published patched version.",
                migration.metadata.correlation_id,
            )
        if (
            migration.contract_kind is not contract_kind
            or migration.source_version_id != source_version_id
            or migration.target_version_id != target_version_id
        ):
            return RegistryService._conflict(
                "Vulnerability migration references must match the source and patched version.",
                migration.metadata.correlation_id,
            )
        return None

    @staticmethod
    def _organization_mismatch(
        organization_id: OrganizationId,
        record_organization_id: OrganizationId,
        correlation_id: CorrelationId,
    ) -> ErrorDetail | None:
        if organization_id == record_organization_id:
            return None
        return ErrorDetail(
            ErrorCode.AUTHORIZATION_DENIED,
            "The common contract is unavailable.",
            correlation_id,
        )

    @staticmethod
    def _invalid_status(message: str, correlation_id: CorrelationId) -> ErrorDetail:
        return ErrorDetail(ErrorCode.INVALID_TRANSITION, message, correlation_id)

    @staticmethod
    def _conflict(message: str, correlation_id: CorrelationId) -> ErrorDetail:
        return ErrorDetail(ErrorCode.CONFLICT, message, correlation_id)

    @staticmethod
    def _repository_error(result: Result[object, ErrorDetail]) -> ErrorDetail:
        error = result.error
        assert error is not None
        return error
