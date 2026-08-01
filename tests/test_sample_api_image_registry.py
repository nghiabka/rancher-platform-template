from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCKER_HUB_IMAGE = "nghiadvbka/sample-api"


def read_repo_file(relative_path: str) -> str:
    return (ROOT / relative_path).read_text()


def test_local_overlay_rewrites_sample_api_image_to_docker_hub_release_tag():
    overlay = read_repo_file("gitops/apps/sample-api/overlays/local/kustomization.yaml")

    assert "name: localhost:5000/sample-api" in overlay
    assert f"newName: {DOCKER_HUB_IMAGE}" in overlay
    assert "newTag:" in overlay
    assert "newTag: local" not in overlay


def test_build_helper_pushes_sample_api_to_docker_hub_by_default():
    script = read_repo_file("bin/build-local-sample-api.sh")

    assert f'IMAGE="${{IMAGE:-{DOCKER_HUB_IMAGE}:local}}"' in script


def test_github_actions_uses_docker_hub_image_and_login():
    workflow = read_repo_file("ci/github/sample-api-ci.yaml")

    assert f"IMAGE_NAME: {DOCKER_HUB_IMAGE}" in workflow
    assert 'echo "IMAGE_TAG=${GITHUB_SHA::12}" >> "$GITHUB_ENV"' in workflow
    assert "secrets.DOCKERHUB_TOKEN" in workflow
    assert "if: github.event_name == 'push'" in workflow
    assert 'docker login -u "nghiadvbka" --password-stdin' in workflow
    assert "python -m pytest" in workflow
    assert "ignore-unfixed: true" in workflow
    assert 'kustomize edit set image "localhost:5000/sample-api=$IMAGE_NAME:$IMAGE_TAG"' in workflow


def test_sample_api_dockerfile_runs_as_non_root_uid():
    dockerfile = read_repo_file("apps/sample-api/Dockerfile")

    assert "USER 10001" in dockerfile


def test_sample_api_deployment_runs_with_non_root_uid():
    deployment = read_repo_file("gitops/apps/sample-api/base/deployment.yaml")

    assert "runAsNonRoot: true" in deployment
    assert "runAsUser: 10001" in deployment


def test_local_overlay_forces_pull_on_mutable_local_tag():
    overlay = read_repo_file("gitops/apps/sample-api/overlays/local/kustomization.yaml")
    patch = read_repo_file("gitops/apps/sample-api/overlays/local/deployment-patch.yaml")

    assert "patchesStrategicMerge:" in overlay
    assert "- deployment-patch.yaml" in overlay
    assert "imagePullPolicy: Always" in patch
