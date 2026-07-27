import { writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { createRequire } from "node:module";
import { register } from "node:module";

// Load TS module via tsx-compatible dynamic import path
const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const generatedPath = resolve(root, "src/lib/projections/pack-agents.generated.ts");

const { PACK_AGENTS, PACK_AGENT_COUNTS } = await import(
  pathToFileURL(generatedPath).href
);

function trunc(s, n = 160) {
  const t = String(s ?? "")
    .replace(/\s+/g, " ")
    .trim();
  return t.length <= n ? t : `${t.slice(0, n - 1)}…`;
}

const catalog = PACK_AGENTS.map((a) => ({
  id: a.id,
  pack: a.pack,
  name: a.name,
  role: a.role,
  status: a.status,
  description: trunc(a.description, 180),
  versionLabel: a.versionLabel,
  success: a.success,
  avgTokens: a.avgTokens,
  latency: a.latency,
  usage: a.usage,
  badges: a.badges,
  domains: a.domains,
  category: a.category,
  architecture: a.architecture,
  critiqueCompat: trunc(a.critiqueCompat, 80),
}));

const outPath = resolve(
  root,
  "src/lib/projections/pack-agents-catalog.generated.ts",
);

const body = `/* AUTO-GENERATED slim catalog for RegistryHome — short descriptions only. */
/* Source: pack-agents.generated.ts. Rebuild: node scripts/build-pack-agents-catalog.mjs */

export interface PackAgentCatalogEntry {
  readonly id: string;
  readonly pack: string;
  readonly name: string;
  readonly role: string;
  readonly status: string;
  readonly description: string;
  readonly versionLabel: string;
  readonly success: string;
  readonly avgTokens: string;
  readonly latency: string;
  readonly usage: string;
  readonly badges: readonly string[];
  readonly domains: readonly string[];
  readonly category: string;
  readonly architecture: string;
  readonly critiqueCompat: string;
}

export const PACK_AGENT_CATALOG_COUNTS = ${JSON.stringify(PACK_AGENT_COUNTS, null, 2)} as const;

export const PACK_AGENT_CATALOG: readonly PackAgentCatalogEntry[] = ${JSON.stringify(catalog, null, 2)};
`;

writeFileSync(outPath, body, "utf8");
console.log(`wrote ${catalog.length} agents → ${outPath} (${body.length} chars)`);
