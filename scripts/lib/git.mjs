import { spawn } from 'node:child_process';
export function git(args, cwd) {
  return new Promise((resolve, reject) => {
    const child = spawn('git', args, { cwd, shell: false, stdio: ['ignore', 'pipe', 'pipe'] }); let out = ''; let err = '';
    child.stdout.on('data', data => { out += data; }); child.stderr.on('data', data => { err += data; });
    child.on('error', reject); child.on('close', code => code === 0 ? resolve(out.trim()) : reject(new Error(err.trim() || `git exited ${code}`)));
  });
}
export async function gitAvailable() { try { await git(['--version']); return true; } catch { return false; } }
