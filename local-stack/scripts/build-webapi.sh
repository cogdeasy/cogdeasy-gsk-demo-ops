#!/usr/bin/env bash
# Builds target/WebAPI.war from cogdeasy/cogdeasy-gsk-ohdsi-webapi and copies it to webapi/WebAPI.war.
#   WEBAPI_SRC   path to a local clone of the fork (default: ../cogdeasy-gsk-ohdsi-webapi next to this repo;
#                cloned there if missing)
#   WEBAPI_REF   git ref to check out when cloning (default: main)
# Uses a host JDK 8 when found, otherwise builds inside a maven:3.9-eclipse-temurin-8 container.
set -euo pipefail
here="$(cd "$(dirname "$0")/.." && pwd)"
src="${WEBAPI_SRC:-$here/../../cogdeasy-gsk-ohdsi-webapi}"
ref="${WEBAPI_REF:-main}"
settings="$here/maven-settings.xml"

if [ ! -d "$src/.git" ]; then
  git clone --branch "$ref" https://github.com/cogdeasy/cogdeasy-gsk-ohdsi-webapi.git "$src"
fi
src="$(cd "$src" && pwd)"
echo "building WebAPI from $src ($(git -C "$src" rev-parse --short HEAD))"

mvn_args=(-B -s "$settings" -Pwebapi-postgresql -DskipTests -DskipUnitTests -DskipITtests package)
jdk8="${JAVA8_HOME:-/usr/lib/jvm/java-8-openjdk-amd64}"
if [ -x "$jdk8/bin/javac" ] && command -v mvn >/dev/null; then
  (cd "$src" && JAVA_HOME="$jdk8" PATH="$jdk8/bin:$PATH" mvn "${mvn_args[@]}")
else
  docker run --rm -v "$src":/code -v "$settings":/settings.xml:ro -v gsk-m2:/root/.m2 -w /code \
    maven:3.9-eclipse-temurin-8 mvn -B -s /settings.xml -Pwebapi-postgresql -DskipTests -DskipUnitTests -DskipITtests package
fi
cp "$src/target/WebAPI.war" "$here/webapi/WebAPI.war"
echo "copied WebAPI.war to $here/webapi/"
