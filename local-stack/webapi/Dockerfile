# Runtime image for a WebAPI.war built from cogdeasy/cogdeasy-gsk-ohdsi-webapi by scripts/build-webapi.sh.
# Mirrors the runtime stage of the fork's own Dockerfile (Java 8, exploded WAR, WarLauncher).
FROM eclipse-temurin:8-jdk AS unpack
WORKDIR /war
COPY WebAPI.war .
RUN jar -xf WebAPI.war && rm WebAPI.war

FROM eclipse-temurin:8-jre
ENV DEFAULT_JAVA_OPTS="-Djava.security.egd=file:///dev/./urandom"
ENV JAVA_OPTS=""
WORKDIR /var/lib/ohdsi/webapi
COPY --from=unpack /war/WEB-INF/lib*/* WEB-INF/lib/
COPY --from=unpack /war/org org
COPY --from=unpack /war/WEB-INF/classes WEB-INF/classes
COPY --from=unpack /war/META-INF META-INF
EXPOSE 8080
USER 101
CMD exec java ${DEFAULT_JAVA_OPTS} ${JAVA_OPTS} \
    -cp ".:WEB-INF/lib/*.jar" \
    org.springframework.boot.loader.WarLauncher
