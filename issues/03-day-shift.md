# Investigate one-day / cross-city date shifts and anomalous invite timing — 5 reports from #4471

**Coverage: 5 unique report IDs**, exactly the `oneDayMove` list in the export's `desk-notes.json`: **R-41202, R-41209, R-41236, R-41344, R-41620**. These are removed from parser issue coverage. They span five tenants, two app reports and three email reports, received **2026-04-02–2026-10-04** (source date portions).

## Distinct reported problem

These reports describe date shifts or timing anomalies that the shared month/day-parser explanation does not establish. The export itself flags them separately. Track their investigation now instead of declaring them covered by the parser fix. This issue groups reported symptoms for investigation; it does **not** assert one proved timezone defect or a common technical cause for all five.

| Report | Original body | Evidence needed |
| --- | --- | --- |
| R-41202 | Invite says Tuesday 12 May. Calendar says Monday 11 May. My client turned up on the Monday. We had coffee. | Original invite/calendar fields, intended date, stored value and recipient timezone. A same-month one-day shift is not a day/month transposition. |
| R-41209 | Every booking in June is one day off. Only June. Why only June. | Concrete June inputs/outputs and comparison months; tenant and client zone/settings history. |
| R-41236 | The invite arrived before I made the booking. I would like to know how. | Creation/send/receipt timestamps and their clocks, event identifiers and relevant scheduling logs. The body does not specify a one-day offset. |
| R-41344 | Client in Lisbon got Tuesday. Client in Toronto got Monday. Same meeting. We held it twice. | Intended instant or local date, both calendar payloads and zones. Different local days can correctly represent one instant; the reported duplicate meeting is a scheduling complaint requiring investigation. |
| R-41620 | Tuesday 6 October showed as Monday. I moved it myself. I have stopped reporting these but my colleague says it helps you. | Original and manually corrected event values, render settings and zones. Preserve the manual correction history. |

## Count and boundaries

The unchanged desk classifier assigns all five to `parser` because it checks tenant settings and channel, not the body. Its comment “counted where they're filed, footnoted under it” explains the old display; it does not prove their root cause. The brief asks for each problem found, so unresolved diagnosis is not a reason to hide these reports inside an unrelated fix.

The complete allocation is **374 parser + 33 form hint + 5 investigation = 412** unique reports. All five intake tags say `parser`, which is intake's guess. The [coverage ledger](../evidence/report-coverage.json), group `day-shift`, records the exact membership. The unchanged original reports and desk notes are in `support-kb/src/lib/data/`.

## Investigation completion criteria

1. Preserve and obtain the missing evidence for each row above. Establish whether values represent a date only, a local time or an absolute instant before choosing conversion rules.
2. Reproduce the reported mismatch or document why the observed local dates are expected. Do not label a legitimate timezone conversion as a bug without the intended semantics.
3. Identify the affected path and any shared cause. Split this investigation into linked issues if the evidence establishes distinct defects, retaining each report ID and coverage once.
4. Verify any correction against the original cases. Do not close these reports merely because the [shared parser](01-parser.md) or [form hint](02-form-hint.md) was fixed.

No cause or fix is claimed as verified. [The signed KB page](../support-kb/src/routes/kb/decisions/0002-triage-by-cause/+page.svx) includes all five bodies and separate computed coverage; [its rendered version](../rendered/page.html) is included.
