import { spawn } from 'node:child_process';
const child = spawn('npm', ['run', 'sdd:check'], { shell: process.platform === 'win32', stdio: 'inherit' });
child.on('close', code => { if (code) process.exitCode = code; else console.log('Review: specification gate passed; human approval remains required for high-impact changes.'); });
