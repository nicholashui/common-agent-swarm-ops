import test from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { readFile } from 'node:fs/promises';

test('audit writes policy and source metadata without executing sources', async () => {
  const run = spawnSync(process.execPath, ['scripts/source-audit.mjs'], { encoding: 'utf8' });
  assert.equal(run.status, 0, run.stderr);
  const audit = await readFile('docs/source-audit.md', 'utf8');
  assert.match(audit, /# Source Audit/); assert.match(audit, /Selected components: none yet/);
});
