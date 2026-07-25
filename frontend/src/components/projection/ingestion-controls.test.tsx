import assert from "node:assert/strict";
import test from "node:test";

import React from "react";
import { renderToStaticMarkup } from "react-dom/server";

import type { GeneratedActionReference, GeneratedJsonObject } from "../../lib/api/client";
import { VaProjectionScreen } from "../KnowledgeArtifactScreens";
import { mapArtifactProjection, mapVaProjection } from "../../lib/projections/va-adapters";
import {
  ImportProjection,
  IngestionRequirementSummary,
  correctableIngestionIssue,
  submitAuthorizedIngestion,
  type GeneratedAuthorizedIngestionContract,
} from "./IngestionForms";
import { ExternalNavigationControl, SafeContent, inertText, mapAllowedActionContract } from "./SafeContent";

const requirements = {
  fileTypes: ["text/plain", "application/pdf"],
  maximumSizeBytes: 4096,
  ownershipRequirement: "A returned owner is required.",
  retentionRequirement: "Retain for 30 days.",
} as const;

test("ingestion controls render only returned requirements and import projection fields", () => {
  const markup = renderToStaticMarkup(<><IngestionRequirementSummary requirements={requirements} /><ImportProjection onResolveReference={(): void => {}} projection={{
    state: "quarantined",
    references: [{ id: "import-1", label: "Imported record", source: { id: "import-1", label: "Imported record" } }],
    scanResult: "Redacted scan result",
  }} /></>);
  assert.match(markup, /text\/plain, application\/pdf/);
  assert.match(markup, /4096 bytes/);
  assert.match(markup, /Import state: quarantined/);
  assert.match(markup, /Imported record/);
  assert.doesNotMatch(markup, /processing|indexed|rejected|archived/);
});

test("untrusted content is escaped and client correction feedback is non-authoritative", () => {
  const untrustedMarkup = '<img src="https://untrusted.example" onerror="alert(1)">';
  const markup = renderToStaticMarkup(<SafeContent content={untrustedMarkup} />);
  assert.equal(inertText(untrustedMarkup), untrustedMarkup);
  assert.match(markup, /&lt;img/);
  assert.doesNotMatch(markup, /<img/);
  assert.deepEqual(correctableIngestionIssue("", "not a URL"), {
    message: "Check the external import URL format before submitting.", authority: "non-authoritative",
  });
});

test("ingestion cannot submit without a generated authorized contract", async () => {
  const intent = { kind: "knowledge" as const, content: { value: "safe text" }, externalImportUrl: { value: "https://untrusted.example/import" } };
  assert.equal(await submitAuthorizedIngestion(undefined, intent), false);

  let submittedIntent: unknown;
  const contract: GeneratedAuthorizedIngestionContract = {
    operationId: "handoff_video_artifact_api_v1_video_artifacts_post",
    submit: async (submitted): Promise<void> => { submittedIntent = submitted; },
  };
  assert.equal(await submitAuthorizedIngestion(contract, intent), true);
  assert.strictEqual(submittedIntent, intent);
});

test("external navigation needs an explicit returned allowed action contract", () => {
  const returnedAction: GeneratedActionReference = {
    id: "external-1",
    label: "Open reviewed destination",
    kind: "external_navigation",
    allowed: true,
    destination: "https://approved.example/resource",
    open_in_new_context: true,
  };
  const contract = mapAllowedActionContract(returnedAction);
  assert.ok(contract !== null);
  const enabledMarkup = renderToStaticMarkup(<ExternalNavigationControl action={contract} />);
  assert.match(enabledMarkup, /href="https:\/\/approved.example\/resource"/);
  assert.match(enabledMarkup, /target="_blank"/);
  assert.match(enabledMarkup, /rel="noopener noreferrer"/);

  const deniedAction: GeneratedJsonObject = { ...returnedAction, allowed: false };
  assert.equal(mapAllowedActionContract(deniedAction), null);
  const blockedMarkup = renderToStaticMarkup(<ExternalNavigationControl action={null} />);
  assert.match(blockedMarkup, /disabled/);
  assert.doesNotMatch(blockedMarkup, /approved\.example/);
});

test("external navigation revalidates its source contract and rejects unsafe destinations", () => {
  const returnedAction: GeneratedActionReference = {
    id: "external-2",
    label: "Open reviewed destination",
    kind: "external_navigation",
    allowed: true,
    destination: "https://approved.example/resource",
    open_in_new_context: false,
  };
  const contract = mapAllowedActionContract(returnedAction);
  assert.ok(contract !== null);
  const forgedAction = { ...contract, destination: "https://attacker.example/redirect", label: "Open attacker" };
  const markup = renderToStaticMarkup(<ExternalNavigationControl action={forgedAction} />);
  assert.match(markup, /href="https:\/\/approved\.example\/resource"/);
  assert.match(markup, />Open reviewed destination</);
  assert.doesNotMatch(markup, /attacker\.example|Open attacker/);

  const unsafeAction: GeneratedActionReference = { ...returnedAction, destination: "javascript:alert(1)" };
  assert.equal(mapAllowedActionContract(unsafeAction), null);
});

test("artifact adapter blocks delivery when returned delivery data or gate approval is missing", () => {
  const artifact = mapArtifactProjection({
    artifact_version: "artifact-v2",
    parent_lineage: [{ id: "parent-1", label: "Parent artifact" }],
    rights_and_consent_state: "approved",
    continuity_state: "continuity-retained",
    quality_control_state: "passed",
    delivery_state: "ready",
    delivery_targets: ["review-channel"],
    provenance_reference: "prov-artifact-v2",
  });
  assert.equal(artifact.deliveryBlocked, true);
  assert.deepEqual(artifact.deliveryBlockReasons, ["missing_gate_approval"]);
  assert.equal(artifact.parentLineage[0] && typeof artifact.parentLineage[0] === "object" ? artifact.parentLineage[0].label : undefined, "Parent artifact");
});

test("conditional VA renderer shows returned domain data and routes returned actions", () => {
  const action: GeneratedActionReference = { id: "va-action-1", label: "Evaluate returned run", eligible: true, kind: "evaluate" };
  const projection: GeneratedJsonObject = {
    va_projection: {
      template: "Template C",
      production_phase: "Editorial review",
      common_pattern_version: "pattern-v3",
      common_agent_versions: [{
        canonical_identity: "Verifier",
        boundaries: "Review only",
        responsibilities: ["Compare returned evidence"],
        runtime_policy: { max_iterations: 3 },
        quality_rubric: { threshold: 0.8 },
        critique_relationships: ["Writer"],
        provenance_policy: ["retain-run-reference"],
        agent_version_id: "agent-v4",
      }],
      agent_tasks: [{
        task_id: "task-1",
        graph_revision: "graph-v7",
        dependencies: ["task-0"],
        approval_gate_ids: ["gate-1"],
        lifecycle_state: "waiting_for_critique",
        recovery_state: "retryable",
        budget: { budget_remaining: "10 credits" },
        checkpoint_reference: "checkpoint-1",
        pinned_agent_version_id: "agent-v4",
      }],
      artifact_handoffs: [{
        artifact_version: "artifact-v2",
        parent_lineage: ["artifact-v1"],
        rights_and_consent_state: "approved",
        continuity_state: "retained",
        quality_control_state: "passed",
        delivery_state: "ready",
        delivery_targets: ["review-channel"],
        provenance_reference: "prov-v2",
        gate_approval: "approved",
      }],
      critique_records: [{ critique_state: "open", source_reference: "agent-v4", target_task_id: "task-1", message: "Returned critique", submitted_at: "2026-01-01T00:00:00Z" }],
      quality_evidence: [{ kind: "l2_role_rubric_evaluation", evidence_reference: "evidence-2", passed: true }],
      approval_gates: [{ status: "approved", evidence_revision: "revision-4", action_references: [action] }],
      pinned_provenance: { graph_revision_id: "graph-v7" },
      action_references: [action],
    },
    protected_detail: "must-not-render",
  };
  const returnedActions: GeneratedActionReference[] = [];
  const mapped = mapVaProjection(projection);
  assert.ok(mapped !== undefined);
  assert.equal(mapped.template, "Template C");
  assert.equal(mapped.tasks[0]?.lifecycle, "waiting_for_critique");
  assert.equal(mapped.artifacts[0]?.deliveryBlocked, false);
  const markup = renderToStaticMarkup(<VaProjectionScreen onAction={(returned): void => { returnedActions.push(returned); }} projection={projection} />);
  assert.match(markup, /Template C|Editorial review|waiting_for_critique|Rights and consent|l2_role_rubric_evaluation/);
  assert.doesNotMatch(markup, /must-not-render/);
  assert.match(markup, /data-action-reference-id="va-action-1"/);
  assert.deepEqual(returnedActions, []);
});

test("absent VA data keeps the common projection without VA placeholders", () => {
  const projection: GeneratedJsonObject = {
    graph_revision: "graph-common-v2",
    governance_status: "returned-governance",
    provenance_reference: "returned-provenance",
    graph: { graph_revision: "graph-common-v2", nodes: [{ id: "node-1", label: "Common node", kind: "common", immutable_version: "common-v2", provenance_reference: "returned-provenance", task: { lifecycle: "complete" } }], edges: [] },
  };
  const markup = renderToStaticMarkup(<VaProjectionScreen projection={projection} />);
  assert.match(markup, /graph-common-v2|returned-governance|returned-provenance|Common node/);
  assert.doesNotMatch(markup, /VA DOMAIN ADAPTER|Returned production projection|Template C/);
});

test("unavailable approval data retains returned VA data and exposes Unavailable_State", () => {
  const projection: GeneratedJsonObject = {
    va_projection: {
      template: "Template A",
      common_agent_versions: [{ canonical_identity: "Returned agent", agent_version_id: "agent-v1" }],
      artifact_handoffs: [{ artifact_version: "artifact-v1", delivery_state: "ready" }],
      approval_gates: [{ criteria: ["returned criterion"] }],
    },
  };
  const markup = renderToStaticMarkup(<VaProjectionScreen projection={projection} />);
  assert.match(markup, /Template A|Returned agent|artifact-v1|Unavailable_State/);
  assert.match(markup, /data-approval-gate-unavailable="true"/);
});
