/**
 * Wire onAction + classifyAnnounce into presentation Homes.
 * Run: node scripts/wire-screen-actions.mjs
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const dir = path.join(path.dirname(fileURLToPath(import.meta.url)), "../src/components");
const importLine =
  'import { classifyAnnounce, type ScreenUiAction } from "../lib/ui/screen-actions";';

const homes = fs
  .readdirSync(dir)
  .filter((f) => f.endsWith("Home.tsx") && !f.includes(".test."));

function patchAnnounce(src) {
  const simple =
    "const announce = (message: string): void => setStatusMessage(message);";
  const bridged = `const announce = (message: string): void => {
    if (onAction) {
      void onAction(classifyAnnounce(message));
      return;
    }
    setStatusMessage(message);
  };
  const feedback = externalStatus ?? statusMessage;`;
  if (src.includes(simple)) {
    return src.replace(simple, bridged);
  }
  return src;
}

function addImport(src) {
  if (src.includes("screen-actions")) return src;
  const matches = [...src.matchAll(/^import .+;$/gm)];
  const last = matches[matches.length - 1];
  if (!last) return src;
  const idx = last.index + last[0].length;
  return src.slice(0, idx) + "\n" + importLine + src.slice(idx);
}

function patchSignature(src, file) {
  if (file === "KnowledgeHome.tsx") {
    return src
      .replace(
        /export function KnowledgeHome\(\{[\s\S]*?statusMessage\?: string;\s*\}>\): JSX\.Element \{/,
        `export function KnowledgeHome({
  view,
  onSearch,
  onAction,
  statusMessage: externalStatus,
}: Readonly<{
  view: KnowledgeLandingView;
  onSearch?: (query: string) => void | Promise<void>;
  onAction?: (action: ScreenUiAction) => void | Promise<void>;
  statusMessage?: string;
}>): JSX.Element {`,
      )
      .replace(
        /const announce = \(message: string\): void => setStatusMessage\(message\);/,
        `const announce = (message: string): void => {
    if (onAction) {
      void onAction(classifyAnnounce(message));
      return;
    }
    setStatusMessage(message);
  };`,
      );
  }

  if (file === "DashboardHome.tsx") {
    let next = src.replace(
      /export function DashboardHome\(\{\s*view \}: Readonly<\{ view: DashboardLandingView \}>\): JSX\.Element \{/,
      `export function DashboardHome({
  view,
  onAction,
  onPause,
  statusMessage: externalStatus,
}: Readonly<{
  view: DashboardLandingView;
  onAction?: (action: ScreenUiAction) => void | Promise<void>;
  onPause?: (swarmId: string) => void;
  statusMessage?: string;
}>): JSX.Element {`,
    );
    next = next.replace(
      /<RunningSwarmCard\s+key=\{swarm\.id\}\s+labels=\{labels\}\s+swarm=\{swarm\}\s*\/>/g,
      "<RunningSwarmCard key={swarm.id} labels={labels} swarm={swarm} onPause={onPause} />",
    );
    next = next.replace(
      /<RunningSwarmCard\n(\s+)key=\{swarm\.id\}\n\s+labels=\{labels\}\n\s+swarm=\{swarm\}\n\s*\/>/g,
      "<RunningSwarmCard\n$1key={swarm.id}\n$1labels={labels}\n$1swarm={swarm}\n$1onPause={onPause}\n$1/>",
    );
    return next;
  }

  const re =
    /export function (\w+Home)\(\{\s*view\s*\}: Readonly<\{\s*view: (\w+)\s*\}>\): JSX\.Element \{/;
  const reMulti =
    /export function (\w+Home)\(\{\s*\n\s*view \}: Readonly<\{ view: (\w+) \}>\): JSX\.Element \{/;

  if (re.test(src)) {
    return src.replace(
      re,
      `export function $1({
  view,
  onAction,
  statusMessage: externalStatus,
}: Readonly<{
  view: $2;
  onAction?: (action: ScreenUiAction) => void | Promise<void>;
  statusMessage?: string;
}>): JSX.Element {`,
    );
  }
  if (reMulti.test(src)) {
    return src.replace(
      reMulti,
      `export function $1({
  view,
  onAction,
  statusMessage: externalStatus,
}: Readonly<{
  view: $2;
  onAction?: (action: ScreenUiAction) => void | Promise<void>;
  statusMessage?: string;
}>): JSX.Element {`,
    );
  }
  return null;
}

function preferFeedback(src) {
  if (!src.includes("const feedback = externalStatus")) return src;
  let next = src;
  next = next.replace(
    /\{statusMessage \? \(\s*\n(\s*)<p aria-live="polite"/g,
    "{feedback ? (\n$1<p aria-live=\"polite\"",
  );
  next = next.replace(
    /(className="[^"]*__status"[^>]*>\s*\n\s*)\{statusMessage\}/g,
    "$1{feedback}",
  );
  next = next.replace(
    /\{statusMessage \? \(\s*\n(\s*)<p className="([^"]*status[^"]*)"/g,
    '{feedback ? (\n$1<p className="$2"',
  );
  // Composer / others: {statusMessage ? ( <p className=...status
  next = next.replace(
    /\{statusMessage \?\s*\(\s*\n\s*<p className="composer-home__status"/,
    '{feedback ? (\n        <p className="composer-home__status"',
  );
  return next;
}

function patchComposer(src) {
  // Composer uses setStatusMessage directly for save/load
  if (!src.includes("export function ComposerHome")) return src;
  let next = src;
  if (!next.includes("const feedback = externalStatus")) {
    // after useState hooks, add feedback and bridge helper
    next = next.replace(
      /const \[statusMessage, setStatusMessage\] = useState<string \| undefined>\(\);/,
      `const [statusMessage, setStatusMessage] = useState<string | undefined>();
  const feedback = externalStatus ?? statusMessage;
  const announce = (message: string): void => {
    if (onAction) {
      void onAction(classifyAnnounce(message));
      return;
    }
    setStatusMessage(message);
  };`,
    );
  }
  next = next.replace(
    /onClick=\{\(\) =>\s*\n\s*setStatusMessage\(L\(labels, "save_draft_requires_an_authorized_compose_contra"\)\)\s*\n\s*\}/g,
    'onClick={() => announce(L(labels, "save_draft_requires_an_authorized_compose_contra"))}',
  );
  next = next.replace(
    /onClick=\{\(\) =>\s*\n\s*setStatusMessage\(L\(labels, "load_template_requires_an_authorized_template_pr"\)\)\s*\n\s*\}/g,
    'onClick={() => announce(L(labels, "load_template_requires_an_authorized_template_pr"))}',
  );
  // other setStatusMessage that are announce-like
  next = next.replace(
    /setStatusMessage\((L\([^)]+\)|"[^"]+"|`[^`]+`)\)/g,
    "announce($1)",
  );
  next = preferFeedback(next);
  return next;
}

let ok = 0;
let fail = 0;
for (const file of homes) {
  let src = fs.readFileSync(path.join(dir, file), "utf8");
  if (src.includes("ScreenUiAction") && src.includes("classifyAnnounce") && file !== "DashboardHome.tsx") {
    // may still need work
  }
  src = addImport(src);
  const sig = patchSignature(src, file);
  if (sig === null) {
    console.log("NO_SIGNATURE", file);
    fail += 1;
    fs.writeFileSync(path.join(dir, file), src);
    continue;
  }
  src = sig;
  src = patchAnnounce(src);
  if (file === "ComposerHome.tsx") src = patchComposer(src);
  src = preferFeedback(src);
  // silence unused onAction for dashboard if only onPause used - keep both
  if (file === "DashboardHome.tsx" && !src.includes("void onAction") && src.includes("onAction,")) {
    // ensure no unused lint - reference onAction
    src = src.replace(
      /const labels = view\.labels;\s*return \(/,
      "const labels = view.labels;\n  void onAction;\n  void externalStatus;\n  return (",
    );
  }
  fs.writeFileSync(path.join(dir, file), src);
  console.log("OK", file);
  ok += 1;
}
console.log(JSON.stringify({ ok, fail }));
