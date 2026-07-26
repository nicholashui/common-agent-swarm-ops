import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import React from "react";
import { renderToStaticMarkup } from "react-dom/server";

import { LOCAL_ONBOARDING_LANDING } from "../lib/projections/onboarding-landing";
import { getScreenParameters } from "../lib/projections/screen-parameters";
import { OnboardingHome } from "./OnboardingHome";

const componentDirectory = dirname(fileURLToPath(import.meta.url));

test("onboarding home matches ui_16 md/svg structure", () => {
  const markup = renderToStaticMarkup(<OnboardingHome view={getScreenParameters("onboarding")} />);

  assert.match(markup, /common-agent-swarm-ops/);
  assert.match(markup, /Skip for now/);
  assert.match(markup, /Step 3 of 5/);
  assert.match(markup, /Select Your Common Agents/);
  assert.match(markup, /battle-tested commons from the Registry/);
  assert.match(markup, /Search or describe what you need/i);
  assert.match(markup, /All \(87\)/);
  assert.match(markup, /Data &amp; ETL/);
  assert.match(markup, /Verification/);
  assert.match(markup, /Analysis/);
  assert.match(markup, /Synthesis/);
  assert.match(markup, /DataFetcher/);
  assert.match(markup, /VerifierNode/);
  assert.match(markup, /SentimentAgent/);
  assert.match(markup, /SynthesisAgent/);
  assert.match(markup, /ContentDirector/);
  assert.match(markup, /MarketPredictor/);
  assert.match(markup, /commons selected/);
  assert.match(markup, /Clear all/);
  assert.match(markup, /Recommended Pattern/);
  assert.match(markup, /Parallel Independent \+ Verification Loop v1\.4/);
  assert.match(markup, /Use this pattern/);
  assert.match(markup, /Next|Back/);
  assert.match(markup, /Registry Hub/);
  assert.match(markup, /Help Center/);
  assert.match(markup, /AI Help Chat/);
  assert.match(markup, /Sample Guided Projects/);
  assert.match(markup, /Request new common pattern/);
  assert.match(markup, /Report commons issue/);
  assert.match(markup, /versioned configurations|approval gates/);
  assert.doesNotMatch(markup, /tenant_id|password=|authorization:\s*bearer/i);
});

test("onboarding fixture covers five steps, agents, help, samples", () => {
  assert.equal(LOCAL_ONBOARDING_LANDING.steps.length, 5);
  assert.equal(LOCAL_ONBOARDING_LANDING.agents.length, 6);
  assert.ok(
    LOCAL_ONBOARDING_LANDING.agents.filter((a) => a.selectedByDefault).length >=
      3,
  );
  assert.equal(LOCAL_ONBOARDING_LANDING.helpCategories.length, 6);
  assert.equal(LOCAL_ONBOARDING_LANDING.sampleProjects.length, 3);
  assert.ok(LOCAL_ONBOARDING_LANDING.tourConcepts.length >= 4);
  assert.match(LOCAL_ONBOARDING_LANDING.vaNote, /without implying they are universal/i);
});

test("onboarding CSS defines wizard, agent grid, help, and progress", async () => {
  const css = await readFile(
    resolve(componentDirectory, "../app/globals.css"),
    "utf8",
  );
  assert.match(css, /\.onboarding-home \{/);
  assert.match(css, /\.onboarding-home__progress/);
  assert.match(css, /\.onboarding-home__agent-grid/);
  assert.match(css, /\.onboarding-home__help/);
  assert.match(css, /\.onboarding-home__pattern/);
});
