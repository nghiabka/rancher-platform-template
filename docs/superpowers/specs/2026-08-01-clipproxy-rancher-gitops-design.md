---
name: clipproxy-rancher-gitops-design
description: Design for deploying clipproxy to a Rancher-managed Kubernetes cluster through ArgoCD GitOps
metadata:
  type: project
---

# Clipproxy Rancher GitOps Deployment Design

## Goal

Deploy `clipproxy` to the Rancher-managed Kubernetes lab cluster through the repository's existing GitOps and ArgoCD structure.

The current source under `cliprouter/` only contains Docker Compose configuration. This design renames the component to `clipproxy` and adds first-class Kubernetes manifests so the service is deployed by ArgoCD instead of being run manually with Docker Compose.

## Scope

### In scope

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

### Out of scope

- Running Docker Compose as the production deployment path.
- Installing or reconfiguring Rancher itself.
- Installing a new ingress controller.
- Choosing a real public DNS name.
- Committing production secret values.
- Adding TLS certificates in the first implementation.
- Adding monitoring, logging, or backup resources specifically for `clipproxy`.

## Proposed architecture

`clipproxy` becomes a normal GitOps application managed by ArgoCD, matching the pattern already used by `sample-api`.

The application has two workloads:

1. `clipproxy-api`, based on `eceasy/cli-proxy-api:latest`.
2. `clipproxy-manager`, based on `seakee/cpa-manager-plus:latest`.

Only the manager is exposed outside the cluster. The API stays internal and is called by the manager through a Kubernetes service.

The default external endpoint is:

```text
http://clipproxy.local
```

The expected local-cluster flow is:

1. The repository contains the `clipproxy` manifests.
2. The root/local ArgoCD configuration includes `clipproxy.yaml`.
3. ArgoCD creates and syncs the `clipproxy-local` application.
4. Kubernetes creates the `clipproxy` namespace, deployments, services, PVCs, and ingress.
5. The user maps `clipproxy.local` to the ingress controller address and opens the manager UI.

## Components

### 1. Source directory

`cliprouter/` is renamed to `clipproxy/` so the repository uses the product name consistently.

The existing Docker Compose file can remain as a local reference, but the Kubernetes deployment path is the GitOps manifests under `gitops/apps/clipproxy/`.

### 2. Namespace

The platform namespace manifest adds a `clipproxy` namespace.

The namespace should follow the security posture used by the existing application namespace where practical. If the third-party images cannot satisfy the strictest pod security settings, the implementation should document that limitation instead of silently weakening unrelated namespaces.

### 3. ConfigMap

The current `config.yaml` content is represented as a `ConfigMap` and mounted into the API container at:

```text
/CLIProxyAPI/config.yaml
```

This preserves the path expected by the existing Docker Compose configuration.

### 4. Secret handling

The deployment must not commit real admin or management keys.

The manifests should reference a Kubernetes `Secret` named `clipproxy-secret` for values such as:

- `CPA_MANAGER_ADMIN_KEY`
- `CPA_MANAGEMENT_KEY`
- remote-management secret material if moved out of the ConfigMap during implementation

The local overlay should include an example or documented command for creating the secret, but not a real production secret.

A later improvement can use Sealed Secrets to manage this secret through GitOps, consistent with the existing secrets-management phase in the repo.

### 5. `clipproxy-api` deployment

The API deployment runs:

```text
eceasy/cli-proxy-api:latest
```

It listens on container port `8317`, mounts the config file, and stores persistent state in a PVC mounted at the path used by the Compose deployment:

```text
/root/.cli-proxy-api
```

The service name is:

```text
clipproxy-api
```

The service is internal-only with `ClusterIP`.

### 6. `clipproxy-manager` deployment

The manager deployment runs:

```text
seakee/cpa-manager-plus:latest
```

It listens on container port `18317` and receives environment values equivalent to the Compose deployment, with sensitive values loaded from `clipproxy-secret`.

The upstream API URL is internal:

```text
http://clipproxy-api:8317
```

Manager data is stored in a PVC mounted at:

```text
/data
```

The service name is:

```text
clipproxy-manager
```

### 7. Ingress

The Ingress exposes only the manager service:

```text
clipproxy.local/ -> clipproxy-manager:http
```

The initial implementation uses the existing ingress class pattern from the repo, currently `nginx`.

The API service is not exposed directly in the first version. If direct API access is needed later, add a separate route only after confirming the application's supported base paths and auth behavior.

### 8. ArgoCD Application

`gitops/clusters/local/clipproxy.yaml` defines an ArgoCD `Application` named:

```text
clipproxy-local
```

It points at:

```text
gitops/apps/clipproxy/overlays/local
```

The destination namespace is:

```text
clipproxy
```

The sync policy should match the existing local app pattern:

- automated sync enabled
- prune enabled
- self-heal enabled
- `CreateNamespace=true`

## Data flow

1. A user opens `http://clipproxy.local`.
2. The ingress controller routes the request to `clipproxy-manager`.
3. `clipproxy-manager` stores usage data in its PVC at `/data`.
4. `clipproxy-manager` calls `clipproxy-api` through `http://clipproxy-api:8317`.
5. `clipproxy-api` reads `/CLIProxyAPI/config.yaml` from the mounted ConfigMap.
6. `clipproxy-api` stores state in its PVC at `/root/.cli-proxy-api`.
7. ArgoCD continuously reconciles the desired state from Git.

## Error handling and recovery

### Missing secret

If `clipproxy-secret` is missing, the manager pod should fail clearly rather than starting with unsafe default credentials. Recovery is to create the secret manually or add a SealedSecret in a later change.

### PVC not bound

If the Rancher/Kubernetes cluster does not have a default storage class, pods that need persistent data may remain Pending. Recovery is to configure a storage class or patch the PVCs with the intended `storageClassName`.

### API unavailable

If `clipproxy-api` is unavailable, the manager may start but upstream operations fail. Recovery is to check the `clipproxy-api` rollout and logs.

### Ingress unavailable

If `clipproxy.local` does not resolve or the ingress controller is not ready, the manager can still be tested with:

```bash
kubectl -n clipproxy port-forward svc/clipproxy-manager 18317:18317
```

Then open:

```text
http://localhost:18317
```

### Rollback

Rollback is Git-first: revert the manifest change and let ArgoCD reconcile the previous desired state.

## Verification strategy

Repository verification should stay lightweight because the change is mostly YAML and documentation.

Add a focused test file such as:

```text
tests/test_clipproxy_gitops.py
```

The tests should assert that:

- `gitops/clusters/local/clipproxy.yaml` exists and defines `clipproxy-local`.
- `gitops/clusters/local/kustomization.yaml` includes `clipproxy.yaml`.
- `gitops/platform/00-namespaces/namespaces.yaml` includes the `clipproxy` namespace.
- `gitops/apps/clipproxy/base/ingress.yaml` uses host `clipproxy.local`.
- `gitops/apps/clipproxy/base` includes API and manager deployments.
- sensitive manager keys are referenced from a secret rather than committed as plain production values.
- `cliprouter/` has been replaced by `clipproxy/`.

Expected local test command:

```bash
python -m pytest tests/test_clipproxy_gitops.py
```

Manual cluster verification after ArgoCD sync:

```bash
kubectl -n argocd get application clipproxy-local
kubectl -n clipproxy get pods,svc,ingress,pvc
kubectl -n clipproxy rollout status deploy/clipproxy-api
kubectl -n clipproxy rollout status deploy/clipproxy-manager
curl -I http://clipproxy.local
```

## Success criteria

The implementation is complete when all of the following are true:

- The repository uses `clipproxy` as the canonical component name.
- There is no remaining `cliprouter/` directory.
- A GitOps app exists under `gitops/apps/clipproxy/`.
- The local ArgoCD app-of-apps path includes `clipproxy-local`.
- The `clipproxy` namespace is declared.
- The manager UI is exposed through Ingress host `clipproxy.local`.
- The API service is reachable internally by the manager.
- Persistent data uses PVCs instead of Docker volumes.
- Real secrets are not committed.
- The deploy guide explains the Rancher/Kubernetes flow step by step.
- The focused GitOps tests pass.

## Notes for implementation

- Keep the manifests close to the existing `sample-api` style.
- Prefer simple Kustomize base plus local overlay layout.
- Do not run `kubectl`, Docker, Helm, or deployment commands unless the user explicitly asks.
- Do not print or inspect secret files.
- If the third-party images require root or writable filesystem behavior, document the exact limitation instead of weakening security globally.
