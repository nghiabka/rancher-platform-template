# Platform Architecture

## 1. Management Layer

Thanh phan:

- Rancher Manager chay bang Docker container.
- Rancher quan ly Kubernetes cluster qua agent.
- Nguoi hoc thao tac tren Rancher UI de quan sat cluster, workload, namespace, RBAC.

Vai tro:

- Cluster management UI.
- User/RBAC management.
- Import/provision cluster.
- View workload, logs, events.

## 2. Kubernetes Runtime Layer

Thanh phan:

- K3s local cluster.
- Traefik mac dinh co the tat neu dung ingress-nginx.
- Local path provisioner cho PVC lab.

Vai tro:

- Chay platform components.
- Chay application workloads.
- Cung cap Kubernetes API de ArgoCD va CI/CD tuong tac.

## 3. Delivery Layer

Thanh phan:

- CI: GitHub Actions hoac GitLab CI.
- Registry: GHCR/Docker Hub/local registry/Harbor.
- CD: ArgoCD.

Flow:

```text
Developer push code
-> CI test/build/scan image
-> Push image
-> Update GitOps manifest
-> ArgoCD sync
-> Kubernetes rollout
```

## 4. Traffic Layer

Thanh phan:

- ingress-nginx.
- cert-manager.
- DNS local hoac public domain.

Vai tro:

- Expose app/platform UI.
- Quan ly TLS.
- Route traffic theo host/path.

## 5. Observability Layer

Thanh phan:

- kube-prometheus-stack.
- Grafana.
- Alertmanager.
- Loki.
- Promtail.

Vai tro:

- Metrics, dashboard, alerts.
- Centralized logging.
- Theo doi rollout va app health.

## 6. Security Layer

Thanh phan:

- RBAC.
- Pod Security Admission.
- NetworkPolicy.
- Sealed Secrets.
- Kyverno.
- Trivy trong CI.

Vai tro:

- Giam quyen pod.
- Khong commit plain secret.
- Chan image/config nguy hiem.
- Scan image truoc khi deploy.

## 7. Backup Layer

Thanh phan:

- MinIO local lam S3-compatible storage.
- Velero backup Kubernetes resources va PVC.
- Docker volume backup cho Rancher.

Vai tro:

- Backup cluster state.
- Restore drill.
- Giam rui ro mat cau hinh lab.

## MVP Va Phase Sau

MVP:

- Rancher Manager
- K3s
- ArgoCD
- ingress-nginx
- Prometheus/Grafana
- Loki
- Sealed Secrets

Phase sau:

- Harbor
- Vault
- Crossplane
- Backstage
- Longhorn
- Falco
