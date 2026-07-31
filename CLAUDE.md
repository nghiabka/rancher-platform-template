# Project instructions

## Scope

- Đây là template học DevOps/Kubernetes cho Rancher, K3s, ArgoCD và GitOps.
- `apps/sample-api/` là ứng dụng mẫu; `gitops/` chứa Kubernetes manifests; `infra/` chứa Docker/K3s/local services; `bin/` chứa script hỗ trợ.
- Repo không có tích hợp Claude/Anthropic API.

## Working rules

- Với yêu cầu đơn giản, chỉ đọc các file liên quan trực tiếp; không quét toàn bộ repo hoặc thư mục cha.
- Nếu repo có `.codegraph/`, ưu tiên CodeGraph trước `rg`/`Read` khi cần hiểu luồng code, tìm symbol, call path hoặc blast radius; với MCP, truyền repo root hiện tại làm `projectPath`.
- Nếu repo chưa có `.codegraph/`, dùng `rg`/`rg --files` để tìm kiếm thay vì duyệt đệ quy không giới hạn; bật index bằng `codegraph init` tại repo root khi cần.

## CodeGraph prompt examples

- "Dùng codegraph trace luồng từ <entrypoint> tới <output>."
- "Dùng codegraph tìm symbol/file chịu trách nhiệm cho <behavior>."
- "Dùng codegraph kiểm tra blast radius nếu sửa <symbol/file>."
- "Dùng codegraph xem các caller của <function> trước khi sửa."

- Không chạy `docker`, `kubectl`, `helm`, `pytest` hoặc lệnh triển khai nếu người dùng chưa yêu cầu rõ.
- Commit message không được tự thêm dòng `Co-Authored-By: Claude <noreply@anthropic.com>`
- Khi hiển thị lịch sử commit, ưu tiên format ngắn không in commit body/trailer như `git log --oneline --decorate` hoặc `git log --format='%h %s'`, trừ khi người dùng yêu cầu xem commit message đầy đủ.
- Không đọc hoặc in secret, kubeconfig, `.env` hay credential files.
- Trước khi sửa, kiểm tra `git diff` và giữ nguyên các thay đổi không liên quan.
- Sau khi sửa, chạy kiểm tra nhỏ nhất phù hợp với thay đổi và báo rõ lệnh đã chạy.
- merge code thì không cần phải test

## Suggested checks

- Markdown/YAML: kiểm tra diff và cấu trúc file liên quan.
- Python sample API: `cd apps/sample-api && python -m pytest`.
- GitOps manifests: `bin/render-gitops.sh` chỉ khi người dùng yêu cầu render hoặc thay đổi manifest.

## Response style

- Nêu kết luận trước, sau đó mới giải thích ngắn gọn.
- Nếu thiếu thông tin, đưa ra giả định an toàn và tiếp tục; chỉ hỏi lại khi không thể thực hiện đúng phạm vi.
- Với tác vụ chỉ cần tư vấn, không tự ý chỉnh sửa file hay chạy lệnh có side effect.
