"""Documentation integrity and reviewed Video Pack refresh orchestration.

Documentation is an operationally isolated diagnostic surface.  The checker only
reads local files and reports claims that cannot be proven from the checked-in
Video Pack.  Refreshes use the same local intake, exact approval, corpus
manifest, mapping-review, standalone, evidence, and provenance boundaries for
both normal and urgent requests; urgency never removes a gate.
"""

from __future__ import annotations

import inspect
import re
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Final

from app.video.migration.approval import ApprovalVerificationReport, verify_human_import_gate
from app.video.migration.canonical import canonicalize_json, sort_findings
from app.video.migration.contracts import (
    ApprovedImportSet,
    CanonicalRecord,
    HistoricalProvenance,
    ImportDryRunReport,
    ImportFinding,
    ImportMode,
    MigrationResult,
    SourceSnapshot,
)
from app.video.migration.corpus import CorpusWriteReport, validate_corpus_integrity, write_corpus
from app.video.migration.intake import LicenseDeclaration, plan_source_intake
from app.video.migration.paths import PathInput

DOCUMENTATION_SCHEMA_VERSION: Final[str] = "1.0"
VIDEO_README_PATH: Final[str] = "business/video/README.md"
ADOPTION_PATH: Final[str] = "adoption.md"
STRUCTURE_PATH: Final[str] = "structure.md"
DOCUMENTATION_PATHS: Final[tuple[str, ...]] = (
    VIDEO_README_PATH,
    ADOPTION_PATH,
    STRUCTURE_PATH,
)

_COUNT_PATTERNS: Final[tuple[tuple[str, re.Pattern[str]], ...]] = (
    (
        "agents",
        re.compile(
            r"(?:\b(\d+)\s+(?:common\s+)?(?:video[- ]agents?|agents?)\b|"
            r"\bagents?\b\s*(?:[:|]|-\s*)\s*\**(\d+))",
            re.I,
        ),
    ),
    (
        "workflows",
        re.compile(
            r"(?:\b(\d+)\s+(?:workflow(?:s)?(?:\s+dna)?|dna workflows?)\b|"
            r"\bworkflows?(?:\s+dna)?\b\s*(?:[:|]|-\s*)\s*\**(\d+))",
            re.I,
        ),
    ),
    (
        "special_skills",
        re.compile(
            r"(?:\b(\d+)\s+special[- ]skills?\b|"
            r"\bspecial[- ]skills?\b\s*(?:[:|]|-\s*)\s*\**(\d+))",
            re.I,
        ),
    ),
    (
        "corpus",
        re.compile(
            r"(?:\b(\d+)\s+(?:knowledge\s+)?corpus\s+files?\b|"
            r"\b(?:knowledge\s+)?corpus(?:\s+files?)?\b\s*(?:[:|]|-\s*)\s*\**(\d+))",
            re.I,
        ),
    ),
    (
        "schemas",
        re.compile(
            r"(?:\b(\d+)\s+schemas?\b|\bschemas?\b\s*(?:[:|]|-\s*)\s*\**(\d+))",
            re.I,
        ),
    ),
    (
        "policies",
        re.compile(
            r"(?:\b(\d+)\s+polic(?:y|ies)\b|\bpolic(?:y|ies)\b\s*(?:[:|]|-\s*)\s*\**(\d+))",
            re.I,
        ),
    ),
)
_PATH_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"(?<![A-Za-z0-9_.-])(?:business/video/)?"
    r"(?:agents|workflows|corpus|special_skills|knowledge|schemas|policies)"
    r"/[A-Za-z0-9_.*/-]+"
)
_MANAGED_START: Final[str] = "<!-- BEGIN VIDEO PACK MIGRATION -->"
_MANAGED_END: Final[str] = "<!-- END VIDEO PACK MIGRATION -->"


class RefreshKind(StrEnum):
    """Refresh urgency is descriptive only; both values use one gate pipeline."""

    NORMAL = "normal"
    URGENT = "urgent"


@dataclass(frozen=True, slots=True)
class LocalAssetSnapshot(CanonicalRecord):
    """Counts and paths derived only from the checked-in local Video Pack."""

    agent_count: int
    workflow_count: int
    special_skill_count: int
    corpus_file_count: int
    knowledge_file_count: int
    schema_file_count: int
    policy_file_count: int
    agent_ids: tuple[str, ...]
    asset_paths: tuple[str, ...]

    def __post_init__(self) -> None:
        counts = (
            "agent_count",
            "workflow_count",
            "special_skill_count",
            "corpus_file_count",
            "knowledge_file_count",
            "schema_file_count",
            "policy_file_count",
        )
        for name in counts:
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError(f"{name} must be a non-negative integer.")
        ids = tuple(sorted(set(self.agent_ids)))
        if len(ids) != len(self.agent_ids):
            raise ValueError("agent_ids must not contain duplicates.")
        object.__setattr__(self, "agent_ids", ids)
        paths = tuple(sorted(set(self.asset_paths)))
        if len(paths) != len(self.asset_paths):
            raise ValueError("asset_paths must not contain duplicates.")
        object.__setattr__(self, "asset_paths", paths)

    @property
    def counts(self) -> dict[str, int]:
        """Return stable count keys used by documentation claims."""
        return {
            "agents": self.agent_count,
            "workflows": self.workflow_count,
            "special_skills": self.special_skill_count,
            "corpus": self.corpus_file_count,
            "knowledge": self.knowledge_file_count,
            "schemas": self.schema_file_count,
            "policies": self.policy_file_count,
        }


@dataclass(frozen=True, slots=True)
class DocumentationFinding(CanonicalRecord):
    """A non-blocking diagnostic that remains a completion-gate failure."""

    code: str
    path: str
    field: str
    message: str
    blocks_unrelated_operations: bool = False
    blocks_completion: bool = True

    def __post_init__(self) -> None:
        if not self.code.strip() or not self.path.strip() or not self.message.strip():
            raise ValueError("Documentation findings require code, path, and message.")
        if not isinstance(self.blocks_unrelated_operations, bool):
            raise TypeError("blocks_unrelated_operations must be a boolean.")
        if not isinstance(self.blocks_completion, bool):
            raise TypeError("blocks_completion must be a boolean.")

    def to_import_finding(self) -> ImportFinding:
        """Project to the common redaction-safe diagnostic contract."""
        return ImportFinding(self.code, path=self.path, field=self.field, message=self.message)


@dataclass(frozen=True, slots=True)
class DocumentationReport(CanonicalRecord):
    """Deterministic documentation result consumed by completion gates."""

    result: MigrationResult
    documents: tuple[str, ...]
    claims: tuple[dict[str, object], ...]
    findings: tuple[DocumentationFinding, ...]
    assets: LocalAssetSnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "result", MigrationResult(self.result))
        object.__setattr__(self, "documents", tuple(sorted(set(self.documents))))
        object.__setattr__(self, "claims", tuple(self.claims))
        findings = tuple(self.findings)
        if any(not isinstance(finding, DocumentationFinding) for finding in findings):
            raise TypeError("findings must contain DocumentationFinding records.")
        object.__setattr__(
            self, "findings", tuple(sorted(findings, key=_documentation_finding_key))
        )
        if not isinstance(self.assets, LocalAssetSnapshot):
            raise TypeError("assets must be a LocalAssetSnapshot.")

    @property
    def is_valid(self) -> bool:
        """Return whether all checked documentation claims are locally provable."""
        return self.result is MigrationResult.PASS and not self.findings

    @property
    def completion_gate_passed(self) -> bool:
        """Documentation remains a completion gate despite non-blocking diagnostics."""
        return self.is_valid and all(not finding.blocks_completion for finding in self.findings)

    @property
    def allows_unrelated_operations(self) -> bool:
        """Documentation failures never stop unrelated migration operations."""
        return True

    @property
    def diagnostics(self) -> tuple[ImportFinding, ...]:
        """Return common diagnostic projections for evidence and CLI consumers."""
        return tuple(finding.to_import_finding() for finding in self.findings)


def _documentation_finding_key(finding: DocumentationFinding) -> tuple[str, str, str, str]:
    return finding.code, finding.path, finding.field, finding.message


def _finding(code: str, path: str, field: str, message: str) -> DocumentationFinding:
    return DocumentationFinding(code, path, field, message)


def _count_files(root: Path, suffixes: frozenset[str] | None = None) -> int:
    if not root.is_dir():
        return 0
    return sum(
        1
        for path in root.rglob("*")
        if path.is_file() and (suffixes is None or path.suffix.casefold() in suffixes)
    )


def _relative_asset_paths(video_root: Path, repository_root: Path) -> tuple[str, ...]:
    paths: list[str] = []
    if not video_root.is_dir():
        return ()
    for path in sorted(video_root.rglob("*"), key=lambda value: value.as_posix()):
        if not path.is_file():
            continue
        try:
            paths.append(path.relative_to(repository_root).as_posix())
        except ValueError:
            continue
    return tuple(paths)


def collect_local_asset_snapshot(
    video_root: PathInput,
    *,
    repository_root: PathInput | None = None,
) -> LocalAssetSnapshot:
    """Build a count snapshot without reading documentation or corpus bodies."""
    root = Path(video_root).resolve(strict=False)
    repository = (
        Path(repository_root).resolve(strict=False)
        if repository_root is not None
        else root.parent.parent
    )
    agents_root = root / "agents"
    agent_ids = (
        tuple(
            path.name
            for path in sorted(agents_root.iterdir(), key=lambda value: value.name)
            if path.is_dir()
            and (path.name.startswith("video.") or (path / "agent_spec.json").exists())
        )
        if agents_root.is_dir()
        else ()
    )
    workflows_root = root / "workflows"
    special_skills_root = root / "special_skills"
    return LocalAssetSnapshot(
        agent_count=len(agent_ids),
        workflow_count=_count_files(workflows_root, frozenset({".json"})),
        special_skill_count=sum(1 for path in special_skills_root.iterdir() if path.is_dir())
        if special_skills_root.is_dir()
        else 0,
        corpus_file_count=_count_files(root / "corpus"),
        knowledge_file_count=_count_files(root / "knowledge"),
        schema_file_count=_count_files(root / "schemas"),
        policy_file_count=_count_files(root / "policies"),
        agent_ids=agent_ids,
        asset_paths=_relative_asset_paths(root, repository),
    )


def _read_documents(
    repository_root: Path, video_root: Path
) -> tuple[dict[str, str], tuple[DocumentationFinding, ...]]:
    paths = {
        VIDEO_README_PATH: video_root / "README.md",
        ADOPTION_PATH: repository_root / ADOPTION_PATH,
        STRUCTURE_PATH: repository_root / STRUCTURE_PATH,
    }
    documents: dict[str, str] = {}
    findings: list[DocumentationFinding] = []
    for relative_path, path in paths.items():
        try:
            documents[relative_path] = path.read_text(encoding="utf-8")
        except FileNotFoundError:
            findings.append(
                _finding(
                    "documentation_missing_document",
                    relative_path,
                    "document",
                    "The checked-in documentation asset is absent from the repository.",
                )
            )
        except (OSError, UnicodeError):
            findings.append(
                _finding(
                    "documentation_unreadable",
                    relative_path,
                    "document",
                    "The checked-in documentation asset could not be read.",
                )
            )
    return documents, tuple(findings)


def _normalize_claim_path(raw: str) -> str:
    value = raw.strip().strip("` ").rstrip(".,;:)]}>")
    if value.startswith("./"):
        value = value[2:]
    if value.startswith("business/video/"):
        return value
    return f"business/video/{value}"


def _claim_path_exists(claim: str, assets: LocalAssetSnapshot) -> bool:
    if "*" in claim:
        return True
    return claim in assets.asset_paths


def _extract_claims(
    document_path: str, text: str, assets: LocalAssetSnapshot
) -> tuple[tuple[dict[str, object], ...], tuple[DocumentationFinding, ...]]:
    claims: list[dict[str, object]] = []
    findings: list[DocumentationFinding] = []
    for raw_path in sorted(set(_PATH_PATTERN.findall(text))):
        claim_path = _normalize_claim_path(raw_path)
        if claim_path.endswith("/"):
            prefix_present = any(path.startswith(claim_path) for path in assets.asset_paths)
            exists = prefix_present or (
                claim_path == "business/video/corpus/" and assets.corpus_file_count > 0
            )
        else:
            exists = _claim_path_exists(claim_path, assets)
        claims.append({"kind": "path", "path": claim_path, "present": exists})
        if not exists:
            findings.append(
                _finding(
                    "documentation_asset_missing",
                    document_path,
                    "asset_path",
                    f"The documented local asset is absent: {claim_path}.",
                )
            )
    for kind, pattern in _COUNT_PATTERNS:
        for match in pattern.finditer(text):
            expected_text = next(
                (group for group in match.groups() if group is not None),
                None,
            )
            if expected_text is None:
                continue
            expected = int(expected_text)
            actual = assets.counts[kind]
            claims.append({"kind": "count", "asset": kind, "expected": expected, "actual": actual})
            if expected != actual:
                findings.append(
                    _finding(
                        "documentation_count_mismatch",
                        document_path,
                        f"asset_count.{kind}",
                        (
                            f"The documented {kind} count {expected} does not match "
                            f"local count {actual}."
                        ),
                    )
                )
    return tuple(claims), tuple(findings)


def _ownership_findings(document_path: str, text: str) -> tuple[DocumentationFinding, ...]:
    normalized = text.casefold()
    required: dict[str, tuple[tuple[str, ...], str]] = {
        VIDEO_README_PATH: (
            ("common-agent-swarm-ops", "common repository"),
            "The Video Pack README must name the Common Repository owner.",
        ),
        ADOPTION_PATH: (
            ("common-agent-swarm-ops", "business/video"),
            "Adoption documentation must identify the local Common Repository Video Pack.",
        ),
        STRUCTURE_PATH: (
            ("common-agent-swarm-ops", "business/video"),
            "Structure documentation must identify the local Common Repository Video Pack.",
        ),
    }
    terms, message = required[document_path]
    findings: list[DocumentationFinding] = []
    if not all(term.casefold() in normalized for term in terms):
        findings.append(
            _finding("documentation_ownership_mismatch", document_path, "ownership", message)
        )
    stale_markers = (
        "va-agent-swarm remains the canonical repository",
        "va-agent-swarm remains the domain authority",
        "product name: `generic-swarm-ops`",
        "real host path: `c:\\project\\generic-swarm-ops`",
    )
    if any(marker in normalized for marker in stale_markers):
        findings.append(
            _finding(
                "documentation_ownership_mismatch",
                document_path,
                "ownership",
                (
                    "Documentation still assigns Video Pack authority to a historical "
                    "upstream or stale host identity."
                ),
            )
        )
    return tuple(findings)


class DocumentationIntegrityChecker:
    """Read-only checker for local documentation claims and ownership."""

    def __init__(
        self,
        repository_root: PathInput,
        video_root: PathInput | None = None,
    ) -> None:
        self.repository_root = Path(repository_root).resolve(strict=False)
        self.video_root = (
            Path(video_root).resolve(strict=False)
            if video_root is not None
            else self.repository_root / "business" / "video"
        )

    def check(self) -> DocumentationReport:
        """Return all deterministic documentation diagnostics without mutation."""
        assets = collect_local_asset_snapshot(self.video_root, repository_root=self.repository_root)
        documents, document_findings = _read_documents(self.repository_root, self.video_root)
        claims: list[dict[str, object]] = []
        findings: list[DocumentationFinding] = list(document_findings)
        for path in DOCUMENTATION_PATHS:
            text = documents.get(path)
            if text is None:
                continue
            document_claims, claim_findings = _extract_claims(path, text, assets)
            claims.extend({"document": path, **claim} for claim in document_claims)
            findings.extend(claim_findings)
            findings.extend(_ownership_findings(path, text))
        findings = list(sorted(findings, key=_documentation_finding_key))
        return DocumentationReport(
            result=MigrationResult.PASS if not findings else MigrationResult.FAIL,
            documents=tuple(documents),
            claims=tuple(sorted(claims, key=canonicalize_json)),
            findings=tuple(findings),
            assets=assets,
        )


def check_documentation_integrity(
    repository_root: PathInput,
    *,
    video_root: PathInput | None = None,
) -> DocumentationReport:
    """Check documentation claims against local assets; never mutate files."""
    return DocumentationIntegrityChecker(repository_root, video_root).check()


validate_documentation = check_documentation_integrity


def _documentation_section(assets: LocalAssetSnapshot) -> str:
    counts = assets.counts
    return "\n".join(
        (
            _MANAGED_START,
            "## Local Video Pack Authority",
            "",
            "`common-agent-swarm-ops` owns the checked-in `business/video` Video Pack.",
            "The checked-in local assets are the source of truth; upstream values are "
            "historical provenance only.",
            "Refreshes require a pinned snapshot, exact human approval, corpus integrity "
            "verification, standalone verification, and migration evidence.",
            "",
            f"- Agents: {counts['agents']}",
            f"- Workflows: {counts['workflows']}",
            f"- Special skills: {counts['special_skills']}",
            f"- Corpus files: {counts['corpus']}",
            f"- Knowledge files: {counts['knowledge']}",
            f"- Schemas: {counts['schemas']}",
            f"- Policies: {counts['policies']}",
            _MANAGED_END,
        )
    )


def render_local_documentation(assets: LocalAssetSnapshot) -> dict[str, str]:
    """Render deterministic documentation solely from a local asset snapshot."""
    section = _documentation_section(assets)
    readme = "\n".join(
        (
            "# Video Pack",
            "",
            (
                "This checked-in `business/video` directory is the authoritative local "
                "Video Pack owned by `common-agent-swarm-ops`, the Common Repository."
            ),
            (
                "Upstream repositories are historical provenance and reviewed refresh "
                "inputs, not runtime dependencies."
            ),
            "",
            section,
            "",
        )
    )
    adoption = "\n".join(
        (
            "# Video Pack Adoption",
            "",
            (
                "`common-agent-swarm-ops` owns the checked-in `business/video` Video Pack "
                "and its local source of truth."
            ),
            (
                "Historical upstream material may be refreshed only through the reviewed "
                "local migration pipeline."
            ),
            "",
            section,
            "",
        )
    )
    structure = "\n".join(
        (
            "# Common Repository Structure",
            "",
            (
                "`common-agent-swarm-ops` is the Common Repository. `business/video` is its "
                "checked-in local Video Pack."
            ),
            (
                "Asset counts below are generated from the local filesystem and are not "
                "runtime activation claims."
            ),
            "",
            section,
            "",
        )
    )
    return {
        VIDEO_README_PATH: readme,
        ADOPTION_PATH: adoption,
        STRUCTURE_PATH: structure,
    }


def _validated_local_assets(assets: LocalAssetSnapshot) -> bool:
    return assets.agent_count == len(assets.agent_ids) and all(
        path.startswith("business/video/") for path in assets.asset_paths
    )


def write_local_documentation(
    repository_root: PathInput,
    *,
    video_root: PathInput | None = None,
) -> DocumentationReport:
    """Write docs generated from validated local assets, then verify them."""
    repository = Path(repository_root).resolve(strict=True)
    video = (
        Path(video_root).resolve(strict=True)
        if video_root is not None
        else repository / "business" / "video"
    )
    assets = collect_local_asset_snapshot(video, repository_root=repository)
    if not video.is_dir() or not _validated_local_assets(assets):
        return DocumentationIntegrityChecker(repository, video).check()
    rendered = render_local_documentation(assets)
    targets = {
        VIDEO_README_PATH: video / "README.md",
        ADOPTION_PATH: repository / ADOPTION_PATH,
        STRUCTURE_PATH: repository / STRUCTURE_PATH,
    }
    try:
        for relative_path in DOCUMENTATION_PATHS:
            target = targets[relative_path]
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(rendered[relative_path], encoding="utf-8", newline="\n")
    except (OSError, UnicodeError):
        return DocumentationIntegrityChecker(repository, video).check()
    return DocumentationIntegrityChecker(repository, video).check()


update_documentation = write_local_documentation


@dataclass(frozen=True, slots=True)
class ChangedMapReview(CanonicalRecord):
    """Exact human review record for changed Agent Source Map entries."""

    review_id: str
    reviewer: str
    reviewed_at: datetime
    common_agent_ids: tuple[str, ...]
    result: str = "pass"

    def __post_init__(self) -> None:
        if not self.review_id.strip() or not self.reviewer.strip():
            raise ValueError("Changed map reviews require review_id and reviewer.")
        if self.reviewed_at.tzinfo is None:
            raise ValueError("reviewed_at must be timezone-aware.")
        ids = tuple(sorted(set(self.common_agent_ids)))
        if len(ids) != len(self.common_agent_ids):
            raise ValueError("common_agent_ids must not contain duplicates.")
        object.__setattr__(self, "common_agent_ids", ids)
        if self.result not in {"pass", "fail", "blocked"}:
            raise ValueError("Changed map review result must be pass, fail, or blocked.")

    @property
    def is_approved(self) -> bool:
        return self.result == "pass"


@dataclass(frozen=True, slots=True)
class RefreshRequest:
    """Inputs for a normal or urgent reviewed Video Pack refresh."""

    source_root: PathInput
    snapshot: SourceSnapshot
    destination_root: PathInput
    repository_root: PathInput
    approved_import_set: ApprovedImportSet | None = None
    refresh_kind: RefreshKind = RefreshKind.NORMAL
    write_mode: bool = False
    license_status: LicenseDeclaration = None
    provenance: HistoricalProvenance | Mapping[str, object] | None = None
    allow_paths: tuple[str, ...] = ()
    map_before: object | None = None
    map_after: object | None = None
    changed_map_review: ChangedMapReview | None = None
    standalone_check: Callable[..., object] | None = None
    evidence_recorder: Callable[..., object] | None = None
    update_docs: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "refresh_kind", RefreshKind(self.refresh_kind))
        if not isinstance(self.snapshot, SourceSnapshot):
            raise TypeError("snapshot must be a SourceSnapshot.")
        if self.write_mode and self.approved_import_set is None:
            raise ValueError("write_mode refreshes require an Approved Import Set.")


@dataclass(frozen=True, slots=True)
class RefreshReport(CanonicalRecord):
    """Canonical result of a reviewed refresh attempt."""

    result: MigrationResult
    refresh_kind: RefreshKind
    steps: tuple[str, ...]
    findings: tuple[ImportFinding, ...]
    documentation: DocumentationReport
    changed_map_agent_ids: tuple[str, ...] = ()
    approval_verified: bool = False
    corpus_manifest_digest: str | None = None
    standalone_passed: bool = False
    evidence_recorded: bool = False
    provenance_preserved: bool = False
    completion_gate_passed: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "result", MigrationResult(self.result))
        object.__setattr__(self, "refresh_kind", RefreshKind(self.refresh_kind))
        object.__setattr__(self, "steps", tuple(self.steps))
        object.__setattr__(self, "findings", sort_findings(tuple(self.findings)))
        object.__setattr__(
            self, "changed_map_agent_ids", tuple(sorted(set(self.changed_map_agent_ids)))
        )
        if self.corpus_manifest_digest is not None and len(self.corpus_manifest_digest) != 64:
            raise ValueError("corpus_manifest_digest must be a SHA-256 digest.")
        for name in (
            "approval_verified",
            "standalone_passed",
            "evidence_recorded",
            "provenance_preserved",
            "completion_gate_passed",
        ):
            if not isinstance(getattr(self, name), bool):
                raise TypeError(f"{name} must be a boolean.")

    @property
    def is_success(self) -> bool:
        return self.result in (MigrationResult.PASS, MigrationResult.NO_CHANGE)

    @property
    def is_completion_ready(self) -> bool:
        return self.completion_gate_passed


StandaloneCheck = Callable[[RefreshRequest], object]
EvidenceRecorder = Callable[[RefreshReport], object]


def _map_entries(value: object | None) -> dict[str, object]:
    if value is None:
        return {}
    if hasattr(value, "entries"):
        raw_entries = value.entries
        return {
            str(entry.common_agent_id): entry
            for entry in raw_entries
            if getattr(entry, "common_agent_id", None)
        }
    if isinstance(value, Mapping):
        raw_entries = value.get("entries", value)
        if isinstance(raw_entries, Mapping):
            return {str(key): item for key, item in raw_entries.items()}
        if isinstance(raw_entries, Sequence) and not isinstance(
            raw_entries, (str, bytes, bytearray)
        ):
            result: dict[str, object] = {}
            for item in raw_entries:
                if isinstance(item, Mapping) and isinstance(item.get("common_agent_id"), str):
                    result[item["common_agent_id"]] = item
            return result
    return {}


def changed_map_entries(before: object | None, after: object | None) -> tuple[str, ...]:
    """Return Common Agent IDs whose reviewed map entries changed."""
    before_entries = _map_entries(before)
    after_entries = _map_entries(after)
    changed = {
        agent_id
        for agent_id in set(before_entries) | set(after_entries)
        if canonicalize_json(before_entries.get(agent_id))
        != canonicalize_json(after_entries.get(agent_id))
    }
    return tuple(sorted(changed))


def _invoke_step(
    callback: Callable[..., object], request: RefreshRequest | RefreshReport
) -> object:
    try:
        has_parameters = bool(inspect.signature(callback).parameters)
    except (TypeError, ValueError):
        has_parameters = True
    if has_parameters:
        return callback(request)
    return callback()


def _step_passed(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.casefold() in {"pass", "passed", "ok", "standalone pass", "no_change"}
    if isinstance(value, Mapping):
        result = value.get("result")
        if result is not None:
            return _step_passed(result)
        return bool(value.get("is_valid", value.get("passed", False)))
    for attribute in ("is_valid", "is_success", "passed"):
        candidate = getattr(value, attribute, None)
        if candidate is not None:
            return bool(candidate() if callable(candidate) else candidate)
    result = getattr(value, "result", None)
    return _step_passed(result) if result is not None else False


def _step_finding(code: str, message: str) -> ImportFinding:
    return ImportFinding(code, field="refresh", message=message)


class RefreshOrchestrator:
    """Run normal and urgent refreshes through one reviewed local pipeline."""

    def run(self, request: RefreshRequest) -> RefreshReport:
        if not isinstance(request, RefreshRequest):
            raise TypeError("request must be a RefreshRequest.")
        steps: list[str] = ["pinned_snapshot"]
        findings: list[ImportFinding] = []
        documentation = DocumentationIntegrityChecker(
            request.repository_root,
            Path(request.repository_root) / "business" / "video",
        ).check()
        if request.update_docs and request.write_mode:
            updated = write_local_documentation(
                request.repository_root,
                video_root=Path(request.repository_root) / "business" / "video",
            )
            documentation = updated
            steps.append("documentation_update")
        steps.append("documentation_check")

        try:
            intake = plan_source_intake(
                request.source_root,
                request.snapshot,
                destination_root=request.destination_root,
                allow_paths=request.allow_paths,
                license_status=request.license_status,
                allowed_existing_destinations=(
                    tuple(file.destination_path for file in request.approved_import_set.files)
                    if request.approved_import_set is not None
                    else ()
                ),
            )
        except (OSError, TypeError, ValueError):
            intake = ImportDryRunReport(
                snapshot=request.snapshot,
                mode=ImportMode.DRY_RUN,
                included=(),
                excluded=(),
                findings=(
                    _step_finding(
                        "refresh_intake_configuration_error",
                        "Refresh intake configuration is invalid.",
                    ),
                ),
                total_bytes=0,
                result=MigrationResult.FAIL,
            )
        steps.append("pinned_dry_run")
        findings.extend(intake.findings)
        if intake.result is not MigrationResult.PASS:
            return self._report(
                request,
                MigrationResult.FAIL,
                steps,
                findings,
                documentation,
                (),
                False,
                None,
                False,
                False,
                self._provenance_preserved(request),
            )

        approval_verified = False
        approval_report: ApprovalVerificationReport | None = None
        corpus_report: CorpusWriteReport | None = None
        if request.approved_import_set is not None:
            approval_report = verify_human_import_gate(
                intake,
                request.approved_import_set,
                approval_id=request.approved_import_set.approval_id,
                approved_by=request.approved_import_set.approved_by,
                license_status=request.license_status,
                provenance=request.provenance,
                declared_destinations=tuple(
                    file.destination_path for file in request.approved_import_set.files
                ),
            )
            steps.append("exact_approval")
            findings.extend(approval_report.findings)
            approval_verified = approval_report.result is MigrationResult.PASS
            if request.write_mode and not approval_verified:
                findings.append(
                    _step_finding(
                        "refresh_approval_blocked",
                        "Refresh approval does not exactly match the pinned snapshot.",
                    )
                )
        elif request.write_mode:
            findings.append(
                _step_finding(
                    "refresh_approval_required",
                    "Write-mode refresh requires an Approved Import Set.",
                )
            )

        changed_ids = changed_map_entries(request.map_before, request.map_after)
        if changed_ids:
            steps.append("changed_map_review")
            review = request.changed_map_review
            if (
                review is None
                or not review.is_approved
                or set(review.common_agent_ids) != set(changed_ids)
            ):
                findings.append(
                    _step_finding(
                        "refresh_changed_map_review_required",
                        (
                            "Every changed Agent Source Map entry requires an exact "
                            "passing human review."
                        ),
                    )
                )
        else:
            steps.append("changed_map_review_not_required")

        if request.write_mode and approval_verified and not findings:
            if approval_report is None or request.approved_import_set is None:
                raise RuntimeError(
                    "A passing refresh approval report is required before corpus write."
                )
            corpus_report = write_corpus(
                request.destination_root,
                request.approved_import_set,
                verification=approval_report,
                allow_reviewed_replacements=True,
            )
            steps.append("corpus_manifest")
            findings.extend(corpus_report.findings)
            if corpus_report.is_success:
                integrity = validate_corpus_integrity(request.destination_root)
                steps.append("corpus_integrity")
                findings.extend(integrity.findings)
        elif request.write_mode:
            steps.append("corpus_manifest_blocked")

        standalone_passed = False
        if request.write_mode:
            steps.append("standalone")
            if request.standalone_check is None:
                findings.append(
                    _step_finding(
                        "refresh_standalone_required",
                        "Refresh completion requires standalone verification.",
                    )
                )
            else:
                try:
                    standalone_passed = _step_passed(
                        _invoke_step(request.standalone_check, request)
                    )
                except (OSError, TypeError, ValueError):
                    standalone_passed = False
                if not standalone_passed:
                    findings.append(
                        _step_finding(
                            "refresh_standalone_failed", "Standalone verification did not pass."
                        )
                    )

        provisional = self._report(
            request,
            MigrationResult.NO_CHANGE
            if corpus_report is not None and corpus_report.is_no_change
            else MigrationResult.PASS,
            steps,
            findings,
            documentation,
            changed_ids,
            approval_verified,
            corpus_report.manifest_digest if corpus_report is not None else None,
            standalone_passed,
            False,
            self._provenance_preserved(request),
        )
        evidence_recorded = False
        if request.write_mode:
            steps.append("evidence")
            if request.evidence_recorder is None:
                findings.append(
                    _step_finding(
                        "refresh_evidence_required",
                        "Refresh completion requires migration evidence.",
                    )
                )
            else:
                try:
                    evidence_recorded = _step_passed(
                        _invoke_step(request.evidence_recorder, provisional)
                    )
                except (OSError, TypeError, ValueError):
                    evidence_recorded = False
                if not evidence_recorded:
                    findings.append(
                        _step_finding(
                            "refresh_evidence_failed", "Migration evidence could not be recorded."
                        )
                    )

        return self._report(
            request,
            MigrationResult.NO_CHANGE
            if corpus_report is not None and corpus_report.is_no_change
            else MigrationResult.PASS,
            steps,
            findings,
            documentation,
            changed_ids,
            approval_verified,
            corpus_report.manifest_digest if corpus_report is not None else None,
            standalone_passed,
            evidence_recorded,
            self._provenance_preserved(request),
        )

    @staticmethod
    def _provenance_preserved(request: RefreshRequest) -> bool:
        approved = request.approved_import_set
        return (
            approved is not None
            and approved.snapshot.source_repository == request.snapshot.source_repository
            and approved.snapshot.source_commit == request.snapshot.source_commit
            and approved.snapshot.source_root == request.snapshot.source_root
            and bool(approved.files)
        )

    @staticmethod
    def _report(
        request: RefreshRequest,
        result: MigrationResult,
        steps: Iterable[str],
        findings: Iterable[ImportFinding],
        documentation: DocumentationReport,
        changed_ids: Iterable[str],
        approval_verified: bool,
        manifest_digest: str | None,
        standalone_passed: bool,
        evidence_recorded: bool,
        provenance_preserved: bool,
    ) -> RefreshReport:
        all_findings = tuple(findings)
        operational_pass = result in (MigrationResult.PASS, MigrationResult.NO_CHANGE) and not any(
            finding.code.startswith("refresh_")
            or finding.code.startswith("approval_")
            or finding.code.startswith("corpus_")
            for finding in all_findings
        )
        completion = (
            (
                operational_pass
                and documentation.completion_gate_passed
                and approval_verified
                and standalone_passed
                and evidence_recorded
                and provenance_preserved
            )
            if request.write_mode
            else False
        )
        return RefreshReport(
            result=result if operational_pass else MigrationResult.BLOCKED,
            refresh_kind=request.refresh_kind,
            steps=tuple(steps),
            findings=all_findings,
            documentation=documentation,
            changed_map_agent_ids=tuple(changed_ids),
            approval_verified=approval_verified,
            corpus_manifest_digest=manifest_digest,
            standalone_passed=standalone_passed,
            evidence_recorded=evidence_recorded,
            provenance_preserved=provenance_preserved,
            completion_gate_passed=completion,
        )


def orchestrate_refresh(request: RefreshRequest) -> RefreshReport:
    """Convenience entry point for either a normal or urgent refresh."""
    return RefreshOrchestrator().run(request)


refresh_video_pack = orchestrate_refresh

__all__ = [
    "ADOPTION_PATH",
    "DOCUMENTATION_PATHS",
    "DOCUMENTATION_SCHEMA_VERSION",
    "STRUCTURE_PATH",
    "VIDEO_README_PATH",
    "ChangedMapReview",
    "DocumentationFinding",
    "DocumentationIntegrityChecker",
    "DocumentationReport",
    "LocalAssetSnapshot",
    "RefreshKind",
    "RefreshOrchestrator",
    "RefreshReport",
    "RefreshRequest",
    "changed_map_entries",
    "check_documentation_integrity",
    "collect_local_asset_snapshot",
    "orchestrate_refresh",
    "refresh_video_pack",
    "render_local_documentation",
    "update_documentation",
    "validate_documentation",
    "write_local_documentation",
]
