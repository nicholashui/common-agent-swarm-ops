import assert from "node:assert/strict";
import test from "node:test";

import React from "react";
import { renderToStaticMarkup } from "react-dom/server";

import {
  MarkdownDocument,
  pretreatHtmlImages,
  resolveMarkdownAssetUrl,
} from "./markdown-render";

test("resolveMarkdownAssetUrl keeps absolute and root-relative", () => {
  assert.equal(
    resolveMarkdownAssetUrl("https://example.com/a.png", "/docs/x.md"),
    "https://example.com/a.png",
  );
  assert.equal(
    resolveMarkdownAssetUrl("/docs/assets/a.png", "/docs/x.md"),
    "/docs/assets/a.png",
  );
});

test("resolveMarkdownAssetUrl resolves relative to markdown path", () => {
  assert.equal(
    resolveMarkdownAssetUrl("./assets/a.svg", "/docs/registry/userguide.md"),
    "/docs/registry/assets/a.svg",
  );
});

test("pretreatHtmlImages converts raw img tags", () => {
  const out = pretreatHtmlImages('<img src="./x.png" alt="X" />');
  assert.equal(out, "![X](./x.png)");
});

test("MarkdownDocument renders headings lists and code", () => {
  const markup = renderToStaticMarkup(
    <MarkdownDocument
      markdown={`# Title\n\n- one\n\n\`\`\`ts\nconst x = 1\n\`\`\`\n`}
      markdownPath="/docs/sample.md"
    />,
  );
  assert.match(markup, /help-md__h1/);
  assert.match(markup, /Title/);
  assert.match(markup, /help-md__ul/);
  assert.match(markup, /help-md__pre/);
  assert.match(markup, /const x = 1/);
});
