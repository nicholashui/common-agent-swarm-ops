"""Property tests for target-confined process-artifact traceability."""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import pytest
from hypothesis import HealthCheck, given, settings, strategies as st

from app.core.boundary import WorkspaceBoundary
from app.process_intelligence.models import ProcessArtifactDraft, ProcessArtifactKind
from app.process_intelligence.repository import RootConfinedProcessArtifactRepository
from app.process_intelligence.service import ProcessIntelligenceService

# Feature: generic-swarm-business-os, Property 5: Process artifacts retain source traceability.
# **Validates: Requirements 3.1**

_TIMESTAMP = "2025-01-01T12:00:00+00:00"


@dataclass(frozen=True, slots=True)
class PermittedEventLogInput:
    """One bounded permitted source log set and its derived artifact drafts."""

    log_set_id: str
    record_ids: tuple[str, ...]
    drafts: tuple[ProcessArtifactDraft, ...]


type ProcessArtifactServiceFactory = Callable[
    [], tuple[ProcessIntelligenceService, RootConfinedProcessArtifactRepository, Path]
]


@pytest.fixture
def process_artifact_service_factory(tmp_path: Path) -> ProcessArtifactServiceFactory:
    """Create isolated target roots exclusively below pytest's temporary directory."""
    fixture_root = tmp_path / "target-workspace"
    fixture_root.mkdir()
    invocation_count = 0

    def create_service() -> tuple[
        ProcessIntelligenceService, RootConfinedProcessArtifactRepository, Path
    ]:
        nonlocal invocation_count
        invocation_count += 1
        target_workspace = fixture_root / f"case-{invocation_count}"
        target_workspace.mkdir()
        repository = RootConfinedProcessArtifactRepository(
            WorkspaceBoundary(target_workspace, reference_workspace=None)
        )
        return ProcessIntelligenceService(repository), repository, target_workspace

    return create_service


@st.composite
def _permitted_event_log_inputs(draw: st.DrawFn) -> PermittedEventLogInput:
    """Generate valid, bounded logs with non-empty in-log supporting references."""
    record_suffixes = draw(
        st.lists(st.integers(min_value=1, max_value=99), min_size=1, max_size=6, unique=True)
    )
    record_ids = tuple(f"event-{suffix}" for suffix in record_suffixes)
    artifact_kinds = draw(
        st.lists(
            st.sampled_from(tuple(ProcessArtifactKind)),
            min_size=1,
            max_size=4,
        )
    )
    drafts: list[ProcessArtifactDraft] = []
    for artifact_index, kind in enumerate(artifact_kinds):
        supporting_refs = tuple(
            draw(
                st.lists(
                    st.sampled_from(record_ids),
                    min_size=1,
                    max_size=len(record_ids),
                    unique=True,
                )
            )
        )
        drafts.append(
            ProcessArtifactDraft(
                kind=kind,
                supporting_record_refs=supporting_refs,
                output={
                    "artifact_index": artifact_index,
                    "supporting_record_count": len(supporting_refs),
                },
            )
        )
    return PermittedEventLogInput(
        log_set_id=f"ops-log-{draw(st.integers(min_value=1, max_value=9_999))}",
        record_ids=record_ids,
        drafts=tuple(drafts),
    )


def _raw_log_set(event_log: PermittedEventLogInput) -> dict[str, object]:
    """Render a valid source payload without introducing unbounded test input."""
    return {
        "permitted": True,
        "log_set_id": event_log.log_set_id,
        "records": [
            {
                "record_id": record_id,
                "case_id": f"case-{index}",
                "activity": f"activity-{index}",
                "occurred_at": _TIMESTAMP,
            }
            for index, record_id in enumerate(event_log.record_ids, start=1)
        ],
    }


@settings(
    max_examples=100,
    deadline=None,
    derandomize=True,
    suppress_health_check=(HealthCheck.function_scoped_fixture,),
)
@given(event_log=_permitted_event_log_inputs())
def test_permitted_process_artifacts_retain_source_traceability(
    process_artifact_service_factory: ProcessArtifactServiceFactory,
    event_log: PermittedEventLogInput,
) -> None:
    """Every derived artifact retains its permitted log set and source-record references."""
    service, repository, target_workspace = process_artifact_service_factory()

    result = service.ingest(_raw_log_set(event_log), event_log.drafts)

    assert result.is_success
    assert result.value is not None
    artifacts = result.value
    assert len(artifacts) == len(event_log.drafts)
    assert repository.artifact_root.is_relative_to(target_workspace)
    persisted_paths = tuple(repository.artifact_root.glob("*.json"))
    assert len(persisted_paths) == len(artifacts)
    assert all(path.is_relative_to(repository.artifact_root) for path in persisted_paths)

    source_record_ids = set(event_log.record_ids)
    persisted_payloads = {
        payload["artifact_id"]: payload
        for path in persisted_paths
        for payload in (json.loads(path.read_text(encoding="utf-8")),)
    }
    assert set(persisted_payloads) == {artifact.metadata.record_id for artifact in artifacts}
    for artifact, draft in zip(artifacts, event_log.drafts, strict=True):
        assert artifact.source_log_set_id == event_log.log_set_id
        assert artifact.supporting_record_refs == draft.supporting_record_refs
        assert set(artifact.supporting_record_refs).issubset(source_record_ids)
        persisted = persisted_payloads[artifact.metadata.record_id]
        assert persisted["source_log_set_id"] == event_log.log_set_id
        assert tuple(persisted["supporting_record_refs"]) == draft.supporting_record_refs
