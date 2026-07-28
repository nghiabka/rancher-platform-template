# Common Commands

## Docker

```bash
docker ps
docker logs rancher
docker volume ls
docker system df
```

## Kubernetes

```bash
kubectl config get-contexts
kubectl get nodes -o wide
kubectl get ns
kubectl get pods -A
kubectl get events -A --sort-by=.lastTimestamp
```

## ArgoCD

```bash
kubectl -n argocd get applications
kubectl -n argocd get pods
kubectl -n argocd get svc
```

## Ingress

```bash
kubectl -n ingress-nginx get pods,svc
kubectl get ingress -A
```

## Monitoring

```bash
kubectl -n observability get pods
kubectl -n observability get servicemonitor
```

## Velero

```bash
velero backup get
velero restore get
velero schedule get
```
