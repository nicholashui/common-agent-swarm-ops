import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import React from "react";
import { renderToStaticMarkup } from "react-dom/server";

import { LOCAL_PROFILE_LANDING } from "../lib/projections/profile-landing";
import { getScreenParameters } from "../lib/projections/screen-parameters";
import { ProfileHome } from "./ProfileHome";

const componentDirectory = dirname(fileURLToPath(import.meta.url));

test("profile home matches ui_13 md/svg structure", () => {
  const markup = renderToStaticMarkup(<ProfileHome view={getScreenParameters("profile")} />);

  assert.match(markup, /PROFILE &amp; CONTRIBUTIONS|Profile/);
  assert.match(markup, /Nicholas Hui/);
  assert.match(markup, /Top Contributor/);
  assert.match(markup, /Owner/);
  assert.match(markup, /Trading Lab/);
  assert.match(markup, /Rank #12/);
  assert.match(markup, /reputation 4,820/);
  assert.match(markup, /Commons contributed/);
  assert.match(markup, />80</);
  assert.match(markup, /Proposals merged/);
  assert.match(markup, /Swarms improved/);
  assert.match(markup, /Ecosystem savings/);
  assert.match(markup, /Streak/);
  assert.match(markup, /Contribution Activity/);
  assert.match(markup, /248 contributions this year/);
  assert.match(markup, /Badges &amp; Recognition/);
  assert.match(markup, /Reputation breakdown/);
  assert.match(markup, /server-attributed provenance/);
  assert.match(markup, /My Contributions/);
  assert.match(markup, /VerifierNode v3\.0/);
  assert.match(markup, /Parallel \+ Verify Pattern/);
  assert.match(markup, /Export contribution history/);
  assert.match(markup, />Overview</);
  assert.match(markup, />Account</);
  assert.match(markup, />Security</);
  assert.match(markup, /Usage &amp; Impact/);
  assert.match(markup, />Preferences</);
  assert.match(markup, /API Tokens/);
  assert.doesNotMatch(markup, /tenant_id|password=|authorization:\s*bearer/i);
  assert.doesNotMatch(markup, /sk-[a-zA-Z0-9]{8,}|casops_pat_[a-zA-Z0-9]{12,}/);
});

test("profile fixture covers impact, contributions, tokens without secrets", () => {
  assert.equal(LOCAL_PROFILE_LANDING.impact.length, 5);
  assert.equal(LOCAL_PROFILE_LANDING.contributions.length, 4);
  assert.equal(LOCAL_PROFILE_LANDING.tokens.length, 2);
  assert.ok(
    LOCAL_PROFILE_LANDING.tokens.every((token) =>
      token.status.includes("value hidden"),
    ),
  );
  assert.ok(LOCAL_PROFILE_LANDING.ssoProviders.length >= 2);
  assert.match(LOCAL_PROFILE_LANDING.safetyNote, /server-derived/i);
  assert.doesNotMatch(
    JSON.stringify(LOCAL_PROFILE_LANDING),
    /sk-|password|bearer\s/i,
  );
});

test("profile CSS defines identity, impact, heatmap, and tokens", async () => {
  const css = await readFile(
    resolve(componentDirectory, "../app/globals.css"),
    "utf8",
  );
  assert.match(css, /\.profile-home \{/);
  assert.match(css, /\.profile-home__impact/);
  assert.match(css, /\.profile-home__heatmap/);
  assert.match(css, /\.profile-home__table/);
  assert.match(css, /\.profile-home__token-once/);
});
