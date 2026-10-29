# Publication record and procedure

Dave authorized publication of the reviewed package and creation of the three issues on
2026-10-29. The issues are filed; the signed page links their returned URLs. Reviewed issue
drafts remain as evidence. Course submission and evaluation are not authorized.

## Authorized now

GitHub issue creation/link updates and publication of this reviewed package are authorized.
Do not contact the course or trigger a solve/evaluation check.
Target repository, created earlier: `davesousa/megadev-s01e03-what-it-shows`.

## Authorized publication procedure

1. Use a dedicated checkout of that repository, not the MegaDev workspace. Confirm its
   current state and check for already-filed matching issues before creating duplicates.
2. Prepare publication copies of `issues/01-parser.md`, `02-form-hint.md` and
   `03-day-shift.md`: convert their file-relative links to explicit URLs for the
   approved repository and publication branch. Relative Markdown paths in a GitHub
   issue do not have the same base as files in a repository. File the approved
   descriptions, save the returned issue URLs, then replace related-ticket links in
   those descriptions with the actual issue URLs and verify their bodies/counts.
   Preserve the exact local draft bodies as review evidence; record publication copies
   and any approved link-only updates. Verify every resulting link after the files
   are published. Do not assume an issue body can be filed verbatim with working links.
   Never predict issue numbers. Any unexpected existing work requires reconciliation.
3. Put those returned URLs in `support-kb/src/lib/data/ticket-links.json` (`github`
   fields). Preserve the draft paths for the audit trail. The page will then show links
   labelled “GitHub issue” instead of “Review issue draft”.
4. Rebuild the native site and standalone HTML in scratch, then promote the verified
   outputs into `site/` and `rendered/page.html`. Regenerate MANIFEST.json. Run
   `python3 tooling/verify.py --require-node --publication-ready`; it requires all
   three recorded URLs but does not contact GitHub or prove those URLs exist.
5. Verify the actual GitHub issue URLs read-only, served page navigation, signature,
   complete coverage and unchanged original sources. Record evidence against the new
   manifest. Commit/push only the approved package from the dedicated checkout.
   Record the commit SHA and confirm the repository's published files read-only.

Course submission requires separate authorization. Publication approval does not permit
an evaluation attempt, course start/resume/claim/proof action or submission. Clarify the
course flow with Dave before those actions. Current permissions do not allow probing it.

## Local review links

The page now links the actual GitHub issues; the preserved UTF-8 `/issues/*.html` previews
show the reviewed drafts. The
native build generates those previews from the exact Markdown bodies and copies the
Markdown to `site/issues/` for download. Each preview includes related-draft and KB navigation.
The standalone HTML carries the same root-relative links and should be served beside the
full site when exercising navigation. Issue Markdown uses repository-relative source,
ledger and related-issue links for GitHub. The reviewed drafts are preserved; the filed issue descriptions use absolute repository and actual issue URLs.
