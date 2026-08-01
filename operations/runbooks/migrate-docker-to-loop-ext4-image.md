# Migrate Docker Data Root to an ext4 Loop Image

> Runbook này dành cho lab/dev trên máy hiện tại: `/` còn ít dung lượng, `/data` còn nhiều dung lượng nhưng là NTFS/fuseblk. Mục tiêu là tạo một file image ext4 trong `/data`, mount ra `/srv/platform-data`, rồi chuyển Docker data-root sang `/srv/platform-data/docker`.

## Mục tiêu cuối cùng

```text
/data/platform-data.img       # file image nằm trên /data
        ↓ loop mount
/srv/platform-data            # mount ext4
        ↓
/srv/platform-data/docker     # Docker data-root mới
```

Sau khi hoàn tất, lệnh này phải trả về:

```bash
docker info --format '{{.DockerRootDir}}'
```

Kết quả mong muốn:

```text
/srv/platform-data/docker
```

## Cảnh báo quan trọng

- Không dùng trực tiếp `/data/...` làm Docker/Rancher volume nếu `/data` là NTFS/fuseblk.
- Không chạy lại `mkfs.ext4` trên `/data/platform-data.img` sau khi đã migrate Docker data vào đó, vì lệnh đó sẽ format/xóa dữ liệu trong image.
- Không xóa `/var/lib/docker` cũ ngay. Chỉ xóa sau khi Docker/Rancher chạy ổn và đã reboot test thành công.
- Đây là giải pháp lab/dev, không khuyến nghị production.

---

# Phase 0: Kiểm tra trạng thái hiện tại

## 0.1 Kiểm tra disk

```bash
df -hT / /data
```

Kỳ vọng:

- `/` còn ít dung lượng.
- `/data` còn đủ dung lượng để chứa image, ví dụ 120GB.

## 0.2 Kiểm tra Docker root hiện tại

```bash
docker info --format '{{.DockerRootDir}}'
```

Nếu chưa migrate, thường là:

```text
/var/lib/docker
```

## 0.3 Kiểm tra Rancher đang chạy không

```bash
docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}'
```

---

# Phase 1: Tạo file image ext4 trong /data

## 1.1 Chọn size image

Ví dụ dưới dùng 120 GiB:

```text
120 GiB = 122880 MiB
```

Nếu muốn size khác:

```text
100 GiB = 102400 MiB
150 GiB = 153600 MiB
200 GiB = 204800 MiB
```

## 1.2 Tạo image bằng dd

Do `/data` là NTFS/fuseblk, `fallocate` có thể lỗi `Operation not supported`. Dùng `dd`:

```bash
sudo dd if=/dev/zero of=/data/platform-data.img bs=1M count=122880 status=progress
```

Lệnh này ghi thật 120GB, có thể chạy lâu.

## 1.3 Kiểm tra file image

```bash
ls -lh /data/platform-data.img
du -h /data/platform-data.img
```

Kỳ vọng thấy file khoảng 120GB.

## 1.4 Format image thành ext4

> Chỉ chạy bước này khi image còn mới/chưa chứa dữ liệu Docker.

```bash
sudo mkfs.ext4 -F -L platform-data /data/platform-data.img
```

## 1.5 Tạo mount point

```bash
sudo mkdir -p /srv/platform-data
```

## 1.6 Mount thử

```bash
sudo mount -o loop,noatime /data/platform-data.img /srv/platform-data
```

Nếu gặp lỗi:

```text
mount point does not exist
```

thì chạy lại:

```bash
sudo mkdir -p /srv/platform-data
sudo mount -o loop,noatime /data/platform-data.img /srv/platform-data
```

## 1.7 Verify mount

```bash
findmnt /srv/platform-data
df -hT /srv/platform-data
```

Kết quả mong muốn: `/srv/platform-data` là `ext4`, ví dụ:

```text
/dev/loopX ext4 ... /srv/platform-data
```

Nếu không phải `ext4`, dừng lại và xử lý trước khi sang phase tiếp theo.

---

# Phase 2: Cấu hình auto-mount khi boot

## 2.1 Backup /etc/fstab

```bash
sudo cp /etc/fstab /etc/fstab.bak.$(date +%F-%H%M%S)
```

## 2.2 Thêm dòng mount vào /etc/fstab

Mở file:

```bash
sudo nano /etc/fstab
```

Thêm dòng này vào cuối file:

```fstab
/data/platform-data.img /srv/platform-data ext4 loop,noatime,nofail,x-systemd.requires-mounts-for=/data,x-systemd.before=docker.service 0 0
```

Giải thích nhanh:

- `loop`: mount file image như block device.
- `noatime`: giảm ghi metadata khi đọc file.
- `nofail`: nếu mount lỗi, máy vẫn boot được.
- `x-systemd.requires-mounts-for=/data`: đảm bảo `/data` mount trước.
- `x-systemd.before=docker.service`: mount image trước Docker.
- `0 0`: không tự fsck image lúc boot.

## 2.3 Reload systemd và test fstab

```bash
sudo systemctl daemon-reload
sudo umount /srv/platform-data
sudo mount -a
```

Verify:

```bash
findmnt /srv/platform-data
df -hT /srv/platform-data
```

Kết quả mong muốn: `/srv/platform-data` đang mounted và type là `ext4`.

Nếu `mount -a` báo lỗi hoặc `findmnt` không thấy `/srv/platform-data`, dừng lại và sửa `/etc/fstab` trước.

---

# Phase 3: Bắt Docker chờ /srv/platform-data mount trước khi start

## 3.1 Ghi systemd override cho Docker

Cách ghi trực tiếp bằng `tee`:

```bash
sudo mkdir -p /etc/systemd/system/docker.service.d

sudo tee /etc/systemd/system/docker.service.d/override.conf >/dev/null <<'EOF'
[Unit]
RequiresMountsFor=/srv/platform-data
After=local-fs.target
EOF
```

## 3.2 Reload systemd

```bash
sudo systemctl daemon-reload
```

## 3.3 Verify override

```bash
systemctl cat docker
```

Kỳ vọng thấy đoạn sau ở cuối output:

```ini
# /etc/systemd/system/docker.service.d/override.conf
[Unit]
RequiresMountsFor=/srv/platform-data
After=local-fs.target
```

## 3.4 Verify mount vẫn còn

```bash
findmnt /srv/platform-data
df -hT /srv/platform-data
```

Không sang phase tiếp nếu `/srv/platform-data` chưa mounted là `ext4`.

---

# Phase 4: Dừng Rancher và Docker trước khi copy data

## 4.1 Dừng Rancher compose

Chạy từ repo:

```bash
cd /data/learning/rancher-platform-template
docker compose -f infra/rancher-docker/compose.yaml down
```

Lệnh này dừng Rancher container nhưng không xóa Docker volume.

## 4.2 Dừng Docker

```bash
sudo systemctl stop docker.service docker.socket
```

Nếu `docker.socket` không tồn tại hoặc báo lỗi thì không sao.

## 4.3 Verify Docker đã dừng

```bash
systemctl status docker --no-pager
```

Kỳ vọng Docker đang `inactive` hoặc đã stop.

---

# Phase 5: Copy Docker data cũ sang /srv/platform-data/docker

## 5.1 Đảm bảo mount vẫn tồn tại

```bash
findmnt /srv/platform-data
df -hT /srv/platform-data
```

Kết quả bắt buộc: `/srv/platform-data` là `ext4`.

## 5.2 Tạo thư mục data-root mới

```bash
sudo mkdir -p /srv/platform-data/docker
```

## 5.3 Copy Docker data

```bash
sudo rsync -aHAX --numeric-ids /var/lib/docker/ /srv/platform-data/docker/
```

Lệnh này có thể chạy lâu.

Nếu máy không có `rsync`, cài bằng:

```bash
sudo apt update
sudo apt install -y rsync
```

Rồi chạy lại lệnh copy.

## 5.4 Kiểm tra dung lượng hai bên

```bash
sudo du -sh /var/lib/docker
sudo du -sh /srv/platform-data/docker
```

Dung lượng hai bên nên gần tương đương.

---

# Phase 6: Cấu hình Docker dùng data-root mới

## 6.1 Backup Docker daemon.json nếu có

```bash
sudo mkdir -p /etc/docker

if [ -f /etc/docker/daemon.json ]; then
  sudo cp /etc/docker/daemon.json /etc/docker/daemon.json.bak.$(date +%F-%H%M%S)
fi
```

## 6.2 Ghi data-root bằng Python, giữ config cũ nếu có

```bash
sudo python3 - <<'PY'
import json
from pathlib import Path

path = Path('/etc/docker/daemon.json')

if path.exists() and path.read_text().strip():
    data = json.loads(path.read_text())
else:
    data = {}

data['data-root'] = '/srv/platform-data/docker'

path.write_text(json.dumps(data, indent=2) + '\n')
PY
```

## 6.3 Kiểm tra daemon.json

```bash
sudo cat /etc/docker/daemon.json
```

Kỳ vọng có:

```json
{
  "data-root": "/srv/platform-data/docker"
}
```

Nếu file có thêm config khác thì vẫn ổn, miễn có `data-root` đúng.

---

# Phase 7: Start Docker lại và verify

## 7.1 Reload systemd

```bash
sudo systemctl daemon-reload
```

## 7.2 Start Docker

```bash
sudo systemctl start docker.service
```

Nếu cần start socket:

```bash
sudo systemctl start docker.socket 2>/dev/null || true
```

## 7.3 Kiểm tra Docker root mới

```bash
docker info --format '{{.DockerRootDir}}'
```

Kết quả bắt buộc:

```text
/srv/platform-data/docker
```

Nếu vẫn là `/var/lib/docker`, dừng lại và kiểm tra lại `/etc/docker/daemon.json`.

## 7.4 Kiểm tra containers/images/volumes

```bash
docker ps -a
docker images
docker volume ls
docker system df -v
```

Bạn nên vẫn thấy Rancher image/container/volume cũ.

---

# Phase 8: Start Rancher lại

## 8.1 Start Rancher compose

```bash
cd /data/learning/rancher-platform-template
docker compose -f infra/rancher-docker/compose.yaml up -d
```

## 8.2 Kiểm tra container

```bash
docker ps
```

Kỳ vọng thấy container `rancher` đang running.

## 8.3 Kiểm tra log Rancher

```bash
docker logs --tail=100 rancher
```

Nếu muốn follow log:

```bash
docker logs -f rancher
```

---

# Phase 9: Reboot test

## 9.1 Reboot

```bash
sudo reboot
```

## 9.2 Sau khi máy lên lại, kiểm tra mount

```bash
findmnt /srv/platform-data
df -hT /srv/platform-data
```

Kết quả mong muốn: `/srv/platform-data` là `ext4`.

## 9.3 Kiểm tra Docker root

```bash
docker info --format '{{.DockerRootDir}}'
```

Kết quả mong muốn:

```text
/srv/platform-data/docker
```

## 9.4 Kiểm tra Rancher

```bash
docker ps
```

Nếu Rancher chưa chạy lại, start thủ công:

```bash
cd /data/learning/rancher-platform-template
docker compose -f infra/rancher-docker/compose.yaml up -d
```

---

# Phase 10: Giải phóng dung lượng / sau khi đã chắc chắn

> Không làm phase này ngay. Chỉ làm sau khi Docker/Rancher chạy ổn, reboot test thành công, và bạn chắc chắn không cần rollback nhanh.

## 10.1 Đổi tên Docker data cũ trước

Dừng Docker:

```bash
sudo systemctl stop docker.service docker.socket
```

Đổi tên data cũ:

```bash
sudo mv /var/lib/docker /var/lib/docker.old
```

Start Docker lại:

```bash
sudo systemctl start docker.service
```

Verify:

```bash
docker info --format '{{.DockerRootDir}}'
docker ps -a
```

Docker root vẫn phải là:

```text
/srv/platform-data/docker
```

Lưu ý: đổi tên thành `/var/lib/docker.old` chưa giải phóng dung lượng vì vẫn nằm trên `/`.

## 10.2 Xóa data cũ sau vài ngày ổn định

Chỉ chạy khi chắc chắn mọi thứ ổn:

```bash
sudo rm -rf /var/lib/docker.old
```

Kiểm tra root disk:

```bash
df -hT /
```

---

# Rollback: Quay lại Docker data-root cũ nếu lỗi

Dùng rollback nếu Docker không start được hoặc Rancher mất data sau migration.

## R1: Dừng Docker

```bash
sudo systemctl stop docker.service docker.socket
```

## R2: Restore daemon.json từ backup nếu có

Liệt kê backup:

```bash
ls -lh /etc/docker/daemon.json.bak.*
```

Restore file backup gần nhất, ví dụ:

```bash
sudo cp /etc/docker/daemon.json.bak.YYYY-MM-DD-HHMMSS /etc/docker/daemon.json
```

Nếu không có backup, mở file:

```bash
sudo nano /etc/docker/daemon.json
```

Xóa dòng:

```json
"data-root": "/srv/platform-data/docker"
```

Nếu file chỉ có mỗi key đó, có thể để:

```json
{}
```

## R3: Nếu đã đổi tên /var/lib/docker thành /var/lib/docker.old

```bash
sudo mv /var/lib/docker.old /var/lib/docker
```

## R4: Start Docker lại

```bash
sudo systemctl daemon-reload
sudo systemctl start docker.service
```

Verify:

```bash
docker info --format '{{.DockerRootDir}}'
docker ps -a
```

Nếu rollback thành công, Docker root sẽ là:

```text
/var/lib/docker
```

---

# Troubleshooting

## Mount point does not exist

Lỗi:

```text
mount: /srv/platform-data: mount point does not exist
```

Fix:

```bash
sudo mkdir -p /srv/platform-data
sudo mount -o loop,noatime /data/platform-data.img /srv/platform-data
```

## fallocate failed: Operation not supported

Lỗi này do `/data` là NTFS/fuseblk. Dùng `dd` thay vì `fallocate`:

```bash
sudo dd if=/dev/zero of=/data/platform-data.img bs=1M count=122880 status=progress
```

## Docker start trước khi mount

Kiểm tra override:

```bash
systemctl cat docker
```

Phải thấy:

```ini
[Unit]
RequiresMountsFor=/srv/platform-data
After=local-fs.target
```

Kiểm tra mount:

```bash
findmnt /srv/platform-data
```

## Docker không start được

Xem log:

```bash
systemctl status docker --no-pager
journalctl -u docker -b --no-pager | tail -200
```

Các nguyên nhân thường gặp:

- `/srv/platform-data` chưa mounted.
- `/etc/docker/daemon.json` sai JSON.
- `/srv/platform-data/docker` thiếu quyền hoặc copy chưa đầy đủ.

## Kiểm tra daemon.json có hợp lệ không

```bash
python3 -m json.tool /etc/docker/daemon.json
```

Nếu có lỗi JSON, sửa file:

```bash
sudo nano /etc/docker/daemon.json
```

## Image ext4 cần fsck

Chỉ chạy khi Docker đã stop và image chưa mounted:

```bash
sudo systemctl stop docker.service docker.socket
sudo umount /srv/platform-data 2>/dev/null || true
sudo e2fsck -f /data/platform-data.img
sudo mount -a
sudo systemctl start docker.service
```

---

# Checklist hoàn thành

- [ ] `/data/platform-data.img` tồn tại.
- [ ] `/srv/platform-data` mounted là ext4.
- [ ] `/etc/fstab` có dòng mount image.
- [ ] `systemctl cat docker` có `RequiresMountsFor=/srv/platform-data`.
- [ ] Docker data đã copy sang `/srv/platform-data/docker`.
- [ ] `/etc/docker/daemon.json` có `data-root` mới.
- [ ] `docker info --format '{{.DockerRootDir}}'` trả về `/srv/platform-data/docker`.
- [ ] Rancher container chạy lại bình thường.
- [ ] Reboot xong `/srv/platform-data` vẫn mount trước Docker.
- [ ] Sau vài ngày ổn định mới xóa `/var/lib/docker.old`.
