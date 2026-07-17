import { spawn } from 'node:child_process';
import { createProject } from './create-project.mjs';
const [command, ...args] = process.argv.slice(2);
function run(commandArgs) { return new Promise((resolve, reject) => { const child = spawn('npm', commandArgs, { shell: process.platform === 'win32', stdio: 'inherit' }); child.on('error', reject); child.on('close', code => code === 0 ? resolve() : reject(new Error(`npm ${commandArgs.join(' ')} failed`))); }); }
if (command === 'bootstrap') { for (const step of [['run', 'doctor'], ['run', 'sources:download'], ['run', 'sources:audit'], ['run', 'security'], ['run', 'sync', '--', '--dry-run'], ['run', 'test']]) await run(step); }
else if (command === 'create') await createProject(args);
else if (command === 'init') console.log('Local hook is tracked at .githooks/pre-commit. Activate it manually with: git config core.hooksPath .githooks');
else if (command === 'format') console.log('No formatter dependency is required; files use .editorconfig conventions.');
else { console.error('Usage: project-starter.mjs <bootstrap|create|init|format>'); process.exitCode = 1; }
