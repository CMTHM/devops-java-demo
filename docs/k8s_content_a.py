"""Front matter and Classes 1-5 of the Kubernetes course."""
import k8s_diagrams as D
from k8s_pdf_lib import *


# ====================================================================== FRONT MATTER
def front_matter():
    s = [Bookmark("intro", "Welcome and how to use these notes")]
    s.append(P("Welcome to Kubernetes", "h1"))
    s.append(P("Docker taught you how to pack an application into a container. That is great for one "
               "laptop. But real companies run hundreds of containers on dozens of servers, and "
               "they need someone to start them, restart them when they crash, spread them across "
               "machines, give them stable addresses, and update them without downtime. "
               "<b>Kubernetes</b> is that someone."))
    s.append(P("These notes go with eleven live classes of 60-90 minutes each. Every class has the same shape:"))
    s += bullets([
        "<b>A story</b> - what problem Ravi faced at QuickBite that day.",
        "<b>Concepts with everyday examples</b> - restaurants, offices, malls, trains.",
        "<b>Diagrams</b> - what happens inside the cluster.",
        "<b>Live lab</b> - commands you type on your own laptop, with the output you should expect.",
        "<b>Common mistakes and a recap</b>.",
        "<b>20 interview questions with model answers</b>.",
    ])
    s.append(story("Ravi joined <b>QuickBite</b>, a food-delivery start-up, as a fresher DevOps engineer. "
                   "QuickBite already ships its apps as Docker containers - a menu service, an orders "
                   "service, a payment service and a MySQL database. On his first Friday night sale, "
                   "the orders container crashed at 9 PM and nobody noticed for 40 minutes. "
                   "His manager said: \"Next month we move to Kubernetes. You are going to learn it.\" "
                   "Follow Ravi through these eleven classes."))
    s.append(P("Course map", "h2"))
    s += table(["Class", "Topic", "Main concepts"], [
        ["1", "Why Kubernetes and its architecture", "orchestration, control plane, nodes, desired state, minikube"],
        ["2", "Pods, YAML and kubectl", "pod, multi-container, init containers, labels, selectors, annotations"],
        ["3", "ReplicaSets and Deployments", "self-healing, scaling, rolling update, rollback, blue-green, canary"],
        ["4", "Services and cluster networking", "ClusterIP, NodePort, LoadBalancer, DNS, kube-proxy, CNI"],
        ["5", "Ingress, Gateway API and Namespaces", "host/path routing, TLS, namespaces, quotas, contexts"],
        ["6", "ConfigMaps and Secrets", "env, envFrom, volumes, base64, immutable, Downward API"],
        ["7", "Storage and StatefulSets", "volumes, PV, PVC, StorageClass, access modes, StatefulSet"],
        ["8", "Workloads and scheduling", "DaemonSet, Job, CronJob, affinity, taints, requests/limits, QoS"],
        ["9", "Health, scaling and troubleshooting", "probes, HPA, VPA, PDB, metrics, logs, debugging"],
        ["10", "Security, GitOps and production", "RBAC, NetworkPolicy, securityContext, Argo CD, managed K8s"],
        ["11", "Helm charts, Kustomize and cluster essentials", "charts, templates, values, hooks, Kustomize, CRDs, kubeadm, etcd backup"],
    ], cols(0.09, 0.36, 0.55))
    s.append(P("Set up your lab before Class 1", "h2"))
    s.append(P("You need Docker Desktop (from the Docker course) and about 8 GB of free RAM. "
               "We use <b>minikube</b>, which runs a real Kubernetes cluster inside a Docker container "
               "on your laptop. Open PowerShell as Administrator:"))
    s.append(code("""winget install Kubernetes.kubectl
winget install Kubernetes.minikube
winget install Helm.Helm

# close and reopen PowerShell, then:
kubectl version --client
minikube version
minikube start --driver=docker --cpus=2 --memory=4096
kubectl get nodes""", "PowerShell - one-time setup"))
    s.append(P("Expected output of the last command:"))
    s.append(code("""NAME       STATUS   ROLES           AGE   VERSION
minikube   Ready    control-plane   45s   v1.3x.x"""))
    s.append(tryit(["Stop the cluster at the end of each class with `minikube stop`; start it again with "
                    "`minikube start`. Your work is kept.",
                    "If things get badly broken, `minikube delete` and then `minikube start` gives you a "
                    "fresh cluster in two minutes.",
                    "Linux and Mac users: install the same tools with your package manager; every "
                    "kubectl command in these notes is identical."], "Lab tips"))
    s.append(P("How to read the notes", "h2"))
    s += table(["Box", "Meaning"], [
        ["Purple - Ravi's story", "The real-world problem behind the topic."],
        ["Gold - Everyday example", "A non-technical comparison to make the idea stick."],
        ["Green - Try it yourself", "Something extra to type and observe."],
        ["Red - Common mistake", "What freshers get wrong in labs and interviews."],
        ["Teal - Did you know?", "A fun fact or bit of history."],
        ["Blue - Remember", "The short summary you should memorise."],
    ], cols(0.32, 0.68))
    return s


# ====================================================================== CLASS 1
def day1():
    s = day_banner(1, "Why Kubernetes? Architecture and how it works inside",
                   "By the end you can explain why companies use Kubernetes, name every component "
                   "of a cluster, and run your own cluster on your laptop.")
    s += covers([
        "The problem with running containers by hand",
        "What container orchestration means, and where Kubernetes came from",
        "Advantages and disadvantages of Kubernetes",
        "Control plane and worker node components - what each one does",
        "Desired state and the reconciliation (control) loop",
        "What happens step by step when you run `kubectl apply`",
        "Lab: start minikube, explore the cluster, watch self-healing",
    ], [["1", "Story and the problem with plain Docker", "10 min"],
        ["2", "Orchestration, history, pros and cons", "15 min"],
        ["3", "Architecture and the apply flow", "25 min"],
        ["4", "Live lab", "25 min"],
        ["5", "Recap and interview questions", "10 min"]])
    s.append(P("1.1 The problem: containers without a manager", "h1"))
    s.append(story("QuickBite runs 12 containers on 3 servers using `docker run`. On Friday night the "
                   "orders container ran out of memory and died. Docker did not move it anywhere, nobody "
                   "was paged, and customers saw \"Something went wrong\" for 40 minutes. Then traffic "
                   "tripled and Ravi had to SSH into each server and start more containers by hand. "
                   "On Monday a new release needed to go out - he stopped the old containers and started "
                   "new ones, causing 3 minutes of downtime."))
    s.append(P("Plain Docker is excellent at running a container on <b>one</b> machine. As soon as you have "
               "many machines and many containers, you need answers to these questions:"))
    s += table(["Question", "With plain Docker", "With Kubernetes"], [
        ["A container crashes at 2 AM. Who restarts it?", "You, after you wake up", "Kubernetes, within seconds"],
        ["A whole server dies. What happens to its containers?", "They are gone until you recreate them",
         "They are recreated on healthy servers"],
        ["Traffic triples. How do we add copies?", "SSH and docker run, one by one",
         "`kubectl scale` or automatic autoscaling"],
        ["Which server has free CPU for a new container?", "You check manually", "The scheduler decides"],
        ["How do containers find each other when IPs change?", "Hard-coded IPs, links", "Services with stable DNS names"],
        ["How do we release a new version?", "Stop old, start new (downtime)", "Rolling update, zero downtime"],
        ["Where do passwords and config live?", "Env files on each server", "ConfigMaps and Secrets"],
    ], cols(0.38, 0.30, 0.32))
    s.append(P("1.2 What is container orchestration?", "h1"))
    s.append(P("<b>Orchestration</b> means automatically deploying, scaling, networking, healing and "
               "updating containers across a group of machines. You describe <i>what</i> you want "
               "(\"3 copies of the orders app, version 2.1, reachable on port 80\") and the orchestrator "
               "figures out <i>how</i> to make it happen and keeps it that way."))
    s.append(real("Think of a large restaurant chain. The <b>head office</b> does not cook. It decides how "
                  "many cooks each branch needs, replaces a cook who calls in sick, opens extra counters "
                  "on festival days, and rolls out the new menu branch by branch so no branch is ever "
                  "closed. Kubernetes is the head office; your servers are the branches; containers are "
                  "the cooks."))
    s.append(P("The name <b>Kubernetes</b> is Greek for <i>helmsman</i> - the person who steers a ship. "
               "That is why the logo is a ship's wheel. People shorten it to <b>K8s</b> "
               "(K, then 8 letters, then s)."))
    s.append(funfact("Google ran its own internal orchestrator called <b>Borg</b> for over a decade, "
                     "launching billions of containers a week. In 2014 Google open-sourced a fresh "
                     "system built on those lessons: Kubernetes. In 2015 it was donated to the Cloud "
                     "Native Computing Foundation (CNCF). Today every major cloud offers it: Amazon EKS, "
                     "Azure AKS and Google GKE."))
    s.append(P("Other orchestrators exist - Docker Swarm, HashiCorp Nomad, Amazon ECS - but Kubernetes "
               "has become the industry standard, which is why it appears in almost every DevOps job "
               "description."))
    s.append(P("1.3 Advantages and disadvantages", "h1"))
    s += table(["Advantage", "What it means in real life"], [
        ["Self-healing", "Crashed containers restart; pods on a dead node are recreated elsewhere."],
        ["Horizontal scaling", "Go from 3 to 30 copies with one command, or automatically on CPU load."],
        ["Zero-downtime releases", "Rolling updates replace pods gradually; one-command rollback."],
        ["Service discovery and load balancing", "Apps call each other by name; traffic is spread across copies."],
        ["Declarative configuration", "Everything is YAML in Git - reviewable, repeatable, auditable."],
        ["Efficient use of servers", "The scheduler packs containers onto nodes based on CPU and memory."],
        ["Portable", "The same YAML runs on a laptop, on-premises, on AWS, Azure or GCP."],
        ["Huge ecosystem", "Helm, Argo CD, Prometheus, Istio and thousands of CNCF tools."],
    ], cols(0.32, 0.68))
    s += table(["Disadvantage", "Why it matters"], [
        ["Steep learning curve", "Many new objects and ideas; that is why this course has eleven classes."],
        ["Operational complexity", "Upgrades, networking, storage and security need skilled people."],
        ["Overkill for small apps", "A single website on one server does not need a cluster."],
        ["Resource overhead", "The control plane and agents use CPU and memory themselves."],
        ["Cost if misconfigured", "Over-sized requests or forgotten load balancers waste cloud money."],
        ["Debugging has more layers", "A failure could be in the app, pod, node, network or config."],
    ], cols(0.32, 0.68))
    s.append(remember("Use Kubernetes when you have many services, need high availability, scale often, "
                      "or release frequently. For one small app, plain Docker or a PaaS is simpler."))
    s.append(P("1.4 Kubernetes architecture", "h1"))
    s.append(P("A Kubernetes <b>cluster</b> is a group of machines (called <b>nodes</b>) split into two roles:"))
    s += bullets([
        "<b>Control plane</b> - the brain. It stores the desired state, makes decisions and exposes the API. "
        "In production there are usually 3 control-plane nodes for high availability.",
        "<b>Worker nodes</b> - the muscle. They actually run your containers.",
    ])
    s.append(figure(D.architecture(), "Figure 1.1 - Kubernetes architecture: one control plane managing worker nodes"))
    s.append(P("Control plane components", "h2"))
    s += table(["Component", "Job", "Everyday example"], [
        ["kube-apiserver", "The only entry point. Validates every request (from kubectl, nodes, controllers) "
         "and reads/writes etcd.", "The reception desk - nobody walks into the office without passing it."],
        ["etcd", "A distributed key-value database that stores the whole cluster state: every pod, "
         "service, secret and config.", "The master register book of the head office."],
        ["kube-scheduler", "Watches for new pods with no node and picks the best node based on "
         "resources, rules and affinity.", "HR deciding which branch a new cook joins."],
        ["kube-controller-manager", "Runs many controllers (Deployment, ReplicaSet, Node, Job...) that "
         "keep actual state equal to desired state.", "Supervisors who keep checking each counter is staffed."],
        ["cloud-controller-manager", "Talks to the cloud provider: creates load balancers, attaches "
         "disks, notices deleted VMs.", "The office admin who deals with the landlord."],
    ], cols(0.24, 0.44, 0.32))
    s.append(P("Worker node components", "h2"))
    s += table(["Component", "Job", "Everyday example"], [
        ["kubelet", "Agent on every node. Receives pod specs from the API server, asks the runtime to "
         "start containers, runs health checks, reports status.", "The branch manager who reports to head office."],
        ["kube-proxy", "Programs network rules (iptables/IPVS) so traffic to a Service reaches the right pods.",
         "The telephone operator forwarding calls to the right desk."],
        ["Container runtime", "Actually runs containers. Usually containerd or CRI-O, talking to the kubelet "
         "through the Container Runtime Interface (CRI).", "The kitchen equipment the cooks use."],
        ["CNI plugin", "Gives every pod an IP and connects pods across nodes (Calico, Flannel, Cilium).",
         "The internal phone lines between branches."],
    ], cols(0.24, 0.44, 0.32))
    s.append(funfact("Kubernetes stopped using Docker Engine as its runtime (\"dockershim\" was removed "
                     "in v1.24). Do not panic - images built with Docker still run perfectly, because "
                     "they follow the OCI image standard, and containerd runs them directly."))
    s.append(P("1.5 Desired state and the control loop", "h1"))
    s.append(P("This is the single most important idea in Kubernetes. You never say \"start a container\". "
               "You say \"I want 3 copies running\" - the <b>desired state</b>. Controllers then run a "
               "never-ending loop: observe what is actually running, compare it with what you asked for, "
               "and act to remove the difference. This is called <b>reconciliation</b>."))
    s.append(figure(D.reconcile(), "Figure 1.2 - The reconciliation loop that powers self-healing"))
    s.append(real("An air conditioner works the same way. You set 24 degrees (desired state). The "
                  "thermostat keeps measuring the room (actual state). If it is 27, it cools; if it is 22, "
                  "it stops. You never tell it \"run the compressor for 10 minutes\" - you only declare "
                  "the target."))
    s.append(P("1.6 What happens when you run kubectl apply", "h1"))
    s.append(figure(D.apply_flow(), "Figure 1.3 - The journey of a Deployment from YAML to running containers"))
    s += bullets([
        "<b>1-2.</b> kubectl sends your YAML to the API server over HTTPS. The API server checks who you "
        "are (authentication), whether you are allowed (authorization/RBAC) and runs admission checks.",
        "<b>3.</b> The object is saved in etcd. Nothing is running yet - only the wish is recorded.",
        "<b>4.</b> The Deployment controller notices the new Deployment and creates a ReplicaSet, which "
        "creates Pod objects.",
        "<b>5.</b> The scheduler sees pods without a node and writes a node name into each one.",
        "<b>6-7.</b> The kubelet on that node sees a pod assigned to it and tells containerd to pull the "
        "image and start the containers.",
        "<b>8.</b> The kubelet reports status back; `kubectl get pods` shows Running.",
    ])
    s.append(remember("Components never talk to each other directly - they all watch the API server. "
                      "This loose coupling is why Kubernetes is so robust."))
    s.append(P("1.7 Live lab: your first cluster", "h1"))
    s.append(P("Step 1 - Start and inspect the cluster", "h2"))
    s.append(code("""minikube start --driver=docker
kubectl cluster-info
kubectl get nodes -o wide
kubectl get pods -n kube-system""", "PowerShell"))
    s.append(P("In `kube-system` you will see the control-plane components running as pods:"))
    s.append(code("""NAME                               READY   STATUS    RESTARTS   AGE
coredns-7c65d6cfc9-x2b8l           1/1     Running   0          2m
etcd-minikube                      1/1     Running   0          2m
kube-apiserver-minikube            1/1     Running   0          2m
kube-controller-manager-minikube   1/1     Running   0          2m
kube-proxy-9fk2s                   1/1     Running   0          2m
kube-scheduler-minikube            1/1     Running   0          2m
storage-provisioner                1/1     Running   0          2m"""))
    s.append(P("Step 2 - Run an app and watch self-healing", "h2"))
    s.append(code("""kubectl create deployment hello --image=nginx:1.27 --replicas=3
kubectl get pods -o wide

# open a second PowerShell window and keep this running:
kubectl get pods -w

# back in the first window, delete one pod:
kubectl delete pod <name-of-any-hello-pod>""", "PowerShell"))
    s.append(P("In the watch window you will see the deleted pod go to <b>Terminating</b> and a brand-new "
               "pod with a different name appear within seconds. You asked for 3; Kubernetes keeps 3."))
    s.append(P("Step 3 - Scale and clean up", "h2"))
    s.append(code("""kubectl scale deployment hello --replicas=5
kubectl get pods
kubectl delete deployment hello
minikube dashboard        # opens a web UI in your browser (Ctrl+C to stop)""", "PowerShell"))
    s.append(tryit(["Run `kubectl api-resources` to see every object type Kubernetes knows about.",
                    "Run `kubectl get events --sort-by=.metadata.creationTimestamp` after the self-healing "
                    "demo and read the story the cluster tells.",
                    "Run `minikube ssh` and then `sudo crictl ps` to see the real containers behind your pods."]))
    s.append(mistake(["Saying \"Kubernetes runs Docker containers\". It runs <b>OCI containers</b> through a "
                      "CRI runtime such as containerd.",
                      "Thinking the control plane runs your apps. In production, app pods run on worker nodes.",
                      "Forgetting that etcd holds everything - losing etcd without a backup means losing the cluster state."]))
    s.append(remember(["Kubernetes = an orchestrator that keeps the desired state you declare.",
                       "Control plane: apiserver, etcd, scheduler, controller-manager, cloud-controller-manager.",
                       "Every node: kubelet, kube-proxy, container runtime, CNI.",
                       "Everything goes through the API server; controllers reconcile in a loop."], "Class 1 recap"))
    s += interview(1, DAY1_QA)
    return s


DAY1_QA = [
    ("What is Kubernetes?",
     "An open-source container orchestration platform that automates deploying, scaling, healing, "
     "networking and updating containerized applications across a cluster of machines. You declare the "
     "desired state in YAML and Kubernetes keeps the actual state matching it."),
    ("Why do we need Kubernetes when we already have Docker?",
     "Docker runs containers on a single host. Kubernetes manages containers across many hosts: it "
     "restarts failed containers, reschedules them when a node dies, scales them, load-balances traffic, "
     "and performs rolling updates. Docker builds and runs images; Kubernetes orchestrates them."),
    ("What is container orchestration?",
     "Automatic management of the container lifecycle across many machines - placement (scheduling), "
     "scaling, health monitoring and restarts, networking and service discovery, configuration, and "
     "rolling updates."),
    ("Explain the Kubernetes architecture.",
     "A cluster has a control plane and worker nodes. The control plane runs kube-apiserver, etcd, "
     "kube-scheduler, kube-controller-manager and optionally cloud-controller-manager. Each worker node "
     "runs kubelet, kube-proxy, a container runtime and a CNI plugin. All components communicate through "
     "the API server."),
    ("What does the kube-apiserver do?",
     "It is the front end of the control plane and the only component that talks to etcd. It exposes the "
     "REST API, authenticates and authorizes requests, runs admission controllers, validates objects, and "
     "lets other components watch for changes."),
    ("What is etcd and why is it critical?",
     "etcd is a consistent, distributed key-value store holding the entire cluster state - all objects, "
     "configs and secrets. If etcd is lost without a backup the cluster state is lost, so it is run in odd "
     "numbers (3 or 5) for quorum and backed up regularly with `etcdctl snapshot save`."),
    ("What does the kube-scheduler do?",
     "It watches for pods with no assigned node and selects a node in two phases: filtering (nodes that "
     "have enough resources and satisfy rules like nodeSelector, taints and affinity) and scoring (ranking "
     "the remaining nodes). It then binds the pod to the best node. It does not start containers."),
    ("What is the kube-controller-manager?",
     "A single process running many controllers such as the Deployment, ReplicaSet, Node, Job, Endpoints "
     "and ServiceAccount controllers. Each controller watches certain objects and reconciles actual state "
     "toward desired state."),
    ("What is the role of the kubelet?",
     "The kubelet is the node agent. It watches the API server for pods assigned to its node, asks the "
     "container runtime to start them, mounts volumes, runs liveness/readiness/startup probes, and reports "
     "pod and node status back."),
    ("What does kube-proxy do?",
     "It runs on each node and maintains network rules (iptables, IPVS or nftables) so that traffic sent to "
     "a Service's virtual IP is forwarded to one of the healthy backing pods."),
    ("What is a container runtime? Name some.",
     "Software that actually pulls images and runs containers. The kubelet talks to it through the "
     "Container Runtime Interface (CRI). Common runtimes are containerd and CRI-O."),
    ("Did Kubernetes drop Docker? What changed?",
     "Kubernetes removed dockershim in v1.24, so Docker Engine is no longer used directly as the runtime. "
     "Images built with Docker still work because they are OCI-compliant; runtimes like containerd run them."),
    ("What is desired state vs actual state?",
     "Desired state is what you declare in manifests (for example 3 replicas of image v2). Actual state is "
     "what is really running. Controllers continuously compare the two and act to remove any difference."),
    ("What is a reconciliation loop?",
     "The observe-compare-act cycle that every controller runs forever. It is the reason Kubernetes is "
     "self-healing: if a pod disappears, the loop sees 2 instead of 3 and creates a new one."),
    ("What is the difference between imperative and declarative management?",
     "Imperative means giving step-by-step commands such as `kubectl run` or `kubectl scale`. Declarative "
     "means writing the desired state in YAML and running `kubectl apply -f`, letting Kubernetes work out "
     "the steps. Declarative is preferred in production because files can be versioned in Git."),
    ("What is a node? What are master and worker nodes?",
     "A node is a physical or virtual machine in the cluster. Control-plane (formerly \"master\") nodes run "
     "the management components; worker nodes run application pods."),
    ("What happens if a worker node fails?",
     "The node controller marks it NotReady after missing heartbeats. After a timeout (about 5 minutes by "
     "default) its pods are evicted, and controllers such as Deployments recreate them on healthy nodes."),
    ("What happens if the control plane goes down?",
     "Running pods keep running because kubelets and containers work independently, but you cannot deploy, "
     "scale, or self-heal until the control plane is back. That is why production uses 3 control-plane nodes."),
    ("What are the advantages and disadvantages of Kubernetes?",
     "Advantages: self-healing, scaling, rolling updates, service discovery, declarative config, portability "
     "and a huge ecosystem. Disadvantages: steep learning curve, operational complexity, overhead, and it is "
     "overkill for small applications."),
    ("What tools can you use to run Kubernetes locally?",
     "minikube, kind (Kubernetes in Docker), k3d/k3s, and the Kubernetes option in Docker Desktop. "
     "For production you would use kubeadm or managed services such as EKS, AKS and GKE."),
]


# ====================================================================== CLASS 2
def day2():
    s = day_banner(2, "Pods, YAML and kubectl",
                   "By the end you can write pod YAML from memory, run multi-container pods, and use "
                   "labels, selectors and the most important kubectl commands.")
    s += covers([
        "What a pod is and why Kubernetes does not run bare containers",
        "Imperative commands vs declarative YAML",
        "The four required fields of every manifest",
        "Multi-container pods: sidecar pattern, shared volume, init containers",
        "Pod lifecycle phases and restart policies",
        "Labels, selectors and annotations",
        "Lab: kubectl get, describe, logs, exec, port-forward, explain, dry-run",
    ], [["1", "Story and what a pod is", "10 min"],
        ["2", "YAML anatomy and kubectl basics", "20 min"],
        ["3", "Multi-container pods and lifecycle", "20 min"],
        ["4", "Labels and selectors", "10 min"],
        ["5", "Live lab, recap and interview questions", "25 min"]])
    s.append(P("2.1 What is a pod?", "h1"))
    s.append(story("Ravi wanted to run the orders app together with a small log-shipper container that "
                   "reads the app's log files and sends them to the monitoring system. In Docker he had to "
                   "set up a shared volume and network by hand. His senior said: \"In Kubernetes, put both "
                   "in one <b>pod</b> - they automatically share network and storage.\""))
    s.append(P("A <b>pod</b> is the smallest deployable unit in Kubernetes. It wraps one or more containers "
               "that:"))
    s += bullets([
        "share <b>one IP address</b> and port space - they talk to each other on `localhost`;",
        "can share <b>volumes</b> (folders);",
        "are always <b>scheduled together</b> on the same node and live and die together.",
    ])
    s.append(real("A pod is like a <b>flat</b> in an apartment building. The flat has one postal address "
                  "(the IP). Flatmates (containers) share the kitchen and living room (network and volumes) "
                  "and can shout to each other directly (localhost). If the flat is demolished, everyone moves "
                  "out together."))
    s.append(figure(D.pod(), "Figure 2.1 - A pod with a main container and a sidecar sharing IP and a volume"))
    s.append(remember("Most pods have exactly one container. Add a second container only when it must live "
                      "and scale with the first one (log shipper, proxy, config reloader)."))
    s.append(P("2.2 Imperative vs declarative", "h1"))
    s += table(["Style", "Example", "Use it for"], [
        ["Imperative command", "`kubectl run web --image=nginx:1.27`", "Quick tests, learning, exams"],
        ["Imperative with file", "`kubectl create -f pod.yaml`", "One-time creation; fails if it exists"],
        ["Declarative", "`kubectl apply -f pod.yaml`", "Real projects: files live in Git, apply is repeatable"],
    ], cols(0.24, 0.42, 0.34))
    s.append(P("2.3 Anatomy of a YAML manifest", "h1"))
    s.append(P("Every Kubernetes object has the same four top-level fields:"))
    s += table(["Field", "Meaning", "Example"], [
        ["apiVersion", "Which API group/version defines this object", "`v1`, `apps/v1`, `networking.k8s.io/v1`"],
        ["kind", "The type of object", "`Pod`, `Deployment`, `Service`"],
        ["metadata", "Name, namespace, labels, annotations", "`name: web`"],
        ["spec", "The desired state - different for every kind", "containers, replicas, ports..."],
    ], cols(0.18, 0.44, 0.38))
    s.append(code("""apiVersion: v1
kind: Pod
metadata:
  name: web
  labels:
    app: web
    tier: frontend
spec:
  containers:
    - name: nginx
      image: nginx:1.27
      ports:
        - containerPort: 80""", "pod.yaml"))
    s.append(P("Kubernetes adds a fifth section, <b>status</b>, which you never write - it is the actual "
               "state reported by the cluster. See it with `kubectl get pod web -o yaml`."))
    s.append(tryit(["Do not memorise YAML - generate it: "
                    "`kubectl run web --image=nginx:1.27 --dry-run=client -o yaml > pod.yaml`",
                    "Forgot a field name? `kubectl explain pod.spec.containers` and "
                    "`kubectl explain pod.spec --recursive` are built-in documentation."], "Pro tip"))
    s.append(mistake(["YAML uses <b>spaces only</b> - a single tab breaks the file.",
                      "Indentation is meaning: `ports` must be inside the container item, not beside `containers`.",
                      "Using `latest` image tags makes deployments unpredictable - always pin a version."]))
    s.append(P("2.4 Multi-container patterns", "h1"))
    s += table(["Pattern", "What the extra container does", "Example"], [
        ["Sidecar", "Adds a helper feature alongside the main app", "Log shipper, service-mesh proxy (Envoy)"],
        ["Ambassador", "Proxies outbound connections for the app", "Local proxy to a remote database"],
        ["Adapter", "Converts the app's output into a standard format", "Exporter turning logs into metrics"],
        ["Init container", "Runs to completion <b>before</b> app containers start", "Wait for DB, download config, run migrations"],
    ], cols(0.2, 0.44, 0.36))
    s.append(code("""apiVersion: v1
kind: Pod
metadata:
  name: web-with-sidecar
spec:
  volumes:
    - name: logs
      emptyDir: {}
  initContainers:
    - name: wait-a-bit
      image: busybox:1.36
      command: ["sh", "-c", "echo preparing...; sleep 5"]
  containers:
    - name: app
      image: busybox:1.36
      command: ["sh", "-c", "while true; do date >> /logs/app.log; sleep 2; done"]
      volumeMounts:
        - name: logs
          mountPath: /logs
    - name: log-shipper
      image: busybox:1.36
      command: ["sh", "-c", "tail -F /logs/app.log"]
      volumeMounts:
        - name: logs
          mountPath: /logs""", "sidecar.yaml"))
    s.append(funfact("Since Kubernetes 1.33, <b>native sidecars</b> are stable: an init container with "
                     "`restartPolicy: Always` starts before the app and keeps running beside it. This "
                     "fixes old problems such as Jobs never finishing because the sidecar kept running."))
    s.append(P("2.5 Pod lifecycle", "h1"))
    s.append(figure(D.pod_lifecycle(), "Figure 2.2 - Pod phases and the CrashLoopBackOff state"))
    s += table(["Phase / state", "Meaning"], [
        ["Pending", "Accepted, but not running yet - waiting for scheduling or image download."],
        ["Running", "Bound to a node and at least one container is running."],
        ["Succeeded", "All containers exited with code 0 and will not restart (typical for Jobs)."],
        ["Failed", "All containers stopped and at least one exited with an error."],
        ["Unknown", "The node stopped reporting, so the state cannot be read."],
        ["CrashLoopBackOff", "Not a phase but a waiting reason: the container keeps crashing and Kubernetes "
         "waits longer (10s, 20s, 40s ... up to 5 min) before each restart."],
    ], cols(0.24, 0.76))
    s.append(P("The pod's `restartPolicy` decides what the kubelet does when a container exits: "
               "<b>Always</b> (default, for long-running apps), <b>OnFailure</b> (Jobs), or <b>Never</b>."))
    s.append(P("2.6 Labels, selectors and annotations", "h1"))
    s.append(P("<b>Labels</b> are key-value tags on objects, such as `app=orders`, `env=prod`, `version=v2`. "
               "<b>Selectors</b> find objects by label. This is how a Deployment knows which pods it owns and "
               "how a Service knows where to send traffic - not by name, but by label."))
    s.append(real("In a supermarket, items carry stickers: \"organic\", \"discount\", \"dairy\". The store "
                  "manager can say \"move all items with discount AND dairy to aisle 3\" without knowing "
                  "each product name. Labels are the stickers; selectors are the manager's instruction."))
    s.append(code("""kubectl get pods --show-labels
kubectl get pods -l app=web                    # equality
kubectl get pods -l 'env in (dev,qa)'          # set-based
kubectl label pod web env=dev                  # add a label
kubectl label pod web env-                     # remove it""", "PowerShell"))
    s.append(P("<b>Annotations</b> are also key-value pairs but are <i>not</i> used for selection. They hold "
               "extra information for tools and humans: build number, Git commit, contact e-mail, or "
               "settings read by an ingress controller."))
    s.append(P("2.7 Live lab: the kubectl toolbox", "h1"))
    s.append(code("""kubectl apply -f pod.yaml
kubectl get pods -o wide                 # IP and node
kubectl describe pod web                 # full details + Events at the bottom
kubectl logs web                         # container output
kubectl exec -it web -- sh               # shell inside (type exit to leave)
kubectl port-forward pod/web 8080:80     # open http://localhost:8080 in a browser

kubectl apply -f sidecar.yaml
kubectl get pod web-with-sidecar -w      # watch Init:0/1 -> PodInitializing -> Running
kubectl logs web-with-sidecar -c log-shipper -f
kubectl exec -it web-with-sidecar -c app -- cat /logs/app.log

kubectl delete -f pod.yaml -f sidecar.yaml""", "PowerShell"))
    s.append(P("Now break things on purpose and read the errors:"))
    s.append(code("""kubectl run broken --image=nginx:doesnotexist
kubectl get pods            # ErrImagePull, then ImagePullBackOff
kubectl describe pod broken # read the Events section

kubectl run crashy --image=busybox:1.36 -- sh -c "exit 1"
kubectl get pods -w         # Error -> CrashLoopBackOff
kubectl delete pod broken crashy""", "PowerShell"))
    s += table(["Command", "What it is for"], [
        ["`kubectl get <kind>`", "List objects; add `-o wide`, `-o yaml`, `-w`, `-A` (all namespaces)"],
        ["`kubectl describe <kind> <name>`", "Human-readable details and Events - first stop for debugging"],
        ["`kubectl logs <pod> [-c ctr] [-f] [--previous]`", "Container logs; `--previous` shows the crashed instance"],
        ["`kubectl exec -it <pod> -- sh`", "Run a command inside a container"],
        ["`kubectl port-forward`", "Tunnel a local port to a pod or service"],
        ["`kubectl apply / delete -f`", "Create/update or delete from files"],
        ["`kubectl explain <path>`", "Built-in field documentation"],
    ], cols(0.42, 0.58))
    s.append(mistake(["Creating bare pods for real apps. A bare pod is <b>not</b> recreated if its node dies - "
                      "use a Deployment (Class 3).",
                      "Expecting to change most fields of a running pod. Pod specs are largely immutable - "
                      "delete and recreate, or let a Deployment do it."]))
    s.append(remember(["Pod = smallest unit; one IP shared by its containers.",
                       "YAML = apiVersion, kind, metadata, spec.",
                       "Init containers run first, in order; sidecars run alongside.",
                       "Labels + selectors connect objects together.",
                       "Debug flow: get -> describe -> logs -> exec."], "Class 2 recap"))
    s += interview(2, DAY2_QA)
    return s


DAY2_QA = [
    ("What is a pod?",
     "The smallest deployable unit in Kubernetes: a group of one or more containers that share a network "
     "namespace (one IP), can share volumes, and are always scheduled together on the same node."),
    ("Why does Kubernetes use pods instead of running containers directly?",
     "Pods let tightly coupled containers share network and storage and be managed as one unit. They also "
     "give Kubernetes a runtime-neutral abstraction for scheduling, IP assignment and lifecycle."),
    ("Can a pod have more than one container? When would you do that?",
     "Yes. Use it when containers must share resources and lifecycle - for example a sidecar log shipper, "
     "a service-mesh proxy, or an adapter. Unrelated services should be in separate pods so they scale independently."),
    ("How do containers in the same pod communicate?",
     "Over `localhost` because they share the network namespace, and through shared volumes such as emptyDir. "
     "They must use different ports."),
    ("What is an init container?",
     "A container that runs to completion before the app containers start. Multiple init containers run "
     "in order. Used to wait for dependencies, prepare files, or run database migrations."),
    ("What are sidecar, ambassador and adapter patterns?",
     "Sidecar adds a helper feature (logging, proxy). Ambassador proxies the app's outbound connections. "
     "Adapter standardises the app's output (for example exposing metrics in Prometheus format)."),
    ("What are the four required top-level fields in a manifest?",
     "`apiVersion`, `kind`, `metadata` and `spec`. Kubernetes adds `status`, which reflects the actual state."),
    ("What is the difference between kubectl create and kubectl apply?",
     "`create` is imperative and fails if the object exists. `apply` is declarative: it creates the object "
     "if missing or updates it to match the file, tracking the last applied configuration."),
    ("Explain the pod lifecycle phases.",
     "Pending (accepted, not yet running), Running (on a node, at least one container running), Succeeded "
     "(all containers exited 0), Failed (at least one exited with error), and Unknown (node not reporting)."),
    ("What is CrashLoopBackOff and how do you troubleshoot it?",
     "The container keeps crashing and Kubernetes restarts it with growing delays. Check "
     "`kubectl logs <pod> --previous`, `kubectl describe pod` (exit code, OOMKilled, events), the command, "
     "environment variables, config files and probes."),
    ("What is ImagePullBackOff?",
     "The kubelet cannot pull the image - usually a wrong name or tag, a private registry without "
     "imagePullSecrets, or no network access. `kubectl describe pod` shows the exact error."),
    ("What restart policies exist for pods?",
     "Always (default; used by Deployments), OnFailure (restart only on non-zero exit; used by Jobs) and Never."),
    ("What are labels and selectors?",
     "Labels are key-value tags on objects. Selectors query objects by labels - equality-based (`app=web`) or "
     "set-based (`env in (dev,qa)`). Deployments, Services and NetworkPolicies use selectors to find pods."),
    ("What is the difference between labels and annotations?",
     "Labels identify and select objects and have size/format limits. Annotations store non-identifying "
     "metadata for tools and humans (build info, ingress settings) and cannot be used in selectors."),
    ("How do you get a shell inside a running container?",
     "`kubectl exec -it <pod> -- sh` (or bash). For multi-container pods add `-c <container>`. If the image "
     "has no shell, use `kubectl debug` with an ephemeral container."),
    ("How do you view logs of a specific container or a previous crash?",
     "`kubectl logs <pod> -c <container>`; add `-f` to follow and `--previous` to see the last terminated instance."),
    ("How can you generate YAML quickly without writing it by hand?",
     "Use `--dry-run=client -o yaml`, e.g. `kubectl run web --image=nginx --dry-run=client -o yaml > pod.yaml`, "
     "and use `kubectl explain` to discover fields."),
    ("Are pods permanent? What happens if a node dies?",
     "No, pods are ephemeral. A bare pod on a dead node is lost. Controllers like Deployments create "
     "replacement pods with new names and IPs, which is why we never run bare pods in production."),
    ("What is a static pod?",
     "A pod managed directly by the kubelet from a manifest file on the node (usually /etc/kubernetes/manifests), "
     "not by the API server. Control-plane components in kubeadm clusters run as static pods."),
    ("What is kubectl port-forward used for?",
     "It tunnels a local port to a pod or service, e.g. `kubectl port-forward pod/web 8080:80`, so you can "
     "test an app from your laptop without exposing it publicly."),
]


# ====================================================================== CLASS 3
def day3():
    s = day_banner(3, "ReplicaSets and Deployments",
                   "By the end you can deploy, scale, update and roll back an application with zero "
                   "downtime, and explain blue-green and canary releases.")
    s += covers([
        "ReplicaSet - keeping N copies alive",
        "Deployment - the object you use every day",
        "Scaling up and down",
        "Rolling updates: maxSurge and maxUnavailable; the Recreate strategy",
        "Rollout history, change-cause and rollback",
        "Release strategies: blue-green and canary",
        "Lab: upgrade nginx, break it with a bad image, roll back",
    ], [["1", "Story, ReplicaSet and Deployment", "15 min"],
        ["2", "Rolling update and rollback", "20 min"],
        ["3", "Blue-green and canary", "10 min"],
        ["4", "Live lab", "25 min"],
        ["5", "Recap and interview questions", "10 min"]])
    s.append(P("3.1 From pods to ReplicaSets", "h1"))
    s.append(story("Ravi's lunch-time rush needs 3 copies of the menu service. He created 3 pods by hand. "
                   "At 1 PM a node rebooted and two pods vanished - nothing brought them back. Worse, "
                   "releasing a new menu version meant deleting and recreating pods, and customers saw "
                   "errors. He needed something that <i>keeps</i> 3 copies alive and swaps versions safely."))
    s.append(P("A <b>ReplicaSet</b> ensures that a specified number of identical pods are running at all "
               "times. It uses a label selector to count its pods and a pod template to create new ones."))
    s.append(P("A <b>Deployment</b> manages ReplicaSets for you and adds versioned updates and rollback. "
               "You almost never create a ReplicaSet directly - you create a Deployment."))
    s.append(real("A restaurant manager is told \"always keep 3 cooks on the shift\". If one goes home sick, "
                  "the manager calls in a replacement (ReplicaSet). When the restaurant introduces a new "
                  "uniform, the manager swaps cooks <i>one at a time</i> so the kitchen never closes, and "
                  "keeps the old uniforms in case customers complain (Deployment with rollback)."))
    s.append(figure(D.deployment(), "Figure 3.1 - A Deployment owns ReplicaSets, which own Pods"))
    s.append(code("""apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
  labels:
    app: web
spec:
  replicas: 3
  revisionHistoryLimit: 10        # old ReplicaSets kept for rollback
  selector:
    matchLabels:
      app: web                    # must match the template labels
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1                 # at most 1 extra pod during update
      maxUnavailable: 0           # never go below 3 ready pods
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
        - name: nginx
          image: nginx:1.26
          ports:
            - containerPort: 80""", "deploy.yaml"))
    s.append(mistake("The `selector.matchLabels` must match `template.metadata.labels`. If they do not, the "
                     "API server rejects the Deployment. The selector cannot be changed after creation."))
    s.append(P("3.2 Rolling updates", "h1"))
    s.append(P("When you change the pod template (for example the image), the Deployment creates a "
               "<b>new ReplicaSet</b> and gradually moves pods from old to new. Two settings control the speed:"))
    s += table(["Setting", "Meaning", "Default"], [
        ["maxSurge", "How many pods above `replicas` may exist during the update", "25%"],
        ["maxUnavailable", "How many pods below `replicas` may be unavailable during the update", "25%"],
    ], cols(0.22, 0.6, 0.18))
    s.append(figure(D.rolling_update(), "Figure 3.2 - Rolling update from nginx:1.26 to nginx:1.27 with maxSurge 1, maxUnavailable 0"))
    s.append(P("The other strategy, <b>Recreate</b>, kills all old pods first and then starts new ones. It "
               "causes downtime but is needed when two versions cannot run side by side (for example a "
               "database schema that only one version understands)."))
    s.append(real("Changing the tyres of a bus while passengers ride: you replace one tyre at a time "
                  "(rolling update). Recreate is parking the bus at a garage, removing all tyres, then fitting "
                  "new ones - simpler, but nobody travels in the meantime."))
    s.append(P("3.3 Rollout history and rollback", "h1"))
    s.append(P("Each template change creates a <b>revision</b>. Old ReplicaSets are kept (scaled to 0), so "
               "rolling back is fast - Kubernetes just scales the old ReplicaSet up again."))
    s.append(code("""kubectl rollout status deployment/web
kubectl rollout history deployment/web
kubectl rollout history deployment/web --revision=2
kubectl rollout undo deployment/web                  # previous revision
kubectl rollout undo deployment/web --to-revision=1
kubectl rollout pause deployment/web                 # batch several changes
kubectl rollout resume deployment/web
kubectl rollout restart deployment/web               # restart pods, same spec""", "Rollout commands"))
    s.append(P("To record <i>why</i> a revision happened, set the `kubernetes.io/change-cause` annotation; it "
               "appears in `rollout history`."))
    s.append(P("3.4 Release strategies", "h1"))
    s += table(["Strategy", "How it works", "Pros / cons"], [
        ["Rolling update", "Replace pods gradually (built into Deployment)", "Zero downtime, no extra cost; both versions live briefly"],
        ["Recreate", "Stop all old, then start new", "Simple; causes downtime"],
        ["Blue-green", "Run full v1 (blue) and v2 (green); switch the Service selector at once",
         "Instant switch and rollback; needs double resources"],
        ["Canary", "Send a small share of traffic (e.g. 10%) to v2, watch metrics, then increase",
         "Lowest risk; needs traffic splitting (replica ratio, Ingress, service mesh, Argo Rollouts)"],
    ], cols(0.18, 0.44, 0.38))
    s.append(real("A canary release is like a restaurant offering a new dish to a few tables first. If "
                  "those diners love it, it goes on the main menu; if not, only a few people were affected. "
                  "The name comes from coal miners who carried canaries to detect gas early."))
    s.append(P("3.5 Live lab: deploy, update, break, roll back", "h1"))
    s.append(code("""kubectl apply -f deploy.yaml
kubectl get deploy,rs,pods -l app=web

# scale
kubectl scale deployment web --replicas=5
kubectl get pods -l app=web

# rolling update - watch in a second window: kubectl get pods -l app=web -w
kubectl set image deployment/web nginx=nginx:1.27
kubectl annotate deployment/web kubernetes.io/change-cause="upgrade to nginx 1.27"
kubectl rollout status deployment/web
kubectl get rs -l app=web           # old RS has 0 pods, new RS has 5""", "PowerShell - part 1"))
    s.append(code("""# release a broken version
kubectl set image deployment/web nginx=nginx:9.99-broken
kubectl annotate deployment/web kubernetes.io/change-cause="bad release" --overwrite
kubectl get pods -l app=web         # new pods: ImagePullBackOff, old pods still serve!
kubectl rollout status deployment/web --timeout=30s

# roll back
kubectl rollout history deployment/web
kubectl rollout undo deployment/web
kubectl get pods -l app=web         # all healthy again on nginx:1.27
kubectl describe deployment web | Select-String Image""", "PowerShell - part 2"))
    s.append(P("Notice that during the broken release, users were <b>not</b> affected: maxUnavailable "
               "kept the old pods serving until new ones became ready - which never happened."))
    s.append(tryit(["Change `replicas` in deploy.yaml and run `kubectl apply -f deploy.yaml` again - this is the "
                    "declarative way to scale.",
                    "Try a simple blue-green: create `web-blue` and `web-green` Deployments with labels "
                    "`version: blue/green`, then switch a Service selector between them after Class 4."]))
    s.append(mistake(["Using `kubectl set image` in production and forgetting to update the YAML in Git - "
                      "the next `apply` reverts your change. Keep Git as the source of truth.",
                      "Thinking `kubectl scale` changes the history. Only pod template changes create revisions."]))
    s.append(remember(["ReplicaSet keeps N pods; Deployment manages ReplicaSets.",
                       "Rolling update tuned by maxSurge / maxUnavailable.",
                       "Rollback = scale an old ReplicaSet back up (`rollout undo`).",
                       "Blue-green switches all traffic; canary shifts a little at a time."], "Class 3 recap"))
    s += interview(3, DAY3_QA)
    return s


DAY3_QA = [
    ("What is a ReplicaSet?",
     "A controller that ensures a specified number of pod replicas matching a label selector are running. "
     "It creates pods from its template when there are too few and deletes them when there are too many."),
    ("What is a Deployment?",
     "A higher-level object that manages ReplicaSets to provide declarative updates, rolling updates, "
     "rollback, scaling and pause/resume for stateless applications."),
    ("What is the difference between a ReplicaSet and a Deployment?",
     "A ReplicaSet only maintains a pod count. A Deployment manages ReplicaSets and adds versioned rollouts, "
     "history and rollback. You normally create Deployments, not ReplicaSets."),
    ("What was a ReplicationController?",
     "The older predecessor of ReplicaSet. It supported only equality-based selectors; ReplicaSet adds "
     "set-based selectors. It is considered legacy."),
    ("How does a Deployment perform a rolling update?",
     "When the pod template changes, it creates a new ReplicaSet and scales it up while scaling the old one "
     "down, respecting maxSurge and maxUnavailable and waiting for new pods to become ready."),
    ("Explain maxSurge and maxUnavailable.",
     "maxSurge is how many pods above the desired count may exist during an update; maxUnavailable is how "
     "many may be unavailable. Both default to 25%. maxSurge 1 / maxUnavailable 0 means one extra pod at a "
     "time and never fewer ready pods than desired."),
    ("What is the Recreate strategy and when would you use it?",
     "It terminates all old pods before creating new ones, causing downtime. Use it when two versions cannot "
     "run simultaneously, such as incompatible schema changes or a single-writer volume."),
    ("How do you roll back a Deployment?",
     "`kubectl rollout undo deployment/<name>` for the previous revision or `--to-revision=N` for a specific "
     "one. Kubernetes scales the old ReplicaSet back up."),
    ("How do you check rollout status and history?",
     "`kubectl rollout status deployment/<name>` and `kubectl rollout history deployment/<name>`, with "
     "`--revision=N` for details of one revision."),
    ("What triggers a new revision?",
     "Only changes to the pod template (`spec.template`) such as image, env, labels or resources. Scaling "
     "replicas does not create a revision."),
    ("What is revisionHistoryLimit?",
     "The number of old ReplicaSets kept for rollback (default 10). Setting it to 0 disables rollback."),
    ("How do you scale a Deployment?",
     "Imperatively with `kubectl scale deployment/<name> --replicas=N`, declaratively by changing `replicas` "
     "and running `kubectl apply`, or automatically with a HorizontalPodAutoscaler."),
    ("How do you restart all pods of a Deployment without changing the image?",
     "`kubectl rollout restart deployment/<name>`. It adds a timestamp annotation to the template, triggering "
     "a rolling restart - useful after changing a ConfigMap used as env variables."),
    ("What happens if you deploy an image that does not exist?",
     "New pods go into ErrImagePull/ImagePullBackOff and never become ready. With a sensible maxUnavailable "
     "the old pods keep serving traffic; the rollout stalls until you fix or undo it."),
    ("What is progressDeadlineSeconds?",
     "How long a Deployment may go without progress before it is reported as failed (default 600 seconds). "
     "CI/CD pipelines use this through `kubectl rollout status` to detect bad releases."),
    ("Explain blue-green deployment in Kubernetes.",
     "Run two full environments - blue (current) and green (new). Test green, then switch the Service "
     "selector from blue to green so all traffic moves at once. Rollback is switching back. It needs twice the resources."),
    ("Explain canary deployment.",
     "Release the new version to a small share of users first, monitor errors and latency, and increase "
     "gradually. In plain Kubernetes this can be done with replica ratios behind one Service; finer control "
     "uses Ingress weights, a service mesh, or Argo Rollouts / Flagger."),
    ("Why must the Deployment selector match the template labels?",
     "The selector tells the ReplicaSet which pods it owns. If template labels did not match, created pods "
     "would not be counted and the controller would create pods forever, so the API rejects it."),
    ("What does kubectl rollout pause do?",
     "It stops the Deployment from rolling out template changes, letting you make several edits and then "
     "`rollout resume` to apply them as a single rollout."),
    ("Are Deployments suitable for databases?",
     "Usually not. Deployment pods are interchangeable with random names and shared storage. Databases need "
     "stable identity and per-pod storage, which StatefulSets provide (Class 7)."),
]


# ====================================================================== CLASS 4
def day4():
    s = day_banner(4, "Services and cluster networking",
                   "By the end you can expose apps inside and outside the cluster, explain every Service "
                   "type, and describe how DNS, kube-proxy and CNI make pod networking work.")
    s += covers([
        "Why pod IPs cannot be trusted",
        "Services, selectors and Endpoints/EndpointSlices",
        "Service types: ClusterIP, NodePort, LoadBalancer, ExternalName, headless",
        "Ports: port, targetPort, nodePort",
        "Cluster DNS with CoreDNS",
        "The Kubernetes networking model, kube-proxy and CNI plugins",
        "Lab: load balancing across pods, NodePort and LoadBalancer on minikube",
    ], [["1", "Story and why Services exist", "10 min"],
        ["2", "Service types and ports", "20 min"],
        ["3", "DNS, kube-proxy, CNI", "15 min"],
        ["4", "Live lab", "25 min"],
        ["5", "Recap and interview questions", "10 min"]])
    s.append(P("4.1 Why we need Services", "h1"))
    s.append(story("The orders service called the menu service at `10.244.1.5`. After a rolling update "
                   "the menu pods got new IPs and every order failed with \"connection refused\". Ravi "
                   "learned the hard way: <b>pod IPs change every time a pod is recreated</b>. He needed "
                   "one address that never changes."))
    s.append(P("A <b>Service</b> gives a group of pods a stable virtual IP (ClusterIP) and a DNS name. It "
               "finds its pods using a <b>label selector</b> and load-balances traffic across the ones "
               "that are ready."))
    s.append(real("A restaurant prints one phone number on every menu card. Behind it, whichever staff "
                  "member is free answers the call. Staff join and leave, but the number on the card never "
                  "changes. The Service is that phone number; pods are the staff."))
    s.append(figure(D.services(), "Figure 4.1 - A Service selects pods by label and spreads traffic across them"))
    s.append(P("Behind the scenes Kubernetes keeps an <b>EndpointSlice</b> object listing the IP:port of every "
               "ready pod that matches the selector. If a Service has no endpoints, its selector or "
               "readiness is wrong - this is one of the most common bugs."))
    s.append(P("4.2 Ports explained", "h1"))
    s += table(["Field", "Where", "Example"], [
        ["port", "The port the Service listens on (what clients call)", "80"],
        ["targetPort", "The port on the container that receives traffic", "8080"],
        ["nodePort", "Port opened on every node (NodePort/LoadBalancer only), range 30000-32767", "30080"],
        ["containerPort", "Documentation in the pod spec - informational only", "8080"],
    ], cols(0.2, 0.62, 0.18))
    s.append(P("4.3 Service types", "h1"))
    s.append(figure(D.service_types(), "Figure 4.2 - Each Service type builds on the previous one"))
    s += table(["Type", "Reachable from", "Typical use"], [
        ["ClusterIP (default)", "Inside the cluster only", "Backend APIs, databases, internal microservices"],
        ["NodePort", "`<any-node-IP>:30000-32767`", "Labs, on-prem setups, behind your own load balancer"],
        ["LoadBalancer", "Public/private IP from the cloud load balancer", "Exposing an app directly on EKS/AKS/GKE"],
        ["ExternalName", "DNS alias (CNAME) to an outside hostname", "Calling a managed DB like `db.example.com` by an internal name"],
        ["Headless (`clusterIP: None`)", "DNS returns pod IPs directly; no load balancing",
         "StatefulSets, databases, clients that pick their own pod"],
    ], cols(0.24, 0.36, 0.40))
    s.append(code("""apiVersion: v1
kind: Service
metadata:
  name: web
spec:
  type: ClusterIP          # change to NodePort or LoadBalancer
  selector:
    app: web
  ports:
    - port: 80             # service port
      targetPort: 80       # container port
      # nodePort: 30080    # only for NodePort/LoadBalancer""", "service.yaml"))
    s.append(P("4.4 Cluster DNS", "h1"))
    s.append(P("Every cluster runs <b>CoreDNS</b>. Each Service gets a DNS record:"))
    s.append(code("""<service>.<namespace>.svc.cluster.local

web                                   # from a pod in the same namespace
web.shop                              # from another namespace
web.shop.svc.cluster.local            # fully qualified"""))
    s.append(P("Pods find CoreDNS through `/etc/resolv.conf`, which the kubelet writes into every container."))
    s.append(P("4.5 How pod networking works", "h1"))
    s.append(P("Kubernetes has a simple networking model with three rules:"))
    s += bullets([
        "Every pod gets its own unique IP address.",
        "Pods can reach every other pod on any node without NAT.",
        "Agents on a node (like the kubelet) can reach all pods on that node.",
    ])
    s.append(P("Kubernetes itself does not implement this. A <b>CNI plugin</b> (Container Network Interface) "
               "does - Calico, Flannel, Cilium, Weave, or the cloud's own (AWS VPC CNI, Azure CNI). "
               "<b>kube-proxy</b> then implements Services by writing iptables/IPVS/nftables rules on every "
               "node that translate the Service IP into a real pod IP."))
    s.append(real("Think of an office campus. The CNI plugin builds the roads and gives every cabin a door "
                  "number. kube-proxy is the receptionist with a rule book: \"calls for Accounts go to cabin "
                  "12, 14 or 19 - pick any free one\"."))
    s.append(P("4.6 Live lab: Services in action", "h1"))
    s.append(P("We use `traefik/whoami`, a tiny web app that replies with its own pod name - perfect for "
               "seeing load balancing."))
    s.append(code("""kubectl create deployment whoami --image=traefik/whoami --replicas=3
kubectl expose deployment whoami --port=80 --target-port=80
kubectl get svc whoami
kubectl get endpointslices -l kubernetes.io/service-name=whoami

# call it from inside the cluster several times
kubectl run client --rm -it --image=busybox:1.36 -- sh
  wget -qO- http://whoami | grep Hostname      # repeat 5 times - names change
  nslookup whoami
  exit""", "PowerShell - ClusterIP"))
    s.append(code("""kubectl expose deployment whoami --name=whoami-np --type=NodePort --port=80
kubectl get svc whoami-np               # note the 3xxxx port
minikube service whoami-np --url        # gives a localhost URL on Windows; keep it open
curl.exe <url-from-previous-command>

kubectl expose deployment whoami --name=whoami-lb --type=LoadBalancer --port=80
kubectl get svc whoami-lb               # EXTERNAL-IP is <pending>
minikube tunnel                         # in a separate admin window; leave running
kubectl get svc whoami-lb               # EXTERNAL-IP now 127.0.0.1
curl.exe http://127.0.0.1""", "PowerShell - NodePort and LoadBalancer"))
    s.append(P("Now break it: change the selector so it matches nothing and see the endpoints disappear."))
    s.append(code("""kubectl set selector svc whoami app=wrong
kubectl get endpointslices -l kubernetes.io/service-name=whoami   # no endpoints
kubectl delete deployment whoami; kubectl delete svc whoami whoami-np whoami-lb""", "PowerShell"))
    s.append(tryit(["Scale whoami to 1 and back to 5 while looping requests - the Service adapts instantly.",
                    "Run `kubectl get svc -A` to find the `kubernetes` Service, which points at the API server, "
                    "and `kube-dns` in kube-system."]))
    s.append(mistake(["Confusing `port` and `targetPort`; if the app listens on 8080, targetPort must be 8080.",
                      "Labels typo in the selector: the Service is created fine but has zero endpoints.",
                      "Expecting to ping a ClusterIP - it is virtual and only answers on its defined ports."]))
    s.append(remember(["Services give pods a stable IP + DNS name and load-balance.",
                       "ClusterIP < NodePort < LoadBalancer; ExternalName = DNS alias; headless = no IP.",
                       "DNS: service.namespace.svc.cluster.local (CoreDNS).",
                       "CNI gives pods IPs; kube-proxy routes Service traffic."], "Class 4 recap"))
    s += interview(4, DAY4_QA)
    return s


DAY4_QA = [
    ("What is a Kubernetes Service and why is it needed?",
     "An abstraction that gives a set of pods a stable virtual IP and DNS name and load-balances traffic to "
     "them. It is needed because pod IPs change whenever pods are recreated or rescheduled."),
    ("How does a Service know which pods to send traffic to?",
     "Through its label selector. The EndpointSlice controller keeps a list of ready pods matching the "
     "selector, and kube-proxy routes traffic to those IPs."),
    ("What are the Service types?",
     "ClusterIP (internal, default), NodePort (opens a port 30000-32767 on every node), LoadBalancer "
     "(provisions a cloud load balancer), ExternalName (DNS CNAME to an external name). A headless Service "
     "is a ClusterIP Service with `clusterIP: None`."),
    ("Difference between port, targetPort and nodePort?",
     "port is what the Service listens on, targetPort is the container port traffic is forwarded to, and "
     "nodePort is the port opened on every node for NodePort/LoadBalancer Services."),
    ("What is a headless Service?",
     "A Service with `clusterIP: None`. There is no virtual IP or load balancing; DNS returns the pod IPs "
     "directly. StatefulSets use it to give each pod a stable DNS name."),
    ("What is an ExternalName Service?",
     "A Service that maps an internal name to an external DNS name via a CNAME record, with no selector or "
     "proxying - for example pointing `db` to a managed database hostname."),
    ("What are Endpoints and EndpointSlices?",
     "Objects listing the IP:port pairs of the pods backing a Service. EndpointSlices are the newer, scalable "
     "version that splits large lists into chunks. `kubectl get endpointslices` helps debug Services."),
    ("A Service is not reachable. How do you troubleshoot?",
     "Check the Service has endpoints, compare selector with pod labels, confirm pods are Ready, verify "
     "port/targetPort, test from a pod with wget/curl by IP and by DNS name, check CoreDNS, and check any "
     "NetworkPolicies."),
    ("How does DNS work inside Kubernetes?",
     "CoreDNS runs in kube-system and is exposed as the kube-dns Service. The kubelet configures every pod's "
     "/etc/resolv.conf to use it. Services resolve as `<svc>.<ns>.svc.cluster.local`."),
    ("How can a pod reach a Service in another namespace?",
     "By using the namespace in the name, e.g. `http://orders.shop` or the full "
     "`orders.shop.svc.cluster.local`."),
    ("What is kube-proxy and which modes does it support?",
     "A node component that implements Services by programming iptables, IPVS or nftables rules that "
     "translate Service IPs to pod IPs. Some CNIs like Cilium can replace kube-proxy with eBPF."),
    ("What is CNI? Name some plugins.",
     "Container Network Interface - a standard for plugins that give pods IPs and connect them across nodes. "
     "Examples: Calico, Flannel, Cilium, Weave, AWS VPC CNI, Azure CNI."),
    ("Explain the Kubernetes networking model.",
     "Every pod gets a unique IP; all pods can communicate with all other pods across nodes without NAT; "
     "node agents can reach pods on their node. The CNI plugin implements it."),
    ("How do you expose an application outside the cluster?",
     "With a NodePort or LoadBalancer Service, or an Ingress/Gateway in front of ClusterIP Services. "
     "`kubectl port-forward` works for temporary local testing."),
    ("What is the difference between NodePort and LoadBalancer?",
     "NodePort opens a fixed port on each node; clients must know a node IP. LoadBalancer additionally asks "
     "the cloud for an external load balancer with one stable IP that forwards to the node ports."),
    ("How does a LoadBalancer Service work on bare metal or minikube?",
     "There is no cloud controller, so EXTERNAL-IP stays pending unless you add something like MetalLB, or on "
     "minikube run `minikube tunnel`."),
    ("What is session affinity in a Service?",
     "Setting `sessionAffinity: ClientIP` sends requests from the same client IP to the same pod. Default is None."),
    ("Can a Service exist without a selector?",
     "Yes. You then create Endpoints/EndpointSlices manually to point to IPs outside the cluster, such as a "
     "legacy database."),
    ("Why can't you ping a ClusterIP?",
     "A ClusterIP is a virtual IP implemented by kube-proxy rules for specific ports and protocols. No "
     "interface owns it, so ICMP ping usually does not work; test with curl on the service port."),
    ("What is the `kubernetes` Service in the default namespace?",
     "A built-in ClusterIP Service pointing to the API server, so pods can reach the API at "
     "`https://kubernetes.default.svc`."),
]


# ====================================================================== CLASS 5
def day5():
    s = day_banner(5, "Ingress, Gateway API and Namespaces",
                   "By the end you can route many apps through one entry point using host and path "
                   "rules, add TLS, and organise a cluster with namespaces, quotas and contexts.")
    s += covers([
        "Why one LoadBalancer per app does not scale",
        "Ingress resources and Ingress controllers",
        "Host-based and path-based routing, TLS termination",
        "Gateway API - the modern successor",
        "Namespaces: isolation, DNS, which objects are namespaced",
        "ResourceQuota and LimitRange",
        "kubeconfig, clusters, users and contexts",
        "Lab: route /menu and /orders behind quickbite.local",
    ], [["1", "Story and Ingress concepts", "15 min"],
        ["2", "Gateway API", "5 min"],
        ["3", "Namespaces, quotas, contexts", "20 min"],
        ["4", "Live lab", "25 min"],
        ["5", "Recap and interview questions", "10 min"]])
    s.append(P("5.1 Why Ingress?", "h1"))
    s.append(story("QuickBite exposed menu, orders and payment with three LoadBalancer Services. The cloud "
                   "bill showed three load balancers, three public IPs and three SSL certificates to renew. "
                   "Marketing wanted everything under one address: quickbite.com/menu, quickbite.com/orders. "
                   "Ravi needed one smart front door."))
    s.append(P("An <b>Ingress</b> is a set of HTTP/HTTPS routing rules: \"requests for host X and path Y go to "
               "Service Z\". An <b>Ingress controller</b> is the actual reverse proxy (NGINX, Traefik, HAProxy, "
               "cloud load balancers) that reads those rules and does the routing. Without a controller, an "
               "Ingress object does nothing."))
    s.append(real("A shopping mall has one main entrance and a directory board: \"Food court - level 3, "
                  "Cinema - level 4, Electronics - level 1\". Visitors use one door and are directed to the "
                  "right shop. The Ingress is the directory board; the Ingress controller is the security "
                  "guard at the entrance who reads it and points you the right way."))
    s.append(figure(D.ingress(), "Figure 5.1 - One Ingress controller routes requests to several Services by path"))
    s.append(code("""apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: quickbite
spec:
  ingressClassName: nginx
  tls:                                  # optional HTTPS
    - hosts: ["quickbite.local"]
      secretName: quickbite-tls
  rules:
    - host: quickbite.local
      http:
        paths:
          - path: /menu
            pathType: Prefix
            backend:
              service: { name: menu, port: { number: 80 } }
          - path: /orders
            pathType: Prefix
            backend:
              service: { name: orders, port: { number: 80 } }""", "ingress.yaml"))
    s += table(["Term", "Meaning"], [
        ["Path-based routing", "`/menu` to one Service, `/orders` to another"],
        ["Host-based routing", "`menu.quickbite.com` and `admin.quickbite.com` to different Services"],
        ["pathType", "`Prefix` (matches /menu/...), `Exact` (only /menu), `ImplementationSpecific`"],
        ["TLS termination", "The controller decrypts HTTPS using a certificate stored in a TLS Secret"],
        ["IngressClass", "Chooses which controller handles this Ingress when several are installed"],
        ["cert-manager", "A popular add-on that obtains and renews free Let's Encrypt certificates automatically"],
    ], cols(0.24, 0.76))
    s.append(P("5.2 Gateway API - the next generation", "h1"))
    s.append(P("Ingress only covers basic HTTP routing; advanced features ended up in controller-specific "
               "annotations. The <b>Gateway API</b> is the official successor with richer, portable objects:"))
    s += bullets([
        "<b>GatewayClass</b> - which implementation (like IngressClass).",
        "<b>Gateway</b> - the actual listener (ports, TLS), usually owned by the platform team.",
        "<b>HTTPRoute / GRPCRoute / TCPRoute</b> - routing rules, owned by app teams; supports header "
        "matching and weighted traffic splitting for canaries.",
    ])
    s.append(funfact("The community <b>ingress-nginx</b> controller was retired in March 2026 and no longer "
                     "receives fixes. Ingress objects still work with other controllers, but new projects "
                     "should prefer the Gateway API or a maintained controller. minikube's ingress addon is "
                     "still perfectly fine for learning the concepts."))
    s.append(P("5.3 Namespaces", "h1"))
    s.append(P("A <b>namespace</b> is a virtual cluster inside a physical cluster. It groups objects, scopes "
               "names (two namespaces can each have a Service called `web`), and is the unit for quotas, "
               "RBAC permissions and network policies."))
    s.append(real("One office building, many floors. Finance on floor 2 and HR on floor 3 can both have a "
                  "room called \"Meeting Room A\". Each floor has its own budget (quota) and access cards "
                  "(RBAC), but they share the lifts, power and security (the cluster)."))
    s.append(figure(D.namespaces(), "Figure 5.2 - Namespaces divide one cluster into isolated areas"))
    s += table(["Default namespace", "Purpose"], [
        ["default", "Where objects go if you do not specify a namespace"],
        ["kube-system", "Kubernetes' own components (CoreDNS, kube-proxy, control plane)"],
        ["kube-public", "Readable by everyone, rarely used"],
        ["kube-node-lease", "Node heartbeat Lease objects for fast failure detection"],
    ], cols(0.3, 0.7))
    s.append(P("Not everything is namespaced. Nodes, PersistentVolumes, StorageClasses, ClusterRoles and "
               "Namespaces themselves are <b>cluster-scoped</b>. Check with "
               "`kubectl api-resources --namespaced=false`."))
    s.append(P("ResourceQuota and LimitRange", "h2"))
    s.append(code("""apiVersion: v1
kind: ResourceQuota
metadata:
  name: dev-quota
  namespace: dev
spec:
  hard:
    pods: "10"
    requests.cpu: "2"
    requests.memory: 4Gi
    limits.cpu: "4"
    limits.memory: 8Gi
---
apiVersion: v1
kind: LimitRange
metadata:
  name: dev-defaults
  namespace: dev
spec:
  limits:
    - type: Container
      default:          { cpu: 500m, memory: 256Mi }   # limit if none given
      defaultRequest:   { cpu: 100m, memory: 128Mi }   # request if none given""", "quota.yaml"))
    s.append(P("<b>ResourceQuota</b> caps the total a namespace may use. <b>LimitRange</b> sets default and "
               "min/max values for each container, so pods without resources still get sensible values."))
    s.append(P("kubeconfig and contexts", "h2"))
    s.append(P("kubectl reads `~/.kube/config` (on Windows `C:\\Users\\<you>\\.kube\\config`). It lists "
               "<b>clusters</b> (API server addresses), <b>users</b> (credentials) and <b>contexts</b> "
               "(cluster + user + default namespace). Switching context switches which cluster you control."))
    s.append(code("""kubectl config get-contexts
kubectl config current-context
kubectl config use-context minikube
kubectl config set-context --current --namespace=dev   # change default namespace"""))
    s.append(mistake("Running `kubectl delete` while your context points at production. Always check "
                     "`kubectl config current-context` - many engineers show it in their shell prompt."))
    s.append(P("5.4 Live lab: one door, two apps", "h1"))
    s.append(code("""minikube addons enable ingress
kubectl get pods -n ingress-nginx          # wait until controller is Running

kubectl create namespace shop
kubectl config set-context --current --namespace=shop

kubectl create deployment menu   --image=hashicorp/http-echo -- /http-echo -text="Menu: biryani"
kubectl create deployment orders --image=hashicorp/http-echo -- /http-echo -text="Orders service OK"
kubectl expose deployment menu   --port=80 --target-port=5678
kubectl expose deployment orders --port=80 --target-port=5678""", "PowerShell - part 1"))
    s.append(P("Save the Ingress from section 5.1 as `ingress.yaml`, remove the `tls` block for now, and apply it:"))
    s.append(code("""kubectl apply -f ingress.yaml
kubectl get ingress
minikube tunnel                            # separate admin window; keep it open

curl.exe -H "Host: quickbite.local" http://127.0.0.1/menu
curl.exe -H "Host: quickbite.local" http://127.0.0.1/orders
curl.exe -H "Host: quickbite.local" http://127.0.0.1/unknown     # 404 from controller""", "PowerShell - part 2"))
    s.append(code("""kubectl apply -f quota.yaml            # change namespace: dev -> shop first
kubectl describe quota -n shop
kubectl create deployment big --image=nginx:1.27 --replicas=15
kubectl get deploy big                 # only 10 pods allowed - see why:
kubectl describe rs -l app=big | Select-String quota

kubectl config set-context --current --namespace=default
kubectl delete namespace shop          # deletes everything inside it""", "PowerShell - quotas"))
    s.append(tryit(["Add `127.0.0.1 quickbite.local` to `C:\\Windows\\System32\\drivers\\etc\\hosts` (as "
                    "admin) and open http://quickbite.local/menu in your browser.",
                    "Create a self-signed certificate with OpenSSL, store it with "
                    "`kubectl create secret tls quickbite-tls --cert=tls.crt --key=tls.key`, add the tls block "
                    "back and test https."]))
    s.append(remember(["Ingress = HTTP routing rules; Ingress controller = the proxy that applies them.",
                       "Gateway API = modern, role-oriented successor of Ingress.",
                       "Namespaces scope names, quotas, RBAC and policies.",
                       "ResourceQuota caps totals; LimitRange sets per-container defaults.",
                       "Context = cluster + user + namespace; always check it."], "Class 5 recap"))
    s += interview(5, DAY5_QA)
    return s


DAY5_QA = [
    ("What is an Ingress?",
     "An API object that defines HTTP/HTTPS routing rules from outside the cluster to Services, based on "
     "host names and URL paths, with optional TLS termination."),
    ("What is an Ingress controller and why is it required?",
     "The component that implements Ingress rules - a reverse proxy such as NGINX, Traefik, HAProxy or a "
     "cloud load balancer controller. An Ingress object has no effect unless a controller is running."),
    ("Ingress vs LoadBalancer Service?",
     "A LoadBalancer Service exposes one Service at layer 4 and usually costs one cloud load balancer each. "
     "Ingress works at layer 7 and routes many hosts/paths to many Services through one entry point."),
    ("What is path-based vs host-based routing?",
     "Path-based routes by URL path (/menu, /orders) on the same host; host-based routes by hostname "
     "(menu.example.com, admin.example.com)."),
    ("Explain pathType values.",
     "Prefix matches the path and anything below it split by `/`; Exact matches only the exact path; "
     "ImplementationSpecific leaves matching to the controller."),
    ("How do you enable HTTPS with Ingress?",
     "Store the certificate and key in a Secret of type kubernetes.io/tls and reference it under `spec.tls` "
     "with the host names. cert-manager can issue and renew certificates automatically."),
    ("What is an IngressClass?",
     "A resource that identifies which controller should handle an Ingress, referenced with "
     "`spec.ingressClassName`. It allows multiple controllers in one cluster."),
    ("What is the Gateway API?",
     "The newer Kubernetes networking API that succeeds Ingress. It splits responsibilities into "
     "GatewayClass, Gateway and Routes (HTTPRoute, GRPCRoute, etc.), and natively supports header matching, "
     "traffic splitting and more protocols."),
    ("What is a namespace?",
     "A logical partition of a cluster that scopes object names and is the boundary for RBAC, quotas, "
     "LimitRanges and NetworkPolicies."),
    ("Which namespaces exist by default?",
     "default, kube-system, kube-public and kube-node-lease. Add-ons may create more, like ingress-nginx."),
    ("Are all objects namespaced?",
     "No. Nodes, PersistentVolumes, StorageClasses, Namespaces, ClusterRoles, ClusterRoleBindings and CRDs "
     "are cluster-scoped. `kubectl api-resources --namespaced=false` lists them."),
    ("Do namespaces provide network isolation?",
     "No, by default pods in different namespaces can talk to each other. Isolation requires "
     "NetworkPolicies and a CNI that enforces them."),
    ("What is a ResourceQuota?",
     "A namespace-level limit on total resource consumption - CPU and memory requests/limits, number of "
     "pods, Services, PVCs and so on. New objects that would exceed it are rejected."),
    ("What is a LimitRange?",
     "A namespace policy that sets default requests/limits and minimum/maximum values per container or pod, "
     "so workloads without resource settings still get sensible values."),
    ("What happens when you delete a namespace?",
     "All objects inside it are deleted. It stays in Terminating until finalizers complete."),
    ("What is kubeconfig?",
     "A YAML file (default ~/.kube/config) holding clusters, users and contexts that kubectl uses to "
     "connect and authenticate. The KUBECONFIG variable can point to other files."),
    ("What is a context in kubectl?",
     "A named combination of cluster, user and default namespace. `kubectl config use-context` switches "
     "between them; `set-context --current --namespace=x` changes the default namespace."),
    ("How do you run a command against a namespace without switching?",
     "Add `-n <namespace>` to the command, or `-A`/`--all-namespaces` to list across all."),
    ("Why would you use multiple namespaces instead of multiple clusters?",
     "Namespaces are cheaper and simpler for separating teams or environments with quotas and RBAC. Separate "
     "clusters give stronger isolation and are preferred for production vs non-production or strict compliance."),
    ("The Ingress returns 404 or 503. How do you debug?",
     "404: check host header and path rules, pathType and ingressClassName. 503: the backend Service has no "
     "ready endpoints - check selectors, ports and pod readiness. Also read the controller pod logs."),
]
