import { readJson, assertNoProhibited } from './fs-safe.mjs';
const sourceFields = ['id', 'name', 'url', 'target', 'type', 'enabled', 'priority', 'tier', 'quarantine', 'import_policy', 'purpose'];
export async function loadManifests() { const sources = await readJson('sources/manifest.json'); const docs = await readJson('sources/docs-manifest.json'); validateManifests(sources, docs); return { sources, docs }; }
export function validateManifests(sources, docs) {
  assertNoProhibited(sources, 'source manifest'); assertNoProhibited(docs, 'documentation manifest');
  if (!Array.isArray(sources.sources) || !Array.isArray(docs.docs)) throw new Error('Manifest arrays are required');
  const ids = new Set();
  for (const source of sources.sources) {
    for (const field of sourceFields) if (!(field in source)) throw new Error(`Source ${source.id || '<unknown>'} lacks ${field}`);
    if (ids.has(source.id)) throw new Error(`Duplicate source id: ${source.id}`); ids.add(source.id);
    if (!source.target.startsWith('external/sources/') || source.target.includes('..')) throw new Error(`Unsafe source target: ${source.target}`);
    if (source.type !== 'git' || !/^https:\/\//.test(source.url)) throw new Error(`Invalid source URL: ${source.id}`);
  }
  for (const doc of docs.docs) if (!doc.id || !doc.url || !doc.target?.startsWith('external/docs/') || doc.target.includes('..')) throw new Error(`Invalid documentation record: ${doc.id || '<unknown>'}`);
}
export function selectSources(manifest, profile = 'all') { return manifest.sources.filter(s => s.enabled && (profile === 'all' || s.tier === profile)); }
