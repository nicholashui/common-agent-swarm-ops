import { readdir, readFile } from 'node:fs/promises';
import { exists, confined, readJson, assertNoProhibited } from './lib/fs-safe.mjs';
import { loadManifests } from './lib/manifest.mjs';
const findings = [];
async function walk(relative) { let entries; try { entries = await readdir(confined(relative), { withFileTypes: true }); } catch { return; }
  for (const entry of entries) { const next = `${relative}/${entry.name}`; if (entry.isSymbolicLink() || entry.name === '.git' || entry.name === 'node_modules') continue;
    if (/^\.env($|\.)|\.(pem|key|p12)$/i.test(entry.name)) findings.push(`sensitive file: ${next}`);
    if (entry.isDirectory()) await walk(next); else if (entry.isFile() && /(?:package\.json|\.sh|\.ps1|\.md)$/i.test(entry.name)) { const text = await readFile(confined(next), 'utf8').catch(() => ''); if (/curl\s+[^\n]*\|\s*(ba)?sh|irm\s+[^\n]*\|\s*iex/i.test(text)) findings.push(`remote installer pattern: ${next}`); if (/postinstall/i.test(text)) findings.push(`postinstall pattern: ${next}`); }
  }
}
await loadManifests(); if (await exists('sources/source-lock.json')) assertNoProhibited(await readJson('sources/source-lock.json'), 'source lock'); if (await exists('external/sources')) await walk('external/sources');
console.log('CASOPS security'); if (findings.length) { for (const finding of findings) console.log(`WARN: ${finding}`); } else console.log('No downloaded source findings.'); console.log('Result: OK');
