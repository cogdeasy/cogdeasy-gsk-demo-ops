# Post-migration metrics: WebAPI on Spring Boot 2.7 / Java 17 (GSK-55)

Measured locally on 2026-10-20 on WebAPI branch `devin/gsk-55-spring-boot-2-7`, commit
8cbf8114, JDK 17 (`mvn -B -Pwebapi-postgresql test`). `main` is unchanged until a named GSK
approver merges the PR, so `docs/BASELINE.md` stays the live-demo baseline. Quote CI on the day.

| metric | `main` (Boot 1.5, JDK 8) | branch (Boot 2.7, JDK 17) |
|---|---|---|
| unit tests (surefire) | 237 run, 0 failures, 3 skipped | 237 run, 0 failures, 0 errors, 3 skipped |
| integration tests (failsafe) | 11 run, 0 failures, 1 skipped | 11 run, 0 failures, 0 errors, 1 skipped |
| total | 248 run, 244 passed, 0 failures, 4 skipped | 248 run, 244 passed, 0 failures, 4 skipped |
| JaCoCo lines, `org.ohdsi.webapi.util` | 362 / 730 = 49.6% | 356 / 731 = 48.7% |
| JaCoCo branches, `org.ohdsi.webapi.util` | 148 / 346 = 42.8% | 147 / 346 = 42.5% |
| JaCoCo lines, all | 9,724 / 131,990 = 7.4% | 9,651 / 132,012 = 7.3% |
| `./reproduce.sh` (GSK-102) | exit 1, 3 of 4 unsafe | exit 1, 3 of 4 unsafe (same four lines, kept for Q1) |
| local stack `/WebAPI/info`, `/source/sources` | 200, 200 | 200, 200 |
| Flyway 4.2.0 on a fresh schema | 153 + 5 migrations applied | 153 + 5 migrations applied |
| Trivy CVEs in `WebAPI.war` (unique, all severities) | 187 (17 critical, 81 high) | 165 (13 critical, 69 high) |

Coverage drop in `util`: lines that were only hit as a side effect of Boot 1.5 start-up
(`GenericExceptionMapper` class load, `SourceUtils.hasSourceDaimon`) plus one new javac 17 line
entry. No logic changed; recorded as DEV-GSK-55-3 in the WebAPI evidence pack.

Trivy: 38 CVEs closed (4 critical, 20 high), 16 new (8 high, 0 critical) in Boot 2.7.18-managed
Tomcat 9.0.83, Spring 5.3.31 and Micrometer 1.9.17. Detail:
`validation/changes/GSK-55/evidence/trivy-summary.md` in WebAPI.

Known differences seen by clients: the 409 error body gains `"originalMessage":null` (Spring 5),
DEV-GSK-55-2. Dates stay epoch milliseconds. REST docs (Miredot) are not built on Java 17.

The playbook is `playbooks/gsk-boot2-migration.md`; the ADR is WebAPI
`docs/adr/0001-spring-boot-2-7-java-17.md`.
