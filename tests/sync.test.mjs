import test from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
function sync(...args) { return spawnSync(process.execPath, ['scripts/sync.mjs', ...args], { encoding: 'utf8' }); }
test('sync dry run is scoped to approved outputs', () => {
  const run = sync('--dry-run'); assert.equal(run.status, 0, run.stderr);
  const paths = [...run.stdout.matchAll(/PLAN (.+)/g)].map(m => m[1]);
  assert.ok(paths.some(p => p.startsWith('.kiro/'))); assert.ok(paths.some(p => p === 'CLAUDE.md' || p.startsWith('.claude/')));
  assert.ok(paths.every(p => /^(\.kiro\/(settings\.json|mcp\.json|steering\/|hooks\/|skills\/)|CLAUDE\.md|\.claude\/(settings\.json|skills\/|commands\/|agents\/))/.test(p)));
});
test('sync rejects unsupported target', () => { const run = sync('--target', 'other'); assert.notEqual(run.status, 0); });
