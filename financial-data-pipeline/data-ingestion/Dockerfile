FROM maven:3.8-eclipse-temurin-17 AS build
WORKDIR /app
COPY . .
RUN mvn clean package -DskipTests

FROM eclipse-temurin:17-jre
WORKDIR /app
COPY --from=build /app/target/financial-data-pipeline-1.0-SNAPSHOT.jar /app/data-ingestion.jar
CMD ["java", "-jar", "/app/data-ingestion.jar"]
