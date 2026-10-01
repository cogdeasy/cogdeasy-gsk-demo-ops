# GSK refine request

## Overview
Turn a rough GSK request into a ticket a developer and a validation lead can act on: problem
statement, acceptance criteria, draft URS lines, impacted code and an initial risk call. The
business analyst / product owner reviews and accepts. Started by the `gsk-refine` automation
(Jira label `devin-refine`).

## What's Needed From User
- A GSK Jira issue with the rough request in the description.
- Repo the request concerns (default cogdeasy/cogdeasy-gsk-ohdsi-webapi).

## Procedure
1. Read the issue and any linked issues. Comment "Devin is refining this: <session link>".
2. Find the code path the request touches (code search / Ask Devin on the repo). Note file paths
   and existing tests.
3. Search open GSK issues for duplicates or overlap; list any you find.
4. Draft, as one Jira comment:
   - problem statement (2-3 lines, user language);
   - acceptance criteria AC1..ACn, each testable (given / when / then);
   - draft URS lines `URS-<key>-n`, one per AC;
   - impacted components with file paths and existing tests;
   - initial risk call (low / medium / high) using the questions in
     `validation/risk-assessment.md` of the WebAPI repo, with one line of reasoning;
   - open questions for the BA, and the roles that will be involved (dev, test, CSV lead, QA,
     scientist for UAT).
5. Add the label `refined-draft`. Do not edit the description; the BA accepts by copying the AC in.

## Specifications
- Every AC is testable and maps to exactly one draft URS line.
- Risk call is a proposal for the CSV lead, not a decision.
- Validation: one comment on the issue with all sections above; label `refined-draft` present.

## Advice and Pointers
- Keep AC in the scientist's language; put technical detail under "impacted components".
- If the request is really two changes, say so and propose a split.

## Forbidden Actions
- Do not write code or open a PR.
- Do not change the issue's status, priority, assignee or description.
- Do not add any `devin*` trigger label.
