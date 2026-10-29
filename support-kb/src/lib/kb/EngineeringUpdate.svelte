<script lang="ts">
  import update from '#lib/data/engineering-update.json';
  import tickets from '#lib/data/ticket-links.json';
  import reports from '#lib/data/reports-4471.json';
  import notes from '#lib/data/desk-notes.json';
  import { allocateReports } from '#lib/kb/problems';
  import { tenantOf } from '#lib/kb/locales';
  import type { Report } from '#lib/kb/causes';

  const outcomes = update.outcomes as Array<{
    problem: 'parser' | 'hint'; label: string; reportedStatus: string;
    detail: string; githubAction: string;
  }>;
  const investigation = allocateReports(reports as Report[], tenantOf, notes.oneDayMove)
    .find(group => group.problem === 'day-shift')?.reports ?? [];
  const issueUrl = (problem: 'parser' | 'hint' | 'day-shift') => tickets[problem].github ?? tickets[problem].preview;
  const issueNumber = (url: string) => url.split('/').filter(Boolean).at(-1);
</script>

<section aria-labelledby="engineering-outcomes">
  <h2 id="engineering-outcomes">Engineering update and ticket status</h2>
  <p>
    The <a href={update.source}>support desk's course-page update</a> reports
    <strong>#{update.incident} closed {update.closedLabel}</strong>.
    The notice does not state a year. It was observed on <time>{update.observedOn}</time>,
    after the first ticket submission. Report coverage still uses the
    <time>{update.reportSnapshotDate}</time> export.
  </p>

  <!-- svelte-ignore a11y_no_noninteractive_tabindex (Scrollable table needs keyboard focus.) -->
  <div class="table-scroll" role="region" aria-label="Reported engineering outcomes and current GitHub status" tabindex="0">
    <table>
      <thead><tr><th>Problem</th><th>Reported engineering outcome</th><th>GitHub status</th></tr></thead>
      <tbody>
        {#each outcomes as outcome (outcome.problem)}
          <tr data-outcome={outcome.problem}>
            <td><a href={issueUrl(outcome.problem)}>{outcome.label} · issue #{issueNumber(issueUrl(outcome.problem))}</a></td>
            <td><strong>{outcome.reportedStatus}</strong><br /><code>{outcome.detail}</code></td>
            <td>{outcome.githubAction}</td>
          </tr>
        {/each}
        <tr data-outcome="day-shift">
          <td><a href={issueUrl('day-shift')}>Investigation · issue #{issueNumber(issueUrl('day-shift'))}</a></td>
          <td>No case-specific outcome stated for the {investigation.length} flagged reports</td>
          <td>Open: unresolved investigation</td>
        </tr>
      </tbody>
    </table>
  </div>

  <p class="tracking-status">
    <strong>GitHub tracking updated: issue #1 closed as completed; issue #2 closed as not planned; issue #3 remains open.</strong>
    A reported parser fix and a decision not to fix a retired form have different outcomes.
    The engineering notice supplies no resolution for the separate investigation.
    These are attributed desk statements; no production fix was independently tested here.
  </p>
</section>

<style>
  .table-scroll { overflow-x: auto; }
  table { width: 100%; min-width: 620px; border-collapse: collapse; }
  th, td { padding: 0.65rem; text-align: left; vertical-align: top; border-bottom: 1px solid var(--muted); }
  code { overflow-wrap: anywhere; }
  .tracking-status { border-left: 3px solid var(--warn); padding-left: 1rem; }
</style>
