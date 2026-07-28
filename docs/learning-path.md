# Learning Path

## Phase 0: Host Readiness

Muc tieu:

- Biet may co du CPU/RAM/disk.
- Biet Docker/kubectl/helm dang tro vao dau.

Can hoc:

- Docker container, volume, port.
- kubeconfig va context.
- Linux port va disk.

## Phase 1: Rancher UI

Muc tieu:

- Mo duoc Rancher web UI.
- Login duoc bang bootstrap password.

Can hoc:

- Rancher Manager la gi.
- Rancher khac Rancher Desktop the nao.
- Import/provision cluster la gi.

## Phase 2: Kubernetes Core

Muc tieu:

- Tao duoc namespace.
- Deploy duoc nginx/sample app.
- Expose app bang Service va Ingress.

Can hoc:

- Pod, Deployment, ReplicaSet.
- Service ClusterIP/NodePort/LoadBalancer.
- Ingress.
- ConfigMap, Secret.
- PVC.

## Phase 3: GitOps

Muc tieu:

- Cai ArgoCD.
- Deploy app tu Git.
- Rollback bang Git revert.

Can hoc:

- Desired state.
- App-of-apps.
- Kustomize overlay.
- Helm values.

## Phase 4: Observability

Muc tieu:

- Mo Grafana.
- Xem node/pod metrics.
- Xem log app trong Loki.

Can hoc:

- Metrics vs logs.
- ServiceMonitor.
- Alertmanager.

## Phase 5: CI/CD

Muc tieu:

- Push code -> build image -> update GitOps -> ArgoCD deploy.

Can hoc:

- Dockerfile.
- Image tag theo Git SHA.
- Registry auth.
- Trivy scan.

## Phase 6: Security And Backup

Muc tieu:

- Ma hoa secret bang Sealed Secrets.
- Backup/restore namespace bang Velero.
- Ap policy co ban bang Kyverno.

Can hoc:

- Secret lifecycle.
- Restore drill.
- Policy-as-code.
