from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCKER_HUB_IMAGE = "nghiadvbka/sample-api"


def read_repo_file(relative_path: str) -> str:
    return (ROOT / relative_path).read_text()


def test_local_overlay_rewrites_sample_api_image_to_docker_hub():
    overlay = read_repo_file("gitops/apps/sample-api/overlays/local/kustomization.yaml")

    assert "name: localhost:5000/sample-api" in overlay
    assert f"newName: {DOCKER_HUB_IMAGE}" in overlay
    assert "newTag: local" in overlay


def test_build_helper_pushes_sample_api_to_docker_hub_by_default():
    script = read_repo_file("bin/build-local-sample-api.sh")

    assert f'IMAGE="${{IMAGE:-{DOCKER_HUB_IMAGE}:local}}"' in script


def test_github_actions_uses_docker_hub_image_and_login():
    workflow = read_repo_file("ci/github/sample-api-ci.yaml")

    assert f"IMAGE_NAME: {DOCKER_HUB_IMAGE}" in workflow
    assert "secrets.DOCKERHUB_TOKEN" in workflow
    assert 'docker login -u "nghiadvbka" --password-stdin' in workflow
    assert 'kustomize edit set image "localhost:5000/sample-api=$IMAGE_NAME:$IMAGE_TAG"' in workflow
