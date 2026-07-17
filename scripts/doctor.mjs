import { access } from 'node:fs/promises';
import { root, exists, confined, outputAllowlist } from './lib/fs-safe.mjs';
import { loadManifests } from './lib/manifest.mjs';
import { gitAvailable } from './lib/git.mjs';
const nodeOK = Number(process.versions.node.split('.')[0]) >= 20, gitOK = await gitAvailable(); let manifestOK = true;
try { await loadManifests(); } catch { manifestOK = false; }
const externalOK = await (async () => { try { await access(confined('external')); return true; } catch { return false; } })();
const scopeOK = outputAllowlist.every(Boolean) && !outputAllowlist.some(path => path.includes('..'));
console.log('CASOPS doctor\n'); console.log(`Node: ${nodeOK ? 'OK' : 'FAIL'}`); console.log(`Git: ${gitOK ? 'OK' : 'FAIL'}`); console.log(`Manifest: ${manifestOK ? 'OK' : 'FAIL'}`); console.log(`Output scope: ${scopeOK ? 'OK' : 'FAIL'}`); console.log(`External dir: ${externalOK ? 'OK' : 'FAIL'}`); console.log(`OS: ${process.platform}`);
const ok = nodeOK && gitOK && manifestOK && scopeOK && externalOK && root === process.cwd(); console.log(`Result: ${ok ? 'OK' : 'FAIL'}`); if (!ok) process.exitCode = 1;
