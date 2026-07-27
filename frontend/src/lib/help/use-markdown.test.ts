import assert from "node:assert/strict";
import test from "node:test";

import {
  clearMarkdownCacheForTests,
  fetchMarkdownCandidates,
} from "./use-markdown";

test("fetchMarkdownCandidates returns ready for markdown", async () => {
  clearMarkdownCacheForTests();
  const fetchImpl = async (): Promise<Response> =>
    new Response("# Hello", {
      status: 200,
      headers: { "content-type": "text/markdown" },
    });
  const result = await fetchMarkdownCandidates(
    ["/docs/sample.md"],
    fetchImpl as typeof fetch,
  );
  assert.equal(result.status, "ready");
  if (result.status === "ready") {
    assert.equal(result.markdown, "# Hello");
    assert.equal(result.resolvedPath, "/docs/sample.md");
  }
});

test("fetchMarkdownCandidates treats 404 and HTML as soft miss then empty", async () => {
  clearMarkdownCacheForTests();
  let calls = 0;
  const fetchImpl = async (input: RequestInfo | URL): Promise<Response> => {
    calls += 1;
    const path = String(input);
    if (path.endsWith("a.md")) {
      return new Response("missing", { status: 404 });
    }
    return new Response("<!doctype html><html></html>", {
      status: 200,
      headers: { "content-type": "text/html" },
    });
  };
  const result = await fetchMarkdownCandidates(
    ["/docs/a.md", "/docs/b.md"],
    fetchImpl as typeof fetch,
  );
  assert.equal(calls, 2);
  assert.equal(result.status, "empty");
});

test("fetchMarkdownCandidates caches successful loads", async () => {
  clearMarkdownCacheForTests();
  let calls = 0;
  const fetchImpl = async (): Promise<Response> => {
    calls += 1;
    return new Response("ok", {
      status: 200,
      headers: { "content-type": "text/plain" },
    });
  };
  await fetchMarkdownCandidates(["/docs/c.md"], fetchImpl as typeof fetch);
  await fetchMarkdownCandidates(["/docs/c.md"], fetchImpl as typeof fetch);
  assert.equal(calls, 1);
});
