import test from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { readFile } from 'node:fs/promises';

test('source downloader dry run validates selection without network', () => {
  const run = spawnSync(process.execPath, ['scripts/source-download.mjs', '--dry-run'], { encoding: 'utf8' });
  assert.equal(run.status, 0, run.stderr);
  assert.match(run.stdout, /Dry run: ecc/);
  assert.doesNotMatch(run.stdout + run.stderr, /clone|fetch|pull/i);
});
test('real source lock records the required metadata shape', async () => {
  const lock = JSON.parse(await readFile('sources/source-lock.json', 'utf8'));
  const required = ['id', 'name', 'url', 'resolved_url', 'target', 'status', 'commit', 'branch', 'last_commit_at', 'last_commit_subject', 'license_files', 'package_files', 'quarantine', 'import_policy'];
  assert.equal(lock.schema_version, '2.0'); assert.ok(lock.sources.length >= 4);
  for (const entry of lock.sources) for (const field of required) assert.ok(field in entry, `${entry.id} lacks ${field}`);
  assert.doesNotMatch(JSON.stringify(lock), /gemini/i);
});
