#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Rendering cluster root"
kubectl kustomize "$ROOT_DIR/gitops/clusters/local" >/tmp/rancher-platform-cluster-local.yaml

echo "Rendering platform"
kubectl kustomize "$ROOT_DIR/gitops/platform" >/tmp/rancher-platform-components.yaml

echo "Rendering sample-api"
kubectl kustomize "$ROOT_DIR/gitops/apps/sample-api/overlays/local" >/tmp/rancher-platform-sample-api.yaml

echo "Rendered files:"
echo "  /tmp/rancher-platform-cluster-local.yaml"
echo "  /tmp/rancher-platform-components.yaml"
echo "  /tmp/rancher-platform-sample-api.yaml"
