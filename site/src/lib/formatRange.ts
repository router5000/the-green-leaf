/**
 * Format a reported min/max percentage (THC, CBD, …) for display.
 * Collapses equal values so we never render "21–21%".
 *   (18, 22) -> "18–22%"   (21, 21) -> "21%"   (null, 21) -> "21%"   (21, null) -> "21%"
 * `sep` lets plain-text/structured-data callers use "-" instead of an en dash.
 */
export function formatPctRange(
  min: number | null | undefined,
  max: number | null | undefined,
  { suffix = '%', sep = '–' }: { suffix?: string; sep?: string } = {},
): string | null {
  const lo = min ?? null
  const hi = max ?? null
  if (lo == null && hi == null) return null
  if (lo == null || hi == null || lo === hi) return `${lo ?? hi}${suffix}`
  return `${Math.min(lo, hi)}${sep}${Math.max(lo, hi)}${suffix}`
}

/** Sentence form: "between 18% and 22%" or "21%". */
export function describePctRange(min: number | null | undefined, max: number | null | undefined): string | null {
  const lo = min ?? null
  const hi = max ?? null
  if (lo == null && hi == null) return null
  if (lo == null || hi == null || lo === hi) return `${lo ?? hi}%`
  return `between ${Math.min(lo, hi)}% and ${Math.max(lo, hi)}%`
}
