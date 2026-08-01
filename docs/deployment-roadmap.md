# Deployment Roadmap

Roadmap nay danh cho nguoi moi hoc nhung muon xay platform theo huong chuyen nghiep. Di tung phase, verify xong moi sang phase tiep theo.

## Phase 0: Chuan Bi Host

Muc tieu:

- Biet may hien tai co du tai nguyen.
- Biet Docker, kubectl, helm dang dung context nao.
- Khong de Docker lam day phan vung `/`.

Checklist:

- [ ] Chay `bin/check-host.sh`.
- [ ] Kiem tra RAM con it nhat 8 GB.
- [ ] Kiem tra disk con it nhat 50 GB cho Docker/Kubernetes.
- [ ] Kiem tra port 80, 443, 6443, 8080, 9000, 9001, 5000.
- [ ] Quyet dinh co can chuyen Docker data-root sang `/data/docker` hay khong.

Ket qua mong doi:

- Host san sang de chay Rancher, Kubernetes va cac platform services.

## Phase 1: Rancher Manager Web UI

Muc tieu:

- Co giao dien web Rancher de quan ly cluster.

Checklist:

- [ ] Copy `infra/rancher-docker/.env.example` thanh `.env`.
- [ ] Doi `RANCHER_BOOTSTRAP_PASSWORD`.
- [ ] Chay Rancher bang Docker Compose.
- [ ] Mo `https://localhost`.
- [ ] Login thanh cong.
- [ ] Luu admin password vao noi an toan.

Ket qua mong doi:

- Rancher UI hoat dong.
- Rancher container co volume rieng `rancher-data`.

## Phase 2: Ket Noi Kubernetes Cluster

Muc tieu:

- Rancher nhin thay cluster Kubernetes.
- `kubectl get nodes` chay duoc tu terminal.

Checklist:

- [ ] Xac dinh cluster hien co la Rancher Desktop, K3s, minikube hay cluster khac.
- [ ] Sua kubeconfig neu context dang loi certificate hoac sai endpoint.
- [ ] Verify `kubectl get nodes`.
- [ ] Import cluster vao Rancher UI.
- [ ] Kiem tra cluster status trong Rancher la Active.

Ket qua mong doi:

- Cluster san sang de cai ArgoCD va platform components.

## Phase 3: GitOps Bootstrap Voi ArgoCD

Muc tieu:

- Git la source of truth cho platform.
- ArgoCD tu dong sync desired state vao cluster.

Checklist:

- [ ] Cai ArgoCD vao namespace `argocd`.
- [ ] Mo ArgoCD UI bang port-forward hoac ingress.
- [ ] Doi `repoURL` trong cac file GitOps ve repo that.
- [ ] Chay `make render` de validate Kustomize.
- [ ] Apply `gitops/bootstrap/argocd/root-local.yaml`.
- [ ] Verify root app, platform app va sample app trong ArgoCD.

Ket qua mong doi:

- ArgoCD quan ly platform va app theo mo hinh app-of-apps.

## Phase 4: Traffic Layer

Muc tieu:

- App va platform UI truy cap duoc qua domain local.

Checklist:

- [ ] Cai `ingress-nginx`.
- [ ] Them domain local vao `/etc/hosts`.
- [ ] Verify ingress controller pod Ready.
- [ ] Deploy ingress cho `sample-api.local`.
- [ ] Cai `cert-manager`.
- [ ] Dung `selfsigned-local` cho lab hoac Let's Encrypt staging neu co domain that.

Ket qua mong doi:

- Truy cap duoc app qua HTTP/HTTPS.
- Hieu duoc flow request: browser -> ingress -> service -> pod.

## Phase 5: Observability

Muc tieu:

- Theo doi duoc cluster va app.

Checklist:

- [ ] Cai `kube-prometheus-stack`.
- [ ] Mo Grafana.
- [ ] Kiem tra Prometheus targets.
- [ ] Kiem tra node, pod, deployment dashboards.
- [ ] Kiem tra `ServiceMonitor` cua sample API.
- [ ] Tao alert co ban: pod restart, deployment unavailable, node pressure.

Ket qua mong doi:

- Nhin duoc suc khoe cluster/app bang Grafana.
- Co alert co ban qua Alertmanager.

## Phase 6: Logging

Muc tieu:

- Tap trung log tu cac pod ve mot noi.

Checklist:

- [ ] Cai Loki.
- [ ] Cai Promtail.
- [ ] Them Loki datasource vao Grafana.
- [ ] Query log theo namespace/app.
- [ ] Kiem tra log cua `sample-api`.

Ket qua mong doi:

- Xem log app va platform tu Grafana.

## Phase 7: CI/CD End-To-End

Muc tieu:

- Push code -> test -> build image -> scan -> push registry -> update GitOps -> ArgoCD deploy.

Checklist:

- [x] Chon registry: Docker Hub cho CI/release, local registry cho lab.
- [x] Cap nhat image name trong CI va GitOps manifests.
- [x] Chay test sample API.
- [x] Build image.
- [x] Scan image bang Trivy.
- [x] Push image.
- [x] Update image tag trong Kustomize overlay.
- [x] Verify ArgoCD sync va rollout.
- [x] Test rollback bang Git revert.

Ket qua mong doi:

- Co pipeline release hoan chinh cho app mau.

## Phase 8: Secrets Management

Muc tieu:

- Khong commit secret plain text vao Git.

Checklist:

- [ ] Cai Sealed Secrets.
- [ ] Cai `kubeseal` tren may local.
- [ ] Tao Kubernetes Secret tam thoi.
- [ ] Seal secret thanh `SealedSecret`.
- [ ] Commit `SealedSecret` vao GitOps repo.
- [ ] Verify app doc duoc secret sau khi ArgoCD sync.

Ket qua mong doi:

- Secrets duoc quan ly theo GitOps ma khong lo plain text leak.

## Phase 9: Backup And Restore

Muc tieu:

- Co kha nang backup/restore namespace va resource quan trong.

Checklist:

- [ ] Start MinIO local.
- [ ] Tao bucket `velero`.
- [ ] Tao credentials secret cho Velero.
- [ ] Cai Velero.
- [ ] Tao backup schedule.
- [ ] Chay backup manual cho namespace `sample-api`.
- [ ] Restore sang namespace test.
- [ ] Ghi lai restore drill result.

Ket qua mong doi:

- Backup khong chi ton tai tren ly thuyet, ma restore duoc.

## Phase 10: Policy And Hardening

Muc tieu:

- Bat dau ap dung governance ma khong lam nguoi moi bi chan qua som.

Checklist:

- [ ] Cai Kyverno.
- [ ] De policy o `Audit` truoc.
- [ ] Kiem tra report vi pham policy.
- [ ] Sua app de chay non-root, drop capabilities, co resource limits.
- [ ] Sau khi on dinh, chuyen mot so policy sang `Enforce`.
- [ ] Them NetworkPolicy cho app.
- [ ] Bat Pod Security labels cho namespace.

Ket qua mong doi:

- Platform co security baseline ro rang.

## Phase 11: Nang Cap Sau MVP

Chi lam sau khi cac phase tren chay on:

- [ ] Harbor thay cho registry don gian.
- [ ] Longhorn cho storage UI va volume management.
- [ ] Vault hoac External Secrets.
- [ ] Backstage cho developer portal.
- [ ] Crossplane cho infra self-service.
- [ ] Falco cho runtime security.
- [ ] Multi-environment: local, dev, staging, prod.

## Thu Tu Uu Tien Neu Bi Qua Tai

Neu thay qua nhieu tool, hay di theo thu tu ngan gon nay:

1. Rancher UI
2. Kubernetes access bang `kubectl`
3. Deploy app thu cong
4. ArgoCD
5. Ingress
6. Prometheus/Grafana
7. Loki
8. CI pipeline
9. Sealed Secrets
10. Velero
11. Kyverno
