# Testing H2 Data Persistence with a Docker Volume

> **Note:** the project now uses **MySQL with Docker Compose** instead of an H2 file. This guide describes the earlier H2 setup and is kept for reference. For the current setup and its persistence tests, see [DOCKER-COMPOSE.md](./DOCKER-COMPOSE.md) (Section 8).

This guide proves, step by step, that student data stored in the **H2 database** is **not lost** when the application or the Docker container is stopped, restarted, deleted or rebuilt.

All commands are for **PowerShell** on Windows and must be run from the project folder:

```powershell
cd D:\TRISHA-ACADEMY\DevOPs\devops-java-demo
```

---

## How it works (1-minute overview)

| Piece | Setting | File |
|-------|---------|------|
| H2 runs in **file mode** (not in-memory) | `spring.datasource.url=jdbc:h2:file:./data/trishadb;WRITE_DELAY=0` | `src/main/resources/application.properties` |
| The database file | `data/trishadb.mv.db` in the project folder | created on first start |
| Docker marks the data folder | `VOLUME ["/app/data"]` | `Dockerfile` |
| The container uses the project's `data` folder | `-v "${PWD}\data:/app/data"` | `docker run` command |
| Tests never touch the real data | `jdbc:h2:mem:testdb` | `pom.xml` (Surefire) |

```text
 Your computer                                  Container
 D:\...\devops-java-demo\data\   <== -v ==>     /app/data/
     trishadb.mv.db                                 trishadb.mv.db  (same file)
```

- **`jdbc:h2:file:`** — data is written to a file instead of memory.
- **`WRITE_DELAY=0`** — every change is written to the file at once, so nothing is lost even if the container is killed.
- **`-v` (bind mount)** — the container writes the file into your project folder, which lives outside the container. Deleting the container does not delete the file.

---

## Helper commands used in the tests

Add a student:

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:9090/students -ContentType "application/json" -Body '{"name":"Priya","course":"DevOps"}'
```

List all students:

```powershell
Invoke-RestMethod http://localhost:9090/students
```

Wait until the app has started (prints `Started SpringLabApplication ...`, press `Ctrl + C` to stop watching):

```powershell
docker logs -f devops-java-demo
```

> You can also use Swagger instead: http://localhost:9090/swagger-ui/index.html → `POST /students` and `GET /students`.

---

## Step 0 — Prepare

1. Start Docker Desktop and check it is running:

   ```powershell
   docker info
   ```

2. Build the image:

   ```powershell
   docker build -t devops-java-demo:1.0.0 .
   ```

3. Start with a clean database (removes any old container and old data):

   ```powershell
   docker rm -f devops-java-demo
   Remove-Item -Recurse -Force data -ErrorAction SilentlyContinue
   ```

---

## Test 1 — Data is saved in the project folder

1. Run the container with the project's `data` folder mounted:

   ```powershell
   docker run -d --name devops-java-demo -p 9090:9090 -v "${PWD}\data:/app/data" devops-java-demo:1.0.0
   ```

2. Wait for `Started SpringLabApplication` (`docker logs -f devops-java-demo`).

3. Add two students:

   ```powershell
   Invoke-RestMethod -Method Post -Uri http://localhost:9090/students -ContentType "application/json" -Body '{"name":"Priya","course":"DevOps"}'
   Invoke-RestMethod -Method Post -Uri http://localhost:9090/students -ContentType "application/json" -Body '{"name":"Rahul","course":"Java"}'
   ```

4. Look at the project folder:

   ```powershell
   Get-ChildItem data
   ```

**Expected:** a file named `trishadb.mv.db` appears in `devops-java-demo\data`.

---

## Test 2 — Data survives a container restart

```powershell
docker restart devops-java-demo
# wait for "Started SpringLabApplication"
Invoke-RestMethod http://localhost:9090/students
```

**Expected:**

```text
id name  course
-- ----  ------
 1 Priya DevOps
 2 Rahul Java
```

---

## Test 3 — Data survives deleting the container (the key test)

Delete the container completely and create a brand-new one with the same `-v`:

```powershell
docker rm -f devops-java-demo
docker run -d --name devops-java-demo -p 9090:9090 -v "${PWD}\data:/app/data" devops-java-demo:1.0.0
# wait for "Started SpringLabApplication"
Invoke-RestMethod http://localhost:9090/students
```

**Expected:** Priya and Rahul are still listed. The old container is gone, but the database file stayed in the project folder.

---

## Test 4 — Data survives a hard kill

`docker kill` stops the app instantly, without a clean shutdown (like a power cut):

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:9090/students -ContentType "application/json" -Body '{"name":"Anil","course":"AWS"}'
docker kill devops-java-demo
docker start devops-java-demo
# wait for "Started SpringLabApplication"
Invoke-RestMethod http://localhost:9090/students
```

**Expected:** Priya, Rahul **and Anil** are listed. `WRITE_DELAY=0` wrote Anil to the file before the kill.

> After a hard kill, the next new student may get a much higher id (for example 33 instead of 4). That is normal: H2 reserves ids in blocks of 32 and skips the unused ones after a crash. No data is lost.

---

## Test 5 — Data survives an image rebuild

```powershell
docker rm -f devops-java-demo
docker build -t devops-java-demo:1.0.0 .
docker run -d --name devops-java-demo -p 9090:9090 -v "${PWD}\data:/app/data" devops-java-demo:1.0.0
# wait for "Started SpringLabApplication"
Invoke-RestMethod http://localhost:9090/students
```

**Expected:** all students are still listed. The image only contains the application; the data lives in the project's `data` folder (and `data/` is in `.dockerignore`, so it is never copied into the image).

---

## Test 6 — Docker and local run share the same database

1. Stop the container (H2 allows only one app to open the file at a time):

   ```powershell
   docker stop devops-java-demo
   ```

2. Run the app locally with Maven:

   ```powershell
   mvn spring-boot:run
   ```

3. In a second terminal:

   ```powershell
   Invoke-RestMethod http://localhost:9090/students
   ```

**Expected:** the same students that were added in Docker. Press `Ctrl + C` in the first terminal to stop the app.

---

## Test 7 — Without a volume the data is lost (why `-v` is needed)

```powershell
docker rm -f devops-java-demo
docker run -d --name devops-java-demo -p 9090:9090 devops-java-demo:1.0.0
# wait for "Started SpringLabApplication"
Invoke-RestMethod -Method Post -Uri http://localhost:9090/students -ContentType "application/json" -Body '{"name":"Temp","course":"Test"}'

docker rm -f -v devops-java-demo
docker run -d --name devops-java-demo -p 9090:9090 devops-java-demo:1.0.0
# wait for "Started SpringLabApplication"
Invoke-RestMethod http://localhost:9090/students
```

**Expected:** an **empty** list — "Temp" is gone. Without `-v`, the database file was stored inside the container and was deleted with it.

Clean up and go back to the normal run command:

```powershell
docker rm -f -v devops-java-demo
docker run -d --name devops-java-demo -p 9090:9090 -v "${PWD}\data:/app/data" devops-java-demo:1.0.0
```

The students from Tests 1–5 are back, because they are still in the project's `data` folder.

---

## Test 8 — JUnit tests do not change the real data

```powershell
docker stop devops-java-demo
(Get-Item data\trishadb.mv.db).LastWriteTime
mvn test
(Get-Item data\trishadb.mv.db).LastWriteTime
```

**Expected:** `Tests run: 18, Failures: 0` and the **same** `LastWriteTime` before and after. Tests use the in-memory database `jdbc:h2:mem:testdb` (set in `pom.xml`).

---

## See the data in the H2 console

1. Make sure the app (or container) is running.
2. Open http://localhost:9090/h2-console.
3. **JDBC URL:** `jdbc:h2:file:./data/trishadb` · **User Name:** `sa` · **Password:** `sa@123`.
4. Click **Connect** and run `SELECT * FROM students;`.

---

## Reset the database

Stop whatever is using the database, then delete the `data` folder:

```powershell
docker rm -f devops-java-demo
Remove-Item -Recurse -Force data
```

The next start creates a new, empty `data\trishadb.mv.db`.

---

## Results checklist

| # | Test | Expected result |
|---|------|-----------------|
| 1 | Data saved in project folder | `data\trishadb.mv.db` exists |
| 2 | `docker restart` | Data kept |
| 3 | `docker rm` + new container with `-v` | Data kept |
| 4 | `docker kill` (hard kill) | Data kept (ids may jump) |
| 5 | Image rebuild | Data kept |
| 6 | Docker → `mvn spring-boot:run` | Same data |
| 7 | No `-v`, container deleted | Data **lost** |
| 8 | `mvn test` | Real database not touched |

---

## Troubleshooting

| Problem | Cause and fix |
|---------|---------------|
| `Database may be already in use` / `The file is locked` | Two apps are using `data\trishadb.mv.db` at the same time. Stop the container (`docker stop devops-java-demo`) or the local app (`Ctrl + C`), then start only one. |
| Data is empty after starting a new container | The `-v "${PWD}\data:/app/data"` part was missing, or the command was run from a different folder (`${PWD}` is the current folder). Run it from the project folder. |
| `port is already allocated` | Something else uses port 9090 (maybe `mvn spring-boot:run`). Stop it first. |
| `Invoke-RestMethod : Unable to connect` | The app has not finished starting. Wait for `Started SpringLabApplication` in `docker logs -f devops-java-demo`. |
| Ids jump (1, 2, 33, 65 …) | Normal after a hard kill — see Test 4. |
