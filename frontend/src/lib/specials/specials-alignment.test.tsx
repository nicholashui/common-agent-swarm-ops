/**
 * Alignment gate for docs/special_agents_redesign/agents/*.md
 * ↔ business/specials pack ↔ frontend catalog.
 */
import assert from "node:assert/strict";
import { readdir, readFile } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import React from "react";
import { renderToStaticMarkup } from "react-dom/server";

import { SpecialsCatalog } from "../../components/SpecialsCatalog";
import {
  SPECIAL_AGENT_CATALOG,
  SPECIAL_AGENT_CATALOG_COUNT,
  isSpecialsCatalogFailClosed,
  specialAgentIds,
} from "./specials-catalog";

const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), "../../../..");
const docsAgents = resolve(repoRoot, "docs/special_agents_redesign/agents");
const specialsRoot = resolve(repoRoot, "business/specials");

test("specials catalog has exact 19 fail-closed draft agents", (): void => {
  assert.equal(SPECIAL_AGENT_CATALOG.length, SPECIAL_AGENT_CATALOG_COUNT);
  assert.equal(specialAgentIds().length, 19);
  assert.equal(isSpecialsCatalogFailClosed(), true);
  for (const entry of SPECIAL_AGENT_CATALOG) {
    assert.match(entry.agentId, /^specials\.[a-z0-9]+(?:-[a-z0-9]+)*$/);
    assert.equal(entry.status, "draft");
    assert.equal(entry.activation, "non_active");
    assert.equal(entry.productionActivationRequested, false);
    assert.equal(entry.networkAccess, false);
    assert.deepEqual(entry.allowedTools, []);
    assert.equal(entry.provider, "local_deterministic");
  }
});

test("every specials redesign doc maps to one pack agent and source record", async () => {
  const docs = (await readdir(docsAgents))
    .filter((name) => name.endsWith(".md"))
    .sort();
  assert.equal(docs.length, 19);

  const manifest = JSON.parse(
    await readFile(join(specialsRoot, "manifest.json"), "utf8"),
  ) as {
    readonly agents: readonly {
      readonly agent_id: string;
      readonly status: string;
      readonly production_activation_requested: boolean;
      readonly allowed_tools: readonly unknown[];
      readonly agent_spec_path: string;
    }[];
    readonly production_activation_requested: boolean;
  };

  assert.equal(manifest.agents.length, 19);
  assert.equal(manifest.production_activation_requested, false);

  const catalogBySource = new Map(
    SPECIAL_AGENT_CATALOG.map((entry) => [entry.sourcePath.split("/").pop(), entry]),
  );

  for (const doc of docs) {
    const entry = catalogBySource.get(doc);
    assert.ok(entry, `catalog missing mapping for ${doc}`);
    assert.equal(entry.sourcePath, `docs/special_agents_redesign/agents/${doc}`);

    const packAgent = manifest.agents.find((agent) => agent.agent_id === entry.agentId);
    assert.ok(packAgent, `manifest missing ${entry.agentId}`);
    assert.equal(packAgent.status, "draft");
    assert.equal(packAgent.production_activation_requested, false);
    assert.deepEqual(packAgent.allowed_tools, []);

    const specPath = join(specialsRoot, packAgent.agent_spec_path);
    const spec = JSON.parse(await readFile(specPath, "utf8")) as {
      readonly agent_id: string;
      readonly status: string;
      readonly production_activation_requested: boolean;
      readonly allowed_tools: readonly unknown[];
      readonly model_policy: { readonly network_access: boolean; readonly provider: string };
    };
    assert.equal(spec.agent_id, entry.agentId);
    assert.equal(spec.status, "draft");
    assert.equal(spec.production_activation_requested, false);
    assert.deepEqual(spec.allowed_tools, []);
    assert.equal(spec.model_policy.network_access, false);
    assert.equal(spec.model_policy.provider, "local_deterministic");

    const sourceRecordPath = join(
      specialsRoot,
      "governance/source-records",
      `${entry.agentId}.json`,
    );
    const sourceRecord = JSON.parse(await readFile(sourceRecordPath, "utf8")) as {
      readonly source_path: string;
      readonly agent_id: string;
    };
    assert.equal(sourceRecord.agent_id, entry.agentId);
    assert.equal(sourceRecord.source_path, entry.sourcePath);
  }
});

test("SpecialsCatalog UI presents draft/non-active and never production activation", (): void => {
  const markup = renderToStaticMarkup(<SpecialsCatalog />);
  assert.match(markup, /Special Agents Pack/);
  assert.match(markup, /19/);
  assert.match(markup, /specials\.aesthetics-agent/);
  assert.match(markup, /specials\.controller-agent/);
  assert.match(markup, /specials\.techology-advisor-agent/);
  assert.match(markup, /draft · non-active/);
  assert.match(markup, /production activation requested: no/);
  assert.match(markup, /untrusted design provenance/i);
  assert.doesNotMatch(markup, /production-ready|114 agents active|migration complete/i);
  assert.doesNotMatch(markup, /production_activation_requested:\s*yes/i);
});

test("specials pack has no executable workflows under business/specials", async () => {
  async function walk(directory: string): Promise<readonly string[]> {
    const entries = await readdir(directory, { withFileTypes: true });
    const files: string[] = [];
    for (const entry of entries) {
      const full = join(directory, entry.name);
      if (entry.isDirectory()) files.push(...await walk(full));
      else files.push(full);
    }
    return files;
  }
  const files = await walk(specialsRoot);
  for (const file of files) {
    assert.doesNotMatch(file, /\.(py|ts|tsx|js|mjs|cjs|sh|ps1)$/i, `executable-looking ${file}`);
  }
});
