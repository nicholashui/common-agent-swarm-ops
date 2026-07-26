/**
 * Stored UI chrome labels. Components must read labels via view.labels / L().
 * Never hardcode product copy in presentation components.
 */

export type ScreenLabels = Readonly<Record<string, string>>;

/** Resolve a required stored label; missing keys fail closed in tests/dev. */
export function L(labels: ScreenLabels, key: string): string {
  const value = labels[key];
  if (typeof value !== "string" || value.length === 0) {
    throw new Error(`Missing stored screen label: ${key}`);
  }
  return value;
}

/** Replace `{name}` placeholders in a stored template string. */
export function Lfmt(
  labels: ScreenLabels,
  key: string,
  vars: Readonly<Record<string, string | number>>,
): string {
  let text = L(labels, key);
  for (const [name, value] of Object.entries(vars)) {
    text = text.split(`{${name}}`).join(String(value));
  }
  return text;
}
