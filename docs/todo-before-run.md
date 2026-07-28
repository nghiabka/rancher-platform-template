# TODO Before Run

Cap nhat cac gia tri sau truoc khi dung nghiem tuc:

## Git Repository

Files:

- `gitops/bootstrap/argocd/root-local.yaml`
- `gitops/clusters/local/platform.yaml`
- `gitops/clusters/local/sample-api.yaml`

Thay:

```text
https://github.com/your-org/rancher-platform-template.git
```

Bang repo Git that cua ban.

## Passwords

Files:

- `infra/rancher-docker/.env`
- `infra/local-services/.env`
- `gitops/platform/30-observability/kube-prometheus-stack.yaml`

Thay cac password lab:

- `admin12345`
- `change-me-strong-password`
- `change-me-minio-password`

## Registry

Files:

- `gitops/apps/sample-api/base/deployment.yaml`
- `gitops/apps/sample-api/overlays/local/kustomization.yaml`
- `ci/github/sample-api-ci.yaml`

Chon 1 trong cac huong:

- GHCR: `ghcr.io/<org>/sample-api`
- Docker Hub: `<user>/sample-api`
- Local registry: `localhost:5000/sample-api`
- Harbor phase sau: `harbor.local/library/sample-api`

## Cert Manager Email

File:

- `gitops/platform/20-cert-manager/cluster-issuers.yaml`

Thay:

```text
platform@example.com
```

Bang email cua ban neu dung Let's Encrypt.

## Velero MinIO Endpoint

File:

- `gitops/platform/60-backup/velero.yaml`

Gia tri:

```text
http://host.docker.internal:9000
```

Co the can thay bang IP host neu K3s khong resolve duoc `host.docker.internal`.
