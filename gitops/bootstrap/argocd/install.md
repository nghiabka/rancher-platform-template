# Install ArgoCD

Sau khi cluster Ready:

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

Lay password:

```bash
kubectl -n argocd get secret argocd-initial-admin-secret \
  -o jsonpath="{.data.password}" | base64 -d
```

Port-forward tam thoi:

```bash
kubectl -n argocd port-forward svc/argocd-server 8080:443
```

Mo:

```text
https://localhost:8080
```

Sau do apply root app:

```bash
kubectl apply -n argocd -f gitops/bootstrap/argocd/root-local.yaml
```
