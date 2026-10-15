# TRISHA ACADEMY — DevOps Java Demo

A small Spring Boot 3 application used for DevOps training. It has:

- A **Welcome API** that shows a welcome message.
- A **Student CRUD API** (insert, read, update, delete) that stores data in a **MySQL** database.
- **Swagger** pages to try every API from the browser.
- **Lint** (Checkstyle), **formatting** (Spotless), **JUnit 5 tests** and a **code coverage** check (JaCoCo) that run on every build.
- A **Docker Compose** setup with two containers — MySQL and the Java app. Full guide: [DOCKER-COMPOSE.md](./DOCKER-COMPOSE.md).

Follow the steps below in order.

---

## Contents

1. [Install the requirements](#step-1--install-the-requirements)
2. [Open the project](#step-2--open-the-project)
3. [Understand the project structure](#step-3--understand-the-project-structure)
4. [Build the project](#step-4--build-the-project)
5. [Run the application](#step-5--run-the-application)
6. [Call the APIs](#step-6--call-the-apis)
7. [Use Swagger](#step-7--use-swagger)
8. [View the data in MySQL](#step-8--view-the-data-in-mysql)
9. [Run lint and format checks](#step-9--run-lint-and-format-checks)
10. [Run the JUnit tests](#step-10--run-the-junit-tests)
11. [Run the full build with coverage](#step-11--run-the-full-build-with-coverage)
12. [Package and run the JAR](#step-12--package-and-run-the-jar)
13. [Run with Docker Compose](#step-13--run-with-docker-compose)
14. [Troubleshooting](#troubleshooting)

---

## Step 1 — Install the requirements

| Tool | Version | Check it is installed |
|------|---------|-----------------------|
| JDK (Java) | 17 or newer | `java -version` |
| Maven | 3.8 or newer | `mvn -v` |
| Docker Desktop | Any recent version | `docker --version` and `docker compose version` |

Run the commands in a terminal. Each should print a version number. If you see "command not found" / "not recognized", install the tool and add it to your `PATH`.

The app stores its data in **MySQL**. You do not need to install MySQL — it runs in a Docker container (Step 5). [Docker Desktop](https://www.docker.com/products/docker-desktop/) is required for that.

> Building and testing (`mvn clean install`, `mvn test`) do **not** need MySQL — the tests use an in-memory H2 database.

---

## Step 2 — Open the project

Open a terminal and go to the project folder:

```bash
cd D:\TRISHA-ACADEMY\DevOPs\devops-java-demo
```

All commands in this guide are run from this folder (the one that contains `pom.xml`).

---

## Step 3 — Understand the project structure

```text
devops-java-demo/
├── pom.xml                         # Maven build: dependencies, lint, tests, coverage
├── Dockerfile                      # Builds the app image (Step 13)
├── compose.yaml                    # Docker Compose: mysql + app containers (Step 13)
├── .env                            # Database name, users and passwords used by compose.yaml
├── .dockerignore                   # Files Docker does not copy into the image
├── DOCKER-COMPOSE.md               # Full Docker Compose guide
├── .mvn/jvm.config                 # JVM options Maven needs for the formatter on new JDKs
├── config/checkstyle/checkstyle.xml# Lint rules
├── docs/                           # PDF guides (REST API CRUD guide, Docker course)
└── src/
    ├── main/
    │   ├── java/com/trisha/academy/springlab/
    │   │   ├── SpringLabApplication.java        # Application entry point (main method)
    │   │   ├── config/OpenApiConfig.java        # Swagger title, description, version
    │   │   ├── controller/WelcomeController.java# GET /name
    │   │   ├── controller/StudentController.java# /students CRUD APIs
    │   │   ├── model/Student.java               # Student entity -> "students" table
    │   │   └── repository/StudentRepository.java# Database access (Spring Data JPA)
    │   └── resources/application.properties     # Port, MySQL database settings
    └── test/java/com/trisha/academy/springlab/  # JUnit 5 tests
```

---

## Step 4 — Build the project

```bash
mvn clean install
```

What happens, in order:

1. **Lint and format checks** run first (Checkstyle and Spotless). The build stops if the code breaks a rule.
2. The code is **compiled**.
3. All **JUnit tests** run.
4. **Coverage** is checked (at least 80% of lines must be tested).
5. The application JAR is created in `target/`.

At the end you should see:

```text
Tests run: 18, Failures: 0, Errors: 0, Skipped: 0
BUILD SUCCESS
```

> The first build downloads dependencies from the internet, so it takes longer.

---

## Step 5 — Run the application

First start the MySQL database in Docker (Docker Desktop must be running):

```bash
docker compose up -d mysql
```

This starts only the `mysql` container from `compose.yaml`, published on **port 3307** of your computer. Wait until `docker compose ps` shows it as `(healthy)` — about 30 seconds the first time.

Then start the application:

```bash
mvn spring-boot:run
```

Wait until the console shows:

```text
Started SpringLabApplication in ... seconds
```

The application is now running on **port 9090**. Keep this terminal open. To stop the application, press `Ctrl + C`.

Quick check — open http://localhost:9090/name in the browser. It shows:

```text
Welcome to TrishaAcademy
```

> The port is set by `server.port=9090` in `src/main/resources/application.properties`. The database connection (`localhost:3307`, database `trishadb`, user `trisha`) is set in the same file.

To run **both** MySQL and the app in containers instead, see Step 13.

---

## Step 6 — Call the APIs

### API list

| API | Operation | Method | URL | Success code |
|-----|-----------|--------|-----|--------------|
| Welcome | Welcome message | GET | `/name` | 200 |
| Students | Insert | POST | `/students` | 201 |
| Students | Get all | GET | `/students` | 200 |
| Students | Get one | GET | `/students/{id}` | 200 (404 if not found) |
| Students | Update | PUT | `/students/{id}` | 200 (404 if not found) |
| Students | Delete | DELETE | `/students/{id}` | 204 (404 if not found) |

### Try them with curl

Open a **second** terminal (the app keeps running in the first one) and run these in order:

```bash
# 1. Welcome message
curl http://localhost:9090/name

# 2. Insert a student (the server assigns the id)
curl -X POST http://localhost:9090/students -H "Content-Type: application/json" -d "{\"name\":\"Priya\",\"course\":\"DevOps\"}"

# 3. Get all students
curl http://localhost:9090/students

# 4. Get the student with id 1
curl http://localhost:9090/students/1

# 5. Update the student with id 1
curl -X PUT http://localhost:9090/students/1 -H "Content-Type: application/json" -d "{\"name\":\"Priya\",\"course\":\"Java\"}"

# 6. Delete the student with id 1
curl -X DELETE http://localhost:9090/students/1
```

> On Windows PowerShell use `curl.exe` instead of `curl`. On Linux/macOS you can use single quotes around the JSON: `-d '{"name":"Priya","course":"DevOps"}'`.

A full PDF guide with all CRUD APIs, HTTP status codes and interview questions is in [docs/REST-API-CRUD-Guide.pdf](./docs/REST-API-CRUD-Guide.pdf).

---

## Step 7 — Use Swagger

Swagger is a web page that lists every API and lets you call it from the browser, without curl or Postman.

| Page | URL |
|------|-----|
| Swagger UI (interactive page) | http://localhost:9090/swagger-ui/index.html |
| OpenAPI JSON (raw API spec) | http://localhost:9090/v3/api-docs |

### 7.1 Open Swagger

1. Make sure the application is running (Step 5).
2. Open http://localhost:9090/swagger-ui/index.html.
3. You will see two groups: **Welcome** and **Students**.

### 7.2 Call an API

For every endpoint the steps are the same:

1. Click the endpoint to expand it.
2. Click **Try it out**.
3. Fill in the **id** and/or the **request body** if asked.
4. Click **Execute**.
5. Read the **response code** and **response body** below. Swagger also shows the equivalent curl command.

### 7.3 Walk through all APIs

| # | Endpoint | What to enter | Expected result |
|---|----------|---------------|-----------------|
| 1 | `GET /name` | nothing | 200, `Welcome to TrishaAcademy` |
| 2 | `POST /students` | body `{"name": "Priya", "course": "DevOps"}` (leave out `id`) | 201, `{"id": 1, "name": "Priya", "course": "DevOps"}` |
| 3 | `GET /students` | nothing | 200, list of all students |
| 4 | `GET /students/{id}` | id `1` | 200 with the student, or 404 |
| 5 | `PUT /students/{id}` | id `1`, body `{"name": "Priya", "course": "Java"}` | 200 with the updated student, or 404 |
| 6 | `DELETE /students/{id}` | id `1` | 204 (no body), or 404 |

### 7.4 How Swagger is added to the project

1. **Dependency** in `pom.xml` — springdoc scans the controllers and builds the docs automatically:

   ```xml
   <dependency>
     <groupId>org.springdoc</groupId>
     <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
     <version>2.5.0</version>
   </dependency>
   ```

   springdoc 2.x is for Spring Boot 3. Spring Boot 2 projects need springdoc 1.x.

2. **API information** in `config/OpenApiConfig.java` — the title, description and version at the top of the page:

   ```java
   @Bean
   public OpenAPI devopsJavaDemoOpenApi() {
       return new OpenAPI()
               .info(new Info()
                       .title("TRISHA ACADEMY DevOps Java Demo API")
                       .description("Welcome API and Student CRUD API")
                       .version("1.0.0"));
   }
   ```

3. **Annotations** in the controllers — `@Tag` groups the APIs and `@Operation` describes each one. They are optional; Swagger lists every endpoint without them.

No extra settings are needed in `application.properties`.

---

## Step 8 — View the data in MySQL

The app stores its data in the **MySQL** container `trisha-mysql`. MySQL keeps its files in the Docker volume `devops-java-demo_mysql-data`, so the data is **kept when the app or the containers stop, restart or are removed** (only `docker compose down -v` deletes it).

- The `students` table is created automatically from `model/Student.java` (`spring.jpa.hibernate.ddl-auto=update` keeps existing data).
- JUnit tests use a separate in-memory H2 database (`jdbc:h2:mem:testdb`, set in `pom.xml`), so tests never change your data.

| Setting | From your computer | From the app container (Compose) |
|---------|--------------------|----------------------------------|
| Host and port | `localhost:3307` | `mysql:3306` |
| Database | `trishadb` | `trishadb` |
| Username / password | `trisha` / `trisha@123` | `trisha` / `trisha@123` |
| Root password | `root@123` | `root@123` |
| Table | `students` | `students` |

### 8.1 With the MySQL client inside the container

```bash
docker exec -it trisha-mysql mysql -utrisha -ptrisha@123 trishadb
```

```sql
SELECT * FROM students;
EXIT;
```

### 8.2 With MySQL Workbench or DBeaver

Connect to host `localhost`, port `3307`, user `trisha`, password `trisha@123`, database `trishadb`.

The SQL that Hibernate runs is also printed in the application console (`spring.jpa.show-sql=true`).

---

## Step 9 — Run lint and format checks

Two tools keep the code clean. Both run automatically at the start of every build, so a build fails if the code breaks a rule.

| Tool | What it checks | Rules |
|------|----------------|-------|
| **Checkstyle** (lint) | Unused imports, `*` imports, naming, missing braces, empty catch blocks, public fields, long methods, too many parameters, etc. | `config/checkstyle/checkstyle.xml` |
| **Spotless** (format) | Indentation, spacing, import order, trailing whitespace (Palantir Java Format) | `pom.xml` |

### 9.1 Run the lint check

```bash
mvn checkstyle:check
```

- Pass: `You have 0 Checkstyle violations.`
- Fail: each problem is printed with the file, line number and rule name, for example:

  ```text
  [WARN] src/main/java/.../StudentController.java:[12,8] (imports) UnusedImports: Unused import - java.util.Map.
  ```

  Open the file at that line, fix it, and run the command again.

### 9.2 Run the format check

```bash
mvn spotless:check
```

If it fails, let Spotless fix the formatting for you:

```bash
mvn spotless:apply
```

Then run `mvn spotless:check` again — it should pass.

> Tip: run `mvn spotless:apply` before every commit.

---

## Step 10 — Run the JUnit tests

```bash
mvn test
```

Expected output:

```text
Tests run: 18, Failures: 0, Errors: 0, Skipped: 0
BUILD SUCCESS
```

### 10.1 What is tested

| Test class | Type | What it checks |
|------------|------|----------------|
| `controller/WelcomeControllerTest` | Controller test (MockMvc) | `GET /name` returns 200 and the welcome message |
| `controller/StudentControllerTest` | Controller test (MockMvc + mocked repository) | Every CRUD API: success codes, 404 for unknown ids, 400 for bad JSON or a non-number id, 415 for wrong content type |
| `repository/StudentRepositoryTest` | Database test (`@DataJpaTest`, H2) | Saving, finding and deleting students |
| `StudentApiIntegrationTest` | Integration test (whole app) | Full flow: insert → get → update → delete, and the Swagger docs |
| `SpringLabApplicationTests` | Smoke test | The application starts |

> During the tests you may see a `JSON parse error` warning in the log. That is expected — one test sends broken JSON on purpose to check that the API returns 400.

### 10.2 Run only some tests

```bash
# One test class
mvn test -Dtest=StudentControllerTest

# One test method
mvn test -Dtest=WelcomeControllerTest#welcomeReturnsName
```

### 10.3 Test reports

After `mvn test`, detailed results are in `target/surefire-reports/`.

---

## Step 11 — Run the full build with coverage

```bash
mvn clean verify
```

This runs everything — lint, format check, compile, all tests — and then checks **code coverage** with JaCoCo. The build fails if less than **80%** of the code lines are covered by tests.

Open the coverage report in the browser:

```text
target/site/jacoco/index.html
```

It shows, for every class, which lines are tested (green) and which are not (red).

This is the command to use in a CI pipeline (Jenkins, GitHub Actions, etc.).

---

## Step 12 — Package and run the JAR

```bash
mvn clean package
java -jar target/devops-java-demo-1.0.0.jar
```

The application starts on port 9090, the same as Step 5 (MySQL must be running: `docker compose up -d mysql`). Press `Ctrl + C` to stop it.

---

## Step 13 — Run with Docker Compose

Docker packages the application, Java and Maven into one **image**. A running image is called a **container**. **Docker Compose** starts several containers together from one file, `compose.yaml`. This project uses two containers:

| Container | Service | What it runs | Port on your computer |
|-----------|---------|--------------|-----------------------|
| `trisha-mysql` | `mysql` | MySQL 8.4 (official image) | 3307 |
| `devops-java-demo` | `app` | This Spring Boot app (built from the `Dockerfile`) | 9090 |

The full Compose guide — every line of `compose.yaml`, how the app finds MySQL, persistence tests, commands and interview questions — is in **[DOCKER-COMPOSE.md](./DOCKER-COMPOSE.md)**.

### 13.1 The Dockerfile, line by line

The `Dockerfile` in the project folder has 7 steps:

| Step | Instruction | What it does |
|------|-------------|--------------|
| 1 | `FROM maven:3.9-eclipse-temurin-21-alpine` | Start from the **official** Maven image (Java 21 + Maven on lightweight Alpine Linux) |
| 2 | `LABEL maintainer="Developer Team"` | Record who maintains the image |
| 3 | `WORKDIR /app` | Use `/app` as the working folder inside the image |
| 4 | `COPY . .` | Copy the project from your computer (first `.`) into `/app` (second `.`) |
| 5 | `RUN --mount=type=cache,target=/root/.m2 mvn -B clean package -DskipTests` | Build the JAR. Lint and format checks run here too. The cache keeps downloaded Maven libraries between builds |
| 6 | `EXPOSE 9090` | Document the port the app listens on |
| 7 | `CMD ["java", "-jar", "target/devops-java-demo-1.0.0.jar"]` | Start the app when the container starts |

Files listed in `.dockerignore` (`target/`, `docs/`, `.env`, `compose.yaml`, IDE files, etc.) are **not** copied into the image. `.env` is excluded so passwords are never baked into the image.

> `maven` and `eclipse-temurin` are **Docker Official Images** — on Docker Hub their URL is `hub.docker.com/_/maven` (the `_/` means official).

### 13.2 Start Docker Desktop

Open Docker Desktop from the Start menu, or run:

```bash
docker desktop start
```

Check the engine is running — it should print server details with no error:

```bash
docker info
```

### 13.3 Build and start both containers

From the project folder (stop `mvn spring-boot:run` first if it is running — it uses port 9090):

```bash
docker compose up -d --build
```

- `up` — create the network, the volume and both containers, and start them.
- `-d` — run in the background.
- `--build` — build the app image from the `Dockerfile` first.

Compose starts MySQL first and starts the app only when MySQL is **healthy**. The first run takes a few minutes (it downloads `mysql:8.4`, the Maven image and the Maven libraries).

### 13.4 Check the containers

```bash
docker compose ps
```

```text
NAME               SERVICE   STATUS                    PORTS
devops-java-demo   app       Up 14 seconds             0.0.0.0:9090->9090/tcp
trisha-mysql       mysql     Up 36 seconds (healthy)   0.0.0.0:3307->3306/tcp
```

Watch the app logs until you see `Started SpringLabApplication` (press `Ctrl + C` to stop watching — the container keeps running):

```bash
docker compose logs -f app
```

Inside Compose the app connects to `jdbc:mysql://mysql:3306/trishadb` — `mysql` is the **service name**, which Docker's DNS resolves to the MySQL container. The values come from environment variables in `compose.yaml`, which override `application.properties`.

### 13.5 Test the application

| What | URL |
|------|-----|
| Welcome API | http://localhost:9090/name |
| Swagger UI | http://localhost:9090/swagger-ui/index.html |
| MySQL (Workbench / DBeaver) | `localhost:3307`, user `trisha`, password `trisha@123` |

Everything from Steps 6–8 works the same. From a terminal:

```bash
curl http://localhost:9090/name
```

Expected output: `Welcome to TrishaAcademy`

### 13.6 Useful Docker commands for the demo

| Goal | Command |
|------|---------|
| Show the maintainer and other labels | `docker inspect --format "{{json .Config.Labels}}" devops-java-demo:1.0.0` |
| Show image history (one layer per instruction) | `docker history devops-java-demo:1.0.0` |
| Open a shell inside the app container | `docker compose exec app sh` |
| Open the MySQL client | `docker compose exec mysql mysql -utrisha -ptrisha@123 trishadb` |
| CPU and memory usage | `docker stats devops-java-demo trisha-mysql` |
| Restart one service | `docker compose restart app` |
| See the database volume | `docker volume ls --filter name=devops-java-demo` |

### 13.7 Stop and clean up

```bash
# Stop and remove both containers and the network (the database volume is KEPT)
docker compose down

# Also delete the database volume (all students are deleted)
docker compose down -v

# (Optional) remove the app image
docker rmi devops-java-demo:1.0.0
```

### 13.8 Rebuild after a code change

```bash
docker compose up -d --build app
```

Only the app image is rebuilt and the app container recreated. MySQL keeps running, and the students are still there because they are stored in MySQL's volume, not in the app image.

---

## Command summary

| Goal | Command |
|------|---------|
| Start only MySQL (for local runs) | `docker compose up -d mysql` |
| Run the app | `mvn spring-boot:run` |
| Lint check | `mvn checkstyle:check` |
| Format check | `mvn spotless:check` |
| Fix formatting | `mvn spotless:apply` |
| Run JUnit tests | `mvn test` |
| Full build + coverage | `mvn clean verify` |
| Build the JAR | `mvn clean package` |
| Run the JAR | `java -jar target/devops-java-demo-1.0.0.jar` |
| Build and start MySQL + app | `docker compose up -d --build` |
| Container status | `docker compose ps` |
| App logs | `docker compose logs -f app` |
| Stop everything (keep data) | `docker compose down` |
| Reset the database | `docker compose down -v` |

---

## Troubleshooting

### Port 9090 is already in use

If startup fails with `Port 9090 was already in use`, find and stop the process holding the port.

Windows:

```powershell
netstat -ano | findstr :9090
taskkill /PID <PID> /F
```

Linux/macOS:

```bash
lsof -i :9090
kill -9 <PID>
```

Replace `<PID>` with the process id from the output, then start the app again.

### Build fails with Checkstyle violations

Read the file name, line number and rule in the error, fix the code, and run `mvn checkstyle:check` again.

### Build fails with "The following files had format violations"

Run `mvn spotless:apply`, then build again.

### Build fails with "Coverage checks have not been met"

New code was added without tests. Add JUnit tests for it, then run `mvn clean verify` again. Open `target/site/jacoco/index.html` to see which lines are not tested.

### Docker problems

| Error | Fix |
|-------|-----|
| `error during connect` / `cannot find the file specified` | Docker Desktop is not running — see Step 13.2 |
| `ports are not available` / `port is already allocated` on 9090 | Port 9090 is in use (maybe by `mvn spring-boot:run`). Stop it, or change `"9090:9090"` to `"9091:9090"` in `compose.yaml` and open `http://localhost:9091/name` |
| `ports are not available` on 3306 / 3307 | Another MySQL uses the port. This project publishes 3307 because a locally installed MySQL often uses 3306 |
| App log: `Communications link failure` | MySQL is not running or not ready. `docker compose ps` must show `trisha-mysql` as `(healthy)` |
| App log: `Access denied for user 'trisha'` | `.env` was changed after the first start. Run `docker compose down -v` (deletes the data), then `docker compose up -d` |
| `container name "/devops-java-demo" is already in use` | An old container from `docker run`. `docker rm -f devops-java-demo`, then run again |
| `Could not transfer artifact ... Premature end of Content-Length` | A Maven download was interrupted by the network. Run `docker build` again — libraries already downloaded are kept in the cache |
| `docker build` fails with Checkstyle or format errors | The lint gate runs inside the build. Run `mvn spotless:apply` and fix Checkstyle errors (Step 9), then build again |
| Page does not open but the container is running | Check the port in the logs (`Tomcat started on port ...`) matches the `-p` mapping |
