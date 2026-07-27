/**
 * Shared local (presentation-only) control helpers for screen Homes.
 * Browser remains non-authority: these only mutate React state / session feedback.
 */

/** Cycle a list of labels (date range, period, group-by, etc.). */
export function cycleOption(
  options: readonly string[],
  current: string,
): string {
  if (options.length === 0) return current;
  const index = options.indexOf(current);
  const next = index < 0 ? 0 : (index + 1) % options.length;
  return options[next] ?? options[0] ?? current;
}

/** Toggle membership of a chip in a multi-select set. */
export function toggleChip(
  current: ReadonlySet<string>,
  chip: string,
): ReadonlySet<string> {
  const next = new Set(current);
  if (next.has(chip)) next.delete(chip);
  else next.add(chip);
  return next;
}

/** Case-insensitive includes any selected chip token. */
export function matchesAnyChip(
  haystack: string,
  chips: ReadonlySet<string>,
): boolean {
  if (chips.size === 0) return true;
  const lower = haystack.toLowerCase();
  for (const chip of chips) {
    const token = chip.replace(/▾/g, "").trim().toLowerCase();
    if (token.length === 0) continue;
    if (lower.includes(token) || token.includes(lower) || lower.includes(token.split(/\s+/)[0] ?? "")) {
      return true;
    }
  }
  // Soft match: if nothing literal matches, still show when chip is generic "All"
  for (const chip of chips) {
    if (/^all\b/i.test(chip.trim())) return true;
  }
  return false;
}

export function clampZoom(value: number, min = 0.5, max = 2): number {
  return Math.min(max, Math.max(min, value));
}
