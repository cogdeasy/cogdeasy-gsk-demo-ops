# Z-code reader

Used by the `gsk-zcode-reader` automation (Jira label `devin-abap`). Repo: cogdeasy/cogdeasy-gsk-abap2xlsx.

## Procedure

1. Read the ticket and AGENTS.md. Identify the target object.
2. Read the object end to end; record the line count (`wc -l`).
3. Map dependencies: custom classes/interfaces/exceptions, forms, function modules
   (`CALL FUNCTION`), SAP classes, DDIC tables. State FI/CO, MM, SD tables touched, or none.
4. Rate S/4 risk: simplification items and clean core, naming the unreleased APIs.
5. List defects found by reading with file:line, trigger and impact (e.g. missing `sy-subrc`
   check after `READ TABLE` or a function call).
6. Design one ABAP Unit test per defect (given / when / expect).
7. Write `docs/zcode/<object>.md` from `docs/zcode/TEMPLATE.md`, run `npm run lint` (0 issues),
   open a PR, and comment on the ticket with the PR link and the counts: lines read,
   dependencies, defects, test designs.

## Specifications

- The brief says "analysis only, not run in an SAP system" at the top.

## Forbidden actions

- Do not claim defects are confirmed or tests pass on an SAP system.
- No Basis, click-configuration, data migration or S/4 conversion work.
