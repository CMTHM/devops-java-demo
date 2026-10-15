# Simple Dockerfile for the TRISHA ACADEMY DevOps Java Demo
#
# The app needs a MySQL database, so start it with Docker Compose (see DOCKER-COMPOSE.md):
#   docker compose up -d --build
# Open  : http://localhost:9090/name

# 1. Start from the official Maven image (Java 21 + Maven, lightweight Alpine Linux)
FROM maven:3.9-eclipse-temurin-21-alpine
#FROM maven:3.10-eclipse-temurin-17-alpine
# 2. Who maintains this image
LABEL maintainer="Developer Team"

# 3. Go to the /app folder inside the container
WORKDIR /app

# 4. Copy the project files from your computer into /app
COPY . .

# 5. Build the application JAR (tests are skipped to keep the build fast)
#    --mount=type=cache keeps downloaded Maven libraries between builds, so they are not downloaded again
RUN --mount=type=cache,target=/root/.m2 mvn -B clean package -DskipTests

# 6. The application listens on port 9090 (server.port in application.properties)
EXPOSE 9090

# 7. Start the application when the container starts
CMD ["java", "-jar", "target/devops-java-demo-1.0.0.jar"]
