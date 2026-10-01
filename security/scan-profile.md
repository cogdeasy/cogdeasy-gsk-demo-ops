# Security Swarm scan profile: WebAPI (paste-in text)

Paste each block into the matching field of a new **Discover** profile (Security > Profiles > Create manually). Field names follow the [Security Swarm docs](https://docs.devin.ai/work-with-devin/security-swarm#scan-profiles). Do not start a scan from this file; the AppSec reviewer starts it with Interactive mode on.

## Profile name

```text
OHDSI WebAPI: REST auth, data exposure and SQL generation
```

## Description

```text
Find authentication, authorization, information-disclosure and injection vulnerabilities in the WebAPI REST services (Jersey + Shiro, Java 8) that ATLAS calls. Silver-tier GxP-adjacent application.
```

## Threat model

```text
Two attackers: (1) unauthenticated, with network access to /WebAPI; (2) an authenticated
low-privilege user with a valid JWT and only the default role.
Assets: cohort definitions and concept sets; source (CDM) credentials and connection strings;
per-user JWT signing keys; auth database users and password hashes; patient-level CDM data
reachable through cohort generation.
Trust boundaries: the Shiro filter chain (ShiroConfiguration, AtlasSecurity.setupProtectedPaths,
AtlasJwtAuthFilter, UrlBasedAuthorizingFilter); the paths that skip authentication (/info,
/ddl/*, /saml/*, /executionservice/callbacks/**, /i18n/**); the JDBC boundary to CDM sources.
Entry points: every Jersey resource under src/main/java/org/ohdsi/webapi (classes with @Path),
the login endpoints in AtlasRegularSecurity, and the execution-engine callbacks.
Priorities: auth bypass and missing permission checks; one user reading or changing another
user's cohort definitions; source credential disclosure; raw database text or stack traces in
API responses (see GenericExceptionMapper); SQL injection through cohort expressions, sourceKey
or other path/query parameters; secrets in URLs or logs.
Assume the deployment runs AtlasRegularSecurity. Report findings that only apply under the
DisabledSecurity default as configuration findings.
```

## Investigation guidance

```text
Trace input from the Jersey resource method through services to the sensitive operation (JDBC
call, SqlRender template, repository save, response entity). Check at each step: is the path
protected in the Shiro filter chain, which permission string does UrlBasedAuthorizingFilter
require, is ownership checked, is the value escaped or parameterised before it reaches SQL.
Cite file and line for every step. Use the existing tests and ./reproduce.sh as evidence where
they apply. If a control blocks the path (filter, permission, parameter binding), say so and
do not report it. Treat a risky pattern as a lead until you have a reachable path.
```

## Triage guidance (severity criteria)

```text
Group findings with the same root cause.
Critical: unauthenticated code execution, SQL execution on a CDM source, or auth bypass to
any protected endpoint.
High: authenticated low-privilege user reads source credentials, changes another user's
cohort definitions, or runs arbitrary SQL; unauthenticated disclosure of database text,
credentials or tokens.
Medium: authenticated disclosure of raw database text or internals; secrets in URLs or logs;
unauthenticated denial of service of shared components (for example the authDataSource pool).
Low: defense in depth, insecure defaults that a documented deployment setting overrides.
Mark duplicates of open Jira issues (for example GSK-1 for GenericExceptionMapper) as duplicates.
```

## Sandbox validation

```text
Optional. Build with: export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64;
mvn -B -Pwebapi-postgresql -DskipUnitTests -DskipITtests compile.
Database tests use embedded PostgreSQL (zonky); no external database. Prefer a focused JUnit
test or ./reproduce.sh-style harness that shows the issue. Do not call any external service
and use no real credentials.
```

## Report

```text
Audience: the AppSec reviewer and the WebAPI tech lead. Confirmed critical and high first,
then unvalidated. For each: file and line, attacker model, evidence, proposed fix, Jira link
if one exists. Keep it short.
```

## Remediation guidance

```text
Follow AGENTS.md: one finding per PR, smallest safe change, keep public API behaviour.
Add a regression test that fails before and passes after; run
mvn -B -Pwebapi-postgresql test. Fill the PR template (Ticket, URS delta, Test mapping,
Change record). Never return stack traces, SQL or constraint names to clients. Dependency
upgrades: one library family per PR. Do not merge; the CODEOWNERS approver merges.
```

## Advanced: include globs

```text
src/main/java/**
src/main/resources/**
pom.xml
```

## Advanced: exclude globs

```text
src/test/**
dev/**
validation/**
**/README.md
i18n.md
api.html
src/main/resources/i18n/**
```

Exclusion notes: `src/test/**` is test code; `README.md`, `i18n.md`, `api.html` and the `README.md` files under `src/main/extras/` and `shiro/realms/` are the bundled upstream docs; `dev/` is the GSK repro harness; `validation/` is evidence-pack templates. `src/main/resources/i18n/**` is UI message bundles. `src/main/resources/resources/**` (SQL templates) stays in scope.
