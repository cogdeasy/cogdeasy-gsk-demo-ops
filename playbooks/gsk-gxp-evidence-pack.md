# GxP evidence pack

## Overview
Draft the GxP evidence for a PR on cogdeasy/cogdeasy-gsk-ohdsi-webapi, sized by risk: CSA by
default, full GAMP 5 CSV for high-risk changes. The parent session does the risk assessment, then
fans the document set out to child sessions (one per document group) that commit to the same PR
branch, then ties them together. A named GSK approver completes and signs in GSK's quality
system. Started by the `gsk-gxp-evidence-pack` automation (GitHub PR opened).

## What's Needed From User
- The PR (URL or number) and its linked GSK Jira ticket.

## Procedure
1. Read the PR, its linked Jira ticket and AC, and `validation/README.md` (document matrix and
   owners). If the PR has no ticket (tooling or docs only), comment that no evidence pack is
   needed and stop.
2. Risk gate: fill `validation/changes/<key>/risk-assessment.md` from
   `validation/risk-assessment.md` (GAMP category; patient safety, product quality, data
   integrity impact; severity x likelihood x detectability). Result: low, medium or high, and the
   required document list from the README matrix.
3. Always draft yourself: change record (`change-record.md`), URS delta (`urs-delta.md`), and
   traceability rows (`traceability.csv`).
4. Fan out one child session per remaining document group required by the risk result, each
   committing only its own files under `validation/changes/<key>/` on the PR branch (pull before
   push):
   - specification: `fs-ds-delta.md` (+ `validation-plan-delta.md` if high);
   - test evidence: `csa-test-record.md` (low) or `oq-protocol.md` (medium/high), plus
     `iq-checklist.md` if high, using the repo skill `test-engineer`;
   - user acceptance: `pq-uat-script.md` (medium/high) for the R&D scientist;
   - release: `release-notes.md` and `training-note.md`.
5. When the children finish, draft `test-summary-report.md`, `validation-summary-report.md` (high
   only) and `inspection-pack.md` (index of every artefact with links), and check that every URS
   line maps to a test with a recorded result.
6. Post one PR comment: risk result and route (CSA / CSV), documents produced and owner role for
   each, URS count, trace rows, open deviations, rollback, and audit events so far (session
   created, PR opened, Devin Review run, CI runs).

## Specifications
- Draft only. Reviewer, decision, signature and date fields stay blank.
- Every URS line maps to at least one test with a result.
- The document set matches the README matrix for the risk level, no more, no less.
- Validation: all required files on the PR branch under `validation/changes/<key>/` and the
  summary comment posted.

## Advice and Pointers
- Medium is the usual result for silver-tier error handling; high is for changes that touch
  data written to GxP records, audit trail, access control or calculations used in decisions.
- Child sessions must not edit each other's files; the parent owns traceability and the index.
- Documentation-only change; CI re-runs on the new commits.

## Forbidden Actions
- Do not fill reviewer, decision, signature or date fields. Do not approve or merge.
- Do not change application code.
- Do not downgrade a risk rating to shorten the document set.
