import { managedJson, managedMarkdown } from '../lib/fs-safe.mjs';
export const target = 'kiro';
export async function plan(inputs) {
  const files = new Map();
  files.set('.kiro/settings.json', managedJson({ settings: { casops: { localOnly: true } } }));
  files.set('.kiro/mcp.json', managedJson(inputs.mcp));
  for (const rule of inputs.rules) files.set(`.kiro/steering/${rule.name}`, managedMarkdown(rule.content));
  for (const skill of inputs.skills) files.set(`.kiro/skills/${skill.id}/SKILL.md`, managedMarkdown(skill.content));
  for (const hook of inputs.hooks) files.set(`.kiro/hooks/${hook.id}.json`, managedJson({ event: hook.event, command: hook.command }));
  return files;
}
