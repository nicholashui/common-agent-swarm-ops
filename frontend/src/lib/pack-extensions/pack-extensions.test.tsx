import assert from "node:assert/strict";
import test from "node:test";

import React from "react";
import { renderToStaticMarkup } from "react-dom/server";

import { DomainPackExtensionSlot } from "../../components/pack/DomainPackExtensionSlot";
import {
  extensionsForSlot,
  isPackUiExtensionManifest,
  type PackUiExtensionManifest,
} from "./types";

const VIDEO_PACK_EXTENSION: PackUiExtensionManifest = {
  domainId: "video",
  packVersion: "1.0.0",
  slotId: "registry.detail",
  title: "Video release readiness",
  panels: [{ panelId: "release", title: "Release gates", summary: "Readiness only; not production activation." }],
};

const SYNTHETIC_EXTENSION: PackUiExtensionManifest = {
  domainId: "synthetic-ops",
  packVersion: "0.2.0",
  slotId: "operations.panel",
  title: "Synthetic ops panel",
};

test("pack extension types accept domain-neutral manifests including video as a pack value", (): void => {
  assert.equal(isPackUiExtensionManifest(VIDEO_PACK_EXTENSION), true);
  assert.equal(isPackUiExtensionManifest(SYNTHETIC_EXTENSION), true);
  assert.equal(isPackUiExtensionManifest({ domainId: "video" }), false);
  assert.equal(isPackUiExtensionManifest(null), false);
});

test("extensionsForSlot filters by slot without domain special-casing", (): void => {
  const all = [VIDEO_PACK_EXTENSION, SYNTHETIC_EXTENSION];
  assert.deepEqual(extensionsForSlot(all, "registry.detail"), [VIDEO_PACK_EXTENSION]);
  assert.deepEqual(extensionsForSlot(all, "operations.panel"), [SYNTHETIC_EXTENSION]);
  assert.deepEqual(extensionsForSlot(all, "shell.nav"), []);
});

test("DomainPackExtensionSlot renders pack metadata without host video branches", (): void => {
  const markup = renderToStaticMarkup(
    <DomainPackExtensionSlot
      extensions={[VIDEO_PACK_EXTENSION, SYNTHETIC_EXTENSION]}
      slotId="registry.detail"
    />,
  );
  assert.match(markup, /data-slot-id="registry\.detail"/);
  assert.match(markup, /data-domain-id="video"/);
  assert.match(markup, /Video release readiness/);
  assert.doesNotMatch(markup, /synthetic-ops/);
  assert.doesNotMatch(markup, /\/api\/v1\/video\//);
});

test("DomainPackExtensionSlot stays empty when no extensions match", (): void => {
  const markup = renderToStaticMarkup(
    <DomainPackExtensionSlot
      emptyLabel="No pack extensions for this slot."
      extensions={[SYNTHETIC_EXTENSION]}
      slotId="registry.detail"
    />,
  );
  assert.match(markup, /No pack extensions for this slot/);
});
