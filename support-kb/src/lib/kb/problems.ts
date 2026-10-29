import { causeOf, type Report, type Tenant } from './causes';

export type Problem = 'parser' | 'hint' | 'day-shift' | 'unplaced';
export const problemOrder: Problem[] = ['parser', 'hint', 'day-shift', 'unplaced'];

// JSON object key order is not report content; array order remains significant.
function canonical(value: unknown): string {
  if (Array.isArray(value)) return '[' + value.map(canonical).join(',') + ']';
  if (value !== null && typeof value === 'object') {
    return '{' + Object.entries(value).sort(([a], [b]) => a.localeCompare(b))
      .map(([key, item]) => JSON.stringify(key) + ':' + canonical(item)).join(',') + '}';
  }
  return JSON.stringify(value);
}

// Proposed ticket coverage, separate from the desk's unchanged cause classifier.
// A flagged symptom gets its own investigation even before its mechanism is known.
export function allocateReports(
  reports: Report[],
  tenantOf: (report: Report) => Tenant | undefined,
  flaggedIds: readonly string[],
) {
  const seen = new Map<string, Report>();
  for (const report of reports) {
    const previous = seen.get(report.id);
    if (previous && canonical(previous) !== canonical(report)) {
      throw new Error(`Conflicting export rows for ${report.id}; reconcile before counting`);
    }
    seen.set(report.id, report);
  }
  const flagged = new Set(flaggedIds);
  if (flagged.size !== flaggedIds.length) throw new Error('Duplicate diagnostic note ID');
  const scoped = [...seen.values()].filter(report => report.mergedInto === 4471);
  const ids = new Set(scoped.map(report => report.id));
  for (const id of flagged) {
    if (!ids.has(id)) throw new Error(`Diagnostic note ${id} is outside the supplied ticket`);
  }
  return problemOrder.map(problem => ({
    problem,
    reports: scoped.filter(report => {
      const allocated: Problem = flagged.has(report.id) ? 'day-shift' : causeOf(report, tenantOf(report)) ?? 'unplaced';
      return allocated === problem;
    }).sort((a, b) => a.id.localeCompare(b.id)),
  }));
}
