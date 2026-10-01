# R&D support triage

Used by the `gsk-rd-support-triage` automation (Jira label `rd-support`, or a message in the
GSK support Slack channel). Repo: cogdeasy/cogdeasy-gsk-ohdsi-webapi.

## Procedure

1. Read the new report. Search open Jira issues labelled `rd-support` from the last 14 days
   (and the Slack channel history if triggered from Slack) for the same symptom.
2. If it duplicates an existing report: link it ("is duplicated by"), comment with the
   original key and its status, and stop.
3. If new: clone the repo, `mvn -q test-compile`, reproduce (`./reproduce.sh` or a minimal
   test), find the likely code path, and post the evidence on the ticket: reproduction output,
   file and method, likely cause.
4. If it is an in-scope bug with a clear fix, continue with the `gsk-ticket-to-pr` playbook
   in the same session and post the PR link. Otherwise label `needs-owner` and stop.
5. Keep a running tally on the ticket: duplicate / new / fixed.

## Specifications

- Every report gets a response within the session: duplicate link, triage evidence, or PR.

## Forbidden actions

- Do not close user reports; the owning team closes them.
