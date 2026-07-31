import assert from "node:assert/strict";
import test from "node:test";

import React from "react";
import { renderToStaticMarkup } from "react-dom/server";

import {
  MarkdownDocument,
  pretreatHtmlImages,
  resolveMarkdownAssetUrl,
  splitInlineMath,
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

test("MarkdownDocument renders tables and bare section numbers as headings", () => {
  const markdown = [
    "11. Common Structure of an AI Agent",
    "",
    "Every agent implements this skeleton.",
    "",
    "11.1 Architecture Diagram",
    "",
    "![diagram](/docs/assets/common-agent-structure.svg)",
    "",
    "| # | Component | Purpose |",
    "|---|---|---|",
    "| 1 | **Identity** | Stable handle |",
    "",
    "1. Emit artifacts matching role responsibility; self-score against criteria.",
    "2. Accept critique only from listed critics.",
  ].join("\n");
  const markup = renderToStaticMarkup(
    <MarkdownDocument markdown={markdown} markdownPath="/docs/agents/video.director/SPEC.md" />,
  );
  assert.match(markup, /help-md__h2/);
  assert.match(markup, /Common Structure of an AI Agent/);
  assert.match(markup, /help-md__h3/);
  assert.match(markup, /Architecture Diagram/);
  assert.match(markup, /help-md__table/);
  assert.match(markup, /help-md__img/);
  assert.match(markup, /help-md__ol/);
  assert.match(markup, /Emit artifacts matching role responsibility/);
  // Must not dump the whole section as a single pre/code block
  assert.doesNotMatch(markup, /help-md__pre/);
});

test("MarkdownDocument accepts triple-single-quote fences", () => {
  const markup = renderToStaticMarkup(
    <MarkdownDocument
      markdown={"'''json\n{\"a\":1}\n'''\n"}
      markdownPath="/docs/sample.md"
    />,
  );
  assert.match(markup, /help-md__pre/);
  assert.match(markup, /data-lang="json"/);
  assert.match(markup, /&quot;a&quot;:1|&quot;a&quot;:1|\{&quot;a&quot;:1\}/);
});

test("splitInlineMath extracts paren and dollar delimiters", () => {
  const parts = splitInlineMath("Let \\( S \\) and $x_i$ stay.");
  const maths = parts.filter((p) => p.kind === "math");
  assert.equal(maths.length, 2);
  assert.equal(maths[0]?.kind === "math" ? maths[0].tex : "", "S");
  assert.equal(maths[1]?.kind === "math" ? maths[1].tex : "", "x_i");
});

test("MarkdownDocument marks inline and display math for KaTeX", () => {
  const markdown = [
    "Let a situation/problem \\( S \\) be described by \\( \\{D_1, D_2, \\dots, D_n\\} \\).",
    "",
    "\\[",
    "\\operatorname{Cr}(y \\mid c, v, g) = B\\bigl(N(y), K(y)\\bigr) \\cdot U(y) \\cdot Q(y) \\cdot F(y)",
    "\\]",
    "",
    "- \\( N(y) \\): Novelty/surprise.",
  ].join("\n");
  const markup = renderToStaticMarkup(
    <MarkdownDocument markdown={markdown} markdownPath="/docs/agents/video.director/SPEC.md" />,
  );
  // MathTex hosts (client hydrates with KaTeX); assert data attributes from SSR markup
  assert.match(markup, /data-math="inline"/);
  assert.match(markup, /data-math="display"/);
  assert.match(markup, /data-tex="S"/);
  assert.match(markup, /operatorname\{Cr\}/);
  assert.match(markup, /help-md__math-block/);
  assert.match(markup, /help-md__math-inline/);
  // Must not leave raw display delimiters as paragraph text
  assert.doesNotMatch(markup, />\\\[</);
});
