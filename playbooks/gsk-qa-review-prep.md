# GSK QA review prep

## Overview
Prepare the QA approver's review of a change: check the evidence pack against the document
matrix, check traceability end to end, list gaps and deviations, and pre-fill the QA checklist
for the human QA reviewer. Started by the `gsk-qa-review-prep` automation (GitHub label
`ready-for-qa` on a WebAPI PR).

## What's Needed From User
- The PR with an evidence pack under `validation/changes/<key>/`.

## Procedure
1. Read the PR, the linked ticket, the evidence pack and the Devin Review comments on the PR.
2. Check the pack against the matrix in `validation/README.md` for its risk level: every required
   document present and non-empty, no unexpected ones.
3. Walk traceability: each URS line -> test -> CI result -> commit on the PR head. Flag any URS
   without a passing test, any test result from an older commit, and any open Devin Review
   finding.
4. Check CI: `build`, `tests`, `scan` green on the head commit; new scan findings count.
5. Draft `validation/changes/<key>/qa-review-checklist.md` from the template with each item
   marked met / not met / n/a and the evidence link. Draft `deviation-capa.md` entries for
   anything not met.
6. Commit to the PR branch, wait for `build`, `tests` and `scan` to finish on the new head, then
   post one comment: ready / not ready for QA sign-off, with that head's CI result and the gap
   list.

## Specifications
- The checklist is a preparation for QA, not the QA decision.
- Validation: checklist committed; comment lists every gap with a link.

## Advice and Pointers
- A finding Devin Review raised and the author resolved counts as met only if the fix commit is
  in the PR head.

## Forbidden Actions
- Do not mark the QA decision, sign or date anything. Do not approve, merge or remove labels.
- Do not change application code or other roles' documents.
