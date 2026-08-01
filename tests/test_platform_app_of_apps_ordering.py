from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_repo_file(relative_path: str) -> str:
    return (ROOT / relative_path).read_text()


def test_backup_parent_does_not_sync_velero_crs_before_crd_app():
    backup = read_repo_file("gitops/platform/60-backup/kustomization.yaml")

    assert "velero.yaml" in backup
    assert "schedules.yaml" not in backup


def test_policy_parent_does_not_sync_kyverno_crs_before_crd_app():
    policy = read_repo_file("gitops/platform/80-policy/kustomization.yaml")

    assert "kyverno.yaml" in policy
    assert "require-non-root-policy.yaml" not in policy


def test_kyverno_app_uses_server_side_apply_for_crds():
    kyverno = read_repo_file("gitops/platform/80-policy/kyverno.yaml")

    assert "ServerSideApply=true" in kyverno


def test_velero_app_uses_server_side_apply_for_crds():
    velero = read_repo_file("gitops/platform/60-backup/velero.yaml")

    assert "ServerSideApply=true" in velero
