# R&D support triage

Used by the `gsk-rd-support-triage` automation (Jira label `rd-support`, or a message in the
GSK support Slack channel). Repo: cogdeasy/cogdeasy-gsk-ohdsi-webapi.

## Procedure

1. Read the new report. Search open GSK Jira issues for the same symptom: every open Bug
   (including tickets already being worked by Devin, such as the error-mapper bug) and issues
   labelled `rd-support` from the last 14 days. If triggered from Slack, also search the
   channel history for the last 14 days.
2. If it duplicates an existing issue: on Jira, link the new report to the earliest matching
   issue with the Duplicate link type so the new report "duplicates" it; comment with the
   original key, its status and any open PR, and stop. A report that matches a bug already in
   progress joins that work; do not start a second fix.
3. If new and the report came from Slack, first create a GSK Jira Bug from it (summary, the
   report text, a link to the Slack message; no `rd-support` label, so the Jira trigger does not
   start a second session) and reply in the thread with the key. Steps 3 and 4 then use that
   ticket. If new: clone the repo, `mvn -q test-compile`, reproduce (`./reproduce.sh` or a minimal
   test), find the likely code path, and post the evidence on the ticket: reproduction output,
   file and method, likely cause.
4. If it is an in-scope bug with a clear fix, continue with the `gsk-ticket-to-pr` playbook
   in the same session and post the PR link. Otherwise label `needs-owner` and stop.
5. Keep a running tally (ticket comment or Slack thread): duplicate / new / fixed.

## Specifications

- Every report gets a response within the session: duplicate link, triage evidence, or PR.
  Jira reports get it as a ticket comment; Slack reports get it as a thread reply on the
  original message (link the original Slack message or Jira key for duplicates).

## Forbidden actions

- Do not close user reports; the owning team closes them.
