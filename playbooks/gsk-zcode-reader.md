# Z-code reader

## Overview
Produce an analysis-only brief of one ABAP object in cogdeasy/cogdeasy-gsk-abap2xlsx:
dependencies, S/4HANA simplification and clean-core risk, defects found by reading, and ABAP
Unit test designs. Started by the `gsk-zcode-reader` automation (Jira label `devin-abap`).

## What's Needed From User
- A GSK Jira ticket naming the target object (e.g. `ZEXCEL_TEMPLATE_GET_TYPES`).

## Procedure
1. Read the ticket and `AGENTS.md`; locate the target object's source file.
2. Read the object end to end and record the line count (`wc -l`).
3. Map dependencies: custom classes/interfaces/exceptions, forms, function modules
   (`CALL FUNCTION`), SAP classes, DDIC tables. State the FI/CO, MM and SD tables touched, or none.
4. Rate S/4 risk: simplification items and clean core, naming the unreleased APIs.
5. List defects found by reading with file:line, trigger and impact (e.g. a missing `sy-subrc`
   check after `READ TABLE` or a function call).
6. Design one ABAP Unit test per defect (given / when / expect).
7. Write `docs/zcode/<object>.md` from `docs/zcode/TEMPLATE.md` and run `npm run lint`
   (0 issues).
8. Open a PR and comment on the ticket with the PR link and the counts: lines read,
   dependencies, defects, test designs.

## Specifications
- The brief states "analysis only, not run in an SAP system" at the top.
- Every defect has a file:line reference and a matching test design.
- Validation: `npm run lint` reports 0 issues and the PR's `abaplint` check is green.

## Advice and Pointers
- No frontend or SAP system exists here; verification is the lint run and CI.

## Forbidden Actions
- Do not claim defects are confirmed or tests pass on an SAP system.
- No Basis, click-configuration, data migration or S/4 conversion work.
