FROM eclipse-temurin:21-jdk AS build
WORKDIR /src
COPY pom.xml .
COPY src src
RUN --mount=type=cache,target=/root/.m2 apt-get update -qq && apt-get install -y -qq maven >/dev/null \
    && mvn -q -DskipTests package

FROM eclipse-temurin:21-jre
RUN useradd --system --uid 10001 app
USER app
COPY --from=build /src/target/fund-api-*.jar /app/fund-api.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "/app/fund-api.jar"]
