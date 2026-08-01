# Rancher Platform Template

Template nay dung de xay mot local platform day du cho hoc DevOps/Kubernetes:

- Rancher Manager Web UI
- Kubernetes cluster local bang K3s
- GitOps/CD bang ArgoCD
- CI mau bang GitHub Actions/GitLab CI
- Traffic bang ingress-nginx va cert-manager
- Monitoring bang Prometheus, Grafana, Alertmanager
- Logging bang Loki va Promtail
- Secrets bang Sealed Secrets
- Backup bang Velero va MinIO
- Registry local hoac external registry
- Policy bang Kyverno

Day la template, khong phai script auto-cai-dat tat ca. Hay di tung phase de de debug va hieu tung thanh phan.

## Kien Truc Muc Tieu

```text
Ubuntu Host
|
|-- Docker Engine
|   |-- Rancher Manager Web UI
|   |-- MinIO backup storage
|   `-- Local registry optional
|
`-- K3s Kubernetes Cluster
    |-- ArgoCD
    |-- ingress-nginx
    |-- cert-manager
    |-- kube-prometheus-stack
    |-- Loki + Promtail
    |-- Sealed Secrets
    |-- Velero
    |-- Kyverno
    `-- Application workloads
```

## Thu Muc

```text
.
|-- apps/                 # Source app demo
|-- bin/                  # Script helper
|-- ci/                   # CI templates
|-- docs/                 # Architecture va learning path
|-- gitops/               # Kubernetes desired state
|-- infra/                # Rancher/K3s/local service setup
`-- operations/           # Runbooks va checklists
```

## Learning Path Khuyen Nghi

1. Doc `docs/learning-path.md`.
2. Doc `docs/deployment-roadmap.md`.
3. Doc `docs/architecture.md` de nam kien truc tong the.
4. Lam theo `docs/tutorial-phase-0-3.md` de chay lab theo tung phase.
5. Chay Rancher Manager bang Docker.
6. Dung cluster `local` san co hoac tao/import K3s cluster vao Rancher.
7. Cai ArgoCD va chuyen sang GitOps.
8. Cai traffic layer, monitoring/logging, secrets, backup va policy.
9. Lam CI build image va cap nhat GitOps repo.

## Repo Strategy

Production thuong nen tach 2 repo:

- `app-repo`: chua source code, Dockerfile, tests, CI.
- `gitops-repo`: chua Kubernetes manifests, Helm values, environment config.

Template nay gom ca hai de hoc nhanh. Khi len thuc te, hay tach ra.

## Domain Local Goi Y

Dung `/etc/hosts` cho lab local:

```text
127.0.0.1 rancher.local
127.0.0.1 argocd.local
127.0.0.1 grafana.local
127.0.0.1 prometheus.local
127.0.0.1 sample-api.local
```

Neu cluster khong expose qua localhost, thay `127.0.0.1` bang IP node/VM.

Voi lab dang expose qua Cloudflare/ingress-nginx, ArgoCD co the truy cap qua:

```text
https://argocd.justnghia.dev
```

Neu ingress-nginx van la NodePort khi chay local, truy cap truc tiep qua port NodePort HTTP, vi du:

```text
http://argocd.local:31910
http://grafana.local:31910
http://prometheus.local:31910
```

## Phase 1 Commands

Chi chay khi ban da doc va muon bat dau:

```bash
bin/check-host.sh
docker compose -f infra/rancher-docker/compose.yaml up -d
```

Sau khi Rancher len:

```bash
docker logs rancher 2>&1 | grep "Bootstrap Password:"
```

## Luu Y

- Rancher Docker install chi nen dung cho lab/dev, khong dung production.
- Neu may het disk, uu tien chuyen Docker data-root sang `/data/docker`.
- Khong cai tat ca tool cung luc. Moi phase can verify truoc khi sang phase tiep theo.
