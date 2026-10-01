# On-call simulator (WebAPI)

Four synthetic alerts for `ohdsi-webapi` so the demo can show Devin taking an on-call page: read the alert, check code and logs, classify it, and propose the next step. Devin investigates and proposes. A human on-call engineer approves any rollback, restart, config change or other prod change.

| file | what |
|---|---|
| `alerts.json` | 4 alerts in a monitoring-tool-neutral webhook shape |
| `expected.json` | answer key, never posted |
| `post_alert.py` | posts one alert or all of them to a Devin webhook (stdlib only) |

Alert fields: `id`, `title`, `severity`, `status`, `service`, `env`, `metric`, `threshold`, `observed`, `started_at`, `runbook_url`, `dashboard_url` (placeholder host), `context`, `sample_logs`. Log lines use the WebAPI Console pattern from `src/main/resources/log4j2.xml` (`%d %p %t %C - %x - %m`); lines starting `[ingress]` are reverse-proxy access logs, which WebAPI itself does not write.

## Wire it up

1. In Devin, create an automation with a **Webhook** trigger ([trigger sources](https://docs.devin.ai/product-guides/automations#trigger-sources)). Action: start session on `cogdeasy/cogdeasy-gsk-ohdsi-webapi`. Prompt: triage the alert in the payload, classify it (real / duplicate / noise), gather evidence, propose the next step, and do not change prod.
2. Copy the webhook URL and secret from the trigger. The secret is shown once.
3. Post:

   ```bash
   export DEVIN_ONCALL_WEBHOOK_URL='<webhook url>'
   export DEVIN_ONCALL_WEBHOOK_SECRET='<secret>'   # sent as X-Webhook-Secret
   python3 oncall-sim/post_alert.py --dry-run       # print payloads only
   python3 oncall-sim/post_alert.py --alert A3      # one alert
   python3 oncall-sim/post_alert.py --all --delay 30
   ```

If the customer pages through PagerDuty, the same automation can use the PagerDuty trigger instead (incident triggered); see the [PagerDuty integration](https://docs.devin.ai/integrations/pagerduty). The webhook route needs no PagerDuty account and is the one to rehearse.

## Answer key

| id | alert | expected |
|---|---|---|
| A1 | p95 latency on `GET /WebAPI/cohortdefinition/` after deploy | real. Investigate, then propose rollback or a query fix |
| A2 | Hikari pool `authDataSource` exhausted | real. Follow the runbook below |
| A3 | 5xx spike, NPE in `GenericExceptionMapper` | duplicate of GSK-1. Comment on GSK-1 and join that work |
| A4 | flapping disk alert on `/var/log` | noise. Suppress and propose a for-duration on the rule |

Details and the evidence Devin should cite are in `expected.json`.

## Runbooks

### A1 latency after deploy

- Confirm the step change lines up with the deploy time and is limited to the list endpoint (`CohortDefinitionService#getCohortDefinitionList`, `@Path("/cohortdefinition")` + `GET /`). Single-item `GET /cohortdefinition/{id}` should be normal.
- Diff the two builds around `CohortDefinitionService`, `CohortDefinitionRepository#list` and the `COHORT_DEFINITION_LIST_CACHE` cache.
- Propose either a rollback to the previous build or a draft PR that fixes the query. The on-call engineer decides.

### A2 Hikari pool exhaustion

The only Hikari pool in WebAPI is `authDataSource` (`org.ohdsi.webapi.AuthDataSource`, pool name set from `spring.datasource.hikari.mbean-name`), so the log reads `authDataSource - Connection is not available, request timed out after 5001ms.`, not Hikari's default `HikariPool-1`. The primary datasource is a non-pooled `DriverManagerDataSource`. Defaults in `pom.xml`: `maximum-pool-size` 5, `minimum-idle` 1, `connection-timeout` 5000 ms. Callers: `JdbcAuthRealm` on `POST /WebAPI/user/login/db`.

1. Check pool stats (`active`, `idle`, `waiting`) on the dashboard or the `authDataSource` MBean (`register-mbeans` is true).
2. Check the login rate on `/user/login/db`. A burst (scripted client, brute force) points to rate limiting, not pool size.
3. On the auth database, look for long-running or idle-in-transaction sessions held by the WebAPI auth user.
4. Propose the fix: kill stuck sessions, restart, or raise `maximum-pool-size` (as a draft PR). Each of these needs the on-call engineer's approval.

### A3 500 spike from GenericExceptionMapper

`GenericExceptionMapper.toResponse` line 61 calls `ex.getCause().getCause().getMessage()` on a `DataIntegrityViolationException`. With no nested cause this throws the NPE. This is GSK-1 (seed `Q1`). Run `./reproduce.sh` in the WebAPI repo (exit 1 = bug present), comment on GSK-1 with the alert and error rate, and point to the GSK-1 PR. Do not open a new ticket.

### A4 flapping disk alert

Usage moves within a 1% band around the threshold and drops after each hourly logrotate. No trend. Close as noise and propose a rule change (for example `> 85% for 30 min`, resolve below 80%) to the rule owner.

## Boundary

Devin reads code, logs and metrics, writes the incident note, and opens draft PRs. It does not roll back, restart, change config or touch prod. The on-call engineer approves each of those, and fix PRs go through the normal CODEOWNERS approver.
