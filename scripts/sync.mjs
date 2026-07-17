import { readdir, readFile } from 'node:fs/promises';
import { allowedOutput, assertNoProhibited, exists, readJson, writeText } from './lib/fs-safe.mjs';
import { loadManifests } from './lib/manifest.mjs';
import * as kiro from './adapters/kiro.mjs'; import * as claude from './adapters/claude-code.mjs';
const args = process.argv.slice(2), dry = args.includes('--dry-run'), check = args.includes('--check'); const requested = args.includes('--target') ? args[args.indexOf('--target') + 1] : 'all';
if (!['all', 'kiro', 'claude-code'].includes(requested)) throw new Error(`Unsupported target: ${requested}`);
async function files(relative) { return (await readdir(new URL(`../${relative}/`, import.meta.url), { withFileTypes: true })).filter(e => e.isFile() && e.name.endsWith('.md')).map(async e => ({ name: e.name, content: await readFile(new URL(`../${relative}/${e.name}`, import.meta.url), 'utf8') })); }
const skillManifest = await readJson('skills/manifest.json');
const inputs = { rules: await Promise.all(await files('rules')), skills: await Promise.all(skillManifest.skills.map(async s => ({ id: s.id, content: await readFile(new URL(`../skills/${s.path}`, import.meta.url), 'utf8') }))), hooks: (await readJson('hooks/manifest.json')).hooks, mcp: await readJson('mcp-configs/minimal.json') };
await loadManifests(); assertNoProhibited(JSON.stringify({ hooks: inputs.hooks, mcp: inputs.mcp }), 'sync inputs');
const adapters = requested === 'all' ? [kiro, claude] : [requested === 'kiro' ? kiro : claude]; const planned = new Map(); for (const adapter of adapters) for (const [file, content] of await adapter.plan(inputs)) { if (!allowedOutput(file)) throw new Error(`Unapproved output path: ${file}`); planned.set(file, content); }
let drift = false; for (const [file, content] of planned) { if (dry) console.log(`PLAN ${file}`); else if (check) { const current = await exists(file) ? await readFile(new URL(`../${file}`, import.meta.url), 'utf8') : ''; if (current !== content) { console.log(`DRIFT ${file}`); drift = true; } } else { await writeText(file, content); console.log(`WROTE ${file}`); } }
if (check && drift) process.exitCode = 1; if (dry) console.log(`Planned files: ${planned.size}`);
