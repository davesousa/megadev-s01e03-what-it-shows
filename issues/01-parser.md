# Shared month-first parser misreads day-first tenant dates — 374 reports from #4471

**Coverage: 374 unique report IDs** in the 2026-10-04 export: 202 app, 147 email and 25 booking-v2 form reports across 11 tenants. Exact IDs and distributions are in [the coverage ledger](../evidence/report-coverage.json), group `parser`.

## Problem and evidence

The shared parser reads dates month first while these tenants write day first (`support-kb/src/lib/kb/causes.ts`, `causeOf`). A date entered in the tenant's convention should preserve the intended calendar day.

- R-41200, Harbour Dental app, describes 7 April becoming 4 July: a day/month transposition.
- R-41205, Morrow Tax app, describes 3 October becoming 10 March. Its en-US browser and `hint` intake tag do not change the tenant's fr-FR / booking-v2 parser path.
- R-41201 appears to correct R-41200's direction. The export has separate IDs and no explicit correction relationship, so both are retained. This is report coverage, not a count of independently affected customers.

The model supplies the parser explanation; the bodies supply reported symptoms. Production reproduction and historical tenant settings are not supplied.

## Count and boundaries

Deduplicate the 427 rows by ID: 412 unique reports remain, with 15 identical repeats. The unchanged classifier returns 379 parser and 33 hint. Remove the five IDs in `desk-notes.json` from parser coverage because their bodies do not establish a day/month swap; they belong to [the separate date-shift investigation](03-day-shift.md). Final exclusive coverage is **374 parser + 33 form hint + 5 investigation = 412**.

Parser coverage has 351 `parser` intake tags and 23 `hint` tags. Received dates span **2026-04-01–2026-10-04**, preserving source date portions. Of these 374 reports, 370 describe explicit transpositions. Four assignments are provisional: R-41290 asks about a day-first country setting; R-41417 says a dentist visit was on the wrong day without dates; R-41514 describes a verbal-date workaround; R-41615 says October bookings became January without day numbers. Their bodies do not prove the parser mechanism. Retain them under the supplied tenant/path model while seeking original dates; reassign if evidence supports another problem. In particular, do not assume R-41417 rules out a one-day shift.

Sources: original `reports-4471.json`, `tenants/`, `desk-notes.json`, `causes.ts` and `locales.ts` under `support-kb/src/lib/`; proposed coverage is computed by `kb/problems.ts`. No original source is edited.

## Engineering follow-up and acceptance criteria

1. Reproduce the app, email and booking-v2 paths with the recorded tenant settings and original inputs.
2. Make parsing consistent with the declared input convention; test ambiguous valid dates and unambiguous dates through input, storage, reminder and calendar output.
3. Verify the correction separately from [the booking-v3 hint issue](02-form-hint.md).
4. Do not close the date-shift investigation as a parser fix unless reproduction explains its distinct symptoms.

No product fix has been implemented or verified. This is a prepared issue for the supplied snapshot. [The signed KB page](../support-kb/src/routes/kb/decisions/0002-triage-by-cause/+page.svx) explains the complete allocation; [its rendered version](../rendered/page.html) is included.
