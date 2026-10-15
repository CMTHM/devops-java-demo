"""Build the TRISHA ACADEMY "Docker Networking" student guide.

Reference: https://docs.docker.com/engine/network/
Run:  python generate_docker_networking_pdf.py
Output: docs/docker/Docker-Networking-Guide.pdf
"""
import os

import k8s_pdf_lib as L
from k8s_pdf_lib import *
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics

L.COURSE = "Docker Networking"
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docker")
OUT_FILE = os.path.join(OUT_DIR, "Docker-Networking-Guide.pdf")
DOCKER_BLUE = HexColor("#1D63ED")


# ---------------------------------------------------------------- layout helpers
def banner(num, title, outcome):
    kicker = Paragraph(f'<font color="#F2A900">DOCKER NETWORKING · PART {num:02d}</font>',
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


def draw_network_cover(c, doc):
    c.saveState()
    c.setFillColor(NAVY_DEEP)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    c.setFillColor(DOCKER_BLUE)
    c.rect(0, PAGE_H - 12, PAGE_W, 12, fill=1, stroke=0)
    c.setFillColor(GOLD)
    c.rect(0, 0, PAGE_W, 6, fill=1, stroke=0)
    # containers linked to a central bridge
    hub_x, hub_y = PAGE_W - 170, PAGE_H - 270
    nodes = [(-110, 70), (0, 105), (110, 70), (-110, -70), (110, -70)]
    c.setStrokeColor(HexColor("#2E4572"))
    c.setLineWidth(2.5)
    for dx, dy in nodes:
        c.line(hub_x, hub_y, hub_x + dx, hub_y + dy)
    for dx, dy in nodes:
        x, y = hub_x + dx - 34, hub_y + dy - 18
        c.setFillColor(HexColor("#22335A"))
        c.roundRect(x, y, 68, 36, 4, fill=1, stroke=0)
        c.setStrokeColor(HexColor("#2E4572"))
        c.setLineWidth(2)
        for k in range(1, 4):
            c.line(x + k * 17, y + 6, x + k * 17, y + 30)
    c.setFillColor(DOCKER_BLUE)
    c.circle(hub_x, hub_y, 34, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Segoe-Bold", 9)
    c.drawCentredString(hub_x, hub_y - 3, "BRIDGE")

    c.setFillColor(GOLD)
    c.setFont("Segoe-Bold", 13)
    c.drawString(60, PAGE_H - 90, ACADEMY)
    c.setFillColor(HexColor("#9FB4E0"))
    c.setFont("Segoe", 10)
    c.drawString(60, PAGE_H - 106, "DevOps Career Track · Student Notes")
    c.setFillColor(WHITE)
    c.setFont("Segoe-Bold", 34)
    c.drawString(60, 440, "Docker Networking")
    c.drawString(60, 398, "& Container Communication")
    c.setFillColor(HexColor("#C9D6F5"))
    c.setFont("Segoe", 14)
    c.drawString(60, 360, "Connect containers to each other, to the host and to the world")
    c.setFont("Segoe-Italic", 11)
    c.setFillColor(HexColor("#9FB4E0"))
    c.drawString(60, 336, "Based on docs.docker.com/engine/network · Lab: Spring Boot Student API")
    chips = ["Bridge networks", "User-defined bridge", "Published ports", "Embedded DNS", "host & none",
             "container: mode", "macvlan / ipvlan", "Subnets & static IPs", "host.docker.internal",
             "Hands-on lab", "20 interview Q&A"]
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
def d_overview():
    d = drawing(230)
    text(d, 40, 200, "Internet", size=9, color=NAVY, bold=True)
    box(d, 0, 150, 80, 40, ["Browser", "your laptop"], fill=WHITE, stroke=NAVY, size=8.5)
    frame(d, 120, 0, 395, 226, "Docker host", fill=GREY_BG)
    box(d, 135, 150, 110, 44, ["Host eth0", "e.g. 192.168.1.20"], fill=GOLD_BG, stroke=ORANGE, size=8.5)
    arrow(d, 80, 170, 135, 170, color=ORANGE, label="-p 9090:9090", label_size=7, label_dy=-12)
    box(d, 135, 70, 365, 40, ["docker0  (default bridge)", "172.17.0.1/16 - the containers' gateway, NAT to the "
                                                         "host network"], fill=BLUE_BG, stroke=DOCKER_BLUE, size=8.5)
    arrow(d, 190, 150, 190, 110, color=ORANGE)
    arrow(d, 210, 110, 210, 150, color=MUTED, label="outbound (NAT)", label_dx=38, label_size=7)
    for i, (name, ip) in enumerate([("app", "172.17.0.2"), ("client", "172.17.0.3")]):
        x = 300 + i * 105
        box(d, x, 150, 95, 44, [name, f"eth0 {ip}"], fill=WHITE, stroke=NAVY, size=8.5)
        arrow(d, x + 47, 150, x + 47, 110, color=DOCKER_BLUE, head=False, label="veth", label_dx=14,
              label_size=7)
    box(d, 135, 14, 365, 40, ["Each container has its own network namespace:",
                              "its own interfaces, IP address, routing table and DNS settings"],
        fill=WHITE, stroke=LINE, size=8.5)
    return d


def d_bridges():
    d = drawing(200)
    frame(d, 0, 0, 250, 196, "Default bridge (bridge)", fill=RED_BG, stroke=RED, title_color=RED)
    box(d, 15, 110, 100, 46, ["nettest-web1", "172.17.0.2"], fill=WHITE, stroke=NAVY, size=8.5)
    box(d, 135, 110, 100, 46, ["alpine", "client"], fill=WHITE, stroke=NAVY, size=8.5)
    arrow(d, 135, 133, 115, 133, color=NAVY)
    text(d, 125, 80, "wget http://nettest-web1  ->  bad address", size=8, color=RED, bold=True)
    text(d, 125, 64, "wget http://172.17.0.2  ->  OK", size=8, color=GREEN, bold=True)
    text(d, 125, 30, "No name resolution between containers", size=8, color=RED)
    text(d, 125, 16, "(only IP addresses or legacy --link)", size=8, color=RED)

    frame(d, 265, 0, 250, 196, "User-defined bridge (trisha-net)", fill=GREEN_BG, stroke=GREEN, title_color=GREEN)
    box(d, 280, 110, 100, 46, ["devops-java-demo", "172.18.0.2"], fill=WHITE, stroke=NAVY, size=8.5)
    box(d, 400, 110, 100, 46, ["alpine", "client"], fill=WHITE, stroke=NAVY, size=8.5)
    arrow(d, 400, 133, 380, 133, color=NAVY)
    box(d, 330, 60, 120, 32, ["Embedded DNS", "127.0.0.11"], fill=BLUE_BG, stroke=DOCKER_BLUE, size=8)
    text(d, 390, 30, "wget http://devops-java-demo:9090  ->  OK", size=8, color=GREEN, bold=True)
    text(d, 390, 16, "Containers find each other by name", size=8, color=GREEN)
    return d


def d_ports():
    d = drawing(150)
    box(d, 0, 80, 120, 50, ["Browser / PowerShell", "localhost:9090"], fill=WHITE, stroke=NAVY, size=8.5)
    frame(d, 160, 0, 355, 146, "Docker host", fill=GREY_BG)
    box(d, 175, 80, 110, 50, ["Host port 9090", "0.0.0.0 or 127.0.0.1"], fill=GOLD_BG, stroke=ORANGE, size=8.5)
    box(d, 375, 80, 125, 50, ["Container port 9090", "app listens here"], fill=BLUE_BG, stroke=DOCKER_BLUE,
        size=8.5)
    arrow(d, 120, 105, 175, 105, color=ORANGE)
    arrow(d, 285, 105, 375, 105, color=ORANGE, label="-p 9090:9090", label_size=7.5)
    text(d, 337, 46, "-p  HOST_PORT : CONTAINER_PORT   (left = outside, right = inside)", size=8.5,
         color=NAVY, bold=True)
    text(d, 337, 26, "Without -p the app is reachable only from containers on the same network", size=8,
         color=MUTED)
    return d


def d_dns():
    d = drawing(150)
    box(d, 0, 50, 130, 60, ["Container", "asks: devops-java-demo?", "asks: example.com?"], fill=WHITE,
        stroke=NAVY, size=8.5)
    box(d, 180, 50, 125, 60, ["Embedded DNS", "127.0.0.11", "(inside every container)"], fill=BLUE_BG,
        stroke=DOCKER_BLUE, size=8.5)
    box(d, 400, 90, 115, 44, ["Container name / alias", "-> 172.18.0.2"], fill=GREEN_BG, stroke=GREEN, size=8)
    box(d, 400, 20, 115, 44, ["External names", "-> host's DNS servers"], fill=GOLD_BG, stroke=ORANGE, size=8)
    arrow(d, 130, 80, 180, 80, color=NAVY, label="query")
    arrow(d, 305, 92, 400, 112, color=GREEN, label="on this network", label_size=7, label_dx=-8, label_dy=10)
    arrow(d, 305, 68, 400, 42, color=ORANGE, label="forwarded", label_size=7, label_dx=-8, label_dy=-16)
    return d


def d_modes():
    d = drawing(170)
    frame(d, 0, 0, 165, 166, "--network host", fill=GOLD_BG, stroke=ORANGE, title_color=ORANGE)
    box(d, 12, 82, 141, 50, ["Container", "uses the host's interfaces"], fill=WHITE, stroke=ORANGE, size=8)
    text(d, 82, 52, "No own IP, -p is ignored", size=7.5, color=ORANGE, bold=True)
    text(d, 82, 38, "app on :9090 = host :9090", size=7.5, color=INK)
    text(d, 82, 18, "Best performance, no isolation", size=7.5, color=MUTED)

    frame(d, 175, 0, 165, 166, "--network none", fill=GREY_BG, stroke=MUTED, title_color=NAVY)
    box(d, 187, 82, 141, 50, ["Container", "only lo 127.0.0.1"], fill=WHITE, stroke=MUTED, size=8)
    text(d, 257, 52, "No eth0, no gateway", size=7.5, color=NAVY, bold=True)
    text(d, 257, 38, "fully cut off", size=7.5, color=INK)
    text(d, 257, 18, "Batch jobs, untrusted code", size=7.5, color=MUTED)

    frame(d, 350, 0, 165, 166, "--network container:web", fill=PURPLE_BG, stroke=PURPLE, title_color=PURPLE)
    box(d, 362, 108, 66, 30, ["web"], fill=WHITE, stroke=PURPLE, size=8)
    box(d, 437, 108, 66, 30, ["sidecar"], fill=WHITE, stroke=PURPLE, size=8)
    box(d, 362, 70, 141, 26, ["one shared network stack"], fill=WHITE, stroke=PURPLE, size=7.5,
        bold_first=False)
    text(d, 432, 52, "Same IP, same ports", size=7.5, color=PURPLE, bold=True)
    text(d, 432, 38, "talk via localhost", size=7.5, color=INK)
    text(d, 432, 18, "Debug tools, sidecars", size=7.5, color=MUTED)
    return d


def d_lab():
    d = drawing(230)
    frame(d, 0, 0, 515, 226, "Your laptop (Docker Desktop)", fill=GREY_BG)
    box(d, 14, 150, 110, 44, ["PowerShell / browser", "localhost:9090"], fill=WHITE, stroke=NAVY, size=8.5)
    frame(d, 182, 110, 321, 96, "Network trisha-net (user-defined bridge)", fill=GREEN_BG, stroke=GREEN,
          title_color=GREEN, title_size=8)
    box(d, 196, 122, 135, 50, ["devops-java-demo", "port 9090  ·  172.18.0.2"], fill=WHITE, stroke=NAVY, size=8.5)
    box(d, 375, 122, 115, 50, ["alpine (client)", "wget devops-java-demo:9090"], fill=WHITE, stroke=GREEN,
        size=8)
    arrow(d, 375, 147, 331, 147, color=GREEN, label="by name", label_size=7, label_dy=5)
    arrow(d, 124, 165, 196, 152, color=ORANGE, label="-p 9090:9090", label_size=7, label_dx=-4, label_dy=-17)
    frame(d, 182, 12, 321, 84, "Default bridge", fill=RED_BG, stroke=RED, title_color=RED, title_size=8)
    box(d, 196, 22, 150, 46, ["alpine (other client)", "host.docker.internal:9090"], fill=WHITE, stroke=RED,
        size=8)
    text(d, 428, 52, "devops-java-demo:9090", size=7.5, color=RED, bold=True)
    text(d, 428, 40, "-> bad address (different network)", size=7.5, color=RED)
    arrow(d, 263, 68, 263, 122, color=ORANGE, dashed=True, label="via the host port", label_dx=46,
          label_dy=8, label_size=7)
    return d


# ---------------------------------------------------------------- content
def front():
    s = [P("How to use these notes", "h1")]
    s.append(P("These notes teach Docker networking from zero, following the official Docker documentation "
               "(<b>docs.docker.com/engine/network</b>), and finish with a hands-on lab on the TRISHA ACADEMY "
               "<b>devops-java-demo</b> project - a Spring Boot Student API that listens on port <b>9090</b>."))
    s += bullets([
        "Read each part, then type every command yourself - do not copy-paste without reading.",
        "Commands are shown for <b>PowerShell</b> (Windows). Linux/macOS differences are noted where needed.",
        "Blue boxes quote the official documentation; green boxes are things to try; red boxes are common "
        "mistakes.",
        "Every command in Parts 3 to 9 was run on Docker Desktop (Engine 29) while writing these notes.",
        "You need two small images: `docker pull alpine` and `docker pull nginx:alpine`.",
    ])
    s += table(["Part", "Topic"], [
        ["1", "How container networking works"],
        ["2", "Network drivers"],
        ["3", "Default bridge vs user-defined bridge"],
        ["4", "Publishing ports"],
        ["5", "DNS and service discovery"],
        ["6", "Managing networks: create, connect, inspect, remove"],
        ["7", "host, none and container: networking"],
        ["8", "macvlan and ipvlan"],
        ["9", "Hands-on lab: networking the devops-java-demo app"],
        ["10", "Best practices, troubleshooting and cheat sheet"],
        ["11", "Top 20 interview questions"],
    ], cols(0.12, 0.88))
    return s


def part1():
    s = banner(1, "How container networking works", "Understand what a container sees, and how it reaches "
               "other containers, the host and the internet.")
    s.append(P("1.1 What is container networking?", "h1"))
    s.append(official([
        "Container networking refers to the ability for containers to connect to and communicate with each other, "
        "and with non-Docker network services.",
        "Containers have networking enabled by default, and they can make outgoing connections. A container has no "
        "information about what kind of network it's attached to, or whether its peers are also Docker "
        "workloads or not. A container only sees a network interface with an IP address, a gateway, a routing "
        "table, DNS services, and other networking details.",
    ]))
    s.append(figure(d_overview(), "Figure 1.1 - Containers on the default bridge: private IPs, a shared gateway, "
                                  "NAT for outbound traffic and -p for inbound traffic"))
    s.append(P("1.2 The three directions of traffic", "h1"))
    s += table(["Direction", "How it works", "What you do"], [
        ["Container -> internet", "NAT through the host (masquerading)", "Nothing - works by default"],
        ["Container -> container", "Over a shared Docker network", "Put both on the same <b>user-defined</b> "
                                                                   "network and use the container name"],
        ["Outside -> container", "Through a published host port", "Run with `-p HOST_PORT:CONTAINER_PORT`"],
    ], cols(0.24, 0.36, 0.40))
    s.append(real("A Docker network is like an office floor with its own phone extension list. People on the "
                  "same floor (network) call each other by name. To reach someone from outside the building, the "
                  "reception desk (published port) forwards the call to the right extension."))
    s.append(P("1.3 Look at it yourself", "h1"))
    s.append(code("""docker network ls

NETWORK ID     NAME      DRIVER    SCOPE
b9f48163cd36   bridge    bridge    local
13ada6da870f   host      host      local
dff0714beab7   none      null      local""", "Three networks exist on every Docker host"))
    s.append(code("""docker network inspect bridge -f "{{range .IPAM.Config}}{{.Subnet}} gw {{.Gateway}}{{end}}"
172.17.0.0/16 gw 172.17.0.1""", "Subnet and gateway of the default bridge"))
    return s


def part2():
    s = banner(2, "Network drivers", "Know which driver to pick for each situation.")
    s.append(P("2.1 The drivers", "h1"))
    s.append(official("Docker's networking subsystem is pluggable, using drivers. Several drivers exist by "
                      "default, and provide core networking functionality."))
    s += table(["Driver", "What it does", "Use it for"], [
        ["`bridge`", "The default. A private software bridge on the host; containers get private IPs.",
         "Apps on one host - almost everything you do on a laptop"],
        ["`host`", "Removes isolation: the container uses the host's network directly.",
         "Maximum network performance, or many ports"],
        ["`none`", "Completely isolates the container from the host and other containers (only loopback).",
         "Jobs that must have no network"],
        ["`macvlan`", "Gives the container its own MAC address so it looks like a physical device on the LAN.",
         "Legacy apps that expect to be directly on the physical network"],
        ["`ipvlan`", "Full control over IPv4/IPv6 addressing; containers share the host's MAC address.",
         "Large LANs, or networks that limit MAC addresses"],
        ["Plugins", "Third-party network drivers.", "Special integrations"],
    ], cols(0.14, 0.50, 0.36))
    s.append(P("2.2 Which one should I use?", "h1"))
    s += bullets([
        "<b>User-defined bridge</b> - when containers on the same host must talk to each other. This is the "
        "right answer most of the time.",
        "<b>host</b> - when the network stack should not be isolated from the host, but the rest of the container "
        "should be.",
        "<b>none</b> - when the container needs no network at all.",
        "<b>macvlan / ipvlan</b> - when containers must appear directly on the physical network (Linux hosts).",
    ])
    s.append(mistake("Leaving everything on the <b>default</b> `bridge` network. It works for one container, but "
                     "containers on it cannot find each other by name. Create your own network (Part 3)."))
    return s


def part3():
    s = banner(3, "Default bridge vs user-defined bridge", "See why your own bridge network is better than the "
               "default one.")
    s.append(P("3.1 The difference in one picture", "h1"))
    s.append(figure(d_bridges(), "Figure 3.1 - Tested on Docker Desktop: names work only on a user-defined bridge"))
    s.append(P("3.2 Try it: the default bridge", "h1"))
    s.append(code("""docker run -d --name nettest-web1 nginx:alpine
docker run --rm alpine wget -qO- -T 3 http://nettest-web1
wget: bad address 'nettest-web1'

# Find the IP address (Docker 29: read it per network)
docker inspect -f "{{.NetworkSettings.Networks.bridge.IPAddress}}" nettest-web1
172.17.0.2
docker run --rm alpine wget -qO- -T 3 http://172.17.0.2        # works""", "PowerShell"))
    s.append(P("3.3 Try it: a user-defined bridge", "h1"))
    s.append(code("""docker network create nettest-net
docker run -d --name nettest-web2 --network nettest-net nginx:alpine
docker run --rm --network nettest-net alpine wget -qO- http://nettest-web2      # works by name
docker run --rm --network nettest-net alpine cat /etc/resolv.conf
nameserver 127.0.0.11""", "PowerShell"))
    s.append(P("3.4 Why user-defined bridges are better", "h1"))
    s += table(["", "Default bridge", "User-defined bridge"], [
        ["Find containers by name", "No (IP only, or legacy `--link`)", "<b>Yes</b> - automatic DNS"],
        ["Isolation", "All containers started without `--network` share it", "Only containers you attach"],
        ["Attach / detach while running", "No - recreate the container", "Yes - `docker network connect`"],
        ["Configuration", "Global, changing it needs a Docker restart", "Per network: subnet, gateway, options"],
        ["Created by", "Docker, automatically", "You: `docker network create`"],
    ], cols(0.28, 0.36, 0.36))
    s.append(funfact("`--link` is a legacy feature of the default bridge. Do not use it in new setups - a "
                     "user-defined network does the same job and more."))
    s.append(tryit("Start two `nginx:alpine` containers on your own network and `wget` one from the other by "
                   "name. Then repeat on the default bridge and read the error."))
    return s


def part4():
    s = banner(4, "Publishing ports", "Make a container reachable from your browser - and only where you want it.")
    s.append(P("4.1 What -p does", "h1"))
    s.append(official("By default, when you create or run a container using `docker create` or `docker run`, "
                      "containers on bridge networks don't expose any ports to the outside world. Use the "
                      "`--publish` or `-p` flag to make a port available to services outside the bridge network."))
    s.append(figure(d_ports(), "Figure 4.1 - A published port forwards host traffic into the container"))
    s.append(P("4.2 All the forms of -p", "h1"))
    s += table(["Flag", "Meaning"], [
        ["`-p 8080:80`", "Host port 8080 (all interfaces) -> container TCP port 80"],
        ["`-p 192.168.1.100:8080:80`", "Only on the host IP 192.168.1.100"],
        ["`-p 127.0.0.1:8080:80`", "Only on localhost - other machines cannot connect"],
        ["`-p 8080:80/udp`", "UDP instead of TCP"],
        ["`-p 8080:80/tcp -p 8080:80/udp`", "Both TCP and UDP"],
        ["`-p 80`", "Container port 80 -> a <b>random</b> free host port"],
        ["`-P`", "Publish every `EXPOSE`d port to random host ports"],
    ], cols(0.40, 0.60))
    s.append(code("""docker run -d --name nettest-web3 -p 127.0.0.1:8089:80 nginx:alpine
docker port nettest-web3
80/tcp -> 127.0.0.1:8089

docker run -d --name nettest-web4 -P nginx:alpine
docker port nettest-web4
80/tcp -> 0.0.0.0:32768""", "Check which ports are published"))
    s.append(P("4.3 Security", "h1"))
    s.append(official("Publishing container ports is insecure by default. Meaning, when you publish a container's "
                      "ports it becomes available not only to the Docker host, but to the outside world as well. "
                      "If you include the localhost IP address (127.0.0.1, or ::1) with the publish flag, only the "
                      "Docker host and its containers can access the published container port.",
                      title="Official warning"))
    s.append(mistake("Thinking `EXPOSE 9090` in the Dockerfile publishes the port. `EXPOSE` is only documentation "
                     "(and the list used by `-P`). Nothing is reachable from the host until you use `-p` or `-P`."))
    s.append(mistake("On Linux servers, Docker writes its own firewall (iptables) rules. A published port can be "
                     "reachable from the internet even when `ufw` seems to block it. Publish to `127.0.0.1` or "
                     "use a cloud security group.", title="Firewall surprise"))
    s.append(funfact("Containers on the same network never need `-p` to talk to each other - they use the "
                     "container port directly, e.g. `http://devops-java-demo:9090`."))
    return s


def part5():
    s = banner(5, "DNS and service discovery", "Find containers by name and control how names are resolved.")
    s.append(P("5.1 The embedded DNS server", "h1"))
    s.append(official("Containers that use the default bridge network get a copy of the host's /etc/resolv.conf. "
                      "Containers on custom networks use Docker's embedded DNS server, which forwards external DNS "
                      "lookups to the DNS servers configured on the host."))
    s.append(figure(d_dns(), "Figure 5.1 - 127.0.0.11 answers container names itself and forwards everything else"))
    s.append(P("5.2 Names a container can be found by", "h1"))
    s += table(["Name", "How", "Example"], [
        ["Container name", "`--name`", "`http://devops-java-demo:9090`"],
        ["Network alias", "`--network-alias` (several containers may share one)", "`http://webalias`"],
        ["Container ID", "Short ID also resolves", "`http://eb6861818895`"],
    ], cols(0.20, 0.45, 0.35))
    s.append(code("""docker run -d --name nettest-web2 --network nettest-net --network-alias webalias nginx:alpine
docker run --rm --network nettest-net alpine wget -qO- http://webalias       # works""", "Network alias"))
    s.append(P("5.3 DNS options for docker run", "h1"))
    s += table(["Flag", "Effect"], [
        ["`--dns 8.8.8.8`", "Use this DNS server for external names"],
        ["`--dns-search example.com`", "Search domain for short names"],
        ["`--dns-option ndots:2`", "Extra resolver option"],
        ["`--hostname web01`", "Host name inside the container"],
        ["`--add-host db.local:10.0.0.5`", "Adds a line to the container's `/etc/hosts`"],
    ], cols(0.40, 0.60))
    s.append(P("5.4 Reaching the host from a container", "h1"))
    s.append(P("`localhost` inside a container is the container itself, not your laptop. To call a service "
               "running on the host (for example an app started with `mvn spring-boot:run`):"))
    s += bullets([
        "<b>Docker Desktop</b> (Windows/macOS): use `host.docker.internal` - it works out of the box.",
        "<b>Linux</b>: add `--add-host=host.docker.internal:host-gateway` to `docker run`.",
    ])
    s.append(code("""docker run --rm alpine wget -qO- http://host.docker.internal:9090/name
Welcome to TrishaAcademy""", "Container -> app published on the host"))
    s.append(mistake("Configuring `jdbc:mysql://localhost:3306` in a container and expecting it to reach a "
                     "database on your laptop or in another container. Use the container name (same network) or "
                     "`host.docker.internal` (service on the host)."))
    return s


def part6():
    s = banner(6, "Managing networks", "Create, connect, inspect and remove networks with the Docker CLI.")
    s.append(P("6.1 The docker network commands", "h1"))
    s += table(["Command", "What it does"], [
        ["`docker network create NAME`", "Create a user-defined bridge network"],
        ["`docker network ls`", "List networks"],
        ["`docker network inspect NAME`", "Subnet, gateway, options and attached containers"],
        ["`docker network connect NAME CONTAINER`", "Attach a running container to another network"],
        ["`docker network disconnect NAME CONTAINER`", "Detach it again"],
        ["`docker network rm NAME`", "Delete a network (no container may be attached)"],
        ["`docker network prune`", "Delete all unused networks"],
    ], cols(0.48, 0.52))
    s.append(P("6.2 Subnet, gateway, static IP and internal networks", "h1"))
    s.append(code("""docker network create --subnet 172.30.0.0/24 --gateway 172.30.0.1 nettest-sub
docker run --rm --network nettest-sub --ip 172.30.0.50 alpine ip -o -4 addr show eth0
2: eth0    inet 172.30.0.50/24 brd 172.30.0.255 scope global eth0""", "Custom subnet and a fixed IP"))
    s.append(code("""docker network create --internal nettest-int
docker run --rm --network nettest-int alpine wget -qO- -T 4 http://example.com
wget: bad address 'example.com'          # no way out to the internet""", "Internal network"))
    s += table(["Option", "Use"], [
        ["`--driver bridge`", "Driver (bridge is the default)"],
        ["`--subnet`, `--gateway`, `--ip-range`", "Choose the address range - avoid clashes with office/VPN networks"],
        ["`--ip` (on `docker run`)", "Fixed IP - only on a user-defined network with `--subnet`"],
        ["`--internal`", "No outbound traffic - good for databases"],
        ["`--ipv6`", "Enable IPv6 on the network"],
        ["`-o com.docker.network.bridge.name=br-trisha`", "Name of the bridge interface on the Linux host"],
    ], cols(0.48, 0.52))
    s.append(P("6.3 One container, several networks", "h1"))
    s.append(P("A container can be on several networks at the same time - the classic pattern is a front-end "
               "network for the web app and a back-end network shared only with the database."))
    s.append(code("""docker network connect nettest-net nettest-web1
docker inspect -f "{{range $k,$v := .NetworkSettings.Networks}}{{$k}}={{$v.IPAddress}} {{end}}" nettest-web1
bridge=172.17.0.2 nettest-net=172.18.0.3
docker network disconnect nettest-net nettest-web1""", "Connect and disconnect a running container"))
    s.append(funfact("Since Docker Engine 29 the old shortcut `{{.NetworkSettings.IPAddress}}` is gone - read the "
                     "IP per network as shown above, or look at `docker inspect` output under `Networks`."))
    s.append(P("6.4 Clean up", "h1"))
    s.append(code("""docker rm -f nettest-web1 nettest-web2 nettest-web3 nettest-web4
docker network rm nettest-net nettest-int nettest-sub
docker network prune          # removes every network no container uses""", "PowerShell"))
    return s


def part7():
    s = banner(7, "host, none and container: networking", "Turn isolation off, switch networking off, or share "
               "one container's network.")
    s.append(figure(d_modes(), "Figure 7.1 - Three special network modes"))
    s.append(P("7.1 host", "h1"))
    s.append(official("If you use the host network mode for a container, that container's network stack isn't "
                      "isolated from the Docker host (the container shares the host's networking namespace), and "
                      "the container doesn't get its own IP-address allocated."))
    s.append(code("""docker run -d --name web-host --network host nginx:alpine
# nginx now listens on port 80 of the host itself - no -p needed (and -p is ignored)""", "Linux host"))
    s += bullets([
        "Fastest option: no NAT and no port forwarding.",
        "Port clashes: two containers cannot both listen on port 80.",
        "On Docker Desktop host networking is an opt-in setting in newer versions, and it means the Docker "
        "Desktop VM's network - use `-p` on Windows/macOS instead.",
    ])
    s.append(P("7.2 none", "h1"))
    s.append(code("""docker run --rm --network none alpine ip -o addr
1: lo    inet 127.0.0.1/8 scope host lo""", "Only the loopback interface"))
    s.append(P("7.3 container:<name>", "h1"))
    s.append(P("The new container joins the network namespace of an existing one: same IP, same ports, and they "
               "talk over `localhost`. Useful for debugging a container that has no tools inside."))
    s.append(code("""docker run --rm --network container:nettest-web2 alpine wget -qO- http://localhost
<!DOCTYPE html> ... Welcome to nginx! ...""", "Share the network of nettest-web2"))
    s.append(tryit("Start `nginx:alpine` without any port, then use `--network container:` with `alpine` to fetch "
                   "its page over `localhost`."))
    return s


def part8():
    s = banner(8, "macvlan and ipvlan", "Put containers directly on the physical network (Linux hosts).")
    s.append(P("8.1 macvlan", "h1"))
    s.append(official("Some applications, especially legacy applications or applications which monitor network "
                      "traffic, expect to be directly connected to the physical network. In this type of situation, "
                      "you can use the macvlan network driver to assign a MAC address to each container's virtual "
                      "network interface, making it appear to be a physical network interface directly connected to "
                      "the physical network."))
    s.append(code("""docker network create -d macvlan `
  --subnet=192.168.1.0/24 --gateway=192.168.1.1 `
  -o parent=eth0 pub_net
docker run -d --name legacy-app --network pub_net --ip 192.168.1.50 nginx:alpine""",
                  "Linux host, eth0 on the 192.168.1.0/24 LAN"))
    s += bullets([
        "The container gets an address on your real LAN - other machines reach it without `-p`.",
        "The host itself usually <b>cannot</b> talk to its macvlan containers directly.",
        "Many switches and cloud networks (AWS, Azure) block unknown MAC addresses - check first.",
        "Pick an IP range that your DHCP server does not hand out.",
    ])
    s.append(P("8.2 ipvlan", "h1"))
    s.append(P("Like macvlan, but every container shares the host's MAC address. Use it when the network limits the "
               "number of MAC addresses per port."))
    s += table(["Mode", "How it works"], [
        ["`ipvlan` L2 (default)", "Containers are on the same subnet as the host, like macvlan"],
        ["`ipvlan` L3", "The host routes between container subnets - no broadcast, needs routes on the router"],
    ], cols(0.32, 0.68))
    s.append(code("""docker network create -d ipvlan --subnet=192.168.1.0/24 --gateway=192.168.1.1 `
  -o parent=eth0 -o ipvlan_mode=l2 ipvlan_net""", "ipvlan L2"))
    s.append(mistake("Trying macvlan or ipvlan on Docker Desktop for Windows/macOS. They need a Linux host with a "
                     "real network interface. On a laptop, stay with bridge networks and `-p`."))
    return s


def part9():
    s = banner(9, "Hands-on lab: network the devops-java-demo app",
               "Run the Student API on its own network, call it by name from another container, and control "
               "who can reach it.")
    s.append(figure(d_lab(), "Figure 9.1 - The lab setup (every arrow was tested)"))
    s.append(P("9.1 Build the image and create the network", "h1"))
    s.append(code("""cd D:\\TRISHA-ACADEMY\\DevOPs\\devops-java-demo
docker build -t devops-java-demo:1.0.0 .
docker network create trisha-net""", "PowerShell"))
    s.append(P("9.2 Run the app on trisha-net and publish port 9090", "h1"))
    s.append(code("""docker run -d --name devops-java-demo --network trisha-net -p 9090:9090 `
  -v "${PWD}\\data:/app/data" devops-java-demo:1.0.0
docker logs -f devops-java-demo        # wait for "Started SpringLabApplication", then Ctrl + C""",
                  "PowerShell"))
    s.append(P("9.3 Call it from three places", "h1"))
    s.append(code("""# 1. From the host (published port)
Invoke-RestMethod http://localhost:9090/name
Welcome to TrishaAcademy

# 2. From another container on trisha-net (by name, container port)
docker run --rm --network trisha-net alpine wget -qO- http://devops-java-demo:9090/name
Welcome to TrishaAcademy

# 3. From a container on the default bridge
docker run --rm alpine wget -qO- -T 3 http://devops-java-demo:9090/name
wget: bad address 'devops-java-demo:9090'
docker run --rm alpine wget -qO- http://host.docker.internal:9090/name
Welcome to TrishaAcademy""", "Expected output"))
    s.append(P("9.4 Keep the app private", "h1"))
    s.append(P("Run it again <b>without</b> `-p`: other containers on `trisha-net` can still use it, but the host "
               "and the outside world cannot."))
    s.append(code("""docker rm -f devops-java-demo
docker run -d --name devops-java-demo --network trisha-net `
  -v "${PWD}\\data:/app/data" devops-java-demo:1.0.0

docker run --rm --network trisha-net alpine wget -qO- http://devops-java-demo:9090/name
Welcome to TrishaAcademy
Invoke-RestMethod http://localhost:9090/name -TimeoutSec 3
Invoke-RestMethod : The operation has timed out.""", "Expected output"))
    s.append(P("9.5 Results", "h1"))
    s += table(["#", "From", "Address", "Result"], [
        ["1", "Host (with `-p 9090:9090`)", "`localhost:9090`", "Works"],
        ["2", "Container on `trisha-net`", "`devops-java-demo:9090`", "Works - embedded DNS"],
        ["3", "Container on default bridge", "`devops-java-demo:9090`", "<b>Fails</b> - different network"],
        ["4", "Container on default bridge", "`host.docker.internal:9090`", "Works - through the host port"],
        ["5", "Container on `trisha-net` (no `-p`)", "`devops-java-demo:9090`", "Works"],
        ["6", "Host (no `-p`)", "`localhost:9090`", "<b>Fails</b> - port not published"],
    ], cols(0.05, 0.33, 0.32, 0.30))
    s.append(P("9.6 Variations to try", "h1"))
    s += bullets([
        "Publish only to your laptop: `-p 127.0.0.1:9090:9090`.",
        "Run a second copy on another host port: `--name devops-java-demo-2 -p 9091:9090` - the container port "
        "stays 9090.",
        "Give the app an alias: `--network-alias student-api`, then call `http://student-api:9090/name`.",
        "Make the network internal (`docker network create --internal trisha-private`) - the app keeps working "
        "for other containers but cannot reach the internet.",
    ])
    s.append(P("9.7 Clean up", "h1"))
    s.append(code("""docker rm -f devops-java-demo
docker network rm trisha-net""", "PowerShell"))
    return s


def part10():
    s = banner(10, "Best practices, troubleshooting and cheat sheet", "Avoid the classic mistakes.")
    s.append(P("10.1 Best practices", "h1"))
    s += bullets([
        "Create a <b>user-defined bridge</b> per application; never rely on the default bridge.",
        "Call other containers by <b>name</b> or alias - never hard-code container IP addresses.",
        "Publish only the ports users need; keep databases unpublished on an internal network.",
        "Publish to `127.0.0.1` on shared or public machines unless the port must be public.",
        "Choose subnets that do not clash with your office, VPN or cloud networks.",
        "Use `host.docker.internal` (Docker Desktop) or `host-gateway` (Linux) to reach host services.",
        "Remove unused networks with `docker network prune`.",
    ])
    s.append(P("10.2 Troubleshooting", "h1"))
    s += table(["Problem", "Cause and fix"], [
        ["`wget: bad address 'name'`", "Containers are on different networks, or on the default bridge - put both "
                                       "on the same user-defined network"],
        ["Browser cannot open `localhost:9090`", "No `-p`, wrong port order (`HOST:CONTAINER`), or the app is not "
                                                 "started yet - check `docker port` and `docker logs`"],
        ["`port is already allocated`", "Another container or program uses the host port - pick another host "
                                        "port, e.g. `-p 9091:9090`"],
        ["App unreachable although published", "The app listens on `127.0.0.1` inside the container - it must "
                                               "listen on `0.0.0.0` (Spring Boot does by default)"],
        ["`network ... has active endpoints`", "Containers still attached - `docker network inspect`, then remove "
                                               "or disconnect them"],
        ["`Pool overlaps with other one`", "Subnet clash - choose another `--subnet`"],
        ["`localhost` in a container does not reach the host", "Use `host.docker.internal`"],
        ["Template error on `.NetworkSettings.IPAddress`", "Docker 29+ - use "
                                                           "`.NetworkSettings.Networks.<net>.IPAddress`"],
    ], cols(0.38, 0.62))
    s.append(P("10.3 Cheat sheet", "h1"))
    s += table(["Goal", "Command"], [
        ["Create / list / inspect", "`docker network create n` · `docker network ls` · `docker network inspect n`"],
        ["Run on a network", "`docker run --network n --name app image`"],
        ["Alias", "`--network-alias api`"],
        ["Publish", "`-p 9090:9090` · `-p 127.0.0.1:9090:9090` · `-P`"],
        ["Which ports are published", "`docker port c`"],
        ["Attach / detach", "`docker network connect n c` · `docker network disconnect n c`"],
        ["IP of a container", "`docker inspect -f \"{{.NetworkSettings.Networks.n.IPAddress}}\" c`"],
        ["Test from inside", "`docker run --rm --network n alpine wget -qO- http://app:9090`"],
        ["Special modes", "`--network host` · `--network none` · `--network container:c`"],
        ["Remove", "`docker network rm n` · `docker network prune`"],
    ], cols(0.28, 0.72))
    return s


QA = [
    ("What is the default network driver?",
     "bridge. Containers started without --network join the default bridge network called bridge (docker0, "
     "172.17.0.0/16 by default)."),
    ("Name the built-in network drivers.",
     "bridge, host, none, macvlan and ipvlan, plus third-party network plugins."),
    ("Default bridge vs user-defined bridge?",
     "A user-defined bridge gives automatic DNS by container name, better isolation, attach/detach while "
     "running, and per-network configuration. The default bridge only allows IP addresses (or legacy --link)."),
    ("How do two containers talk to each other?",
     "Put them on the same user-defined network and use the container name (or an alias) with the container port, "
     "e.g. http://devops-java-demo:9090."),
    ("What does -p 8080:80 mean?",
     "Traffic to host port 8080 is forwarded to port 80 inside the container. Left side = host, right side = "
     "container."),
    ("Does EXPOSE publish a port?",
     "No. EXPOSE only documents the port (and is used by -P). You must publish with -p or -P."),
    ("Why is publishing a port considered insecure by default?",
     "-p 8080:80 binds to all host interfaces, so the port is reachable from other machines. Use "
     "-p 127.0.0.1:8080:80 to allow only the host."),
    ("What is 127.0.0.11?",
     "Docker's embedded DNS server in containers on user-defined networks. It resolves container names and "
     "aliases and forwards other names to the host's DNS servers."),
    ("What is a network alias?",
     "An extra DNS name for a container on a network (--network-alias). Several containers can share one alias."),
    ("What does --network host do?",
     "The container shares the host's network stack: no own IP, no NAT, -p is ignored, and the app's ports are the "
     "host's ports. Fast but not isolated."),
    ("When would you use --network none?",
     "For containers that must have no network at all, such as batch jobs or untrusted code. Only loopback exists."),
    ("What is --network container:<name>?",
     "The new container joins another container's network namespace: same IP and ports, communication over "
     "localhost. Useful for debugging and sidecars."),
    ("How does a container reach a service on the host?",
     "Use host.docker.internal on Docker Desktop; on Linux add --add-host=host.docker.internal:host-gateway. "
     "localhost inside a container is the container itself."),
    ("Can a container be on more than one network?",
     "Yes. Use docker network connect / disconnect, e.g. a web app on a front-end and a back-end network."),
    ("What is an internal network?",
     "A network created with --internal: containers on it can talk to each other but have no outbound internet "
     "access."),
    ("How do you give a container a fixed IP?",
     "Create a user-defined network with --subnet, then docker run --network <net> --ip <address>."),
    ("macvlan vs ipvlan?",
     "Both put containers directly on the physical network. macvlan gives each container its own MAC address; "
     "ipvlan shares the host's MAC and supports L2 and L3 modes."),
    ("How do you find a container's IP address?",
     "docker inspect -f \"{{.NetworkSettings.Networks.<net>.IPAddress}}\" <container>, or look under Networks in "
     "docker inspect."),
    ("Why should you not hard-code container IPs?",
     "IPs change when containers are recreated. Names and aliases are resolved by Docker's DNS every time."),
    ("Your app in a container is published but not reachable - what do you check?",
     "docker ps / docker port for the mapping, docker logs for start-up, that the app listens on 0.0.0.0 and the "
     "right port, the host port is free, and the firewall."),
]


def part11():
    s = banner(11, "Top 20 interview questions", "Answer aloud before reading the model answer.")
    s.append(P("Interviewers look for a clear definition, one real example and one trade-off."))
    for i, (q, a) in enumerate(QA, 1):
        s.append(KeepTogether([P(f"Q{i}. {q}", "q"), P(a, "a")]))
    s.append(gap(10))
    s.append(P("Reference", "h2"))
    s += bullets([
        "Docker docs - Networking overview: https://docs.docker.com/engine/network/",
        "Docker docs - Bridge network driver: https://docs.docker.com/engine/network/drivers/bridge/",
        "Docker docs - Port publishing: https://docs.docker.com/engine/network/port-publishing/",
        "Docker docs - host, none, macvlan, ipvlan: https://docs.docker.com/engine/network/drivers/",
        "Companion notes: Docker-Volumes-Guide.pdf",
    ])
    return s


def build():
    os.makedirs(OUT_DIR, exist_ok=True)
    doc = new_doc(OUT_FILE, "Docker Networking", "Docker training notes", draw_network_cover)
    story = start_story() + front()
    for part in (part1, part2, part3, part4, part5, part6, part7, part8, part9, part10, part11):
        story += part()
    doc.multiBuild(story)
    return OUT_FILE


if __name__ == "__main__":
    print(build())
