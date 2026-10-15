# Docker Volumes — Complete Guide

How Docker keeps data **outside** a container, explained with the **TRISHA ACADEMY DevOps Java Demo** (Spring Boot + H2 database).

---

## Contents

1. [The problem: containers forget everything](#1-the-problem-containers-forget-everything)
2. [What is a Docker volume?](#2-what-is-a-docker-volume)
3. [The 4 types of mounts](#3-the-4-types-of-mounts)
4. [Named volumes](#4-named-volumes)
5. [Bind mounts](#5-bind-mounts)
6. [Anonymous volumes and the `VOLUME` instruction](#6-anonymous-volumes-and-the-volume-instruction)
7. [tmpfs mounts](#7-tmpfs-mounts)
8. [`-v` vs `--mount` syntax](#8--v-vs---mount-syntax)
9. [Volume commands cheat sheet](#9-volume-commands-cheat-sheet)
10. [Read-only mounts](#10-read-only-mounts)
11. [Sharing a volume between containers](#11-sharing-a-volume-between-containers)
12. [Backup and restore a volume](#12-backup-and-restore-a-volume)
13. [Volumes in Docker Compose](#13-volumes-in-docker-compose)
14. [How this project uses a volume](#14-how-this-project-uses-a-volume)
15. [Best practices](#15-best-practices)
16. [Troubleshooting](#16-troubleshooting)
17. [Interview questions](#17-interview-questions)

---

## 1. The problem: containers forget everything

Every container gets its own **writable layer** on top of the read-only image. Files the app writes (logs, uploads, database files) go into this layer.

```text
┌──────────────────────────────┐
│  Writable container layer    │  <- data written by the app lives here
├──────────────────────────────┤
│  Image layers (read-only)    │  <- Java, Maven, your JAR
└──────────────────────────────┘
```

| Action | Writable layer |
|--------|----------------|
| `docker stop` / `docker start` | Kept |
| `docker restart` | Kept |
| `docker rm` (delete the container) | **Deleted** |
| New container from the same image | **Starts empty** |
| Rebuild the image and run again | **Starts empty** |

In real life containers are deleted and recreated all the time (new version, scaling, crash, server move). A database inside the writable layer would lose all data each time.

**Solution:** store the data in a **volume** — storage that lives **outside** the container.

---

## 2. What is a Docker volume?

A volume is a folder that is **mounted** into the container at a path you choose. The app reads and writes that path normally, but the files are stored outside the container.

```text
 Docker host (your computer / server)            Container
 ┌──────────────────────────────┐               ┌──────────────────────┐
 │  volume / folder             │  <== mount => │  /app/data           │
 │    trishadb.mv.db            │               │    trishadb.mv.db    │
 └──────────────────────────────┘               └──────────────────────┘
        survives docker rm                           deleted by docker rm
```

Key points:

- The container can be deleted and recreated — the volume stays.
- Several containers can use the same volume.
- The volume is **not** part of the image, so data is never baked into the image.

---

## 3. The 4 types of mounts

| Type | Example | Where the data is stored | Managed by | Typical use |
|------|---------|--------------------------|-----------|-------------|
| **Named volume** | `-v trishadb-data:/app/data` | Docker's storage area | Docker | Databases on servers / production |
| **Bind mount** | `-v "${PWD}\data:/app/data"` | Any folder **you** choose on the host | You | Development, seeing/editing files directly |
| **Anonymous volume** | `-v /app/data` or `VOLUME` in Dockerfile | Docker's storage area, random name | Docker | Temporary data |
| **tmpfs** | `--tmpfs /app/cache` | Host **memory (RAM)** only | Docker | Secrets, fast temporary files (Linux only) |

---

## 4. Named volumes

Docker creates and manages the storage. You refer to it by a **name**.

### Create and use

```powershell
# Create (optional - docker run creates it automatically if it does not exist)
docker volume create trishadb-data

# Run the app with the named volume
docker run -d --name devops-java-demo -p 9090:9090 -v trishadb-data:/app/data devops-java-demo:1.0.0
```

### Inspect

```powershell
docker volume ls
docker volume inspect trishadb-data
```

Example output of `inspect`:

```json
[
  {
    "Name": "trishadb-data",
    "Driver": "local",
    "Mountpoint": "/var/lib/docker/volumes/trishadb-data/_data",
    "Scope": "local"
  }
]
```

On Windows/macOS with Docker Desktop, the `Mountpoint` is inside Docker Desktop's Linux VM — not a normal Windows folder. To look at the files, use a container:

```powershell
docker run --rm -v trishadb-data:/data alpine ls -l /data
```

### Facts

- `docker rm` of the container does **not** delete a named volume.
- `docker rm -v` also does **not** delete a named volume (it only removes anonymous ones).
- When an **empty** named volume is mounted over a folder that already has files in the image, Docker **copies those files into the volume** first.
- Works the same on Windows, Linux and macOS — best for servers and production.

---

## 5. Bind mounts

You choose an existing folder on the host and mount it into the container.

```powershell
# PowerShell (Windows) - run from the project folder
docker run -d --name devops-java-demo -p 9090:9090 -v "${PWD}\data:/app/data" devops-java-demo:1.0.0
```

```bash
# Git Bash / Linux / macOS
docker run -d --name devops-java-demo -p 9090:9090 -v "$(pwd)/data:/app/data" devops-java-demo:1.0.0
```

- `${PWD}` (PowerShell) / `$(pwd)` (bash) = the current folder. Always use a **full path** for bind mounts.
- If the host folder does not exist, Docker creates it.
- The host folder **hides** whatever the image had at that path (nothing is copied, unlike named volumes).
- You can open, copy, back up or delete the files directly in Windows Explorer.

### Named volume vs bind mount

| | Named volume | Bind mount |
|--|--------------|------------|
| Who chooses the location | Docker | You |
| See files in Explorer | No (inside Docker's VM) | Yes |
| Depends on host folder structure | No | Yes |
| Speed on Windows/macOS | Faster | Slower (files cross from Windows to the VM) |
| Copies image content on first use | Yes (if empty) | No |
| Best for | Production, servers | Development, demos, learning |

---

## 6. Anonymous volumes and the `VOLUME` instruction

The project's `Dockerfile` contains:

```dockerfile
VOLUME ["/app/data"]
```

What it does:

- Marks `/app/data` as a folder whose data should live **outside** the container.
- If you run the container **without** `-v ... :/app/data`, Docker automatically creates an **anonymous volume** (a long random name) for that path.
- If you run **with** `-v`, your named volume or bind mount is used instead.
- A Dockerfile **cannot** choose a host folder — only `docker run -v` (or Compose) can.

See anonymous volumes:

```powershell
docker volume ls
# DRIVER    VOLUME NAME
# local     3f6c0c3a9e5b4d1c8a...   <- anonymous
# local     trishadb-data           <- named
```

Why anonymous volumes are not enough:

```powershell
docker rm -f -v devops-java-demo       # -v deletes the anonymous volume too
docker run -d --name devops-java-demo -p 9090:9090 devops-java-demo:1.0.0
# -> a NEW anonymous volume is created: the database is empty
```

A new container never reuses an old anonymous volume, because it has no name to refer to. **Always use a named volume or a bind mount for data you want to keep.**

---

## 7. tmpfs mounts

Data is stored only in RAM and is gone when the container stops. Never written to disk.

```bash
docker run -d --tmpfs /app/tmp devops-java-demo:1.0.0
```

Use for secrets or scratch files. **Not** for a database. Works only with Linux containers.

---

## 8. `-v` vs `--mount` syntax

Both do the same thing. `--mount` is longer but clearer, and it gives an error instead of silently creating a missing bind-mount folder.

| | `-v` (short) | `--mount` (long) |
|--|--------------|------------------|
| Named volume | `-v trishadb-data:/app/data` | `--mount type=volume,source=trishadb-data,target=/app/data` |
| Bind mount | `-v "${PWD}\data:/app/data"` | `--mount type=bind,source="${PWD}\data",target=/app/data` |
| Read-only | `-v trishadb-data:/app/data:ro` | `--mount type=volume,source=trishadb-data,target=/app/data,readonly` |
| tmpfs | `--tmpfs /app/tmp` | `--mount type=tmpfs,target=/app/tmp` |

Format of `-v`: `SOURCE:TARGET[:OPTIONS]`

- **SOURCE** = a volume name, or a host path (bind mount).
- **TARGET** = the path inside the container.
- **OPTIONS** = for example `ro` (read-only).

---

## 9. Volume commands cheat sheet

| Goal | Command |
|------|---------|
| Create a volume | `docker volume create trishadb-data` |
| List volumes | `docker volume ls` |
| Details (mount point, driver) | `docker volume inspect trishadb-data` |
| Which containers use a volume | `docker ps -a --filter volume=trishadb-data` |
| Mounts of a container | `docker inspect --format "{{json .Mounts}}" devops-java-demo` |
| Delete a volume (must not be in use) | `docker volume rm trishadb-data` |
| Delete unused anonymous volumes | `docker volume prune` |
| Delete **all** unused volumes (named too!) | `docker volume prune -a` |
| Delete container + its anonymous volumes | `docker rm -v devops-java-demo` |
| Disk usage of volumes | `docker system df -v` |
| Look inside a volume | `docker run --rm -v trishadb-data:/data alpine ls -l /data` |

> **Careful:** `docker volume rm` and `docker volume prune -a` delete the data for good. There is no undo — take a backup first (section 12).

---

## 10. Read-only mounts

Mount a volume so the container can read it but not change it — useful for configuration files.

```powershell
docker run -d -v "${PWD}\config:/app/config:ro" devops-java-demo:1.0.0
```

A write inside `/app/config` fails with `Read-only file system`. **Do not** mount the database folder read-only — H2 must write to it.

---

## 11. Sharing a volume between containers

Several containers can mount the same volume:

```powershell
# App container writes the database
docker run -d --name devops-java-demo -p 9090:9090 -v trishadb-data:/app/data devops-java-demo:1.0.0

# Another container reads the same files
docker run --rm -v trishadb-data:/data alpine ls -l /data

# Or reuse all volumes of an existing container
docker run --rm --volumes-from devops-java-demo alpine ls -l /app/data
```

> H2 in file mode allows only **one** application to open the database at a time. Sharing is fine for reading files, backups or inspection, but do not run two app containers on the same H2 database.

---

## 12. Backup and restore a volume

The trick: start a small temporary container (`alpine`) that mounts **both** the volume and a host folder, and use `tar`.

Stop the app first so the database file is not being written during the backup:

```powershell
docker stop devops-java-demo
```

### Backup a named volume to the current folder

```powershell
docker run --rm -v trishadb-data:/data -v "${PWD}:/backup" alpine tar czf /backup/trishadb-backup.tar.gz -C /data .
```

Result: `trishadb-backup.tar.gz` in the current folder.

### Restore into a (new) volume

```powershell
docker volume create trishadb-data-restored
docker run --rm -v trishadb-data-restored:/data -v "${PWD}:/backup" alpine tar xzf /backup/trishadb-backup.tar.gz -C /data
docker run -d --name devops-java-demo-restored -p 9091:9090 -v trishadb-data-restored:/app/data devops-java-demo:1.0.0
```

Open http://localhost:9091/students — the restored data is there.

### Backup a bind mount

A bind mount is a normal folder, so just copy it:

```powershell
docker stop devops-java-demo
Copy-Item -Recurse data "data-backup-$(Get-Date -Format yyyyMMdd)"
docker start devops-java-demo
```

---

## 13. Volumes in Docker Compose

Compose writes the same options in a `docker-compose.yml` file.

### With a bind mount (database in the project folder)

```yaml
services:
  app:
    image: devops-java-demo:1.0.0
    build: .
    container_name: devops-java-demo
    ports:
      - "9090:9090"
    volumes:
      - ./data:/app/data          # bind mount: relative paths are allowed in Compose
    restart: unless-stopped
```

### With a named volume

```yaml
services:
  app:
    image: devops-java-demo:1.0.0
    build: .
    container_name: devops-java-demo
    ports:
      - "9090:9090"
    volumes:
      - trishadb-data:/app/data   # named volume

volumes:
  trishadb-data:                  # declare the named volume
```

Commands:

| Goal | Command |
|------|---------|
| Build and start | `docker compose up -d --build` |
| Stop and remove containers (volumes kept) | `docker compose down` |
| Stop and remove containers **and named volumes** | `docker compose down -v` |
| List volumes of this project | `docker volume ls --filter label=com.docker.compose.project` |

> Compose prefixes named volumes with the project (folder) name, e.g. `devops-java-demo_trishadb-data`.

---

## 14. How this project uses a volume

### The pieces

| File | Setting | Why |
|------|---------|-----|
| `application.properties` | `spring.datasource.url=jdbc:h2:file:./data/trishadb;WRITE_DELAY=0` | H2 stores data in a **file** (`data/trishadb.mv.db`) instead of memory |
| `application.properties` | `spring.jpa.hibernate.ddl-auto=update` | Keeps existing tables and rows on restart (`create`/`create-drop` would wipe them) |
| `application.properties` | `spring.h2.console.settings.web-allow-others=true` | Lets the H2 console open from your browser when the app runs in Docker (requests come from outside the container) |
| `Dockerfile` | `WORKDIR /app` + `VOLUME ["/app/data"]` | `./data` inside the container is `/app/data`, marked as a volume |
| `.dockerignore` | `data/` | The local database file is never copied into the image |
| `pom.xml` (Surefire) | `jdbc:h2:mem:testdb` | JUnit tests use a throw-away in-memory DB, never the real file |

### Why `WRITE_DELAY=0`?

By default H2 keeps the latest changes in memory for up to about a second before writing them to the file. If the container is hard-killed (`docker kill`, `docker rm -f`, power cut) in that moment, the last changes are lost. `WRITE_DELAY=0` writes every change to the file immediately. This was tested: without it, a student saved right before `docker rm -f` was lost; with it, nothing was lost.

### Run it (bind mount — database in the project folder)

```powershell
cd D:\TRISHA-ACADEMY\DevOPs\devops-java-demo
docker build -t devops-java-demo:1.0.0 .
docker run -d --name devops-java-demo -p 9090:9090 -v "${PWD}\data:/app/data" devops-java-demo:1.0.0
```

The database file appears at `devops-java-demo\data\trishadb.mv.db`. The same file is used by `mvn spring-boot:run`, so you see the same students in both — run only one of them at a time.

### Or run it with a named volume

```powershell
docker run -d --name devops-java-demo -p 9090:9090 -v trishadb-data:/app/data devops-java-demo:1.0.0
```

Data is kept by Docker in the `trishadb-data` volume instead of the project folder.

### Prove it works

```powershell
# Add a student
Invoke-RestMethod -Method Post -Uri http://localhost:9090/students -ContentType "application/json" -Body '{"name":"Priya","course":"DevOps"}'

# Delete the container and create a brand-new one with the same volume
docker rm -f devops-java-demo
docker run -d --name devops-java-demo -p 9090:9090 -v "${PWD}\data:/app/data" devops-java-demo:1.0.0

# After "Started SpringLabApplication" - Priya is still there
Invoke-RestMethod http://localhost:9090/students
```

The full set of tests is in [DB-PERSISTENCE-TESTING.md](./DB-PERSISTENCE-TESTING.md).

### View the data

- **H2 console:** http://localhost:9090/h2-console → JDBC URL `jdbc:h2:file:./data/trishadb`, user `sa`, password `sa@123` → `SELECT * FROM students;`
- **File:** `data\trishadb.mv.db` in the project folder (bind mount), or `docker run --rm -v trishadb-data:/data alpine ls -l /data` (named volume).

---

## 15. Best practices

1. **Never store important data in the container's writable layer** — use a named volume or a bind mount.
2. **Use named volumes in production**, bind mounts for development and demos.
3. **Give volumes clear names** (`trishadb-data`, not random anonymous volumes).
4. **Keep data out of the image** — add data folders to `.dockerignore`.
5. **One writer per database file** — do not run two app containers on the same H2 file.
6. **Stop the app before backing up** a database volume, and test your restore.
7. **Be careful with** `docker volume prune -a`, `docker volume rm` and `docker compose down -v` — they delete data permanently.
8. **For real production databases** (MySQL, PostgreSQL) use the official image with a named volume, e.g. `-v pgdata:/var/lib/postgresql/data`, or a managed service such as Amazon RDS.

---

## 16. Troubleshooting

| Problem | Cause and fix |
|---------|---------------|
| Data is gone after `docker rm` + `docker run` | `-v` was missing, or a different volume name/folder was used. Use exactly the same `-v` every time. |
| New container is empty although `data\trishadb.mv.db` exists | The command was run from another folder, so `${PWD}\data` points somewhere else. `cd` to the project folder first. |
| `Database may be already in use` / file is locked | Two apps use the same H2 file (e.g. the container and `mvn spring-boot:run`). Stop one of them. |
| `docker volume rm` says `volume is in use` | A container (even a stopped one) still uses it. `docker ps -a --filter volume=<name>`, remove that container, then retry. |
| Many unknown volumes in `docker volume ls` | Anonymous volumes from containers run without `-v`. Remove them with `docker volume prune`. |
| H2 console says "remote connections are not allowed" | `spring.h2.console.settings.web-allow-others=true` is missing in `application.properties`. |
| Bind mount works on Linux but not on Windows | Check Docker Desktop → Settings → Resources → File sharing, and use a full Windows path (`${PWD}\data`). |
| Student ids jump (1, 2, 33 …) after a crash | Normal for H2: it reserves ids in blocks and skips unused ones after a hard kill. No data is lost. |

---

## 17. Interview questions

1. **Why is data lost when a container is deleted?**
   It is stored in the container's writable layer, which is deleted with the container.

2. **What is the difference between a named volume and a bind mount?**
   A named volume is created and managed by Docker in its own storage area; a bind mount maps a folder that you choose on the host.

3. **What does the `VOLUME` instruction in a Dockerfile do?**
   It marks a path as external storage. If no `-v` is given, Docker creates an anonymous volume for it. It cannot choose a host folder.

4. **Does `docker rm -v` delete named volumes?**
   No. It only deletes the container's anonymous volumes.

5. **How do you back up a Docker volume?**
   Run a temporary container that mounts the volume and a host folder, and archive the volume with `tar`.

6. **What is the difference between `-v` and `--mount`?**
   Same feature, different syntax. `--mount` uses explicit `key=value` pairs and does not auto-create a missing bind-mount folder.

7. **What happens when you mount an empty named volume over a folder that has files in the image?**
   Docker copies the image's files into the volume first. A bind mount does not copy — it hides the image's files.

8. **When would you use tmpfs?**
   For temporary or sensitive data that must never be written to disk.

9. **How do you share data between two containers?**
   Mount the same named volume in both, or use `--volumes-from`.

10. **Which command removes unused volumes, and what is the risk?**
    `docker volume prune` (anonymous only) or `docker volume prune -a` (all unused). Deleted data cannot be recovered.
