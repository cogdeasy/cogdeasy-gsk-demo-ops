# GSK release pack

## Overview
For the release / change manager: gather the merged changes for a release, and draft release
notes, the change-board pack, and the deployment and rollback plan, with links to each change's
evidence pack and validation summary. Started by the `gsk-release-pack` automation (Jira label
`devin-release` on a release Task).

## What's Needed From User
- A GSK Jira release Task naming the release (e.g. `2.15.x maintenance`) and its scope (fix
  version, list of keys, or a date range).

## Procedure
1. Read the Task. Resolve the scope to a list of merged PRs on cogdeasy/cogdeasy-gsk-ohdsi-webapi
   and their Jira keys.
2. For each change: title, risk level and route from its risk assessment, evidence pack link, QA
   checklist status, open deviations.
3. Draft Markdown on a branch `devin/<key>-release-pack` in the WebAPI repo
   under `validation/releases/<release>/`: `release-notes.md` (user-facing, scientist language),
   `change-board-pack.md` (changes table, risk summary, validation status, open items,
   go / no-go criteria), `deploy-rollback-plan.md` (steps, checks, rollback trigger and steps,
   owner per step).
4. Open one PR and comment on the Task with the link and a go / no-go readiness summary.

## Specifications
- Any change without QA sign-off is listed as blocking, not omitted.
- Validation: three files on the PR; the comment states blocking items.

## Advice and Pointers
- Rollback for this repo is "revert PR, redeploy previous WAR"; call out any change with a schema
  migration because it needs a down-migration or restore step.

## Forbidden Actions
- Do not tag, release, deploy or merge.
- Do not mark the change-board decision.
