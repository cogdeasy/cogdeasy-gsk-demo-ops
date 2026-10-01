# WebAPI threat model (draft)

Scope: `cogdeasy/cogdeasy-gsk-ohdsi-webapi`, the REST services behind ATLAS. Silver tier. Draft example for the demo, not a reviewed security record. File references are to that repo at `main` (3de09d96) and were checked by reading the code. Risks below are leads for the scan to confirm or dismiss, not confirmed vulnerabilities.

## Entry points

| entry point | where |
|---|---|
| Jersey REST resources under `/WebAPI` | `src/main/resources/application.properties:94` (`server.context-path`) |
| Cohort definitions: list, create, save, generate, `POST /cohortdefinition/sql` | `service/CohortDefinitionService.java:169` (`@Path`), `:673`, `:696`, `:724`, `:827`, `:863` |
| Concept sets | `service/ConceptSetService.java:90`, update at `:549-555` |
| Sources (CDM connections) | `source/SourceController.java:34`, details at `:135-145` |
| Execution-engine callbacks (no login) | `executionengine/controller/ScriptExecutionCallbackController.java:48`, `:89-94`, `:121-126` |
| Shiro filter chain | `ShiroConfiguration.java:48` (`shiroFilter`), `shiro/management/AtlasSecurity.java:97-120` |
| JWT bearer filter | `shiro/filters/auth/AtlasJwtAuthFilter.java:17-25`, `shiro/TokenManager.java:116-131` (`Authorization: Bearer`) |
| Login endpoints (db, ldap, ad, openid, saml, kerberos, windows) | `shiro/management/AtlasRegularSecurity.java:417-461` |

Paths that skip authentication (`AtlasSecurity.java:101-118`): `/info`, `/ddl/*`, `/saml/saml-metadata`, `/saml/slo`, `/executionservice/callbacks/**`, `/i18n/**`. Everything else is `addProtectedRestPath("/**/*")` (`:120`): JWT authentication plus URL-based permission check.

All paths are relative to `src/main/java/org/ohdsi/webapi/` unless they start with `src/` or `pom.xml`.

## Assets

- Cohort definitions and concept sets: the study logic, stored in the WebAPI schema (`CohortDefinition`, `CohortDefinitionDetails`).
- Source credentials: CDM database username and password on `source/Source.java:89-95` (`@Type(type = "encryptedString")`), plus the connection string and Kerberos keytab.
- JWT signing keys: one random HS512 key per user, held in memory (`shiro/TokenManager.java:31-32`).
- Auth database users and password hashes, read through the `authDataSource` pool (`AuthDataSource.java`, query at `pom.xml:148`).
- Patient-level CDM data reachable through cohort generation on a source.

## Attacker models

1. **Unauthenticated**: network access to `/WebAPI`, no token. Can reach the public paths above and the login endpoints.
2. **Authenticated low-privilege user**: valid JWT, default role only. Wants to read or change other users' cohort definitions, see source credentials, or run SQL on a CDM source.

## Top risks

| # | risk | evidence | attacker |
|---|---|---|---|
| R1 | Error mapper returns raw database text, or crashes to 500, on data integrity violations (GSK-1) | `util/GenericExceptionMapper.java:59-63` reads `ex.getCause().getCause().getMessage()` and returns the text after `Detail:` | 1, 2 |
| R2 | Security off by default: the build default is `security.provider=DisabledSecurity`; then every path except `/user`, `/role`, `/permission` is anonymous | `pom.xml:81`, `shiro/management/DisabledSecurity.java:31-37` | 1 (if a deployment keeps the default) |
| R3 | Source credentials stored unencrypted by default, and the configured algorithm is weak | `pom.xml:216-218` (`jasypt.encryptor.enabled=false`, `PBEWithMD5AndDES`), `DataAccessConfig.java:116-124` (`NotEncrypted` when disabled) | insider, DB read |
| R4 | Source details return the username and full connection string; the password is masked but some JDBC URLs carry credentials | `source/SourceDetails.java:14`, `:17-18`; endpoint `source/SourceController.java:135-145` | 2 (needs the source details permission) |
| R5 | Unauthenticated callbacks take a shared secret in the URL path, compared with `Objects.equals`; request body is logged before the check | `shiro/management/AtlasSecurity.java:112`, `executionengine/controller/ScriptExecutionCallbackController.java:89-103` | 1 |
| R6 | Every authenticated user can read every cohort definition by default | `pom.xml:194` (`defaultGlobalReadPermissions=true`), `service/CohortDefinitionService.java:283-284`, `:701-706` | 2 |
| R7 | Cohort expression to SQL: user-supplied cohort JSON becomes SQL run on a CDM source; check that literals and identifiers are escaped | `service/CohortDefinitionService.java:673-686` (`/sql`), `:863` (`/{id}/generate/{sourceKey}`) | 2 |
| R8 | JWT keys live in a static `HashMap` per JVM; the untrusted subject is parsed before signature check to pick the key | `shiro/TokenManager.java:31-32`, `:54-95` | 1, 2 |

Config-dependent items to check per deployment: `security.origin` with `Access-Control-Allow-Credentials: true` (`shiro/filters/CorsFilter.java:49-50`, default `http://localhost` at `pom.xml:83`) and `security.ssl.enabled=false` (`pom.xml:84`).

Out of scope: test code, the bundled upstream docs, the `dev/` repro harness, third-party libraries (covered by Trivy).
