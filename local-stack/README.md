# local-stack: run the GSK cohort-analytics app locally

PostgreSQL + Eunomia demo CDM, **WebAPI built from `cogdeasy/cogdeasy-gsk-ohdsi-webapi`**, ATLAS 2.15 and an
nginx proxy that serves ATLAS and WebAPI on one origin. Based on [OHDSI Broadsea](https://github.com/OHDSI/Broadsea)
with Broadsea's WebAPI swapped for the fork.

```
browser ──> proxy :8090 ──/atlas──>  atlas   (ohdsi/atlas:2.15.0, config-local.js -> same-origin /WebAPI/)
                        └─/WebAPI─>  webapi  (gsk-webapi:local = fork WAR on Java 8)
                                        └──> atlasdb (ohdsi/broadsea-atlasdb:2.3.0, host port 5433)
                                              schemas: webapi, demo_cdm (CDM + vocab), demo_cdm_results (Achilles)
```

## Quick start

```bash
cd local-stack
scripts/up.sh              # build the fork WAR, build the image, start everything, wait for EUNOMIA
# ATLAS:  http://localhost:8090/atlas/
# API:    http://localhost:8090/WebAPI/info   http://localhost:8090/WebAPI/source/sources
scripts/down.sh            # stop (add `docker compose down -v` to also drop the database volume)
```

`SKIP_BUILD=1 scripts/up.sh` reuses an existing `webapi/WebAPI.war`.

Prerequisites: Docker with Compose v2, ~6 GB RAM free, and either a JDK 8 + Maven on the host
(`/usr/lib/jvm/java-8-openjdk-amd64`, override with `JAVA8_HOME`) or Docker access to `maven:3.9-eclipse-temurin-8`.
`scripts/build-webapi.sh` builds from `../../cogdeasy-gsk-ohdsi-webapi` (override with `WEBAPI_SRC`), cloning it
there (`WEBAPI_REF`, default `main`) if missing. It runs `mvn -Pwebapi-postgresql -DskipTests package`.

## What you get

| | |
|---|---|
| Source | `EUNOMIA` - "OHDSI Eunomia Demo Database" (GiBleed, 2,694 persons), CDM v5.3.1, vocabulary `v5.0 18-JAN-19` |
| Seeded content | cohort definition #1 "Demo new users of diclofenac" (generates 830 people on EUNOMIA), concept set #1 "Demo chronic sinusitis" |
| Security | disabled (`SECURITY_PROVIDER=DisabledSecurity`), so every user is `anonymous` |
| WebAPI | `/WebAPI/info` reports `WebAPI 2.15.1-SNAPSHOT` and the fork's commit id |

## Startup time (measured)

| step | time |
|---|---|
| `SKIP_BUILD=1 scripts/up.sh` after `docker compose down -v` (images cached, fresh DB volume) | ~29 s to `/WebAPI/info` + EUNOMIA ready |
| `scripts/build-webapi.sh` with a warm `~/.m2` | ~10 s |
| first WAR build with an empty `~/.m2` + first image pulls | dominated by downloads (repo.ohdsi.org is slow); budget 15-30 min |

Do the first build the day before a demo.

## Demo checks

- GSK-1 / WEBAPI-DEMO-102: `./reproduce.sh` in the fork exits 1 (3 of 4 `DataIntegrityViolationException`
  shapes unsafe). Through the live API, renaming a concept set to an existing name returns
  `409 {"payload":{"message":"Key (concept_set_name)=(...) already exists.  Call getNextException ..."}}`
  (raw PostgreSQL text). In the ATLAS UI the duplicate name is caught client-side first
  (`/conceptset/0/exists`) and shows a browser alert "A concept set with this name already exists".
- `scripts/capture-walkthrough.py` re-creates the screenshots + screen recording of the demo path (see the
  header of the script for its requirements).

## Notes / troubleshooting

- `maven-settings.xml` routes Maven Central through Google's mirror: `repo.maven.apache.org` and Docker Hub
  both returned HTTP 429 from cloud egress during setup. OHDSI artifacts still come from `repo.ohdsi.org`.
- The DB image's `webapi.source` row points at `broadsea-atlasdb:5432`; compose gives `atlasdb` that alias.
- Host port 5432 is often taken, so Postgres is published on `5433` (`ATLASDB_PORT`), the proxy on `8090` (`PROXY_PORT`).
- `webapi/Dockerfile` copies `WEB-INF/lib*/*` (including `lib-provided`): copying only `WEB-INF/lib` fails with
  `ClassNotFoundException: org.apache.catalina.webresources.TomcatURLStreamHandlerFactory`.
- No changes to the fork are needed; the WAR is built from an unmodified checkout.
