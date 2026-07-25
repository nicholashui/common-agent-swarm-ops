import assert from "node:assert/strict";
import test from "node:test";

import fc from "fast-check";
import React from "react";
import { renderToStaticMarkup } from "react-dom/server";

import type { OpaqueReferenceView } from "../../lib/projections/ProjectionMapper";
import {
  ImportProjection,
  IngestionRequirementSummary,
  submitAuthorizedIngestion,
  type GeneratedAuthorizedIngestionContract,
  type IngestionIntent,
  type ImportState,
} from "./IngestionForms";
import { SafeContent } from "./SafeContent";

const IMPORT_STATES: readonly ImportState[] = ["validating", "quarantined", "processing", "indexed", "rejected", "archived"];
const hostileTextArbitrary = fc.tuple(
  fc.constantFrom("<script>alert('x')</script>", "<img src=x onerror=alert(1)>", "javascript:alert(1)", "密碼 🔒 \\u202E"),
  fc.string({ maxLength: 64 }),
).map(([prefix, suffix]: [string, string]): string => `${prefix}${suffix}`);
const identifierArbitrary = fc.uuid().map((value: string): string => value.replaceAll("-", ""));
const externalUrlArbitrary = fc.tuple(fc.constantFrom("https", "http"), identifierArbitrary, hostileTextArbitrary)
  .map(([scheme, identifier, hostile]: [string, string, string]): string => `${scheme}://external-${identifier}.example/import?payload=${encodeURIComponent(hostile)}`);

interface Scenario {
  readonly content: string;
  readonly externalUrl: string;
  readonly state: ImportState;
  readonly requirements: { readonly fileTypes: readonly string[]; readonly maximumSizeBytes: number; readonly ownershipRequirement: string; readonly retentionRequirement: string };
  readonly reference: OpaqueReferenceView;
}

const scenarioArbitrary: fc.Arbitrary<Scenario> = fc.tuple(hostileTextArbitrary, externalUrlArbitrary, fc.constantFrom(...IMPORT_STATES), identifierArbitrary, fc.integer({ min: 0, max: Number.MAX_SAFE_INTEGER }))
  .map(([content, externalUrl, state, identifier, maximumSizeBytes]): Scenario => ({
    content,
    externalUrl,
    state,
    requirements: { fileTypes: [`application/x-${identifier}`], maximumSizeBytes, ownershipRequirement: `owner-${identifier}`, retentionRequirement: `retain-${identifier}` },
    reference: { id: `import-${identifier}`, label: `Import ${identifier}`, source: { id: `import-${identifier}`, label: `Import ${identifier}`, protected_detail: `private-${identifier}` } },
  }));

interface BrowserSideEffectSpies {
  readonly networkUrls: string[];
  readonly navigationUrls: string[];
  readonly dynamicEvaluations: string[];
  readonly fetch: typeof fetch;
  readonly window: { readonly open: (url?: string | URL) => null; readonly location: { readonly assign: (url: string) => void; readonly replace: (url: string) => void } };
}

interface BrowserGlobals { fetch: typeof fetch; window?: BrowserSideEffectSpies["window"]; eval: (source: string) => unknown; }

function createBrowserSideEffectSpies(): BrowserSideEffectSpies {
  const networkUrls: string[] = [];
  const navigationUrls: string[] = [];
  const dynamicEvaluations: string[] = [];
  return {
    networkUrls,
    navigationUrls,
    dynamicEvaluations,
    fetch: async (input: RequestInfo | URL): Promise<Response> => { networkUrls.push(String(input)); throw new TypeError("Browser network access is forbidden in this property test."); },
    window: {
      open: (url?: string | URL): null => { navigationUrls.push(String(url ?? "")); return null; },
      location: { assign: (url: string): void => { navigationUrls.push(url); }, replace: (url: string): void => { navigationUrls.push(url); } },
    },
  };
}

async function withBrowserSideEffectSpies(run: (spies: BrowserSideEffectSpies) => Promise<void>): Promise<void> {
  const browser = globalThis as unknown as BrowserGlobals;
  const originalFetch = browser.fetch;
  const originalWindow = browser.window;
  const originalEval = browser.eval;
  const spies = createBrowserSideEffectSpies();
  browser.fetch = spies.fetch;
  browser.window = spies.window;
  browser.eval = (source: string): undefined => { spies.dynamicEvaluations.push(source); return undefined; };
  try {
    await run(spies);
  } finally {
    browser.fetch = originalFetch;
    browser.window = originalWindow;
    browser.eval = originalEval;
  }
}

// Feature: frontend-redesign, Property 12: Artifact and import content is inert and non-authoritative
// Validates: Requirements 8.1, 8.4, 8.6, 8.7, 8.8
test("Property 12: keeps arbitrary artifact and import content inert and non-authoritative", async (): Promise<void> => {
  await fc.assert(fc.asyncProperty(scenarioArbitrary, async (scenario: Scenario): Promise<void> => {
    await withBrowserSideEffectSpies(async (spies: BrowserSideEffectSpies): Promise<void> => {
      const intent: IngestionIntent = { kind: "knowledge", content: { value: scenario.content }, externalImportUrl: { value: scenario.externalUrl } };
      const submittedIntents: IngestionIntent[] = [];
      const contract: GeneratedAuthorizedIngestionContract = {
        operationId: "handoff_video_artifact_api_v1_video_artifacts_post",
        submit: async (submitted: IngestionIntent): Promise<void> => { submittedIntents.push(submitted); },
      };
      const markup = renderToStaticMarkup(<main><IngestionRequirementSummary requirements={scenario.requirements} /><ImportProjection onResolveReference={(): void => undefined} projection={{ state: scenario.state, references: [scenario.reference], scanResult: scenario.content, indexingResult: scenario.content }} /><SafeContent content={{ value: scenario.content, externalImportUrl: scenario.externalUrl }} /></main>);

      assert.match(markup, new RegExp(`data-import-state="${scenario.state}"`));
      assert.equal(markup.includes(scenario.requirements.fileTypes[0]!), true);
      assert.equal(markup.includes(`${scenario.requirements.maximumSizeBytes} bytes`), true);
      assert.equal(markup.includes(scenario.requirements.ownershipRequirement), true);
      assert.equal(markup.includes(scenario.requirements.retentionRequirement), true);
      assert.equal(markup.includes(scenario.reference.label), true);
      assert.doesNotMatch(markup, /<(?:script|iframe|img|object|embed|link)\b/i);
      assert.doesNotMatch(markup, /<[^>]+\s(?:href|src|action)=/i);
      assert.doesNotMatch(markup, /<[^>]+\son\w+=/i);
      assert.equal(await submitAuthorizedIngestion(contract, intent), true);
      assert.deepEqual(submittedIntents, [intent]);
      assert.deepEqual(spies.networkUrls, []);
      assert.deepEqual(spies.navigationUrls, []);
      assert.deepEqual(spies.dynamicEvaluations, []);
    });
  }), { numRuns: 100 });
});
