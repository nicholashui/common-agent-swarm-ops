import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import React from "react";
import { renderToStaticMarkup } from "react-dom/server";

import { LOCAL_KNOWLEDGE_LANDING } from "../lib/projections/knowledge-landing";
import { KnowledgeHome } from "./KnowledgeHome";

const componentDirectory = dirname(fileURLToPath(import.meta.url));

test("knowledge home matches ui_10 md/svg structure", () => {
  const markup = renderToStaticMarkup(<KnowledgeHome />);

  assert.match(markup, /Knowledge Management Hub/);
  assert.match(markup, /Common \+ business-scoped RAG sources/);
  assert.match(markup, /Search collections, chunks/);
  assert.match(markup, /Add source/);
  assert.match(markup, /Sync from Git/);
  assert.match(markup, /All types/);
  assert.match(markup, /Common/);
  assert.match(markup, /Business-scoped/);
  assert.match(markup, /Trading Corpus \(Common\)/);
  assert.match(markup, /Wuxia Lore/);
  assert.match(markup, /DSE ICT Notes/);
  assert.match(markup, /Healthy/);
  assert.match(markup, /Reindexing/);
  assert.match(markup, /Sync Jobs/);
  assert.match(markup, /Git · Trading Corpus|Git/);
  assert.match(markup, /untrusted refs/);
  assert.match(markup, /Detail/);
  assert.match(markup, />Sources</);
  assert.match(markup, /Search Test/);
  assert.match(markup, /market_reports_2026\.md/);
  assert.match(markup, /sentiment_dataset\.csv/);
  assert.match(markup, /strategy_wiki/);
  assert.match(markup, /pasted_notes\.txt/);
  assert.match(markup, /Drag &amp; drop files/);
  assert.match(markup, /client checks aren/);
  assert.match(markup, /can.?t be promoted to Common|can&apos;t be promoted to Common|can&#x27;t be promoted to Common|can’t be promoted to Common|can&apos;t be promoted|promoted to Common solely/);
  assert.doesNotMatch(markup, /tenant_id|password=|authorization:\s*bearer/i);
});

test("knowledge fixture covers bindings, sources, contributions, retrieval trace", () => {
  assert.equal(LOCAL_KNOWLEDGE_LANDING.collections.length, 3);
  assert.equal(LOCAL_KNOWLEDGE_LANDING.sources.length, 4);
  assert.equal(LOCAL_KNOWLEDGE_LANDING.searchHits.length, 2);
  assert.equal(LOCAL_KNOWLEDGE_LANDING.contributions.length, 2);
  assert.equal(LOCAL_KNOWLEDGE_LANDING.syncJobs.length, 3);
  assert.ok(
    LOCAL_KNOWLEDGE_LANDING.collections.some((c) =>
      c.bindingKinds.includes("constitutional"),
    ),
  );
  assert.ok(
    LOCAL_KNOWLEDGE_LANDING.retrievalTrace.some((line) =>
      line.includes("Query purpose"),
    ),
  );
  assert.match(LOCAL_KNOWLEDGE_LANDING.governanceNote, /verification state/i);
});

test("knowledge CSS defines hub grid, detail tabs, and contribution queue", async () => {
  const css = await readFile(
    resolve(componentDirectory, "../app/globals.css"),
    "utf8",
  );
  assert.match(css, /\.knowledge-home \{/);
  assert.match(css, /\.knowledge-home__grid/);
  assert.match(css, /\.knowledge-home__detail/);
  assert.match(css, /\.knowledge-home__contributions/);
  assert.match(css, /\.knowledge-home__drop/);
});
