import assert from "node:assert/strict";
import test from "node:test";

import {
  createWorkspaceFile,
  getWorkspaceFile,
  listWorkspaceFiles,
  memoryFileStore,
  saveWorkspaceFile,
  stringField,
} from "./workspace-files";

test("save creates file and list includes it", () => {
  const store = memoryFileStore();
  const created = saveWorkspaceFile("composer", store, {
    name: "Wuxia brief",
    payload: { goal: "90s short", swarmName: "Wuxia crew" },
  });
  assert.ok(created.id.startsWith("wf_"));
  assert.equal(created.name, "Wuxia brief");
  const listed = listWorkspaceFiles("composer", store);
  assert.equal(listed.length, 1);
  assert.equal(listed[0]?.id, created.id);
  assert.equal(stringField(listed[0]!.payload, "goal"), "90s short");
});

test("save updates existing file by id without duplicating", () => {
  const store = memoryFileStore();
  const first = saveWorkspaceFile("canvas", store, {
    name: "Draft A",
    payload: { swarmName: "A" },
  });
  const second = saveWorkspaceFile("canvas", store, {
    id: first.id,
    name: "Draft A renamed",
    payload: { swarmName: "A2" },
  });
  assert.equal(second.id, first.id);
  const listed = listWorkspaceFiles("canvas", store);
  assert.equal(listed.length, 1);
  assert.equal(listed[0]?.name, "Draft A renamed");
  assert.equal(stringField(listed[0]!.payload, "swarmName"), "A2");
});

test("create adds another entry visible in dropdown data", () => {
  const store = memoryFileStore();
  createWorkspaceFile("composer", store, { name: "One" });
  createWorkspaceFile("composer", store, { name: "Two" });
  const names = listWorkspaceFiles("composer", store).map((f) => f.name);
  assert.deepEqual(names.sort(), ["One", "Two"]);
});

test("getWorkspaceFile returns null for missing id", () => {
  const store = memoryFileStore();
  assert.equal(getWorkspaceFile("composer", store, "missing"), null);
});

test("surfaces are isolated", () => {
  const store = memoryFileStore();
  saveWorkspaceFile("composer", store, {
    name: "Composer only",
    payload: {},
  });
  assert.equal(listWorkspaceFiles("canvas", store).length, 0);
  assert.equal(listWorkspaceFiles("composer", store).length, 1);
});

test("composer and canvas homes wire file picker Save and New", async () => {
  const { readFile } = await import("node:fs/promises");
  const { dirname, resolve } = await import("node:path");
  const { fileURLToPath } = await import("node:url");
  const root = resolve(dirname(fileURLToPath(import.meta.url)), "../..");
  const composer = await readFile(
    resolve(root, "components/ComposerHome.tsx"),
    "utf8",
  );
  const canvas = await readFile(
    resolve(root, "components/CanvasHome.tsx"),
    "utf8",
  );
  for (const source of [composer, canvas]) {
    assert.match(source, /workspace-file-picker/);
    assert.match(source, /Select .* file to edit/);
    assert.match(source, /saveWorkspaceFile/);
    assert.match(source, /createWorkspaceFile/);
    assert.match(source, />\s*Save\s*</);
    assert.match(source, />\s*New\s*</);
  }
  assert.match(composer, /listWorkspaceFiles\("composer"/);
  assert.match(canvas, /listWorkspaceFiles\("canvas"/);
});
