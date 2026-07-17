import { readdir } from 'node:fs/promises';
import { exists, confined, stable, writeText } from './lib/fs-safe.mjs';
import { loadManifests, selectSources } from './lib/manifest.mjs';
import { git } from './lib/git.mjs';
const args = process.argv.slice(2), dry = args.includes('--dry-run'), strict = args.includes('--strict'), check = args.includes('--check'), update = args.includes('--update');
const profile = args.includes('--profile') ? args[args.indexOf('--profile') + 1] : 'all';
function metadata(source, status, extra = {}) { return { id: source.id, name: source.name, url: source.url, resolved_url: source.url, target: source.target, status, commit: null, branch: null, last_commit_at: null, last_commit_subject: null, license_files: [], package_files: [], quarantine: source.quarantine, import_policy: source.import_policy, ...extra }; }
async function files(target) { const names = await readdir(confined(target)); return { license_files: names.filter(n => /^(license|copying|notice)/i.test(n)), package_files: names.filter(n => /^(package\.json|pyproject\.toml|cargo\.toml|go\.mod)$/i.test(n)) }; }
async function inspect(source) { const target = confined(source.target); const gitDir = `${source.target}/.git`;
  if (!await exists(gitDir)) await git(['clone', '--depth', '1', source.url, target]);
  else if (update) { await git(['-C', target, 'fetch', '--depth', '1', 'origin']); await git(['-C', target, 'pull', '--ff-only']); }
  const [resolved_url, commit, branch, last_commit_at, last_commit_subject, info] = await Promise.all([git(['-C', target, 'remote', 'get-url', 'origin']), git(['-C', target, 'rev-parse', 'HEAD']), git(['-C', target, 'branch', '--show-current']), git(['-C', target, 'log', '-1', '--format=%cI']), git(['-C', target, 'log', '-1', '--format=%s']), files(source.target)]);
  return metadata(source, 'ok', { resolved_url, commit, branch, last_commit_at, last_commit_subject, ...info });
}
const { sources } = await loadManifests(); const selected = selectSources(sources, profile);
if (check) { if (!await exists('sources/source-lock.json')) throw new Error('Missing source lock'); console.log('Source lock: OK'); }
else if (dry) { console.log(`Dry run: ${selected.map(s => s.id).join(', ') || 'no sources'}`); }
else { const entries = [], failures = []; for (const source of selected) try { entries.push(await inspect(source)); } catch (error) { const entry = metadata(source, 'failed', { error: error.message }); entries.push(entry); failures.push({ id: source.id, required: source.priority === 'required', error: error.message }); if (source.priority === 'required' || strict) { await writeText('sources/source-lock.json', stable({ schema_version: '2.0', generated_at: new Date().toISOString(), sources: entries, failures })); throw error; } }
  await writeText('sources/source-lock.json', stable({ schema_version: '2.0', generated_at: new Date().toISOString(), sources: entries, failures })); console.log(`Sources: ${entries.filter(e => e.status === 'ok').length} succeeded, ${failures.length} failed`); }
