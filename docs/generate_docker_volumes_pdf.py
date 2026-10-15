"""Build the TRISHA ACADEMY "Docker Volumes" student guide.

Reference: https://docs.docker.com/engine/storage/volumes/
Run:  python generate_docker_volumes_pdf.py
Output: docs/docker/Docker-Volumes-Guide.pdf
"""
import os

import k8s_pdf_lib as L
from k8s_pdf_lib import *
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics

L.COURSE = "Docker Volumes - Data Persistence"
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docker")
OUT_FILE = os.path.join(OUT_DIR, "Docker-Volumes-Guide.pdf")
DOCKER_BLUE = HexColor("#1D63ED")


# ---------------------------------------------------------------- layout helpers
def banner(num, title, outcome):
    kicker = Paragraph(f'<font color="#F2A900">DOCKER VOLUMES · PART {num:02d}</font>',
                       S("kick", fontName="Segoe-Bold", fontSize=9, leading=12))
    head = Paragraph(f'<font color="#FFFFFF">{rich(title)}</font>',
                     S("dt", fontName="Segoe-Bold", fontSize=19, leading=24))
    sub = Paragraph(f'<font color="#DCE6FB">{rich(outcome)}</font>', S("ds", fontSize=10, leading=14))
    t = Table([[[kicker, gap(3), head, gap(4), sub]]], colWidths=[CONTENT_W])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NAVY),
        ("LINEBEFORE", (0, 0), (0, -1), 6, DOCKER_BLUE),
        ("LEFTPADDING", (0, 0), (-1, -1), 16),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
    ]))
    return [PageBreak(), Bookmark(f"part{num}", f"Part {num}: {title}"), t, gap(10)]


def official(body, title="From the official Docker documentation"):
    return callout(title, body, BLUE_BG, DOCKER_BLUE)


def draw_docker_cover(c, doc):
    c.saveState()
    c.setFillColor(NAVY_DEEP)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    c.setFillColor(DOCKER_BLUE)
    c.rect(0, PAGE_H - 12, PAGE_W, 12, fill=1, stroke=0)
    c.setFillColor(GOLD)
    c.rect(0, 0, PAGE_W, 6, fill=1, stroke=0)
    # stacked "shipping containers" and a volume cylinder
    for row in range(3):
        for col in range(3 - row):
            x = PAGE_W - 300 + col * 78 + row * 39
            y = PAGE_H - 330 + row * 46
            c.setFillColor(HexColor("#22335A"))
            c.roundRect(x, y, 72, 40, 4, fill=1, stroke=0)
            c.setStrokeColor(HexColor("#2E4572"))
            c.setLineWidth(2)
            for k in range(1, 5):
                c.line(x + k * 14.4, y + 6, x + k * 14.4, y + 34)
    cx, cy = PAGE_W - 95, PAGE_H - 420
    c.setFillColor(DOCKER_BLUE)
    c.rect(cx - 45, cy - 50, 90, 50, fill=1, stroke=0)
    c.ellipse(cx - 45, cy - 62, cx + 45, cy - 38, fill=1, stroke=0)
    c.setFillColor(HexColor("#4C86F5"))
    c.ellipse(cx - 45, cy - 12, cx + 45, cy + 12, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Segoe-Bold", 10)
    c.drawCentredString(cx, cy - 32, "VOLUME")

    c.setFillColor(GOLD)
    c.setFont("Segoe-Bold", 13)
    c.drawString(60, PAGE_H - 90, ACADEMY)
    c.setFillColor(HexColor("#9FB4E0"))
    c.setFont("Segoe", 10)
    c.drawString(60, PAGE_H - 106, "DevOps Career Track · Student Notes")
    c.setFillColor(WHITE)
    c.setFont("Segoe-Bold", 34)
    c.drawString(60, 440, "Docker Volumes")
    c.drawString(60, 398, "& Data Persistence")
    c.setFillColor(HexColor("#C9D6F5"))
    c.setFont("Segoe", 14)
    c.drawString(60, 360, "Keep your data when containers come and go")
    c.setFont("Segoe-Italic", 11)
    c.setFillColor(HexColor("#9FB4E0"))
    c.drawString(60, 336, "Based on docs.docker.com/engine/storage/volumes · Lab: Spring Boot + H2")
    chips = ["Named volumes", "Anonymous volumes", "Bind mounts", "tmpfs", "--mount vs -v",
             "Read-only & subpath", "Volume drivers / NFS", "Backup & restore",
             "H2 hands-on lab", "20 interview Q&A"]
    x, y = 60, 286
    c.setFont("Segoe-Bold", 9)
    for chip in chips:
        w = pdfmetrics.stringWidth(chip, "Segoe-Bold", 9) + 18
        if x + w > PAGE_W - 60:
            x, y = 60, y - 26
        c.setFillColor(HexColor("#22335A"))
        c.roundRect(x, y, w, 19, 9, fill=1, stroke=0)
        c.setFillColor(HexColor("#DCE6FB"))
        c.drawString(x + 9, y + 6, chip)
        x += w + 8
    c.setFillColor(HexColor("#9FB4E0"))
    c.setFont("Segoe", 9)
    c.drawString(60, 40, "For students of TRISHA ACADEMY · Keep these notes for revision and interviews")
    c.restoreState()


# ---------------------------------------------------------------- diagrams
def d_layers():
    d = drawing(200)
    frame(d, 0, 0, 250, 196, "Without a volume", fill=RED_BG, stroke=RED, title_color=RED)
    box(d, 20, 118, 210, 44, ["Writable container layer", "database file is written here"],
        fill=WHITE, stroke=RED)
    box(d, 20, 64, 210, 44, ["Image layers (read-only)", "Alpine + Java + app JAR"],
        fill=GREY_BG, stroke=MUTED)
    text(d, 125, 38, "docker rm  =  writable layer deleted", size=8.5, color=RED, bold=True)
    text(d, 125, 24, "a new container starts with an empty database", size=8, color=RED)

    frame(d, 265, 0, 250, 196, "With a volume", fill=GREEN_BG, stroke=GREEN, title_color=GREEN)
    box(d, 280, 118, 118, 44, ["Container", "writes to /app/data"], fill=WHITE, stroke=NAVY)
    box(d, 280, 64, 118, 44, ["Image layers", "read-only"], fill=GREY_BG, stroke=MUTED)
    box(d, 420, 80, 82, 64, ["Volume", "trishadb.mv.db", "outside"], fill=BLUE_BG, stroke=DOCKER_BLUE)
    arrow(d, 398, 140, 420, 124, color=DOCKER_BLUE, label="mount", label_dy=8)
    text(d, 390, 38, "docker rm  =  container deleted", size=8.5, color=GREEN, bold=True)
    text(d, 390, 24, "the volume and the data are kept", size=8, color=GREEN)
    return d


def d_mount_types():
    d = drawing(250)
    frame(d, 0, 0, 262, 246, "Docker host (your laptop / server)", fill=GREY_BG)
    frame(d, 12, 112, 238, 106, "Docker storage area  /var/lib/docker/volumes", fill=WHITE,
          stroke=DOCKER_BLUE, title_color=DOCKER_BLUE, title_size=8)
    box(d, 24, 160, 214, 34, ["Named volume", "trishadb-data/_data"], fill=BLUE_BG, stroke=DOCKER_BLUE)
    box(d, 24, 120, 214, 34, ["Anonymous volume", "3f6c0c3a9e5b.../_data (random name)"],
        fill=BLUE_BG, stroke=DOCKER_BLUE, dashed=True)
    box(d, 12, 62, 238, 40, ["Bind mount - any folder you choose", "D:\\...\\devops-java-demo\\data"],
        fill=GOLD_BG, stroke=ORANGE)
    box(d, 12, 12, 238, 40, ["tmpfs mount", "host memory (RAM) only - never on disk"],
        fill=PURPLE_BG, stroke=PURPLE)

    frame(d, 400, 0, 115, 246, "Container", fill=GREY_BG)
    targets = [(177, "/app/data"), (137, "/var/cache"), (82, "/app/data"), (32, "/app/tmp")]
    for y, path in targets:
        box(d, 410, y - 15, 95, 30, [path], fill=WHITE, stroke=NAVY, font="Consolas", size=8.5)
    arrow(d, 238, 177, 410, 177, color=DOCKER_BLUE, label="-v trishadb-data:/app/data", label_size=7)
    arrow(d, 238, 137, 410, 137, color=DOCKER_BLUE, label="-v /var/cache", label_size=7)
    arrow(d, 250, 82, 410, 82, color=ORANGE, label='-v "${PWD}\\data:/app/data"', label_size=7)
    arrow(d, 250, 32, 410, 32, color=PURPLE, label="--tmpfs /app/tmp", label_size=7)
    return d


def d_lifecycle():
    d = drawing(150)
    box(d, 0, 78, 140, 52, ["Container A", "POST Priya, Rahul"], fill=RED_BG, stroke=RED, dashed=True)
    text(d, 70, 64, "docker rm -f  (deleted)", size=8, color=RED, bold=True)
    box(d, 187, 60, 140, 70, ["Volume", "trishadb-data", "Priya, Rahul"], fill=BLUE_BG,
        stroke=DOCKER_BLUE)
    box(d, 375, 78, 140, 52, ["Container B (new)", "GET -> Priya, Rahul"], fill=GREEN_BG, stroke=GREEN)
    arrow(d, 140, 104, 187, 104, color=RED, label="writes", dashed=True)
    arrow(d, 375, 104, 327, 104, color=GREEN, label="same -v")
    text(d, 257, 30, "The volume lives outside every container: delete, recreate, rebuild -",
         size=8.5, color=NAVY)
    text(d, 257, 16, "the data stays until you delete the volume itself.", size=8.5, color=NAVY)
    return d


def d_backup():
    d = drawing(130)
    box(d, 0, 50, 140, 56, ["Volume", "trishadb-data", "mounted at /data"], fill=BLUE_BG,
        stroke=DOCKER_BLUE)
    box(d, 187, 44, 140, 68, ["Temporary container", "alpine (--rm)", "tar czf ..."], fill=GREY_BG,
        stroke=NAVY)
    box(d, 375, 50, 140, 56, ["Host folder", "mounted at /backup", "trishadb-backup.tar.gz"],
        fill=GOLD_BG, stroke=ORANGE)
    arrow(d, 140, 78, 187, 78, color=DOCKER_BLUE, label="read")
    arrow(d, 327, 78, 375, 78, color=ORANGE, label="write")
    text(d, 257, 18, "Restore = the same idea in reverse (tar xzf into an empty volume)",
         size=8.5, color=NAVY)
    return d


def d_project():
    d = drawing(210)
    frame(d, 0, 0, 205, 206, "Your computer", fill=GREY_BG)
    box(d, 12, 120, 181, 56, ["D:\\...\\devops-java-demo\\data", "trishadb.mv.db"],
        fill=GOLD_BG, stroke=ORANGE, size=8.5)
    box(d, 12, 22, 181, 60, ["mvn spring-boot:run", "jdbc:h2:file:./data/trishadb", "uses the same file"],
        fill=WHITE, stroke=NAVY, size=8.5)
    arrow(d, 102, 82, 102, 120, color=NAVY, label="  reads / writes", label_dx=34)
    frame(d, 320, 0, 195, 206, "Container devops-java-demo", fill=BLUE_BG, stroke=DOCKER_BLUE,
          title_color=DOCKER_BLUE)
    box(d, 332, 120, 171, 56, ["/app/data", "VOLUME [\"/app/data\"]"], fill=WHITE, stroke=DOCKER_BLUE,
        size=8.5)
    box(d, 332, 22, 171, 60, ["java -jar app.jar", "WORKDIR /app  ->  ./data = /app/data",
                              "WRITE_DELAY=0"], fill=WHITE, stroke=NAVY, size=8.5)
    arrow(d, 417, 82, 417, 120, color=NAVY)
    arrow(d, 332, 148, 193, 148, color=ORANGE, label='-v "${PWD}\\data:/app/data"', label_size=7,
          label_dy=6)
    return d


# ---------------------------------------------------------------- content
def front():
    s = [P("How to use these notes", "h1")]
    s.append(P("These notes teach Docker volumes from zero, following the official Docker documentation "
               "(<b>docs.docker.com/engine/storage/volumes</b>), and finish with a hands-on lab on the "
               "TRISHA ACADEMY <b>devops-java-demo</b> project - a Spring Boot Student API that stores its data "
               "in an <b>H2</b> database file."))
    s += bullets([
        "Read each part, then type every command yourself - do not copy-paste without reading.",
        "Commands are shown for <b>PowerShell</b> (Windows). Linux/macOS differences are noted where needed.",
        "Blue boxes quote the official documentation; green boxes are things to try; red boxes are common "
        "mistakes.",
        "Docker Desktop (Engine 26 or newer) is enough for every example.",
    ])
    s += table(["Part", "Topic"], [
        ["1", "Why containers lose data, and what a volume is"],
        ["2", "Mount types: named, anonymous, bind, tmpfs"],
        ["3", "Volume lifecycle and mounting over existing data"],
        ["4", "Syntax: --mount vs -v, and all options"],
        ["5", "Create, inspect, use and remove volumes"],
        ["6", "Read-only volumes, subdirectories and populating volumes"],
        ["7", "Sharing data: between containers and with volume drivers (NFS)"],
        ["8", "Back up, restore and migrate"],
        ["9", "Bind mounts and the Dockerfile VOLUME instruction"],
        ["10", "Hands-on lab: persist the H2 database of devops-java-demo"],
        ["11", "Best practices, troubleshooting and cheat sheet"],
        ["12", "Top 20 interview questions"],
    ], cols(0.12, 0.88))
    return s


def part1():
    s = banner(1, "Why containers lose data", "Understand the writable layer, and why volumes are the "
               "preferred way to persist data.")
    s.append(P("1.1 The writable container layer", "h1"))
    s.append(P("An image is read-only. When you start a container, Docker adds a thin <b>writable layer</b> on "
               "top of the image. Everything the application writes - log files, uploaded files, database files - "
               "goes into that layer."))
    s += table(["Action", "What happens to the writable layer"], [
        ["`docker stop` / `docker start` / `docker restart`", "Kept - same container"],
        ["`docker rm` (delete the container)", "<b>Deleted</b> together with the container"],
        ["New container from the same image", "Starts with an <b>empty</b> writable layer"],
        ["Rebuild the image and run again", "Starts <b>empty</b> again"],
    ], cols(0.45, 0.55))
    s.append(figure(d_layers(), "Figure 1.1 - Without a volume the data dies with the container; "
                                "with a volume it lives outside"))
    s.append(real("A container is like a hotel room. You can leave your clothes there while you stay "
                  "(stop/start), but when you check out (`docker rm`) housekeeping clears the room. A volume is "
                  "your own locker in the hotel lobby: you can change rooms as often as you like and your things "
                  "are still in the locker."))
    s.append(P("1.2 What is a volume?", "h1"))
    s.append(official("Volumes are persistent data stores for containers, created and managed by Docker. You can "
                      "create a volume explicitly using the `docker volume create` command, or Docker can create a "
                      "volume during container creation. When you create a volume, it's stored within a "
                      "directory on the Docker host. When you mount the volume into a container, this directory is "
                      "what's mounted into the container."))
    s.append(P("1.3 When to use volumes", "h1"))
    s.append(P("The official documentation calls volumes <b>the preferred mechanism for persisting data</b> "
               "generated by and used by Docker containers, because:"))
    s += bullets([
        "Volumes are easier to back up or migrate than bind mounts.",
        "You can manage them with Docker CLI commands or the Docker API.",
        "They work on both Linux and Windows containers.",
        "They can be shared more safely among multiple containers.",
        "New volumes can be pre-populated with content by a container or build.",
        "They give high-performance I/O.",
        "A volume does not increase the size of the container, and it is faster than writing into the "
        "writable layer (which goes through the storage driver's union filesystem).",
    ])
    s.append(mistake("Volumes are <b>not</b> a good choice when you need to open the files directly from the host "
                     "(for example in Windows Explorer or your IDE). For that, use a <b>bind mount</b> (Part 9). "
                     "For temporary data that must never be stored, use a <b>tmpfs</b> mount.",
                     title="When NOT to use a volume"))
    return s


def part2():
    s = banner(2, "Mount types", "Know the four ways to give a container storage, and pick the right one.")
    s.append(P("2.1 The four mount types", "h1"))
    s += table(["Type", "Example", "Where data lives", "Use it for"], [
        ["Named volume", "`-v trishadb-data:/app/data`", "Docker storage area, chosen name",
         "Databases, production data"],
        ["Anonymous volume", "`-v /app/data` or `VOLUME` in Dockerfile", "Docker storage area, random name",
         "Short-lived data"],
        ["Bind mount", "`-v \"${PWD}\\data:/app/data\"`", "Any host folder you choose",
         "Development, demos, config files"],
        ["tmpfs", "`--tmpfs /app/tmp`", "Host memory (RAM) only", "Secrets, scratch files (Linux)"],
    ], cols(0.17, 0.33, 0.25, 0.25))
    s.append(figure(d_mount_types(), "Figure 2.1 - Where each mount type stores its data"))
    s.append(funfact("Docker also has <b>image mounts</b> (mount the content of another image read-only into a "
                     "container) - see the 'Next steps' links on the official page."))
    s.append(P("2.2 Named vs anonymous volumes", "h1"))
    s.append(official([
        "A volume may be named or anonymous. Anonymous volumes are given a random name that's guaranteed to be "
        "unique within a given Docker host.",
        "Just like named volumes, anonymous volumes persist even if you remove the container that uses them, "
        "except if you use the `--rm` flag when creating the container.",
        "If you create multiple containers consecutively that each use anonymous volumes, each container creates "
        "its own volume. Anonymous volumes aren't reused or shared between containers automatically.",
    ]))
    s.append(mistake("Running `docker run` without a named `-v` and expecting the data back in the next container. "
                     "Each new container gets a <b>new</b> anonymous volume, so the database looks empty - the old "
                     "data is still in an orphaned anonymous volume that nobody uses."))
    return s


def part3():
    s = banner(3, "Volume lifecycle", "See how long a volume lives, and what happens when it is mounted over "
               "existing files.")
    s.append(P("3.1 A volume outlives its containers", "h1"))
    s.append(official("A volume's contents exist outside the lifecycle of a given container. When a container is "
                      "destroyed, the writable layer is destroyed with it. Using a volume ensures that the data is "
                      "persisted even if the container using it is removed. A given volume can be mounted into "
                      "multiple containers simultaneously. When no running container is using a volume, the volume "
                      "is still available to Docker and isn't removed automatically."))
    s.append(figure(d_lifecycle(), "Figure 3.1 - Delete container A, start container B with the same volume: "
                                   "the data is still there"))
    s.append(P("3.2 Mounting a volume over existing data", "h1"))
    s += table(["Situation", "What Docker does"], [
        ["<b>Non-empty</b> volume mounted on a folder that has files in the image",
         "The image's files are <b>hidden</b> (obscured) by the volume's files - like plugging a USB drive into "
         "`/mnt`. To see them again you must recreate the container without the mount."],
        ["<b>Empty</b> volume mounted on a folder that has files in the image",
         "The image's files are <b>copied into the volume</b> first (default behaviour)."],
        ["Volume name that does not exist yet", "Docker creates an empty volume for you."],
        ["Empty volume + `volume-nocopy` option", "Nothing is copied - the volume stays empty."],
    ], cols(0.4, 0.6))
    s.append(remember("Pre-populating is a handy way to give another container the data it needs: the first "
                      "container fills the new volume from its image, later containers just mount it."))
    return s


def part4():
    s = banner(4, "Syntax: --mount vs -v", "Read and write both flags, and know every option.")
    s.append(P("4.1 Two flags, same result", "h1"))
    s.append(code("""docker run --mount type=volume,src=<volume-name>,dst=<mount-path>
docker run --volume <volume-name>:<mount-path>      # short form: -v""", "Syntax"))
    s.append(official("In general, `--mount` is preferred. The main difference is that the `--mount` flag is more "
                      "explicit and supports all the available options. You must use `--mount` to specify volume "
                      "driver options or to mount a volume subdirectory."))
    s.append(P("4.2 Options for --mount", "h1"))
    s.append(P("Comma-separated `key=value` pairs; the order does not matter."))
    s += table(["Option", "Meaning"], [
        ["`source`, `src`", "Name of the volume. Omit it for an anonymous volume."],
        ["`destination`, `dst`, `target`", "Path inside the container."],
        ["`readonly`, `ro`", "Mount read-only."],
        ["`volume-nocopy`", "Do not copy the image's files into an empty volume."],
        ["`volume-subpath`", "Mount only a subdirectory of the volume (it must already exist)."],
        ["`volume-opt`", "Driver option as key=value; can be given more than once."],
        ["`volume-driver`", "Use a specific volume driver (default `local`)."],
    ], cols(0.32, 0.68))
    s.append(code("docker run --mount type=volume,src=myvolume,dst=/data,ro,volume-subpath=/foo alpine ls /data",
                  "Example"))
    s.append(P("4.3 Options for -v / --volume", "h1"))
    s.append(P("Three fields separated by colons, in this exact order: `[<volume-name>:]<mount-path>[:opts]`. "
               "Leave out the name for an anonymous volume."))
    s += table(["Option (3rd field)", "Meaning"], [
        ["`readonly`, `ro`", "Mount read-only."],
        ["`volume-nocopy`", "Do not copy the image's files into an empty volume."],
    ], cols(0.32, 0.68))
    s += table(["Goal", "-v", "--mount"], [
        ["Named volume", "`-v trishadb-data:/app/data`", "`--mount source=trishadb-data,target=/app/data`"],
        ["Anonymous volume", "`-v /app/data`", "`--mount type=volume,target=/app/data`"],
        ["Read-only", "`-v trishadb-data:/app/data:ro`", "`--mount source=trishadb-data,target=/app/data,ro`"],
        ["Bind mount", "`-v \"${PWD}\\data:/app/data\"`", "`--mount type=bind,src=\"${PWD}\\data\",dst=/app/data`"],
        ["tmpfs", "`--tmpfs /app/tmp`", "`--mount type=tmpfs,dst=/app/tmp`"],
    ], cols(0.18, 0.34, 0.48))
    s.append(mistake("With `-v`, a typo in a bind-mount path silently creates a new empty folder. `--mount "
                     "type=bind` stops with an error if the source folder does not exist - safer in scripts."))
    return s


def part5():
    s = banner(5, "Create, inspect, use and remove", "Manage volumes with the Docker CLI and verify mounts.")
    s.append(P("5.1 Manage volumes", "h1"))
    s.append(P("Unlike a bind mount, a volume can be created and managed outside the scope of any container."))
    s.append(code("""docker volume create trishadb-data       # create
docker volume ls                         # list
docker volume inspect trishadb-data      # details
docker volume rm trishadb-data           # remove (must not be used by any container)""", "PowerShell"))
    s.append(code("""[
  {
    "Driver": "local",
    "Labels": {},
    "Mountpoint": "/var/lib/docker/volumes/trishadb-data/_data",
    "Name": "trishadb-data",
    "Options": {},
    "Scope": "local"
  }
]""", "Output of docker volume inspect"))
    s.append(funfact("On Docker Desktop (Windows/macOS) the `Mountpoint` is inside Docker Desktop's Linux VM, not "
                     "a normal Windows folder. To look inside a volume, use a throw-away container: "
                     "`docker run --rm -v trishadb-data:/data alpine ls -l /data`"))
    s.append(P("5.2 Start a container with a volume", "h1"))
    s.append(P("If the volume does not exist yet, Docker creates it. Both commands below give the same result."))
    s.append(code("""docker run -d --name devops-java-demo -p 9090:9090 `
  --mount source=trishadb-data,target=/app/data devops-java-demo:1.0.0

docker run -d --name devops-java-demo -p 9090:9090 `
  -v trishadb-data:/app/data devops-java-demo:1.0.0""", "PowerShell (` continues the line)"))
    s.append(P("Verify the mount with `docker inspect devops-java-demo` and look at the `Mounts` section:"))
    s.append(code("""docker inspect --format "{{json .Mounts}}" devops-java-demo

[{"Type":"volume","Name":"trishadb-data",
  "Source":"/var/lib/docker/volumes/trishadb-data/_data",
  "Destination":"/app/data","Driver":"local","Mode":"z","RW":true,"Propagation":""}]""",
                  "Check the mount"))
    s += table(["Field", "Meaning"], [
        ["`Type`", "`volume`, `bind` or `tmpfs`"],
        ["`Name` / `Source`", "Volume name and where Docker stores it"],
        ["`Destination`", "Path inside the container"],
        ["`RW`", "`true` = read-write, `false` = read-only"],
    ], cols(0.28, 0.72))
    s.append(P("5.3 Remove volumes", "h1"))
    s += table(["Command", "What it removes"], [
        ["`docker volume rm <name>`", "One volume (fails if a container, even a stopped one, uses it)"],
        ["`docker run --rm -v /foo -v awesome:/bar busybox top`",
         "With `--rm`, the anonymous `/foo` volume is removed when the container exits; the named `awesome` "
         "volume is kept"],
        ["`docker rm -v <container>`", "The container and its <b>anonymous</b> volumes (never named ones)"],
        ["`docker volume prune`", "All unused <b>anonymous</b> volumes (Docker Engine 23 and newer)"],
        ["`docker volume prune -a`", "All unused volumes, <b>named ones too</b>"],
    ], cols(0.42, 0.58))
    s.append(mistake("`docker volume prune -a` and `docker volume rm` delete data for "
                     "good - there is no recycle bin. Take a backup first (Part 8)."))
    s.append(funfact("If another container mounted the volumes with `--volumes-from`, the volume definitions are "
                     "copied, and the anonymous volume stays after the first container is removed."))
    return s


def part6():
    s = banner(6, "Read-only, subdirectories and pre-populating", "Control how a container can use a volume.")
    s.append(P("6.1 Populate a volume using a container", "h1"))
    s.append(P("When a container creates a <b>new</b> volume on a folder that has files in the image, Docker copies "
               "those files into the volume. Here the `nginx-vol` volume is filled with Nginx's default web page:"))
    s.append(code("""docker run -d --name=nginxtest -v nginx-vol:/usr/share/nginx/html nginx:latest
docker run --rm -v nginx-vol:/data alpine ls /data      # 50x.html  index.html
docker rm -f nginxtest
docker volume rm nginx-vol""", "PowerShell"))
    s.append(P("6.2 Read-only volumes", "h1"))
    s.append(P("Several containers can mount the same volume - some read-write, others read-only. Add `ro` "
               "(or `readonly` with `--mount`):"))
    s.append(code("""docker run -d --name=nginxtest -v nginx-vol:/usr/share/nginx/html:ro nginx:latest
docker run -d --name=nginxtest2 `
  --mount source=nginx-vol,destination=/usr/share/nginx/html,readonly nginx:latest""", "PowerShell"))
    s.append(P("`docker inspect` then shows `\"RW\": false`. Any write inside the mount fails with "
               "<i>Read-only file system</i>."))
    s.append(mistake("Never mount a <b>database</b> folder read-only - H2, MySQL and PostgreSQL must write to it."))
    s.append(P("6.3 Mount a volume subdirectory", "h1"))
    s.append(P("With `volume-subpath` (only with `--mount`) each container sees just one folder of a shared volume. "
               "The subdirectory must exist before you mount it."))
    s.append(code("""docker volume create logs
docker run --rm --mount src=logs,dst=/logs alpine mkdir -p /logs/app1 /logs/app2
docker run -d --name=app1 --mount src=logs,dst=/var/log/app1,volume-subpath=app1 app1:latest
docker run -d --name=app2 --mount src=logs,dst=/var/log/app2,volume-subpath=app2 app2:latest""",
                  "Separate log folders in one volume"))
    s.append(P("Each container writes to its own subfolder of the `logs` volume and cannot see the other one's logs."))
    return s


def part7():
    s = banner(7, "Sharing data", "Share volumes between containers and between machines.")
    s.append(P("7.1 Between containers on one host", "h1"))
    s.append(code("""# The app writes to the volume
docker run -d --name devops-java-demo -p 9090:9090 -v trishadb-data:/app/data devops-java-demo:1.0.0
# Another container reads the same volume
docker run --rm -v trishadb-data:/data alpine ls -l /data
# Or reuse every volume of an existing container
docker run --rm --volumes-from devops-java-demo alpine ls -l /app/data""", "PowerShell"))
    s.append(mistake("H2 in file mode allows only <b>one</b> application to open the database at a time. Sharing the "
                     "volume for reading, inspection or backup is fine - two app containers on one H2 file is not."))
    s.append(P("7.2 Between machines: volume drivers", "h1"))
    s.append(P("For fault-tolerant apps with replicas on several servers, either store files in cloud object "
               "storage (for example Amazon S3) from the application, or create volumes with a driver that writes "
               "to external storage (NFS, SFTP, S3 ...). The application code does not change."))
    s.append(code("""docker volume create --driver local `
  --opt type=nfs `
  --opt o=addr=10.0.0.10,rw,nfsvers=4 `
  --opt device=:/var/docker-nfs `
  nfsvolume
docker run -d -v nfsvolume:/app nginx:latest""", "NFS volume with the built-in local driver (Linux host)"))
    s.append(code("""docker plugin install --grant-all-permissions rclone/docker-volume-rclone --aliases rclone
docker volume create -d rclone --name rclonevolume `
  -o type=sftp -o path=remote -o sftp-host=1.2.3.4 -o sftp-user=user""",
                  "Third-party driver plugin (SFTP via rclone)"))
    s += table(["Driver / option", "Stores data on"], [
        ["`local` (default)", "The Docker host's disk"],
        ["`local` + `type=nfs`", "An NFS server (NFSv3 / NFSv4)"],
        ["`local` + `type=cifs`", "A Windows / Samba share"],
        ["`rclone` plugin", "SFTP, S3 and many cloud stores"],
        ["Cloud CSI / plugins", "Amazon EBS / EFS, Azure Disk / Files, etc."],
    ], cols(0.35, 0.65))
    s.append(funfact("If a driver option itself contains commas (like NFS `o=` options) inside `--mount`, put that "
                     "option in double quotes and the whole `--mount` value in single quotes."))
    return s


def part8():
    s = banner(8, "Back up, restore and migrate", "Protect volume data and move it between hosts.")
    s.append(P("8.1 The idea", "h1"))
    s.append(P("Start a short-lived helper container that mounts <b>both</b> the volume and a host folder, and use "
               "`tar` to copy between them. Stop the application first so the files are not changing."))
    s.append(figure(d_backup(), "Figure 8.1 - A temporary container archives the volume into a host folder"))
    s.append(P("8.2 Back up and restore a named volume", "h1"))
    s.append(code("""docker stop devops-java-demo

# Backup  ->  .\\trishadb-backup.tar.gz
docker run --rm -v trishadb-data:/data -v "${PWD}:/backup" alpine `
  tar czf /backup/trishadb-backup.tar.gz -C /data .

# Restore into a new volume and start a second copy of the app on port 9091
docker volume create trishadb-data-restored
docker run --rm -v trishadb-data-restored:/data -v "${PWD}:/backup" alpine `
  tar xzf /backup/trishadb-backup.tar.gz -C /data
docker run -d --name devops-java-demo-restored -p 9091:9090 `
  -v trishadb-data-restored:/app/data devops-java-demo:1.0.0""", "PowerShell"))
    s.append(P("8.3 The official --volumes-from method", "h1"))
    s.append(code("""docker run -v /dbdata --name dbstore ubuntu /bin/bash
docker run --rm --volumes-from dbstore -v "${PWD}:/backup" ubuntu tar cvf /backup/backup.tar /dbdata

docker run -v /dbdata --name dbstore2 ubuntu /bin/bash
docker run --rm --volumes-from dbstore2 -v "${PWD}:/backup" ubuntu `
  bash -c "cd /dbdata && tar xvf /backup/backup.tar --strip 1\"""", "Back up and restore via another container"))
    s.append(P("8.4 Migrate to another server", "h1"))
    s += bullets([
        "Back up the volume to a `.tar.gz` file (8.2).",
        "Copy the file to the new server (`scp`, S3, USB ...).",
        "Create a volume there, restore into it, and start the container with the same `-v`.",
    ])
    s.append(tryit("Back up your `trishadb-data` volume, delete the volume, restore it from the archive and check "
                   "that `GET /students` still returns your students."))
    return s


def part9():
    s = banner(9, "Bind mounts and the VOLUME instruction", "Compare bind mounts with volumes, and see what "
               "`VOLUME` in a Dockerfile really does.")
    s.append(P("9.1 Bind mounts", "h1"))
    s.append(P("A bind mount maps a folder that <b>you</b> choose on the host into the container. The files are "
               "normal host files - you can open, edit, copy and back them up directly."))
    s.append(code("""# PowerShell - run from the project folder
docker run -d --name devops-java-demo -p 9090:9090 -v "${PWD}\\data:/app/data" devops-java-demo:1.0.0
# Git Bash / Linux / macOS
docker run -d --name devops-java-demo -p 9090:9090 -v "$(pwd)/data:/app/data" devops-java-demo:1.0.0""",
                  "Bind mount"))
    s += table(["", "Volume", "Bind mount"], [
        ["Managed by", "Docker", "You (host folder)"],
        ["See files in Explorer / IDE", "No (inside Docker's storage)", "Yes"],
        ["Depends on host folder layout and OS", "No", "Yes"],
        ["Copies image files into an empty mount", "Yes (unless volume-nocopy)", "No - hides the image's files"],
        ["Speed on Docker Desktop (Windows/macOS)", "Fast", "Slower (files cross into the VM)"],
        ["Backup / migrate", "Docker CLI (Part 8)", "Copy the folder"],
        ["Best for", "Production, servers", "Development, demos, config"],
    ], cols(0.38, 0.31, 0.31))
    s.append(P("9.2 The VOLUME instruction in a Dockerfile", "h1"))
    s.append(code("""WORKDIR /app
VOLUME ["/app/data"]""", "Dockerfile of devops-java-demo"))
    s += bullets([
        "Marks `/app/data` as a folder whose data belongs <b>outside</b> the container.",
        "Run <b>without</b> `-v`: Docker creates an anonymous volume for `/app/data` automatically.",
        "Run <b>with</b> `-v`: your named volume or bind mount is used instead.",
        "A Dockerfile can <b>never</b> choose a host folder or a volume name - only `docker run` can.",
    ])
    s.append(mistake("Relying on `VOLUME` alone. A new container gets a new anonymous volume, so the data seems to "
                     "disappear. Always run with a named volume or a bind mount."))
    return s


def part10():
    s = banner(10, "Hands-on lab: persist the H2 database",
               "Make the devops-java-demo Student API keep its data through restarts, deletes, hard kills and "
               "rebuilds.")
    s.append(P("10.1 How the project is set up", "h1"))
    s += table(["File", "Setting", "Why"], [
        ["`application.properties`", "`spring.datasource.url=jdbc:h2:file:./data/trishadb;WRITE_DELAY=0`",
         "H2 writes to the file `data/trishadb.mv.db` instead of memory"],
        ["`application.properties`", "`spring.jpa.hibernate.ddl-auto=update`",
         "Keeps tables and rows on restart (`create` would wipe them)"],
        ["`application.properties`", "`spring.h2.console.settings.web-allow-others=true`",
         "Lets the H2 console open from your browser when the app runs in Docker"],
        ["`Dockerfile`", "`WORKDIR /app` + `VOLUME [\"/app/data\"]`", "`./data` inside the container = `/app/data`"],
        ["`.dockerignore`", "`data/`", "Your local database is never copied into the image"],
        ["`pom.xml` (Surefire)", "`jdbc:h2:mem:testdb`", "JUnit tests use a throw-away in-memory database"],
    ], cols(0.27, 0.43, 0.30))
    s.append(figure(d_project(), "Figure 10.1 - The project's data folder is bind-mounted to /app/data; "
                                 "mvn spring-boot:run uses the same file"))
    s.append(callout("Why WRITE_DELAY=0?",
                     "By default H2 keeps the newest changes in memory for up to about a second before writing them. "
                     "In our tests, a student saved just before `docker rm -f` was lost. With `WRITE_DELAY=0` every "
                     "change is written at once, and the same test kept all data.", ORANGE_BG, ORANGE))
    s.append(P("10.2 Build and run", "h1"))
    s.append(code("""cd D:\\TRISHA-ACADEMY\\DevOPs\\devops-java-demo
docker build -t devops-java-demo:1.0.0 .
docker run -d --name devops-java-demo -p 9090:9090 -v "${PWD}\\data:/app/data" devops-java-demo:1.0.0
docker logs -f devops-java-demo        # wait for "Started SpringLabApplication", then Ctrl + C""",
                  "PowerShell"))
    s.append(code("""Invoke-RestMethod -Method Post -Uri http://localhost:9090/students `
  -ContentType "application/json" -Body '{"name":"Priya","course":"DevOps"}'
Invoke-RestMethod http://localhost:9090/students""", "Helper commands: add and list students"))
    s.append(P("10.3 Prove that the data is kept", "h1"))
    s += table(["#", "Test", "Commands", "Expected"], [
        ["1", "File in project", "Add 2 students, then `Get-ChildItem data`", "`trishadb.mv.db` exists"],
        ["2", "Restart", "`docker restart devops-java-demo`", "Students still listed"],
        ["3", "Delete container", "`docker rm -f devops-java-demo`, then the same `docker run ... -v ...`",
         "Students still listed"],
        ["4", "Hard kill", "Add a student, `docker kill`, `docker start`", "New student kept (ids may jump)"],
        ["5", "Rebuild image", "`docker rm -f`, `docker build`, `docker run ... -v ...`", "Students still listed"],
        ["6", "Local run", "`docker stop`, then `mvn spring-boot:run`", "Same students"],
        ["7", "No volume", "Run without `-v`, add, `docker rm -f -v`, run again", "<b>Empty</b> list"],
        ["8", "Tests isolated", "`mvn test`, compare file time before/after", "File unchanged"],
    ], cols(0.05, 0.17, 0.48, 0.30))
    s.append(funfact("After a hard kill the next id may jump (1, 2, 33 ...). H2 reserves ids in blocks of 32 and "
                     "skips the unused ones after a crash. No data is lost."))
    s.append(P("10.4 Switch to a named volume", "h1"))
    s.append(code("""docker rm -f devops-java-demo
docker run -d --name devops-java-demo -p 9090:9090 -v trishadb-data:/app/data devops-java-demo:1.0.0""",
                  "PowerShell"))
    s.append(P("Now Docker stores the database in the `trishadb-data` volume instead of the project folder - "
               "this is how you would run it on a server."))
    s.append(P("10.5 Look at the data", "h1"))
    s += bullets([
        "H2 console: http://localhost:9090/h2-console - JDBC URL `jdbc:h2:file:./data/trishadb`, user `sa`, "
        "password `sa@123`, then `SELECT * FROM students;`",
        "Bind mount: open `devops-java-demo\\data` in Explorer.",
        "Named volume: `docker run --rm -v trishadb-data:/data alpine ls -l /data`",
        "Reset: stop the app and delete the `data` folder (or `docker volume rm trishadb-data`).",
    ])
    s.append(tryit("Full step-by-step test scripts with expected output are in `DB-PERSISTENCE-TESTING.md` in the "
                   "project folder."))
    return s


def part11():
    s = banner(11, "Best practices, troubleshooting and cheat sheet", "Avoid the classic mistakes.")
    s.append(P("11.1 Best practices", "h1"))
    s += bullets([
        "Never keep important data in the container's writable layer.",
        "Use <b>named volumes</b> on servers and in production; <b>bind mounts</b> for development and demos.",
        "Prefer `--mount` in scripts - it is explicit and fails on wrong bind paths.",
        "Give volumes clear names; avoid relying on anonymous volumes.",
        "Keep data folders out of the image with `.dockerignore`.",
        "One writer per database file; never run two app containers on the same H2 file.",
        "Stop the app before a backup, and test your restore regularly.",
        "For production databases use the official image with a named volume, e.g. "
        "`-v pgdata:/var/lib/postgresql/data`, or a managed database such as Amazon RDS.",
    ])
    s.append(P("11.2 Troubleshooting", "h1"))
    s += table(["Problem", "Cause and fix"], [
        ["Data gone after `docker rm` + `docker run`", "`-v` missing or a different name/folder - use exactly the "
                                                      "same `-v` every time"],
        ["New container empty although `data\\trishadb.mv.db` exists", "Command run from another folder, so "
                                                                       "`${PWD}` points elsewhere - `cd` first"],
        ["`Database may be already in use`", "Two apps use the same H2 file - stop one"],
        ["`volume is in use`", "A (stopped) container uses it - `docker ps -a --filter volume=<name>`"],
        ["Many unknown volumes", "Anonymous volumes from runs without `-v` - `docker volume prune`"],
        ["H2 console: remote connections not allowed", "Set `spring.h2.console.settings.web-allow-others=true`"],
        ["`Read-only file system`", "Volume mounted with `ro` / `readonly`"],
        ["Bind mount fails on Windows", "Use a full path (`${PWD}\\data`) and check Docker Desktop file sharing"],
    ], cols(0.4, 0.6))
    s.append(P("11.3 Cheat sheet", "h1"))
    s += table(["Goal", "Command"], [
        ["Create / list / inspect", "`docker volume create v` · `docker volume ls` · `docker volume inspect v`"],
        ["Run with a named volume", "`docker run -v v:/path image` or `--mount source=v,target=/path`"],
        ["Run with a bind mount", "`docker run -v \"${PWD}\\data:/path\" image`"],
        ["Read-only", "`-v v:/path:ro` or `--mount source=v,target=/path,readonly`"],
        ["Which containers use v", "`docker ps -a --filter volume=v`"],
        ["Mounts of a container", "`docker inspect --format \"{{json .Mounts}}\" c`"],
        ["Look inside", "`docker run --rm -v v:/data alpine ls -l /data`"],
        ["Remove", "`docker volume rm v` · `docker rm -v c` · `docker volume prune [-a]`"],
        ["Disk usage", "`docker system df -v`"],
        ["Backup", "`docker run --rm -v v:/data -v \"${PWD}:/backup\" alpine tar czf /backup/v.tgz -C /data .`"],
    ], cols(0.28, 0.72))
    return s


QA = [
    ("Why is data lost when a container is deleted?",
     "It is written into the container's writable layer, which is destroyed with the container. A new container "
     "from the same image starts with an empty writable layer."),
    ("What is a Docker volume?",
     "Persistent storage created and managed by Docker, stored in a directory on the host and mounted into "
     "containers. It lives independently of any container."),
    ("Why are volumes preferred over writing to the container?",
     "They persist after the container is removed, do not grow the container size, are faster (no union filesystem "
     "/ storage driver), and are easy to back up, migrate and share."),
    ("Named vs anonymous volume?",
     "A named volume has a name you choose and can be reused by any container. An anonymous volume gets a random "
     "name; each new container creates its own, so it is not reused automatically."),
    ("Volume vs bind mount?",
     "A volume is managed by Docker in its storage area and is independent of the host layout. A bind mount maps a "
     "host folder you choose - good when you need the files on the host, but it depends on the host's paths and OS."),
    ("When would you use tmpfs?",
     "For non-persistent or sensitive data that must never be written to disk, and to avoid writing into the "
     "writable layer. It lives in RAM and disappears when the container stops."),
    ("--mount or -v - which is preferred and why?",
     "--mount: it is explicit key=value syntax and supports all options. It is required for volume driver options "
     "and volume-subpath."),
    ("What happens when you mount an empty volume over a folder that has files?",
     "Docker copies the existing files into the volume first, unless the volume-nocopy option is used."),
    ("And a non-empty volume?",
     "The existing files in the container are obscured (hidden) by the volume's content, like mounting a USB drive "
     "over /mnt."),
    ("What does the VOLUME instruction in a Dockerfile do?",
     "It marks a path as external storage. If no -v is given, Docker creates an anonymous volume for it. It cannot "
     "specify a host path or a volume name."),
    ("Does docker rm -v delete named volumes?",
     "No. It removes only the anonymous volumes associated with the container."),
    ("What does --rm do to volumes?",
     "When the container exits it is removed together with its anonymous volumes; named volumes are kept."),
    ("docker volume prune vs docker volume prune -a?",
     "On Docker Engine 23+, prune removes unused anonymous volumes; -a removes all unused volumes including named "
     "ones. Both are irreversible."),
    ("How do you back up a volume?",
     "Run a temporary container that mounts the volume and a host folder (or uses --volumes-from) and archive the "
     "volume with tar into the host folder. Stop the writing application first."),
    ("How do you check which volume a container uses?",
     "docker inspect <container> and read the Mounts section (Type, Name, Source, Destination, RW)."),
    ("How do you share data between containers?",
     "Mount the same named volume in each, or use --volumes-from. Several containers can mount a volume at the same "
     "time, some read-write and some read-only."),
    ("What is volume-subpath used for?",
     "Mounting only one subdirectory of a volume into a container, e.g. separate log folders per app in one "
     "shared logs volume. The subdirectory must already exist."),
    ("How can replicas on different servers share data?",
     "Store files in object storage from the app (e.g. S3), or use a volume driver backed by shared storage such as "
     "NFS, CIFS, SFTP (rclone) or cloud file systems."),
    ("How do you keep an H2 database in Docker?",
     "Use H2 file mode (jdbc:h2:file:...), ddl-auto=update, and mount a named volume or bind mount on the data "
     "folder. Add WRITE_DELAY=0 so a hard kill cannot lose the last writes."),
    ("Where is a volume stored on Docker Desktop?",
     "Inside Docker Desktop's Linux VM at /var/lib/docker/volumes/<name>/_data, not in a Windows folder. To see "
     "the files, run a throw-away container: docker run --rm -v <name>:/data alpine ls -l /data."),
]


def part12():
    s = banner(12, "Top 20 interview questions", "Answer aloud before reading the model answer.")
    s.append(P("Interviewers look for a clear definition, one real example and one trade-off."))
    for i, (q, a) in enumerate(QA, 1):
        s.append(KeepTogether([P(f"Q{i}. {q}", "q"), P(a, "a")]))
    s.append(gap(10))
    s.append(P("Reference", "h2"))
    s += bullets([
        "Docker docs - Volumes: https://docs.docker.com/engine/storage/volumes/",
        "Docker docs - Bind mounts: https://docs.docker.com/engine/storage/bind-mounts/",
        "Docker docs - tmpfs mounts: https://docs.docker.com/engine/storage/tmpfs/",
        "Project notes: README.md, DOCKER-VOLUMES.md, DB-PERSISTENCE-TESTING.md",
    ])
    return s


def build():
    os.makedirs(OUT_DIR, exist_ok=True)
    doc = new_doc(OUT_FILE, "Docker Volumes and Data Persistence", "Docker training notes", draw_docker_cover)
    story = start_story() + front()
    for part in (part1, part2, part3, part4, part5, part6, part7, part8, part9, part10, part11, part12):
        story += part()
    doc.multiBuild(story)
    return OUT_FILE


if __name__ == "__main__":
    print(build())
