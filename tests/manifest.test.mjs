import test from 'node:test';
import assert from 'node:assert/strict';
import { loadManifests, selectSources, validateManifests } from '../scripts/lib/manifest.mjs';

test('manifests parse and enabled sources are complete', async () => {
  const { sources, docs } = await loadManifests();
  assert.ok(sources.sources.every(s => s.target.startsWith('external/sources/')));
  assert.equal(new Set(sources.sources.map(s => s.id)).size, sources.sources.length);
  assert.ok(docs.docs.every(d => d.target.startsWith('external/docs/')));
  assert.ok(!selectSources(sources).some(s => s.priority === 'archived'));
});
test('manifest policy rejects prohibited ecosystem references', () => {
  assert.throws(() => validateManifests({ sources: [{ id: 'x', name: 'gemini', url: 'https://example.test/x', target: 'external/sources/x', type: 'git', enabled: true, priority: 'required', tier: 'core', quarantine: true, import_policy: 'never-import', purpose: 'x' }] }, { docs: [] }));
});
