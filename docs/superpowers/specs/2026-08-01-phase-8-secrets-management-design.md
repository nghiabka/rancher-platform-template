---
name: phase-8-secrets-management-design
description: Design for phase 8 secrets management with Sealed Secrets controller and sample-api env var demo
metadata:
  type: project
---

# Phase 8: Secrets Management Design

## Goal

Phase 8 adds a GitOps-friendly secret management flow using Sealed Secrets and a small `sample-api` demo that proves a secret can be injected into a pod without committing plain text secret data.

## Scope

### In scope

- [gitops/platform/kustomization.yaml](../../../gitops/platform/kustomization.yaml)
- [gitops/platform/50-secrets/kustomization.yaml](../../../gitops/platform/50-secrets/kustomization.yaml)
- [gitops/platform/50-secrets/sealed-secrets.yaml](../../../gitops/platform/50-secrets/sealed-secrets.yaml)
- [gitops/apps/sample-api/base/deployment.yaml](../../../gitops/apps/sample-api/base/deployment.yaml)
- [gitops/apps/sample-api/overlays/local/kustomization.yaml](../../../gitops/apps/sample-api/overlays/local/kustomization.yaml)
- [gitops/apps/sample-api/overlays/local/sealed-secret.example.yaml](../../../gitops/apps/sample-api/overlays/local/sealed-secret.example.yaml)
- [docs/deployment-roadmap.md](../../../docs/deployment-roadmap.md)
- [docs/tutorial-phase-0-3.md](../../../docs/tutorial-phase-0-3.md)
- tests covering the above manifests and docs

### Out of scope

- Storing plain text secrets in Git
- Adding new app API responses that print secret values
- Introducing Vault or External Secrets
- Changing unrelated platform phases

## Proposed architecture

The platform parent will manage the Sealed Secrets controller through GitOps, just like the other platform capabilities. The sample app will use a pod environment variable sourced from a secret so the demo stays small and easy to reason about.

The repository will also include a `SealedSecret` template/example file for the lab. That file is intentionally not part of the default overlay resources, so the template remains safe to commit and does not pretend to contain a real cluster-specific encrypted payload.

## Components

### 1. Platform controller

`gitops/platform/kustomization.yaml` will include `50-secrets`, which keeps the Sealed Secrets controller under the platform parent.

`gitops/platform/50-secrets/sealed-secrets.yaml` remains the ArgoCD Application for the Bitnami Sealed Secrets Helm chart.

### 2. Sample app secret demo

`gitops/apps/sample-api/base/deployment.yaml` or the local overlay will define an env var sourced from a secret key, for example `DEMO_SECRET_VALUE` from `sample-api-demo-secret` / `DEMO_VALUE`.

`gitops/apps/sample-api/overlays/local/sealed-secret.example.yaml` will serve as a template/example only. It will not be included in `resources:` by default. The docs will tell the user to generate a real sealed secret outside the repo or replace the example with a cluster-specific file after using `kubeseal`.

### 3. Docs

The roadmap will mark phase 8 as complete once the controller and demo are wired in.

The tutorial will explain the intended lab flow:

1. create a temporary Kubernetes Secret outside the repo,
2. seal it with `kubeseal`,
3. save the sealed manifest into the overlay or a nearby example path,
4. let ArgoCD sync the result,
5. verify the pod receives the env var without exposing the secret value.

## Data flow

1. ArgoCD syncs `gitops/platform/kustomization.yaml`.
2. The platform parent includes `50-secrets`, so the Sealed Secrets controller is installed in the `sealed-secrets` namespace.
3. The user creates a temporary Secret outside the repo.
4. The user seals it with `kubeseal`.
5. The user commits or stages the resulting `SealedSecret` manifest as a lab artifact or example, not as plain text secret data.
6. ArgoCD applies the manifest.
7. The controller decrypts the `SealedSecret` into a Kubernetes Secret.
8. `sample-api` receives the secret-backed env var in the pod.
9. The app remains silent about the actual secret value.

## Error handling and recovery

### Controller not installed

If the controller is not yet synced, the example `SealedSecret` file remains inert because it is not part of the default overlay resources.

### Wrong certificate or cluster mismatch

If a user generates a `SealedSecret` with the wrong public cert, ArgoCD/app sync will not produce the expected Secret. The tutorial should treat that as the expected failure mode and instruct the user to rerun `kubeseal` against the correct cluster.

### Secret key mismatch

If the secret name or key does not match the deployment reference, the pod may start without the expected env var. The design keeps the demo optional and easy to recover from by updating the secret name/key pair in both files.

### Secret leakage

No app endpoint, log line, or doc should print the secret value. Verification is structural: inspect manifests, pod env wiring, or Kubernetes objects, not the secret content itself.

## Verification strategy

The repo should use small string-based tests that assert the intended structure:

- `gitops/platform/kustomization.yaml` includes `50-secrets`
- `gitops/platform/50-secrets/sealed-secrets.yaml` still points to the Sealed Secrets Helm chart and `sealed-secrets` namespace
- `gitops/apps/sample-api/overlays/local/sealed-secret.example.yaml` exists and uses `kind: SealedSecret`
- the example file is not included in the default overlay `resources:`
- the sample app deployment includes an env var sourced from the intended secret name/key
- the roadmap and tutorial text describe the sealed secret workflow correctly

## Success criteria

Phase 8 is complete when:

- Sealed Secrets is managed through the platform parent
- the sample app has a secret-backed env var demo
- the repository contains a safe template/example flow instead of plain text secret data
- docs explain how to generate the real sealed secret with `kubeseal`
- tests assert the intended manifest structure and docs wording
