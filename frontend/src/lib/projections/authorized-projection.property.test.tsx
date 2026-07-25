import assert from "node:assert/strict";
import test from "node:test";

import fc from "fast-check";
import React from "react";
import { renderToStaticMarkup } from "react-dom/server";

import { ActionControl } from "../../components/projection/ActionControl";
import { EvidenceLink } from "../../components/projection/EvidenceLink";
import type { GeneratedActionReference, GeneratedJsonObject, GeneratedJsonValue } from "../api/client";
import { BrowserSessionSafeCache, type SessionStorageLike } from "../session/session-safe-cache";
import { ProjectionMapper } from "./ProjectionMapper";

const PRESENTABLE_FIELDS = ["name", "status", "summary"] as const;
type PresentableField = (typeof PRESENTABLE_FIELDS)[number];
interface MutableGeneratedJsonObject { [key: string]: GeneratedJsonValue; }

interface ReferenceSubset {
  readonly allActions: readonly GeneratedActionReference[];
  readonly allEvidence: readonly GeneratedJsonObject[];
  readonly actions: readonly GeneratedActionReference[];
  readonly evidence: readonly GeneratedJsonObject[];
}

class MemoryStorage implements SessionStorageLike {
  private readonly values = new Map<string, string>();

  public getItem(key: string): string | null {
    return this.values.get(key) ?? null;
  }

  public setItem(key: string, value: string): void {
    this.values.set(key, value);
  }

  public removeItem(key: string): void {
    this.values.delete(key);
  }

  public serializedValues(): readonly string[] {
    return [...this.values.values()];
  }
}

const identifierArbitrary = fc.uuid().map((value: string): string => value.replaceAll("-", ""));
const sensitiveSentinelArbitrary = identifierArbitrary.map((value: string): string => `SENSITIVE_${value}`);

const actionReferenceArbitrary = fc.tuple(identifierArbitrary, sensitiveSentinelArbitrary, fc.boolean())
  .map(([id, sensitive, eligible]): GeneratedActionReference => ({
    id: `action-${id}`,
    label: `Action ${id}`,
    eligible,
    private_trace: sensitive,
  }));

const evidenceReferenceArbitrary = fc.tuple(identifierArbitrary, sensitiveSentinelArbitrary)
  .map(([id, sensitive]): GeneratedJsonObject => ({
    id: `evidence-${id}`,
    label: `Evidence ${id}`,
    summary: `Summary ${id}`,
    protected_detail: sensitive,
  }));

const referenceSubsetArbitrary: fc.Arbitrary<ReferenceSubset> = fc.tuple(
  fc.uniqueArray(actionReferenceArbitrary, { maxLength: 3, selector: (reference: GeneratedActionReference): string => String(reference.id) }),
  fc.uniqueArray(evidenceReferenceArbitrary, { maxLength: 3, selector: (reference: GeneratedJsonObject): string => String(reference.id) }),
).chain(([allActions, allEvidence]) => fc.tuple(fc.subarray(allActions), fc.subarray(allEvidence))
  .map(([actions, evidence]): ReferenceSubset => ({ allActions, allEvidence, actions, evidence })));

// Feature: frontend-redesign, Property 2: Authorized projection rendering has no client-created data or authority
// Validates: Requirements 2.2, 2.3, 2.4, 2.7, 2.8, 2.9
test("Property 2: authorized projection rendering has no client-created data or authority", () => {
  fc.assert(fc.property(
    fc.subarray([...PRESENTABLE_FIELDS]),
    fc.array(identifierArbitrary, { minLength: PRESENTABLE_FIELDS.length, maxLength: PRESENTABLE_FIELDS.length }),
    fc.array(sensitiveSentinelArbitrary, { minLength: 3, maxLength: 3 }),
    referenceSubsetArbitrary,
    (presentFields: readonly PresentableField[], fieldValues, sensitiveValues, references): void => {
      const projection: MutableGeneratedJsonObject = {
        access_token: sensitiveValues[0]!,
        internal_trace: sensitiveValues[1]!,
        protected_field: sensitiveValues[2]!,
      };
      for (const [index, field] of presentFields.entries()) projection[field] = `VALUE_${field}_${fieldValues[index]}`;

      const mapper = new ProjectionMapper();
      const view = mapper.map(projection, PRESENTABLE_FIELDS);
      assert.deepEqual(Object.keys(view.fields).sort(), [...presentFields].sort());
      for (const field of PRESENTABLE_FIELDS) assert.equal(mapper.hasField(view, field), presentFields.includes(field));

      const persistence = new MemoryStorage();
      const cache = new BrowserSessionSafeCache({
        sessionVersion: "property-2",
        allowlist: [{ key: "projection", projectionFields: PRESENTABLE_FIELDS }],
        persistence,
      });
      cache.write("projection", { projection, eventCursor: null });
      assert.deepEqual(cache.read("projection")?.projection, view.fields);
      const serializedCache = persistence.serializedValues();
      assert.equal(serializedCache.length, 1);
      for (const sensitiveValue of sensitiveValues) assert.equal(serializedCache[0]!.includes(sensitiveValue), false);

      const actions = references.actions.map((reference) => {
        const action = mapper.mapActionReference(reference);
        assert.ok(action !== null);
        assert.strictEqual(action.source, reference);
        return action;
      });
      const evidence = references.evidence.map((reference) => {
        const item = mapper.mapEvidenceReference(reference, ["summary"]);
        assert.ok(item !== null);
        assert.strictEqual(item.source, reference);
        return item;
      });

      const actionPayloads: GeneratedActionReference[] = [];
      const evidencePayloads: GeneratedJsonObject[] = [];
      const markup = renderToStaticMarkup(<main>
        {PRESENTABLE_FIELDS.map((field) => mapper.hasField(view, field)
          ? <span data-projection-field={field} key={field}>{String(view.fields[field])}</span>
          : null)}
        {actions.map((action, index) => <ActionControl action={action!} key={`action-${index}`} onInvoke={(reference): void => { actionPayloads.push(reference); }} stale={false} />)}
        {evidence.map((item, index) => <EvidenceLink evidence={item!} key={`evidence-${index}`} onSelect={(reference): void => { evidencePayloads.push(reference); }} />)}
      </main>);

      for (const sensitiveValue of sensitiveValues) assert.equal(markup.includes(sensitiveValue), false);
      for (const field of PRESENTABLE_FIELDS) {
        const renderedValue = String(view.fields[field]);
        assert.equal(markup.includes(renderedValue), presentFields.includes(field));
      }
      for (const reference of references.allActions) {
        assert.equal(markup.includes(`data-action-reference-id="${reference.id}"`), references.actions.includes(reference));
        assert.equal(markup.includes(String(reference.private_trace)), false);
      }
      for (const reference of references.allEvidence) {
        assert.equal(markup.includes(`data-evidence-reference-id="${reference.id}"`), references.evidence.includes(reference));
        assert.equal(markup.includes(String(reference.protected_detail)), false);
      }

      actions.forEach((action, index) => {
        const control = ActionControl({ action: action!, stale: false, onInvoke: (reference): void => { actionPayloads.push(reference); } });
        control.props.onClick();
        if (action!.eligible) assert.strictEqual(actionPayloads.at(-1), references.actions[index]);
      });
      evidence.forEach((item, index) => {
        const control = EvidenceLink({ evidence: item!, onSelect: (reference): void => { evidencePayloads.push(reference); } });
        control.props.onClick();
        assert.strictEqual(evidencePayloads.at(-1), references.evidence[index]);
      });
    },
  ), { numRuns: 100 });
});