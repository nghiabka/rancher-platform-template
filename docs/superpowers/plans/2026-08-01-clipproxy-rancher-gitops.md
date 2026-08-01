# Clipproxy Rancher GitOps Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deploy `clipproxy` to the Rancher-managed Kubernetes lab cluster through ArgoCD GitOps and rename the existing `cliprouter` source directory to `clipproxy`.

**Architecture:** Add a new Kustomize app at `gitops/apps/clipproxy/` with separate API and manager deployments, internal services, PVC-backed data, and an Ingress for the manager UI at `clipproxy.local`. Wire it into the existing local app-of-apps path with an ArgoCD `Application` named `clipproxy-local`.

**Tech Stack:** Rancher-managed Kubernetes, ArgoCD, Kustomize, Kubernetes Deployment/Service/Ingress/PVC/ConfigMap/Secret, Docker Compose reference files, Pytest, Markdown.

## Global Constraints

- Rename `cliprouter/` to `clipproxy/`.
- Add Kubernetes manifests under `gitops/apps/clipproxy/`.
- Add a local ArgoCD `Application` at `gitops/clusters/local/clipproxy.yaml`.
- Include the new application in `gitops/clusters/local/kustomization.yaml`.
- Add namespace `clipproxy` to `gitops/platform/00-namespaces/namespaces.yaml`.
- Expose the manager UI with an Ingress host of `clipproxy.local`.
- Use PVCs for data that was previously stored with Docker volumes.
- Avoid committing real secrets.
- Add lightweight repository tests for the important GitOps wiring.
- Document the deploy steps for Rancher/Kubernetes users.
- Running Docker Compose is not the production deployment path.
- Do not install or reconfigure Rancher itself.
- Do not install a new ingress controller.
- Do not choose a real public DNS name.
- Do not commit production secret values.
- Do not add TLS certificates in the first implementation.
- Do not add monitoring, logging, or backup resources specifically for `clipproxy`.
- Do not run `kubectl`, Docker, Helm, or deployment commands unless the user explicitly asks.
- Do not print or inspect secret files.
- If the third-party images require root or writable filesystem behavior, document the exact limitation instead of weakening security globally.
- During execution, commit only if the user explicitly authorizes commits.

---

## File Structure

- `clipproxy/config.yaml` — renamed source config for the API container; remains the local reference config that the Kubernetes ConfigMap mirrors.
- `clipproxy/docker-compose.yml` — renamed Docker Compose reference; service names and container names use `clipproxy` while Kubernetes is the primary deploy path.
- `tests/test_clipproxy_gitops.py` — focused string/path tests for rename, GitOps wiring, manifests, secret handling, and documentation.
- `gitops/platform/00-namespaces/namespaces.yaml` — platform namespace list; add `clipproxy` without weakening existing namespaces.
- `gitops/clusters/local/clipproxy.yaml` — ArgoCD `Application` for the local `clipproxy` overlay.
- `gitops/clusters/local/kustomization.yaml` — local app-of-apps resource list; include `clipproxy.yaml`.
- `gitops/apps/clipproxy/base/configmap.yaml` — ConfigMap containing `config.yaml` for `clipproxy-api`.
- `gitops/apps/clipproxy/base/pvc-api.yaml` — persistent claim for `/root/.cli-proxy-api`.
- `gitops/apps/clipproxy/base/deployment-api.yaml` — API deployment using `eceasy/cli-proxy-api:latest`.
- `gitops/apps/clipproxy/base/service-api.yaml` — internal API service on port `8317`.
- `gitops/apps/clipproxy/base/pvc-manager.yaml` — persistent claim for `/data`.
- `gitops/apps/clipproxy/base/deployment-manager.yaml` — manager deployment using `seakee/cpa-manager-plus:latest` and secret-backed keys.
- `gitops/apps/clipproxy/base/service-manager.yaml` — internal manager service on port `18317`.
- `gitops/apps/clipproxy/base/ingress.yaml` — Ingress routing `clipproxy.local/` to the manager service.
- `gitops/apps/clipproxy/base/kustomization.yaml` — base resource list and app labels.
- `gitops/apps/clipproxy/overlays/local/kustomization.yaml` — local overlay pointing to the base and setting namespace `clipproxy`.
- `gitops/apps/clipproxy/overlays/local/secret.example.yaml` — non-applied example Secret file with non-production example values.
- `docs/clipproxy-rancher-deploy.md` — step-by-step Rancher/Kubernetes deployment guide.

## Task 1: Rename the source directory to `clipproxy`

**Files:**
- Create: `tests/test_clipproxy_gitops.py`
- Rename: `cliprouter/` -> `clipproxy/`
- Modify: `clipproxy/docker-compose.yml`

**Interfaces:**
- Consumes: existing `cliprouter/config.yaml` and `cliprouter/docker-compose.yml`.
- Produces: canonical source paths `clipproxy/config.yaml` and `clipproxy/docker-compose.yml` for docs and GitOps ConfigMap content.

- [ ] **Step 1: Write the failing rename test**

Create `tests/test_clipproxy_gitops.py` with this initial content:

```python
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_repo_file(relative_path: str) -> str:
    return (ROOT / relative_path).read_text()


def test_clipproxy_source_directory_replaces_cliprouter():
    assert (ROOT / "clipproxy").is_dir()
    assert not (ROOT / "cliprouter").exists()
    assert (ROOT / "clipproxy/config.yaml").is_file()
    assert (ROOT / "clipproxy/docker-compose.yml").is_file()

    compose = read_repo_file("clipproxy/docker-compose.yml")
    assert "clipproxy-api:" in compose
    assert "container_name: clipproxy-api" in compose
    assert "clipproxy-manager:" in compose
    assert "container_name: clipproxy-manager" in compose
    assert "CPA_UPSTREAM_URL: \"http://clipproxy-api:8317\"" in compose
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
python3 -m pytest tests/test_clipproxy_gitops.py -q
```

Expected: fail because `clipproxy/` does not exist yet and `cliprouter/` still exists.

- [ ] **Step 3: Rename the directory**

Run:

```bash
mv cliprouter clipproxy
```

- [ ] **Step 4: Update the Docker Compose reference names**

Replace `clipproxy/docker-compose.yml` with:

```yaml
services:
  clipproxy-api:
    image: eceasy/cli-proxy-api:latest
    container_name: clipproxy-api
    restart: unless-stopped
    ports:
      - "8317:8317"
    volumes:
      - ./config.yaml:/CLIProxyAPI/config.yaml
      - ./cpa-data:/root/.cli-proxy-api

  clipproxy-manager:
    image: seakee/cpa-manager-plus:latest
    container_name: clipproxy-manager
    restart: unless-stopped
    ports:
      - "18317:18317"
    environment:
      HTTP_ADDR: "0.0.0.0:18317"
      CPA_MANAGER_ADMIN_KEY: "example-admin-key-change-me"
      CPA_UPSTREAM_URL: "http://clipproxy-api:8317"
      CPA_MANAGEMENT_KEY: "example-management-key-change-me"
      USAGE_DB_PATH: "/data/usage.sqlite"
      CPA_MANAGER_DATA_KEY_PATH: "/data/data.key"
      USAGE_COLLECTOR_MODE: "auto"
      USAGE_BATCH_SIZE: "100"
      USAGE_POLL_INTERVAL_MS: "500"
    volumes:
      - clipproxy-manager-data:/data
    depends_on:
      - clipproxy-api

volumes:
  clipproxy-manager-data:
```

- [ ] **Step 5: Re-run the rename test**

Run:

```bash
python3 -m pytest tests/test_clipproxy_gitops.py -q
```

Expected: pass.

- [ ] **Step 6: Commit the rename if commits are authorized**

Use this focused commit message only after the user explicitly authorizes commits:

```bash
git add clipproxy tests/test_clipproxy_gitops.py
git add -u cliprouter
git commit -m "refactor(clipproxy): rename cliprouter source directory"
```

## Task 2: Add ArgoCD app and namespace wiring

**Files:**
- Modify: `tests/test_clipproxy_gitops.py`
- Modify: `gitops/platform/00-namespaces/namespaces.yaml`
- Create: `gitops/clusters/local/clipproxy.yaml`
- Modify: `gitops/clusters/local/kustomization.yaml`

**Interfaces:**
- Consumes: local ArgoCD app-of-apps pattern from `gitops/clusters/local/sample-api.yaml`.
- Produces: ArgoCD entrypoint `clipproxy-local`, destination namespace `clipproxy`, and local kustomization reference `clipproxy.yaml`.

- [ ] **Step 1: Add the failing GitOps wiring test**

Append these tests to `tests/test_clipproxy_gitops.py`:

```python

def test_clipproxy_namespace_is_declared():
    namespaces = read_repo_file("gitops/platform/00-namespaces/namespaces.yaml")

    assert "name: clipproxy" in namespaces


def test_clipproxy_argocd_application_is_wired_into_local_cluster():
    app = read_repo_file("gitops/clusters/local/clipproxy.yaml")
    local = read_repo_file("gitops/clusters/local/kustomization.yaml")

    assert "kind: Application" in app
    assert "name: clipproxy-local" in app
    assert "namespace: argocd" in app
    assert "repoURL: https://github.com/nghiabka/rancher-platform-template.git" in app
    assert "targetRevision: main" in app
    assert "path: gitops/apps/clipproxy/overlays/local" in app
    assert "namespace: clipproxy" in app
    assert "prune: true" in app
    assert "selfHeal: true" in app
    assert "CreateNamespace=true" in app
    assert "- clipproxy.yaml" in local
```

- [ ] **Step 2: Run the wiring tests to verify they fail**

Run:

```bash
python3 -m pytest tests/test_clipproxy_gitops.py -q
```

Expected: fail because the namespace and ArgoCD Application do not exist yet.

- [ ] **Step 3: Add the `clipproxy` namespace**

Append this document to `gitops/platform/00-namespaces/namespaces.yaml`:

```yaml
---
apiVersion: v1
kind: Namespace
metadata:
  name: clipproxy
```

This namespace intentionally has no restricted pod-security labels in this first version because the upstream images use root-oriented paths such as `/root/.cli-proxy-api`. Do not remove or change labels from existing namespaces.

- [ ] **Step 4: Create the ArgoCD Application**

Create `gitops/clusters/local/clipproxy.yaml`:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: clipproxy-local
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/nghiabka/rancher-platform-template.git
    targetRevision: main
    path: gitops/apps/clipproxy/overlays/local
  destination:
    server: https://kubernetes.default.svc
    namespace: clipproxy
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
```

- [ ] **Step 5: Include the app in the local kustomization**

Update `gitops/clusters/local/kustomization.yaml` to:

```yaml
resources:
  - platform.yaml
  - sample-api.yaml
  - clipproxy.yaml
```

- [ ] **Step 6: Re-run the wiring tests**

Run:

```bash
python3 -m pytest tests/test_clipproxy_gitops.py -q
```

Expected: pass for the rename and GitOps wiring tests. Tests for manifests will be added in later tasks.

- [ ] **Step 7: Commit the wiring if commits are authorized**

Use this focused commit message only after the user explicitly authorizes commits:

```bash
git add gitops/platform/00-namespaces/namespaces.yaml gitops/clusters/local/clipproxy.yaml gitops/clusters/local/kustomization.yaml tests/test_clipproxy_gitops.py
git commit -m "feat(clipproxy): add local argocd application"
```

## Task 3: Add the `clipproxy-api` Kubernetes base

**Files:**
- Modify: `tests/test_clipproxy_gitops.py`
- Create: `gitops/apps/clipproxy/base/configmap.yaml`
- Create: `gitops/apps/clipproxy/base/pvc-api.yaml`
- Create: `gitops/apps/clipproxy/base/deployment-api.yaml`
- Create: `gitops/apps/clipproxy/base/service-api.yaml`
- Create: `gitops/apps/clipproxy/base/kustomization.yaml`
- Create: `gitops/apps/clipproxy/overlays/local/kustomization.yaml`

**Interfaces:**
- Consumes: `clipproxy/config.yaml` content and `clipproxy-api` service name from the approved design.
- Produces: internal API service `clipproxy-api:8317`, config mount `/CLIProxyAPI/config.yaml`, data mount `/root/.cli-proxy-api`, and overlay path consumed by `clipproxy-local`.

- [ ] **Step 1: Add the failing API manifest test**

Append this test to `tests/test_clipproxy_gitops.py`:

```python

def test_clipproxy_api_base_manifests_are_defined():
    kustomization = read_repo_file("gitops/apps/clipproxy/base/kustomization.yaml")
    configmap = read_repo_file("gitops/apps/clipproxy/base/configmap.yaml")
    pvc = read_repo_file("gitops/apps/clipproxy/base/pvc-api.yaml")
    deployment = read_repo_file("gitops/apps/clipproxy/base/deployment-api.yaml")
    service = read_repo_file("gitops/apps/clipproxy/base/service-api.yaml")
    overlay = read_repo_file("gitops/apps/clipproxy/overlays/local/kustomization.yaml")

    assert "- configmap.yaml" in kustomization
    assert "- pvc-api.yaml" in kustomization
    assert "- deployment-api.yaml" in kustomization
    assert "- service-api.yaml" in kustomization
    assert "app.kubernetes.io/name: clipproxy" in kustomization
    assert "app.kubernetes.io/part-of: rancher-platform-template" in kustomization

    assert "name: clipproxy-config" in configmap
    assert "config.yaml: |" in configmap
    assert "port: 8317" in configmap
    assert "allow-remote: true" in configmap

    assert "name: clipproxy-api-data" in pvc
    assert "ReadWriteOnce" in pvc
    assert "storage: 1Gi" in pvc

    assert "name: clipproxy-api" in deployment
    assert "image: eceasy/cli-proxy-api:latest" in deployment
    assert "containerPort: 8317" in deployment
    assert "mountPath: /CLIProxyAPI/config.yaml" in deployment
    assert "subPath: config.yaml" in deployment
    assert "mountPath: /root/.cli-proxy-api" in deployment
    assert "claimName: clipproxy-api-data" in deployment

    assert "name: clipproxy-api" in service
    assert "type: ClusterIP" in service
    assert "port: 8317" in service
    assert "targetPort: http" in service

    assert "- ../../base" in overlay
    assert "namespace: clipproxy" in overlay
```

- [ ] **Step 2: Run the API manifest test to verify it fails**

Run:

```bash
python3 -m pytest tests/test_clipproxy_gitops.py -q
```

Expected: fail because the `gitops/apps/clipproxy/` files do not exist yet.

- [ ] **Step 3: Create the API ConfigMap**

Create `gitops/apps/clipproxy/base/configmap.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: clipproxy-config
data:
  config.yaml: |
    host: ""
    port: 8317
    remote-management:
      allow-remote: true
      secret-key: "$2a$10$tU4j5YeYeiYJ1EWSBYrdDe16f6MDwKYK8Y9n/Ef.H0BLL8XMBxEBO"
      disable-control-panel: false
    plugins:
      enabled: true
    usage-statistics-enabled: true
    redis-usage-queue-retention-seconds: 60
```

- [ ] **Step 4: Create the API PVC**

Create `gitops/apps/clipproxy/base/pvc-api.yaml`:

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: clipproxy-api-data
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
```

- [ ] **Step 5: Create the API Deployment**

Create `gitops/apps/clipproxy/base/deployment-api.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: clipproxy-api
spec:
  replicas: 1
  selector:
    matchLabels:
      app.kubernetes.io/name: clipproxy
      app.kubernetes.io/component: api
  template:
    metadata:
      labels:
        app.kubernetes.io/name: clipproxy
        app.kubernetes.io/component: api
    spec:
      containers:
        - name: clipproxy-api
          image: eceasy/cli-proxy-api:latest
          imagePullPolicy: IfNotPresent
          ports:
            - name: http
              containerPort: 8317
          readinessProbe:
            tcpSocket:
              port: http
            initialDelaySeconds: 5
            periodSeconds: 10
          livenessProbe:
            tcpSocket:
              port: http
            initialDelaySeconds: 15
            periodSeconds: 20
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 500m
              memory: 512Mi
          volumeMounts:
            - name: config
              mountPath: /CLIProxyAPI/config.yaml
              subPath: config.yaml
            - name: data
              mountPath: /root/.cli-proxy-api
      volumes:
        - name: config
          configMap:
            name: clipproxy-config
        - name: data
          persistentVolumeClaim:
            claimName: clipproxy-api-data
```

- [ ] **Step 6: Create the API Service**

Create `gitops/apps/clipproxy/base/service-api.yaml`:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: clipproxy-api
spec:
  type: ClusterIP
  selector:
    app.kubernetes.io/name: clipproxy
    app.kubernetes.io/component: api
  ports:
    - name: http
      port: 8317
      targetPort: http
```

- [ ] **Step 7: Create the base kustomization with API resources**

Create `gitops/apps/clipproxy/base/kustomization.yaml`:

```yaml
resources:
  - configmap.yaml
  - pvc-api.yaml
  - deployment-api.yaml
  - service-api.yaml

labels:
  - pairs:
      app.kubernetes.io/name: clipproxy
      app.kubernetes.io/part-of: rancher-platform-template
```

- [ ] **Step 8: Create the local overlay kustomization**

Create `gitops/apps/clipproxy/overlays/local/kustomization.yaml`:

```yaml
resources:
  - ../../base

namespace: clipproxy
```

- [ ] **Step 9: Re-run the API manifest test**

Run:

```bash
python3 -m pytest tests/test_clipproxy_gitops.py -q
```

Expected: pass for rename, GitOps wiring, and API manifest tests.

- [ ] **Step 10: Commit the API base if commits are authorized**

Use this focused commit message only after the user explicitly authorizes commits:

```bash
git add gitops/apps/clipproxy tests/test_clipproxy_gitops.py
git commit -m "feat(clipproxy): add api gitops base"
```

## Task 4: Add manager, secret example, PVC, service, and Ingress

**Files:**
- Modify: `tests/test_clipproxy_gitops.py`
- Modify: `gitops/apps/clipproxy/base/kustomization.yaml`
- Create: `gitops/apps/clipproxy/base/pvc-manager.yaml`
- Create: `gitops/apps/clipproxy/base/deployment-manager.yaml`
- Create: `gitops/apps/clipproxy/base/service-manager.yaml`
- Create: `gitops/apps/clipproxy/base/ingress.yaml`
- Create: `gitops/apps/clipproxy/overlays/local/secret.example.yaml`

**Interfaces:**
- Consumes: internal API service `http://clipproxy-api:8317` from Task 3 and Kubernetes Secret name `clipproxy-secret`.
- Produces: manager service `clipproxy-manager:18317`, Ingress host `clipproxy.local`, data mount `/data`, and non-applied secret example file.

- [ ] **Step 1: Add the failing manager and ingress test**

Append this test to `tests/test_clipproxy_gitops.py`:

```python

def test_clipproxy_manager_secret_pvc_service_and_ingress_are_defined():
    kustomization = read_repo_file("gitops/apps/clipproxy/base/kustomization.yaml")
    pvc = read_repo_file("gitops/apps/clipproxy/base/pvc-manager.yaml")
    deployment = read_repo_file("gitops/apps/clipproxy/base/deployment-manager.yaml")
    service = read_repo_file("gitops/apps/clipproxy/base/service-manager.yaml")
    ingress = read_repo_file("gitops/apps/clipproxy/base/ingress.yaml")
    example_secret = read_repo_file("gitops/apps/clipproxy/overlays/local/secret.example.yaml")
    overlay = read_repo_file("gitops/apps/clipproxy/overlays/local/kustomization.yaml")

    assert "- pvc-manager.yaml" in kustomization
    assert "- deployment-manager.yaml" in kustomization
    assert "- service-manager.yaml" in kustomization
    assert "- ingress.yaml" in kustomization

    assert "name: clipproxy-manager-data" in pvc
    assert "ReadWriteOnce" in pvc
    assert "storage: 1Gi" in pvc

    assert "name: clipproxy-manager" in deployment
    assert "image: seakee/cpa-manager-plus:latest" in deployment
    assert "containerPort: 18317" in deployment
    assert "name: CPA_UPSTREAM_URL" in deployment
    assert "value: http://clipproxy-api:8317" in deployment
    assert "name: CPA_MANAGER_ADMIN_KEY" in deployment
    assert "name: CPA_MANAGEMENT_KEY" in deployment
    assert "secretKeyRef:" in deployment
    assert "name: clipproxy-secret" in deployment
    assert "key: CPA_MANAGER_ADMIN_KEY" in deployment
    assert "key: CPA_MANAGEMENT_KEY" in deployment
    assert "mountPath: /data" in deployment
    assert "claimName: clipproxy-manager-data" in deployment
    assert "CPA_MANAGER_ADMIN_KEY_TEST" not in deployment
    assert "CPA_MANAGEMENT_KEY_TEST" not in deployment

    assert "name: clipproxy-manager" in service
    assert "type: ClusterIP" in service
    assert "port: 18317" in service
    assert "targetPort: http" in service

    assert "kind: Ingress" in ingress
    assert "name: clipproxy" in ingress
    assert "ingressClassName: nginx" in ingress
    assert "host: clipproxy.local" in ingress
    assert "name: clipproxy-manager" in ingress
    assert "name: http" in ingress

    assert "kind: Secret" in example_secret
    assert "name: clipproxy-secret" in example_secret
    assert "namespace: clipproxy" in example_secret
    assert "CPA_MANAGER_ADMIN_KEY: example-admin-key-change-me" in example_secret
    assert "CPA_MANAGEMENT_KEY: example-management-key-change-me" in example_secret
    assert "- secret.example.yaml" not in overlay
```

- [ ] **Step 2: Run the manager and ingress test to verify it fails**

Run:

```bash
python3 -m pytest tests/test_clipproxy_gitops.py -q
```

Expected: fail because manager, ingress, and secret example files do not exist yet.

- [ ] **Step 3: Create the manager PVC**

Create `gitops/apps/clipproxy/base/pvc-manager.yaml`:

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: clipproxy-manager-data
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
```

- [ ] **Step 4: Create the manager Deployment**

Create `gitops/apps/clipproxy/base/deployment-manager.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: clipproxy-manager
spec:
  replicas: 1
  selector:
    matchLabels:
      app.kubernetes.io/name: clipproxy
      app.kubernetes.io/component: manager
  template:
    metadata:
      labels:
        app.kubernetes.io/name: clipproxy
        app.kubernetes.io/component: manager
    spec:
      containers:
        - name: clipproxy-manager
          image: seakee/cpa-manager-plus:latest
          imagePullPolicy: IfNotPresent
          ports:
            - name: http
              containerPort: 18317
          env:
            - name: HTTP_ADDR
              value: 0.0.0.0:18317
            - name: CPA_UPSTREAM_URL
              value: http://clipproxy-api:8317
            - name: CPA_MANAGER_ADMIN_KEY
              valueFrom:
                secretKeyRef:
                  name: clipproxy-secret
                  key: CPA_MANAGER_ADMIN_KEY
            - name: CPA_MANAGEMENT_KEY
              valueFrom:
                secretKeyRef:
                  name: clipproxy-secret
                  key: CPA_MANAGEMENT_KEY
            - name: USAGE_DB_PATH
              value: /data/usage.sqlite
            - name: CPA_MANAGER_DATA_KEY_PATH
              value: /data/data.key
            - name: USAGE_COLLECTOR_MODE
              value: auto
            - name: USAGE_BATCH_SIZE
              value: "100"
            - name: USAGE_POLL_INTERVAL_MS
              value: "500"
          readinessProbe:
            tcpSocket:
              port: http
            initialDelaySeconds: 5
            periodSeconds: 10
          livenessProbe:
            tcpSocket:
              port: http
            initialDelaySeconds: 15
            periodSeconds: 20
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 500m
              memory: 512Mi
          volumeMounts:
            - name: data
              mountPath: /data
      volumes:
        - name: data
          persistentVolumeClaim:
            claimName: clipproxy-manager-data
```

- [ ] **Step 5: Create the manager Service**

Create `gitops/apps/clipproxy/base/service-manager.yaml`:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: clipproxy-manager
spec:
  type: ClusterIP
  selector:
    app.kubernetes.io/name: clipproxy
    app.kubernetes.io/component: manager
  ports:
    - name: http
      port: 18317
      targetPort: http
```

- [ ] **Step 6: Create the manager Ingress**

Create `gitops/apps/clipproxy/base/ingress.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: clipproxy
spec:
  ingressClassName: nginx
  rules:
    - host: clipproxy.local
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: clipproxy-manager
                port:
                  name: http
```

- [ ] **Step 7: Create the non-applied secret example**

Create `gitops/apps/clipproxy/overlays/local/secret.example.yaml`:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: clipproxy-secret
  namespace: clipproxy
type: Opaque
stringData:
  CPA_MANAGER_ADMIN_KEY: example-admin-key-change-me
  CPA_MANAGEMENT_KEY: example-management-key-change-me
```

- [ ] **Step 8: Add manager resources to the base kustomization**

Replace `gitops/apps/clipproxy/base/kustomization.yaml` with:

```yaml
resources:
  - configmap.yaml
  - pvc-api.yaml
  - deployment-api.yaml
  - service-api.yaml
  - pvc-manager.yaml
  - deployment-manager.yaml
  - service-manager.yaml
  - ingress.yaml

labels:
  - pairs:
      app.kubernetes.io/name: clipproxy
      app.kubernetes.io/part-of: rancher-platform-template
```

Keep `gitops/apps/clipproxy/overlays/local/kustomization.yaml` as:

```yaml
resources:
  - ../../base

namespace: clipproxy
```

The example secret file must not be listed in `resources:` because it contains lab example values.

- [ ] **Step 9: Re-run the manager and ingress test**

Run:

```bash
python3 -m pytest tests/test_clipproxy_gitops.py -q
```

Expected: pass for rename, GitOps wiring, API manifests, manager manifests, secret reference, and ingress checks.

- [ ] **Step 10: Commit the manager and ingress resources if commits are authorized**

Use this focused commit message only after the user explicitly authorizes commits:

```bash
git add gitops/apps/clipproxy tests/test_clipproxy_gitops.py
git commit -m "feat(clipproxy): add manager ingress and secret wiring"
```

## Task 5: Add the Rancher/Kubernetes deploy guide

**Files:**
- Modify: `tests/test_clipproxy_gitops.py`
- Create: `docs/clipproxy-rancher-deploy.md`

**Interfaces:**
- Consumes: ArgoCD Application name `clipproxy-local`, namespace `clipproxy`, Ingress host `clipproxy.local`, services `clipproxy-api` and `clipproxy-manager`, and secret name `clipproxy-secret`.
- Produces: user-facing deployment guide that explains the GitOps path and manual verification commands without requiring Docker Compose.

- [ ] **Step 1: Add the failing deploy guide test**

Append this test to `tests/test_clipproxy_gitops.py`:

```python

def test_clipproxy_rancher_deploy_guide_documents_gitops_flow():
    guide = read_repo_file("docs/clipproxy-rancher-deploy.md")

    assert "# Deploy Clipproxy on Rancher/Kubernetes" in guide
    assert "clipproxy-local" in guide
    assert "gitops/apps/clipproxy/overlays/local" in guide
    assert "clipproxy-secret" in guide
    assert "kubectl -n clipproxy create secret generic clipproxy-secret" in guide
    assert "kubectl -n argocd get application clipproxy-local" in guide
    assert "kubectl -n clipproxy get pods,svc,ingress,pvc" in guide
    assert "kubectl -n clipproxy rollout status deploy/clipproxy-api" in guide
    assert "kubectl -n clipproxy rollout status deploy/clipproxy-manager" in guide
    assert "kubectl -n clipproxy port-forward svc/clipproxy-manager 18317:18317" in guide
    assert "http://clipproxy.local" in guide
    assert "Docker Compose is kept only as a local reference" in guide
```

- [ ] **Step 2: Run the deploy guide test to verify it fails**

Run:

```bash
python3 -m pytest tests/test_clipproxy_gitops.py -q
```

Expected: fail because the deploy guide does not exist yet.

- [ ] **Step 3: Create the deploy guide**

Create `docs/clipproxy-rancher-deploy.md`:

```markdown
# Deploy Clipproxy on Rancher/Kubernetes

This guide deploys `clipproxy` through the repository GitOps flow. Docker Compose is kept only as a local reference; the Rancher/Kubernetes deployment is managed by ArgoCD.

## What will be deployed

ArgoCD application:

```text
clipproxy-local
```

GitOps path:

```text
gitops/apps/clipproxy/overlays/local
```

Kubernetes namespace:

```text
clipproxy
```

External URL:

```text
http://clipproxy.local
```

Workloads:

- `clipproxy-api` runs `eceasy/cli-proxy-api:latest` on port `8317`.
- `clipproxy-manager` runs `seakee/cpa-manager-plus:latest` on port `18317`.

Only `clipproxy-manager` is exposed through Ingress. `clipproxy-api` stays internal and is reached by the manager at `http://clipproxy-api:8317`.

## Step 1: Create the manager secret

The manager deployment expects a Kubernetes Secret named `clipproxy-secret`. Create it in the cluster before ArgoCD syncs the manager deployment.

```bash
kubectl -n clipproxy create secret generic clipproxy-secret \
  --from-literal=CPA_MANAGER_ADMIN_KEY='replace-this-admin-key' \
  --from-literal=CPA_MANAGEMENT_KEY='replace-this-management-key'
```

If the namespace does not exist yet, create it first or let ArgoCD create it during sync and then run the secret command:

```bash
kubectl create namespace clipproxy
```

Do not commit real key values to Git. The file `gitops/apps/clipproxy/overlays/local/secret.example.yaml` is an example only and is not included in the overlay resources.

## Step 2: Push the GitOps manifests

Commit and push the repository changes that add:

- `gitops/clusters/local/clipproxy.yaml`
- `gitops/apps/clipproxy/overlays/local`
- `gitops/apps/clipproxy/base`
- the `clipproxy` namespace entry

The local app-of-apps kustomization includes `clipproxy.yaml`, so ArgoCD should discover `clipproxy-local` from Git.

## Step 3: Check ArgoCD

```bash
kubectl -n argocd get application clipproxy-local
```

If the application does not appear, check that the root/local ArgoCD app has synced the `gitops/clusters/local` path.

## Step 4: Check Kubernetes resources

```bash
kubectl -n clipproxy get pods,svc,ingress,pvc
kubectl -n clipproxy rollout status deploy/clipproxy-api
kubectl -n clipproxy rollout status deploy/clipproxy-manager
```

If pods are Pending, check whether your Rancher/Kubernetes cluster has a default StorageClass for the PVCs.

If `clipproxy-manager` fails with a missing secret error, create `clipproxy-secret` and sync the app again.

## Step 5: Point `clipproxy.local` at the ingress controller

Find the ingress controller address with the method used by your lab cluster. For local testing, map that address to `clipproxy.local` in your workstation hosts file.

Example hosts entry:

```text
192.168.1.50 clipproxy.local
```

Use the actual ingress controller address from your cluster.

## Step 6: Open the manager UI

Open:

```text
http://clipproxy.local
```

If DNS or ingress routing is not ready, use port-forward for a direct smoke check:

```bash
kubectl -n clipproxy port-forward svc/clipproxy-manager 18317:18317
```

Then open:

```text
http://localhost:18317
```

## Recovery notes

- Missing `clipproxy-secret`: create the secret and sync `clipproxy-local` again.
- PVC not bound: configure a default StorageClass or set the desired `storageClassName` on the PVCs.
- Ingress not reachable: verify the ingress controller, the `clipproxy.local` hosts entry, and the `clipproxy` Ingress resource.
- Bad rollout: inspect the failing pod events and logs from the Rancher UI or with `kubectl -n clipproxy describe pod <pod-name>`.

## Rollback

Rollback is Git-first. Revert the Git commit that introduced or changed the `clipproxy` manifests, then let ArgoCD reconcile the previous desired state.
```

- [ ] **Step 4: Re-run the deploy guide test**

Run:

```bash
python3 -m pytest tests/test_clipproxy_gitops.py -q
```

Expected: pass for all focused `clipproxy` tests.

- [ ] **Step 5: Commit the deploy guide if commits are authorized**

Use this focused commit message only after the user explicitly authorizes commits:

```bash
git add docs/clipproxy-rancher-deploy.md tests/test_clipproxy_gitops.py
git commit -m "docs(clipproxy): add rancher deployment guide"
```

## Task 6: Final focused verification and diff review

**Files:**
- Verify: `tests/test_clipproxy_gitops.py`
- Verify: `clipproxy/`
- Verify: `gitops/apps/clipproxy/`
- Verify: `gitops/clusters/local/`
- Verify: `gitops/platform/00-namespaces/namespaces.yaml`
- Verify: `docs/clipproxy-rancher-deploy.md`
- Verify: `docs/superpowers/specs/2026-08-01-clipproxy-rancher-gitops-design.md`
- Verify: `docs/superpowers/plans/2026-08-01-clipproxy-rancher-gitops.md`

**Interfaces:**
- Consumes: all files produced by Tasks 1 through 5.
- Produces: verification evidence that the repo has the intended `clipproxy` GitOps deployment and no unrelated changes.

- [ ] **Step 1: Run the focused test file**

Run:

```bash
python3 -m pytest tests/test_clipproxy_gitops.py -q
```

Expected: all tests pass.

- [ ] **Step 2: Review the full diff stat**

Run:

```bash
git diff --stat
```

Expected: changed files are limited to `clipproxy/`, `gitops/apps/clipproxy/`, `gitops/clusters/local/`, `gitops/platform/00-namespaces/namespaces.yaml`, `docs/clipproxy-rancher-deploy.md`, `docs/superpowers/specs/2026-08-01-clipproxy-rancher-gitops-design.md`, `docs/superpowers/plans/2026-08-01-clipproxy-rancher-gitops.md`, and `tests/test_clipproxy_gitops.py`.

- [ ] **Step 3: Review the detailed diff without printing secret files**

Run:

```bash
git diff -- clipproxy/ gitops/apps/clipproxy/ gitops/clusters/local/ gitops/platform/00-namespaces/namespaces.yaml docs/clipproxy-rancher-deploy.md tests/test_clipproxy_gitops.py docs/superpowers/specs/2026-08-01-clipproxy-rancher-gitops-design.md docs/superpowers/plans/2026-08-01-clipproxy-rancher-gitops.md
```

Expected: diff shows the `clipproxy` rename, GitOps app wiring, namespace, Kustomize manifests, non-applied secret example, and deploy guide. It must not show real production secret values.

- [ ] **Step 4: Confirm the old directory name is gone**

Run:

```bash
test ! -e cliprouter && test -d clipproxy
```

Expected: exit code `0`.

- [ ] **Step 5: Commit the final verification state if commits are authorized**

If earlier tasks were not committed and the user now explicitly authorizes a single final commit, use:

```bash
git add clipproxy gitops/apps/clipproxy gitops/clusters/local/clipproxy.yaml gitops/clusters/local/kustomization.yaml gitops/platform/00-namespaces/namespaces.yaml docs/clipproxy-rancher-deploy.md docs/superpowers/specs/2026-08-01-clipproxy-rancher-gitops-design.md docs/superpowers/plans/2026-08-01-clipproxy-rancher-gitops.md tests/test_clipproxy_gitops.py
git add -u cliprouter
git commit -m "feat(clipproxy): add rancher gitops deployment"
```

## Plan Self-Review

- Spec coverage: Tasks 1 through 5 cover rename, GitOps app manifests, ArgoCD application, local kustomization inclusion, namespace, Ingress host, PVCs, secret handling, tests, and deployment docs.
- Scope control: The plan does not install Rancher, ingress controllers, TLS, monitoring, logging, or backup resources.
- Test strategy: Each implementation task starts with a failing string/path test and ends by running `python3 -m pytest tests/test_clipproxy_gitops.py -q`.
- Secret handling: Manager keys are loaded from `clipproxy-secret`; the example secret file uses non-production example values and is not listed in overlay resources.
- Security note: The `clipproxy` namespace is not given restricted pod-security labels because the third-party images use root-oriented paths; existing namespace security labels are preserved.
