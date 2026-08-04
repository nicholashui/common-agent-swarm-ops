import assert from "node:assert/strict";
import test from "node:test";

import React from "react";
import { renderToStaticMarkup } from "react-dom/server";

import { InfoTooltip } from "../design";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "./tooltip";

test("InfoTooltip keeps full text in accessible label (SSR-safe)", () => {
  const markup = renderToStaticMarkup(
    <TooltipProvider delayDuration={0}>
      <InfoTooltip label="About Plan" text="Form a multi-agent work from available agents" />
    </TooltipProvider>,
  );
  assert.match(markup, /info-tooltip/);
  assert.match(markup, /About Plan: Form a multi-agent work/);
  assert.doesNotMatch(markup, /\stitle="/);
  // Span trigger — safe inside other buttons (no nested <button>)
  assert.match(markup, /role="button"/);
  assert.doesNotMatch(markup, /<button[^>]*class="info-tooltip"/);
});

test("Tooltip API matches shadcn shape: Provider + Trigger + Content", () => {
  const markup = renderToStaticMarkup(
    <TooltipProvider delayDuration={0}>
      <Tooltip delayDuration={0}>
        <TooltipTrigger type="button">Hover me</TooltipTrigger>
        <TooltipContent>Fast tip</TooltipContent>
      </Tooltip>
    </TooltipProvider>,
  );
  assert.match(markup, /Hover me/);
  // Content portals only when open — closed on SSR
  assert.doesNotMatch(markup, /Fast tip/);
});
