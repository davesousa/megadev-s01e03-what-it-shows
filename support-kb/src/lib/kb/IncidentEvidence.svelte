<script lang="ts">
  import reports from '#lib/data/reports-4471.json';
  import notes from '#lib/data/desk-notes.json';
  import bodyReview from '#lib/data/body-review.json';
  import tickets from '#lib/data/ticket-links.json';
  import { uniqueById, groupByCause, type Report } from '#lib/kb/causes';
  import { allocateReports, type Problem } from '#lib/kb/problems';
  import { tenantOf } from '#lib/kb/locales';

  const unique = uniqueById(reports as Report[]);
  const scoped = unique.filter(r => r.mergedInto === 4471);
  const classified = groupByCause(scoped, tenantOf);
  const allocation = allocateReports(reports as Report[], tenantOf, notes.oneDayMove);
  const groups = allocation.filter(g => g.reports.length);
  const parserBefore = classified.find(g => g.cause === 'parser')?.reports.length ?? 0;
  const hintBefore = classified.find(g => g.cause === 'hint')?.reports.length ?? 0;
  const anomaly = allocation.find(g => g.problem === 'day-shift')!;
  const parser = allocation.find(g => g.problem === 'parser')!;
  const provisional = parser.reports.filter(r => bodyReview.provisionalParserIds.includes(r.id));
  const disagreement = classified.reduce((n, g) => n + g.reports.filter(r => r.meta.intakeTag !== g.cause).length, 0);
  const firstMerge = scoped.flatMap(r => r.mergedAt ? [r.mergedAt.slice(0, 10)] : []).sort()[0];
  const receivedBeforeMerge = scoped.filter(r => r.receivedAt.slice(0, 10) < firstMerge);
  const firstHint = classified.find(g => g.cause === 'hint')?.reports.toSorted((a, b) => Date.parse(a.receivedAt) - Date.parse(b.receivedAt))[0];
  const labels: Record<Problem, string> = {
    parser: 'Shared month-first parser', hint: 'Booking-v3 form hint mismatch',
    'day-shift': 'One-day / cross-city date shifts — investigation', unplaced: 'Unplaced — needs review',
  };
  const ticketFor = (problem: Problem) => problem === 'unplaced' ? null : tickets[problem];
  const dateRange = (rs: Report[]) => {
    const days = rs.map(r => r.receivedAt.slice(0, 10)).sort();
    return `${days[0]} – ${days[days.length - 1]}`;
  };
</script>

<p>
  <strong>{reports.length}</strong> export rows become <strong>{unique.length}</strong> unique report IDs;
  <strong>{reports.length - unique.length}</strong> identical repeat rows are removed.
  <strong>{scoped.length}</strong> unique reports belong to #4471. The proposed ticket allocation below
  covers each report once, in <strong>{groups.length}</strong> problem groups.
</p>

<!-- svelte-ignore a11y_no_noninteractive_tabindex (Horizontal table scrolling needs keyboard focus.) -->
<div class="table-scroll" role="region" aria-label="Proposed ticket coverage" tabindex="0">
  <table>
    <thead><tr><th>Problem</th><th>Reports</th><th>Received dates</th><th>Ticket</th></tr></thead>
    <tbody>
      {#each groups as group (group.problem)}
        {@const ticket = ticketFor(group.problem)}
        <tr data-problem={group.problem}>
          <td>{labels[group.problem]}</td><td>{group.reports.length}</td>
          <td>{dateRange(group.reports)}</td>
          <td>{#if ticket}<a href={ticket.github ?? ticket.preview}>{ticket.github ? 'GitHub issue' : 'Review issue draft'}</a>{:else}Needs investigation{/if}</td>
        </tr>
      {/each}
    </tbody>
  </table>
</div>
{#if Object.values(tickets).some(ticket => !ticket.github)}
  <p>Links marked “Review issue draft” are prepared issue bodies, not filed GitHub issues.</p>
{:else}
  <p>The linked GitHub issues cover this exported snapshot. Filing an issue does not confirm a fix.</p>
{/if}

<p>
  The original classifier still returns <strong>{parserBefore}</strong> parser and
  <strong>{hintBefore}</strong> hint reports. It does not read report bodies.
  The new allocation removes the <strong>{anomaly.reports.length}</strong> desk-flagged reports
  from parser coverage and gives them a separate investigation. No report is counted twice.
  Intake tags disagree with the original classifier for <strong>{disagreement}</strong> reports;
  intake guesses are not used to decide ticket coverage.
</p>

<details>
  <summary>Investigation evidence: {anomaly.reports.length} original report bodies</summary>
  <ul>
    {#each anomaly.reports as report (report.id)}
      <li><code>{report.id}</code> · {report.tenant} · {report.channel}: {report.body}</li>
    {/each}
  </ul>
</details>

<details>
  <summary>Parser evidence: {parser.reports.length - provisional.length} explicit transpositions and {provisional.length} provisional assignments</summary>
  <p>The following bodies lack exact date pairs. Their coverage uses the exported tenant/path model;
    follow up before asserting each report shares the parser mechanism. These annotations come from
    a full manual review of this snapshot, not an automatic detector for new reports.</p>
  <ul>
    {#each provisional as report (report.id)}
      <li><code>{report.id}</code>: {report.body}</li>
    {/each}
  </ul>
</details>

{#each groups as group (group.problem)}
  <details>
    <summary>{labels[group.problem]}: all {group.reports.length} covered report IDs</summary>
    <p class="ids">{group.reports.map(r => r.id).join(', ')}</p>
  </details>
{/each}

<p>
  Before the first merge date, <code>{firstMerge}</code>,
  <strong>{receivedBeforeMerge.length}</strong> of these reports had already arrived.
  {#if firstHint}
    The first hint-classified report, <code>{firstHint.id}</code>, was received
    <code>{firstHint.receivedAt}</code> and merged <code>{firstHint.mergedAt}</code>.
  {/if}
  These use the dates and offsets stated in the source, not a conversion to the reader's timezone.
</p>

<style>
  .table-scroll { overflow-x: auto; }
  table { border-collapse: collapse; min-width: 600px; width: 100%; }
  th, td { text-align: left; padding: 0.6rem; border-bottom: 1px solid var(--muted); }
  .ids { overflow-wrap: anywhere; }
  details { margin-block: 1rem; }
  code { overflow-wrap: anywhere; }
</style>
