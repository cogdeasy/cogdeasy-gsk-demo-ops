# GSK S/4HANA remediation wave

## Overview
Devin for migrations on the ERP Evolution workspace cogdeasy/gsk: take one migration wave from
the scanner backlog and remediate its custom ABAP objects in parallel, one child session and one
PR per object, following the remediated reference pattern. Started by the `gsk-s4-remediation-wave`
automation (Jira label `devin-migrate` on an Epic naming the wave).

## What's Needed From User
- A GSK Jira Epic naming the wave (e.g. `wave 1`) and optionally a list of objects.
- Repo: cogdeasy/gsk (`make setup && make check` must pass).

## Procedure
1. Read the Epic and the repo's `AGENTS.md`. Run `make setup` and `make scan`; read
   `reports/remediation-backlog.md` and `estate/inventory.csv`. Comment on the Epic with the
   wave's objects, findings and engineer-days from the report.
2. For each object in the wave, start one child session with: the object path, its findings, the
   target pattern in `abap/remediated/`, and the definition of done from `AGENTS.md` (scan clean
   with `--fail-on minor`, ABAP Unit test class, inventory `remediated_path`, regenerate reports,
   `make check` green). One PR per object.
3. When the children finish, take each child PR's regenerated `reports/` (its PR branch, not
   main, since the PRs are still unmerged) and post a summary on the Epic: per object the PR link,
   findings cleared and days moved from outstanding to cleared, plus open deviations (findings
   that could not be remediated, left visible). Mark the totals as projected until the PRs merge.
4. For any object with a data-migration impact, note the related `tools/datamig` rule or
   reconciliation check and leave it for the data migration lead.

## Specifications
- One object per child, one PR per object; no scanner changes in remediation PRs.
- Validation: each child PR passes `make check`; each object's line in the Epic summary
  reconciles with `make scan` on that child's PR branch.

## Advice and Pointers
- `ZGSK_MM_BATCH_MOVEMENTS` is the worked example; point children at it.
- Report regeneration conflicts across parallel PRs: each child regenerates on its branch; the
  parent rebases and regenerates after merges.

## Forbidden Actions
- No SAP system access, no transports, no Basis work, no production data.
- Do not silence a scanner rule to make an object pass. Do not merge.
