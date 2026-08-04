import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import React from "react";
import { renderToStaticMarkup } from "react-dom/server";

import { LOCAL_NOTIFICATIONS_LANDING } from "../lib/projections/notifications-landing";
import { getScreenParameters } from "../lib/projections/screen-parameters";
import { NotificationsHome } from "./NotificationsHome";

const componentDirectory = dirname(fileURLToPath(import.meta.url));

test("notifications home matches ui_12 md/svg structure", () => {
  const markup = renderToStaticMarkup(<NotificationsHome view={getScreenParameters("notifications")} />);

  assert.match(markup, /Notifications Center/);
  assert.match(markup, /Actionable, centralized alerts/);
  assert.match(markup, /All \(7\)/);
  assert.match(markup, /Proposals/);
  assert.match(markup, /Rollouts/);
  assert.match(markup, /Gates/);
  assert.match(markup, /Anomalies/);
  assert.match(markup, /Mark all read/);
  assert.match(markup, /Today · High priority|Today/);
  assert.match(markup, /Approval gate ready/);
  assert.match(markup, /video.editor v3\.0/);
  assert.match(markup, /L1 pass/);
  assert.match(markup, /L2 rubric 0\.94/);
  assert.match(markup, /GateKeeper/);
  assert.match(markup, /Approve/);
  assert.match(markup, /Review/);
  assert.match(markup, /Anomaly/);
  assert.match(markup, /error spike/);
  assert.match(markup, /Rollback/);
  assert.match(markup, /video.analyst/);
  assert.match(markup, /Archive Batch/);
  assert.match(markup, /video.judge v3\.0/);
  assert.match(markup, /Update to latest/);
  assert.match(markup, /Preferences/);
  assert.match(markup, /Notify me about/);
  assert.match(markup, /Swarm failures/);
  assert.match(markup, /Delivery channels/);
  assert.match(markup, /In-app/);
  assert.match(markup, /Telegram/);
  assert.match(markup, /PWA push/);
  assert.match(markup, /Quiet hours/);
  assert.match(markup, /Snooze type 24h/);
  assert.match(markup, /no approval op or secret/);
  assert.doesNotMatch(markup, /tenant_id|password=|authorization:\s*bearer/i);
  assert.doesNotMatch(markup, /sk-|api_key\s*=/i);
});

test("notifications fixture covers event kinds and redacted safety", () => {
  assert.equal(LOCAL_NOTIFICATIONS_LANDING.badgeCount, 7);
  assert.equal(LOCAL_NOTIFICATIONS_LANDING.items.length, 7);
  assert.ok(
    LOCAL_NOTIFICATIONS_LANDING.items.some((item) => item.kind === "gate"),
  );
  assert.ok(
    LOCAL_NOTIFICATIONS_LANDING.items.some((item) => item.kind === "critique"),
  );
  assert.ok(
    LOCAL_NOTIFICATIONS_LANDING.items.some((item) => item.kind === "budget"),
  );
  assert.equal(LOCAL_NOTIFICATIONS_LANDING.notifyAbout.length, 5);
  assert.equal(LOCAL_NOTIFICATIONS_LANDING.channels.length, 5);
  assert.match(LOCAL_NOTIFICATIONS_LANDING.safetyNote, /authorized commands/i);
  assert.doesNotMatch(
    JSON.stringify(LOCAL_NOTIFICATIONS_LANDING),
    /sk-[a-zA-Z0-9]|password|bearer\s/i,
  );
});

test("notifications CSS defines list, cards, and preferences", async () => {
  const css = await readFile(
    resolve(componentDirectory, "../app/globals.css"),
    "utf8",
  );
  assert.match(css, /\.notifications-home \{/);
  assert.match(css, /\.notifications-home__list/);
  assert.match(css, /\.notifications-home__card/);
  assert.match(css, /\.notifications-home__prefs/);
  assert.match(css, /\.notifications-home__badge/);
});
