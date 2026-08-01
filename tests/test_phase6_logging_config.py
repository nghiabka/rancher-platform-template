from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_repo_file(relative_path: str) -> str:
    return (ROOT / relative_path).read_text()


def test_loki_uses_test_schema_for_lab_filesystem_storage():
    loki = read_repo_file("gitops/platform/40-logging/loki.yaml")

    assert "useTestSchema: true" in loki
    assert "type: filesystem" in loki


def test_promtail_pushes_logs_to_loki_gateway():
    promtail = read_repo_file("gitops/platform/40-logging/promtail.yaml")

    assert "url: http://loki-gateway.logging.svc.cluster.local/loki/api/v1/push" in promtail


def test_grafana_has_loki_datasource():
    kube_prometheus_stack = read_repo_file(
        "gitops/platform/30-observability/kube-prometheus-stack.yaml"
    )

    assert "additionalDataSources:" in kube_prometheus_stack
    assert "name: Loki" in kube_prometheus_stack
    assert "type: loki" in kube_prometheus_stack
    assert "url: http://loki-gateway.logging.svc.cluster.local" in kube_prometheus_stack
