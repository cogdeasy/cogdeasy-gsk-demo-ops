# Baseline on cogdeasy-gsk-ohdsi-webapi `main`

Measured locally with JDK 8 (`mvn -B -Pwebapi-postgresql test`) on the scaffolding branch,
before any demo ticket is worked. Re-measure from CI on the day and quote CI.

| metric | value |
|---|---|
| unit tests (surefire) | 237 run, 0 failures, 3 skipped |
| integration tests (failsafe) | 11 run, 0 failures, 1 skipped |
| total | 248 run, 244 passed, 0 failures, 4 skipped |
| JaCoCo lines, `org.ohdsi.webapi.util` | 362 / 730 = 49.6% |
| JaCoCo branches, `org.ohdsi.webapi.util` | 148 / 346 = 42.8% |
| `./reproduce.sh` (GSK-102) | exit 1, 3 of 4 scenarios unsafe |

`./reproduce.sh` output on the unfixed code:

```
FAIL   no cause                       mapper threw java.lang.NullPointerException
FAIL   single cause                   mapper threw java.lang.NullPointerException
FAIL   nested cause without Detail    409 "duplicate key value violates unique constraint "uq_cs_name""  <- raw database text
ok     nested cause with Detail       409 "Key (name)=(Diabetes) already exists."

REPRODUCED: 3 of 4 scenarios return an unsafe response
```

Upstream note: OHDSI/WebAPI `master` (a5476f20) does not compile its tests
(`CDMResultsAnalysisRunnerTest` ambiguous `query(...)` stub); the scaffolding PR fixes the
stub so `tests` can run.

Trivy counts come from the first `scan` run on `main`; fill in after the scaffolding PR merges.
