#!/usr/bin/env bash
set -euo pipefail

echo "== Host =="
uname -a

echo
echo "== Memory =="
free -h

echo
echo "== Disk =="
df -h /
df -h /data 2>/dev/null || true

echo
echo "== Tools =="
for tool in docker kubectl helm; do
  if command -v "$tool" >/dev/null 2>&1; then
    echo "OK: $tool -> $(command -v "$tool")"
  else
    echo "MISSING: $tool"
  fi
done

echo
echo "== Docker =="
docker version --format 'Client {{.Client.Version}} / Server {{.Server.Version}}'
docker system df

echo
echo "== Kubernetes Contexts =="
kubectl config get-contexts || true
