# Kubernetes Beginner Architecture Report Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Update `docs/architecture.md` so someone new to Kubernetes can understand the Rancher/K3s/ArgoCD/GitOps platform and the `clipproxy` application.

**Architecture:** Keep the existing architecture document as the canonical report, but expand it with a beginner mental model, GitOps and runtime flows, a Kubernetes object glossary, a `clipproxy` section, and a troubleshooting map. Add lightweight string-based tests so the educational anchors remain present.

**Tech Stack:** Markdown, Mermaid diagrams, Kubernetes concepts, Rancher, K3s, ArgoCD, GitOps, Pytest.

## Global Constraints

- Rewrite or expand `docs/architecture.md` as a beginner-friendly architecture report.
- Explain the roles of Rancher, K3s/Kubernetes, ArgoCD, GitOps, Ingress, and application manifests.
- Explain how `sample-api` and `clipproxy` are deployed.
- Add a `clipproxy` architecture section covering API, manager, ConfigMap, Secret, PVCs, Service, and Ingress.
- Include runtime request flow for `http://clipproxy.local`.
- Include a troubleshooting map for common ArgoCD/Kubernetes states such as `NotFound`, `Synced`, `Degraded`, `CrashLoopBackOff`, `Pending`, and `too many open files`.
- Add lightweight tests that pin key educational content in `docs/architecture.md`.
- Do not change Kubernetes manifests.
- Do not change application code.
- Do not run deployment commands.
- Do not print or inspect secret values.
- Do not add a full Kubernetes textbook.

---

## File Structure

- `docs/architecture.md` — canonical architecture report; expand it for Kubernetes beginners and include `clipproxy`.
- `tests/test_architecture_report.py` — focused string tests for the new beginner architecture anchors.
- `docs/superpowers/specs/2026-08-01-kubernetes-beginner-architecture-report-design.md` — design spec already written.
- `docs/superpowers/plans/2026-08-01-kubernetes-beginner-architecture-report.md` — this implementation plan.

## Task 1: Pin beginner architecture anchors with tests

**Files:**
- Create: `tests/test_architecture_report.py`

**Interfaces:**
- Consumes: `docs/architecture.md` text.
- Produces: tests that require beginner mental model, GitOps flow, runtime flow, `clipproxy`, troubleshooting states, and read-only command examples.

- [ ] **Step 1: Write the failing architecture report tests**

Create `tests/test_architecture_report.py`:

```python
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_repo_file(relative_path: str) -> str:
    return (ROOT / relative_path).read_text()


def test_architecture_report_explains_beginner_mental_model():
    architecture = read_repo_file("docs/architecture.md")

    assert "## 2. Mental model cho người mới Kubernetes" in architecture
    assert "Git is the source of truth" in architecture
    assert "ArgoCD là robot đồng bộ" in architecture
    assert "Kubernetes là runtime" in architecture
    assert "Rancher là lớp quan sát và quản trị" in architecture


def test_architecture_report_traces_gitops_and_runtime_flows():
    architecture = read_repo_file("docs/architecture.md")

    assert "root-local" in architecture
    assert "platform-local" in architecture
    assert "sample-api-local" in architecture
    assert "clipproxy-local" in architecture
    assert "Ingress -> Service -> Pod" in architecture
    assert "http://clipproxy.local" in architecture
    assert "clipproxy.local -> Ingress -> clipproxy-manager Service -> clipproxy-manager Pod" in architecture


def test_architecture_report_explains_kubernetes_objects_with_repo_examples():
    architecture = read_repo_file("docs/architecture.md")

    assert "Namespace" in architecture
    assert "Deployment" in architecture
    assert "Pod" in architecture
    assert "Service" in architecture
    assert "Ingress" in architecture
    assert "ConfigMap" in architecture
    assert "Secret" in architecture
    assert "PersistentVolumeClaim" in architecture
    assert "ArgoCD Application" in architecture


def test_architecture_report_documents_clipproxy_architecture_and_troubleshooting():
    architecture = read_repo_file("docs/architecture.md")

    assert "## 9. Kiến trúc ứng dụng: sample-api và clipproxy" in architecture
    assert "clipproxy-api" in architecture
    assert "clipproxy-manager" in architecture
    assert "clipproxy-secret" in architecture
    assert "clipproxy-api-data" in architecture
    assert "clipproxy-manager-data" in architecture
    assert "too many open files" in architecture
    assert "CrashLoopBackOff" in architecture
    assert "Degraded" in architecture
    assert "Pending" in architecture
    assert "kubectl -n clipproxy logs deploy/clipproxy-api --tail=50" in architecture
```

- [ ] **Step 2: Run the new tests and confirm they fail**

Run:

```bash
python3 -m pytest tests/test_architecture_report.py -q
```

Expected: fail until `docs/architecture.md` contains the new beginner-focused sections.

## Task 2: Update `docs/architecture.md`

**Files:**
- Modify: `docs/architecture.md`

**Interfaces:**
- Consumes: existing architecture report and current GitOps layout.
- Produces: beginner-friendly architecture report with required sections and commands.

- [ ] **Step 1: Replace `docs/architecture.md` with the updated report**

Write a Markdown report that includes these exact section anchors and educational strings:

```markdown
# Architecture report: Rancher, K3s, ArgoCD, GitOps và clipproxy

Repo này là template học DevOps/Kubernetes cho Rancher, K3s, ArgoCD và GitOps. Tài liệu này viết cho người mới tiếp xúc với Kubernetes: đọc từ mental model trước, sau đó mới đi vào manifest, luồng deploy, runtime request và cách debug.

## 1. Executive summary

Repo này mô phỏng một platform Kubernetes local. Git chứa desired state, ArgoCD đọc Git và đồng bộ cluster, Kubernetes chạy workload, Rancher giúp quan sát và quản trị cluster.

Luồng quan trọng nhất:

```text
Developer -> Git push -> ArgoCD sync -> Kubernetes resources -> Pod chạy app -> Người dùng truy cập qua Ingress
```

## 2. Mental model cho người mới Kubernetes

- Git is the source of truth: trạng thái mong muốn của cluster nằm trong repo, chủ yếu ở `gitops/`.
- ArgoCD là robot đồng bộ: ArgoCD so sánh Git với cluster rồi tạo/sửa/xóa resource để cluster giống Git.
- Kubernetes là runtime: Kubernetes nhận manifest và chạy Pod, Service, Ingress, PVC, Secret, ConfigMap.
- Rancher là lớp quan sát và quản trị: Rancher giúp nhìn cluster, workload, namespace, event, log và trạng thái tài nguyên qua UI.

Nếu bạn mới học, hãy nhớ: không sửa tay trong cluster trước. Sửa Git trước, để ArgoCD sync, rồi dùng `kubectl` hoặc Rancher UI để quan sát.
```

Continue the document with these topics:

- repository map,
- cluster and GitOps architecture,
- GitOps deployment flow,
- runtime request flow with `Ingress -> Service -> Pod`,
- Kubernetes object glossary,
- platform components,
- application architecture for `sample-api` and `clipproxy`,
- troubleshooting map,
- read-only command cheat sheet.

The final document must include these exact snippets:

```text
clipproxy.local -> Ingress -> clipproxy-manager Service -> clipproxy-manager Pod
```

```bash
kubectl -n clipproxy logs deploy/clipproxy-api --tail=50
```

- [ ] **Step 2: Run the architecture report tests**

Run:

```bash
python3 -m pytest tests/test_architecture_report.py -q
```

Expected: pass.

## Task 3: Final verification

**Files:**
- Verify: `docs/architecture.md`
- Verify: `tests/test_architecture_report.py`
- Verify: architecture spec and plan docs

**Interfaces:**
- Consumes: completed doc/test update.
- Produces: verification evidence.

- [ ] **Step 1: Run the focused architecture test**

Run:

```bash
python3 -m pytest tests/test_architecture_report.py -q
```

Expected: pass.

- [ ] **Step 2: Run the root test suite**

Run:

```bash
python3 -m pytest -q
```

Expected: pass.

- [ ] **Step 3: Review status**

Run:

```bash
git status --short
```

Expected: only `.claude/`, `.codegraph/`, `docs/architecture.md`, `docs/superpowers/specs/2026-08-01-kubernetes-beginner-architecture-report-design.md`, `docs/superpowers/plans/2026-08-01-kubernetes-beginner-architecture-report.md`, and `tests/test_architecture_report.py` are uncommitted/untracked.

## Plan Self-Review

- Spec coverage: The plan covers beginner mental model, GitOps flow, runtime flow, object glossary, `clipproxy`, troubleshooting states, and read-only commands.
- Scope control: The plan changes documentation and tests only; it does not change manifests or app code.
- Test strategy: The plan pins specific educational anchors with string tests and verifies the root suite.
