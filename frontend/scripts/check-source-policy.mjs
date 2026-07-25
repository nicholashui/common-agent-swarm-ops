import { readdir, readFile } from "node:fs/promises";
import { relative, resolve, sep } from "node:path";
import { fileURLToPath } from "node:url";

const FRONTEND_ROOT = resolve(fileURLToPath(new URL("..", import.meta.url)));
const SOURCE_EXTENSION = /\.(?:[cm]?[jt]sx?)$/;
const TEST_FILE = /(?:\.test\.|\/test\/|\\test\\)/;

export async function checkSourcePolicy(root = FRONTEND_ROOT) {
  const violations = [];
  for (const file of await sourceFiles(resolve(root))) {
    const source = await readFile(file, "utf8");
    const path = relative(root, file).split(sep).join("/");
    if (path === "scripts/check-source-policy.mjs" || TEST_FILE.test(path) || !SOURCE_EXTENSION.test(path)) continue;
    for (const [rule, expression] of rulesFor(path)) {
      for (const match of source.matchAll(expression)) violations.push({ path, rule, line: lineFor(source, match.index ?? 0) });
    }
  }
  return violations;
}

async function sourceFiles(directory) {
  const entries = await readdir(directory, { withFileTypes: true });
  const nested = await Promise.all(entries.filter((entry) => !entry.name.startsWith(".") && entry.name !== "node_modules").map(async (entry) => entry.isDirectory() ? sourceFiles(resolve(directory, entry.name)) : [resolve(directory, entry.name)]));
  return nested.flat();
}

function rulesFor(path) {
  const directFetch = /\b(?:globalThis\s*\.\s*)?fetch\b/g;
  return [
    ...(path === "src/lib/api/transport.ts" || path.startsWith("src/app/api/") ? [] : [["direct-fetch", directFetch]]),
    ["unversioned-public-api", /(?<![\w.])\/api\/(?!v1(?:[^A-Za-z0-9_-]|$))/g],
    ["liveness-readiness", /\/api\/v1\/(?:(?:health\/)?(?:live(?:ness)?|ready(?:iness)?))(?:\/|['"`])/gi],
    ["dangerously-set-inner-html", /\bdangerouslySetInnerHTML\b/g],
    ["dynamic-evaluation", /\beval\s*\(|\bnew\s+Function\s*\(/g],
    ["arbitrary-window-open", /\bwindow\s*\.\s*open\s*\(/g],
    ["browser-persistence-write", /\b(?:localStorage|sessionStorage)\s*\.\s*(?:setItem|removeItem|clear)\s*\(|\bindexedDB\s*\.\s*(?:open|deleteDatabase)\s*\(|(?<![\w.])caches\s*\.\s*(?:open|delete)\s*\(|\bdocument\s*\.\s*cookie\s*=/g],
  ];
}

function lineFor(source, index) { return source.slice(0, index).split("\n").length; }

if (process.argv[1] !== undefined && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const rootIndex = process.argv.indexOf("--root");
  const root = rootIndex === -1 ? FRONTEND_ROOT : resolve(process.argv[rootIndex + 1] ?? "");
  const violations = await checkSourcePolicy(root);
  for (const violation of violations) console.error(`${violation.path}:${violation.line} ${violation.rule}`);
  if (violations.length > 0) process.exitCode = 1;
}
