FROM maven:3.9-eclipse-temurin-21 AS build
WORKDIR /src
COPY pom.xml .
COPY src src
RUN mvn -q -DskipTests package

FROM quay.io/wildfly/wildfly:31.0.1.Final-jdk21
# Le pilote Oracle et la datasource BackofficeDS sont configurés par docker/configure-ds.cli
COPY docker/configure-ds.cli /opt/jboss/configure-ds.cli
COPY --from=build /src/target/legacy-backoffice.war /opt/jboss/wildfly/standalone/deployments/
