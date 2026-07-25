import { readFile } from 'node:fs/promises';
import { exists } from './lib/fs-safe.mjs';

const SPEC_GATES = [
  {
    base: '.kiro/specs/casops-bootstrap',
    files: {
      'requirements.md': ['# Requirements', 'Acceptance Criteria'],
      'design.md': ['# Design', 'Requirements trace'],
      'tasks.md': ['# Tasks', 'Validation'],
      'trace.md': ['# Traceability', 'REQ-'],
      'evidence.md': ['# Evidence', 'sdd:check'],
    },
  },
  {
    base: '.kiro/specs/migration-redesign',
    files: {
      'requirements.md': ['# Requirements', 'Acceptance Criteria'],
      'design.md': ['# Technical Design', 'Requirement Traceability'],
      'tasks.md': ['# Implementation Plan', '## Tasks'],
    },
    metadata: 'tasks.meta.json',
  },
  {
    base: '.kiro/specs/special-business-agents',
    files: {
      'requirements.md': ['# Requirements', 'Acceptance Criteria'],
      'design.md': ['# Technical Design', 'Primary coverage'],
      'tasks.md': ['# Implementation Plan', '## Tasks'],
    },
    metadata: 'tasks.meta.json',
  },
];

const failures = [];
const projectRoot = new URL('../', import.meta.url);

async function readProjectFile(relativePath) {
  return readFile(new URL(relativePath, projectRoot), 'utf8');
}

for (const spec of SPEC_GATES) {
  for (const [file, requiredHeadings] of Object.entries(spec.files)) {
    const relativePath = `${spec.base}/${file}`;
    if (!await exists(relativePath)) {
      failures.push(`missing ${relativePath}`);
      continue;
    }
    const text = await readProjectFile(relativePath);
    for (const heading of requiredHeadings) {
      if (!text.includes(heading)) failures.push(`${relativePath} lacks ${heading}`);
    }
  }

  if (spec.metadata === undefined) continue;
  const metadataPath = `${spec.base}/${spec.metadata}`;
  if (!await exists(metadataPath)) {
    failures.push(`missing ${metadataPath}`);
    continue;
  }
  try {
    const metadata = JSON.parse(await readProjectFile(metadataPath));
    const propertyResults = metadata?.pbtResults;
    if (propertyResults === null || typeof propertyResults !== 'object') {
      failures.push(`${metadataPath} lacks pbtResults`);
      continue;
    }
    for (const [task, result] of Object.entries(propertyResults)) {
      if (result?.status !== 'passed') {
        failures.push(`${metadataPath} has non-passing pbtResult: ${task}`);
      }
    }
  } catch {
    failures.push(`${metadataPath} is not valid JSON`);
  }
}

if (failures.length) {
  console.error(`SDD gate failed: ${failures.join('; ')}`);
  process.exitCode = 1;
} else {
  console.log('SDD gate: OK');
}
