import assert from "node:assert/strict";
import test from "node:test";

import fc from "fast-check";
import React from "react";
import { renderToStaticMarkup } from "react-dom/server";

import { Activity, Registry } from "../../components/OperationalScreens";
import { ActionControl } from "../../components/projection/ActionControl";
import type {
  GeneratedActionReference,
  GeneratedJsonObject,
} from "../api/client";
import { ProjectionMapper } from "./ProjectionMapper";
import {
  mapGeneratedScreenProjection,
  selectGeneratedFilterOption,
} from "./screen-renderers";

const SENSITIVE_SENTINEL = "CLIENT_CREATED_SENTINEL";
const VALIDATION_CATEGORY_KEYS = [
  "version",
  "schema",
  "tool_policy",
  "budget",
  "verification",
  "rollback",
  "approval",
] as const;

interface ProvenanceCase {
  readonly registry: GeneratedJsonObject;
  readonly activity: GeneratedJsonObject;
  readonly graphValidation: GeneratedJsonObject;
  readonly filterOption: GeneratedJsonObject;
  readonly action: GeneratedActionReference;
  readonly immutableIdentifier: string;
  readonly version: string;
  readonly provenanceReference: string;
  readonly graphRevision: string;
  readonly commonVersions: string;
  readonly lifecycle: string;
  readonly dependency: string;
  readonly checkpoint: string;
  readonly retry: string;
  readonly failure: string;
  readonly recovery: string;
  readonly eventSummary: string;
  readonly correlationIdentifier: string;
  readonly validationCategoryValues: Readonly<Record<(typeof VALIDATION_CATEGORY_KEYS)[number], string>>;
}

const identifierArbitrary = fc.uuid().map((value: string): string => value.replaceAll("-", ""));
const returnedTextArbitrary = (prefix: string): fc.Arbitrary<string> => identifierArbitrary.map((value: string): string => `${prefix}-${value}`);
const lifecycleArbitrary = fc.constantFrom(
  "queued",
  "running",
  "self_refine",
  "waiting_for_critique",
  "blocked",
  "failed",
  "complete",
  "cancelling",
  "cancelled",
  "manual_recovery_required",
);

const provenanceCaseArbitrary = fc.tuple(
  returnedTextArbitrary("common"),
  returnedTextArbitrary("version"),
  returnedTextArbitrary("status"),
  returnedTextArbitrary("provenance"),
  returnedTextArbitrary("compatibility"),
  returnedTextArbitrary("metrics"),
  returnedTextArbitrary("filter"),
  returnedTextArbitrary("filter-label"),
  returnedTextArbitrary("filter-option"),
  returnedTextArbitrary("filter-value"),
  returnedTextArbitrary("action"),
  returnedTextArbitrary("action-label"),
  returnedTextArbitrary("graph"),
  returnedTextArbitrary("common-versions"),
  lifecycleArbitrary,
  returnedTextArbitrary("dependency"),
  returnedTextArbitrary("checkpoint"),
  returnedTextArbitrary("retry"),
  returnedTextArbitrary("failure"),
  returnedTextArbitrary("recovery"),
  returnedTextArbitrary("event"),
  returnedTextArbitrary("correlation"),
  returnedTextArbitrary("event-heading"),
  returnedTextArbitrary("validation-version"),
  returnedTextArbitrary("validation-schema"),
  returnedTextArbitrary("validation-tool-policy"),
  returnedTextArbitrary("validation-budget"),
  returnedTextArbitrary("validation-verification"),
  returnedTextArbitrary("validation-rollback"),
  returnedTextArbitrary("validation-approval"),
).map(([
  immutableIdentifier,
  version,
  status,
  provenanceReference,
  compatibility,
  metrics,
  filterId,
  filterLabel,
  filterOptionLabel,
  filterValue,
  actionId,
  actionLabel,
  graphRevision,
  commonVersions,
  lifecycle,
  dependency,
  checkpoint,
  retry,
  failure,
  recovery,
  eventSummary,
  correlationIdentifier,
  eventHeading,
  versionValidation,
  schemaValidation,
  toolPolicyValidation,
  budgetValidation,
  verificationValidation,
  rollbackValidation,
  approvalValidation,
]): ProvenanceCase => {
  const action: GeneratedActionReference = {
    id: actionId,
    label: actionLabel,
    eligible: true,
    kind: "recover",
    client_created_action_sentinel: SENSITIVE_SENTINEL,
  };
  const filterOption: GeneratedJsonObject = {
    label: filterOptionLabel,
    value: filterValue,
    client_created_filter_sentinel: SENSITIVE_SENTINEL,
  };
  const validationCategoryValues = {
    version: versionValidation,
    schema: schemaValidation,
    tool_policy: toolPolicyValidation,
    budget: budgetValidation,
    verification: verificationValidation,
    rollback: rollbackValidation,
    approval: approvalValidation,
  } as const;

  return {
    registry: {
      immutable_identifier: immutableIdentifier,
      version,
      status,
      provenance_reference: provenanceReference,
      compatibility_state: compatibility,
      aggregate_metrics: metrics,
      filters: [{ id: filterId, label: filterLabel, options: [filterOption] }],
      action_references: [action],
      client_created_registry_sentinel: SENSITIVE_SENTINEL,
    },
    activity: {
      graph_revision: graphRevision,
      common_versions: commonVersions,
      lifecycle,
      dependency,
      checkpoint,
      retry,
      failure,
      recovery,
      sections: [{
        heading: eventHeading,
        summary: eventSummary,
        correlation_identifier: correlationIdentifier,
        action_references: [action],
        client_created_event_sentinel: SENSITIVE_SENTINEL,
      }],
      action_references: [action],
      client_created_activity_sentinel: SENSITIVE_SENTINEL,
    },
    graphValidation: {
      ...validationCategoryValues,
      client_created_validation_sentinel: SENSITIVE_SENTINEL,
    },
    filterOption,
    action,
    immutableIdentifier,
    version,
    provenanceReference,
    graphRevision,
    commonVersions,
    lifecycle,
    dependency,
    checkpoint,
    retry,
    failure,
    recovery,
    eventSummary,
    correlationIdentifier,
    validationCategoryValues,
  };
});

function requiredItem<T>(items: readonly T[], description: string): T {
  const item = items[0];
  if (item === undefined) throw new Error(`Expected ${description}.`);
  return item;
}

function assertReturnedProvenance(item: ProvenanceCase): void {
  const registry = mapGeneratedScreenProjection("registry", item.registry);
  assert.deepEqual(registry.fields.fields, {
    immutable_identifier: item.immutableIdentifier,
    version: item.version,
    status: item.registry.status,
    provenance_reference: item.provenanceReference,
    compatibility_state: item.registry.compatibility_state,
    aggregate_metrics: item.registry.aggregate_metrics,
  });

  const filter = requiredItem(registry.filters, "a generated registry filter");
  assert.strictEqual(requiredItem(filter.options, "a generated filter option").source, item.filterOption);
  assert.strictEqual(selectGeneratedFilterOption(filter, String(item.filterOption.value)), item.filterOption);
  assert.equal(selectGeneratedFilterOption(filter, "client-created-value"), undefined);

  const registryAction = requiredItem(registry.actions, "a returned registry action");
  assert.strictEqual(registryAction.source, item.action);
  let invokedAction: GeneratedActionReference | undefined;
  const control = ActionControl({
    action: registryAction,
    stale: false,
    onInvoke: (action: GeneratedActionReference): void => { invokedAction = action; },
  });
  control.props.onClick();
  assert.strictEqual(invokedAction, item.action);

  const activity = mapGeneratedScreenProjection("activity", item.activity);
  assert.deepEqual(activity.fields.fields, {
    graph_revision: item.graphRevision,
    common_versions: item.commonVersions,
    lifecycle: item.lifecycle,
    dependency: item.dependency,
    checkpoint: item.checkpoint,
    retry: item.retry,
    failure: item.failure,
    recovery: item.recovery,
  });
  const event = requiredItem(activity.sections, "a returned operational event");
  assert.equal(event.fields.find((field) => field.key === "summary")?.value, item.eventSummary);
  assert.equal(event.fields.find((field) => field.key === "correlation_identifier")?.value, item.correlationIdentifier);
  assert.strictEqual(requiredItem(event.actions, "a returned event action").source, item.action);

  const graphValidation = new ProjectionMapper().map(item.graphValidation, VALIDATION_CATEGORY_KEYS);
  assert.deepEqual(graphValidation.fields, item.validationCategoryValues);

  const registryMarkup = renderToStaticMarkup(<Registry
    projection={item.registry}
    onAction={(): void => undefined}
    onEvidence={(): void => undefined}
    onFilterChange={(): void => undefined}
    onReference={(): void => undefined}
  />);
  const activityMarkup = renderToStaticMarkup(<Activity
    projection={item.activity}
    onAction={(): void => undefined}
    onEvidence={(): void => undefined}
    onFilterChange={(): void => undefined}
    onReference={(): void => undefined}
  />);
  assert.match(registryMarkup, new RegExp(`data-action-reference-id=\"${item.action.id}\"`));
  assert.match(activityMarkup, new RegExp(`data-action-reference-id=\"${item.action.id}\"`));
  assert.doesNotMatch(`${registryMarkup}${activityMarkup}`, new RegExp(SENSITIVE_SENTINEL));
}

// Feature: frontend-redesign, Property 9: Common registry, activity, and graph metadata preserve returned provenance
// Validates: Requirements 6.2, 6.3, 6.5, 6.6, 6.7, 6.13, 6.16
test("Property 9: preserves generated common, activity, graph-validation, filter, event, and action provenance", (): void => {
  fc.assert(fc.property(provenanceCaseArbitrary, assertReturnedProvenance), { numRuns: 100 });
});
