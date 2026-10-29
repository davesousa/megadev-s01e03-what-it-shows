// Reproduce the page's allocation as portable, exact report membership evidence.
// Writes only to stdout; redirect to a NEW scratch file to compare with the frozen ledger.
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { build } from 'esbuild';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const data = path.join(root, 'support-kb/src/lib/data');
const read = async name => JSON.parse(await fs.readFile(path.join(data, name), 'utf8'));
const reports = await read('reports-4471.json');
const notes = await read('desk-notes.json');
const tenants = new Map();
for (const file of (await fs.readdir(path.join(data, 'tenants'))).sort()) {
  if (!file.endsWith('.json')) continue;
  const t = await read('tenants/' + file); tenants.set(t.handle, t);
}
const result = await build({entryPoints:[path.join(root, 'support-kb/src/lib/kb/problems.ts')],
  bundle:true, platform:'node', format:'esm', write:false});
const { allocateReports } = await import('data:text/javascript;base64,' + Buffer.from(result.outputFiles[0].text).toString('base64'));
const groups = allocateReports(reports, r => tenants.get(r.tenant), notes.oneDayMove);
const counts = values => Object.fromEntries([...new Set(values)].sort().map(v => [v, values.filter(x => x === v).length]));
console.log(JSON.stringify({
  scope:'Proposed exclusive ticket coverage for the 2026-10-04 export; not proven root causes.',
  rawRows: reports.length,
  uniqueIDs: new Set(reports.map(r => r.id)).size,
  groups: groups.map(g => ({problem:g.problem, count:g.reports.length,
    ids:g.reports.map(r => r.id), channels:counts(g.reports.map(r => r.channel)),
    tenants:counts(g.reports.map(r => r.tenant)), intakeTags:counts(g.reports.map(r => r.meta.intakeTag)),
    firstReceived:g.reports.map(r => r.receivedAt.slice(0,10)).sort()[0] ?? null,
    lastReceived:g.reports.map(r => r.receivedAt.slice(0,10)).sort().at(-1) ?? null,
    basis:g.problem === 'day-shift' ? 'desk-notes.oneDayMove; full body review; mechanism unresolved' :
      g.problem === 'unplaced' ? 'classifier unresolved; requires investigation' : 'exported tenant/form/channel rule after removing desk-noted anomalies',
  })),
}, null, 2));
