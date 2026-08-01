from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_repo_file(relative_path: str) -> str:
    return (ROOT / relative_path).read_text()


def test_gitlab_ci_builds_scans_and_pushes_sample_api():
    workflow = read_repo_file("ci/gitlab/sample-api-ci.yml")

    assert 'IMAGE_NAME: "$CI_REGISTRY_IMAGE/sample-api"' in workflow
    assert 'IMAGE_TAG: "$CI_COMMIT_SHORT_SHA"' in workflow
    assert "cd apps/sample-api" in workflow
    assert "pip install -r requirements.txt" in workflow
    assert "python -m pytest" in workflow
    assert 'docker login -u "$CI_REGISTRY_USER" -p "$CI_REGISTRY_PASSWORD" "$CI_REGISTRY"' in workflow
    assert 'docker build -t "$IMAGE_NAME:$IMAGE_TAG" apps/sample-api' in workflow
    assert 'docker push "$IMAGE_NAME:$IMAGE_TAG"' in workflow
    assert 'trivy image --exit-code 1 --ignore-unfixed --severity HIGH,CRITICAL "$IMAGE_NAME:$IMAGE_TAG"' in workflow
