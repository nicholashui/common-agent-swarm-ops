import test from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
test('bootstrap SDD artifact passes lifecycle gate', () => {
  const run = spawnSync(process.execPath, ['scripts/sdd-check.mjs'], { encoding: 'utf8' });
  assert.equal(run.status, 0, run.stderr); assert.match(run.stdout, /SDD gate: OK/);
});
