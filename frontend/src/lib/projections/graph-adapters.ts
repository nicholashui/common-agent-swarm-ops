import type { CommandIntent } from "../commands/CommandCoordinator";
import type { GeneratedActionReference, GeneratedJsonObject, GeneratedJsonValue } from "../api/client";
import { ProjectionMapper, type ActionReferenceView } from "./ProjectionMapper";

export const GRAPH_RELATIONSHIPS = ["data_flow", "state_flow", "iteration"] as const;
export type GraphRelationship = (typeof GRAPH_RELATIONSHIPS)[number];

export const GRAPH_VALIDATION_CATEGORIES = [
  "version",
  "schema",
  "tool_policy",
  "budget",
  "verification",
  "rollback",
  "approval",
] as const;
export type GraphValidationCategory = (typeof GRAPH_VALIDATION_CATEGORIES)[number];

export const GRAPH_COMMAND_KINDS = ["run", "retry", "skip", "cancel", "replay", "escalation", "instantiate"] as const;
export type GraphCommandKind = (typeof GRAPH_COMMAND_KINDS)[number];

export interface GraphEdgeSemantics {
  readonly textLabel: "Data flow" | "State flow" | "Iteration";
  readonly lineStyle: "solid" | "dashed" | "dotted";
  readonly marker: "arrow" | "state-arrow" | "loop";
}

export interface GraphTaskView {
  readonly lifecycle: string;
  readonly statusDetail?: string;
}

export interface GraphNodeView {
  readonly id: string;
  readonly label: string;
  readonly kind: "common" | "custom";
  readonly immutableVersion?: string;
  readonly provenanceReference?: string;
  readonly forkOrigin?: string;
  readonly customReason?: string;
  readonly task?: GraphTaskView;
}

export interface GraphEdgeView {
  readonly id: string;
  readonly sourceId: string;
  readonly targetId: string;
  readonly relationship: GraphRelationship;
  readonly semantics: GraphEdgeSemantics;
  readonly label?: string;
}

export interface GraphValidationCategoryView {
  readonly category: GraphValidationCategory;
  readonly result: string;
  readonly detail?: string;
}

export interface GraphValidationView {
  readonly ineligible: boolean;
  readonly categories: readonly GraphValidationCategoryView[];
}

export interface GraphActionView extends ActionReferenceView {
  readonly kind: GraphCommandKind;
}

export interface GraphProjectionView {
  readonly graphRevision?: string;
  readonly statusLabel?: string;
  readonly nodes: readonly GraphNodeView[];
  readonly edges: readonly GraphEdgeView[];
  readonly validation: GraphValidationView;
  readonly actions: readonly GraphActionView[];
}

export interface ComposerPatternView {
  readonly id: string;
  readonly label: string;
  readonly immutableVersion: string;
  readonly provenanceReference: string;
  readonly instantiationAction?: GraphActionView;
}

export interface ComposerProjectionView {
  readonly patterns: readonly ComposerPatternView[];
}

export interface GraphCommandPayload {
  readonly graphRevision?: string;
}

const MAPPER = new ProjectionMapper();

/**
 * Translates generated graph projection fields into a graph-library-neutral view.
 * It preserves returned semantics and provenance without supplying UI defaults.
 */
export function mapGraphProjection(projection: GeneratedJsonObject): GraphProjectionView {
  const validation = mapValidation(objectValue(projection.validation));
  return {
    ...(stringValue(projection.graph_revision) === undefined ? {} : { graphRevision: stringValue(projection.graph_revision) }),
    ...(graphStatusLabel(projection) === undefined ? {} : { statusLabel: graphStatusLabel(projection) }),
    nodes: objectList(projection.nodes).flatMap(mapNode),
    edges: objectList(projection.edges).flatMap(mapEdge),
    validation,
    actions: mapGraphActions(projection.action_references),
  };
}

/** Maps common pattern provenance and only a returned instantiation action for composer selection. */
export function mapComposerProjection(projection: GeneratedJsonObject): ComposerProjectionView {
  return {
    patterns: objectList(projection.common_patterns).flatMap((pattern): readonly ComposerPatternView[] => {
      const id = stringValue(pattern.id);
      const label = stringValue(pattern.label);
      const immutableVersion = stringValue(pattern.immutable_version);
      const provenanceReference = stringValue(pattern.provenance_reference);
      if (id === undefined || label === undefined || immutableVersion === undefined || provenanceReference === undefined) return [];
      const instantiationAction = mapGraphAction(objectValue(pattern.instantiation_action_reference));
      return [{
        id,
        label,
        immutableVersion,
        provenanceReference,
        ...(instantiationAction?.kind === "instantiate" ? { instantiationAction } : {}),
      }];
    }),
  };
}

/** Provides text, line pattern, and marker semantics so relationships are never color-only. */
export function graphEdgeSemantics(relationship: GraphRelationship): GraphEdgeSemantics {
  switch (relationship) {
    case "data_flow":
      return { textLabel: "Data flow", lineStyle: "solid", marker: "arrow" };
    case "state_flow":
      return { textLabel: "State flow", lineStyle: "dashed", marker: "state-arrow" };
    case "iteration":
      return { textLabel: "Iteration", lineStyle: "dotted", marker: "loop" };
  }
}

/** Run actions are blocked by an ineligible validation result in addition to returned action eligibility. */
export function isGraphActionDisabled(
  action: GraphActionView,
  validation: GraphValidationView,
): boolean {
  return !action.eligible || (action.kind === "run" && validation.ineligible);
}

/** Builds a command intent solely from a returned graph action reference and returned graph revision. */
export function createGraphCommandIntent(
  action: GraphActionView,
  graphRevision?: string,
): CommandIntent<GraphCommandPayload> | undefined {
  if (!GRAPH_COMMAND_KINDS.includes(action.kind) || !action.eligible) return undefined;
  return {
    actionReferenceId: action.id,
    actionReference: action.source,
    payload: graphRevision === undefined ? {} : { graphRevision },
  };
}

function mapNode(source: GeneratedJsonObject): readonly GraphNodeView[] {
  const id = stringValue(source.id);
  const label = stringValue(source.label);
  const kind = stringValue(source.kind);
  if (id === undefined || label === undefined || (kind !== "common" && kind !== "custom")) return [];

  const task = mapTask(objectValue(source.task));
  if (kind === "common") {
    const immutableVersion = stringValue(source.immutable_version);
    const provenanceReference = stringValue(source.provenance_reference);
    return [{
      id,
      label,
      kind,
      ...(immutableVersion === undefined ? {} : { immutableVersion }),
      ...(provenanceReference === undefined ? {} : { provenanceReference }),
      ...(task === undefined ? {} : { task }),
    }];
  }

  const forkOrigin = stringValue(source.fork_origin);
  const customReason = stringValue(source.custom_reason);
  return [{
    id,
    label,
    kind,
    ...(forkOrigin === undefined ? {} : { forkOrigin }),
    ...(customReason === undefined ? {} : { customReason }),
    ...(task === undefined ? {} : { task }),
  }];
}

function mapTask(source: GeneratedJsonObject | undefined): GraphTaskView | undefined {
  if (source === undefined) return undefined;
  const lifecycle = stringValue(source.lifecycle);
  const statusDetail = stringValue(source.status_detail);
  return lifecycle === undefined ? undefined : {
    lifecycle,
    ...(statusDetail === undefined ? {} : { statusDetail }),
  };
}

function mapEdge(source: GeneratedJsonObject): readonly GraphEdgeView[] {
  const id = stringValue(source.id);
  const sourceId = stringValue(source.source_id);
  const targetId = stringValue(source.target_id);
  const relationship = stringValue(source.relationship);
  if (id === undefined || sourceId === undefined || targetId === undefined || !isGraphRelationship(relationship)) return [];
  const label = stringValue(source.label);
  return [{
    id,
    sourceId,
    targetId,
    relationship,
    semantics: graphEdgeSemantics(relationship),
    ...(label === undefined ? {} : { label }),
  }];
}

function mapValidation(source: GeneratedJsonObject | undefined): GraphValidationView {
  return {
    ineligible: source?.eligible === false,
    categories: objectList(source?.categories).flatMap((category): readonly GraphValidationCategoryView[] => {
      const name = stringValue(category.category);
      const result = stringValue(category.result);
      const detail = stringValue(category.detail);
      if (!isGraphValidationCategory(name) || result === undefined) return [];
      return [{ category: name, result, ...(detail === undefined ? {} : { detail }) }];
    }),
  };
}

function mapGraphActions(value: GeneratedJsonValue | undefined): readonly GraphActionView[] {
  return objectList(value).flatMap((source): readonly GraphActionView[] => {
    const action = mapGraphAction(source);
    return action === undefined ? [] : [action];
  });
}

function mapGraphAction(source: GeneratedJsonObject | undefined): GraphActionView | undefined {
  if (source === undefined) return undefined;
  const mapped = MAPPER.mapActionReference(source as GeneratedActionReference);
  const kind = stringValue(source.kind);
  return mapped === null || !isGraphCommandKind(kind) ? undefined : { ...mapped, kind };
}

function graphStatusLabel(projection: GeneratedJsonObject): string | undefined {
  return projection.stale === true ? "Stale" : stringValue(projection.state_label);
}

function objectList(value: GeneratedJsonValue | undefined): readonly GeneratedJsonObject[] {
  return Array.isArray(value) ? value.filter((item): item is GeneratedJsonObject => objectValue(item) !== undefined) : [];
}

function objectValue(value: GeneratedJsonValue | undefined): GeneratedJsonObject | undefined {
  return typeof value === "object" && value !== null && !Array.isArray(value) ? value as GeneratedJsonObject : undefined;
}

function stringValue(value: GeneratedJsonValue | undefined): string | undefined {
  return typeof value === "string" && value.length > 0 ? value : undefined;
}

function isGraphRelationship(value: string | undefined): value is GraphRelationship {
  return value !== undefined && GRAPH_RELATIONSHIPS.includes(value as GraphRelationship);
}

function isGraphValidationCategory(value: string | undefined): value is GraphValidationCategory {
  return value !== undefined && GRAPH_VALIDATION_CATEGORIES.includes(value as GraphValidationCategory);
}

function isGraphCommandKind(value: string | undefined): value is GraphCommandKind {
  return value !== undefined && GRAPH_COMMAND_KINDS.includes(value as GraphCommandKind);
}
