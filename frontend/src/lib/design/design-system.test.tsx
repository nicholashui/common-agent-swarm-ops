import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import React from "react";
import { renderToStaticMarkup } from "react-dom/server";

import {
  DesignCommonBadge,
  DesignStatusPill,
} from "../../components/design/DesignSystemPrimitives";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "../..");

test("design-system.css encodes common-style.html light-frame tokens", async () => {
  const css = await readFile(
    resolve(root, "app/design-system.css"),
    "utf8",
  );

  // Color system from common-style.html
  assert.match(css, /#ffffff|#fff\b/i);
  assert.match(css, /#fafaf9/); // surface stone-50
  assert.match(css, /#f5f5f4/); // elevated stone-100
  assert.match(css, /#e7e5e4/); // border stone-200
  assert.match(css, /#1c1917/); // primary text / CTA stone-900
  assert.match(css, /#78716c/); // secondary text stone-500
  assert.match(css, /#4f46e5/); // common indigo-600
  assert.match(css, /#eef2ff/); // common surface indigo-50
  assert.match(css, /#7c3aed/); // pattern violet-600
  assert.match(css, /#f59e0b/); // custom fork amber
  assert.match(css, /#10b981/); // success emerald
  assert.match(css, /#ef4444/); // error red

  assert.match(css, /\.ds-status/);
  assert.match(css, /\.ds-status--live/);
  assert.match(css, /\.ds-status--reconnecting/);
  assert.match(css, /\.ds-status--stale/);
  assert.match(css, /\.ds-status--manual_recovery_required/);
  assert.match(css, /\.ds-common-badge/);
  assert.match(css, /\.ds-freshness/);
  assert.match(css, /Inter/);
});

test("globals.css imports design-system and authenticated shell uses light frame", async () => {
  const css = await readFile(resolve(root, "app/globals.css"), "utf8");
  assert.match(css, /@import ["'].\/design-system\.css["']/);
  assert.match(css, /\.app-shell:has\(\.menu-workspace\)/);
  assert.match(css, /#fafaf9/);
  assert.match(css, /#4f46e5/);
});

test("docs viewer is light-framed for shell main content", async () => {
  const [ds, globals] = await Promise.all([
    readFile(resolve(root, "app/design-system.css"), "utf8"),
    readFile(resolve(root, "app/globals.css"), "utf8"),
  ]);
  // Light design tokens apply to .docs-page alongside login/shell
  assert.match(ds, /\.docs-page\s*\{/);
  assert.match(ds, /\.login-page,\s*\n\.docs-page|\.docs-page\s*,/);
  // In-shell content surface (not a chrome-less dark page)
  assert.match(globals, /\.docs-page\s*\{[^}]*color-scheme:\s*light/s);
  assert.match(globals, /\.docs-page\s*\{[^}]*color:\s*#1c1917/s);
  assert.match(globals, /\.docs-page__body\s*\{[^}]*background:\s*#ffffff/s);
  // Explicit override so dark .panel never wins on the guide body
  assert.match(globals, /\.docs-page__body\.panel|\.docs-page\s+\.panel/);
});

test("design status pill announces text status not color alone", () => {
  const markup = renderToStaticMarkup(
    <DesignStatusPill status="reconnecting" />,
  );
  assert.match(markup, /ds-status--reconnecting/);
  assert.match(markup, /Status:/);
  assert.match(markup, /Reconnecting/);
  assert.match(markup, /ds-status__dot--pulse/);
});

test("design common badge uses indigo common treatment", () => {
  const markup = renderToStaticMarkup(
    <DesignCommonBadge version="3.0" runs="31.2k" success="97" />,
  );
  assert.match(markup, /ds-common-badge/);
  assert.match(markup, /Common/);
  assert.match(markup, /v3\.0/);
  assert.match(markup, /31\.2k/);
  assert.match(markup, /97/);
});
