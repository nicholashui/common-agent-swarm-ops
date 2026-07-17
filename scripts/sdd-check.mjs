import { readFile } from 'node:fs/promises';
import { exists } from './lib/fs-safe.mjs';
const base = '.kiro/specs/casops-bootstrap';
const requirements = ['requirements.md', 'design.md', 'tasks.md', 'trace.md', 'evidence.md'];
const headings = { 'requirements.md': ['# Requirements', 'Acceptance Criteria'], 'design.md': ['# Design', 'Requirements trace'], 'tasks.md': ['# Tasks', 'Validation'], 'trace.md': ['# Traceability', 'REQ-'], 'evidence.md': ['# Evidence', 'sdd:check'] };
const failures = [];
for (const file of requirements) { if (!await exists(`${base}/${file}`)) { failures.push(`missing ${file}`); continue; } const text = await readFile(new URL(`../${base}/${file}`, import.meta.url), 'utf8'); for (const heading of headings[file]) if (!text.includes(heading)) failures.push(`${file} lacks ${heading}`); }
if (failures.length) { console.error(`SDD gate failed: ${failures.join('; ')}`); process.exitCode = 1; } else console.log('SDD gate: OK');
