from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_repo_file(relative_path: str) -> str:
    return (ROOT / relative_path).read_text()


def test_sample_api_sealed_secret_example_is_not_in_default_resources():
    overlay = read_repo_file("gitops/apps/sample-api/overlays/local/kustomization.yaml")
    example = read_repo_file("gitops/apps/sample-api/overlays/local/sealed-secret.example.yaml")

    assert "- sealed-secret.example.yaml" not in overlay
    assert "kind: SealedSecret" in example
    assert "metadata:" in example
    assert "name: sample-api-demo-secret" in example
    assert "namespace: sample-api" in example


def test_sample_api_sealed_secret_example_has_placeholder_payload():
    example = read_repo_file("gitops/apps/sample-api/overlays/local/sealed-secret.example.yaml")

    assert "PLACEHOLDER_GENERATED_BY_KUBESEAL" in example
    assert "template:" in example
    assert "type: Opaque" in example


def test_sample_api_deployment_sources_secret_env_var():
    deployment = read_repo_file("gitops/apps/sample-api/base/deployment.yaml")

    assert "name: DEMO_SECRET_VALUE" in deployment
    assert "secretKeyRef:" in deployment
    assert "name: sample-api-demo-secret" in deployment
    assert "key: DEMO_VALUE" in deployment
    assert "optional: true" in deployment


def test_tutorial_phase_8_explains_kubeseal_workflow():
    tutorial = read_repo_file("docs/tutorial-phase-0-3.md")

    assert "## Phase 8: Secrets Management" in tutorial
    assert "kubectl apply -n argocd -f gitops/platform/50-secrets/sealed-secrets.yaml" in tutorial
    assert "kubeseal --version" in tutorial
    assert "sample-api-demo-secret" in tutorial
    assert "sealed-secret.example.yaml" in tutorial
    assert "verify the pod receives the env var without exposing secret value" in tutorial
    assert "sealed-secrets" in tutorial
    assert "ArgoCD" in tutorial
    assert "temp Secret outside the repo" in tutorial
    assert "seal it to a manifest for the overlay/example path" in tutorial
