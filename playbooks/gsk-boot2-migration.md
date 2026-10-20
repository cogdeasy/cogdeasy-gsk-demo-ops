# GSK Spring Boot 1.5 -> 2.7 migration (WebAPI)

## Overview
Devin for migrations on cogdeasy/cogdeasy-gsk-ohdsi-webapi: move WebAPI from Spring Boot 1.5 /
Java 8 to Spring Boot 2.7 / Java 17 in one PR. Behaviour stays the same; the test suite and
`./reproduce.sh` show it. Covers the Architect lane (GSK-55, ADR) and the engineering change
that follows from it. Started from a session or Ask Devin. There is no automation trigger.

## What's Needed From User
- The ticket key (GSK-55 by default) for the branch name and PR title.
- Approval to leave the PR open. A named GSK approver merges it after the demo, not before:
  the live Q1 act (GSK-1) runs on Java 8 / Boot 1.5 `main`.

## Procedure
1. Baseline on `main` with JDK 8: `mvn -B -Pwebapi-postgresql test`, `python3 dev/ci/summary.py`,
   JaCoCo for `org.ohdsi.webapi.util` from `target/site/jacoco/jacoco.csv`, and `./reproduce.sh`.
   Compare with demo-ops `docs/BASELINE.md`. If they differ, stop and report.
2. Branch `devin/gsk-55-spring-boot-2-7`. Write the ADR first (`docs/adr/`, status Proposed).
3. POM (Spring Boot family only):
   - `spring.boot.version` 2.7.18. The BOM import moves Spring 5.3, Spring Data 2.7,
     Spring Batch 4.3, Jersey 2.35, Tomcat 9 and Hibernate 5.6 with it.
   - Remove version pins that would fight the BOM (`spring-security-crypto`, `spring-ldap-core`,
     `javax.servlet-api`). Move `hibernate-validator` to `org.hibernate.validator`. Set the Tomcat
     pins to 9.0.x, `jersey-media-multipart` to the Jersey version and
     `spring-data-jpa-entity-graph` to 2.7.x.
   - Java: `maven.compiler.release` 17. Tests: add `junit-vintage-engine` so the JUnit 4 suite
     runs on the JUnit Platform. Write new tests in JUnit 5 and do not rewrite the existing ones.
4. Code, compiler-driven, smallest change that compiles:
   - Boot class moves (`web.servlet.support.SpringBootServletInitializer`,
     `web.servlet.error.ErrorMvcAutoConfiguration`, `boot.jdbc.DataSourceBuilder`).
   - Flyway stays at 4.2. Exclude `FlywayAutoConfiguration` and replace Boot's
     `FlywayMigrationInitializer` with a local one in `FlywayConfig`.
   - Spring Data 2: `findOne(id)` -> `findById(id).orElse(null)`, `save(Iterable)` -> `saveAll`,
     `delete(id)` -> `deleteById`, `exists` -> `existsById`, `findAll(ids)` -> `findAllById`,
     `new PageRequest/Sort` -> `PageRequest.of` / `Sort.by`.
   - Spring Batch 4: bean `batchDatabaseInitializer` is now `batchDataSourceInitializer`.
   - `FlywayConfig` secondary datasource: set `.type(tomcat-jdbc)`. Boot 2 would otherwise pick
     HikariCP (on the classpath for `AuthDataSource`), which does not bind `flyway.datasource.url`.
   - Boot 2.1+ forbids bean overriding. `JobConfig` overrides `jobBuilders`, so set
     `spring.main.allow-bean-definition-overriding=true` (Boot 1.5 behaviour).
   - Mockito 1 -> 4: `ArgumentMatchers`, `org.mockito.junit.MockitoJUnitRunner`, `getArgument`.
     `anyString()` no longer matches null; use `nullable(String.class)` where Mockito 1 relied on it.
   - Build: `gmaven-plugin` 1.5 fails on Java 17; replace with `gmavenplus-plugin`.
   - Boot 2.6+ forbids circular references: `spring.main.allow-circular-references=true`.
   - Spring 5 will not inject a `null` `@Bean`: `AtlasRegularSecurity.jdbcDataSource` becomes
     `@Autowired(required = false)` (`AuthDataSource` returns null when the auth DB is down).
   - Keep `hibernate.version` 5.4.2 (5.6 rejects HQL in `IncidenceRateAnalysisRepository`).
   - Pin `spring-plugin-core` 2.0.0 for spring-hateoas 1.5; add `jakarta.jms-api` and exclude
     `geronimo-jms_1.1_spec` from `com.odysseusinc:logging` (Spring JMS 5 needs JMS 2.0).
   - Redshift JDBC 1.2.10 needs `--add-opens java.base/java.net=ALL-UNNAMED` on Java 17:
     surefire/failsafe `argLine` and Docker `DEFAULT_JAVA_OPTS`; Docker images to Temurin 17.
   - Import `jackson-bom` `${jackson.version}` before the Boot BOM (keeps modules on 2.12).
   - Mockito 2+ runner is strict: use `MockitoJUnitRunner.Silent` where a test has unused stubs.
   - `spring.jackson.serialization.write-dates-as-timestamps=true` (Boot 2 writes ISO dates).
   - Pin `commons-collections` 3.2.2 (Boot 1.5 managed it; 3.2.1 is CVE-2015-7501).
   - Miredot 2.4 needs JDK 8 `tools.jar`: skip it on Java 9+ (`miredot-off-on-jdk9plus`).
   - Smoke-test one Spring context (`-Dtest=PermissionTest,CohortTaggingTest`) before the full
     suite; most Boot 2 breakages only show when a context starts.
   - Property renames: `server.context-path` -> `server.servlet.context-path`,
     `spring.datasource.initialize` -> `spring.sql.init.mode`, `spring.batch.initializer.enabled`
     -> `spring.batch.jdbc.initialize-schema`.
5. CI: switch `actions/setup-java` to 17 for `build` and `tests`. Keep `scan` unchanged.
6. Run the full suite with JDK 17. Report run / passed / failed / skipped and the JaCoCo numbers
   next to the baseline. `./reproduce.sh` must still exit 1 with the same four lines.
7. Boot the real stack (demo-ops `local-stack` branch, detached worktree). Its runtime image is
   Java 8: for the branch WAR use `eclipse-temurin:17-jre` and add
   `--add-opens java.base/java.net=ALL-UNNAMED` to `DEFAULT_JAVA_OPTS` (local change only).
   Check `/WebAPI/info` (`buildInfo.commitId` = branch head), `/WebAPI/source/sources`, Flyway
   start-up, and a duplicate concept set. Run the same requests against a `main` WAR (JDK 8) on a
   second stack (`-p gsk-base`, other ports) and compare the JSON bodies, not just status codes.
   Run Trivy over both WARs and list closed and new CVEs.
8. Open the PR with the WebAPI template (Ticket, URS delta, Test mapping, Change record).
   Record the post-migration numbers in demo-ops `docs/BASELINE-BOOT2.md`.

## Specifications
- Same test count as baseline (248), 0 failures. Skips do not increase without a stated reason.
- `./reproduce.sh` output is identical to baseline. The GSK-1 / GSK-102 defect is the Q1 live
  act and must not be fixed in this PR.
- Flyway 4.2 -> 8, Shiro 1.13 -> 2.x, Hikari, `javax` -> `jakarta` and Boot 3 are each a later,
  separate PR (one library family per PR). The ADR lists their order.

## Advice and Pointers
- Upstream OHDSI/WebAPI went straight from 1.5 to 3.2 in commit 62b9cb1d ("migrate java").
  Use it as a list of files that move. It is not a 2.7 recipe, because it also renames
  `javax` to `jakarta`.
- Shiro is the security layer. Spring Security is used only for `BCryptPasswordEncoder`, so
  there is no `WebSecurityConfigurerAdapter` work.
- `HibernateJpaAutoConfiguration` is excluded. JPA properties come from `DataAccessConfig`, so
  Boot 2's JPA defaults do not apply.
- Maven Central rate-limits Devin VMs. Use the GCS mirror in `~/.m2/settings.xml`.

## Forbidden Actions
- Do not fix GenericExceptionMapper in this PR.
- Do not upgrade Flyway, Shiro or move to `jakarta` in this PR.
- Do not disable, skip or delete a test to get green. Raise a deviation instead.
- Do not merge. Do not change Jira labels.
