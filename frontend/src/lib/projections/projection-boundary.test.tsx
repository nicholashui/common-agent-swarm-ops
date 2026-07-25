import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import { renderToStaticMarkup } from "react-dom/server";

import { ActionControl } from "../../components/projection/ActionControl";
import { CopyCorrelationIdentifierButton } from "../../components/projection/CopyCorrelationIdentifierButton";
import { EvidenceLink } from "../../components/projection/EvidenceLink";
import { ReferenceLink } from "../../components/projection/ReferenceLink";
import type { GeneratedActionReference, GeneratedJsonObject } from "../api/client";
import { BrowserSessionSafeCache } from "../session/session-safe-cache";
import { ProjectionMapper, type GeneratedEvidenceReference, type GeneratedOpaqueReference } from "./ProjectionMapper";

interface RedactionFixture { readonly fixtureVersion: string; readonly projection: GeneratedJsonObject; readonly allowedFields: readonly string[]; }
interface ReferenceFixture { readonly fixtureVersion: string; readonly opaque: GeneratedOpaqueReference; readonly action: GeneratedActionReference; readonly evidence: GeneratedEvidenceReference; }
const FIXTURES = resolve(dirname(fileURLToPath(import.meta.url)), "../../test/fixtures/frontend-redesign/v1");
async function fixture<T>(name: string): Promise<T> { return JSON.parse(await readFile(resolve(FIXTURES, name), "utf8")) as T; }

test("mapper and session-safe cache omit absent protected and sensitive fixture fields", async () => {
  const redaction = await fixture<RedactionFixture>("projection-redaction.json");
  const mapper = new ProjectionMapper();
  const view = mapper.map(redaction.projection, redaction.allowedFields);
  const cache = new BrowserSessionSafeCache({ sessionVersion: "fixture", allowlist: [{ key: "run", projectionFields: redaction.allowedFields }] });
  cache.write("run", { projection: redaction.projection, eventCursor: "event-1" });
  assert.equal(redaction.fixtureVersion, "frontend-redesign/v1");
  assert.deepEqual(view.fields, { status: "queued", summary: "Safe returned summary" });
  assert.doesNotMatch(JSON.stringify({ view, cached: cache.read("run") }), /PROTECTED_SENTINEL|RAW_SENTINEL|TRACE_SENTINEL/);
});

test("reference controls and correlation copy preserve only returned fixture origins", async () => {
  const references = await fixture<ReferenceFixture>("reference-origin.json");
  const mapper = new ProjectionMapper();
  const opaque = mapper.mapOpaqueReference(references.opaque); const action = mapper.mapActionReference(references.action); const evidence = mapper.mapEvidenceReference(references.evidence, ["summary"]);
  assert.ok(opaque !== null && action !== null && evidence !== null);
  let resolved: GeneratedOpaqueReference | undefined; let invoked: GeneratedActionReference | undefined; let selected: GeneratedEvidenceReference | undefined; let copied = "";
  const originalNavigator = Object.getOwnPropertyDescriptor(globalThis, "navigator");
  Object.defineProperty(globalThis, "navigator", { configurable: true, value: { clipboard: { writeText: (value: string): Promise<void> => { copied = value; return Promise.resolve(); } } } });
  try {
    const opaqueControl = ReferenceLink({ reference: opaque, onResolve: (value): void => { resolved = value; } });
    const actionControl = ActionControl({ action, stale: false, onInvoke: (value): void => { invoked = value; } });
    const evidenceControl = EvidenceLink({ evidence, onSelect: (value): void => { selected = value; } });
    const copyControl = CopyCorrelationIdentifierButton({ correlationIdentifier: "corr-fixture-1" });
    const copyMarkup = renderToStaticMarkup(copyControl);
    opaqueControl.props.onClick(); actionControl.props.onClick(); evidenceControl.props.onClick(); copyControl.props.onClick(); await Promise.resolve();
    assert.match(copyMarkup, /aria-label="Copy correlation identifier"/);
    assert.strictEqual(resolved, references.opaque); assert.strictEqual(invoked, references.action); assert.strictEqual(selected, references.evidence); assert.equal(copied, "corr-fixture-1");
  } finally { if (originalNavigator === undefined) Reflect.deleteProperty(globalThis, "navigator"); else Object.defineProperty(globalThis, "navigator", originalNavigator); }
});
