# Implementation Plan

## Phase 1: Rancher UI

Output:

- Rancher UI tai `https://localhost`.
- Admin login duoc.

Steps:

1. Kiem tra host.
2. Start Rancher Docker.
3. Doi Rancher healthy.
4. Luu bootstrap password.

## Phase 2: K3s Cluster

Output:

- `kubectl get nodes` Ready.
- Cluster hien trong Rancher.

Steps:

1. Cai K3s voi Traefik disabled.
2. Cau hinh kubeconfig.
3. Import vao Rancher.

## Phase 3: ArgoCD GitOps

Output:

- ArgoCD UI ready.
- Root app synced.

Steps:

1. Cai ArgoCD.
2. Update `repoURL` trong `gitops/bootstrap/argocd/root-local.yaml`.
3. Apply root app.

## Phase 4: Platform Components

Output:

- ingress-nginx, cert-manager, monitoring, logging, secrets, backup, policy.

Steps:

1. Sync platform app.
2. Xu ly CRD dependency neu resource nao sync qua som.
3. Mo Grafana.
4. Kiem tra Loki.

## Phase 5: App Delivery

Output:

- sample-api deploy qua ArgoCD.
- CI build image va update tag.

Steps:

1. Build/push image local hoac external registry.
2. Sync sample app.
3. Cai GitHub/GitLab CI.
4. Test rollout va rollback.

## Phase 6: Backup And Restore

Output:

- Velero backup thanh cong.
- Restore drill thanh cong.

Steps:

1. Start MinIO.
2. Tao bucket `velero`.
3. Tao secret credential cho Velero.
4. Chay backup manual.
5. Restore sang namespace test.
