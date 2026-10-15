# TRISHA ACADEMY — DevOps Java Demo

A small Spring Boot 3 application used for DevOps training. It has:

- A **Welcome API** that shows a name.
- A **Student CRUD API** (insert, read, update, delete) that stores data in an **H2** database.
- **Swagger** pages to try every API from the browser.
- **Lint** (Checkstyle), **formatting** (Spotless), **JUnit 5 tests** and a **code coverage** check (JaCoCo) that run on every build.

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
8. [View the data in the H2 database](#step-8--view-the-data-in-the-h2-database)
9. [Run lint and format checks](#step-9--run-lint-and-format-checks)
10. [Run the JUnit tests](#step-10--run-the-junit-tests)
11. [Run the full build with coverage](#step-11--run-the-full-build-with-coverage)
12. [Package and run the JAR](#step-12--package-and-run-the-jar)
13. [Troubleshooting](#troubleshooting)

---

## Step 1 — Install the requirements

| Tool | Version | Check it is installed |
|------|---------|-----------------------|
| JDK (Java) | 17 or newer | `java -version` |
| Maven | 3.8 or newer | `mvn -v` |

Run both commands in a terminal. Each should print a version number. If you see "command not found" / "not recognized", install the tool and add it to your `PATH`.

No database or Docker is needed — H2 runs inside the application.

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
    │   └── resources/application.properties     # Port, H2 database settings
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

```bash
mvn spring-boot:run
```

Wait until the console shows:

```text
Started SpringLabApplication in ... seconds
```

The application is now running on **port 8080**. Keep this terminal open. To stop the application, press `Ctrl + C`.

Quick check — open http://localhost:8080/name in the browser. It shows:

```text
My name is Bhagyashree Behera
```

---

## Step 6 — Call the APIs

### API list

| API | Operation | Method | URL | Success code |
|-----|-----------|--------|-----|--------------|
| Welcome | Show name | GET | `/name` | 200 |
| Students | Insert | POST | `/students` | 201 |
| Students | Get all | GET | `/students` | 200 |
| Students | Get one | GET | `/students/{id}` | 200 (404 if not found) |
| Students | Update | PUT | `/students/{id}` | 200 (404 if not found) |
| Students | Delete | DELETE | `/students/{id}` | 204 (404 if not found) |

### Try them with curl

Open a **second** terminal (the app keeps running in the first one) and run these in order:

```bash
# 1. Show name
curl http://localhost:8080/name

# 2. Insert a student (the server assigns the id)
curl -X POST http://localhost:8080/students -H "Content-Type: application/json" -d "{\"name\":\"Priya\",\"course\":\"DevOps\"}"

# 3. Get all students
curl http://localhost:8080/students

# 4. Get the student with id 1
curl http://localhost:8080/students/1

# 5. Update the student with id 1
curl -X PUT http://localhost:8080/students/1 -H "Content-Type: application/json" -d "{\"name\":\"Priya\",\"course\":\"Java\"}"

# 6. Delete the student with id 1
curl -X DELETE http://localhost:8080/students/1
```

> On Windows PowerShell use `curl.exe` instead of `curl`. On Linux/macOS you can use single quotes around the JSON: `-d '{"name":"Priya","course":"DevOps"}'`.

A full PDF guide with all CRUD APIs, HTTP status codes and interview questions is in [docs/REST-API-CRUD-Guide.pdf](./docs/REST-API-CRUD-Guide.pdf).

---

## Step 7 — Use Swagger

Swagger is a web page that lists every API and lets you call it from the browser, without curl or Postman.

| Page | URL |
|------|-----|
| Swagger UI (interactive page) | http://localhost:8080/swagger-ui/index.html |
| OpenAPI JSON (raw API spec) | http://localhost:8080/v3/api-docs |

### 7.1 Open Swagger

1. Make sure the application is running (Step 5).
2. Open http://localhost:8080/swagger-ui/index.html.
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
| 1 | `GET /name` | nothing | 200, `My name is Bhagyashree Behera` |
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

## Step 8 — View the data in the H2 database

The app uses an **H2 in-memory database**. The `students` table is created automatically from `model/Student.java`. Data is **lost when the app stops**.

| Setting | Value |
|---------|-------|
| JDBC URL | `jdbc:h2:mem:trishadb` |
| Username | `sa` |
| Password | `sa@123` |
| Table | `students` |

Steps:

1. Make sure the application is running (Step 5) and insert a student (Step 6 or 7).
2. Open http://localhost:8080/h2-console.
3. Set **JDBC URL** to `jdbc:h2:mem:trishadb`, **User Name** to `sa`, **Password** to `sa@123`.
4. Click **Connect**.
5. Run:

   ```sql
   SELECT * FROM students;
   ```

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
| `controller/WelcomeControllerTest` | Controller test (MockMvc) | `GET /name` returns 200 and the name |
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

The application starts on port 8080, the same as Step 5. Press `Ctrl + C` to stop it.

---

## Command summary

| Goal | Command |
|------|---------|
| Run the app | `mvn spring-boot:run` |
| Lint check | `mvn checkstyle:check` |
| Format check | `mvn spotless:check` |
| Fix formatting | `mvn spotless:apply` |
| Run JUnit tests | `mvn test` |
| Full build + coverage | `mvn clean verify` |
| Build the JAR | `mvn clean package` |
| Run the JAR | `java -jar target/devops-java-demo-1.0.0.jar` |

---

## Troubleshooting

### Port 8080 is already in use

If startup fails with `Port 8080 was already in use`, find and stop the process holding the port.

Windows:

```powershell
netstat -ano | findstr :8080
taskkill /PID <PID> /F
```

Linux/macOS:

```bash
lsof -i :8080
kill -9 <PID>
```

Replace `<PID>` with the process id from the output, then start the app again.

### Build fails with Checkstyle violations

Read the file name, line number and rule in the error, fix the code, and run `mvn checkstyle:check` again.

### Build fails with "The following files had format violations"

Run `mvn spotless:apply`, then build again.

### Build fails with "Coverage checks have not been met"

New code was added without tests. Add JUnit tests for it, then run `mvn clean verify` again. Open `target/site/jacoco/index.html` to see which lines are not tested.
