import { cp, mkdir, readdir, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { root } from './lib/fs-safe.mjs';
export async function createProject(args) {
  const value = key => args.includes(key) ? args[args.indexOf(key) + 1] : undefined; const destination = value('--path'); const name = value('--name') || 'casops-project'; const force = args.includes('--force');
  if (!destination) throw new Error('create requires --path'); const target = path.resolve(destination); const existing = await readdir(target).catch(() => []);
  if (existing.length && !force) throw new Error('Target directory is non-empty; use --force only with explicit approval.');
  await mkdir(target, { recursive: true }); await cp(root, target, { recursive: true, filter: source => !source.includes(`${path.sep}.git`) && !source.includes(`${path.sep}external${path.sep}`) });
  const pkgPath = path.join(target, 'package.json'); const pkg = JSON.parse(await (await import('node:fs/promises')).readFile(pkgPath, 'utf8')); pkg.name = name; pkg.description = value('--purpose') || pkg.description; await writeFile(pkgPath, `${JSON.stringify(pkg, null, 2)}\n`); console.log(`Created ${name} at ${target}`);
}
