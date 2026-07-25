"""Test-only manifest coverage for deterministic adoption verification evidence."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Final

from app.evaluation.verification_suite import VerificationCheck, VerificationSuite
from app.evidence.release_evidence import (
    InMemoryReleaseEvidenceRepository,
    ReleaseEvidenceBundle,
    VerificationLayer,
)
from app.models.control_plane import VerificationCoverageStatus
from app.models.identifiers import (
    CorrelationId,
    DomainPackId,
    OrganizationId,
    is_uuid_identifier,
)

_NOW: Final[datetime] = datetime(2025, 1, 1, tzinfo=UTC)
_ORGANIZATION_ID: Final[OrganizationId] = OrganizationId("organization-manifest")
_CORRELATION_ID: Final[CorrelationId] = CorrelationId("correlation-manifest")
_PACK_ID: Final[DomainPackId] = DomainPackId("pack-manifest")
_FIXED_SEED: Final[str] = "adoption-redesign-seed"
_FIXTURE_DIGEST: Final[str] = "adoption-redesign-fixtures"
_PYTEST_COMMAND: Final[str] = (
    "python -m pytest --tb=short -q tests/evidence/test_adoption_verification_manifest.py"
)
_RUFF_COMMAND: Final[str] = (
    "python -m ruff check app/evaluation/verification_suite.py app/evidence/release_evidence.py "
    "tests/evidence/test_adoption_verification_manifest.py"
)
_MYPY_COMMAND: Final[str] = (
    "python -m mypy app/evaluation/verification_suite.py app/evidence/release_evidence.py "
    "tests/evidence/test_adoption_verification_manifest.py"
)
_PYTEST_DIGEST: Final[str] = (
    "sha256:e95a03a3549bddf3c9ec0fd2deae960c20e26941c9219fc86e0c17ca5ef9effe"
)
_RUFF_DIGEST: Final[str] = "sha256:edd4e0a93f7ecc3ce3941e186e2e224be816b33d2c0be707ccd91235862de078"
_MYPY_DIGEST: Final[str] = "sha256:7a750443ebe10958e8648234f8540c8a2eb2ba7d52788e3e5c255d0471e68d54"
_LESSON_CONTENT = "Lesson content must never enter a release evidence manifest."


@dataclass(frozen=True, slots=True)
class _CommandObservation:
    """Raw test-run input; output is intentionally not copied into the manifest."""

    key: str
    check_name: str
    command: str
    exit_status: int
    artifact_digest: str
    raw_output: str


@dataclass(frozen=True, slots=True)
class _ManifestCommand:
    """Redacted command evidence retained by the test-only manifest generator."""

    command: str
    exit_status: int
    artifact_digest: str
    verification_id: str
    failure_reference: str | None


@dataclass(frozen=True, slots=True)
class _VerificationEvidenceManifest:
    """Reference-only verification projection used by these tests."""

    verification_run_id: str
    fixed_seed: str
    fixture_digest: str
    commands: tuple[_ManifestCommand, ...]
    integration_coverage_evidence_ids: tuple[str, ...]
    failure_references: tuple[str, ...]
    failure_persistence_errors: tuple[str, ...]


def _command_observations(*, failing_key: str | None = None) -> tuple[_CommandObservation, ...]:
    """Create deterministic local command observations without executing subprocesses."""
    definitions = (
        ("pytest", "command.pytest", _PYTEST_COMMAND, _PYTEST_DIGEST),
        ("ruff", "command.ruff", _RUFF_COMMAND, _RUFF_DIGEST),
        ("mypy", "command.mypy", _MYPY_COMMAND, _MYPY_DIGEST),
    )
    return tuple(
        _CommandObservation(
            key=key,
            check_name=check_name,
            command=command,
            exit_status=1 if key == failing_key else 0,
            artifact_digest=artifact_digest,
            raw_output=f"{command}: {key} output; {_LESSON_CONTENT}",
        )
        for key, check_name, command, artifact_digest in definitions
    )


def _verification_checks(
    observations: tuple[_CommandObservation, ...],
) -> tuple[VerificationCheck, ...]:
    """Translate command statuses into real VerificationSuite checks."""
    return tuple(
        VerificationCheck(
            name=observation.check_name,
            layer=VerificationLayer.PROPERTY,
            outcome=observation.exit_status == 0,
            evidence_reference=observation.artifact_digest,
        )
        for observation in observations
    )


def _run_suite(
    observations: tuple[_CommandObservation, ...],
    *,
    fail_failure_persistence: bool = False,
    record_failed_command_after_coverage: bool = False,
) -> tuple[ReleaseEvidenceBundle, InMemoryReleaseEvidenceRepository]:
    """Run the real suite against isolated in-memory evidence repositories."""
    evidence = InMemoryReleaseEvidenceRepository(
        fail_failure_persistence=fail_failure_persistence,
    )
    suite = VerificationSuite(evidence_repository=evidence, clock=lambda: _NOW)
    if record_failed_command_after_coverage:
        before_coverage = tuple(
            observation for observation in observations if observation.exit_status == 0
        )
        after_coverage = tuple(
            observation for observation in observations if observation.exit_status != 0
        )
    else:
        before_coverage = observations
        after_coverage = ()
    result = suite.run(
        _ORGANIZATION_ID,
        _CORRELATION_ID,
        pack_id=_PACK_ID,
        immutable_version="1.0.0",
        pack_contract_version="1.0.0",
        host_contract_version="1.0.0",
        alc_version="1.0.0",
        fixed_seed=_FIXED_SEED,
        fixture_digest=_FIXTURE_DIGEST,
        property_checks=_verification_checks(before_coverage),
        integration_checks=(("integration.coverage", True),),
        post_coverage_checks=_verification_checks(after_coverage),
        integration_coverage_complete=True,
    )
    assert result.is_success and result.value is not None
    return result.value, evidence


def _generate_manifest(
    bundle: ReleaseEvidenceBundle,
    observations: tuple[_CommandObservation, ...],
) -> _VerificationEvidenceManifest:
    """Generate a redacted manifest from persisted suite evidence only."""
    results_by_name = {record.check_name: record for record in bundle.check_results}
    commands: list[_ManifestCommand] = []
    for observation in observations:
        result = results_by_name.get(observation.check_name)
        if result is None:
            raise AssertionError(f"Missing verification result for {observation.check_name}.")
        commands.append(
            _ManifestCommand(
                command=observation.command,
                exit_status=observation.exit_status,
                artifact_digest=observation.artifact_digest,
                verification_id=str(result.evidence_id),
                failure_reference=result.failure_reference,
            )
        )
    return _VerificationEvidenceManifest(
        verification_run_id=str(bundle.verification_run.verification_run_id),
        fixed_seed=bundle.verification_run.fixed_seed,
        fixture_digest=bundle.verification_run.fixture_digest,
        commands=tuple(commands),
        integration_coverage_evidence_ids=bundle.verification_run.integration_evidence_references,
        failure_references=bundle.verification_run.failure_evidence_references,
        failure_persistence_errors=bundle.failure_persistence_errors,
    )


def test_manifest_records_exact_commands_statuses_seeds_digests_and_verification_ids() -> None:
    """Passing local checks retain exact reproducibility metadata and evidence IDs."""
    observations = _command_observations()
    bundle, evidence = _run_suite(observations)
    manifest = _generate_manifest(bundle, observations)

    assert tuple(command.command for command in manifest.commands) == (
        _PYTEST_COMMAND,
        _RUFF_COMMAND,
        _MYPY_COMMAND,
    )
    assert tuple(command.exit_status for command in manifest.commands) == (0, 0, 0)
    assert tuple(command.artifact_digest for command in manifest.commands) == (
        _PYTEST_DIGEST,
        _RUFF_DIGEST,
        _MYPY_DIGEST,
    )
    assert manifest.fixed_seed == _FIXED_SEED
    assert manifest.fixture_digest == _FIXTURE_DIGEST
    assert is_uuid_identifier(manifest.verification_run_id)
    assert all(is_uuid_identifier(command.verification_id) for command in manifest.commands)
    assert manifest.failure_references == ()
    assert manifest.failure_persistence_errors == ()
    assert bundle.coverage_status is VerificationCoverageStatus.COMPLETE
    assert manifest.integration_coverage_evidence_ids
    assert set(manifest.integration_coverage_evidence_ids) == {
        str(record.evidence_id)
        for record in evidence.check_results()
        if record.layer is VerificationLayer.INTEGRATION
    }
    assert all(record.fixed_seed == _FIXED_SEED for record in evidence.check_results())
    assert all(record.fixture_digest == _FIXTURE_DIGEST for record in evidence.check_results())


def test_manifest_records_late_command_failure_without_lesson_content_or_coverage_loss() -> None:
    """A failed command is redacted while independently persisted coverage remains inspectable."""
    observations = _command_observations(failing_key="mypy")
    bundle, evidence = _run_suite(
        observations,
        fail_failure_persistence=True,
        record_failed_command_after_coverage=True,
    )
    manifest = _generate_manifest(bundle, observations)

    failed_command = manifest.commands[-1]
    assert failed_command.command == _MYPY_COMMAND
    assert failed_command.exit_status == 1
    assert failed_command.failure_reference is not None
    assert manifest.failure_references == (failed_command.failure_reference,)
    assert manifest.failure_persistence_errors
    assert bundle.release_decision is not None
    assert bundle.release_decision.status.value == "failed"
    assert bundle.coverage_status is VerificationCoverageStatus.COMPLETE
    assert manifest.integration_coverage_evidence_ids == tuple(
        str(record.evidence_id)
        for record in evidence.check_results()
        if record.layer is VerificationLayer.INTEGRATION
    )
    assert _LESSON_CONTENT not in repr(manifest)
    assert all(_LESSON_CONTENT not in repr(record) for record in evidence.check_results())
    assert any(
        record.check_name == "integration.coverage" and record.passed
        for record in evidence.check_results()
    )
    assert any(
        record.check_name == "command.mypy" and record.failed for record in evidence.check_results()
    )


# Keep the test-only manifest generator independent from wall-clock state in focused runs.
def test_manifest_generation_uses_isolated_deterministic_clock() -> None:
    """Manifest evidence uses the injected fixed suite clock."""
    observations = _command_observations()
    bundle, _ = _run_suite(observations)

    assert all(record.recorded_at == _NOW for record in bundle.check_results)
    assert bundle.verification_run.metadata.created_at == _NOW
