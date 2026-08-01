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
