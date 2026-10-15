"""Vector diagrams for the Kubernetes course (reportlab.graphics)."""
from k8s_pdf_lib import (BLUE, BLUE_BG, BLUE_DARK, GOLD, GOLD_BG, GREEN, GREEN_BG,
                         GREY_BG, INK, LINE, MUTED, NAVY, ORANGE, ORANGE_BG, PURPLE,
                         PURPLE_BG, RED, RED_BG, TEAL, TEAL_BG, WHITE, arrow, badge,
                         box, drawing, frame, pod_icon, text)
from reportlab.graphics.shapes import Line


def architecture():
    d = drawing(300)
    box(d, 5, 200, 82, 46, ["kubectl", "you / CI pipeline"], fill=GOLD_BG, stroke=ORANGE)
    frame(d, 100, 160, 412, 132, "CONTROL PLANE  (the head office)", fill=BLUE_BG,
          stroke=BLUE, title_color=BLUE_DARK)
    box(d, 112, 172, 112, 92, ["kube-apiserver", "front door of the", "cluster - every", "request comes here"],
        fill=WHITE, stroke=BLUE, size=9)
    box(d, 262, 228, 118, 38, ["etcd", "key-value store of state"], fill=WHITE, stroke=BLUE)
    box(d, 262, 176, 118, 38, ["kube-scheduler", "picks a node for a pod"], fill=WHITE, stroke=BLUE)
    box(d, 390, 228, 114, 38, ["controller-manager", "keeps desired = actual"], fill=WHITE, stroke=BLUE)
    box(d, 390, 176, 114, 38, ["cloud-controller", "talks to AWS/Azure/GCP"], fill=WHITE, stroke=BLUE)
    arrow(d, 87, 223, 111, 223)
    text(d, 46, 252, "HTTPS requests", size=7.5, color=MUTED)
    arrow(d, 224, 247, 261, 247)
    arrow(d, 224, 195, 261, 195)
    for i, x in enumerate((100, 310)):
        frame(d, x, 8, 202, 122, f"WORKER NODE {i + 1}  (a branch)", fill=WHITE, stroke=NAVY)
        box(d, x + 8, 74, 90, 30, ["kubelet", "node agent"], fill=GREEN_BG, stroke=GREEN, size=8.5)
        box(d, x + 104, 74, 90, 30, ["kube-proxy", "service routing"], fill=TEAL_BG, stroke=TEAL, size=8.5)
        box(d, x + 8, 42, 186, 26, ["containerd  (container runtime)"], fill=GREY_BG, stroke=MUTED, size=8.5)
        for k in range(3):
            pod_icon(d, x + 12 + k * 62, 12, w=54, h=22, label=f"pod {chr(97 + k + i * 3)}")
    arrow(d, 150, 172, 175, 131, color=GREEN, label="watch & report", label_dx=-38, label_dy=0)
    arrow(d, 205, 172, 385, 131, color=GREEN)
    text(d, 46, 150, "Rule:", size=8.5, bold=True, color=BLUE_DARK)
    text(d, 46, 138, "every component", size=7.8, color=MUTED)
    text(d, 46, 127, "talks only to the", size=7.8, color=MUTED)
    text(d, 46, 116, "API server", size=7.8, color=MUTED)
    return d


def apply_flow():
    d = drawing(178)
    steps = [
        ("kubectl apply", "you send YAML"),
        ("API server", "authn, authz, admission"),
        ("etcd", "desired state saved"),
        ("Controller", "creates ReplicaSet/Pods"),
        ("Scheduler", "assigns pod to a node"),
        ("kubelet", "sees new pod on its node"),
        ("containerd", "pulls image, starts it"),
        ("Status: Running", "kubectl get pods"),
    ]
    xs_top = [5, 141, 277, 413]
    xs_bot = [413, 277, 141, 5]
    w, h = 98, 46
    for i, (t, s) in enumerate(steps):
        x, y = (xs_top[i], 110) if i < 4 else (xs_bot[i - 4], 18)
        fill = GREEN_BG if i == 7 else (GOLD_BG if i == 0 else WHITE)
        box(d, x, y, w, h, [t, s], fill=fill, stroke=BLUE if 0 < i < 7 else ORANGE, size=9)
        badge(d, x + 4, y + h, i + 1)
    for i in range(3):
        arrow(d, xs_top[i] + w, 133, xs_top[i + 1] - 1, 133)
    arrow(d, 462, 110, 462, 65)
    for i in range(3):
        arrow(d, xs_bot[i], 41, xs_bot[i + 1] + w + 1, 41)
    return d


def reconcile():
    d = drawing(190)
    box(d, 175, 140, 165, 42, ["1. Observe", "what is running right now?"], fill=WHITE, stroke=BLUE)
    box(d, 350, 76, 160, 42, ["2. Compare", "desired (etcd) vs actual"], fill=GOLD_BG, stroke=ORANGE)
    box(d, 175, 10, 165, 42, ["3. Act", "start / stop / replace pods"], fill=GREEN_BG, stroke=GREEN)
    box(d, 5, 76, 160, 42, ["4. Repeat", "forever, every few seconds"], fill=GREY_BG, stroke=MUTED)
    arrow(d, 340, 161, 430, 119)
    arrow(d, 430, 76, 340, 31)
    arrow(d, 175, 31, 85, 76)
    arrow(d, 85, 118, 175, 161)
    text(d, 257, 100, "Control loop", size=11, bold=True, color=NAVY)
    text(d, 257, 86, "want 3 pods, see 2", size=8, color=MUTED)
    text(d, 257, 75, "-> start 1 more", size=8, color=MUTED)
    return d


def pod():
    d = drawing(185)
    frame(d, 55, 8, 405, 170, "POD  web-6f7c  -  one IP: 10.244.1.7", fill=BLUE_BG, stroke=BLUE,
          title_color=BLUE_DARK)
    box(d, 75, 90, 155, 54, ["main container", "nginx  - port 80", "writes /var/log/app"],
        fill=WHITE, stroke=NAVY)
    box(d, 285, 90, 155, 54, ["sidecar container", "log shipper", "reads /var/log/app"],
        fill=WHITE, stroke=PURPLE)
    arrow(d, 231, 117, 284, 117, color=PURPLE, label="localhost", label_dy=5, head=True)
    box(d, 75, 22, 365, 44, ["shared volume (emptyDir)", "lives as long as the pod lives"],
        fill=GOLD_BG, stroke=ORANGE)
    arrow(d, 152, 90, 152, 67, color=ORANGE, dashed=True)
    arrow(d, 362, 90, 362, 67, color=ORANGE, dashed=True)
    return d


def pod_lifecycle():
    d = drawing(128)
    box(d, 5, 70, 92, 40, ["Pending", "waiting for node"], fill=GOLD_BG, stroke=ORANGE)
    box(d, 115, 70, 110, 40, ["ContainerCreating", "pulling image"], fill=WHITE, stroke=BLUE)
    box(d, 243, 70, 92, 40, ["Running", "at least 1 up"], fill=GREEN_BG, stroke=GREEN)
    box(d, 360, 90, 150, 32, ["Succeeded", "all containers exited 0"], fill=GREEN_BG, stroke=GREEN, size=8.5)
    box(d, 360, 48, 150, 32, ["Failed", "a container exited non-zero"], fill=RED_BG, stroke=RED, size=8.5)
    box(d, 205, 5, 168, 32, ["CrashLoopBackOff", "keeps crashing, waits longer"], fill=RED_BG,
        stroke=RED, size=8.5)
    arrow(d, 97, 90, 114, 90)
    arrow(d, 225, 90, 242, 90)
    arrow(d, 335, 98, 359, 106)
    arrow(d, 335, 82, 359, 66)
    arrow(d, 270, 70, 270, 38, color=RED)
    arrow(d, 305, 38, 305, 69, color=RED, dashed=True)
    text(d, 240, 50, "crash", size=7.5, color=RED, anchor="end")
    text(d, 312, 50, "restart", size=7.5, color=RED, anchor="start")
    return d


def deployment():
    d = drawing(192)
    box(d, 157, 148, 200, 40, ["Deployment: web", "replicas: 3  ·  image nginx:1.27"],
        fill=BLUE_BG, stroke=BLUE)
    box(d, 300, 82, 205, 40, ["ReplicaSet web-7d9f (current)", "keeps exactly 3 pods"],
        fill=WHITE, stroke=BLUE)
    box(d, 10, 82, 205, 40, ["ReplicaSet web-5c6b (old)", "0 pods - kept for rollback"],
        fill=GREY_BG, stroke=MUTED, dashed=True)
    arrow(d, 290, 148, 380, 123)
    arrow(d, 225, 148, 130, 123, color=MUTED, dashed=True)
    for k in range(3):
        pod_icon(d, 305 + k * 68, 14, w=60, h=34, label=f"pod {k + 1}", fill=GREEN_BG, stroke=GREEN)
        arrow(d, 402, 82, 335 + k * 68, 49, color=GREEN, width=1)
    text(d, 112, 55, "rollback = scale this", size=8, color=MUTED)
    text(d, 112, 43, "old ReplicaSet back up", size=8, color=MUTED)
    return d


def rolling_update():
    d = drawing(182)
    stages = [
        ("Start", ["v1", "v1", "v1"]),
        ("Surge +1", ["v1", "v1", "v1", "v2*"]),
        ("Swap one by one", ["v1", "v2", "v2"]),
        ("Done", ["v2", "v2", "v2"]),
    ]
    for i, (title, pods) in enumerate(stages):
        x = 8 + i * 130
        text(d, x + 52, 166, f"{i + 1}. {title}", size=9, bold=True, color=NAVY)
        for k, v in enumerate(pods):
            y = 128 - k * 33
            new = v.startswith("v2")
            label = "nginx:1.27" if new else "nginx:1.26"
            if v.endswith("*"):
                label += " (starting)"
            box(d, x, y, 104, 26, [label], fill=GREEN_BG if new else BLUE_BG,
                stroke=GREEN if new else BLUE, size=8, dashed=v.endswith("*"))
        if i < 3:
            arrow(d, x + 108, 95, x + 126, 95)
    text(d, 257, 6, "maxSurge: 1 (one extra pod allowed)  ·  maxUnavailable: 0 (never below 3 ready)",
         size=8, color=MUTED)
    return d


def services():
    d = drawing(196)
    box(d, 5, 82, 95, 44, ["client pod", "curl http://web"], fill=GOLD_BG, stroke=ORANGE)
    box(d, 140, 70, 140, 68, ["Service: web", "ClusterIP 10.96.12.5", "port 80", "selector app=web"],
        fill=BLUE_BG, stroke=BLUE)
    arrow(d, 100, 104, 139, 104)
    text(d, 100, 158, "DNS name:", size=7.5, color=MUTED)
    text(d, 100, 148, "web.default.svc", size=7.5, color=MUTED)
    ys = [150, 105, 60]
    for i, y in enumerate(ys):
        box(d, 340, y, 170, 34, [f"pod web-{i + 1}   label app=web", f"10.244.{i + 1}.5:80"],
            fill=GREEN_BG, stroke=GREEN, size=8.5)
        arrow(d, 280, 104, 339, y + 17, color=GREEN)
    box(d, 340, 8, 170, 34, ["pod db-1   label app=db", "not selected - no traffic"],
        fill=GREY_BG, stroke=MUTED, size=8.5, dashed=True)
    text(d, 310, 185, "load-balanced", size=7.8, color=GREEN)
    return d


def service_types():
    d = drawing(205)
    frame(d, 2, 2, 511, 198, "LoadBalancer  -  cloud gives one public IP, e.g. 34.10.2.8:80",
          fill=PURPLE_BG, stroke=PURPLE, title_color=PURPLE)
    frame(d, 22, 12, 471, 162, "NodePort  -  every node opens the same port (30000-32767), e.g. 30080",
          fill=GOLD_BG, stroke=ORANGE, title_color=ORANGE)
    frame(d, 42, 22, 431, 126, "ClusterIP  -  internal virtual IP, works only inside the cluster",
          fill=BLUE_BG, stroke=BLUE, title_color=BLUE_DARK)
    for k in range(3):
        pod_icon(d, 75 + k * 130, 45, w=110, h=40, label=f"pod web-{k + 1}", fill=GREEN_BG, stroke=GREEN,
                 size=8.5)
    text(d, 257, 100, "each outer type builds on the inner one", size=8, color=MUTED)
    return d


def ingress():
    d = drawing(196)
    box(d, 5, 80, 88, 44, ["Browser", "quickbite.local"], fill=GOLD_BG, stroke=ORANGE)
    box(d, 125, 64, 140, 76, ["Ingress controller", "a smart reverse proxy", "reads Ingress rules",
                              "(NGINX, Traefik ...)"], fill=BLUE_BG, stroke=BLUE)
    arrow(d, 93, 102, 124, 102)
    box(d, 315, 122, 100, 40, ["Service: menu", "ClusterIP"], fill=WHITE, stroke=BLUE)
    box(d, 315, 38, 100, 40, ["Service: orders", "ClusterIP"], fill=WHITE, stroke=BLUE)
    arrow(d, 265, 115, 314, 142, label="/menu", label_dx=-6, label_dy=8)
    arrow(d, 265, 88, 314, 58, label="/orders", label_dx=-6, label_dy=-14)
    for y in (150, 122):
        pod_icon(d, 445, y, w=65, h=22, label="menu pod", fill=GREEN_BG, stroke=GREEN)
        arrow(d, 415, 142, 444, y + 11, color=GREEN, width=1)
    for y in (52, 24):
        pod_icon(d, 445, y, w=65, h=22, label="orders pod", fill=GREEN_BG, stroke=GREEN)
        arrow(d, 415, 58, 444, y + 11, color=GREEN, width=1)
    text(d, 195, 180, "rule: host quickbite.local", size=8, color=BLUE_DARK, bold=True)
    text(d, 195, 168, "one entry point, many apps", size=7.8, color=MUTED)
    return d


def namespaces():
    d = drawing(172)
    frame(d, 0, 0, 515, 170, "ONE CLUSTER  (one building)", fill=GREY_BG, stroke=MUTED)
    spaces = [("dev", "quota: 4 CPU, 8Gi", BLUE_BG, BLUE),
              ("prod", "quota: 16 CPU, 32Gi", GREEN_BG, GREEN),
              ("kube-system", "Kubernetes' own pods", PURPLE_BG, PURPLE)]
    for i, (name, q, bg, st) in enumerate(spaces):
        x = 10 + i * 168
        frame(d, x, 10, 158, 132, f"namespace: {name}", fill=bg, stroke=st, title_color=st)
        if name == "kube-system":
            labels = ["coredns", "kube-proxy", "etcd"]
        else:
            labels = ["web", "orders", "db"]
        for k, lab in enumerate(labels):
            pod_icon(d, x + 10 + (k % 2) * 72, 80 - (k // 2) * 32, w=64, h=24, label=lab,
                     fill=WHITE, stroke=st)
        text(d, x + 79, 20, q, size=7.8, color=INK)
    return d


def config():
    d = drawing(172)
    box(d, 5, 108, 160, 52, ["ConfigMap: app-config", "APP_MODE=prod", "menu.json"],
        fill=GOLD_BG, stroke=ORANGE)
    box(d, 5, 18, 160, 52, ["Secret: db-secret", "DB_PASSWORD (base64)", "not encrypted by default!"],
        fill=RED_BG, stroke=RED)
    frame(d, 265, 8, 248, 158, "POD", fill=BLUE_BG, stroke=BLUE, title_color=BLUE_DARK)
    box(d, 280, 92, 220, 46, ["Environment variables", "$APP_MODE   $DB_PASSWORD"], fill=WHITE, stroke=NAVY)
    box(d, 280, 26, 220, 46, ["Mounted files (volume)", "/etc/secrets/db-password"], fill=WHITE,
        stroke=NAVY)
    arrow(d, 165, 134, 279, 115, color=ORANGE, label="env / envFrom", label_dy=8)
    arrow(d, 165, 44, 279, 49, color=RED, label="volume mount", label_dy=6)
    text(d, 208, 88, "Both ConfigMaps and Secrets", size=7.5, color=MUTED)
    text(d, 208, 77, "can be used either way", size=7.5, color=MUTED)
    return d


def storage():
    d = drawing(172)
    box(d, 5, 104, 98, 48, ["Pod: mysql", "mounts /var/lib/mysql"], fill=BLUE_BG, stroke=BLUE, size=8.5)
    box(d, 138, 104, 118, 48, ["PVC: mysql-data", "\"I need 1Gi, RWO\""], fill=GOLD_BG, stroke=ORANGE)
    box(d, 290, 104, 108, 48, ["PV: pvc-3f2a", "1Gi · Bound"], fill=GREEN_BG, stroke=GREEN)
    box(d, 430, 104, 82, 48, ["Real disk", "cloud / local"], fill=GREY_BG, stroke=MUTED)
    arrow(d, 103, 128, 137, 128, label="uses", label_dy=5)
    arrow(d, 256, 128, 289, 128, label="binds", label_dy=5)
    arrow(d, 398, 128, 429, 128, label="is", label_dy=5)
    box(d, 190, 12, 200, 46, ["StorageClass: standard", "creates a PV automatically"],
        fill=PURPLE_BG, stroke=PURPLE)
    arrow(d, 205, 103, 235, 59, color=PURPLE, dashed=True, label="1. request", label_dx=-34, label_dy=0)
    arrow(d, 345, 59, 345, 103, color=PURPLE, dashed=True, label="2. provision", label_dx=34, label_dy=0)
    return d


def statefulset():
    d = drawing(184)
    box(d, 150, 138, 215, 40, ["Headless Service: web-hl", "clusterIP: None - gives each pod a DNS name"],
        fill=BLUE_BG, stroke=BLUE, size=8.5)
    for i in range(3):
        x = 22 + i * 168
        box(d, x, 72, 135, 40, [f"pod web-{i}", f"web-{i}.web-hl"], fill=GREEN_BG, stroke=GREEN)
        box(d, x, 10, 135, 36, [f"PVC data-web-{i}", "own 100Mi disk"], fill=GOLD_BG, stroke=ORANGE,
            size=8.5)
        arrow(d, 257, 138, x + 67, 113)
        arrow(d, x + 67, 72, x + 67, 47, color=ORANGE)
    text(d, 450, 160, "created in order", size=7.8, color=MUTED)
    text(d, 450, 149, "0 -> 1 -> 2", size=7.8, color=MUTED)
    return d


def scheduling():
    d = drawing(196)
    box(d, 175, 152, 165, 38, ["kube-scheduler", "filter nodes -> score -> bind"], fill=BLUE_BG, stroke=BLUE)
    nodes = [("node-1", "label disk=ssd", GREEN, ["db (nodeSelector", "disk=ssd)"]),
             ("node-2", "no labels, no taints", BLUE, ["web", "web"]),
             ("node-3", "taint gpu=true:NoSchedule", RED, ["ml-job (tolerates", "gpu taint)"])]
    for i, (name, lab, col, pods) in enumerate(nodes):
        x = 6 + i * 172
        frame(d, x, 8, 160, 116, name, fill=WHITE, stroke=col, title_color=col)
        text(d, x + 80, 96, lab, size=7.8, color=col)
        if i == 1:
            pod_icon(d, x + 12, 40, w=62, h=34, label="web", fill=BLUE_BG, stroke=BLUE)
            pod_icon(d, x + 86, 40, w=62, h=34, label="web", fill=BLUE_BG, stroke=BLUE)
        else:
            box(d, x + 15, 40, 130, 36, pods, fill=GREEN_BG if i == 0 else RED_BG, stroke=col,
                size=8, bold_first=False)
        arrow(d, 257, 152, x + 80, 125, color=col)
    text(d, 438, 18, "web pods are kept out", size=7.5, color=RED)
    return d


def workloads():
    d = drawing(160)
    frame(d, 0, 0, 255, 156, "DaemonSet  -  one pod on every node", fill=TEAL_BG, stroke=TEAL,
          title_color=TEAL)
    for i in range(3):
        x = 10 + i * 82
        frame(d, x, 10, 74, 118, f"node-{i + 1}", fill=WHITE, stroke=MUTED, title_size=8)
        pod_icon(d, x + 6, 70, w=62, h=22, label="app pod", fill=BLUE_BG, stroke=BLUE, size=7)
        pod_icon(d, x + 6, 18, w=62, h=24, label="log-agent", fill=GOLD_BG, stroke=ORANGE, size=7)
    frame(d, 265, 0, 250, 156, "CronJob -> Job -> Pod", fill=PURPLE_BG, stroke=PURPLE,
          title_color=PURPLE)
    box(d, 290, 100, 200, 34, ["CronJob: nightly-report", "schedule \"0 2 * * *\""], fill=WHITE, stroke=PURPLE,
        size=8.5)
    box(d, 290, 54, 200, 30, ["Job: nightly-report-2891", "retries until success"], fill=WHITE,
        stroke=PURPLE, size=8.5)
    box(d, 290, 10, 200, 30, ["Pod: runs once, then Completed"], fill=GREEN_BG, stroke=GREEN, size=8.5)
    arrow(d, 390, 100, 390, 85, color=PURPLE)
    arrow(d, 390, 54, 390, 41, color=PURPLE)
    text(d, 398, 89, "every night 2 AM", size=7.2, color=PURPLE, anchor="start")
    return d


def resources():
    d = drawing(150)
    frame(d, 0, 0, 515, 146, "NODE  -  4 CPU, 8Gi memory allocatable", fill=GREY_BG, stroke=NAVY)
    specs = [("Guaranteed", "requests = limits", "500m / 500m", GREEN_BG, GREEN),
             ("Burstable", "requests < limits", "250m -> 1 CPU", GOLD_BG, ORANGE),
             ("BestEffort", "no requests/limits", "first to be evicted", RED_BG, RED)]
    for i, (q, rule, eg, bg, st) in enumerate(specs):
        x = 14 + i * 168
        box(d, x, 52, 152, 62, [f"QoS: {q}", rule, eg], fill=bg, stroke=st)
    text(d, 257, 30, "request = what the scheduler reserves  ·  limit = the hard ceiling", size=8.5,
         color=NAVY, bold=True)
    text(d, 257, 14, "over the CPU limit -> slowed down (throttled)  ·  over the memory limit -> OOMKilled",
         size=8, color=MUTED)
    return d


def probes():
    d = drawing(168)
    box(d, 5, 62, 92, 44, ["kubelet", "the checker"], fill=GOLD_BG, stroke=ORANGE)
    rows = [("startupProbe", "finished booting? waits first", BLUE),
            ("livenessProbe", "stuck? -> restart container", RED),
            ("readinessProbe", "ready? -> receive traffic", GREEN)]
    for i, (t, s, col) in enumerate(rows):
        y = 116 - i * 52
        box(d, 140, y, 170, 42, [t, s], fill=WHITE, stroke=col, size=9)
        arrow(d, 97, 84, 139, y + 21, color=col)
        arrow(d, 310, y + 21, 349, 92 if i == 0 else (84 if i == 1 else 76), color=col)
    box(d, 350, 62, 75, 44, ["Pod", "web-1"], fill=BLUE_BG, stroke=BLUE)
    box(d, 440, 4, 72, 40, ["Service", "routes traffic"], fill=TEAL_BG, stroke=TEAL, size=8.5)
    arrow(d, 476, 44, 410, 61, color=TEAL, dashed=True)
    text(d, 470, 66, "only when", size=7.5, color=TEAL, anchor="start")
    text(d, 470, 56, "Ready", size=7.5, color=TEAL, anchor="start")
    return d


def hpa():
    d = drawing(160)
    box(d, 5, 102, 120, 46, ["metrics-server", "CPU / memory per pod"], fill=GOLD_BG, stroke=ORANGE)
    box(d, 168, 102, 160, 46, ["HorizontalPodAutoscaler", "target CPU 50% · min 2 · max 10"],
        fill=BLUE_BG, stroke=BLUE, size=8.5)
    box(d, 370, 102, 142, 46, ["Deployment php-apache", "replicas 2 -> 5"], fill=WHITE, stroke=NAVY,
        size=8.5)
    arrow(d, 125, 125, 167, 125, label="reads", label_dy=5)
    arrow(d, 328, 125, 369, 125, label="scales", label_dy=5)
    for k in range(5):
        old = k < 2
        pod_icon(d, 268 + k * 49, 22, w=44, h=30, label="pod" if old else "new",
                 fill=BLUE_BG if old else GREEN_BG, stroke=BLUE if old else GREEN)
    arrow(d, 440, 102, 440, 53, color=GREEN)
    arrow(d, 266, 37, 65, 101, color=ORANGE, dashed=True, label="kubelet reports usage", label_dx=-30,
          label_dy=-6)
    text(d, 10, 30, "load up -> CPU 90% -> add pods", size=8, color=GREEN, anchor="start")
    text(d, 10, 16, "load down -> wait ~5 min -> remove pods", size=8, color=MUTED, anchor="start")
    return d


def rbac():
    d = drawing(140)
    for x, lab in ((70, "WHO"), (257, "LINK"), (446, "WHAT")):
        text(d, x, 118, lab, size=10, bold=True, color=NAVY)
    box(d, 5, 54, 130, 52, ["ServiceAccount: viewer", "or a User / Group", "namespace dev"],
        fill=GOLD_BG, stroke=ORANGE, size=8.5)
    box(d, 190, 54, 135, 52, ["RoleBinding", "viewer -> pod-reader", "namespace dev"],
        fill=BLUE_BG, stroke=BLUE, size=8.5)
    box(d, 380, 54, 132, 52, ["Role: pod-reader", "verbs: get, list, watch", "resources: pods"],
        fill=GREEN_BG, stroke=GREEN, size=8.5)
    arrow(d, 189, 80, 136, 80)
    arrow(d, 325, 80, 379, 80)
    text(d, 257, 26, "ClusterRole + ClusterRoleBinding = the same idea for the whole cluster",
         size=8.5, color=MUTED)
    text(d, 257, 10, "Default is DENY - you only get what a binding gives you", size=8.5,
         color=RED, bold=True)
    return d


def netpol():
    d = drawing(150)
    frame(d, 160, 4, 352, 140, "namespace: shop   (NetworkPolicy active)", fill=GREY_BG,
          stroke=MUTED)
    box(d, 175, 76, 100, 40, ["frontend", "app=frontend"], fill=BLUE_BG, stroke=BLUE)
    box(d, 300, 76, 92, 40, ["backend", "app=backend"], fill=BLUE_BG, stroke=BLUE)
    box(d, 415, 76, 88, 40, ["mysql", "app=db"], fill=BLUE_BG, stroke=BLUE)
    arrow(d, 275, 96, 299, 96, color=GREEN)
    arrow(d, 392, 96, 414, 96, color=GREEN)
    text(d, 500, 14, "green = allowed by policy", size=7.8, color=GREEN, anchor="end")
    box(d, 5, 18, 120, 40, ["random pod", "other namespace"], fill=RED_BG, stroke=RED)
    arrow(d, 125, 38, 412, 80, color=RED, dashed=True)
    text(d, 300, 40, "X  blocked", size=9, color=RED, bold=True)
    box(d, 5, 86, 120, 40, ["Internet", "via Ingress"], fill=GOLD_BG, stroke=ORANGE)
    arrow(d, 125, 106, 174, 100, color=GREEN)
    return d


def helm():
    d = drawing(150)
    frame(d, 2, 6, 160, 138, "CHART: quickbite", fill=GOLD_BG, stroke=ORANGE, title_color=ORANGE)
    box(d, 14, 92, 136, 26, ["Chart.yaml  (name, version)"], fill=WHITE, stroke=ORANGE, size=7.8,
        bold_first=False)
    box(d, 14, 56, 136, 26, ["values.yaml  (replicas: 2)"], fill=WHITE, stroke=ORANGE, size=7.8,
        bold_first=False)
    box(d, 14, 18, 136, 28, ["templates/  (YAML with", "{{ .Values.replicas }})"], fill=WHITE,
        stroke=ORANGE, size=7.8, bold_first=False, sub_color=INK)
    box(d, 195, 54, 118, 48, ["helm upgrade", "--set replicas=4", "renders final YAML"],
        fill=BLUE_BG, stroke=BLUE, size=8.5)
    arrow(d, 162, 78, 194, 78)
    frame(d, 345, 6, 168, 138, "CLUSTER - release \"shop\"", fill=GREEN_BG, stroke=GREEN,
          title_color=GREEN)
    box(d, 358, 86, 142, 30, ["revision 1  (2 replicas)"], fill=WHITE, stroke=MUTED, size=8,
        bold_first=False)
    box(d, 358, 40, 142, 30, ["revision 2  (4 replicas)"], fill=WHITE, stroke=GREEN, size=8)
    arrow(d, 313, 78, 357, 56)
    arrow(d, 480, 70, 480, 85, color=RED, dashed=True)
    text(d, 470, 22, "helm rollback shop 1", size=7.8, color=RED, anchor="end")
    return d


def gitops():
    d = drawing(150)
    steps = [("Developer", "git push code"), ("CI pipeline", "test + build image"),
             ("Registry", "app:1.4.2 stored"), ("Config repo", "image tag bumped"),
             ("Argo CD", "detects change"), ("Cluster", "synced to Git")]
    for i, (t, s) in enumerate(steps):
        x = 4 + i * 86
        fill = GREEN_BG if i == 5 else (PURPLE_BG if i == 4 else WHITE)
        box(d, x, 62, 78, 48, [t, s], fill=fill, stroke=PURPLE if i == 4 else BLUE, size=8.5)
        badge(d, x + 4, 110, i + 1)
        if i < 5:
            arrow(d, x + 78, 86, x + 85, 86, width=1.1)
    d.add(Line(476, 62, 476, 34, strokeColor=PURPLE, strokeWidth=1.1, strokeDashArray=[4, 3]))
    d.add(Line(476, 34, 390, 34, strokeColor=PURPLE, strokeWidth=1.1, strokeDashArray=[4, 3]))
    arrow(d, 390, 34, 390, 61, color=PURPLE, dashed=True)
    text(d, 433, 20, "Argo CD keeps watching: manual changes get reverted", size=7.8,
         color=PURPLE)
    text(d, 130, 34, "Git is the single source of truth", size=9, color=NAVY, bold=True)
    return d


def troubleshoot():
    d = drawing(200)
    box(d, 180, 160, 155, 34, ["Pod not working?", "kubectl get pods"], fill=GOLD_BG, stroke=ORANGE)
    rows = [("Pending", "describe pod -> Events", "no CPU/memory, PVC, taint"),
            ("ImagePullBackOff", "describe pod", "wrong image name / tag / auth"),
            ("CrashLoopBackOff", "logs --previous", "app error, bad config, command"),
            ("Running, no traffic", "get endpoints", "selector / port / readiness")]
    for i, (st, cmd, cause) in enumerate(rows):
        x = 4 + i * 128
        box(d, x, 88, 122, 36, [st, cmd], fill=WHITE, stroke=RED if i < 3 else BLUE, size=8.5)
        box(d, x, 22, 122, 40, ["Usual cause", cause], fill=GREY_BG, stroke=MUTED, size=8,
            sub_color=INK)
        arrow(d, 257, 160, x + 61, 125, color=NAVY, width=1)
        arrow(d, x + 61, 88, x + 61, 63, color=MUTED, width=1)
    text(d, 257, 6, "Golden order: get -> describe -> logs -> events -> exec", size=8.5, color=NAVY,
         bold=True)
    return d


def _steps_row(steps, h=130, highlight=None):
    d = drawing(h)
    n = len(steps)
    gapw = 8
    w = (512 - (n - 1) * gapw) / n
    for i, (t, s) in enumerate(steps):
        x = 2 + i * (w + gapw)
        last = i == n - 1
        box(d, x, h - 72, w, 52, [t] + (s if isinstance(s, list) else [s]),
            fill=GREEN_BG if last else (PURPLE_BG if i == highlight else WHITE),
            stroke=GREEN if last else BLUE, size=8.5)
        badge(d, x + 4, h - 20, i + 1)
        if not last:
            arrow(d, x + w, h - 46, x + w + gapw, h - 46, width=1.1)
    return d


def helm_flow():
    d = drawing(176)
    box(d, 5, 112, 120, 48, ["Chart templates", "templates/*.yaml"], fill=GOLD_BG, stroke=ORANGE)
    box(d, 5, 46, 120, 52, ["Values", "values.yaml", "+ -f file + --set"], fill=GOLD_BG, stroke=ORANGE)
    box(d, 160, 76, 120, 54, ["Template engine", "Go templates", "+ Sprig functions"], fill=BLUE_BG,
        stroke=BLUE)
    box(d, 315, 76, 95, 54, ["Plain YAML", "Deployment, Service", "Ingress, HPA ..."], fill=WHITE,
        stroke=NAVY, size=8.5)
    box(d, 440, 76, 72, 54, ["API server", "objects", "created"], fill=GREEN_BG, stroke=GREEN, size=8.5)
    arrow(d, 125, 136, 159, 112)
    arrow(d, 125, 72, 159, 94)
    arrow(d, 280, 103, 314, 103, label="render", label_dy=5)
    arrow(d, 410, 103, 439, 103, label="apply", label_dy=5)
    box(d, 300, 8, 212, 40, ["Release record (a Secret in the namespace)",
                             "sh.helm.release.v1.shop.v2 - used for rollback"],
        fill=PURPLE_BG, stroke=PURPLE, size=8.2)
    arrow(d, 362, 76, 362, 49, color=PURPLE, dashed=True, label="stores", label_dx=18, label_dy=0)
    text(d, 85, 20, "helm template = render only", size=7.8, color=MUTED)
    text(d, 85, 8, "helm install / upgrade = render + apply", size=7.8, color=MUTED)
    return d


def values_precedence():
    d = drawing(176)
    layers = [("1. values.yaml inside the chart", "defaults - replicaCount: 1", GREY_BG, MUTED),
              ("2. Parent chart values for a subchart", "mysql.auth.database: shop", BLUE_BG, BLUE),
              ("3. -f values-prod.yaml (later files win)", "replicaCount: 3", GOLD_BG, ORANGE),
              ("4. --set replicaCount=5", "highest priority", GREEN_BG, GREEN)]
    for i, (t, s, bg, st) in enumerate(layers):
        y = 8 + i * 40
        box(d, 20 + i * 14, y, 380 - i * 28, 32, [t, s], fill=bg, stroke=st, size=8.5)
    arrow(d, 440, 10, 440, 160, color=GREEN, width=2)
    text(d, 452, 150, "wins", size=9, bold=True, color=GREEN, anchor="start")
    text(d, 452, 18, "overridden", size=8, color=MUTED, anchor="start")
    text(d, 478, 84, "final:", size=8, color=NAVY, bold=True)
    text(d, 478, 72, "replicas 5", size=8, color=NAVY)
    return d


def kustomize():
    d = drawing(170)
    frame(d, 2, 6, 158, 158, "base/", fill=GOLD_BG, stroke=ORANGE, title_color=ORANGE)
    for i, f in enumerate(["deployment.yaml", "service.yaml", "kustomization.yaml"]):
        box(d, 14, 106 - i * 38, 134, 28, [f], fill=WHITE, stroke=ORANGE, size=8, bold_first=False)
    frame(d, 200, 92, 160, 72, "overlays/dev", fill=BLUE_BG, stroke=BLUE, title_color=BLUE_DARK)
    text(d, 280, 120, "replicas: 1", size=8, color=INK)
    text(d, 280, 106, "image tag: dev-42", size=8, color=INK)
    frame(d, 200, 6, 160, 72, "overlays/prod", fill=GREEN_BG, stroke=GREEN, title_color=GREEN)
    text(d, 280, 34, "replicas: 5  +  HPA patch", size=8, color=INK)
    text(d, 280, 20, "image tag: 1.4.2", size=8, color=INK)
    arrow(d, 160, 110, 199, 128)
    arrow(d, 160, 60, 199, 42)
    box(d, 395, 52, 117, 64, ["kubectl apply -k", "overlays/prod", "= base + patches"],
        fill=WHITE, stroke=NAVY, size=8.5)
    arrow(d, 360, 128, 394, 100, color=MUTED, dashed=True)
    arrow(d, 360, 42, 394, 70, color=GREEN)
    return d


def kubeadm_flow():
    return _steps_row([
        ("Prepare nodes", ["swap off, kernel", "modules, containerd"]),
        ("Install tools", ["kubeadm, kubelet,", "kubectl (same ver.)"]),
        ("kubeadm init", ["on control plane:", "certs, etcd, API"]),
        ("Install CNI", ["Calico / Cilium -", "nodes turn Ready"]),
        ("kubeadm join", ["on each worker", "with token + hash"]),
        ("Verify", ["kubectl get nodes", "all Ready"]),
    ], h=84, highlight=2)


def operator():
    d = drawing(168)
    box(d, 5, 100, 150, 54, ["Custom resource", "kind: PostgresCluster", "replicas: 3, backup: daily"],
        fill=GOLD_BG, stroke=ORANGE, size=8.5)
    box(d, 5, 18, 150, 50, ["CRD", "teaches the API server", "the new kind"], fill=GREY_BG,
        stroke=MUTED, size=8.5)
    arrow(d, 80, 68, 80, 99, color=MUTED, dashed=True, label="defines", label_dx=22, label_dy=-2)
    box(d, 195, 100, 140, 54, ["Operator (controller)", "watches the custom resource", "reconciles forever"],
        fill=PURPLE_BG, stroke=PURPLE, size=8.5)
    arrow(d, 155, 127, 194, 127, label="watch", label_dy=5)
    text(d, 265, 80, "automates: failover,", size=7.8, color=PURPLE)
    text(d, 265, 68, "backups, upgrades, scaling", size=7.8, color=PURPLE)
    frame(d, 370, 6, 142, 156, "Creates and manages", fill=GREEN_BG, stroke=GREEN, title_color=GREEN)
    for i, r in enumerate(["StatefulSet", "Services", "Secrets", "CronJob (backup)"]):
        box(d, 382, 112 - i * 32, 118, 24, [r], fill=WHITE, stroke=GREEN, size=8)
    arrow(d, 335, 127, 369, 127, color=GREEN)
    return d
