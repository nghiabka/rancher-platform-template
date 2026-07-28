# Rancher Docker

Dung cho lab/dev local.

## Start

```bash
cp infra/rancher-docker/.env.example infra/rancher-docker/.env
docker compose --env-file infra/rancher-docker/.env -f infra/rancher-docker/compose.yaml up -d
```

Mo:

```text
https://localhost
```

## Bootstrap Password

Neu khong set `CATTLE_BOOTSTRAP_PASSWORD`, lay password bang:

```bash
docker logs rancher 2>&1 | grep "Bootstrap Password:"
```

## Stop

```bash
docker compose --env-file infra/rancher-docker/.env -f infra/rancher-docker/compose.yaml down
```

Khong xoa volume neu con muon giu data.
