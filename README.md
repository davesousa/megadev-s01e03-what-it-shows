# S01E03 — local engineering-update draft

This candidate addresses MEGA.dev's [“what it shows” challenge](https://hq.mega.dev/challenges/what-it-shows): separate the problems merged into ticket #4471, state report coverage, and add a signed knowledge-base page with its rendered presentation.

**Status: engineering-status update approved for publication by Dave.** The course accepted the first ticket step but has not declared the challenge solved. The course-page engineering notice reports the parser fixed and booking-v3 retired. GitHub issue #1 is closed as completed, #2 is closed as not planned, and #3 remains open as an unresolved investigation. No second course submission was made.

## Current ticket status

The course-page update reports #4471 closed “05 oct”: parser FIXED; hint WON'T FIX because booking-v3 was retired. The notice does not state a year. Report counts remain the 2026-10-04 snapshot; the engineering observation and GitHub tracking update are dated 2026-10-29.

- Issue #1: closed as completed, citing the reported parser fix.
- Issue #2: closed as not planned, citing retirement rather than a hint correction.
- Issue #3: open; no case-specific resolution is supplied for its five reports.

The engineering notice reports outcomes; no production repair was independently reproduced. Publication and the two closures were approved by Dave. Another course submission requires separate authorization.

## Contents

- [Parser issue body](https://github.com/davesousa/megadev-s01e03-what-it-shows/issues/1): 374 reports after separating the desk-noted anomalies.
- [Booking-v3 hint issue body](https://github.com/davesousa/megadev-s01e03-what-it-shows/issues/2): 33 reports.
- [Date-shift and invite-timing investigation](https://github.com/davesousa/megadev-s01e03-what-it-shows/issues/3): 5 reports, without claiming a proved common cause.
- [Exact coverage ledger](evidence/report-coverage.json): 374 + 33 + 5 = 412 unique report IDs.
- [New signed page](support-kb/src/routes/kb/decisions/0002-triage-by-cause/+page.svx) and its [computed evidence component](support-kb/src/lib/kb/IncidentEvidence.svelte).
- [Self-contained interactive page](rendered/page.html): open in a browser without installing dependencies. Its internal KB links target the companion site below.
- [Complete rendered KB](site/kb/index.html): serve `site/` locally to exercise its root-relative links and module loading.
- [Original ZIP](evidence/kb-export-267efc5e.zip), [provenance](PROVENANCE.json), [original-file hashes](ORIGINALS.json) and the final [file manifest](MANIFEST.json).

The original accepted decision and all other export files are preserved. The new decision is **proposed**, with owner Dave. Its frontmatter signature is the exact ticket issued by the course's S01E03 start response, producing desk ref **DR-XTR7-D414**. The course requires that issued value on the public page; it remains valid there after expiry. The first course claim accepted the ticket step only; final course acceptance remains pending.

## Review and reproduce

Run from this directory with Python 3 and a compatible Node runtime available on PATH:

```sh
python3 tooling/verify.py --require-node
python3 -m http.server 8767 --bind 127.0.0.1 --directory site
```

Open `http://127.0.0.1:8767/kb/`. The verifier is read-only and makes no network requests. It checks frozen files, original integrity, schema, an independently implemented partition, exact report membership, rendered counts, signature, native index discovery, and internal links. Its success is not a course acceptance result.

For a fresh dependency installation and rebuild:

```sh
npm ci
npm run build
npm run render
node tooling/coverage.mjs > /tmp/s01e03-coverage-reproduced.json
```

The site rebuild writes `.rebuilt-site/`; the single-page rebuild writes `.single-build/standalone.html`. Both leave reviewed artifacts untouched. The scripts and exact dependency lockfile are included. Render-age text can change with the date; compare semantics and inputs as well as hashes. Installation requires access to the declared registry packages unless they are cached. This workspace also verified a separate offline cached installation; that does not guarantee every other machine has those caches.

## Limits and publication scope

Counts describe proposed ticket coverage for the supplied 2026-10-04 export. Historical tenant settings, production reproduction, production fix behavior, additional real-world causes and final course acceptance are unverified. Current GitHub dispositions are recorded above. The old classifier still returns 379/33; proposed ticket coverage is 374/33/5. The five flagged reports have their own investigation. Four remaining parser assignments lack explicit date pairs and are provisional. Neither model output nor body review proves historical production behavior.

The interactive artifacts embed the complete fictional report dataset and tenant directory; collapsed details do not hide that data. The challenge explicitly calls for public delivery of this course-story material. No unrelated workspace files, account history, credentials, local dependency installations or runtime binaries are included.

The pinned local build toolchain has six low-severity npm audit findings; see [tooling limits](tooling/KNOWN-LIMITS.md). See [publication procedure](PUBLICATION.md) for the authorized delivery steps and separate course boundary. The page links the three filed GitHub issues. Reviewed Markdown drafts and UTF-8 HTML previews remain as evidence; filed issue descriptions use actual issue and repository URLs. Run `python3 tooling/verify.py --require-node --publication-ready` to verify the published artifact locally. No hosted site or production deployment has been configured.
