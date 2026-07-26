/**
 * Pass `labels` into nested helper components that use L(labels, ...).
 */
import { readFileSync, writeFileSync, readdirSync } from "node:fs";
import { join } from "node:path";

const dir = join(process.cwd(), "src/components");
const files = readdirSync(dir).filter(
  (n) => n.endsWith("Home.tsx") || n === "SpecialsCatalog.tsx",
);

for (const name of files) {
  const path = join(dir, name);
  let src = readFileSync(path, "utf8");
  const original = src;

  // Ensure ScreenLabels import
  if (src.includes("L(labels") && !src.includes("ScreenLabels")) {
    if (src.includes('from "../lib/projections/screen-labels"')) {
      src = src.replace(
        /import \{ L, Lfmt \} from "\.\.\/lib\/projections\/screen-labels";/,
        'import { L, Lfmt, type ScreenLabels } from "../lib/projections/screen-labels";',
      );
      src = src.replace(
        /import \{ L \} from "\.\.\/lib\/projections\/screen-labels";/,
        'import { L, type ScreenLabels } from "../lib/projections/screen-labels";',
      );
    }
  }

  // Find nested function components: function Name({ ... }): JSX
  // If body uses L(labels or Lfmt(labels and params don't include labels, inject.
  const fnRe =
    /function\s+([A-Z][A-Za-z0-9_]*)\s*\(\s*\{\s*([\s\S]*?)\s*\}\s*:\s*Readonly<\{\s*([\s\S]*?)\s*\}>\s*\)\s*:\s*JSX\.Element\s*\{/g;

  const helpersNeedingLabels = new Set();
  let m;
  const matches = [...src.matchAll(fnRe)];
  for (const match of matches) {
    const fnName = match[1];
    if (fnName.endsWith("Home") || fnName === "SpecialsCatalog") continue;
    const start = match.index + match[0].length;
    // crude body until next \nfunction or end
    const rest = src.slice(start);
    const endRel = rest.search(/\nfunction\s+[A-Z]/);
    const body = endRel === -1 ? rest : rest.slice(0, endRel);
    if (!/\bL(fmt)?\(\s*labels\s*,/.test(body)) continue;
    if (/\blabels\b/.test(match[2]) || /\blabels\b/.test(match[3])) continue;
    helpersNeedingLabels.add(fnName);

    const newDestructure = match[2].trim().length
      ? `${match[2].trim().replace(/,$/, "")},\n  labels,`
      : "labels,";
    const newType = match[3].trim().length
      ? `${match[3].trim().replace(/;$/, "").replace(/,$/, "")};\n  labels: ScreenLabels;`
      : "labels: ScreenLabels;";
    const replacement = `function ${fnName}({\n  ${newDestructure}\n}: Readonly<{\n  ${newType}\n}>): JSX.Element {`;
    src = src.replace(match[0], replacement);
  }

  // Pass labels={labels} into helper JSX usages
  for (const fnName of helpersNeedingLabels) {
    // <FnName ... /> or <FnName ...>
    const jsxOpen = new RegExp(`<${fnName}(\\s[^>]*)(/?)>`, "g");
    src = src.replace(jsxOpen, (full, attrs, selfClose) => {
      if (/\blabels=/.test(attrs)) return full;
      if (selfClose === "/") {
        return `<${fnName}${attrs} labels={labels} />`;
      }
      return `<${fnName}${attrs} labels={labels}>`;
    });
  }

  if (src !== original) {
    writeFileSync(path, src);
    console.log(
      `fixed ${name}: helpers ${[...helpersNeedingLabels].join(", ") || "(import only)"}`,
    );
  }
}
