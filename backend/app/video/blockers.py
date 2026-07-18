"""Durable, local-only Video_Pack blocker interruption controls."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, replace
from datetime import datetime
from threading import RLock
from time import monotonic
from typing import Final, Protocol

from app.engines.compiler import CompiledGraphNode
from app.engines.graph import GraphExecutionError, GraphNodeResult, GraphNodeServices
from app.models.common import OptimisticTransition, RecordMetadata, utc_now
from app.models.identifiers import CorrelationId, OrganizationId, RunId
from app.models.runs import RunRecord
from app.repositories.protocols import RunRepository

COMPLIANCE_AGENT_ID: Final[str] = "video.compliance_agent"
STUB_MEDIA_ADAPTER_ID: Final[str] = "media.stub"
MAX_BLOCKER_RESPONSE_SECONDS: Final[float] = 5.0


@dataclass(frozen=True, slots=True)
class VideoBlockerDraft:
    """Validated data required to record one unresolved Video_Pack blocker."""

    blocker_id: str
    source_agent_id: str
    category: str
    evidence_reference: str

    def __post_init__(self) -> None:
        if not self.blocker_id.strip() or not self.source_agent_id.startswith("video."):
            raise ValueError(
                "Video blockers require canonical blocker and source agent identifiers."
            )
        if not self.category.strip() or not self.evidence_reference.strip():
            raise ValueError("Video blockers require a category and evidence reference.")


@dataclass(frozen=True, slots=True)
class VideoBlockerEvent:
    """Redaction-safe, durable event projection retained on the owning run."""

    blocker_id: str
    source_agent_id: str
    category: str
    evidence_reference: str
    detected_at: datetime

    def projection(self) -> dict[str, object]:
        """Return only display-safe immutable blocker fields for run state."""
        return {
            "blocker_id": self.blocker_id,
            "source_agent_id": self.source_agent_id,
            "category": self.category,
            "evidence_reference": self.evidence_reference,
            "status": "unresolved",
            "detected_at": self.detected_at.isoformat(),
        }


class ComplianceBlockerDetector(Protocol):
    """Host-owned local detector seam; it never receives an adapter or network client."""

    def detect(self, run: RunRecord, node: CompiledGraphNode) -> VideoBlockerDraft | None:
        """Return a blocker only after the ComplianceAgent's local review."""


class LocalMonotonicBlockerScheduler:
    """Track a blocker response deadline using only an injected local monotonic clock."""

    def __init__(
        self,
        clock: Callable[[], float] = monotonic,
        response_limit_seconds: float = MAX_BLOCKER_RESPONSE_SECONDS,
    ) -> None:
        if response_limit_seconds <= 0 or response_limit_seconds > MAX_BLOCKER_RESPONSE_SECONDS:
            raise ValueError(
                "Video blocker response limit must be greater than zero and at most five seconds."
            )
        self._clock = clock
        self._response_limit_seconds = response_limit_seconds
        self._detected_at: float | None = None
        self._stopped_at: float | None = None

    def mark_detected(self) -> None:
        """Start the local response window on the first unresolved blocker."""
        if self._detected_at is None:
            self._detected_at = self._clock()

    def mark_stopped(self) -> float:
        """Record the local monotonic delay before a new step is prevented."""
        if self._detected_at is None:
            return 0.0
        self._stopped_at = self._clock()
        return max(0.0, self._stopped_at - self._detected_at)

    @property
    def last_stop_elapsed_seconds(self) -> float | None:
        """Expose deterministic timing evidence without relying on wall-clock time."""
        if self._detected_at is None or self._stopped_at is None:
            return None
        return max(0.0, self._stopped_at - self._detected_at)


class VideoBlockerCancellationToken:
    """Durably retain blockers and cancel future graph scheduling until resolution."""

    def __init__(
        self,
        repository: RunRepository,
        organization_id: OrganizationId,
        run_id: RunId,
        correlation_id: CorrelationId,
        *,
        scheduler: LocalMonotonicBlockerScheduler | None = None,
        timestamp_clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._repository = repository
        self._organization_id = organization_id
        self._run_id = run_id
        self._correlation_id = correlation_id
        self._scheduler = scheduler or LocalMonotonicBlockerScheduler()
        self._timestamp_clock = timestamp_clock
        self._unresolved: dict[str, VideoBlockerEvent] = {}
        self._lock = RLock()

    def publish(self, draft: VideoBlockerDraft) -> None:
        """Append a durable blocker event before signalling graph cancellation."""
        with self._lock:
            if draft.blocker_id in self._unresolved:
                return
            event = VideoBlockerEvent(
                blocker_id=draft.blocker_id,
                source_agent_id=draft.source_agent_id,
                category=draft.category,
                evidence_reference=draft.evidence_reference,
                detected_at=self._timestamp_clock(),
            )
            persisted = self._append_event(event)
            if not persisted:
                raise GraphExecutionError("video_blocker_event_persistence_failed")
            self._unresolved[event.blocker_id] = event
            self._scheduler.mark_detected()

    def resolve(self, blocker_id: str, resolution: str) -> bool:
        """Retain a resolution while keeping the historical blocked graph state visible."""
        if not blocker_id.strip() or not resolution.strip():
            return False
        with self._lock:
            if blocker_id not in self._unresolved:
                return False
            current = self._current_run()
            if current is None:
                return False
            output = dict(current.output or {})
            events = self._event_list(output)
            changed = False
            for event in events:
                if event.get("blocker_id") == blocker_id and event.get("status") == "unresolved":
                    event["status"] = "resolved"
                    event["resolution"] = resolution
                    event["resolved_at"] = self._timestamp_clock().isoformat()
                    changed = True
            updated_output = output | {"video_blocker_events": events}
            if not changed or not self._persist_output(current, updated_output):
                return False
            del self._unresolved[blocker_id]
            return True

    def cancellation_reason(self) -> str | None:
        """Return an immediate cancellation reason before the engine schedules another node."""
        with self._lock:
            if not self._unresolved:
                return None
            self._scheduler.mark_stopped()
            sources = {event.source_agent_id for event in self._unresolved.values()}
            if COMPLIANCE_AGENT_ID in sources:
                return "video_compliance_blocker_detected"
            return "video_blocker_detected"

    @property
    def last_stop_elapsed_seconds(self) -> float | None:
        """Return monotonic cancellation timing evidence for deterministic validation."""
        return self._scheduler.last_stop_elapsed_seconds

    def _append_event(self, event: VideoBlockerEvent) -> bool:
        current = self._current_run()
        if current is None:
            return False
        output = dict(current.output or {})
        events = self._event_list(output)
        events.append(event.projection())
        return self._persist_output(current, output | {"video_blocker_events": events})

    def _current_run(self) -> RunRecord | None:
        result = self._repository.get_by_run_id(self._organization_id, self._run_id)
        return result.value if result.is_success else None

    def _persist_output(self, current: RunRecord, output: Mapping[str, object]) -> bool:
        updated = replace(
            current,
            metadata=self._next_metadata(current),
            output=dict(output),
        )
        transition = OptimisticTransition(
            record_id=current.metadata.record_id,
            organization_id=current.metadata.organization_id,
            expected_version=current.metadata.version,
            correlation_id=self._correlation_id,
        )
        return self._repository.transition(updated, transition).is_success

    @staticmethod
    def _event_list(output: Mapping[str, object]) -> list[dict[str, object]]:
        raw_events = output.get("video_blocker_events", ())
        if not isinstance(raw_events, list | tuple):
            return []
        return [dict(event) for event in raw_events if isinstance(event, Mapping)]

    def _next_metadata(self, current: RunRecord) -> RecordMetadata:
        return replace(
            current.metadata,
            correlation_id=self._correlation_id,
            version=current.metadata.version + 1,
            updated_at=self._timestamp_clock(),
        )


class VideoSpineNodeExecutor:
    """Execute the data-only spine through the GraphEngine's broker-only service surface."""

    def __init__(
        self,
        cancellation_token: VideoBlockerCancellationToken,
        detector: ComplianceBlockerDetector | None = None,
    ) -> None:
        self._cancellation_token = cancellation_token
        self._detector = detector

    def execute(
        self,
        run: RunRecord,
        node: CompiledGraphNode,
        services: GraphNodeServices,
    ) -> GraphNodeResult:
        """Call only the registered stub adapter and publish compliance blockers locally."""
        for adapter_id in node.declared_tool_ids:
            if adapter_id != STUB_MEDIA_ADAPTER_ID:
                raise GraphExecutionError("video_non_stub_media_adapter_requested")
            services.request_tool(adapter_id, {"run_id": str(run.run_id), "node_id": node.node_id})
        if node.agent_id == COMPLIANCE_AGENT_ID and self._detector is not None:
            blocker = self._detector.detect(run, node)
            if blocker is not None:
                if blocker.source_agent_id != COMPLIANCE_AGENT_ID:
                    raise GraphExecutionError("video_compliance_blocker_source_invalid")
                self._cancellation_token.publish(blocker)
        return GraphNodeResult()
