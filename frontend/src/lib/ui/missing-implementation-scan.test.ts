/**
 * Auto-detect incomplete frontend Home wiring:
 * - every *Home must accept onAction (real bridge) + optional statusMessage
 * - BoundScreenHome must wire onAction for each bound screen
 * - residual "requires authorized" announces must go through classify/onAction
 */
import assert from "node:assert/strict";
import { readdir, readFile } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const srcRoot = resolve(dirname(fileURLToPath(import.meta.url)), "../..");

async function listHomes(): Promise<readonly string[]> {
  const dir = join(srcRoot, "components");
  const names = await readdir(dir);
  return names
    .filter((n) => n.endsWith("Home.tsx") && !n.includes(".test."))
    .map((n) => join(dir, n));
}

test("scan: every presentation Home accepts onAction bridge props", async () => {
  const files = await listHomes();
  assert.ok(files.length >= 18, `expected Homes, got ${files.length}`);
  for (const file of files) {
    const source = await readFile(file, "utf8");
    assert.match(
      source,
      /onAction\?:/,
      `${file} must accept onAction for real UI actions`,
    );
    assert.match(
      source,
      /ScreenUiAction/,
      `${file} must type onAction with ScreenUiAction`,
    );
    assert.match(
      source,
      /classifyAnnounce|onPause|onSearch/,
      `${file} must route announces through classifyAnnounce or dedicated callbacks`,
    );
  }
});

test("scan: BoundScreenHome wires onAction for all bound screens", async () => {
  const bound = await readFile(
    join(srcRoot, "components/screen/BoundScreenHome.tsx"),
    "utf8",
  );
  assert.match(bound, /useScreenActionBridge/);
  const homes = [
    "ActivityHome",
    "ApiPortalHome",
    "AuditHome",
    "BlueprintsHome",
    "CanvasHome",
    "CollaborationHome",
    "ComposerHome",
    "CostsHome",
    "DashboardHome",
    "EvalHome",
    "KnowledgeHome",
    "MobileHome",
    "NotificationsHome",
    "OnboardingHome",
    "OrgChartHome",
    "AgentWorkflowHome",
    "ProfileHome",
    "RegistryHome",
    "SettingsHome",
    "AgentDetailHome",
    "MonitoringHome",
  ];
  for (const home of homes) {
    assert.match(bound, new RegExp(home), `BoundScreenHome must mount ${home}`);
    // Each home mount should pass onAction=
    const mountIdx = bound.indexOf(`<${home}`);
    assert.ok(mountIdx >= 0, `missing <${home}`);
    const slice = bound.slice(mountIdx, mountIdx + 400);
    assert.match(
      slice,
      /onAction=\{/,
      `${home} mount must pass onAction={...}`,
    );
  }
});

test("scan: interaction runtime exposes run/eval/dispatch for Homes", async () => {
  const runtime = await readFile(
    join(srcRoot, "lib/ui/interaction-runtime.ts"),
    "utf8",
  );
  for (const method of [
    "createRun",
    "dispatchRun",
    "createAndDispatchRun",
    "runEvaluation",
    "loadTopology",
    "retrieveMemory",
    "inspectRun",
    "decideApproval",
  ]) {
    assert.match(runtime, new RegExp(method), `runtime missing ${method}`);
  }
});

test("scan: no Home uses disabled={true} on primary actions without bridge", async () => {
  const files = await listHomes();
  for (const file of files) {
    const source = await readFile(file, "utf8");
    // Allow disabled={busy} or expression; ban permanent disabled={true} on buttons
    const permanent = source.match(/disabled=\{true\}/g) ?? [];
    assert.equal(
      permanent.length,
      0,
      `${file} has permanently disabled controls; wire real handlers or remove`,
    );
  }
});

test("scan: screen-actions module is the single fail-closed path", async () => {
  const actions = await readFile(join(srcRoot, "lib/ui/screen-actions.ts"), "utf8");
  assert.match(actions, /governed\.fail_closed/);
  assert.match(actions, /performScreenAction/);
  assert.match(actions, /classifyAnnounce/);
  assert.match(actions, /eval\.run_campaign/);
  assert.match(actions, /canvas\.run/);
});

test("scan: no dead buttons in component sources (every button has a handler path)", async () => {
  async function walk(dir: string): Promise<string[]> {
    const entries = await readdir(dir, { withFileTypes: true });
    const out: string[] = [];
    for (const entry of entries) {
      const full = join(dir, entry.name);
      if (entry.isDirectory()) {
        out.push(...(await walk(full)));
        continue;
      }
      if (
        entry.name.endsWith(".tsx") &&
        !entry.name.includes(".test.") &&
        !entry.name.includes(".property.")
      ) {
        out.push(full);
      }
    }
    return out;
  }

  const files = await walk(join(srcRoot, "components"));
  const dead: string[] = [];
  for (const file of files) {
    const source = await readFile(file, "utf8");
    const parts = source.split(/<button\b/);
    for (let i = 1; i < parts.length; i += 1) {
      const close = parts[i]!.indexOf(">");
      const attrs = close >= 0 ? parts[i]!.slice(0, close) : parts[i]!.slice(0, 200);
      // Handler via onClick/submit/disabled expression, or prop spread for primitives.
      if (
        /onClick|type="submit"|formAction|\bdisabled\b|\{\.\.\.buttonProps\}|\{\.\.\.props\}/.test(
          attrs,
        )
      ) {
        continue;
      }
      // IconControl-style: onClick destructured and reapplied on next lines after attrs
      // is still detected via explicit onClick= on the opening tag after our fix.
      dead.push(`${file}: ${attrs.replace(/\s+/g, " ").trim().slice(0, 120)}`);
    }
  }
  assert.equal(
    dead.length,
    0,
    `dead buttons (no onClick/submit/disabled path):\n${dead.join("\n")}`,
  );
});
