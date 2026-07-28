# Platform Readiness Checklist

## Host

- [ ] RAM con it nhat 8 GB available.
- [ ] Disk con it nhat 50 GB cho Docker/Kubernetes data.
- [ ] Docker dang chay.
- [ ] kubectl va helm co san.
- [ ] Port 80/443/6443 khong bi conflict.

## Rancher

- [ ] Rancher container running.
- [ ] Rancher UI truy cap duoc.
- [ ] Bootstrap password duoc luu vao password manager.
- [ ] Rancher data dung Docker volume rieng.

## Kubernetes

- [ ] Cluster Ready.
- [ ] Node Ready.
- [ ] StorageClass default ton tai.
- [ ] Metrics-server hoat dong hoac Prometheus da cai.
- [ ] Ingress controller hoat dong.

## GitOps

- [ ] ArgoCD UI truy cap duoc.
- [ ] Root application synced.
- [ ] App demo deployed tu Git.
- [ ] Rollback da test.

## Observability

- [ ] Grafana UI truy cap duoc.
- [ ] Prometheus scrape duoc cluster.
- [ ] Loki nhan log.
- [ ] Alertmanager co rule co ban.

## Security

- [ ] Namespace co Pod Security label.
- [ ] App chay non-root.
- [ ] NetworkPolicy co ban.
- [ ] Secret khong commit plain text.
- [ ] Image scan trong CI.

## Backup

- [ ] MinIO/backup storage ready.
- [ ] Velero backup schedule ton tai.
- [ ] Restore drill da test.
