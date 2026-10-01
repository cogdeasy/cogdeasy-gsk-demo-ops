# R&D support triage

## Overview
Triage one R&D support report about the WebAPI service (cogdeasy/cogdeasy-gsk-ohdsi-webapi):
link duplicates to existing work, reproduce new issues, and fix in-scope bugs. Started by the
`gsk-rd-support-triage-*` automations (a new GSK Jira issue labelled `rd-support`, or a message
in the GSK support Slack channel).

## What's Needed From User
- The report: a GSK Jira issue, or a Slack message with its thread.

## Procedure
1. Read the report. Search open GSK Jira issues for the same symptom: every open Bug (including
   tickets already being worked by Devin, such as the error-mapper bug) and issues labelled
   `rd-support` from the last 14 days. If triggered from Slack, also search the channel history
   for the last 14 days.
2. If it duplicates an existing issue: on Jira, link the new report to the earliest matching
   issue with the Duplicate link type so the new report "duplicates" it; comment with the
   original key, its status and any open PR, and stop. A report that matches a bug already in
   progress joins that work; do not start a second fix.
3. If new and the report came from Slack, create a GSK Jira Bug from it (summary, report text,
   link to the Slack message; no `rd-support` label, so the Jira trigger does not start a second
   session) and reply in the thread with the key. Later steps use that ticket.
4. If new: clone the repo, run `mvn -q -Pwebapi-postgresql test-compile`, reproduce
   (`./reproduce.sh` or a minimal test), find the likely code path, and post the evidence on the
   ticket: reproduction output, file and method, likely cause.
5. If it is an in-scope bug with a clear fix, continue with the `GSK ticket to PR` playbook in
   the same session (including its verification step) and post the PR link. Otherwise label
   `needs-owner` and stop.
6. Update the running tally (ticket comment or Slack thread): duplicate / new / fixed.

## Specifications
- Every report gets a response within the session: duplicate link, triage evidence, or PR.
  Jira reports get it as a ticket comment; Slack reports get it as a thread reply on the
  original message.
- Validation: the report has a Duplicate link, an evidence comment, or a PR link.

## Forbidden Actions
- Do not close user reports; the owning team closes them.
- Do not start a second fix for a bug that already has an open ticket or PR.
