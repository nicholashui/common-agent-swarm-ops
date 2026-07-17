import { managedJson, managedMarkdown } from '../lib/fs-safe.mjs';
export const target = 'claude-code';
export async function plan(inputs) {
  const files = new Map(); const rules = inputs.rules.map(rule => rule.content).join('\n\n');
  files.set('CLAUDE.md', managedMarkdown(`# CASOPS project instructions\n\n${rules}`));
  files.set('.claude/settings.json', managedJson({ permissions: { defaultMode: 'default' } }));
  for (const skill of inputs.skills) files.set(`.claude/skills/${skill.id}/SKILL.md`, managedMarkdown(skill.content));
  files.set('.claude/commands/review.md', managedMarkdown('# Review\nRun `npm run review` and record evidence.'));
  files.set('.claude/agents/reviewer.md', managedMarkdown('# Reviewer\nReview specifications, traceability, tests, and security evidence.'));
  return files;
}
