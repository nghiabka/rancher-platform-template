# Local Services

Dung cho lab:

- MinIO: S3-compatible storage cho Velero.
- Docker registry local: noi push image neu khong muon dung Docker Hub/GHCR.

## Start

```bash
cp infra/local-services/.env.example infra/local-services/.env
docker compose --env-file infra/local-services/.env -f infra/local-services/compose.yaml up -d
```

## URLs

```text
MinIO API:     http://localhost:9000
MinIO Console: http://localhost:9001
Registry:      localhost:5000
```
