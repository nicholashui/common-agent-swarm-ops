import type { CommandIntent } from "../commands/CommandCoordinator";
import type { GeneratedActionReference, GeneratedJsonObject, GeneratedJsonValue } from "../api/client";
import {
  ProjectionMapper,
  type ActionReferenceView,
  type EvidenceReferenceView,
  type OpaqueReferenceView,
} from "./ProjectionMapper";

export interface ReturnedFieldView {
  readonly key: string;
  readonly label: string;
  readonly value: string;
}

export type ReturnedReferenceView = string | OpaqueReferenceView;

export type DeliveryBlockReason = "missing_delivery_field" | "missing_gate_approval";

export interface ArtifactProjectionView {
  readonly artifactVersion?: string;
  readonly parentLineage: readonly ReturnedReferenceView[];
  readonly technicalSpecification: readonly ReturnedFieldView[];
  readonly rightsAndConsent?: string;
  readonly continuity?: string;
  readonly qualityControl?: string;
  readonly deliveryState?: string;
  readonly deliveryTargets: readonly string[];
  readonly provenanceReference?: ReturnedReferenceView;
  readonly gateApproval?: string;
  readonly deliveryBlocked: boolean;
  readonly deliveryBlockReasons: readonly DeliveryBlockReason[];
}

export interface VaAgentProjectionView {
  readonly identity?: string;
  readonly scope?: string;
  readonly capabilities: readonly string[];
  readonly policies: readonly string[];
  readonly runtimeConstraints: readonly ReturnedFieldView[];
  readonly qualityContract: readonly ReturnedFieldView[];
  readonly critiqueRelationships: readonly string[];
  readonly provenanceObligations: readonly string[];
  readonly publishedVersion?: string;
}

export interface VaTaskProjectionView {
  readonly taskId?: string;
  readonly graphRevision?: string;
  readonly dependencies: readonly string[];
  readonly gates: readonly string[];
  readonly lifecycle?: string;
  readonly recoveryState?: string;
  readonly budget: readonly ReturnedFieldView[];
  readonly checkpoint?: string;
  readonly commonVersionProvenance: readonly ReturnedReferenceView[];
  readonly details: readonly ReturnedFieldView[];
}

export interface VaCritiqueProjectionView {
  readonly critiqueState?: string;
  readonly source?: string;
  readonly target?: string;
  readonly artifactReference?: ReturnedReferenceView;
  readonly message?: string;
  readonly timestamp?: string;
  readonly evidence: readonly EvidenceReferenceView[];
  readonly details: readonly ReturnedFieldView[];
}

export interface VaQualityEvidenceView {
  readonly category: string;
  readonly reference?: EvidenceReferenceView;
  readonly referenceValue?: string;
  readonly details: readonly ReturnedFieldView[];
}

export interface VaApprovalGateView {
  readonly state?: string;
  readonly pendingOperation?: string;
  readonly evidenceRevision?: string;
  readonly criteria: readonly string[];
  readonly artifactReferences: readonly OpaqueReferenceView[];
  readonly qualityEvidence: readonly VaQualityEvidenceView[];
  readonly actions: readonly ActionReferenceView[];
  readonly unavailable: boolean;
}

export interface VaProjectionView {
  readonly template?: string;
  readonly productionPhase?: string;
  readonly commonPatternVersion?: ReturnedReferenceView;
  readonly agents: readonly VaAgentProjectionView[];
  readonly tasks: readonly VaTaskProjectionView[];
  readonly artifacts: readonly ArtifactProjectionView[];
  readonly critiques: readonly VaCritiqueProjectionView[];
  readonly qualityEvidence: readonly VaQualityEvidenceView[];
  readonly approvalGates: readonly VaApprovalGateView[];
  readonly provenance: readonly ReturnedFieldView[];
  readonly actions: readonly ActionReferenceView[];
  readonly approvalUnavailable: boolean;
}

export type VaCommandPayload = Readonly<Record<never, never>>;

const MAPPER = new ProjectionMapper();
const TECHNICAL_SPECIFICATION_FIELDS = [
  "format", "file_type", "size_bytes", "duration", "resolution", "aspect_ratio", "frame_rate", "codec", "audio", "language", "delivery_format",
] as const;
const RETURNED_PROVENANCE_FIELDS = [
  "run_provenance_id", "graph_revision_id", "workflow_definition_version", "source_checkpoint_reference", "source_run_provenance_id", "artifact_version_references",
] as const;
const RUNTIME_FIELDS = ["max_iterations", "max_cost", "max_concurrency", "timeout_seconds", "max_retries", "budget_remaining", "model", "generation_tool"] as const;
const QUALITY_FIELDS = ["passed", "required_fields_complete", "score", "threshold", "rubric", "result", "baseline_reference"] as const;
const TASK_DETAIL_FIELDS = ["iteration", "retry_count", "failure_reason", "status_detail", "ineligible_for_execution"] as const;
const LIST_VALUE_KEYS = ["id", "label", "name", "identifier", "reference", "purpose", "scope", "access_scope", "policy", "rule", "obligation", "requirement", "operation", "allowed_operations", "allowed_operation_types", "task_id", "dependency", "condition", "gate_id"] as const;
const ARTIFACT_STATE_FIELDS = ["validation_state", "rights_and_consent_passed", "continuity_state", "quality_control_state", "qc_status"] as const;

/** Maps one returned artifact projection without adding a delivery or approval state. */
export function mapArtifactProjection(source: GeneratedJsonObject): ArtifactProjectionView {
  const parentLineage = mapReturnedReferences(firstPresent(source, ["parent_lineage", "parent_assets", "parent_version_ids"]));
  const technicalSpecification = mapFields(
    objectValue(firstPresent(source, ["technical_specification", "technical_spec"])),
    TECHNICAL_SPECIFICATION_FIELDS,
  );
  const rightsAndConsent = firstString(source, ["rights_and_consent", "rights_and_consent_state", "rights_consent_state"])
    ?? booleanText(source, "rights_and_consent_passed");
  const continuity = firstString(source, ["continuity_state", "continuity"]);
  const qualityControl = firstString(source, ["quality_control_state", "qc_status", "quality_control", "validation_state"]);
  const deliveryState = firstString(source, ["delivery_state", "delivery_status", "release_state"]);
  const deliveryTargets = mapStrings(firstPresent(source, ["delivery_targets", "target_channels", "delivery_channels"]));
  const provenanceReference = mapReturnedReference(firstPresent(source, ["provenance_reference", "provenance_manifest_reference"]));
  const gateApproval = firstString(source, ["gate_approval", "approval_state", "approval_status", "gate_state", "approval_gate_state"])
    ?? nestedApprovalState(source.approval_gate);
  const gateRequired = source.gate_required !== false && source.approval_required !== false;
  const deliveryBlockReasons: DeliveryBlockReason[] = [];
  if (deliveryState === undefined || deliveryTargets.length === 0 || provenanceReference === undefined) deliveryBlockReasons.push("missing_delivery_field");
  if (gateRequired && gateApproval !== "approved") deliveryBlockReasons.push("missing_gate_approval");

  return {
    ...(firstString(source, ["artifact_version", "version", "artifact_version_id"]) === undefined ? {} : { artifactVersion: firstString(source, ["artifact_version", "version", "artifact_version_id"]) }),
    parentLineage,
    technicalSpecification,
    ...(rightsAndConsent === undefined ? {} : { rightsAndConsent }),
    ...(continuity === undefined ? {} : { continuity }),
    ...(qualityControl === undefined ? {} : { qualityControl }),
    ...(deliveryState === undefined ? {} : { deliveryState }),
    deliveryTargets,
    ...(provenanceReference === undefined ? {} : { provenanceReference }),
    ...(gateApproval === undefined ? {} : { gateApproval }),
    deliveryBlocked: deliveryBlockReasons.length > 0,
    deliveryBlockReasons,
  };
}

/** Maps a nested or top-level VA projection; absent VA data returns undefined for generic fallback. */
export function mapVaProjection(projection: GeneratedJsonObject): VaProjectionView | undefined {
  const source = Object.hasOwn(projection, "va_projection")
    ? objectValue(projection.va_projection)
    : hasVaMarker(projection) ? projection : undefined;
  if (source === undefined) return undefined;

  const approvalGates = mapApprovalGates(source);
  return {
    ...(firstString(source, ["template", "va_template", "production_template"]) === undefined ? {} : { template: firstString(source, ["template", "va_template", "production_template"]) }),
    ...(firstString(source, ["production_phase", "phase", "production_phase_label"]) === undefined ? {} : { productionPhase: firstString(source, ["production_phase", "phase", "production_phase_label"]) }),
    ...(mapReturnedReference(firstPresent(source, ["common_pattern_version", "pattern_version_reference", "pattern_version_id"])) === undefined ? {} : { commonPatternVersion: mapReturnedReference(firstPresent(source, ["common_pattern_version", "pattern_version_reference", "pattern_version_id"])) }),
    agents: mapAgents(firstPresent(source, ["common_agent_versions", "agents", "agent_contracts"])),
    tasks: mapTasks(firstPresent(source, ["agent_tasks", "tasks", "task_projections"])),
    artifacts: mapArtifacts(firstPresent(source, ["artifact_handoffs", "artifacts", "artifact_projections"])),
    critiques: mapCritiques(firstPresent(source, ["critique_records", "critiques", "critique_projections"])),
    qualityEvidence: mapQualityEvidence(firstPresent(source, ["quality_evidence", "quality_evidence_references"])),
    approvalGates,
    provenance: mapFields(objectValue(firstPresent(source, ["pinned_provenance", "provenance"])), RETURNED_PROVENANCE_FIELDS),
    actions: mapActions(firstPresent(source, ["action_references", "actions"])),
    approvalUnavailable: approvalGates.some((gate) => gate.unavailable),
  };
}

/** Builds a command intent from a returned eligible VA action; it never creates an action reference. */
export function createVaCommandIntent(action: ActionReferenceView): CommandIntent<VaCommandPayload> | undefined {
  if (!action.eligible) return undefined;
  return { actionReferenceId: action.id, actionReference: action.source, payload: {} };
}

function mapAgents(value: GeneratedJsonValue | undefined): readonly VaAgentProjectionView[] {
  return objectList(value).map((source): VaAgentProjectionView => ({
    ...(firstString(source, ["canonical_identity", "identity", "canonical_name"]) === undefined ? {} : { identity: firstString(source, ["canonical_identity", "identity", "canonical_name"]) }),
    ...(firstString(source, ["scope", "boundaries", "category"]) === undefined ? {} : { scope: firstString(source, ["scope", "boundaries", "category"]) }),
    capabilities: mapStrings(firstPresent(source, ["capabilities", "responsibilities", "tools"])),
    policies: mapStrings(firstPresent(source, ["policies", "tool_policy", "approval_authority"])),
    runtimeConstraints: mapFields(objectValue(firstPresent(source, ["runtime_constraints", "runtime_limits", "runtime_policy"])), RUNTIME_FIELDS),
    qualityContract: mapFields(objectValue(firstPresent(source, ["quality_contract", "quality_rubric"])), QUALITY_FIELDS),
    critiqueRelationships: mapStrings(firstPresent(source, ["critique_relationships", "accepts_critique_from", "comments_on"])),
    provenanceObligations: mapStrings(firstPresent(source, ["provenance_obligations", "provenance_policy"])),
    ...(firstString(source, ["published_version", "version", "agent_version_id", "content_digest"]) === undefined ? {} : { publishedVersion: firstString(source, ["published_version", "version", "agent_version_id", "content_digest"]) }),
  }));
}

function mapTasks(value: GeneratedJsonValue | undefined): readonly VaTaskProjectionView[] {
  return objectList(value).map((source): VaTaskProjectionView => ({
    ...(firstString(source, ["task_id", "id"]) === undefined ? {} : { taskId: firstString(source, ["task_id", "id"]) }),
    ...(firstString(source, ["graph_revision", "graph_revision_id"]) === undefined ? {} : { graphRevision: firstString(source, ["graph_revision", "graph_revision_id"]) }),
    dependencies: mapStrings(firstPresent(source, ["dependencies", "dependency_references"])),
    gates: mapStrings(firstPresent(source, ["approval_gate_ids", "gates", "gate_references"])),
    ...(firstString(source, ["lifecycle", "lifecycle_state", "state"]) === undefined ? {} : { lifecycle: firstString(source, ["lifecycle", "lifecycle_state", "state"]) }),
    ...(firstString(source, ["recovery_state", "recovery", "recovery_status"]) === undefined ? {} : { recoveryState: firstString(source, ["recovery_state", "recovery", "recovery_status"]) }),
    budget: mapFields(objectValue(firstPresent(source, ["budget", "constraints"])), ["budget_remaining", "max_cost", "max_concurrency", "model", "generation_tool"]),
    ...(firstString(source, ["checkpoint", "checkpoint_reference"]) === undefined ? {} : { checkpoint: firstString(source, ["checkpoint", "checkpoint_reference"]) }),
    commonVersionProvenance: mapReturnedReferences(firstPresent(source, ["common_version_provenance", "pinned_common_versions", "pinned_agent_version_id"])),
    details: mapFields(source, TASK_DETAIL_FIELDS),
  }));
}

function mapArtifacts(value: GeneratedJsonValue | undefined): readonly ArtifactProjectionView[] {
  return objectList(value).map(mapArtifactProjection);
}

function mapCritiques(value: GeneratedJsonValue | undefined): readonly VaCritiqueProjectionView[] {
  return objectList(value).map((source): VaCritiqueProjectionView => ({
    ...(firstString(source, ["critique_state", "state", "status"]) === undefined ? {} : { critiqueState: firstString(source, ["critique_state", "state", "status"]) }),
    ...(firstString(source, ["source", "source_reference", "from_agent"]) === undefined ? {} : { source: firstString(source, ["source", "source_reference", "from_agent"]) }),
    ...(firstString(source, ["target", "target_task_id", "to_agent"]) === undefined ? {} : { target: firstString(source, ["target", "target_task_id", "to_agent"]) }),
    ...(mapReturnedReference(firstPresent(source, ["artifact_reference", "artifact_id"])) === undefined ? {} : { artifactReference: mapReturnedReference(firstPresent(source, ["artifact_reference", "artifact_id"])) }),
    ...(firstString(source, ["message", "summary"]) === undefined ? {} : { message: firstString(source, ["message", "summary"]) }),
    ...(firstString(source, ["timestamp", "submitted_at", "created_at"]) === undefined ? {} : { timestamp: firstString(source, ["timestamp", "submitted_at", "created_at"]) }),
    evidence: mapEvidence(firstPresent(source, ["evidence_references", "evidence"])),
    details: mapFields(source, ["severity", "rubric_score", "relationship_reference"]),
  }));
}

function mapQualityEvidence(value: GeneratedJsonValue | undefined): readonly VaQualityEvidenceView[] {
  return objectList(value).flatMap((source): readonly VaQualityEvidenceView[] => {
    const category = firstString(source, ["category", "evidence_category", "kind"]);
    if (category === undefined) return [];
    const evidenceSource = objectValue(source.evidence_reference) ?? objectValue(source.reference);
    const reference = evidenceSource === undefined ? undefined : MAPPER.mapEvidenceReference(evidenceSource, ["summary"]);
    const referenceValue = typeof source.evidence_reference === "string" ? source.evidence_reference : typeof source.reference === "string" ? source.reference : undefined;
    return [{
      category,
      ...(reference === null || reference === undefined ? {} : { reference }),
      ...(referenceValue === undefined ? {} : { referenceValue }),
      details: mapFields(source, ["evidence_id", "subject_reference", "passed", "recorded_at", "rubric_score", "threshold", "baseline_reference", "result"]),
    }];
  });
}

function mapApprovalGates(source: GeneratedJsonObject): readonly VaApprovalGateView[] {
  const value = Array.isArray(source.approval_gates)
    ? source.approval_gates
    : objectValue(source.approval_gate) === undefined ? [] : [source.approval_gate];
  return objectList(value).map((gate): VaApprovalGateView => {
    const state = firstString(gate, ["approval_state_label", "state_label", "gate_status", "status", "decision"]);
    const actions = mapActions(firstPresent(gate, ["decision_action_references", "action_references", "actions"]));
    const qualityEvidence = mapQualityEvidence(firstPresent(gate, ["quality_evidence", "quality_evidence_references"]));
    const hasGateShape = state !== undefined || actions.length > 0 || Object.hasOwn(gate, "criteria") || Object.hasOwn(gate, "evidence_revision");
    return {
      ...(state === undefined ? {} : { state }),
      ...(firstString(gate, ["pending_operation", "pending_operation_reference"]) === undefined ? {} : { pendingOperation: firstString(gate, ["pending_operation", "pending_operation_reference"]) }),
      ...(firstString(gate, ["evidence_revision", "revision"]) === undefined ? {} : { evidenceRevision: firstString(gate, ["evidence_revision", "revision"]) }),
      criteria: mapStrings(gate.criteria),
      artifactReferences: mapOpaqueReferences(firstPresent(gate, ["artifact_references", "redacted_artifact_references"])),
      qualityEvidence,
      actions,
      unavailable: !hasGateShape || state === undefined,
    };
  });
}

function mapActions(value: GeneratedJsonValue | undefined): readonly ActionReferenceView[] {
  return objectList(value).flatMap((source): readonly ActionReferenceView[] => {
    const action = MAPPER.mapActionReference(source as GeneratedActionReference);
    return action === null ? [] : [action];
  });
}

function mapEvidence(value: GeneratedJsonValue | undefined): readonly EvidenceReferenceView[] {
  return objectList(value).flatMap((source): readonly EvidenceReferenceView[] => {
    const evidence = MAPPER.mapEvidenceReference(source, ["summary"]);
    return evidence === null ? [] : [evidence];
  });
}

function mapOpaqueReferences(value: GeneratedJsonValue | undefined): readonly OpaqueReferenceView[] {
  return objectList(value).flatMap((source): readonly OpaqueReferenceView[] => {
    const reference = MAPPER.mapOpaqueReference(source);
    return reference === null ? [] : [reference];
  });
}

function mapReturnedReferences(value: GeneratedJsonValue | undefined): readonly ReturnedReferenceView[] {
  if (!Array.isArray(value)) {
    const reference = mapReturnedReference(value);
    return reference === undefined ? [] : [reference];
  }
  return value.flatMap((item): readonly ReturnedReferenceView[] => {
    const reference = mapReturnedReference(item);
    return reference === undefined ? [] : [reference];
  });
}

function mapReturnedReference(value: GeneratedJsonValue | undefined): ReturnedReferenceView | undefined {
  if (typeof value === "string" && value.length > 0) return value;
  const object = objectValue(value);
  if (object === undefined) return undefined;
  return MAPPER.mapOpaqueReference(object) ?? undefined;
}

function mapFields(source: GeneratedJsonObject | undefined, keys: readonly string[]): readonly ReturnedFieldView[] {
  if (source === undefined) return [];
  return keys.flatMap((key): readonly ReturnedFieldView[] => {
    if (!Object.hasOwn(source, key)) return [];
    const value = source[key];
    if (typeof value !== "string" && typeof value !== "number" && typeof value !== "boolean") return [];
    return [{ key, label: fieldLabel(key), value: String(value) }];
  });
}

function mapStrings(value: GeneratedJsonValue | undefined): readonly string[] {
  if (typeof value === "string" && value.length > 0) return [value];
  if (Array.isArray(value)) return value.flatMap((item): readonly string[] => mapStrings(item));
  const object = objectValue(value);
  if (object === undefined) return [];
  return LIST_VALUE_KEYS.flatMap((key): readonly string[] => {
    const item = object[key];
    return typeof item === "string" && item.length > 0 ? [item] : [];
  });
}

function objectList(value: GeneratedJsonValue | undefined): readonly GeneratedJsonObject[] {
  return Array.isArray(value) ? value.flatMap((item): readonly GeneratedJsonObject[] => {
    const source = objectValue(item);
    return source === undefined ? [] : [source];
  }) : [];
}

function objectValue(value: GeneratedJsonValue | undefined): GeneratedJsonObject | undefined {
  return typeof value === "object" && value !== null && !Array.isArray(value) ? value as GeneratedJsonObject : undefined;
}

function firstPresent(source: GeneratedJsonObject, keys: readonly string[]): GeneratedJsonValue | undefined {
  for (const key of keys) if (Object.hasOwn(source, key) && source[key] !== undefined) return source[key];
  return undefined;
}

function firstString(source: GeneratedJsonObject, keys: readonly string[]): string | undefined {
  for (const key of keys) {
    const value = source[key];
    if (typeof value === "string" && value.length > 0) return value;
  }
  return undefined;
}

function booleanText(source: GeneratedJsonObject, key: string): string | undefined {
  return typeof source[key] === "boolean" ? String(source[key]) : undefined;
}

function nestedApprovalState(value: GeneratedJsonValue | undefined): string | undefined {
  const approval = objectValue(value);
  return approval === undefined ? undefined : firstString(approval, ["state", "status", "approval_state"]);
}

function hasVaMarker(source: GeneratedJsonObject): boolean {
  return ["template", "va_template", "production_phase", "common_agent_versions", "artifact_handoffs"].some((key) => Object.hasOwn(source, key));
}

function fieldLabel(key: string): string {
  return key.split("_").map((part): string => part.length === 0 ? part : `${part[0]!.toUpperCase()}${part.slice(1)}`).join(" ");
}
