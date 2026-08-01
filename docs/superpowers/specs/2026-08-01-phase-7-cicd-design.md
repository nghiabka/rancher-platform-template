---
name: phase-7-cicd-design
description: Design for phase 7 end-to-end CI/CD for sample-api with Docker Hub release and local overlay support
metadata:
  type: project
---

# Phase 7: CI/CD End-To-End Design

## Goal

Phase 7 completes the release path for `sample-api` so the repository demonstrates a full DevOps loop:

1. Developer pushes code.
2. CI runs tests.
3. CI builds the image.
4. CI scans the image with Trivy.
5. CI pushes the image to Docker Hub.
6. CI updates the GitOps overlay image tag.
7. ArgoCD syncs the updated manifest.
8. The `sample-api` workload rolls out in cluster.

This phase stays focused on release automation for the sample app. It does not introduce Harbor, Sealed Secrets, or unrelated platform refactors.

## Scope

### In scope

- [apps/sample-api/](../../../apps/sample-api/)
- [bin/build-local-sample-api.sh](../../../bin/build-local-sample-api.sh)
- [ci/github/sample-api-ci.yaml](../../../ci/github/sample-api-ci.yaml)
- [ci/gitlab/sample-api-ci.yml](../../../ci/gitlab/sample-api-ci.yml)
- [gitops/apps/sample-api/base/deployment.yaml](../../../gitops/apps/sample-api/base/deployment.yaml)
- [gitops/apps/sample-api/overlays/local/kustomization.yaml](../../../gitops/apps/sample-api/overlays/local/kustomization.yaml)
- [gitops/apps/sample-api/overlays/local/deployment-patch.yaml](../../../gitops/apps/sample-api/overlays/local/deployment-patch.yaml)
- [gitops/clusters/local/sample-api.yaml](../../../gitops/clusters/local/sample-api.yaml)
- [tests/test_sample_api_image_registry.py](../../../tests/test_sample_api_image_registry.py)
- [docs/deployment-roadmap.md](../../../docs/deployment-roadmap.md)

### Out of scope

- Harbor setup
- Sealed Secrets
- backup/restore workflow
- registry redesign for all workloads
- changing the app-of-apps structure beyond what is required for `sample-api`

## Proposed architecture

The repository keeps two image paths alive at the same time:

- **Release path:** Docker Hub is the default release registry for CI-produced images.
- **Lab path:** the local overlay can still target the local registry style used in the template.

This split keeps the learning value of the current repo:

- the base manifest still shows a simple local placeholder image name,
- the overlay shows how Kustomize rewrites image references,
- CI shows how to push a real release image and then update GitOps.

## Components

### 1. Sample app

The Flask app remains small and stable. It only needs to keep the health endpoint and metrics endpoint that support the platform exercises.

### 2. Build helper

`bin/build-local-sample-api.sh` acts as the manual build/push helper for local or lab use. It should continue to default to a sensible release-friendly image name while still allowing overrides through `IMAGE`.

### 3. CI pipeline

The CI workflow is the main release path.

It should:

- run `python -m pytest` for the sample app,
- build the container image,
- scan it with Trivy,
- log in to Docker Hub,
- push the image,
- update the GitOps overlay tag with Kustomize.

The update command should continue to target the placeholder base image name so the pipeline remains easy to read:

```bash
kustomize edit set image "localhost:5000/sample-api=$IMAGE_NAME:$IMAGE_TAG"
```

### 4. GitOps manifests

The base deployment keeps the placeholder image name and non-root hardening. The local overlay rewrites the image reference and keeps the mutable-tag pull policy patch where needed.

### 5. ArgoCD application

`gitops/clusters/local/sample-api.yaml` stays the application entrypoint for the sample app. The design assumes ArgoCD continues to watch the local overlay path and reconcile the updated image tag.

## Data flow

1. A code change is pushed.
2. CI starts for `sample-api`.
3. The app test suite runs first.
4. The image is built from the Dockerfile.
5. Trivy scans the image.
6. The image is pushed to Docker Hub.
7. The CI job updates the overlay image reference in Git.
8. ArgoCD notices the Git change and syncs the application.
9. Kubernetes pulls the new image and rolls out the deployment.

## Error handling and recovery

### Test failure

If `python -m pytest` fails, the pipeline stops before build and push. This prevents broken application code from being published.

### Scan failure

If Trivy reports a blocking issue, the pipeline stops before the image is pushed or released through GitOps.

### Push failure

If Docker Hub authentication or push fails, the GitOps manifest should not be updated. This keeps the Git state aligned with the registry state.

### Sync failure

If ArgoCD cannot sync the updated manifest, the rollout stays pinned to the previous known-good image tag. Recovery is to fix the sync issue or revert the Git commit that updated the image tag.

### Rollback

Rollback is Git-first: revert the image-tag update commit and let ArgoCD reconcile the older manifest again.

## Verification strategy

The repo-level verification should stay lightweight and deterministic:

```bash
python -m pytest tests/test_sample_api_image_registry.py tests/test_platform_app_of_apps_ordering.py
```

If the app source changes materially, run the sample app test suite too:

```bash
cd apps/sample-api && python -m pytest
```

Manual cluster verification, when needed, should check that ArgoCD has the application, the rollout completes, and the `/healthz` endpoint responds.

## Success criteria

Phase 7 is complete when all of the following are true:

- `sample-api` has a clear CI path from test to push.
- The CI workflow uses Docker Hub as the release registry.
- The local overlay still supports the lab image path.
- The GitOps manifest update step is present and understandable.
- The repo tests assert the important registry and ordering behavior.
- The roadmap documents phase 7 as a finished learning step.

## Notes for implementation

- Keep changes small and aligned with the current repository style.
- Avoid introducing extra abstraction unless it directly supports the phase 7 release flow.
- Preserve the distinction between base image name, release image name, and local-lab image rewrite.
