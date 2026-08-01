from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_repo_file(relative_path: str) -> str:
    return (ROOT / relative_path).read_text()


def test_phase_7_roadmap_marks_cicd_flow_complete():
    roadmap = read_repo_file("docs/deployment-roadmap.md")

    assert "## Phase 7: CI/CD End-To-End" in roadmap
    assert "Push code -> test -> build image -> scan -> push registry -> update GitOps -> ArgoCD deploy." in roadmap
    assert "- [x] Chon registry: Docker Hub cho CI/release, local registry cho lab." in roadmap
    assert "- [x] Cap nhat image name trong CI va GitOps manifests." in roadmap
    assert "- [x] Update image tag trong Kustomize overlay." in roadmap
    assert "- [x] Test rollback bang Git revert." in roadmap
    assert "Co pipeline release hoan chinh cho app mau." in roadmap


def test_phase_8_roadmap_mentions_sealed_secrets_and_kubeseal():
    roadmap = read_repo_file("docs/deployment-roadmap.md")

    assert "## Phase 8: Secrets Management" in roadmap
    assert "Khong commit secret plain text vao Git." in roadmap
    assert "- [x] Cai Sealed Secrets." in roadmap
    assert "- [x] Cai `kubeseal` tren may local." in roadmap
    assert "- [x] Seal secret thanh `SealedSecret`." in roadmap
    assert "- [x] Commit `SealedSecret` vao GitOps repo." in roadmap
    assert "Secrets duoc quan ly theo GitOps ma khong lo plain text leak." in roadmap
