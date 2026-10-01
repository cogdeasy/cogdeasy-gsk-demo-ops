# GxP evidence pack

## Overview
Draft the GxP change evidence for a PR on cogdeasy/cogdeasy-gsk-ohdsi-webapi: change record,
URS delta and traceability rows, committed to the PR branch for the named GSK approver to
complete. Started by the `gsk-gxp-evidence-pack` automation (GitHub PR opened).

## What's Needed From User
- The PR (URL or number) and its linked GSK Jira ticket.

## Procedure
1. Read the PR, its linked Jira ticket and the acceptance criteria. If the PR has no ticket
   (e.g. tooling or docs only), post a short comment saying no evidence pack is needed and stop.
2. Draft `validation/changes/CR-<ticket>.md` from `validation/change-record.md`. Leave the
   reviewer, decision and date blank.
3. Draft the URS delta from `validation/urs-delta.md`: one URS line per new or changed
   behaviour, sourced to the ticket AC.
4. Append rows to `validation/traceability.csv`: urs_id, requirement, ticket, commit, test,
   result, reviewer (blank).
5. Check that every URS line maps to at least one test in the PR.
6. Commit the drafts to the PR branch and post a PR comment summarising: tier, URS count, trace
   rows, risk, rollback, and the audit events so far (session created, PR opened).

## Specifications
- Draft only; the named GSK approver completes and signs in GSK's quality system.
- Every URS line maps to at least one test.
- Validation: the CR file and traceability rows are on the PR branch and the summary comment is
  posted.

## Advice and Pointers
- Documentation-only change; no app or frontend run is needed. CI on the PR re-runs on the
  new commit.

## Forbidden Actions
- Do not fill the reviewer, decision or date fields. Do not approve or merge.
- Do not change application code.
