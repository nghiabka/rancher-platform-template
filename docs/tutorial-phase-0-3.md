# Tutorial Chạy Phase 0 Đến Phase 10

Tutorial này hướng dẫn chạy từng bước từ host tới Rancher, một cluster Kubernetes dùng được trong Rancher, ArgoCD GitOps bootstrap, rồi mở rộng dần sang traffic, observability, logging, CI/CD, secrets, backup và policy.

Phạm vi:

- Phase 0: Chuẩn bị host.
- Phase 1: Chạy Rancher Manager Web UI bằng Docker.
- Phase 2: Dùng cluster `local` có sẵn trong Rancher hoặc import K3s nếu muốn học luồng import.
- Phase 3: Cài ArgoCD và bootstrap GitOps root app.
- Phase 4: Cấu hình traffic layer bằng ingress-nginx và cert-manager.
- Phase 5: Cài observability bằng Prometheus/Grafana/Alertmanager.
- Phase 6: Cài logging bằng Loki/Promtail.
- Phase 7: Thiết lập CI/CD end-to-end cho sample API.
- Phase 8: Quản lý secret bằng Sealed Secrets.
- Phase 9: Backup và restore bằng Velero/MinIO.
- Phase 10: Policy và hardening bằng Kyverno.

Nguyên tắc chạy lab:

- Không chạy tất cả phase cùng lúc.
- Mỗi phase phải verify xong mới sang phase tiếp theo.
- Không commit file chứa secret như `.env`, kubeconfig hoặc password thật.
- Các lệnh `docker`, `kubectl`, `helm` trong file này là lệnh để bạn tự chạy khi đã sẵn sàng.

## Mục Lục

- [Trước Khi Bắt Đầu](#trước-khi-bắt-đầu)
- [Phase 0: Chuẩn Bị Host](#phase-0-chuẩn-bị-host)
- [Phase 1: Chạy Rancher Manager Web UI](#phase-1-chạy-rancher-manager-web-ui)
- [Phase 2: Dùng Cluster `local` Sẵn Có Hoặc Import K3s Vào Rancher](#phase-2-dùng-cluster-local-sẵn-có-hoặc-import-k3s-vào-rancher)
- [Phase 3: Cài ArgoCD Và Bootstrap GitOps](#phase-3-cài-argocd-và-bootstrap-gitops)
- [Phase 4: Traffic Layer](#phase-4-traffic-layer)
- [Phase 5: Observability](#phase-5-observability)
- [Phase 6: Logging](#phase-6-logging)
- [Phase 7: CI/CD End-To-End](#phase-7-cicd-end-to-end)
- [Phase 8: Secrets Management](#phase-8-secrets-management)
- [Phase 9: Backup And Restore](#phase-9-backup-and-restore)
- [Phase 10: Policy And Hardening](#phase-10-policy-and-hardening)
- [Troubleshooting Nhanh](#troubleshooting-nhanh)
- [Dừng Và Dọn Dẹp Lab](#dừng-và-dọn-dẹp-lab)
- [Bước Tiếp Theo](#bước-tiếp-theo)

## Sơ Đồ Luồng

```text
Phase 0
Host ready
  |
  v
Phase 1
Rancher UI chạy bằng Docker
  |
  v
Phase 2
Dùng cluster local Active hoặc import K3s vào Rancher
  |
  v
Phase 3
ArgoCD được cài và quản lý GitOps root app
  |
  v
Phase 4
Traffic qua ingress-nginx và cert-manager
  |
  v
Phase 5
Observability bằng Prometheus/Grafana
  |
  v
Phase 6
Logging bằng Loki/Promtail
  |
  v
Phase 7
CI/CD build image và update GitOps
  |
  v
Phase 8
Secrets bằng Sealed Secrets
  |
  v
Phase 9
Backup/restore bằng Velero và MinIO
  |
  v
Phase 10
Policy/hardening bằng Kyverno
```

## Trước Khi Bắt Đầu

Đứng tại repo root:

```bash
pwd
```

Kết quả nên là thư mục repo này, ví dụ:

```text
/data/learning/rancher-platform-template
```

Đọc nhanh các file nền:

- `README.md`: tổng quan repo.
- `docs/deployment-roadmap.md`: roadmap đầy đủ Phase 0 đến Phase 10.
- `docs/todo-before-run.md`: các giá trị cần sửa trước khi chạy nghiêm túc.
- `infra/rancher-docker/README.md`: cách chạy Rancher bằng Docker.
- `infra/k3s/README.md`: cách cài K3s local.
- `gitops/bootstrap/argocd/install.md`: cách cài ArgoCD.

## Phase 0: Chuẩn Bị Host

### Mục Tiêu

Sau phase này bạn cần biết:

- Docker, kubectl, helm đã có hay chưa.
- Máy còn đủ RAM và disk hay không.
- Docker daemon chạy được hay không.
- kubectl đang trỏ tới context nào.

### Bước 0.1: Chạy host check

```bash
bin/check-host.sh
```

Script này sẽ kiểm tra:

- Kernel và thông tin host.
- RAM.
- Disk của `/` và `/data` nếu có.
- Tool `docker`, `kubectl`, `helm`.
- Docker version và dung lượng Docker đang dùng.
- Kubernetes contexts hiện có.

Nếu script dừng ở phần Docker, thường là do Docker chưa cài hoặc Docker daemon chưa chạy. Sửa lỗi đó trước khi tiếp tục.

### Bước 0.2: Kiểm tra RAM

```bash
free -h
```

Khuyến nghị cho lab này:

- Tối thiểu: 8 GB RAM trống tương đối.
- Tốt hơn: 16 GB RAM nếu muốn chạy thêm monitoring/logging ở phase sau.

Nếu RAM quá thấp, Rancher, K3s, ArgoCD và các component sau có thể chạy chậm hoặc pod bị evict.

### Bước 0.3: Kiểm tra disk

```bash
df -h /
df -h /data 2>/dev/null || true
docker system df
```

Khuyến nghị:

- Còn ít nhất 50 GB cho Docker/Kubernetes.
- Không để Docker làm đầy phân vùng `/`.

Nếu Docker đang dùng quá nhiều dung lượng, dừng lại và xử lý trước khi chạy Rancher/K3s.

### Bước 0.4: Kiểm tra port quan trọng

Các port thường dùng trong lab:

| Port | Dùng cho |
| --- | --- |
| 80 | HTTP/Rancher/Ingress |
| 443 | HTTPS/Rancher/Ingress |
| 6443 | Kubernetes API server |
| 8080 | ArgoCD port-forward tạm thời |
| 9000 | MinIO API ở phase backup sau |
| 9001 | MinIO console ở phase backup sau |
| 5000 | Local registry nếu dùng |

Kiểm tra port đang listen:

```bash
ss -lntp
```

Nếu port 80 hoặc 443 đã bị chiếm, bạn có thể đổi port Rancher trong `infra/rancher-docker/.env` ở Phase 1.

### Checkpoint Phase 0

Chỉ sang Phase 1 khi:

- `docker version` chạy được.
- `kubectl` có thể chạy lệnh cơ bản như `kubectl config get-contexts`.
- Máy còn đủ RAM/disk.
- Bạn biết port 80/443 có đang rảnh hay cần đổi.

## Phase 1: Chạy Rancher Manager Web UI

### Mục Tiêu

Sau phase này bạn cần có:

- Rancher container đang chạy.
- Rancher UI mở được trên browser.
- Login được bằng bootstrap password.
- Rancher data được lưu trong Docker volume `rancher-data`.

### Bước 1.1: Tạo file cấu hình môi trường

Copy file mẫu:

```bash
cp infra/rancher-docker/.env.example infra/rancher-docker/.env
```

Mở file vừa tạo:

```bash
nano infra/rancher-docker/.env
```

Nội dung mẫu:

```env
RANCHER_VERSION=stable
RANCHER_HTTP_PORT=80
RANCHER_HTTPS_PORT=443
RANCHER_BOOTSTRAP_PASSWORD=change-me-strong-password
```

Đổi `RANCHER_BOOTSTRAP_PASSWORD` thành password lab của bạn.

Nếu port 80 hoặc 443 đã bị chiếm, đổi ví dụ:

```env
RANCHER_HTTP_PORT=8088
RANCHER_HTTPS_PORT=8443
```

Không commit file `.env` nếu trong đó có password thật.

### Bước 1.2: Start Rancher

Chạy từ repo root:

```bash
docker compose --env-file infra/rancher-docker/.env \
  -f infra/rancher-docker/compose.yaml \
  up -d
```

Kiểm tra container:

```bash
docker ps --filter name=rancher
```

Xem log khi Rancher đang khởi động:

```bash
docker logs -f rancher
```

Rancher có thể mất vài phút để sẵn sàng.

### Bước 1.3: Mở Rancher UI

Nếu dùng port mặc định:

```text
https://localhost
```

Nếu bạn đổi `RANCHER_HTTPS_PORT=8443`:

```text
https://localhost:8443
```

Browser có thể cảnh báo certificate self-signed. Với lab local, bạn có thể tiếp tục vào trang.

### Bước 1.4: Login bằng bootstrap password

Nếu bạn đã set `RANCHER_BOOTSTRAP_PASSWORD` trong `.env`, dùng password đó để login.

Nếu không set hoặc cần tìm lại bootstrap password:

```bash
docker logs rancher 2>&1 | grep "Bootstrap Password:"
```

Sau khi login, Rancher có thể yêu cầu đổi admin password. Lưu password mới vào nơi an toàn, không lưu trong repo.

### Bước 1.5: Verify Rancher

Kiểm tra container vẫn chạy:

```bash
docker ps --filter name=rancher
```

Kiểm tra volume:

```bash
docker volume ls | grep rancher
```

Kết quả mong đợi:

- Container `rancher` ở trạng thái Up.
- UI mở được.
- Login thành công.
- Có volume `rancher-data`.

### Checkpoint Phase 1

Chỉ sang Phase 2 khi:

- Rancher UI truy cập được.
- Bạn login được vào Rancher.
- Bạn đã lưu admin password ở nơi an toàn.

## Phase 2: Dùng Cluster `local` Sẵn Có Hoặc Import K3s Vào Rancher

### Mục Tiêu

Sau phase này bạn cần có **ít nhất một cluster Kubernetes dùng được** để sang Phase 3:

- Rancher UI có cluster trạng thái `Active`.
- Terminal có kubeconfig trỏ đúng cluster đó.
- `kubectl get nodes -o wide` trả về node `Ready`.

Trong Rancher thường đã có cluster tên `local`. Với lab học GitOps, nếu cluster `local` đã `Active`, bạn có thể dùng luôn cluster này và **không cần tạo thêm cluster `local-k3s`**.

Chỉ import thêm K3s thành cluster `local-k3s` khi bạn muốn học riêng luồng quản lý downstream/imported cluster.

### Bước 2.1: Quyết định dùng cluster nào

Mở Rancher UI và vào danh sách cluster:

```text
Cluster Management -> Clusters
```

Nếu bạn thấy cluster:

```text
local    Active
```

thì chọn **Luồng A** bên dưới.

Nếu bạn muốn tạo hoặc import thêm một cluster K3s riêng, chọn **Luồng B**.

Khuyến nghị cho lab hiện tại: dùng **Luồng A** vì Rancher đã có cluster `local` đang `Active`. Việc tạo thêm `local-k3s` không bắt buộc cho Phase 3.

## Luồng A: Dùng Cluster `local` Đã Có Trong Rancher

### Bước 2A.1: Hiểu cluster `local` là gì

Cluster `local` là cluster mà Rancher đang quản lý sẵn. Trong lab local, Rancher có thể hiển thị cluster này ngay sau khi Rancher chạy xong.

Bạn có thể dùng cluster `local` để học các bước tiếp theo:

- cài ArgoCD,
- bootstrap GitOps,
- deploy sample app,
- cài platform components ở các phase sau.

Lưu ý: với môi trường production, thường tách management cluster và workload cluster. Nhưng với lab học local, dùng `local` là cách đơn giản để đi tiếp.

### Bước 2A.2: Lấy kubeconfig cho cluster `local`

Trong Rancher UI, mở cluster `local`, rồi tìm chức năng tải/copy kubeconfig:

```text
local -> Download KubeConfig
```

Lưu kubeconfig vào máy local, ví dụ:

```text
~/.kube/rancher-local.yaml
```

Không commit file kubeconfig vào Git vì file này chứa credential truy cập cluster.

### Bước 2A.3: Dùng kubeconfig của cluster `local`

Trong terminal, trỏ `kubectl` tới kubeconfig vừa lưu:

```bash
export KUBECONFIG=~/.kube/rancher-local.yaml
```

Kiểm tra context:

```bash
kubectl config current-context
kubectl get nodes -o wide
kubectl get namespaces
```

Kết quả mong đợi:

- `kubectl get nodes -o wide` hiển thị ít nhất một node `Ready`.
- Rancher UI hiển thị cluster `local` là `Active`.
- Terminal và Rancher đang nói về cùng cluster bạn muốn dùng cho Phase 3.

Nếu muốn dùng kubeconfig này lâu dài cho lab, thêm vào shell profile:

```bash
echo 'export KUBECONFIG=$HOME/.kube/rancher-local.yaml' >> ~/.bashrc
source ~/.bashrc
```

### Bước 2A.4: Checkpoint cho Luồng A

Bạn có thể sang Phase 3 khi các lệnh sau chạy được:

```bash
kubectl get nodes -o wide
kubectl get ns
```

Và trong Rancher UI:

```text
local    Active
```

Nếu đã đạt checkpoint này, bỏ qua Luồng B.

## Luồng B: Tùy Chọn Import K3s Thành Cluster Riêng

Luồng này chỉ cần làm nếu bạn muốn học cách import downstream cluster vào Rancher.

Nếu Rancher đã có `local Active` và mục tiêu của bạn chỉ là cài ArgoCD/GitOps, bạn không cần làm Luồng B.

### Bước 2B.1: Cài K3s với Traefik disabled

Template này dùng ingress-nginx ở phase sau, nên khi cài K3s sẽ disable Traefik mặc định:

```bash
curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="--disable traefik" sh -
```

Sau khi cài, kiểm tra service:

```bash
sudo systemctl status k3s --no-pager
```

Nếu service chưa chạy, xem log:

```bash
sudo journalctl -u k3s -n 100 --no-pager
```

### Bước 2B.2: Cấu hình kubeconfig cho K3s import

Tạo thư mục kubeconfig nếu chưa có:

```bash
mkdir -p ~/.kube
```

Copy kubeconfig của K3s:

```bash
sudo cat /etc/rancher/k3s/k3s.yaml > ~/.kube/k3s.yaml
chmod 600 ~/.kube/k3s.yaml
```

Dùng kubeconfig này trong terminal hiện tại:

```bash
export KUBECONFIG=~/.kube/k3s.yaml
```

Kiểm tra context:

```bash
kubectl config get-contexts
kubectl get nodes -o wide
```

Kết quả mong đợi:

```text
NAME      STATUS   ROLES           AGE   VERSION        INTERNAL-IP
...       Ready    control-plane   ...   v...+k3s...    ...
```

### Bước 2B.3: Kiểm tra Rancher Server URL trước khi import

Import agent trong K3s phải gọi ngược được về Rancher server. Vì vậy Rancher Server URL không nên là `https://localhost` nếu command đó chạy bên trong pod.

Trong Rancher UI, kiểm tra Server URL:

```text
Global Settings / Settings -> server-url
```

Giá trị nên là URL mà pod trong K3s truy cập được, ví dụ:

```text
https://rancher.justnghia.dev
```

Hoặc một hostname/IP nội bộ mà cluster resolve và kết nối được.

Nếu dùng domain public có certificate public như Cloudflare hoặc Let's Encrypt, kiểm tra thêm TLS mode:

```text
Global Settings / Settings -> agent-tls-mode
```

Với public certificate, nên dùng:

```text
system-store
```

Điều này giúp `cattle-cluster-agent` dùng CA trust store hệ thống để verify certificate public.

### Bước 2B.4: Import cluster vào Rancher

Trước khi import, đảm bảo terminal đang trỏ đúng K3s cluster cần import:

```bash
kubectl config current-context
kubectl get nodes
```

Trong Rancher UI:

```text
Cluster Management -> Import Existing -> Generic
```

Làm theo wizard:

1. Đặt tên cluster, ví dụ `local-k3s`.
2. Rancher sẽ sinh ra command import.
3. Copy command đó.
4. Chạy command trên máy host đang dùng kubeconfig K3s.

Sau khi chạy command import, verify pod agent của Rancher:

```bash
kubectl -n cattle-system get pods -o wide
kubectl -n cattle-system logs deploy/cattle-cluster-agent --tail=100
```

Quay lại Rancher UI và chờ cluster chuyển sang:

```text
local-k3s    Active
```

### Bước 2B.5: Debug khi `local-k3s` kẹt `Provisioning`

Nếu Rancher UI hiển thị `local-k3s` là `Provisioning`, kiểm tra agent trong K3s:

```bash
kubectl -n cattle-system get pods -o wide
```

Nếu thấy `cattle-cluster-agent` là `CrashLoopBackOff`, lấy log lần crash trước:

```bash
kubectl -n cattle-system logs deploy/cattle-cluster-agent --previous --tail=200
```

Nếu lệnh theo deployment không có log, lấy log trực tiếp từ pod:

```bash
kubectl -n cattle-system get pods
kubectl -n cattle-system logs <ten-pod-cattle-cluster-agent> --previous --tail=200
```

Lỗi thường gặp:

```text
tls: failed to verify certificate: x509: certificate signed by unknown authority
```

Ví dụ log có thể cho thấy:

```text
CATTLE_SERVER=https://rancher.justnghia.dev
INFO: https://rancher.justnghia.dev/ping is accessible
ERROR: tls: failed to verify certificate: x509: certificate signed by unknown authority
```

Cách đọc lỗi này:

- DNS tới Rancher đã resolve được.
- Network tới `/ping` đã thông.
- Lỗi nằm ở certificate trust giữa agent và Rancher URL.

Cách xử lý khuyến nghị:

1. Trong Rancher UI, đổi setting:

   ```text
   Global Settings / Settings -> agent-tls-mode -> system-store
   ```

2. Xóa cluster import hỏng `local-k3s` trong Rancher UI.

3. Đảm bảo terminal đang trỏ đúng cluster K3s import hỏng, không phải cluster khác:

   ```bash
   kubectl config current-context
   kubectl get nodes
   ```

4. Nếu namespace `cattle-system` vẫn còn trong cluster import hỏng, xóa agent cũ:

   ```bash
   kubectl delete namespace cattle-system
   ```

5. Đợi namespace biến mất:

   ```bash
   kubectl get ns | grep cattle
   ```

6. Tạo lại import trong Rancher UI và chạy command mới.

Không xóa `cattle-system` nếu bạn không chắc kubeconfig đang trỏ vào cluster nào.

### Bước 2B.6: Checkpoint cho Luồng B

Chỉ xem Luồng B hoàn thành khi:

- `kubectl get nodes` hiển thị node `Ready`.
- `kubectl -n cattle-system get pods` hiển thị `cattle-cluster-agent` Running `1/1`.
- Rancher UI hiển thị cluster import, ví dụ `local-k3s`, trạng thái `Active`.

### Checkpoint Phase 2

Phase 2 đạt yêu cầu nếu **một trong hai điều kiện** đúng:

- Bạn dùng cluster `local` có sẵn và Rancher UI hiển thị `local Active`.
- Bạn import cluster riêng và Rancher UI hiển thị cluster đó `Active`.

Trước khi sang Phase 3, quyết định rõ cluster nào sẽ chạy ArgoCD, rồi export đúng kubeconfig:

```bash
# Nếu dùng cluster local từ Rancher
export KUBECONFIG=~/.kube/rancher-local.yaml

# Nếu dùng K3s import riêng
export KUBECONFIG=~/.kube/k3s.yaml
```

Verify lần cuối:

```bash
kubectl config current-context
kubectl get nodes -o wide
```

## Phase 3: Cài ArgoCD Và Bootstrap GitOps

### Mục Tiêu

Sau phase này bạn cần có:

- ArgoCD chạy trong namespace `argocd`.
- Mở được ArgoCD UI.
- Login được ArgoCD bằng user `admin`.
- GitOps root app được apply vào cluster.
- ArgoCD thấy các app con trong `gitops/clusters/local`.

Lưu ý quan trọng: root app hiện tại trỏ tới `gitops/clusters/local`, trong đó có `platform.yaml` và `sample-api.yaml`. Khi sync, ArgoCD có thể bắt đầu quản lý cả platform components và sample app. Nếu một số component thuộc phase sau chưa Healthy ngay, hãy ghi nhận lỗi và xử lý ở phase tương ứng.

### Bước 3.1: Cài ArgoCD

Tạo namespace:

```bash
kubectl create namespace argocd --dry-run=client -o yaml | kubectl apply -f -
```

Cài manifest chính thức của ArgoCD:

```bash
kubectl apply -n argocd \
  -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

Chờ pod Ready:

```bash
kubectl -n argocd get pods -w
```

Khi các pod chính như `argocd-server`, `argocd-repo-server`, `argocd-application-controller` đã Running/Ready, nhấn `Ctrl+C` để thoát watch.

### Bước 3.2: Lấy password admin ban đầu

```bash
kubectl -n argocd get secret argocd-initial-admin-secret \
  -o jsonpath="{.data.password}" | base64 -d
```

User mặc định:

```text
admin
```

Lưu password ở nơi an toàn. Không commit password vào repo.

### Bước 3.3: Mở ArgoCD UI

Trong lab local, bạn có hai cách:

- **Cách cũ**: port-forward tạm thời.
- **Cách mới khuyến nghị**: mở qua Ingress domain `argocd.justnghia.dev`.

Nếu muốn port-forward tạm thời, chạy:

```bash
kubectl -n argocd port-forward svc/argocd-server 8080:443
```

Rồi mở:

```text
https://localhost:8080
```

Nếu muốn dùng domain thật qua Cloudflare hoặc ingress-nginx, mở:

```text
http://argocd.justnghia.dev
```

hoặc nếu bạn tự cấu hình HTTPS ở lớp ngoài:

```text
https://argocd.justnghia.dev
```

Lưu ý: với cấu hình lab hiện tại, ArgoCD server đang chạy `server.insecure=true` sau ingress-nginx.

Nếu port 8080 đã bị chiếm, dùng port khác:

```bash
kubectl -n argocd port-forward svc/argocd-server 8081:443
```

Khi đó mở:

```text
https://localhost:8081
```

### Bước 3.4: Sửa repoURL về repo thật của bạn

Các file cần kiểm tra:

- `gitops/bootstrap/argocd/root-local.yaml`
- `gitops/clusters/local/platform.yaml`
- `gitops/clusters/local/sample-api.yaml`

Tìm `repoURL` hiện tại:

```bash
rg -n "repoURL:" gitops/bootstrap/argocd gitops/clusters/local
```

Đổi URL mẫu trong các file trên thành Git repository thật của bạn.

Ví dụ nếu repo của bạn là:

```text
https://github.com/my-org/rancher-platform-template.git
```

thì `repoURL` nên là:

```yaml
repoURL: https://github.com/my-org/rancher-platform-template.git
```

Nếu repo private, bạn cần cấu hình repository credential trong ArgoCD trước khi sync.

### Bước 3.5: Validate Kustomize render trước khi apply

Chạy render local:

```bash
make render
```

Lệnh này gọi `bin/render-gitops.sh` và render ra:

```text
/tmp/rancher-platform-cluster-local.yaml
/tmp/rancher-platform-components.yaml
/tmp/rancher-platform-sample-api.yaml
```

Nếu render lỗi, sửa manifest trước khi apply root app.

### Bước 3.6: Apply root app

```bash
kubectl apply -n argocd -f gitops/bootstrap/argocd/root-local.yaml
```

Kiểm tra ArgoCD Applications:

```bash
kubectl -n argocd get applications
```

Kết quả mong đợi có các app như:

```text
root-local
platform-local
sample-api-local
```

### Bước 3.7: Verify trong ArgoCD UI

Trong ArgoCD UI, kiểm tra:

- `root-local` tồn tại.
- `platform-local` được tạo từ root app.
- `sample-api-local` được tạo từ root app.
- Repo URL đúng.
- Không còn lỗi authentication với Git repository.

Nếu app chưa Healthy ngay, xem chi tiết trong UI hoặc dùng kubectl:

```bash
kubectl -n argocd describe application root-local
kubectl -n argocd describe application platform-local
kubectl -n argocd describe application sample-api-local
```

### Checkpoint Phase 3

Phase 3 được xem là hoàn thành khi:

- Namespace `argocd` tồn tại.
- Các pod ArgoCD chính Running/Ready.
- Mở được ArgoCD UI.
- Login được bằng user `admin`.
- `kubectl -n argocd get applications` thấy root app và app con.
- Các lỗi repo URL hoặc authentication đã được xử lý.

## Phase 4: Traffic Layer

### Mục Tiêu

Sau phase này bạn cần có:

- `ingress-nginx` chạy trong cluster.
- `cert-manager` chạy trong cluster.
- Có `ClusterIssuer` local để dùng certificate tự ký trong lab.
- Có thể truy cập app/platform UI qua domain local khi ingress đã sẵn sàng.

Lưu ý: repo hiện tại gom nhiều component platform trong `gitops/platform`. Một số resource phụ thuộc CRD của phase sau, nên nếu ArgoCD báo `CRD not found`, hãy cài controller tạo CRD trước rồi sync lại resource phụ thuộc.

### Bước 4.1: Kiểm tra trạng thái app platform

```bash
kubectl -n argocd get applications
kubectl -n argocd describe application platform-local
```

Nếu thấy lỗi kiểu:

```text
The Kubernetes API could not find cert-manager.io/ClusterIssuer
```

thì nguyên nhân là `ClusterIssuer` được sync trước khi cert-manager CRD tồn tại. Đây là lỗi thứ tự triển khai, không phải lỗi Rancher/K3s.

### Bước 4.2: Cài ingress-nginx qua ArgoCD

Nếu app `ingress-nginx` chưa tồn tại trong ArgoCD, apply Application manifest:

```bash
kubectl apply -n argocd -f gitops/platform/10-ingress/ingress-nginx.yaml
```

Kiểm tra app:

```bash
kubectl -n argocd get application ingress-nginx
kubectl -n ingress-nginx get pods,svc
```

Kết quả mong đợi:

- Namespace `ingress-nginx` được tạo.
- Pod ingress controller Running.
- Service ingress controller tồn tại.

Nếu app `ingress-nginx` báo thiếu `ServiceMonitor` CRD, cài `kube-prometheus-stack` ở Phase 5 trước, rồi quay lại sync `ingress-nginx`.

### Bước 4.3: Cài cert-manager qua ArgoCD

Nếu app `cert-manager` chưa tồn tại trong ArgoCD, apply Application manifest:

```bash
kubectl apply -n argocd -f gitops/platform/20-cert-manager/cert-manager.yaml
```

Kiểm tra app và pod:

```bash
kubectl -n argocd get application cert-manager
kubectl -n cert-manager get pods
```

Kiểm tra CRD đã có:

```bash
kubectl get crd clusterissuers.cert-manager.io
kubectl get crd certificates.cert-manager.io
```

Nếu app `cert-manager` báo thiếu `ServiceMonitor` CRD, cài `kube-prometheus-stack` ở Phase 5 trước, rồi quay lại sync `cert-manager`.

### Bước 4.4: Sync ClusterIssuer

Khi `clusterissuers.cert-manager.io` đã tồn tại, sync lại `platform-local` hoặc apply riêng manifest issuer:

```bash
kubectl apply -f gitops/platform/20-cert-manager/cluster-issuers.yaml
```

Kiểm tra:

```bash
kubectl get clusterissuer
```

Kết quả mong đợi có:

```text
selfsigned-local
letsencrypt-staging
```

Với lab local, `selfsigned-local` là đủ. Nếu dùng Let's Encrypt thật, sửa email trong `gitops/platform/20-cert-manager/cluster-issuers.yaml` theo `docs/todo-before-run.md` trước.

### Bước 4.5: Cấu hình domain local

Thêm vào `/etc/hosts` trên máy bạn:

```text
127.0.0.1 rancher.local
127.0.0.1 argocd.local
127.0.0.1 grafana.local
127.0.0.1 sample-api.local
```

Nếu cluster không expose qua localhost, thay `127.0.0.1` bằng IP node/VM.

Kiểm tra ingress sample-api:

```bash
kubectl get ingress -A
```

Nếu ingress controller dùng NodePort, xem port được cấp:

```bash
kubectl -n ingress-nginx get svc
```

### Checkpoint Phase 4

Phase 4 đạt yêu cầu khi:

- `kubectl -n ingress-nginx get pods` có controller Running.
- `kubectl -n cert-manager get pods` có các pod cert-manager Running.
- `kubectl get clusterissuer` thấy `selfsigned-local`.
- Bạn hiểu flow request: browser -> ingress -> service -> pod.

## Phase 5: Observability

### Mục Tiêu

Sau phase này bạn cần có:

- Prometheus, Grafana và Alertmanager chạy trong namespace `observability`.
- CRD `ServiceMonitor` tồn tại.
- Có thể mở Grafana.
- Có thể quan sát pod/deployment cơ bản.

### Bước 5.1: Cài kube-prometheus-stack

Nếu app `kube-prometheus-stack` chưa tồn tại trong ArgoCD, apply Application manifest:

```bash
kubectl apply -n argocd -f gitops/platform/30-observability/kube-prometheus-stack.yaml
```

Kiểm tra app:

```bash
kubectl -n argocd get application kube-prometheus-stack
```

Kiểm tra pod:

```bash
kubectl -n observability get pods
```

Helm chart này có thể mất vài phút vì tạo nhiều CRD, Deployment, StatefulSet và webhook.

### Bước 5.2: Verify CRD monitoring

```bash
kubectl get crd servicemonitors.monitoring.coreos.com
kubectl get crd prometheuses.monitoring.coreos.com
kubectl get crd alertmanagers.monitoring.coreos.com
```

Khi `ServiceMonitor` CRD đã có, các lỗi sync liên quan đến `monitoring.coreos.com/ServiceMonitor` có thể được xử lý bằng cách sync lại app liên quan.

### Bước 5.3: Mở Grafana

Tìm service Grafana:

```bash
kubectl -n observability get svc | grep grafana
```

Port-forward tạm thời:

```bash
kubectl -n observability port-forward svc/kube-prometheus-stack-grafana 3000:80
```

Mở browser:

```text
http://localhost:3000
```

Password lab hiện nằm trong `gitops/platform/30-observability/kube-prometheus-stack.yaml`. Khi dùng nghiêm túc, đổi password theo `docs/todo-before-run.md` và không commit secret thật.

### Bước 5.4: Sync lại sample-api nếu thiếu ServiceMonitor

Nếu `sample-api-local` từng fail vì thiếu `ServiceMonitor`, refresh app:

```bash
kubectl -n argocd annotate application sample-api-local \
  argocd.argoproj.io/refresh=hard --overwrite
```

Nếu cần sync thủ công qua UI:

```text
ArgoCD UI -> sample-api-local -> Sync
```

Kiểm tra ServiceMonitor:

```bash
kubectl -n sample-api get servicemonitor
```

### Checkpoint Phase 5

Phase 5 đạt yêu cầu khi:

- `kubectl -n observability get pods` không còn pod lỗi chính.
- Grafana mở được.
- `kubectl get crd servicemonitors.monitoring.coreos.com` trả về CRD.
- `sample-api` có thể được monitor qua `ServiceMonitor` sau khi app sync.

## Phase 6: Logging

### Mục Tiêu

Sau phase này bạn cần có:

- Loki chạy trong namespace `logging`.
- Promtail chạy và thu log từ pod.
- Có thể query log trong Grafana hoặc kiểm tra log pipeline bằng kubectl.

### Bước 6.1: Cài Loki

Nếu app `loki` chưa tồn tại trong ArgoCD, apply Application manifest:

```bash
kubectl apply -n argocd -f gitops/platform/40-logging/loki.yaml
```

Kiểm tra:

```bash
kubectl -n argocd get application loki
kubectl -n logging get pods
```

Loki trong repo dùng mode `SingleBinary` để phù hợp lab local.

### Bước 6.2: Cài Promtail

Nếu app `promtail` chưa tồn tại trong ArgoCD, apply Application manifest:

```bash
kubectl apply -n argocd -f gitops/platform/40-logging/promtail.yaml
```

Kiểm tra:

```bash
kubectl -n argocd get application promtail
kubectl -n logging get pods
```

Promtail hiện gửi log tới:

```text
http://loki-gateway.logging.svc.cluster.local/loki/api/v1/push
```

### Bước 6.3: Kiểm tra log sample-api

Trước hết kiểm tra pod sample-api:

```bash
kubectl -n sample-api get pods
kubectl -n sample-api logs deploy/sample-api --tail=50
```

Nếu Grafana chưa có Loki datasource tự động, thêm datasource thủ công trong Grafana UI:

```text
Connections -> Data sources -> Add data source -> Loki
URL: http://loki-gateway.logging.svc.cluster.local
```

Sau đó query trong Explore, ví dụ:

```text
{namespace="sample-api"}
```

### Checkpoint Phase 6

Phase 6 đạt yêu cầu khi:

- `kubectl -n logging get pods` có Loki/Promtail Running.
- Grafana query được log từ namespace `sample-api` hoặc namespace platform.
- Bạn hiểu flow log: pod stdout/stderr -> Promtail -> Loki -> Grafana.

## Phase 7: CI/CD End-To-End

### Mục Tiêu

Sau phase này bạn cần có flow:

```text
push code -> test -> build image -> scan -> push registry -> update GitOps -> ArgoCD deploy
```

Repo có template CI ở:

- `ci/github/sample-api-ci.yaml`
- `ci/gitlab/sample-api-ci.yml`

Phần GitOps image local nằm ở:

- `gitops/apps/sample-api/base/deployment.yaml`
- `gitops/apps/sample-api/overlays/local/kustomization.yaml`

### Bước 7.1: Chọn registry

Repo hiện đang dùng Docker Hub image mẫu:

```text
nghiadvbka/sample-api
```

Bạn có thể chọn một trong các hướng:

| Hướng | Image ví dụ | Khi nào dùng |
| --- | --- | --- |
| Docker Hub | `nghiadvbka/sample-api` | Dễ dùng cho lab public/private cơ bản |
| GHCR | `ghcr.io/<org>/sample-api` | Phù hợp GitHub organization |
| Local registry | `localhost:5000/sample-api` | Lab offline/local |
| Harbor | `harbor.local/library/sample-api` | Phase nâng cấp sau MVP |

Nếu đổi registry, cập nhật các file trong `docs/todo-before-run.md` đã liệt kê.

### Bước 7.2: Build và push image thủ công để kiểm tra

Với Docker Hub mặc định:

```bash
docker login
IMAGE=nghiadvbka/sample-api:local bin/build-local-sample-api.sh
```

Script sẽ chạy:

```text
docker build
docker push
```

Nếu dùng local registry, start local services trước:

```bash
cp infra/local-services/.env.example infra/local-services/.env
docker compose --env-file infra/local-services/.env \
  -f infra/local-services/compose.yaml \
  up -d
```

Rồi build/push:

```bash
IMAGE=localhost:5000/sample-api:local bin/build-local-sample-api.sh
```

### Bước 7.3: Update image trong GitOps overlay

Overlay hiện có:

```yaml
images:
  - name: localhost:5000/sample-api
    newName: nghiadvbka/sample-api
    newTag: local
```

Nếu image tag mới là commit SHA hoặc version cụ thể, cập nhật `newTag` trong:

```text
gitops/apps/sample-api/overlays/local/kustomization.yaml
```

Có thể dùng kustomize:

```bash
cd gitops/apps/sample-api/overlays/local
kustomize edit set image "localhost:5000/sample-api=nghiadvbka/sample-api:<tag-moi>"
```

Sau đó commit và push thay đổi GitOps để ArgoCD đọc được.

### Bước 7.4: Cấu hình GitHub Actions

Workflow mẫu dùng Docker Hub:

```text
ci/github/sample-api-ci.yaml
```

Các điểm cần đổi khi dùng repo thật:

- `IMAGE_NAME`
- Docker Hub username trong bước login
- secret `DOCKERHUB_TOKEN`
- quyền write để auto-commit GitOps change

Với GitHub repo, copy workflow vào:

```text
.github/workflows/sample-api-ci.yaml
```

Sau khi push code lên `main`, workflow sẽ:

1. chạy test sample API,
2. build image,
3. scan bằng Trivy,
4. push image,
5. cập nhật GitOps overlay,
6. commit lại tag mới.

### Bước 7.5: Verify rollout và rollback

Kiểm tra ArgoCD app:

```bash
kubectl -n argocd get application sample-api-local
```

Kiểm tra Deployment image:

```bash
kubectl -n sample-api get deploy sample-api -o wide
kubectl -n sample-api rollout status deploy/sample-api
```

Rollback theo GitOps nên làm bằng Git revert commit đổi image tag, rồi để ArgoCD sync lại.

### Checkpoint Phase 7

Phase 7 đạt yêu cầu khi:

- Image sample-api được build và push vào registry bạn chọn.
- GitOps overlay trỏ tới image tag mới.
- ArgoCD sync sample-api thành công.
- Rollback bằng Git revert được hiểu và thử trong lab.

## Phase 8: Secrets Management

### Mục Tiêu

Sau phase này bạn cần có:

- Sealed Secrets controller chạy trong cluster.
- Biết tạo Kubernetes Secret tạm thời.
- Biết seal secret thành `SealedSecret` để commit vào Git.
- Không commit plain text secret.
- `sample-api` nhận được env var từ Secret mà không expose secret value.

### Bước 8.1: Cài Sealed Secrets controller

Platform parent đã include `gitops/platform/50-secrets`, nên khi ArgoCD sync platform thì app `sealed-secrets` sẽ được quản lý qua GitOps. Nếu cần cài thủ công trong lab, apply Application manifest:

```bash
kubectl apply -n argocd -f gitops/platform/50-secrets/sealed-secrets.yaml
```

Kiểm tra:

```bash
kubectl -n argocd get application sealed-secrets
kubectl -n sealed-secrets get pods
```

Kết quả mong đợi có controller Running trong namespace `sealed-secrets`.

### Bước 8.2: Cài kubeseal trên máy local

Kiểm tra:

```bash
kubeseal --version
```

Nếu chưa có, cài `kubeseal` theo hướng dẫn chính thức của Bitnami Sealed Secrets cho OS của bạn.

### Bước 8.3: Tạo temp Secret outside the repo

Tạo Secret tạm ngoài repo để tránh commit plain text secret. Ví dụ dùng Secret name mà Deployment đang tham chiếu:

```bash
kubectl -n sample-api create secret generic sample-api-demo-secret \
  --from-literal=DEMO_VALUE='<secret-value>' \
  --dry-run=client -o yaml > /tmp/sample-api-demo-secret.yaml
```

Không copy file `/tmp/sample-api-demo-secret.yaml` vào Git.

### Bước 8.4: seal it to a manifest for the overlay/example path

Seal Secret tạm thành `SealedSecret` bằng controller trong cluster hiện tại:

```bash
kubeseal \
  --controller-name sealed-secrets-controller \
  --controller-namespace sealed-secrets \
  --format yaml \
  < /tmp/sample-api-demo-secret.yaml \
  > gitops/apps/sample-api/overlays/local/sealed-secret.example.yaml
```

Kiểm tra file `sealed-secret.example.yaml` không còn plain text value trước khi commit. File example trong repo chỉ chứa placeholder; khi chạy lab thật, generate lại bằng public cert của cluster của bạn.

### Bước 8.5: Commit SealedSecret vào GitOps

Khi đã kiểm tra file sealed secret an toàn, add file đã generate vào overlay local:

```text
gitops/apps/sample-api/overlays/local/sealed-secret.example.yaml
```

Sau đó thêm file đã generate vào `resources` của:

```text
gitops/apps/sample-api/overlays/local/kustomization.yaml
```

Commit và để ArgoCD sync. Controller sẽ tạo Kubernetes Secret thật `sample-api-demo-secret` trong namespace `sample-api`.

### Bước 8.6: verify the pod receives the env var without exposing secret value

Deployment `sample-api` đọc Secret qua env var `DEMO_SECRET_VALUE`. Không in giá trị secret ra API hoặc log. Kiểm tra trạng thái pod và manifest wiring:

```bash
kubectl -n sample-api get secret sample-api-demo-secret
kubectl -n sample-api describe deploy sample-api
kubectl -n sample-api rollout status deploy/sample-api
```

### Checkpoint Phase 8

Phase 8 đạt yêu cầu khi:

- Sealed Secrets controller Running.
- Bạn tạo được `SealedSecret` từ một Secret tạm.
- Git chỉ chứa `SealedSecret`, không chứa plain text secret.
- Sau ArgoCD sync, Kubernetes Secret thật xuất hiện trong namespace đích.
- `sample-api` nhận env var từ Secret mà không expose secret value.

## Phase 9: Backup And Restore

### Mục Tiêu

Sau phase này bạn cần có:

- MinIO local làm S3-compatible backup storage.
- Velero chạy trong cluster.
- Có backup namespace `sample-api`.
- Thử restore sang namespace test.

### Bước 9.1: Start MinIO local

Copy env mẫu:

```bash
cp infra/local-services/.env.example infra/local-services/.env
```

Mở `infra/local-services/.env` và đổi password lab trước khi dùng lâu dài.

Start local services:

```bash
docker compose --env-file infra/local-services/.env \
  -f infra/local-services/compose.yaml \
  up -d
```

URLs:

```text
MinIO API:     http://localhost:9000
MinIO Console: http://localhost:9001
Registry:      localhost:5000
```

Tạo bucket trong MinIO Console:

```text
velero
```

### Bước 9.2: Tạo credential secret cho Velero

Tạo file credential tạm ngoài repo:

```bash
cat > /tmp/velero-credentials <<'EOF'
[default]
aws_access_key_id=<minio-user>
aws_secret_access_key=<minio-password>
EOF
```

Tạo secret trong cluster:

```bash
kubectl create namespace velero --dry-run=client -o yaml | kubectl apply -f -
kubectl -n velero create secret generic velero-cloud-credentials \
  --from-file=cloud=/tmp/velero-credentials \
  --dry-run=client -o yaml | kubectl apply -f -
```

Xóa file tạm sau khi tạo secret:

```bash
rm /tmp/velero-credentials
```

### Bước 9.3: Cài Velero qua ArgoCD

Nếu app `velero` chưa tồn tại trong ArgoCD, apply Application manifest:

```bash
kubectl apply -n argocd -f gitops/platform/60-backup/velero.yaml
```

Kiểm tra:

```bash
kubectl -n argocd get application velero
kubectl -n velero get pods
kubectl get crd schedules.velero.io
```

Nếu K3s không resolve được `host.docker.internal`, sửa endpoint trong `gitops/platform/60-backup/velero.yaml` theo IP host như hướng dẫn trong `docs/todo-before-run.md`.

### Bước 9.4: Sync backup schedule

Khi CRD `schedules.velero.io` đã tồn tại, apply hoặc sync schedule:

```bash
kubectl apply -f gitops/platform/60-backup/schedules.yaml
```

Kiểm tra:

```bash
velero schedule get
```

### Bước 9.5: Backup và restore drill

Tạo backup manual cho namespace `sample-api`:

```bash
velero backup create sample-api-manual --include-namespaces sample-api
velero backup get
```

Restore sang namespace test:

```bash
velero restore create sample-api-restore-test \
  --from-backup sample-api-manual \
  --namespace-mappings sample-api:sample-api-restore-test
```

Kiểm tra:

```bash
velero restore get
kubectl -n sample-api-restore-test get all
```

### Checkpoint Phase 9

Phase 9 đạt yêu cầu khi:

- MinIO chạy và có bucket `velero`.
- Velero pod Running.
- `velero backup get` thấy backup Completed.
- Restore drill tạo được resource trong namespace test.

## Phase 10: Policy And Hardening

### Mục Tiêu

Sau phase này bạn cần có:

- Kyverno chạy trong cluster.
- Policy baseline ở chế độ `Audit` trước.
- App sample-api có security context, resource limits và NetworkPolicy.
- Biết cách chuyển dần policy sang `Enforce` khi đã ổn định.

### Bước 10.1: Cài Kyverno qua ArgoCD

Nếu app `kyverno` chưa tồn tại trong ArgoCD, apply Application manifest:

```bash
kubectl apply -n argocd -f gitops/platform/80-policy/kyverno.yaml
```

Kiểm tra:

```bash
kubectl -n argocd get application kyverno
kubectl -n kyverno get pods
kubectl get crd clusterpolicies.kyverno.io
```

### Bước 10.2: Apply policy non-root ở chế độ Audit

Khi CRD `clusterpolicies.kyverno.io` đã tồn tại:

```bash
kubectl apply -f gitops/platform/80-policy/require-non-root-policy.yaml
```

Kiểm tra policy:

```bash
kubectl get clusterpolicy
kubectl describe clusterpolicy require-run-as-non-root
```

Policy trong repo đang dùng:

```text
validationFailureAction: Audit
```

Nghĩa là policy ghi nhận vi phạm nhưng chưa chặn workload.

### Bước 10.3: Kiểm tra hardening của sample-api

Deployment sample-api đã có các cấu hình baseline:

- `runAsNonRoot: true`
- `seccompProfile: RuntimeDefault`
- `allowPrivilegeEscalation: false`
- `capabilities.drop: ALL`
- resource requests/limits

Kiểm tra trong cluster:

```bash
kubectl -n sample-api get deploy sample-api -o yaml | grep -E "runAsNonRoot|seccompProfile|allowPrivilegeEscalation|drop:|requests:|limits:" -A3
```

Kiểm tra NetworkPolicy:

```bash
kubectl -n sample-api get networkpolicy
kubectl -n sample-api describe networkpolicy sample-api-ingress-only
```

### Bước 10.4: Xem policy reports

Tùy version Kyverno, report có thể là `policyreport` hoặc `clusterpolicyreport`:

```bash
kubectl get policyreport -A
kubectl get clusterpolicyreport
```

Nếu chưa có report ngay, chờ controller reconcile rồi kiểm tra lại.

### Bước 10.5: Chuyển dần sang Enforce

Chỉ chuyển policy từ `Audit` sang `Enforce` khi:

- workload quan trọng không còn vi phạm,
- team hiểu lỗi policy và cách sửa,
- đã test trên lab/dev.

Khi sẵn sàng, sửa:

```text
gitops/platform/80-policy/require-non-root-policy.yaml
```

Từ:

```yaml
validationFailureAction: Audit
```

sang:

```yaml
validationFailureAction: Enforce
```

Commit và để ArgoCD sync.

### Checkpoint Phase 10

Phase 10 đạt yêu cầu khi:

- Kyverno pod Running.
- `require-run-as-non-root` tồn tại ở chế độ `Audit`.
- sample-api có security context/resource limits/NetworkPolicy.
- Bạn biết khi nào nên chuyển policy sang `Enforce`.

## Troubleshooting Nhanh

### Rancher không mở được UI

Kiểm tra container:

```bash
docker ps --filter name=rancher
```

Xem log:

```bash
docker logs rancher --tail 100
```

Kiểm tra port:

```bash
ss -lntp | grep -E ':80|:443'
```

Nếu port bị chiếm, sửa `RANCHER_HTTP_PORT` và `RANCHER_HTTPS_PORT` trong `infra/rancher-docker/.env`, rồi chạy lại:

```bash
docker compose --env-file infra/rancher-docker/.env \
  -f infra/rancher-docker/compose.yaml \
  up -d
```

### K3s cài xong nhưng kubectl lỗi

Kiểm tra service:

```bash
sudo systemctl status k3s --no-pager
```

Kiểm tra kubeconfig đang dùng:

```bash
echo "$KUBECONFIG"
kubectl config get-contexts
```

Nếu biến `KUBECONFIG` trống, chạy lại:

```bash
export KUBECONFIG=~/.kube/k3s.yaml
kubectl get nodes
```

### Rancher không thấy cluster Active

Kiểm tra agent namespace/pod:

```bash
kubectl get ns | grep cattle
kubectl get pods -A | grep cattle
```

Nếu pod ImagePullBackOff hoặc CrashLoopBackOff, mở Rancher UI xem lại command import và chạy lại đúng command cho cluster hiện tại.

### ArgoCD UI không mở được

Kiểm tra service:

```bash
kubectl -n argocd get svc argocd-server
```

Chạy lại port-forward với port khác:

```bash
kubectl -n argocd port-forward svc/argocd-server 8081:443
```

Mở:

```text
https://localhost:8081
```

### ArgoCD app báo repo lỗi

Kiểm tra `repoURL`:

```bash
rg -n "repoURL:" gitops/bootstrap/argocd gitops/clusters/local
```

Nếu repo private, thêm credential trong ArgoCD UI:

```text
Settings -> Repositories -> Connect Repo
```

Sau đó sync lại app trong ArgoCD UI.

## Dừng Và Dọn Dẹp Lab

Dừng Rancher container nhưng giữ data:

```bash
docker compose --env-file infra/rancher-docker/.env \
  -f infra/rancher-docker/compose.yaml \
  down
```

Gỡ K3s nếu muốn xóa cluster local:

```bash
sudo /usr/local/bin/k3s-uninstall.sh
```

Chỉ xóa Docker volume nếu bạn chắc chắn không cần data Rancher nữa.

## Bước Tiếp Theo

Sau khi hoàn thành Phase 0 đến Phase 10:

1. Đọc lại `docs/deployment-roadmap.md` phần Phase 11.
2. Chỉ chọn một hướng nâng cấp sau MVP, ví dụ Harbor, Longhorn, Vault/External Secrets hoặc multi-environment.
3. Nếu dùng repo này cho môi trường thật, tách `app-repo` và `gitops-repo` như khuyến nghị trong `README.md`.
4. Viết lại các password, domain, registry, backup endpoint theo môi trường của bạn trước khi dùng lâu dài.
