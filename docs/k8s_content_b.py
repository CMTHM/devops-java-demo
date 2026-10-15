"""Classes 6-10 and closing pages of the Kubernetes course."""
import k8s_diagrams as D
from k8s_pdf_lib import *


# ====================================================================== CLASS 6
def day6():
    s = day_banner(6, "ConfigMaps and Secrets",
                   "By the end you can keep configuration and passwords out of your images, inject them "
                   "as environment variables or files, and explain how to keep Secrets truly secret.")
    s += covers([
        "Why configuration must not be baked into images",
        "ConfigMaps: create from literals, files and YAML",
        "Four ways to consume config: env, envFrom, volume, command arguments",
        "Secrets: types, base64, stringData, imagePullSecrets",
        "Updating config: what reloads automatically and what does not",
        "Immutable ConfigMaps/Secrets and the Downward API",
        "Securing Secrets: encryption at rest, RBAC, external secret managers",
    ], [["1", "Story and ConfigMaps", "15 min"],
        ["2", "Secrets and security", "20 min"],
        ["3", "Updates, immutability, Downward API", "10 min"],
        ["4", "Live lab", "25 min"],
        ["5", "Recap and interview questions", "10 min"]])
    s.append(P("6.1 Separate config from code", "h1"))
    s.append(story("The QuickBite orders image had the database password and the payment-gateway URL "
                   "written inside it. To use a different database in testing, Ravi had to rebuild the "
                   "image. Worse, anyone who pulled the image could read the production password. "
                   "His team lead quoted the Twelve-Factor App rule: \"Store config in the environment.\""))
    s.append(P("Build <b>one image</b> and run it everywhere - dev, test, prod - with different settings "
               "supplied at runtime. Kubernetes gives you two objects for that:"))
    s += table(["Object", "Holds", "Example values"], [
        ["ConfigMap", "Non-sensitive settings, as key-value pairs or whole files",
         "APP_MODE=prod, LOG_LEVEL=info, nginx.conf, menu.json"],
        ["Secret", "Sensitive data: passwords, tokens, keys, certificates",
         "DB_PASSWORD, API keys, TLS cert, registry login"],
    ], cols(0.18, 0.42, 0.40))
    s.append(real("A ConfigMap is the <b>notice board</b> in the office kitchen - anyone can read today's "
                  "menu and timings. A Secret is the <b>locker</b> with a key - only people who are given "
                  "access can open it. Both can change without rebuilding the office."))
    s.append(figure(D.config(), "Figure 6.1 - ConfigMaps and Secrets reach a pod as environment variables or files"))
    s.append(P("6.2 Creating ConfigMaps", "h1"))
    s.append(code("""kubectl create configmap app-config --from-literal=APP_MODE=prod --from-literal=LOG_LEVEL=info
kubectl create configmap menu-file --from-file=menu.json
kubectl create configmap app-config --from-env-file=app.env --dry-run=client -o yaml""", "Imperative"))
    s.append(code("""apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  APP_MODE: prod
  LOG_LEVEL: info
  menu.json: |
    {"specials": ["biryani", "masala dosa"]}""", "configmap.yaml"))
    s.append(P("6.3 Consuming config in a pod", "h1"))
    s.append(code("""apiVersion: v1
kind: Pod
metadata:
  name: config-demo
spec:
  containers:
    - name: app
      image: busybox:1.36
      command: ["sh", "-c", "echo mode=$APP_MODE pass=$DB_PASSWORD; sleep 3600"]
      env:
        - name: APP_MODE                     # 1. a single key
          valueFrom:
            configMapKeyRef: { name: app-config, key: APP_MODE }
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef: { name: db-secret, key: password }
      envFrom:                               # 2. every key as a variable
        - configMapRef: { name: app-config }
      volumeMounts:                          # 3. keys as files
        - name: config-vol
          mountPath: /etc/config
        - name: secret-vol
          mountPath: /etc/secrets
          readOnly: true
  volumes:
    - name: config-vol
      configMap: { name: app-config }
    - name: secret-vol
      secret: { secretName: db-secret }""", "config-demo.yaml"))
    s += table(["Method", "Good for", "Updates live?"], [
        ["`env` with keyRef", "A few specific values", "No - restart the pod"],
        ["`envFrom`", "Load all keys at once", "No - restart the pod"],
        ["Volume mount", "Config files (nginx.conf, application.properties)", "Yes, within about a minute (not with subPath)"],
        ["Command args `$(VAR)`", "Passing values as flags", "No - restart the pod"],
    ], cols(0.24, 0.46, 0.30))
    s.append(P("6.4 Secrets", "h1"))
    s.append(code("""kubectl create secret generic db-secret `
  --from-literal=password='S3cr3t!' --from-literal=user=quickbite
kubectl get secret db-secret -o yaml           # values look scrambled... but are they?
kubectl get secret db-secret -o jsonpath='{.data.password}'
# decode in PowerShell:
[Text.Encoding]::UTF8.GetString([Convert]::FromBase64String("UzNjcjN0IQ=="))""", "PowerShell"))
    s.append(mistake("<b>base64 is encoding, not encryption.</b> Anyone who can read the Secret object "
                     "can decode it in one line. Never commit Secret YAML with real values to Git."))
    s += table(["Secret type", "Used for"], [
        ["Opaque (generic)", "Any user-defined data - the default"],
        ["kubernetes.io/tls", "TLS certificate and key, used by Ingress"],
        ["kubernetes.io/dockerconfigjson", "Private registry login, referenced as imagePullSecrets"],
        ["kubernetes.io/service-account-token", "Long-lived ServiceAccount tokens (legacy)"],
        ["kubernetes.io/basic-auth, ssh-auth", "Username/password, SSH keys"],
    ], cols(0.42, 0.58))
    s.append(P("In YAML you can use `stringData` to write plain text and let Kubernetes encode it:"))
    s.append(code("""apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
stringData:
  user: quickbite
  password: S3cr3t!"""))
    s.append(P("How to really protect Secrets", "h2"))
    s += bullets([
        "<b>Encryption at rest</b> - configure the API server (EncryptionConfiguration or a cloud KMS) so "
        "Secrets are encrypted inside etcd. Managed clusters offer this as a setting.",
        "<b>RBAC</b> - give `get/list` on Secrets only to the ServiceAccounts that need them.",
        "<b>Mount as files</b> rather than env vars where possible; env vars leak into crash dumps and logs.",
        "<b>External secret managers</b> - HashiCorp Vault, AWS Secrets Manager, Azure Key Vault, via the "
        "External Secrets Operator or the Secrets Store CSI driver.",
        "<b>Safe Git</b> - Sealed Secrets or SOPS encrypt Secret files so they can live in Git.",
    ])
    s.append(P("6.5 Immutable config and the Downward API", "h1"))
    s.append(P("Setting `immutable: true` on a ConfigMap or Secret prevents accidental edits and reduces load "
               "on the API server (kubelets stop watching it). To change it, create a new one, e.g. "
               "`app-config-v2`, and update the Deployment - which also gives you a clean rollout and rollback."))
    s.append(P("The <b>Downward API</b> lets a pod read facts about itself - its name, namespace, IP, node "
               "name, labels and resource limits - as env vars or files, without calling the API server:"))
    s.append(code("""env:
  - name: POD_NAME
    valueFrom: { fieldRef: { fieldPath: metadata.name } }
  - name: NODE_NAME
    valueFrom: { fieldRef: { fieldPath: spec.nodeName } }
  - name: MEM_LIMIT
    valueFrom: { resourceFieldRef: { resource: limits.memory } }"""))
    s.append(P("6.6 Live lab", "h1"))
    s.append(code("""kubectl apply -f configmap.yaml
kubectl create secret generic db-secret `
  --from-literal=password='S3cr3t!' --from-literal=user=quickbite
kubectl apply -f config-demo.yaml
kubectl logs config-demo                       # mode=prod pass=S3cr3t!
kubectl exec config-demo -- env | Select-String APP_
kubectl exec config-demo -- ls /etc/config /etc/secrets
kubectl exec config-demo -- cat /etc/config/menu.json

# live update test
kubectl edit configmap app-config              # change LOG_LEVEL to debug, save
kubectl exec config-demo -- cat /etc/config/LOG_LEVEL   # wait ~60 s: becomes debug
kubectl exec config-demo -- printenv LOG_LEVEL          # still info - env never changes

kubectl delete pod config-demo; kubectl delete cm app-config; kubectl delete secret db-secret""", "PowerShell"))
    s.append(tryit(["Reference a ConfigMap that does not exist and look at the pod status: "
                    "<b>CreateContainerConfigError</b>. Fix it by creating the ConfigMap.",
                    "For a Deployment, run `kubectl rollout restart deployment/<name>` after changing a "
                    "ConfigMap used as env vars."]))
    s.append(remember(["ConfigMap = plain settings; Secret = sensitive data (base64, not encrypted).",
                       "Consume via env, envFrom, volume files or args.",
                       "Volume files update live; env vars need a restart.",
                       "Protect Secrets with encryption at rest, RBAC and external managers.",
                       "Downward API exposes pod facts to the container."], "Class 6 recap"))
    s += interview(6, DAY6_QA)
    return s


DAY6_QA = [
    ("What is a ConfigMap?",
     "An API object that stores non-confidential configuration as key-value pairs or files, so the same "
     "image can run with different configuration in different environments."),
    ("What is a Secret?",
     "An object for small amounts of sensitive data such as passwords, tokens and keys. It is stored "
     "base64-encoded and can be protected with RBAC and encryption at rest."),
    ("What is the difference between a ConfigMap and a Secret?",
     "Both inject configuration. Secrets are meant for sensitive data: they are base64-encoded, can be "
     "encrypted at rest, are mounted on tmpfs in memory on nodes, and are usually restricted by RBAC."),
    ("Are Kubernetes Secrets secure by default?",
     "Not fully. They are only base64-encoded and stored unencrypted in etcd unless encryption at rest is "
     "enabled. Anyone with read access to Secrets or etcd can see them."),
    ("How can you make Secrets more secure?",
     "Enable encryption at rest with a KMS provider, limit access with RBAC, avoid committing them to Git "
     "(use Sealed Secrets or SOPS), prefer file mounts over env vars, and use external managers like Vault "
     "or cloud secret stores through External Secrets Operator or the CSI driver."),
    ("What are the ways to use a ConfigMap in a pod?",
     "As individual env vars (configMapKeyRef), all keys as env vars (envFrom), as files in a volume, or "
     "as command-line arguments via env var substitution."),
    ("If you update a ConfigMap, does the pod see the change?",
     "Volume-mounted files update automatically after a short delay (except subPath mounts). Environment "
     "variables do not change until the pod restarts, e.g. via `kubectl rollout restart`."),
    ("What is the difference between data and stringData in a Secret?",
     "`data` expects base64-encoded values; `stringData` accepts plain text and the API server encodes it. "
     "stringData is write-only convenience and is merged into data."),
    ("What Secret types exist?",
     "Opaque, kubernetes.io/tls, kubernetes.io/dockerconfigjson, kubernetes.io/basic-auth, "
     "kubernetes.io/ssh-auth, kubernetes.io/service-account-token and bootstrap tokens."),
    ("How do you pull an image from a private registry?",
     "Create a docker-registry Secret (`kubectl create secret docker-registry ...`) and reference it in the "
     "pod spec under `imagePullSecrets`, or attach it to the ServiceAccount."),
    ("What is an immutable ConfigMap or Secret?",
     "One with `immutable: true`. Its data cannot be changed, which prevents accidental updates and reduces "
     "API server watch load. To change it you create a new object and update references."),
    ("What is the size limit of a ConfigMap or Secret?",
     "1 MiB each, because they are stored in etcd. Larger data should go in volumes or external storage."),
    ("What happens if a pod references a missing ConfigMap?",
     "The container cannot start and shows CreateContainerConfigError, unless the reference is marked "
     "`optional: true`."),
    ("What is the Downward API?",
     "A way to expose pod and container metadata - name, namespace, IP, node name, labels, annotations, "
     "resource requests and limits - to containers as env vars or files."),
    ("How do you create a ConfigMap from a file?",
     "`kubectl create configmap <name> --from-file=<path>`; the file name becomes the key and its content the "
     "value. `--from-env-file` turns each line into a key."),
    ("Why should you prefer mounting Secrets as files over env vars?",
     "Env vars can leak through logs, crash reports, `kubectl describe` output or child processes, and they "
     "cannot be rotated without a restart. Files on tmpfs can be updated and have tighter permissions."),
    ("How do you decode a Secret value?",
     "`kubectl get secret <name> -o jsonpath='{.data.<key>}'` then base64-decode it. This shows why base64 "
     "is not encryption."),
    ("What is the External Secrets Operator?",
     "A controller that reads secrets from external systems such as AWS Secrets Manager, Azure Key Vault, "
     "GCP Secret Manager or Vault and creates/updates Kubernetes Secrets automatically."),
    ("What are Sealed Secrets?",
     "A Bitnami tool where you encrypt a Secret with the cluster's public key into a SealedSecret that is "
     "safe to store in Git; only the controller in the cluster can decrypt it."),
    ("How do you trigger a rollout when a ConfigMap changes?",
     "Run `kubectl rollout restart`, or put a hash of the ConfigMap in a pod-template annotation (Helm and "
     "Kustomize do this) so any change modifies the template and triggers a rolling update."),
]


# ====================================================================== CLASS 7
def day7():
    s = day_banner(7, "Storage, PersistentVolumes and StatefulSets",
                   "By the end you can give pods durable storage, explain PV/PVC/StorageClass, and run "
                   "a stateful app whose pods keep their names and their data.")
    s += covers([
        "Why container storage disappears",
        "Volume types: emptyDir, hostPath, configMap/secret, CSI",
        "PersistentVolume, PersistentVolumeClaim and binding",
        "StorageClass and dynamic provisioning",
        "Access modes, reclaim policies, volume expansion and snapshots",
        "StatefulSets: stable names, ordered startup, per-pod storage",
        "Lab: a StatefulSet that keeps its data after pod deletion",
    ], [["1", "Story and volumes", "10 min"],
        ["2", "PV, PVC, StorageClass", "20 min"],
        ["3", "StatefulSets", "15 min"],
        ["4", "Live lab", "25 min"],
        ["5", "Recap and interview questions", "10 min"]])
    s.append(P("7.1 The disappearing data problem", "h1"))
    s.append(story("Ravi ran MySQL as a Deployment. A node was patched and rebooted on Sunday, the MySQL pod "
                   "was recreated on another node... with an empty database. All test orders were gone. "
                   "Container file systems are temporary; the data had lived and died with the container."))
    s.append(P("A container's writable layer is deleted when the container is. Kubernetes <b>volumes</b> "
               "attach storage to a pod, and <b>persistent</b> volumes keep data beyond the life of any pod."))
    s += table(["Volume type", "Lifetime", "Use"], [
        ["emptyDir", "As long as the pod (survives container restarts)", "Scratch space, cache, sharing files between containers"],
        ["hostPath", "As long as the node", "Node agents reading /var/log; avoid for apps - ties pod to a node and is a security risk"],
        ["configMap / secret / downwardAPI", "Managed by Kubernetes", "Config files (Class 6)"],
        ["persistentVolumeClaim", "Independent of pods", "Databases, uploads, anything that must survive"],
        ["CSI drivers", "Defined by the storage system", "AWS EBS/EFS, Azure Disk/Files, GCE PD, Ceph, NFS"],
    ], cols(0.26, 0.30, 0.44))
    s.append(P("7.2 PersistentVolume and PersistentVolumeClaim", "h1"))
    s += bullets([
        "<b>PersistentVolume (PV)</b> - a piece of real storage in the cluster, created by an admin or "
        "automatically. Cluster-scoped.",
        "<b>PersistentVolumeClaim (PVC)</b> - a request for storage by a user: \"I need 1Gi, read-write by one "
        "node\". Namespaced. Kubernetes <b>binds</b> the claim to a matching PV.",
        "<b>Pod</b> - refers only to the PVC by name. It never needs to know where the disk really is.",
    ])
    s.append(real("A gym has lockers (PVs) of different sizes. A member fills a request slip: \"one medium "
                  "locker\" (PVC). The front desk assigns a locker that matches and gives the member the key. "
                  "The member only remembers \"my locker slip\", not the locker's serial number. If the "
                  "gym builds lockers on demand when a slip arrives, that is a StorageClass."))
    s.append(figure(D.storage(), "Figure 7.1 - A pod uses a PVC, which binds to a PV that a StorageClass can create on demand"))
    s.append(code("""apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mysql-data
spec:
  accessModes: ["ReadWriteOnce"]
  storageClassName: standard        # minikube's default class
  resources:
    requests:
      storage: 1Gi
---
# in the pod spec
  volumes:
    - name: data
      persistentVolumeClaim:
        claimName: mysql-data
  containers:
    - name: mysql
      volumeMounts:
        - name: data
          mountPath: /var/lib/mysql""", "pvc.yaml"))
    s += table(["Access mode", "Short", "Meaning"], [
        ["ReadWriteOnce", "RWO", "Mounted read-write by one node (most block disks)"],
        ["ReadOnlyMany", "ROX", "Mounted read-only by many nodes"],
        ["ReadWriteMany", "RWX", "Read-write by many nodes (NFS, EFS, Azure Files, CephFS)"],
        ["ReadWriteOncePod", "RWOP", "Read-write by exactly one pod"],
    ], cols(0.26, 0.12, 0.62))
    s += table(["Reclaim policy", "What happens to the PV when the PVC is deleted"], [
        ["Delete", "The PV and the real disk are deleted (default for dynamic provisioning)"],
        ["Retain", "The PV and data are kept for manual recovery - use for important data"],
        ["Recycle", "Deprecated - basic scrub; do not use"],
    ], cols(0.26, 0.74))
    s.append(P("7.3 StorageClass and dynamic provisioning", "h1"))
    s.append(P("Creating PVs by hand does not scale. A <b>StorageClass</b> describes a type of storage "
               "(fast SSD, cheap HDD, replicated) and the <b>provisioner</b> that creates it. When a PVC names "
               "a StorageClass, the disk and PV are created automatically. One StorageClass can be marked "
               "as the cluster default."))
    s.append(code("""apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
provisioner: ebs.csi.aws.com           # on AWS; minikube uses k8s.io/minikube-hostpath
parameters:
  type: gp3
reclaimPolicy: Retain
allowVolumeExpansion: true
volumeBindingMode: WaitForFirstConsumer   # create the disk in the zone where the pod lands"""))
    s.append(P("Other features you should know: <b>volume expansion</b> (edit the PVC to a larger size if the "
               "class allows it) and <b>VolumeSnapshots</b> (point-in-time backups through CSI). Tools like "
               "<b>Velero</b> back up whole namespaces including volumes."))
    s.append(P("7.4 StatefulSets", "h1"))
    s.append(P("A Deployment's pods are cattle: random names (`web-7d9f-x2b8l`), interchangeable, sharing one "
               "PVC if any. Databases, Kafka, Zookeeper and Elasticsearch need pets: each member has an identity "
               "and its own data. A <b>StatefulSet</b> provides:"))
    s += bullets([
        "<b>Stable, ordered names</b> - `web-0`, `web-1`, `web-2` - kept after rescheduling.",
        "<b>Stable DNS</b> through a headless Service - `web-0.web-hl.default.svc.cluster.local`.",
        "<b>Per-pod storage</b> via `volumeClaimTemplates` - `data-web-0`, `data-web-1`... which follow the pod.",
        "<b>Ordered operations</b> - created 0, 1, 2 and deleted 2, 1, 0 (configurable with `podManagementPolicy`).",
        "<b>Rolling updates</b> from the highest ordinal down, with `partition` for staged rollouts.",
    ])
    s.append(real("Train seats are numbered. If passenger in seat 12 goes to the washroom and comes back, "
                  "they return to seat 12 and their bag is still under it. That is a StatefulSet. A bus with "
                  "free seating - sit anywhere, no fixed bag space - is a Deployment."))
    s.append(figure(D.statefulset(), "Figure 7.2 - StatefulSet pods keep their name, DNS entry and own PVC"))
    s.append(code("""apiVersion: v1
kind: Service
metadata:
  name: web-hl
spec:
  clusterIP: None              # headless
  selector: { app: web-sts }
  ports: [{ port: 80 }]
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: web
spec:
  serviceName: web-hl
  replicas: 3
  selector:
    matchLabels: { app: web-sts }
  template:
    metadata:
      labels: { app: web-sts }
    spec:
      containers:
        - name: nginx
          image: nginx:1.27
          volumeMounts:
            - name: data
              mountPath: /usr/share/nginx/html
  volumeClaimTemplates:
    - metadata:
        name: data
      spec:
        accessModes: ["ReadWriteOnce"]
        resources:
          requests:
            storage: 100Mi""", "statefulset.yaml"))
    s.append(P("7.5 Live lab", "h1"))
    s.append(code("""kubectl get storageclass                      # 'standard (default)'
kubectl apply -f statefulset.yaml
kubectl get pods -l app=web-sts -w            # web-0, then web-1, then web-2
kubectl get pvc                               # data-web-0, data-web-1, data-web-2 - Bound
kubectl get pv

# give each pod its own page
0..2 | ForEach-Object {
  kubectl exec web-$_ -- sh -c "echo I am web-$_ > /usr/share/nginx/html/index.html"
}

kubectl run client --rm -it --image=busybox:1.36 -- sh
  wget -qO- web-1.web-hl                      # I am web-1
  nslookup web-hl                             # returns 3 pod IPs
  exit""", "PowerShell - part 1"))
    s.append(code("""kubectl delete pod web-1
kubectl get pods -l app=web-sts -w            # web-1 comes back with the SAME name
kubectl exec web-1 -- cat /usr/share/nginx/html/index.html   # still "I am web-1"

kubectl scale statefulset web --replicas=1    # web-2 then web-1 are removed
kubectl get pvc                               # PVCs are kept on purpose!
kubectl delete statefulset web; kubectl delete svc web-hl
kubectl delete pvc data-web-0 data-web-1 data-web-2""", "PowerShell - part 2"))
    s.append(mistake(["Deleting a StatefulSet does <b>not</b> delete its PVCs - this protects data, but costs "
                      "money in the cloud if forgotten.",
                      "Running a database with RWO storage as a Deployment with 2+ replicas - the second pod "
                      "cannot mount the disk or corrupts data.",
                      "Thinking a StatefulSet makes a database highly available by itself - replication is the "
                      "database's job; use an Operator for production databases."]))
    s.append(remember(["emptyDir lives with the pod; PVC data outlives pods.",
                       "PV = the storage, PVC = the request, StorageClass = the factory.",
                       "Access modes RWO/ROX/RWX/RWOP; reclaim Delete vs Retain.",
                       "StatefulSet = stable names + stable DNS + per-pod PVC + ordering."], "Class 7 recap"))
    s += interview(7, DAY7_QA)
    return s


DAY7_QA = [
    ("Why do we need volumes in Kubernetes?",
     "A container's file system is ephemeral - data is lost when the container restarts or the pod is "
     "replaced. Volumes provide storage that survives restarts and can be shared between containers."),
    ("What is an emptyDir volume?",
     "A volume created empty when a pod starts and deleted when the pod is removed. It survives container "
     "restarts and is used for scratch space or sharing files between containers. It can be RAM-backed with "
     "`medium: Memory`."),
    ("What is hostPath and why is it risky?",
     "It mounts a file or directory from the node into the pod. It ties the pod to that node's data and "
     "can expose the host file system, so it is used only for system agents, not applications."),
    ("What is a PersistentVolume?",
     "A cluster-scoped storage resource provisioned by an admin or dynamically by a StorageClass, with its "
     "own lifecycle independent of pods."),
    ("What is a PersistentVolumeClaim?",
     "A namespaced request for storage specifying size, access mode and optionally a StorageClass. Kubernetes "
     "binds it to a suitable PV; pods use storage by referencing the PVC."),
    ("Explain the PV and PVC binding process.",
     "When a PVC is created, the controller looks for a PV with enough capacity, matching access mode and "
     "class. If found, they bind one-to-one; if a StorageClass is set and no PV exists, one is dynamically "
     "provisioned. Otherwise the PVC stays Pending."),
    ("What is a StorageClass?",
     "An object describing a class of storage - provisioner, parameters, reclaim policy, expansion and "
     "binding mode - used for dynamic provisioning of PVs."),
    ("What is dynamic provisioning?",
     "Automatic creation of a PV and the underlying disk when a PVC requests a StorageClass, so admins do not "
     "need to pre-create volumes."),
    ("What access modes are available?",
     "ReadWriteOnce (one node read-write), ReadOnlyMany (many nodes read-only), ReadWriteMany (many nodes "
     "read-write) and ReadWriteOncePod (exactly one pod read-write)."),
    ("What are reclaim policies?",
     "They decide what happens to a PV after its PVC is deleted: Delete removes the PV and backing storage, "
     "Retain keeps them for manual recovery, and Recycle is deprecated."),
    ("What is volumeBindingMode WaitForFirstConsumer?",
     "It delays provisioning and binding until a pod using the PVC is scheduled, so the disk is created in "
     "the same zone as the pod. Immediate binding can place the disk in the wrong zone."),
    ("Can you resize a PVC?",
     "Yes, if the StorageClass has `allowVolumeExpansion: true`. Edit the PVC to a larger size; shrinking is "
     "not supported."),
    ("What is CSI?",
     "The Container Storage Interface - a standard that lets storage vendors write drivers for Kubernetes "
     "without changing Kubernetes code. EBS, Azure Disk and Ceph drivers are CSI drivers."),
    ("What is a StatefulSet?",
     "A workload controller for stateful applications that gives each pod a stable ordinal name, stable "
     "network identity through a headless Service, its own persistent storage, and ordered deployment and scaling."),
    ("StatefulSet vs Deployment?",
     "Deployment pods are interchangeable with random names and typically shared or no storage. StatefulSet "
     "pods have fixed names (app-0, app-1), stable DNS, per-pod PVCs and ordered start, stop and updates."),
    ("Why does a StatefulSet need a headless Service?",
     "The headless Service creates DNS records for each pod, such as `web-0.web-hl.ns.svc.cluster.local`, "
     "so peers and clients can reach a specific member."),
    ("What are volumeClaimTemplates?",
     "Templates in a StatefulSet from which a separate PVC is created for each pod (data-web-0, data-web-1). "
     "The PVC is reattached when that pod is rescheduled."),
    ("What happens to PVCs when you scale down or delete a StatefulSet?",
     "By default they are kept to protect data. Newer versions allow `persistentVolumeClaimRetentionPolicy` "
     "to delete them on scale-down or deletion."),
    ("How would you run a production database on Kubernetes?",
     "Use a StatefulSet managed by an Operator (for example CloudNativePG, Percona or Strimzi for Kafka) with "
     "replicated storage, backups, monitoring and anti-affinity - or use a managed cloud database."),
    ("What are VolumeSnapshots?",
     "CSI-based point-in-time copies of a PVC, defined with VolumeSnapshot and VolumeSnapshotClass objects. "
     "A new PVC can be restored from a snapshot."),
]


# ====================================================================== CLASS 8
def day8():
    s = day_banner(8, "Workload types and scheduling",
                   "By the end you can choose the right workload controller and control exactly where "
                   "pods run and how much CPU and memory they get.")
    s += covers([
        "DaemonSet, Job and CronJob - and when to use each controller",
        "How the scheduler picks a node",
        "nodeSelector, node affinity, pod affinity and anti-affinity",
        "Taints and tolerations; cordon and drain",
        "Resource requests and limits, QoS classes, OOMKilled",
        "PriorityClass, preemption and topology spread",
        "Lab: 3-node cluster - place, block and evict pods",
    ], [["1", "Story and workload types", "15 min"],
        ["2", "Scheduling rules", "20 min"],
        ["3", "Resources and QoS", "15 min"],
        ["4", "Live lab", "20 min"],
        ["5", "Recap and interview questions", "10 min"]])
    s.append(P("8.1 Choosing a workload controller", "h1"))
    s.append(story("Three new requests reached Ravi in one week: run a log collector on <b>every</b> server, "
                   "run a database cleanup <b>once</b>, and generate a sales report <b>every night at 2 AM</b>. "
                   "A Deployment fits none of them. Kubernetes has a controller for each."))
    s += table(["Controller", "Runs", "Typical use", "Everyday example"], [
        ["Deployment", "N interchangeable pods, forever", "Web apps, APIs", "Cooks on every shift"],
        ["StatefulSet", "N pods with identity and storage", "Databases, Kafka", "Numbered train seats"],
        ["DaemonSet", "One pod on each (matching) node", "Log/monitoring agents, CNI, kube-proxy", "A security guard on every floor"],
        ["Job", "Pods until a task completes", "Migrations, batch processing", "A one-time deep cleaning"],
        ["CronJob", "A Job on a schedule", "Backups, reports, cleanups", "A daily alarm clock"],
    ], cols(0.17, 0.25, 0.30, 0.28))
    s.append(figure(D.workloads(), "Figure 8.1 - A DaemonSet runs one pod per node; a CronJob creates Jobs on a schedule"))
    s.append(code("""apiVersion: batch/v1
kind: CronJob
metadata:
  name: nightly-report
spec:
  schedule: "0 2 * * *"            # min hour day month weekday
  concurrencyPolicy: Forbid        # Allow | Forbid | Replace
  successfulJobsHistoryLimit: 3
  jobTemplate:
    spec:
      backoffLimit: 4              # retries before marking failed
      completions: 1
      parallelism: 1
      activeDeadlineSeconds: 600
      ttlSecondsAfterFinished: 3600
      template:
        spec:
          restartPolicy: OnFailure
          containers:
            - name: report
              image: busybox:1.36
              command: ["sh", "-c", "echo Sales report generated at $(date)"]""", "cronjob.yaml"))
    s.append(P("8.2 How scheduling works", "h1"))
    s.append(P("For every new pod, the scheduler <b>filters</b> out nodes that cannot run it (not enough free "
               "requests, wrong labels, taints, port conflicts, volume zone) and then <b>scores</b> the "
               "rest (spread, balanced usage, affinity preferences). The highest-scoring node wins and the "
               "pod is bound to it. If no node passes the filter, the pod stays <b>Pending</b>."))
    s.append(figure(D.scheduling(), "Figure 8.2 - nodeSelector attracts pods; taints repel pods without a toleration"))
    s += table(["Tool", "Direction", "Example"], [
        ["nodeSelector", "Pod must land on nodes with a label", "`disk: ssd`"],
        ["Node affinity", "Like nodeSelector, with operators and required/preferred rules",
         "requiredDuringScheduling... `zone In [a, b]`"],
        ["Pod affinity", "Place near other pods", "Put cache next to the web app"],
        ["Pod anti-affinity", "Keep away from other pods", "Spread 3 replicas over 3 nodes for HA"],
        ["Taint (on node)", "Node repels pods", "`gpu=true:NoSchedule`"],
        ["Toleration (on pod)", "Pod is allowed on a tainted node", "`key: gpu, effect: NoSchedule`"],
        ["topologySpreadConstraints", "Spread evenly across zones/nodes", "`maxSkew: 1` per zone"],
    ], cols(0.26, 0.42, 0.32))
    s.append(real("Taints and tolerations work like a <b>VIP lounge</b> at an airport. The lounge (node) has "
                  "a sign \"members only\" (taint). Only passengers with a lounge card (toleration) may enter. "
                  "But having a card does not force you into the lounge - to force placement you also need "
                  "affinity or nodeSelector."))
    s += table(["Taint effect", "Behaviour"], [
        ["NoSchedule", "New pods without a toleration are not scheduled here"],
        ["PreferNoSchedule", "The scheduler tries to avoid the node, but may use it"],
        ["NoExecute", "New pods are blocked and existing pods without a toleration are evicted"],
    ], cols(0.26, 0.74))
    s.append(P("<b>Cordon</b> marks a node unschedulable (existing pods stay). <b>Drain</b> cordons it and "
               "safely evicts its pods - used before maintenance or upgrades. <b>Uncordon</b> brings it back."))
    s.append(P("8.3 Requests, limits and QoS", "h1"))
    s.append(code("""resources:
  requests:            # reserved; used by the scheduler
    cpu: 250m          # 250 millicores = 1/4 CPU
    memory: 128Mi
  limits:              # hard ceiling enforced on the node
    cpu: "1"
    memory: 256Mi"""))
    s.append(figure(D.resources(), "Figure 8.3 - Requests, limits and the three QoS classes"))
    s += bullets([
        "Over the <b>CPU limit</b>: the container is <b>throttled</b> (slowed down), never killed.",
        "Over the <b>memory limit</b>: the container is <b>OOMKilled</b> (exit code 137) and restarted.",
        "When a node runs short of memory, the kubelet <b>evicts</b> pods: BestEffort first, then Burstable, "
        "Guaranteed last.",
    ])
    s.append(real("Booking a restaurant table for 4 is the <b>request</b> - the restaurant reserves those "
                  "seats even if only 2 come. The fire-safety limit of 6 people per table is the <b>limit</b>. "
                  "If a seventh person squeezes in, the manager asks someone to leave (OOMKilled)."))
    s.append(P("<b>PriorityClass</b> gives pods a priority number. When the cluster is full, the scheduler "
               "may <b>preempt</b> (evict) lower-priority pods to make room for critical ones, such as "
               "payment over a nightly report."))
    s.append(P("8.4 Live lab: a 3-node cluster", "h1"))
    s.append(code("""apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: node-agent
spec:
  selector:
    matchLabels: { app: node-agent }
  template:
    metadata:
      labels: { app: node-agent }
    spec:
      containers:
        - name: agent
          image: busybox:1.36
          env:
            - name: NODE_NAME
              valueFrom: { fieldRef: { fieldPath: spec.nodeName } }
          command: ["sh", "-c", "while true; do echo collecting logs on $NODE_NAME; sleep 10; done"]""",
                  "ds.yaml"))
    s.append(code("""apiVersion: v1
kind: Pod
metadata:
  name: db
spec:
  nodeSelector:
    disk: ssd
  containers:
    - name: db
      image: nginx:1.27""", "db-pod.yaml"))
    s.append(code("""minikube start -p lab --nodes 3 --driver=docker
kubectl get nodes                               # lab, lab-m02, lab-m03

# DaemonSet: one pod per node
kubectl apply -f ds.yaml
kubectl get pods -o wide -l app=node-agent      # one per node
kubectl logs -l app=node-agent --prefix

# Job and CronJob
kubectl create job hello --image=busybox:1.36 -- echo "cleanup done"
kubectl get jobs; kubectl logs job/hello
kubectl apply -f cronjob.yaml
kubectl create job manual-run --from=cronjob/nightly-report""", "PowerShell - workloads"))
    s.append(code("""# nodeSelector
kubectl apply -f db-pod.yaml
kubectl get pod db                              # Pending - no node has disk=ssd yet
kubectl label node lab-m02 disk=ssd
kubectl get pod db -o wide                      # now Running on lab-m02

# taints
kubectl taint node lab-m03 gpu=true:NoSchedule
kubectl create deployment web --image=nginx:1.27 --replicas=6
kubectl get pods -o wide -l app=web             # none on lab-m03

# drain for maintenance
kubectl drain lab-m02 --ignore-daemonsets --delete-emptydir-data --force
kubectl get pods -o wide                        # pods moved away
kubectl uncordon lab-m02
kubectl taint node lab-m03 gpu=true:NoSchedule-   # remove taint""", "PowerShell - scheduling"))
    s.append(code("""apiVersion: v1
kind: Pod
metadata:
  name: memory-hog
spec:
  containers:
    - name: stress
      image: polinux/stress
      resources:
        limits: { memory: 100Mi }
        requests: { memory: 50Mi }
      command: ["stress"]
      args: ["--vm", "1", "--vm-bytes", "250M", "--vm-hang", "1"]""", "oom.yaml - try: kubectl apply, get pod -w, describe"))
    s.append(P("You will see <b>OOMKilled</b>, then CrashLoopBackOff. `kubectl describe pod memory-hog` shows "
               "`Last State: Terminated, Reason: OOMKilled, Exit Code: 137`. Clean up with "
               "`minikube delete -p lab`."))
    s.append(mistake(["Setting no requests: the scheduler thinks the pod needs nothing and overpacks nodes.",
                      "Setting CPU limits too low for Java apps: start-up becomes painfully slow due to throttling.",
                      "Expecting a toleration to <i>attract</i> a pod - it only <i>permits</i>; add affinity too."]))
    s.append(remember(["DaemonSet = one per node; Job = run to completion; CronJob = scheduled Job.",
                       "Scheduler: filter then score. Pending = no node passed the filter.",
                       "nodeSelector/affinity attract; taints repel; tolerations permit.",
                       "Requests reserve, limits cap. CPU throttles, memory OOMKills.",
                       "QoS: Guaranteed > Burstable > BestEffort."], "Class 8 recap"))
    s += interview(8, DAY8_QA)
    return s


DAY8_QA = [
    ("What is a DaemonSet? Give examples.",
     "A controller that runs one copy of a pod on every node, or every node matching a selector. New nodes "
     "automatically get the pod. Examples: log collectors (Fluent Bit), monitoring agents (node-exporter), "
     "kube-proxy and CNI agents."),
    ("What is a Job?",
     "A controller that runs pods until a specified number complete successfully. It retries failed pods up "
     "to backoffLimit (default 6). Used for batch tasks and migrations."),
    ("What is a CronJob?",
     "A controller that creates Jobs on a cron schedule, such as \"0 2 * * *\" for 2 AM daily, with settings "
     "for concurrency, history limits and deadlines."),
    ("Explain completions and parallelism in a Job.",
     "completions is how many successful pods are needed; parallelism is how many may run at once. "
     "completions 10 and parallelism 3 processes ten items three at a time."),
    ("What does concurrencyPolicy do in a CronJob?",
     "It controls overlapping runs: Allow (default) lets them overlap, Forbid skips a new run if the previous "
     "one is still running, Replace stops the old run and starts the new one."),
    ("How does the kube-scheduler decide where to place a pod?",
     "It filters nodes that satisfy requirements (resources, nodeSelector, affinity, taints, ports, volume "
     "topology), scores the remaining nodes by priorities such as spreading and balanced usage, and binds "
     "the pod to the highest-scoring node."),
    ("What is nodeSelector?",
     "The simplest placement constraint: a map of labels that a node must have for the pod to be scheduled there."),
    ("Node affinity vs nodeSelector?",
     "Node affinity is more expressive: operators like In, NotIn, Exists, Gt, and both hard "
     "(requiredDuringSchedulingIgnoredDuringExecution) and soft (preferred...) rules with weights."),
    ("What are pod affinity and anti-affinity?",
     "Rules based on labels of other pods. Affinity co-locates pods (cache with app); anti-affinity separates "
     "them, commonly to spread replicas across nodes or zones using topologyKey."),
    ("What are taints and tolerations?",
     "A taint on a node repels pods; a toleration on a pod allows it onto a node with a matching taint. "
     "They are used to dedicate nodes, for example GPU or control-plane nodes."),
    ("What are the taint effects?",
     "NoSchedule blocks new pods, PreferNoSchedule avoids the node if possible, and NoExecute also evicts "
     "existing pods that do not tolerate the taint."),
    ("Taints vs node affinity?",
     "Taints are node-centric and keep unwanted pods away; affinity is pod-centric and attracts pods to nodes. "
     "To dedicate nodes to specific pods you combine both."),
    ("What is the difference between cordon and drain?",
     "Cordon marks a node unschedulable but leaves existing pods. Drain cordons and evicts pods (respecting "
     "PodDisruptionBudgets) so maintenance can be done. Uncordon makes it schedulable again."),
    ("What are resource requests and limits?",
     "Requests are the CPU/memory guaranteed and used by the scheduler for placement. Limits are the maximum "
     "a container may use, enforced by the kubelet and Linux cgroups."),
    ("What happens when a container exceeds its CPU or memory limit?",
     "Exceeding CPU leads to throttling. Exceeding memory makes the kernel kill the container (OOMKilled, exit "
     "code 137) and the kubelet restarts it according to the restart policy."),
    ("What are QoS classes?",
     "Guaranteed (every container has requests equal to limits for CPU and memory), Burstable (some "
     "requests/limits set but not equal) and BestEffort (none set). Under memory pressure BestEffort is "
     "evicted first and Guaranteed last."),
    ("What does 250m CPU mean?",
     "250 millicores - a quarter of one CPU core. Memory uses binary units such as Mi and Gi."),
    ("What is a PriorityClass and preemption?",
     "A PriorityClass assigns an integer priority to pods. If a high-priority pod cannot be scheduled, the "
     "scheduler can preempt (evict) lower-priority pods to make room."),
    ("Why would a pod stay in Pending?",
     "Insufficient CPU/memory on all nodes, unmatched nodeSelector or affinity, untolerated taints, an unbound "
     "PVC, quota limits or no ready nodes. `kubectl describe pod` shows the scheduler's reason in Events."),
    ("What are topologySpreadConstraints?",
     "Rules that spread pods evenly across topology domains such as zones or nodes, using maxSkew, "
     "topologyKey and whenUnsatisfiable - improving high availability."),
]


# ====================================================================== CLASS 9
def day9():
    s = day_banner(9, "Health checks, autoscaling, monitoring and troubleshooting",
                   "By the end you can make apps self-heal with probes, scale automatically on load, "
                   "observe the cluster, and debug the most common failures quickly.")
    s += covers([
        "Liveness, readiness and startup probes - HTTP, TCP, exec, gRPC",
        "Graceful shutdown: preStop hooks and termination grace period",
        "HorizontalPodAutoscaler with metrics-server; VPA and Cluster Autoscaler",
        "PodDisruptionBudget for safe maintenance",
        "Monitoring and logging: kubectl top, Prometheus, Grafana, Loki",
        "A troubleshooting playbook for the common errors",
        "Lab: probe failures and a live autoscaling demo",
    ], [["1", "Story and probes", "15 min"],
        ["2", "Autoscaling and PDB", "15 min"],
        ["3", "Observability and troubleshooting", "15 min"],
        ["4", "Live lab", "25 min"],
        ["5", "Recap and interview questions", "10 min"]])
    s.append(P("9.1 Health probes", "h1"))
    s.append(story("During a sale the payment service froze - the process was alive but answered nothing. "
                   "Kubernetes saw a running container and kept sending it traffic. Another day, new pods "
                   "received orders before they had connected to the database, and the first 200 customers "
                   "got errors. Ravi needed Kubernetes to know not just \"is it running?\" but \"is it "
                   "healthy?\" and \"is it ready?\""))
    s.append(figure(D.probes(), "Figure 9.1 - The kubelet runs three kinds of probes; only Ready pods get Service traffic"))
    s += table(["Probe", "Question", "On failure"], [
        ["startupProbe", "Has the app finished starting?", "Keep waiting; other probes are paused. Kill after failureThreshold"],
        ["livenessProbe", "Is the app still alive or stuck?", "Container is restarted"],
        ["readinessProbe", "Can it serve traffic now?", "Pod removed from Service endpoints (not restarted)"],
    ], cols(0.2, 0.34, 0.46))
    s.append(real("Probes are like a hospital. The <b>startup</b> check: is the patient awake after surgery? "
                  "Do not judge anything else until then. The <b>liveness</b> check: is the heart beating? If "
                  "not, resuscitate (restart). The <b>readiness</b> check: is the doctor ready to see "
                  "patients? If on a break, the receptionist simply stops sending patients for a while."))
    s.append(code("""containers:
  - name: api
    image: my-api:2.1
    ports: [{ containerPort: 8080 }]
    startupProbe:
      httpGet: { path: /healthz, port: 8080 }
      failureThreshold: 30          # 30 x 5s = up to 150s to start
      periodSeconds: 5
    livenessProbe:
      httpGet: { path: /healthz, port: 8080 }
      periodSeconds: 10
      failureThreshold: 3
    readinessProbe:
      httpGet: { path: /ready, port: 8080 }   # checks DB connection, etc.
      periodSeconds: 5
    lifecycle:
      preStop:
        exec: { command: ["sh", "-c", "sleep 10"] }   # let load balancers drain
terminationGracePeriodSeconds: 30""", "Probe configuration"))
    s.append(P("Probe mechanisms: `httpGet` (2xx/3xx = healthy), `tcpSocket` (port opens), `exec` (command "
               "exits 0) and `grpc`. Useful tuning fields: `initialDelaySeconds`, `periodSeconds`, "
               "`timeoutSeconds`, `failureThreshold`, `successThreshold`."))
    s.append(P("When a pod is deleted, Kubernetes removes it from endpoints, runs the <b>preStop</b> hook, "
               "sends <b>SIGTERM</b>, waits up to `terminationGracePeriodSeconds` (default 30) and finally "
               "sends <b>SIGKILL</b>. Apps should finish in-flight requests on SIGTERM."))
    s.append(mistake(["Making the liveness probe check the database. If the DB blips, every pod restarts at "
                      "once. Liveness should only check the process itself; put dependencies in readiness.",
                      "No startupProbe for slow apps (Spring Boot, large Java apps) - liveness kills them before they finish booting."]))
    s.append(P("9.2 Autoscaling", "h1"))
    s += table(["Autoscaler", "Scales", "Based on"], [
        ["HorizontalPodAutoscaler (HPA)", "Number of pod replicas", "CPU, memory, or custom/external metrics"],
        ["VerticalPodAutoscaler (VPA)", "Requests/limits of each pod", "Historical usage (add-on)"],
        ["Cluster Autoscaler / Karpenter", "Number of nodes", "Pending pods that do not fit / idle nodes"],
        ["KEDA", "Replicas, even to zero", "Events: queue length, Kafka lag, cron"],
    ], cols(0.32, 0.30, 0.38))
    s.append(real("A supermarket opens extra billing counters when queues grow and closes them when it "
                  "is quiet - that is the HPA. Giving one cashier a faster scanner is the VPA. Renting the "
                  "shop next door when there is no space for more counters is the Cluster Autoscaler."))
    s.append(figure(D.hpa(), "Figure 9.2 - HPA reads metrics and changes the Deployment's replica count"))
    s.append(P("The HPA formula: `desired = ceil(current replicas x current metric / target)`. With 2 pods at "
               "90% CPU and a 50% target: ceil(2 x 90 / 50) = 4 pods. Scale-down waits for a stabilisation "
               "window (5 minutes by default) to avoid flapping. HPA needs <b>requests</b> to be set, because "
               "CPU percentage is measured against the request."))
    s.append(code("""apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: php-apache
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: php-apache
  minReplicas: 1
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target: { type: Utilization, averageUtilization: 50 }""", "hpa.yaml"))
    s.append(P("PodDisruptionBudget", "h2"))
    s.append(P("A <b>PDB</b> limits how many pods of an app may be down at once during <i>voluntary</i> "
               "disruptions such as `kubectl drain` or cluster upgrades: `minAvailable: 2` or "
               "`maxUnavailable: 1`. It does not protect against node crashes."))
    s.append(P("9.3 Observability", "h1"))
    s += table(["Need", "Tool"], [
        ["Quick CPU/memory numbers", "`kubectl top nodes`, `kubectl top pods` (needs metrics-server)"],
        ["Metrics, alerts, dashboards", "Prometheus + Alertmanager + Grafana (kube-prometheus-stack Helm chart)"],
        ["Central logs", "Fluent Bit / Fluentd shipping to Loki, Elasticsearch/OpenSearch or a cloud service"],
        ["Distributed tracing", "OpenTelemetry with Jaeger or Tempo"],
        ["Cluster events", "`kubectl get events -A --sort-by=.lastTimestamp`"],
    ], cols(0.3, 0.7))
    s.append(P("9.4 Troubleshooting playbook", "h1"))
    s.append(figure(D.troubleshoot(), "Figure 9.3 - Start from the pod status and follow the matching path"))
    s += table(["Symptom", "First command", "Typical fix"], [
        ["Pending", "`kubectl describe pod`", "Lower requests, add nodes, fix nodeSelector/taint, bind the PVC"],
        ["ErrImagePull / ImagePullBackOff", "`kubectl describe pod`", "Correct image/tag, add imagePullSecrets"],
        ["CrashLoopBackOff", "`kubectl logs --previous`", "Fix the app error, command, env or config"],
        ["OOMKilled (exit 137)", "`kubectl describe pod`", "Raise memory limit or fix the memory leak"],
        ["CreateContainerConfigError", "`kubectl describe pod`", "Create the missing ConfigMap/Secret or key"],
        ["Running but 0/1 Ready", "`kubectl describe pod`", "Fix the readiness probe path/port or the dependency"],
        ["Service not reachable", "`kubectl get endpointslices`", "Fix selector labels, targetPort, NetworkPolicy"],
        ["Node NotReady", "`kubectl describe node`", "Check kubelet, disk/memory pressure, network"],
    ], cols(0.28, 0.28, 0.44))
    s.append(P("For images without a shell, attach a debugging container: "
               "`kubectl debug -it <pod> --image=busybox:1.36 --target=<container>`. "
               "`kubectl debug node/<node> -it --image=busybox:1.36` opens a shell on a node."))
    s.append(P("9.5 Live lab", "h1"))
    s.append(code("""apiVersion: v1
kind: Pod
metadata:
  name: liveness-demo
spec:
  containers:
    - name: app
      image: busybox:1.36
      args: ["sh", "-c", "touch /tmp/healthy; sleep 30; rm -f /tmp/healthy; sleep 600"]
      livenessProbe:
        exec: { command: ["cat", "/tmp/healthy"] }
        initialDelaySeconds: 5
        periodSeconds: 5""", "liveness.yaml - after ~45 s RESTARTS goes up"))
    s.append(code("""kubectl apply -f liveness.yaml
kubectl get pod liveness-demo -w
kubectl describe pod liveness-demo        # "Liveness probe failed: cat: can't open..."

minikube addons enable metrics-server
kubectl create deployment php-apache --image=registry.k8s.io/hpa-example
kubectl set resources deployment php-apache --requests=cpu=200m --limits=cpu=500m
kubectl expose deployment php-apache --port=80
kubectl apply -f hpa.yaml
kubectl get hpa -w                         # keep this window open

# second window - generate load:
kubectl run load --rm -it --image=busybox:1.36 -- `
  sh -c "while true; do wget -q -O- http://php-apache; done"
# watch TARGETS climb above 50% and REPLICAS grow; press Ctrl+C to stop load
kubectl top pods""", "PowerShell"))
    s.append(P("After you stop the load, replicas return to 1 after about five minutes. Clean up: "
               "`kubectl delete hpa php-apache; kubectl delete deploy,svc php-apache; kubectl delete pod liveness-demo`."))
    s.append(remember(["Startup protects slow boots; liveness restarts; readiness removes from traffic.",
                       "Graceful shutdown: preStop -> SIGTERM -> grace period -> SIGKILL.",
                       "HPA scales pods (needs requests + metrics-server); VPA resizes; Cluster Autoscaler adds nodes.",
                       "PDB keeps a minimum running during drains and upgrades.",
                       "Debug order: get -> describe -> logs -> events -> exec/debug."], "Class 9 recap"))
    s += interview(9, DAY9_QA)
    return s


DAY9_QA = [
    ("What are liveness, readiness and startup probes?",
     "Liveness checks whether a container should be restarted; readiness checks whether it should receive "
     "traffic; startup checks whether the application has finished starting and holds off the other probes "
     "until it has."),
    ("What happens when a liveness probe fails versus a readiness probe?",
     "A failing liveness probe makes the kubelet restart the container. A failing readiness probe removes the "
     "pod from Service endpoints without restarting it, and it is added back when it passes again."),
    ("When do you need a startup probe?",
     "For applications with long or unpredictable start-up times, such as large Java apps. It prevents the "
     "liveness probe from killing the container before it is up."),
    ("What probe mechanisms are available?",
     "httpGet (success on status 200-399), tcpSocket (port accepts a connection), exec (command exits 0) and grpc."),
    ("Name important probe parameters.",
     "initialDelaySeconds, periodSeconds, timeoutSeconds, failureThreshold and successThreshold."),
    ("Should a liveness probe check the database?",
     "No. If the database has a problem every pod would restart, making things worse. Liveness should check "
     "only the process; dependency checks belong in readiness."),
    ("Explain graceful termination of a pod.",
     "The pod is marked Terminating and removed from endpoints, the preStop hook runs, the container gets "
     "SIGTERM, Kubernetes waits up to terminationGracePeriodSeconds (default 30) and then sends SIGKILL."),
    ("What is the HorizontalPodAutoscaler?",
     "A controller that adjusts the replica count of a Deployment, StatefulSet or ReplicaSet based on observed "
     "metrics such as CPU, memory, or custom and external metrics, within min and max bounds."),
    ("What are the prerequisites for CPU-based HPA?",
     "A metrics source such as metrics-server and CPU requests defined on the containers, because utilisation "
     "is calculated as a percentage of the request."),
    ("How does the HPA calculate the desired replicas?",
     "desiredReplicas = ceil(currentReplicas x currentMetricValue / targetValue). Scale-down uses a "
     "stabilisation window (300 seconds by default) to avoid flapping."),
    ("What is the VerticalPodAutoscaler?",
     "An add-on that recommends or automatically sets CPU and memory requests based on historical usage. It "
     "should not be combined with HPA on the same CPU or memory metric."),
    ("What is the Cluster Autoscaler?",
     "A component that adds nodes when pods are Pending because of insufficient resources and removes "
     "under-used nodes. Karpenter is a faster, more flexible alternative on AWS and other clouds."),
    ("What is a PodDisruptionBudget?",
     "A policy limiting how many pods of an application can be unavailable during voluntary disruptions like "
     "drains and upgrades, using minAvailable or maxUnavailable."),
    ("How do you check resource usage of pods and nodes?",
     "`kubectl top pods` and `kubectl top nodes`, which need metrics-server. For history and alerts use "
     "Prometheus and Grafana."),
    ("How is logging typically done in Kubernetes?",
     "Apps write to stdout/stderr; the runtime stores logs on the node; a DaemonSet agent such as Fluent Bit "
     "ships them to a central store such as Loki, Elasticsearch or a cloud logging service."),
    ("How would you troubleshoot a pod in CrashLoopBackOff?",
     "Check `kubectl logs --previous`, then `kubectl describe pod` for exit code, reason (OOMKilled) and "
     "events. Verify command, args, env vars, ConfigMaps/Secrets, probes and resource limits; reproduce with "
     "`kubectl debug` if needed."),
    ("What does exit code 137 mean?",
     "The container was killed with SIGKILL (128 + 9), usually OOMKilled for exceeding its memory limit, or "
     "killed after the grace period."),
    ("How do you debug a container that has no shell?",
     "Use `kubectl debug -it <pod> --image=busybox --target=<container>` to attach an ephemeral container "
     "that shares the process namespace, or copy the pod with `--copy-to`."),
    ("How do you view cluster events?",
     "`kubectl get events -n <ns> --sort-by=.lastTimestamp` or the Events section of `kubectl describe`. "
     "Events are kept for about one hour by default."),
    ("What is the difference between monitoring and observability?",
     "Monitoring watches known metrics and alerts on thresholds. Observability combines metrics, logs and "
     "traces so you can ask new questions and understand unknown failures."),
]


# ====================================================================== CLASS 10
def day10():
    s = day_banner(10, "Security, GitOps and production Kubernetes",
                   "By the end you can secure a cluster with RBAC, pod security and NetworkPolicies, "
                   "explain GitOps, and describe how Kubernetes runs in real companies.")
    s += covers([
        "Authentication, authorization (RBAC) and admission",
        "ServiceAccounts, Roles, ClusterRoles and bindings",
        "securityContext and Pod Security Admission",
        "NetworkPolicies",
        "CI/CD and GitOps with Argo CD",
        "Managed Kubernetes, high availability, service mesh and cost",
        "Final project: deploy WordPress + MySQL end to end",
    ], [["1", "Story, RBAC and pod security", "25 min"],
        ["2", "NetworkPolicies", "15 min"],
        ["3", "CI/CD, GitOps and production topics", "15 min"],
        ["4", "Live lab and final project brief", "20 min"],
        ["5", "Recap and interview questions", "10 min"]])
    s.append(P("10.1 Who can do what? (RBAC)", "h1"))
    s.append(story("An intern ran `kubectl delete namespace prod` thinking he was on his test cluster. "
                   "He had full admin rights because everyone shared one kubeconfig. QuickBite was down for an "
                   "hour. Ravi was asked to make sure \"people and apps get only the access they need\"."))
    s.append(P("Every API request passes three gates: <b>authentication</b> (who are you? - certificates, "
               "tokens, cloud IAM, OIDC), <b>authorization</b> (are you allowed? - RBAC) and <b>admission "
               "control</b> (is the request acceptable? - quotas, Pod Security, policy engines)."))
    s.append(figure(D.rbac(), "Figure 10.1 - RBAC connects a subject to a set of permissions through a binding"))
    s += table(["Object", "Scope", "Purpose"], [
        ["Role", "Namespace", "Permissions (verbs on resources) inside one namespace"],
        ["ClusterRole", "Cluster", "Permissions cluster-wide or for cluster-scoped resources; reusable in namespaces"],
        ["RoleBinding", "Namespace", "Grants a Role or ClusterRole to subjects within one namespace"],
        ["ClusterRoleBinding", "Cluster", "Grants a ClusterRole across the whole cluster"],
        ["ServiceAccount", "Namespace", "Identity for pods/apps talking to the API"],
    ], cols(0.24, 0.16, 0.60))
    s.append(real("Office ID cards. Your card (ServiceAccount or user) says who you are. The access policy "
                  "(Role) says \"can open the 3rd-floor store room\". The HR register entry (RoleBinding) "
                  "links your card to that policy. Without an entry, the door stays shut - default deny."))
    s.append(code("""apiVersion: v1
kind: ServiceAccount
metadata: { name: viewer, namespace: dev }
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata: { name: pod-reader, namespace: dev }
rules:
  - apiGroups: [""]
    resources: ["pods", "pods/log"]
    verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata: { name: viewer-reads-pods, namespace: dev }
subjects:
  - kind: ServiceAccount
    name: viewer
    namespace: dev
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io""", "rbac.yaml"))
    s.append(P("10.2 Securing pods", "h1"))
    s.append(code("""spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 2000
    seccompProfile: { type: RuntimeDefault }
  containers:
    - name: app
      image: my-api:2.1
      securityContext:
        allowPrivilegeEscalation: false
        readOnlyRootFilesystem: true
        capabilities: { drop: ["ALL"] }""", "Hardened securityContext"))
    s.append(P("<b>Pod Security Admission</b> enforces the Pod Security Standards per namespace with a label: "
               "`privileged` (anything), `baseline` (blocks known escalations) or `restricted` (best practice). "
               "Example: `kubectl label ns prod pod-security.kubernetes.io/enforce=restricted`. It replaced "
               "the old PodSecurityPolicy, removed in v1.25. For custom rules teams add <b>Kyverno</b> or "
               "<b>OPA Gatekeeper</b>."))
    s += table(["Security layer", "Good practice"], [
        ["Images", "Small base images, pinned tags or digests, scanned with Trivy/Grype, signed with cosign"],
        ["API access", "RBAC least privilege, no shared admin kubeconfig, SSO/OIDC, audit logs"],
        ["Pods", "Non-root, read-only file system, drop capabilities, Pod Security `restricted`"],
        ["Network", "Default-deny NetworkPolicies, TLS everywhere, service mesh mTLS (Istio, Linkerd)"],
        ["Secrets", "Encryption at rest, external secret managers, no secrets in Git"],
        ["Nodes & cluster", "Patch regularly, private API endpoint, CIS benchmark (kube-bench)"],
    ], cols(0.22, 0.78))
    s.append(P("10.3 NetworkPolicies", "h1"))
    s.append(P("By default every pod can talk to every other pod. A <b>NetworkPolicy</b> selects pods by "
               "label and lists which traffic is allowed in (ingress) and out (egress). Once a pod is "
               "selected by any policy, everything not allowed is denied. Policies need a CNI that "
               "enforces them - Calico, Cilium or the cloud equivalents; Flannel alone does not."))
    s.append(real("A housing society gate: by default anyone walks in. After the committee adds rules - "
                  "\"only residents and registered delivery partners may enter Tower B\" - the guard stops "
                  "everyone else. The guard is the CNI; the rule book is the NetworkPolicy."))
    s.append(figure(D.netpol(), "Figure 10.2 - Only the frontend may call the backend, and only the backend may call MySQL"))
    s.append(code("""apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: backend-allow-frontend, namespace: shop }
spec:
  podSelector:
    matchLabels: { app: backend }
  policyTypes: ["Ingress"]
  ingress:
    - from:
        - podSelector:
            matchLabels: { app: frontend }
      ports:
        - port: 80""", "netpol.yaml"))
    s.append(P("10.4 CI/CD and GitOps", "h1"))
    s.append(P("In <b>push-based CI/CD</b> a pipeline (Jenkins, GitHub Actions, GitLab CI, Azure DevOps) "
               "builds the image and runs `kubectl apply` or `helm upgrade` against the cluster. In "
               "<b>GitOps</b>, Git holds the desired state and an agent inside the cluster - <b>Argo CD</b> or "
               "<b>Flux</b> - pulls and applies it continuously, reverting manual drift. The manifests in Git "
               "are usually packaged as a Helm chart or Kustomize overlays - both are covered in depth in "
               "Class 11."))
    s.append(real("GitOps is like a building's approved floor plan kept at the municipal office. If someone "
                  "secretly adds a wall, the inspector compares the building with the plan and removes it. "
                  "To change the building, you first get the plan changed and approved (a pull request)."))
    s.append(figure(D.gitops(), "Figure 10.3 - GitOps flow: Git is the single source of truth and Argo CD keeps the cluster in sync"))
    s.append(code("""apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: guestbook
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/argoproj/argocd-example-apps.git
    targetRevision: HEAD
    path: guestbook
  destination:
    server: https://kubernetes.default.svc
    namespace: guestbook
  syncPolicy:
    automated: { prune: true, selfHeal: true }   # delete removed objects, undo manual edits
    syncOptions: ["CreateNamespace=true"]""", "argocd-app.yaml"))
    s.append(P("10.5 Kubernetes in production", "h1"))
    s += table(["Topic", "What you should know"], [
        ["Managed Kubernetes", "EKS (AWS), AKS (Azure), GKE (Google): the cloud runs the control plane; you manage nodes and workloads"],
        ["Self-managed", "kubeadm (official), k3s (lightweight), Rancher, OpenShift (enterprise distribution)"],
        ["High availability", "3 control-plane nodes, etcd quorum, nodes across availability zones, anti-affinity, PDBs"],
        ["Upgrades", "One minor version at a time: control plane first, then nodes (drain, upgrade, uncordon)"],
        ["Backup", "`etcdctl snapshot save` for etcd; Velero for namespaces and volumes"],
        ["CRDs", "CustomResourceDefinitions add new object types, e.g. `Certificate`, `Application`, `PostgresCluster`"],
        ["Operators", "A CRD plus a controller that encodes human operational knowledge - install, backup, failover"],
        ["Service mesh", "Istio, Linkerd: mTLS, retries, traffic splitting and telemetry without code changes"],
        ["Cost", "Right-size requests, autoscale nodes, use spot instances for stateless work, delete unused volumes/LBs"],
    ], cols(0.22, 0.78))
    s.append(funfact("Many cluster add-ons you met in this course are themselves Operators built on CRDs - "
                     "cert-manager (`Certificate`), Argo CD (`Application`), Prometheus Operator "
                     "(`ServiceMonitor`). Kubernetes is a platform for building platforms."))
    s.append(P("10.6 Live lab: security and GitOps", "h1"))
    s.append(code("""kubectl create namespace dev
kubectl apply -f rbac.yaml
kubectl auth can-i list pods -n dev --as=system:serviceaccount:dev:viewer      # yes
kubectl auth can-i delete pods -n dev --as=system:serviceaccount:dev:viewer    # no
kubectl auth can-i list secrets -n dev --as=system:serviceaccount:dev:viewer   # no
kubectl auth can-i --list -n dev --as=system:serviceaccount:dev:viewer""", "PowerShell - RBAC"))
    s.append(code("""minikube start -p secure --cni=calico --driver=docker
kubectl create namespace shop
kubectl -n shop run backend  --image=nginx:1.27 --labels=app=backend --port=80
kubectl -n shop expose pod backend --port=80
kubectl -n shop run frontend --image=busybox:1.36 --labels=app=frontend -- sleep 3600
kubectl -n shop run random   --image=busybox:1.36 --labels=app=random   -- sleep 3600

kubectl -n shop exec frontend -- wget -qO- -T 3 backend     # works
kubectl apply -f netpol.yaml
kubectl -n shop exec frontend -- wget -qO- -T 3 backend     # still works
kubectl -n shop exec random   -- wget -qO- -T 3 backend     # times out - blocked
minikube delete -p secure""", "PowerShell - NetworkPolicy"))
    s.append(code("""kubectl create namespace argocd
kubectl apply -n argocd --server-side `
  -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
kubectl -n argocd get pods -w                  # wait until all are Running

# admin password, then open https://localhost:8080 (user: admin)
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}"
kubectl -n argocd port-forward svc/argocd-server 8080:443

kubectl apply -f argocd-app.yaml               # in a second window
kubectl -n guestbook get pods                  # deployed from Git by Argo CD
kubectl -n guestbook scale deploy guestbook-ui --replicas=5
kubectl -n guestbook get deploy guestbook-ui -w   # selfHeal puts it back to 1""", "PowerShell - Argo CD"))
    s.append(P("The password is base64-encoded - decode it as shown in Class 6. Remove Argo CD afterwards "
               "with `kubectl delete namespace argocd guestbook`."))
    s.append(P("10.7 Final project: WordPress + MySQL", "h1"))
    s.append(P("Put the whole course together. Build it in a namespace called `blog`, store every file "
               "in a Git repository, and tick each item as you go:"))
    s += table(["Step", "Objects", "Concept from class"], [
        ["1", "Namespace `blog` with a ResourceQuota and LimitRange", "5"],
        ["2", "Secret `mysql-pass` with root and user passwords", "6"],
        ["3", "MySQL StatefulSet (`mysql:8.0`) + headless Service + 1Gi volumeClaimTemplate", "4, 7"],
        ["4", "ConfigMap with WordPress settings (DB host `mysql-0.mysql`, DB name)", "6"],
        ["5", "WordPress Deployment (2 replicas) with readiness/liveness probes and requests/limits", "3, 8, 9"],
        ["6", "ClusterIP Service + Ingress for `blog.local`", "4, 5"],
        ["7", "HPA for WordPress (CPU 60%, 2-5 replicas) and a PDB (minAvailable 1)", "9"],
        ["8", "NetworkPolicy: only WordPress pods can reach MySQL on 3306", "10"],
        ["9", "Delete the MySQL pod and prove posts survive; roll out a new WordPress tag and roll back", "3, 7"],
        ["10", "Bonus: convert everything into a Helm chart and deploy it with Argo CD", "10, 11"],
    ], cols(0.1, 0.7, 0.2))
    s.append(remember(["Every request: authentication -> authorization (RBAC) -> admission.",
                       "Role/RoleBinding = namespace; ClusterRole/ClusterRoleBinding = cluster.",
                       "Harden pods: non-root, read-only FS, drop capabilities, Pod Security `restricted`.",
                       "NetworkPolicy = firewall for pods (needs Calico/Cilium).",
                       "GitOps = Git is the truth; Argo CD pulls, syncs and self-heals drift."],
                      "Class 10 recap"))
    s += interview(10, DAY10_QA)
    return s


DAY10_QA = [
    ("What is RBAC in Kubernetes?",
     "Role-Based Access Control: an authorization mechanism where Roles and ClusterRoles define allowed verbs "
     "on resources, and RoleBindings and ClusterRoleBindings grant them to users, groups or ServiceAccounts. "
     "Everything not granted is denied."),
    ("Role vs ClusterRole?",
     "A Role grants permissions within one namespace. A ClusterRole is cluster-wide and can cover "
     "cluster-scoped resources such as nodes, or be reused in many namespaces through RoleBindings."),
    ("RoleBinding vs ClusterRoleBinding?",
     "A RoleBinding grants a Role or ClusterRole within a single namespace. A ClusterRoleBinding grants a "
     "ClusterRole across all namespaces."),
    ("What is a ServiceAccount?",
     "A namespaced identity for processes running in pods. Pods get a short-lived token automatically "
     "mounted, used to call the API server with the permissions bound to that ServiceAccount."),
    ("How do you check if a user or ServiceAccount can perform an action?",
     "`kubectl auth can-i <verb> <resource> -n <ns> --as=<user>` - for a ServiceAccount use "
     "`--as=system:serviceaccount:<ns>:<name>`; `--list` shows all permissions."),
    ("What are the stages an API request goes through?",
     "Authentication (who), authorization (allowed, usually RBAC), then mutating and validating admission "
     "controllers (defaults, quotas, Pod Security, webhooks), and finally persistence in etcd."),
    ("What is a securityContext?",
     "Pod or container settings that control privileges: runAsUser, runAsNonRoot, fsGroup, "
     "readOnlyRootFilesystem, allowPrivilegeEscalation, capabilities, seccomp and SELinux options."),
    ("What replaced PodSecurityPolicy?",
     "Pod Security Admission, which enforces the Pod Security Standards (privileged, baseline, restricted) "
     "per namespace through labels. Kyverno or OPA Gatekeeper add custom policies."),
    ("What is a NetworkPolicy?",
     "A namespaced object that controls pod-level ingress and egress traffic using pod selectors, namespace "
     "selectors, IP blocks and ports. Pods selected by a policy deny all traffic not explicitly allowed."),
    ("Does every cluster enforce NetworkPolicies?",
     "No. Enforcement depends on the CNI plugin. Calico, Cilium and most cloud CNIs support it; plain Flannel "
     "does not, so policies would have no effect."),
    ("How do you create a default-deny policy for a namespace?",
     "A NetworkPolicy with an empty podSelector (`{}`) and policyTypes Ingress (and Egress) but no rules. It "
     "selects all pods and allows nothing, and specific allow policies are added on top."),
    ("Why should containers not run as root?",
     "If an attacker breaks out of a root container they may gain root on the node. Running as a non-root "
     "user with dropped capabilities, no privilege escalation and a read-only file system limits the damage."),
    ("What are admission webhooks?",
     "HTTP callbacks the API server calls during admission. Mutating webhooks can change objects (inject "
     "sidecars, add defaults); validating webhooks can reject them. Kyverno, Gatekeeper and Istio use them."),
    ("How do you make sure only trusted images run in the cluster?",
     "Scan images in CI (Trivy, Grype), sign them (cosign/Sigstore), and enforce policies with Kyverno or "
     "Gatekeeper that allow only approved registries, pinned tags or digests, and verified signatures."),
    ("What is Kubernetes audit logging?",
     "The API server can record who did what and when for every request, according to an audit policy. "
     "Audit logs are essential for security investigations and compliance."),
    ("What is GitOps?",
     "An operating model where the desired state of the system is stored in Git and an in-cluster agent "
     "(Argo CD, Flux) continuously pulls and reconciles it, giving audit history, easy rollback via git revert, "
     "and drift correction."),
    ("What is Argo CD?",
     "A declarative GitOps continuous-delivery tool for Kubernetes. It watches Git repositories, compares "
     "them with live cluster state, shows differences in a UI, and syncs automatically or on demand."),
    ("What are CRDs and Operators?",
     "A CustomResourceDefinition extends the Kubernetes API with new object types. An Operator is a "
     "controller that watches those custom resources and automates operational tasks such as installing, "
     "backing up, scaling and failing over complex applications."),
    ("How do you upgrade a Kubernetes cluster?",
     "Read release notes and deprecations, back up etcd, upgrade one minor version at a time - control plane "
     "first, then worker nodes one by one with drain, upgrade kubelet, uncordon - using PDBs to keep apps "
     "available. Managed services automate much of this."),
    ("What are managed Kubernetes services and why use them?",
     "EKS, AKS and GKE run and patch the control plane, integrate with cloud IAM, load balancers and storage, "
     "and offer node autoscaling. Teams focus on workloads instead of operating etcd and the API server."),
]


# ====================================================================== CLOSING
def closing():
    s = [Bookmark("cheatsheet", "kubectl cheat sheet"), P("kubectl cheat sheet", "h1")]
    s += table(["Task", "Command"], [
        ["Cluster info", "`kubectl cluster-info`, `kubectl get nodes -o wide`"],
        ["List everything in a namespace", "`kubectl get all -n <ns>`"],
        ["All namespaces", "`kubectl get pods -A`"],
        ["Details and events", "`kubectl describe pod <name>`"],
        ["YAML of a live object", "`kubectl get deploy web -o yaml`"],
        ["Generate YAML", "`kubectl create deploy web --image=nginx --dry-run=client -o yaml`"],
        ["Apply / delete files", "`kubectl apply -f file.yaml`, `kubectl delete -f file.yaml`"],
        ["Preview changes", "`kubectl diff -f file.yaml`"],
        ["Logs", "`kubectl logs <pod> -c <ctr> -f --previous`"],
        ["Shell", "`kubectl exec -it <pod> -- sh`"],
        ["Debug container", "`kubectl debug -it <pod> --image=busybox:1.36 --target=<ctr>`"],
        ["Port forward", "`kubectl port-forward svc/web 8080:80`"],
        ["Scale", "`kubectl scale deploy web --replicas=5`"],
        ["Update image", "`kubectl set image deploy/web nginx=nginx:1.27`"],
        ["Rollout", "`kubectl rollout status|history|undo|restart deploy/web`"],
        ["Expose", "`kubectl expose deploy web --port=80 --type=NodePort`"],
        ["Labels", "`kubectl get pods -l app=web --show-labels`"],
        ["Resource usage", "`kubectl top pods`, `kubectl top nodes`"],
        ["Events", "`kubectl get events --sort-by=.lastTimestamp`"],
        ["Contexts", "`kubectl config get-contexts`, `use-context`, `set-context --current --namespace=x`"],
        ["Permissions", "`kubectl auth can-i <verb> <resource> --as=<user>`"],
        ["Node maintenance", "`kubectl cordon|drain|uncordon <node>`"],
        ["Docs", "`kubectl explain deploy.spec.strategy`, `kubectl api-resources`"],
        ["Kustomize", "`kubectl kustomize overlays/prod`, `kubectl apply -k overlays/prod`"],
    ], cols(0.3, 0.7))
    s.append(P("Helm cheat sheet", "h2"))
    s += table(["Task", "Command"], [
        ["Add and refresh a repository", "`helm repo add <name> <url>`, `helm repo update`"],
        ["Find charts", "`helm search repo <word>`, `helm search hub <word>`"],
        ["See settings of a chart", "`helm show values <repo/chart>`"],
        ["Install / upgrade in one command", "`helm upgrade --install <rel> <chart> -n <ns> --create-namespace -f values.yaml`"],
        ["Safe upgrade", "`helm upgrade <rel> <chart> --atomic --wait --timeout 5m`"],
        ["List and inspect releases", "`helm list -A`, `helm status <rel>`, `helm get values|manifest <rel>`"],
        ["History and rollback", "`helm history <rel>`, `helm rollback <rel> <revision>`"],
        ["Remove", "`helm uninstall <rel> -n <ns>`"],
        ["Create and check a chart", "`helm create <name>`, `helm lint`, `helm template`, `--dry-run --debug`"],
        ["Dependencies", "`helm dependency update`"],
        ["Test a release", "`helm test <rel>`"],
        ["Package and publish", "`helm package <dir>`, `helm push <tgz> oci://<registry>/<path>`"],
    ], cols(0.3, 0.7))
    s.append(tryit(["Add `Set-Alias k kubectl` to your PowerShell profile (`notepad $PROFILE`) and type `k get pods`.",
                    "Enable completion: `kubectl completion powershell | Out-String | Invoke-Expression`."],
                   "Speed tips"))

    s += [PageBreak(), Bookmark("coverage", "Concept coverage map"), P("Concept coverage map", "h1"),
          P("Use this map to revise a topic quickly. Every major Kubernetes concept in the CKAD/CKA "
            "syllabus is covered somewhere in the eleven classes.")]
    s += table(["Concept", "Class"], [
        ["Architecture, control plane, nodes, etcd, kubelet, kube-proxy, CRI", "1"],
        ["Desired state, controllers, reconciliation, self-healing", "1, 3"],
        ["Pods, multi-container, init and sidecar containers, static pods", "2"],
        ["Labels, selectors, annotations, YAML, kubectl", "2"],
        ["ReplicaSet, Deployment, rolling update, rollback, blue-green, canary", "3"],
        ["Services (ClusterIP, NodePort, LoadBalancer, ExternalName, headless), EndpointSlices", "4"],
        ["CoreDNS, networking model, CNI, kube-proxy", "4"],
        ["Ingress, IngressClass, TLS, Gateway API", "5"],
        ["Namespaces, ResourceQuota, LimitRange, kubeconfig and contexts", "5"],
        ["ConfigMaps, Secrets, Downward API, imagePullSecrets", "6"],
        ["Volumes, PV, PVC, StorageClass, CSI, access modes, snapshots", "7"],
        ["StatefulSet and headless Services", "7"],
        ["DaemonSet, Job, CronJob", "8"],
        ["Scheduling: nodeSelector, affinity, anti-affinity, taints, tolerations, topology spread", "8"],
        ["Requests, limits, QoS, OOMKilled, PriorityClass, cordon/drain", "8"],
        ["Probes, lifecycle hooks, graceful shutdown", "9"],
        ["HPA, VPA, Cluster Autoscaler, KEDA, PodDisruptionBudget", "9"],
        ["Monitoring, logging, troubleshooting, kubectl debug", "9"],
        ["Authentication, RBAC, ServiceAccounts, admission, Pod Security, securityContext", "10"],
        ["NetworkPolicy", "10"],
        ["CI/CD, GitOps (Argo CD), managed Kubernetes, high availability, service mesh", "10"],
        ["Helm: charts, templates, values, releases, hooks, tests, dependencies, OCI packaging", "11"],
        ["Kustomize: base, overlays, patches, generators", "11"],
        ["imagePullPolicy, owner references, garbage collection, finalizers", "11"],
        ["CRDs and Operators", "10, 11"],
        ["kubeadm cluster setup, cluster upgrades, etcd backup and restore", "11"],
    ], cols(0.84, 0.16))

    s += [Bookmark("glossary", "Everyday-example glossary"), P("Everyday-example glossary", "h1"),
          P("If you forget a concept, remember its everyday example first - the definition follows easily.")]
    s += table(["Kubernetes term", "Remember it as"], [
        ["Cluster / control plane / node", "A restaurant chain / its head office / its branches"],
        ["etcd", "The head office's master register book"],
        ["Scheduler", "HR deciding which branch a new cook joins"],
        ["kubelet", "The branch manager reporting to head office"],
        ["Reconciliation loop", "An AC thermostat holding 24 degrees"],
        ["Pod", "A flat - one address, shared kitchen"],
        ["Labels and selectors", "Supermarket stickers and the manager's instruction"],
        ["Deployment", "A manager always keeping 3 cooks on shift"],
        ["Rolling update", "Changing a bus's tyres one at a time while it runs"],
        ["Service", "The restaurant's fixed phone number"],
        ["Ingress", "A mall's main entrance and directory board"],
        ["Namespace", "Floors in one office building"],
        ["ConfigMap / Secret", "The notice board / a locker"],
        ["PV / PVC / StorageClass", "A gym locker / the request slip / the locker factory"],
        ["StatefulSet", "Numbered train seats with your bag underneath"],
        ["DaemonSet / Job / CronJob", "A guard on every floor / a one-time cleaning / an alarm clock"],
        ["Taint and toleration", "An airport VIP lounge and the lounge card"],
        ["Requests and limits", "A table booking and the fire-safety maximum"],
        ["Probes", "Hospital checks: awake? heartbeat? ready for patients?"],
        ["HPA", "Opening extra supermarket billing counters"],
        ["RBAC", "Office ID cards and the access register"],
        ["NetworkPolicy", "Housing-society gate rules"],
        ["Helm", "A phone app store with update and rollback"],
        ["Helm chart and values", "A wedding-card design and the names filled in"],
        ["Kustomize", "A tailor altering a ready-made kurta"],
        ["GitOps", "The approved floor plan the inspector checks against"],
        ["Operator", "An expert employee who runs one complex system for you"],
    ], cols(0.38, 0.62))

    s += [PageBreak(), Bookmark("checklist", "Final checklist and next steps"),
          P("Final checklist - can you do these without notes?", "h1")]
    s += bullets([
        "Draw the Kubernetes architecture and explain every component in one sentence.",
        "Explain what happens, step by step, after `kubectl apply -f deploy.yaml`.",
        "Write Pod, Deployment and Service YAML from memory (or generate it with dry-run).",
        "Perform a rolling update and a rollback, and explain maxSurge and maxUnavailable.",
        "Expose an app with ClusterIP, NodePort, LoadBalancer and Ingress.",
        "Inject configuration with a ConfigMap and a Secret, and explain why base64 is not security.",
        "Give a database persistent storage with a PVC and explain StatefulSets.",
        "Place pods with nodeSelector, affinity and taints; set requests and limits.",
        "Add liveness, readiness and startup probes and autoscale with an HPA.",
        "Debug Pending, ImagePullBackOff, CrashLoopBackOff and OOMKilled pods.",
        "Restrict access with RBAC and traffic with a NetworkPolicy.",
        "Explain GitOps and deploy an app from Git with Argo CD.",
        "Install, upgrade and roll back a public Helm chart with your own values.",
        "Write a Helm chart with templates, helpers, per-environment values and a hook, then package it.",
        "Create Kustomize overlays for dev and prod.",
        "Explain kubeadm setup, the cluster upgrade order and how to back up etcd.",
    ])
    s.append(P("Where to go next", "h2"))
    s += bullets([
        "<b>Certifications</b> - CKAD (application developer), CKA (administrator), CKS (security). All "
        "are hands-on exams; the labs in these notes are the right kind of practice.",
        "<b>Practise daily</b> - rebuild the final project from scratch until it takes under 30 minutes.",
        "<b>Try a real cloud</b> - create a small EKS, AKS or GKE cluster with free credits and deploy "
        "your project there. Delete it afterwards to avoid charges.",
        "<b>Official docs</b> - kubernetes.io/docs has tutorials and the full API reference.",
    ])
    s.append(remember("Kubernetes looks big, but it is one idea repeated everywhere: you declare the desired "
                      "state, and a controller works forever to make reality match it. Keep practising!",
                      "Last word from TRISHA ACADEMY"))
    return s
