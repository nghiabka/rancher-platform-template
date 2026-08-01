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
