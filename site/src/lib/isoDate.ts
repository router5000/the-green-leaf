/**
 * ISO 8601 datetime with a timezone offset. Naive datetimes (no Z / offset)
 * are treated as UTC so the output is deterministic across server timezones.
 */
export function toIso8601WithOffset(value: string | Date): string {
  if (value instanceof Date) {
    if (Number.isNaN(value.getTime())) throw new RangeError('Invalid Date')
    return value.toISOString()
  }
  const raw = value.trim()
  if (!raw) throw new RangeError('Empty date')
  const hasTz = /(?:Z|[+-]\d{2}:?\d{2})$/i.test(raw)
  const parsed = new Date(hasTz ? raw : /^\d{4}-\d{2}-\d{2}$/.test(raw) ? `${raw}T00:00:00Z` : `${raw}Z`)
  if (Number.isNaN(parsed.getTime())) throw new RangeError(`Invalid date: ${value}`)
  return parsed.toISOString()
}
