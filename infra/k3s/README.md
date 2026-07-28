# K3s Local Cluster

Co 2 cach dung voi Rancher:

1. Tao K3s cluster local roi import vao Rancher.
2. Dung Rancher UI de provision cluster tren node co SSH.

Voi may ca nhan, cach 1 de hoc va de debug hon.

## Cai K3s Server

Chay khi ban da san sang cai cluster:

```bash
curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="--disable traefik" sh -
```

Ly do disable Traefik:

- Template nay dung ingress-nginx rieng de hoc pattern pho bien.

## Kubeconfig

```bash
sudo cat /etc/rancher/k3s/k3s.yaml > ~/.kube/k3s.yaml
export KUBECONFIG=~/.kube/k3s.yaml
kubectl get nodes
```

## Import Vao Rancher

Trong Rancher UI:

```text
Cluster Management -> Import Existing -> Generic
```

Copy command Rancher dua ra va chay tren may host.

## Uninstall

Chi chay neu muon xoa cluster:

```bash
sudo /usr/local/bin/k3s-uninstall.sh
```
