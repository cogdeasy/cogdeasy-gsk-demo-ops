# GxP evidence pack

Used by the `gsk-gxp-evidence-pack` automation (GitHub PR opened on cogdeasy-gsk-ohdsi-webapi).

## Procedure

1. Read the PR, its linked Jira ticket and the acceptance criteria.
2. Draft `validation/changes/CR-<ticket>.md` from `validation/change-record.md`. Leave
   reviewer, decision and date blank.
3. Draft the URS delta from `validation/urs-delta.md`: one URS line per new or changed
   behaviour, sourced to the ticket AC.
4. Append rows to `validation/traceability.csv`: urs_id, requirement, ticket, commit, test,
   result, reviewer (blank).
5. Commit the drafts to the PR branch and post a PR comment summarising: tier, URS count,
   trace rows, risk, rollback, and the audit events so far (session created, PR opened).

## Specifications

- Draft only; the named GSK approver completes and signs in GSK's quality system.
- Every URS line maps to at least one test.

## Forbidden actions

- Do not fill the reviewer, decision or date fields. Do not approve or merge.
