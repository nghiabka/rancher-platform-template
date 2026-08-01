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
