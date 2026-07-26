import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import React from "react";
import { renderToStaticMarkup } from "react-dom/server";

import { LOCAL_COLLABORATION_LANDING } from "../lib/projections/collaboration-landing";
import { CollaborationHome } from "./CollaborationHome";

const componentDirectory = dirname(fileURLToPath(import.meta.url));

test("collaboration home matches ui_18 md/svg structure", () => {
  const markup = renderToStaticMarkup(<CollaborationHome />);

  assert.match(markup, /Collaboration &amp; Sharing Hub/);
  assert.match(markup, /Share swarms, contribute back to commons/);
  assert.match(markup, /Search shared items/);
  assert.match(markup, /Shared with me/);
  assert.match(markup, /My shares/);
  assert.match(markup, /TradingResearch α/);
  assert.match(markup, /Parallel \+ Verify v1\.4/);
  assert.match(markup, /VerifierNode v3\.0/);
  assert.match(markup, /Dynamic Router Pattern/);
  assert.match(markup, /Open/);
  assert.match(markup, /Duplicate/);
  assert.match(markup, /Share TradingResearch/);
  assert.match(markup, /Add people or teams/);
  assert.match(markup, /Link sharing/);
  assert.match(markup, /tr-alpha-7f2a/);
  assert.match(markup, /Copy link/);
  assert.match(markup, /Access controlled server-side/);
  assert.match(markup, /Contribute Back to Commons/);
  assert.match(markup, /CustomReportAgent/);
  assert.match(markup, /Propose to Registry/);
  assert.match(markup, /Improved SentimentAgent/);
  assert.match(markup, /Create Proposal/);
  assert.match(markup, /Your ecosystem impact/);
  assert.match(markup, /Live Co-Editing/);
  assert.match(markup, /2 editing now/);
  assert.match(markup, /Join session/);
  assert.match(markup, /Team Activity/);
  assert.match(markup, /Proposal Review Workflows/);
  assert.match(markup, /Comments are not interchangeable with critiques/);
  assert.doesNotMatch(markup, /tenant_id|password=|authorization:\s*bearer/i);
});

test("collaboration fixture covers shares, sessions, queue, critique note", () => {
  assert.equal(LOCAL_COLLABORATION_LANDING.sharedItems.length, 3);
  assert.equal(LOCAL_COLLABORATION_LANDING.contributions.length, 2);
  assert.equal(LOCAL_COLLABORATION_LANDING.sessions.length, 2);
  assert.ok(
    LOCAL_COLLABORATION_LANDING.sessions.some((s) => s.canJoin),
  );
  assert.equal(LOCAL_COLLABORATION_LANDING.teamActivity.length, 4);
  assert.equal(LOCAL_COLLABORATION_LANDING.proposalQueue.length, 2);
  assert.match(LOCAL_COLLABORATION_LANDING.critiqueNote, /not interchangeable/i);
  assert.match(LOCAL_COLLABORATION_LANDING.footerNote, /no peer execution/i);
});

test("collaboration CSS defines items, share modal, co-edit, and activity", async () => {
  const css = await readFile(
    resolve(componentDirectory, "../app/globals.css"),
    "utf8",
  );
  assert.match(css, /\.collab-home \{/);
  assert.match(css, /\.collab-home__items/);
  assert.match(css, /\.collab-home__share-modal/);
  assert.match(css, /\.collab-home__sessions/);
  assert.match(css, /\.collab-home__critique/);
});
