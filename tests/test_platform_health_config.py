from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_repo_file(relative_path: str) -> str:
    return (ROOT / relative_path).read_text()


def test_sealed_secrets_uses_current_bitnami_helm_repo():
    sealed_secrets = read_repo_file("gitops/platform/50-secrets/sealed-secrets.yaml")

    assert "repoURL: https://bitnami.github.io/sealed-secrets" in sealed_secrets
    assert "bitnami-labs.github.io/sealed-secrets" not in sealed_secrets
    assert "chart: sealed-secrets" in sealed_secrets


def test_letsencrypt_staging_issuer_does_not_use_forbidden_example_email():
    cluster_issuers = read_repo_file("gitops/platform/20-cert-manager/cluster-issuers.yaml")

    assert "name: letsencrypt-staging" in cluster_issuers
    assert "platform@example.com" not in cluster_issuers
    assert "email: admin@justnghia.dev" in cluster_issuers
