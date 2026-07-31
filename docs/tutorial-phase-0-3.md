# Tutorial Chạy Phase 0 Đến Phase 3

Tutorial này hướng dẫn chạy từng bước từ host trống đến khi có Rancher, K3s cluster và ArgoCD GitOps bootstrap.

Phạm vi:

- Phase 0: Chuẩn bị host.
- Phase 1: Chạy Rancher Manager Web UI bằng Docker.
- Phase 2: Tạo K3s cluster và import vào Rancher.
- Phase 3: Cài ArgoCD và bootstrap GitOps root app.

Nguyên tắc chạy lab:

- Không chạy tất cả phase cùng lúc.
- Mỗi phase phải verify xong mới sang phase tiếp theo.
- Không commit file chứa secret như `.env`, kubeconfig hoặc password thật.
- Các lệnh `docker`, `kubectl`, `helm` trong file này là lệnh để bạn tự chạy khi đã sẵn sàng.

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
K3s cluster Ready và được import vào Rancher
  |
  v
Phase 3
ArgoCD được cài và quản lý GitOps root app
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

## Phase 2: Tạo K3s Cluster Và Import Vào Rancher

### Mục Tiêu

Sau phase này bạn cần có:

- K3s server chạy local.
- `kubectl get nodes` trả về node Ready.
- Cluster xuất hiện trong Rancher và có trạng thái Active.

### Bước 2.1: Cài K3s với Traefik disabled

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

### Bước 2.2: Cấu hình kubeconfig

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
NAME      STATUS   ROLES                  AGE   VERSION
...
...       Ready    control-plane,master   ...   v...
```

Nếu muốn dùng kubeconfig này lâu dài, thêm vào shell profile của bạn:

```bash
echo 'export KUBECONFIG=$HOME/.kube/k3s.yaml' >> ~/.bashrc
```

Mở terminal mới hoặc chạy:

```bash
source ~/.bashrc
```

### Bước 2.3: Import cluster vào Rancher

Trước khi import, đảm bảo kubectl đang trỏ đúng K3s cluster:

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
2. Rancher sẽ sinh ra một command import.
3. Copy command đó.
4. Chạy command trên máy host đang dùng kubeconfig K3s.

Sau khi chạy command import, verify pod agent của Rancher:

```bash
kubectl get pods -A | grep cattle
```

Quay lại Rancher UI và chờ cluster chuyển sang `Active`.

### Checkpoint Phase 2

Chỉ sang Phase 3 khi:

- `kubectl get nodes` hiển thị node `Ready`.
- Rancher UI hiển thị cluster local.
- Cluster trong Rancher có trạng thái `Active`.

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

### Bước 3.3: Mở ArgoCD UI bằng port-forward

```bash
kubectl -n argocd port-forward svc/argocd-server 8080:443
```

Mở browser:

```text
https://localhost:8080
```

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

Sau khi hoàn thành Phase 0 đến Phase 3:

1. Đọc lại `docs/deployment-roadmap.md` từ Phase 4.
2. Cấu hình traffic layer với ingress-nginx và cert-manager.
3. Tiếp tục monitoring, logging, CI/CD, secrets, backup và policy theo từng phase.
