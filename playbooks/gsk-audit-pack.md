# GSK audit pack

## Overview
For an auditor or inspection-readiness lead: assemble the full chain for one change, from request
to approval, and check it is complete. Started on demand through the Devin API
(`api/start_audit_pack.sh`), to show Devin driven from GSK's own tooling.

## What's Needed From User
- A GSK Jira key for a change that has a PR.

## Procedure
1. Collect: Jira issue history (created, refined, labelled, transitions, comments), the Devin
   sessions that worked it, the PR (commits, CI runs, Devin Review comments, approvals), and the
   evidence pack under `validation/changes/<key>/`.
2. Build a timeline: who or what did each step, when, with a link. Mark Devin actions vs human
   actions.
3. Check completeness: every required document for the risk level is present; every URS maps to a
   test with a result; the approver on the PR matches CODEOWNERS; no merge happened before
   approval; reviewer fields are filled by a human or still blank (never by Devin).
4. Produce `inspection-pack.md` for the change (from `validation/inspection-pack.md`) and return
   it as structured output and an attachment. Do not commit unless asked.

## Specifications
- Every row in the timeline has a source link.
- Gaps are listed, not fixed.
- Validation: the pack and a gap list are returned.

## Advice and Pointers
- The audit trail of record is Jira history, GitHub history and Devin session logs; this pack is
  an index over them.

## Forbidden Actions
- Do not change any record, ticket, PR or evidence file.
