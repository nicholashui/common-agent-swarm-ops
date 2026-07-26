/**
 * Screen parameter store: data is stored, not hardcoded into components/pages.
 */
import assert from "node:assert/strict";
import test from "node:test";

import {
  getScreenParameters,
  listScreenParameterKeys,
  resetScreenParameters,
  setScreenParameters,
  updateScreenParameters,
} from "./screen-parameters";

test("store exposes every redesign landing key with stored defaults", (): void => {
  const keys = listScreenParameterKeys();
  assert.ok(keys.includes("dashboard"));
  assert.ok(keys.includes("registry"));
  assert.ok(keys.includes("specials"));
  assert.ok(keys.includes("blueprints"));
  assert.equal(keys.length, 22);
  assert.ok(keys.includes("login"));
  assert.equal(typeof getScreenParameters("dashboard").title, "string");
  assert.ok(getScreenParameters("dashboard").title.length > 0);
});

test("updateScreenParameters mutates store and reset restores defaults", (): void => {
  resetScreenParameters("dashboard");
  const original = getScreenParameters("dashboard").title;
  updateScreenParameters("dashboard", { title: "Updated From Store" });
  assert.equal(getScreenParameters("dashboard").title, "Updated From Store");
  resetScreenParameters("dashboard");
  assert.equal(getScreenParameters("dashboard").title, original);
});

test("setScreenParameters replaces the full view object", (): void => {
  resetScreenParameters("specials");
  const current = getScreenParameters("specials");
  setScreenParameters("specials", {
    ...current,
    title: "Replaced Specials Title",
  });
  assert.equal(getScreenParameters("specials").title, "Replaced Specials Title");
  resetScreenParameters("specials");
});

test("registry stored parameters include specials catalog", (): void => {
  const registry = getScreenParameters("registry");
  assert.ok(registry.specials);
  assert.equal(registry.specials.agents.length, 19);
  assert.equal(registry.specials.agents[0]?.status, "draft");
});
