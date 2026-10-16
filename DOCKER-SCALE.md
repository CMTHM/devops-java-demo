# Scale the app with Docker Compose and nginx

This guide runs **several copies** of the Spring Boot app on one computer. **nginx** is the only container published on port **9090**. It forwards each request to one of the app copies.

No Java code changes. The Student API does not keep session data in memory. Every copy reads and writes the same MySQL database.

The normal stack in `docker-compose.yml` is unchanged. This stack is a separate file: `docker-compose-scale.yml`.

---

## Contents

1. [What you will run](#1-what-you-will-run)
2. [Why the normal Compose file cannot scale](#2-why-the-normal-compose-file-cannot-scale)
3. [The files](#3-the-files)
4. [Stop the normal stack first](#4-stop-the-normal-stack-first)
5. [Start three app containers](#5-start-three-app-containers)
6. [Prove nginx is sharing the traffic](#6-prove-nginx-is-sharing-the-traffic)
7. [Change the number of copies](#7-change-the-number-of-copies)
8. [MySQL stays at one copy](#8-mysql-stays-at-one-copy)
9. [Stop the scaled stack](#9-stop-the-scaled-stack)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. What you will run

```text
 Browser  http://localhost:9090
            │
            ▼
 ┌──────────────────────┐
 │ proxy (nginx)        │  published port 9090 → container port 80
 │ devops-java-demo-    │
 │ proxy                │
 └──────────┬───────────┘
            │  Docker DNS name: app   port 9090
            │  one request → one replica
     ┌──────┼──────────────┐
     ▼      ▼              ▼
   app-1   app-2   ...   app-N          no host port
     │      │              │
     └──────┼──────────────┘
            │  Docker DNS name: mysqldb   port 3306
            ▼
 ┌──────────────────────┐
 │ mysqldb              │  one database, volume mysql_data
 │ mysql_database_scale │  published port 3307 → 3306
 └──────────────────────┘
```

| Container | How many | Published on your computer | Job |
|-----------|----------|----------------------------|-----|
| `proxy` | 1 | **9090** | Receives browser and curl traffic |
| `app` | 3 by default | none | Spring Boot Student API |
| `mysqldb` | 1 | **3307** | MySQL for every app copy |

Swagger stays at http://localhost:9090/swagger-ui/index.html. Workbench still uses `localhost:3307`.

---

## 2. Why the normal Compose file cannot scale

`docker-compose.yml` is built for one app container:

| Setting | What it does | What happens if you scale |
|---------|--------------|---------------------------|
| `container_name: devops-java-demo` | Pins one name | The second container cannot use the same name |
| `ports: "9090:9090"` | Binds host port 9090 | Only the first container gets that port |

`docker-compose-scale.yml` leaves both of those off the `app` service. nginx owns host port 9090. Docker's DNS name `app` points at every app replica.

---

## 3. The files

| File | Role |
|------|------|
| `docker-compose-scale.yml` | MySQL, the app (scalable), and nginx |
| `nginx/nginx.conf` | Forwards `/` to `app:9090` and logs which replica answered |
| `Dockerfile` | Same image as the normal stack. Not modified |

`nginx.conf` is mounted as nginx's site file. It looks up the name `app` in Docker's DNS (`127.0.0.11`). A fixed `proxy_pass http://app:9090` would resolve that name only once, when nginx starts, and would keep sending traffic to a single replica.

---

## 4. Stop the normal stack first

Both stacks publish **9090** and **3307**. Stop the normal one before starting this one. From the project folder:

```powershell
docker compose down
```

`docker compose down` keeps the normal stack's database volume. This scaled stack uses its **own** volume (`devops-java-demo-scale_mysql_data`), so it starts with an empty `students` table.

---

## 5. Start three app containers

Docker Desktop must be running.

```powershell
docker compose -f docker-compose-scale.yml up -d --build --scale app=3
```

- `-f docker-compose-scale.yml` — use this file, not `docker-compose.yml`.
- `--build` — build `devops-java-demo:1.0.0` from the `Dockerfile` if it is missing or stale.
- `--scale app=3` — three app containers. The file also sets `deploy.replicas: 3`.

The first run downloads MySQL and nginx and builds the app image. Later starts are faster.

MySQL has a health check. The app containers start only after MySQL accepts connections. nginx starts when the app containers have been created. Spring Boot still needs a few seconds after that.

Check status:

```powershell
docker compose -f docker-compose-scale.yml ps
```

You want one `proxy`, one `mysqldb` marked `healthy`, and three `app` rows. Watch one app log until you see `Started SpringLabApplication` (Ctrl+C stops watching; the containers keep running):

```powershell
docker compose -f docker-compose-scale.yml logs -f app
```

Then open http://localhost:9090/name. Expected text: `Welcome to TrishaAcademy`.

On the first start, all three apps may try to create the `students` table at the same time. A replica can restart once and then stay up. Wait until `ps` shows all three app containers as `Up`.

---

## 6. Prove nginx is sharing the traffic

The welcome text is the same from every replica. The nginx log shows the difference. `upstream=` is the app container that handled the request.

```powershell
1..12 | ForEach-Object { curl.exe -s http://localhost:9090/name | Out-Null }
docker compose -f docker-compose-scale.yml logs --tail 20 proxy
```

A shared result looks like this (the IP addresses will differ):

```text
proxy-1  | 192.168.65.1 [15/Oct/2026:12:00:01 +0000] "GET /name HTTP/1.1" 200 upstream=172.20.0.5:9090
proxy-1  | 192.168.65.1 [15/Oct/2026:12:00:01 +0000] "GET /name HTTP/1.1" 200 upstream=172.20.0.6:9090
proxy-1  | 192.168.65.1 [15/Oct/2026:12:00:02 +0000] "GET /name HTTP/1.1" 200 upstream=172.20.0.7:9090
```

Map those addresses to container names:

```powershell
docker compose -f docker-compose-scale.yml ps -q app | ForEach-Object {
  docker inspect -f "{{.Name}} {{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}" $_
}
```

Insert a student through the proxy, the same URL as the normal stack:

```powershell
curl.exe -X POST http://localhost:9090/students -H "Content-Type: application/json" -d "{\"name\":\"Priya\",\"course\":\"DevOps\"}"
```

`spring.jpa.show-sql=true` prints the `INSERT` in **one** app container's log. The other two do not run that statement. All three still see the row, because it is stored in MySQL:

```powershell
curl.exe http://localhost:9090/students
```

---

## 7. Change the number of copies

Scale up or down without rebuilding the image:

```powershell
docker compose -f docker-compose-scale.yml up -d --scale app=5
docker compose -f docker-compose-scale.yml up -d --scale app=1
```

nginx reads the name `app` again within about 5 seconds, so you do not restart the proxy after a scale change.

`--scale` only changes the `app` service. MySQL and nginx stay at one container each.

---

## 8. MySQL stays at one copy

Do not run `--scale mysqldb=3`.

Those would be three separate databases, not one database split across three servers. They would also fight over the single data volume. Every app replica uses the host name `mysqldb` and port **3306** (the port inside the network, not 3307).

---

## 9. Stop the scaled stack

```powershell
# Stop and remove the containers and the network. The database volume is kept.
docker compose -f docker-compose-scale.yml down

# Also delete this stack's database volume (the students in THIS stack).
docker compose -f docker-compose-scale.yml down -v
```

To go back to one app container published directly on port 9090, start the normal file again:

```powershell
docker compose up -d
```

---

## 10. Troubleshooting

| What you see | What to do |
|--------------|------------|
| `ports are not available` on 9090 or 3307 | The normal stack is still running. `docker compose down`, then start this file again |
| `container name "/mysql_database_scale" is already in use` | An old scaled container is still there. `docker compose -f docker-compose-scale.yml down`, then start again |
| `GET /name` returns `502 Bad Gateway` | The app is not listening yet. Wait for `Started SpringLabApplication` in `docker compose -f docker-compose-scale.yml logs app` |
| Every `upstream=` address is the same | Replicas were not ready when you curled. Wait until three app containers are `Up`, wait 5 seconds, and run the curl loop again |
| App log: `Communications link failure` | MySQL was not healthy yet. `docker compose -f docker-compose-scale.yml ps` should show `mysqldb` as `healthy`. The app restarts on its own (`restart: unless-stopped`) |
| An app restarts once on the very first start | Two replicas tried to create `students` together. After the table exists, they stay up |
| `nginx: [emerg] unknown directive` | `nginx/nginx.conf` was saved with Windows line endings. The file in Git is LF. Save it as LF and restart the proxy |

### What Compose scaling does not do

You choose the count with `--scale`. Compose does not add containers when CPU rises, and every container runs on this computer. That next step is Kubernetes.
