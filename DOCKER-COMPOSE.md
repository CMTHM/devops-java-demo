# Docker Compose — Java App + MySQL

This guide runs the **devops-java-demo** Student API with **Docker Compose**: two containers, one for **MySQL** and one for the **Spring Boot application**, started with a single command.

---

## Contents

1. [What you will build](#1-what-you-will-build)
2. [Why Docker Compose?](#2-why-docker-compose)
3. [The files involved](#3-the-files-involved)
4. [compose.yaml line by line](#4-composeyaml-line-by-line)
5. [How the app finds MySQL](#5-how-the-app-finds-mysql)
6. [Run it step by step](#6-run-it-step-by-step)
7. [Look at the data in MySQL](#7-look-at-the-data-in-mysql)
8. [Prove the data is kept](#8-prove-the-data-is-kept)
9. [Run the app locally against the MySQL container](#9-run-the-app-locally-against-the-mysql-container)
10. [Rebuild after a code change](#10-rebuild-after-a-code-change)
11. [Docker Compose command cheat sheet](#11-docker-compose-command-cheat-sheet)
12. [Troubleshooting](#12-troubleshooting)
13. [Interview questions](#13-interview-questions)

---

## 1. What you will build

```text
 Your computer (Docker Desktop)
 ┌───────────────────────────────────────────────────────────────────────┐
 │  Network: devops-java-demo_trisha-net                                 │
 │                                                                       │
 │   ┌──────────────────────────┐          ┌──────────────────────────┐  │
 │   │ service: app             │  JDBC    │ service: mysql           │  │
 │   │ container: devops-java-  │ ───────► │ container: trisha-mysql  │  │
 │   │            demo          │ mysql:   │ image: mysql:8.4         │  │
 │   │ Spring Boot, port 9090   │  3306    │ port 3306                │  │
 │   └────────────▲─────────────┘          └─────────────┬────────────┘  │
 │                │                                      │               │
 └────────────────┼──────────────────────────────────────┼───────────────┘
                  │ 9090:9090                            │ /var/lib/mysql
     Browser / Postman / curl                   Volume: devops-java-demo_mysql-data
     http://localhost:9090                      (the database files - kept on "down")
```

| Container | Service name | Image | Port on your computer | Job |
|-----------|--------------|-------|-----------------------|-----|
| `trisha-mysql` | `mysql` | `mysql:8.4` (official image) | `3307` | Stores the `students` table |
| `devops-java-demo` | `app` | `devops-java-demo:1.0.0` (built from the `Dockerfile`) | `9090` | Student CRUD API + Swagger |

---

## 2. Why Docker Compose?

Without Compose you must type (and remember) all of these commands, in the right order:

```powershell
docker network create trisha-net
docker volume create mysql-data

docker run -d --name trisha-mysql --network trisha-net -p 3307:3306 `
  -e MYSQL_ROOT_PASSWORD=root@123 -e MYSQL_DATABASE=trishadb `
  -e MYSQL_USER=trisha -e MYSQL_PASSWORD=trisha@123 `
  -v mysql-data:/var/lib/mysql mysql:8.4

# wait until MySQL is ready ...

docker build -t devops-java-demo:1.0.0 .
docker run -d --name devops-java-demo --network trisha-net -p 9090:9090 `
  -e SPRING_DATASOURCE_URL="jdbc:mysql://trisha-mysql:3306/trishadb?useSSL=false&allowPublicKeyRetrieval=true" `
  -e SPRING_DATASOURCE_USERNAME=trisha -e SPRING_DATASOURCE_PASSWORD=trisha@123 `
  devops-java-demo:1.0.0
```

With Compose, all of that is written **once** in `compose.yaml`, and you run:

```powershell
docker compose up -d --build
```

| | `docker run` commands | Docker Compose |
|--|------------------------|----------------|
| Setup | Many long commands | One file, one command |
| Network and volume | Create them yourself | Created automatically |
| Start order | You wait for MySQL yourself | `depends_on` + health check |
| Share with the team | Copy commands into a document | Commit `compose.yaml` to Git |
| Stop everything | Stop and remove each container | `docker compose down` |

> **Docker Compose** is a tool for defining and running **multi-container** applications. It is part of Docker Desktop. Use the command `docker compose` (with a space). The old `docker-compose` (with a hyphen) is the retired version 1.

---

## 3. The files involved

```text
devops-java-demo/
├── compose.yaml                         # The two services, the volume and the network
├── .env                                 # Database name, users and passwords used by compose.yaml
├── Dockerfile                           # How the "app" image is built
├── .dockerignore                        # Keeps .env, compose.yaml, target/ ... out of the image
├── pom.xml                              # mysql-connector-j (MySQL driver); H2 only for tests
└── src/main/resources/application.properties   # Default database settings (overridden by Compose)
```

### 3.1 `.env`

Docker Compose reads `.env` from the project folder **automatically** and replaces every `${NAME}` in `compose.yaml` with its value:

```properties
MYSQL_ROOT_PASSWORD=root@123
MYSQL_DATABASE=trishadb
MYSQL_USER=trisha
MYSQL_PASSWORD=trisha@123
```

> These are training passwords. In a real project, never commit `.env` with real passwords — add it to `.gitignore` and use a secrets manager.

### 3.2 `application.properties`

```properties
spring.datasource.url=jdbc:mysql://localhost:3307/trishadb?useSSL=false&allowPublicKeyRetrieval=true&serverTimezone=UTC
spring.datasource.username=trisha
spring.datasource.password=trisha@123
spring.jpa.hibernate.ddl-auto=update
```

- These defaults are for running the app **on your computer** (Section 9). `localhost:3307` is the MySQL container's published port.
- Inside Compose they are **replaced** by environment variables (Section 5).
- `ddl-auto=update` creates the `students` table on the first start and keeps the data afterwards.

### 3.3 `pom.xml`

| Dependency | Scope | Why |
|------------|-------|-----|
| `com.mysql:mysql-connector-j` | `runtime` | JDBC driver to talk to MySQL |
| `com.h2database:h2` | `test` | `mvn test` / `mvn verify` use an in-memory database, so the build does **not** need MySQL running |

---

## 4. compose.yaml line by line

```yaml
name: devops-java-demo

services:
  mysql:
    image: mysql:8.4
    container_name: trisha-mysql
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: ${MYSQL_DATABASE}
      MYSQL_USER: ${MYSQL_USER}
      MYSQL_PASSWORD: ${MYSQL_PASSWORD}
    ports:
      - "3307:3306"
    volumes:
      - mysql-data:/var/lib/mysql
    networks:
      - trisha-net
    healthcheck:
      test: ["CMD-SHELL", "mysqladmin ping -h 127.0.0.1 -u root -p$$MYSQL_ROOT_PASSWORD"]
      interval: 10s
      timeout: 5s
      retries: 10
      start_period: 30s
    restart: unless-stopped

  app:
    build: .
    image: devops-java-demo:1.0.0
    container_name: devops-java-demo
    environment:
      SPRING_DATASOURCE_URL: jdbc:mysql://mysql:3306/${MYSQL_DATABASE}?useSSL=false&allowPublicKeyRetrieval=true&serverTimezone=UTC
      SPRING_DATASOURCE_USERNAME: ${MYSQL_USER}
      SPRING_DATASOURCE_PASSWORD: ${MYSQL_PASSWORD}
    ports:
      - "9090:9090"
    depends_on:
      mysql:
        condition: service_healthy
    networks:
      - trisha-net
    restart: unless-stopped

volumes:
  mysql-data:

networks:
  trisha-net:
```

### 4.1 Top level

| Key | Meaning |
|-----|---------|
| `name: devops-java-demo` | Project name. It is the prefix of everything Compose creates: `devops-java-demo_mysql-data`, `devops-java-demo_trisha-net` |
| `services:` | The containers to run — here `mysql` and `app` |
| `volumes:` | Named volumes to create — `mysql-data` |
| `networks:` | Networks to create — `trisha-net` (a user-defined bridge network) |

### 4.2 The `mysql` service

| Key | Meaning |
|-----|---------|
| `image: mysql:8.4` | Official MySQL image, version 8.4 (LTS), downloaded from Docker Hub |
| `container_name: trisha-mysql` | Fixed container name (otherwise Compose names it `devops-java-demo-mysql-1`) |
| `environment:` | On the **first** start the MySQL image creates the root password, the `trishadb` database and the `trisha` user from these variables |
| `ports: "3307:3306"` | Host port **3307** → container port **3306**. Only needed to connect from your computer (Workbench, `mvn spring-boot:run`). 3307 is used because 3306 is often taken by a locally installed MySQL |
| `volumes: mysql-data:/var/lib/mysql` | MySQL stores its data files in `/var/lib/mysql`; the named volume keeps them when the container is removed |
| `networks: trisha-net` | Joins the shared network so the app can reach it |
| `healthcheck:` | Every 10 s Docker runs `mysqladmin ping`. The container becomes **healthy** when MySQL accepts connections |
| `$$MYSQL_ROOT_PASSWORD` | `$$` = a literal `$`, so the password is read inside the container, not replaced by Compose |
| `restart: unless-stopped` | Restart automatically if it crashes or Docker restarts, unless you stopped it |

### 4.3 The `app` service

| Key | Meaning |
|-----|---------|
| `build: .` | Build the image from the `Dockerfile` in this folder |
| `image: devops-java-demo:1.0.0` | Name and tag for the built image |
| `container_name: devops-java-demo` | Fixed container name |
| `SPRING_DATASOURCE_URL` | Overrides `spring.datasource.url`. Host is **`mysql`** (the service name) and port **3306** (the container port) |
| `SPRING_DATASOURCE_USERNAME` / `_PASSWORD` | Override the username and password |
| `ports: "9090:9090"` | Open the API on http://localhost:9090 |
| `depends_on: mysql: condition: service_healthy` | Start the app **only after** MySQL is healthy |
| `networks: trisha-net` | Same network as MySQL |

---

## 5. How the app finds MySQL

### 5.1 The service name is the host name

Compose puts both containers on the network `trisha-net`. Docker's built-in DNS resolves every **service name** to the container's IP address:

```powershell
docker exec devops-java-demo getent hosts mysql
# 172.18.0.2        mysql  mysql
```

That is why the URL inside Compose is `jdbc:mysql://mysql:3306/trishadb`.

### 5.2 Which port when?

| Who connects | Host | Port | Why |
|--------------|------|------|-----|
| `app` container → MySQL | `mysql` | **3306** | Container to container on the same network: the container port, no `ports:` needed |
| Your computer → MySQL (Workbench, `mvn spring-boot:run`) | `localhost` | **3307** | Through the published port `3307:3306` |
| Your browser → app | `localhost` | **9090** | Through the published port `9090:9090` |

> `localhost` inside a container means **that container itself**. The app container must never use `localhost` to reach MySQL.

### 5.3 Environment variables override application.properties

Spring Boot maps environment variables to properties automatically (upper case, `_` instead of `.`):

| Environment variable (compose.yaml) | Property (application.properties) |
|-------------------------------------|-----------------------------------|
| `SPRING_DATASOURCE_URL` | `spring.datasource.url` |
| `SPRING_DATASOURCE_USERNAME` | `spring.datasource.username` |
| `SPRING_DATASOURCE_PASSWORD` | `spring.datasource.password` |

Environment variables win, so the **same image** works on your laptop, in Compose, and on a server — only the variables change.

### 5.4 Start order

```text
docker compose up
  ├─ start mysql ──► first start: create database + user (~20-30 s) ──► health check passes ──► healthy
  └─ start app   (waits for "healthy") ──────────────────────────────────────────────────────► Started
```

Without the health check, `depends_on` only waits for the MySQL **container** to start, not for MySQL to be **ready**, and the app would fail with `Communications link failure`.

---

## 6. Run it step by step

### 6.1 Start Docker Desktop

```powershell
docker info
```

It must print server details without an error.

### 6.2 Go to the project folder

```powershell
cd D:\TRISHA-ACADEMY\DevOPs\devops-java-demo
```

### 6.3 Check the file

```powershell
docker compose config
```

Prints the final configuration with the `.env` values filled in. Any YAML mistake is reported here.

### 6.4 Build and start both containers

```powershell
docker compose up -d --build
```

| Flag | Meaning |
|------|---------|
| `up` | Create the network, volume and containers, and start them |
| `-d` | Run in the background (detached) |
| `--build` | Build the `app` image first (needed the first time and after code changes) |

Expected output (end):

```text
 Container trisha-mysql      Started
 Container trisha-mysql      Waiting
 Container trisha-mysql      Healthy
 Container devops-java-demo  Starting
 Container devops-java-demo  Started
```

The first run takes a few minutes (downloads `mysql:8.4` and the Maven libraries).

### 6.5 Check the containers

```powershell
docker compose ps
```

```text
NAME               SERVICE   STATUS                    PORTS
devops-java-demo   app       Up 14 seconds             0.0.0.0:9090->9090/tcp
trisha-mysql       mysql     Up 36 seconds (healthy)   0.0.0.0:3307->3306/tcp
```

### 6.6 Watch the logs

```powershell
docker compose logs -f app       # Ctrl + C to stop watching
```

Wait for:

```text
HikariPool-1 - Start completed.
Started SpringLabApplication in 8.1 seconds
```

`HikariPool-1 - Start completed` means the app is connected to MySQL.

### 6.7 Call the APIs

PowerShell:

```powershell
Invoke-RestMethod http://localhost:9090/name

Invoke-RestMethod -Method Post -Uri http://localhost:9090/students `
  -ContentType "application/json" -Body '{"name":"Priya","course":"DevOps"}'

Invoke-RestMethod -Method Post -Uri http://localhost:9090/students `
  -ContentType "application/json" -Body '{"name":"Rahul","course":"Java"}'

Invoke-RestMethod http://localhost:9090/students
```

Expected:

```text
Welcome to TrishaAcademy

id name  course
-- ----  ------
 1 Priya DevOps
 2 Rahul Java
```

Or open Swagger: http://localhost:9090/swagger-ui/index.html

---

## 7. Look at the data in MySQL

### 7.1 With the MySQL client inside the container

```powershell
docker exec -it trisha-mysql mysql -utrisha -ptrisha@123 trishadb
```

```sql
SHOW TABLES;
SELECT * FROM students;
DESCRIBE students;
EXIT;
```

```text
+----+--------+-------+
| id | course | name  |
+----+--------+-------+
|  1 | DevOps | Priya |
|  2 | Java   | Rahul |
+----+--------+-------+
```

One-line version:

```powershell
docker exec trisha-mysql mysql -utrisha -ptrisha@123 trishadb -e "SELECT * FROM students;"
```

### 7.2 With MySQL Workbench / DBeaver

| Setting | Value |
|---------|-------|
| Host | `localhost` |
| Port | `3307` |
| Username | `trisha` (or `root`) |
| Password | `trisha@123` (root: `root@123`) |
| Database | `trishadb` |

---

## 8. Prove the data is kept

| # | Test | Commands | Expected |
|---|------|----------|----------|
| 1 | Restart | `docker compose restart` | Students still listed |
| 2 | Remove the containers | `docker compose down`, then `docker compose up -d` | Students still listed — the volume was **not** removed |
| 3 | Rebuild the app image | `docker compose up -d --build` | Students still listed — data is in MySQL, not in the app |
| 4 | Remove containers **and** volume | `docker compose down -v`, then `docker compose up -d` | **Empty** list — the database was deleted |

Check after each step:

```powershell
Invoke-RestMethod http://localhost:9090/students
```

See the volume:

```powershell
docker volume ls --filter name=devops-java-demo
# local     devops-java-demo_mysql-data

docker volume inspect devops-java-demo_mysql-data
```

> `docker compose down` removes containers and the network but **keeps volumes**. `docker compose down -v` also removes the volumes — the data is gone for good.

---

## 9. Run the app locally against the MySQL container

Useful while coding: MySQL in Docker, the app in your IDE or with Maven.

```powershell
docker compose up -d mysql          # start only the database
docker compose stop app             # free port 9090 if the app container is running
mvn spring-boot:run                 # uses localhost:3307 from application.properties
```

You see the same students, because both use the same MySQL database.

When finished, press `Ctrl + C` and start the app container again:

```powershell
docker compose up -d
```

> `mvn test` and `mvn verify` do **not** need MySQL — the tests use an in-memory H2 database.

---

## 10. Rebuild after a code change

```powershell
docker compose up -d --build app
```

Compose rebuilds the `app` image and recreates only the `app` container. MySQL keeps running and the data is kept.

Other options:

```powershell
docker compose build app            # build only, do not start
docker compose build --no-cache app # build from scratch
```

---

## 11. Docker Compose command cheat sheet

| Goal | Command |
|------|---------|
| Validate and show the final file | `docker compose config` |
| Build and start everything | `docker compose up -d --build` |
| Start only MySQL | `docker compose up -d mysql` |
| List the containers of this project | `docker compose ps` |
| All logs / follow one service | `docker compose logs` / `docker compose logs -f app` |
| Stop (keep containers) | `docker compose stop` |
| Start stopped containers | `docker compose start` |
| Restart one service | `docker compose restart app` |
| Shell inside a container | `docker compose exec app sh` |
| MySQL client | `docker compose exec mysql mysql -utrisha -ptrisha@123 trishadb` |
| Running processes | `docker compose top` |
| Images used | `docker compose images` |
| Stop and remove containers + network | `docker compose down` |
| Same, and delete the database volume | `docker compose down -v` |
| Same, and delete the built image too | `docker compose down -v --rmi local` |

> All `docker compose` commands must be run from the folder that contains `compose.yaml` (or use `-f path\to\compose.yaml`).

---

## 12. Troubleshooting

| Problem | Cause and fix |
|---------|---------------|
| `ports are not available: ... 0.0.0.0:3306` | A MySQL installed on Windows already uses 3306. This project publishes **3307** for that reason. Check with `netstat -ano \| findstr :3307` |
| `ports are not available: ... 0.0.0.0:9090` | Something else uses 9090 (often `mvn spring-boot:run` or `java -jar`). Stop it, or change to `"9091:9090"` |
| App log: `Communications link failure` | MySQL was not ready, or the URL host is wrong. Inside Compose the host must be `mysql` (not `localhost`) |
| App log: `Access denied for user 'trisha'` | You changed `.env` after the first start. The MySQL image reads these variables **only when the volume is empty**. Run `docker compose down -v`, then `up -d` (deletes the data) |
| App log: `Public Key Retrieval is not allowed` | Keep `allowPublicKeyRetrieval=true` in the JDBC URL (MySQL 8 default authentication) |
| `trisha-mysql` stays `(health: starting)` | First start takes 20–40 s. Check `docker compose logs mysql` |
| `container name "/devops-java-demo" is already in use` | An old container from `docker run`. `docker rm -f devops-java-demo`, then `docker compose up -d` |
| Old code still running after a change | You forgot `--build`: `docker compose up -d --build app` |
| `no configuration file provided: not found` | You are not in the project folder — `cd` to the folder with `compose.yaml` |

---

## 13. Interview questions

1. **What is Docker Compose?** A tool to define and run multi-container applications from one YAML file (`compose.yaml`) with commands such as `docker compose up` and `docker compose down`.
2. **`docker compose` vs `docker-compose`?** `docker compose` is Compose v2, a Docker CLI plugin. `docker-compose` is the retired Python v1.
3. **How does the app container reach MySQL?** Both are on the same Compose network; Docker DNS resolves the service name `mysql` to the MySQL container's IP, so the URL is `jdbc:mysql://mysql:3306/...`.
4. **Why not `localhost` in the JDBC URL inside the container?** `localhost` is the app container itself; MySQL runs in a different container.
5. **What does `depends_on` do?** Controls start order. With `condition: service_healthy` it waits until the dependency's health check passes.
6. **Why a health check for MySQL?** The container starts before MySQL accepts connections. The health check tells Compose when MySQL is really ready.
7. **`ports` vs container-to-container traffic?** `ports` publishes a port to the host. Containers on the same network talk directly on the container port without `ports`.
8. **What happens to data on `docker compose down`?** Containers and the network are removed; named volumes are kept. `down -v` deletes the volumes too.
9. **How do you pass configuration to the app?** Environment variables in `compose.yaml` (values from `.env`). Spring Boot maps `SPRING_DATASOURCE_URL` to `spring.datasource.url`.
10. **What is `.env` used for?** Variable substitution in `compose.yaml` (`${MYSQL_PASSWORD}`). Compose reads it automatically from the project folder.
11. **`build:` vs `image:`?** `build:` builds an image from a Dockerfile; `image:` names it (or pulls it if there is no `build:`).
12. **How do you rebuild only one service?** `docker compose up -d --build app`.
13. **How do you see logs of one service?** `docker compose logs -f app`.
14. **How would you scale the app?** `docker compose up -d --scale app=3` — but then remove `container_name` and the fixed host port, because names and host ports must be unique.
