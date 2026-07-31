#!/usr/bin/env bash
set -euo pipefail

IMAGE="${IMAGE:-nghiadvbka/sample-api:local}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

docker build -t "$IMAGE" "$ROOT_DIR/apps/sample-api"
docker push "$IMAGE"
