# Phase 8 Secrets Management Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add Sealed Secrets–based secret management to the platform and show a safe sample-api env var demo without committing plain text secret data.

**Architecture:** Manage the Sealed Secrets controller through the platform parent, keep the sample app demo small by wiring one pod env var from a Secret, and provide a non-default `SealedSecret` template/example that teaches the workflow without pretending to contain a real encrypted payload. Documentation and tests stay string-based so the repo remains easy to verify without cluster access.

**Tech Stack:** ArgoCD, Helm chart for Bitnami Sealed Secrets, Kustomize, Kubernetes Secret/SealedSecret manifests, Flask sample app, Pytest, YAML, kubeseal.

## Global Constraints

- Sealed Secrets controller chạy trong cluster.
- Biết tạo Kubernetes Secret tạm thời.
- Biết seal secret thành `SealedSecret` để commit vào Git.
- Không commit plain text secret.
- Avoid introducing Vault or External Secrets.
- No app endpoint, log line, or doc should print the secret value.
- The `SealedSecret` example file is for the lab only and is not included in default overlay resources.

---

## File Structure

- `gitops/platform/kustomization.yaml` — platform parent resources; include `50-secrets` here.
- `gitops/platform/50-secrets/kustomization.yaml` — wraps the Sealed Secrets Application resource.
- `gitops/platform/50-secrets/sealed-secrets.yaml` — ArgoCD Application for the Bitnami Sealed Secrets chart.
- `gitops/apps/sample-api/base/deployment.yaml` — sample-api Deployment; add env var sourcing from a Secret key.
- `gitops/apps/sample-api/overlays/local/kustomization.yaml` — overlay resources and comments for the secret demo; do not include the example file by default.
- `gitops/apps/sample-api/overlays/local/sealed-secret.example.yaml` — new template/example SealedSecret file for lab use.
- `docs/deployment-roadmap.md` — mark phase 8 complete and explain the secret workflow.
- `docs/tutorial-phase-0-3.md` — update the phase 8 tutorial section with kubeseal workflow and safety notes.
- `tests/test_platform_app_of_apps_ordering.py` — update platform parent assertions for `50-secrets`.
- `tests/test_phase8_secrets_management.py` — new coverage for SealedSecret template/example, env var wiring, and documentation text.
- `tests/test_deployment_roadmap.py` — add/adjust coverage that phase 8 is marked complete and references Sealed Secrets and kubeseal.

## Task 1: Include Sealed Secrets in the platform parent

**Files:**
- Modify: `tests/test_platform_app_of_apps_ordering.py:37-44`
- Modify: `gitops/platform/kustomization.yaml:1-8`

**Interfaces:**
- Consumes: existing `50-secrets` directory and Sealed Secrets Application manifest
- Produces: platform parent that includes `50-secrets` and tests that expect it

- [ ] **Step 1: Write the failing platform-parent test update**

Replace the current exclusion assertion with an inclusion assertion:

```python
def test_platform_parent_only_includes_completed_phase_components():
    platform = read_repo_file("gitops/platform/kustomization.yaml")

    assert "40-logging" in platform
    assert "50-secrets" in platform
    assert "60-backup" not in platform
    assert "70-registry" not in platform
    assert "80-policy" not in platform
```

- [ ] **Step 2: Run the targeted ordering test to see it fail**

Run:

```bash
python3 -m pytest tests/test_platform_app_of_apps_ordering.py -q
```

Expected: fail until `50-secrets` is added to the platform parent.

- [ ] **Step 3: Include `50-secrets` in the platform parent**

Update the platform kustomization resources to add the secrets phase in order:

```yaml
resources:
  - 00-namespaces
  - 10-ingress
  - 20-cert-manager
  - 30-observability
  - 40-logging
  - 50-secrets
  - ../bootstrap/argocd
```

- [ ] **Step 4: Re-run the ordering test**

Run:

```bash
python3 -m pytest tests/test_platform_app_of_apps_ordering.py -q
```

Expected: pass.

- [ ] **Step 5: Commit the platform-parent update**

Use a focused commit message such as:

```bash
git add gitops/platform/kustomization.yaml tests/test_platform_app_of_apps_ordering.py
git commit -m "fix(secrets): include sealed secrets in platform parent"
```

## Task 2: Add the sample-api SealedSecret template/example

**Files:**
- Create: `gitops/apps/sample-api/overlays/local/sealed-secret.example.yaml`
- Modify: `gitops/apps/sample-api/overlays/local/kustomization.yaml:1-12`
- Modify: `tests/test_phase8_secrets_management.py`

**Interfaces:**
- Consumes: the secret name/key pair used by the Deployment (`sample-api-demo-secret` / `DEMO_VALUE`)
- Produces: a safe `SealedSecret` example file that is not part of default overlay resources

- [ ] **Step 1: Write the failing template/example test**

Create a new test file that pins the safe template shape:

```python
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
```

- [ ] **Step 2: Run the new test to see it fail**

Run:

```bash
python3 -m pytest tests/test_phase8_secrets_management.py -q
```

Expected: fail until the example file exists.

- [ ] **Step 3: Create the example SealedSecret file**

Add a safe template/example manifest that is clearly not a real encrypted payload:

```yaml
apiVersion: bitnami.com/v1alpha1
kind: SealedSecret
metadata:
  name: sample-api-demo-secret
  namespace: sample-api
spec:
  encryptedData:
    DEMO_VALUE: PLACEHOLDER_GENERATED_BY_KUBESEAL
  template:
    metadata:
      name: sample-api-demo-secret
      namespace: sample-api
    type: Opaque
```

- [ ] **Step 4: Keep the example file out of default overlay resources**

Ensure `gitops/apps/sample-api/overlays/local/kustomization.yaml` does not include the example file in `resources:`. If you want to leave a lab hint, add a comment only.

- [ ] **Step 5: Re-run the template/example test**

Run:

```bash
python3 -m pytest tests/test_phase8_secrets_management.py -q
```

Expected: pass.

- [ ] **Step 6: Commit the template/example file**

Use a focused commit message such as:

```bash
git add gitops/apps/sample-api/overlays/local/sealed-secret.example.yaml gitops/apps/sample-api/overlays/local/kustomization.yaml tests/test_phase8_secrets_management.py
git commit -m "feat(secrets): add sealed secret template example"
```

## Task 3: Wire the sample-api Deployment to a secret-backed env var

**Files:**
- Modify: `gitops/apps/sample-api/base/deployment.yaml:1-50`
- Modify: `tests/test_phase8_secrets_management.py`

**Interfaces:**
- Consumes: secret name `sample-api-demo-secret` and key `DEMO_VALUE`
- Produces: pod env var `DEMO_SECRET_VALUE` sourced from that secret/key pair

- [ ] **Step 1: Write the failing env var wiring test**

Extend the phase 8 test file with a manifest assertion:

```python
def test_sample_api_deployment_sources_secret_env_var():
    deployment = read_repo_file("gitops/apps/sample-api/base/deployment.yaml")

    assert "name: DEMO_SECRET_VALUE" in deployment
    assert "secretKeyRef:" in deployment
    assert "name: sample-api-demo-secret" in deployment
    assert "key: DEMO_VALUE" in deployment
```

- [ ] **Step 2: Run the env var test to see it fail**

Run:

```bash
python3 -m pytest tests/test_phase8_secrets_management.py -q
```

Expected: fail until the Deployment references the Secret.

- [ ] **Step 3: Add the env var reference to the Deployment**

Add a minimal env block in the container spec:

```yaml
          env:
            - name: DEMO_SECRET_VALUE
              valueFrom:
                secretKeyRef:
                  name: sample-api-demo-secret
                  key: DEMO_VALUE
```

- [ ] **Step 4: Re-run the env var test**

Run:

```bash
python3 -m pytest tests/test_phase8_secrets_management.py -q
```

Expected: pass.

- [ ] **Step 5: Commit the Deployment wiring**

Use a focused commit message such as:

```bash
git add gitops/apps/sample-api/base/deployment.yaml tests/test_phase8_secrets_management.py
git commit -m "fix(secrets): wire sample-api env var from secret"
```

## Task 4: Update docs and roadmap for phase 8

**Files:**
- Modify: `docs/deployment-roadmap.md:164-181`
- Modify: `docs/tutorial-phase-0-3.md:1323-1407`
- Modify: `tests/test_deployment_roadmap.py`
- Modify: `tests/test_phase8_secrets_management.py`

**Interfaces:**
- Consumes: the completed Sealed Secrets controller + env var demo flow
- Produces: docs that clearly explain kubeseal workflow and a roadmap that marks phase 8 done

- [ ] **Step 1: Add roadmap and tutorial assertions**

Extend the tests with doc-focused checks:

```python
def test_phase_8_roadmap_mentions_sealed_secrets_and_kubeseal():
    roadmap = read_repo_file("docs/deployment-roadmap.md")

    assert "## Phase 8: Secrets Management" in roadmap
    assert "Khong commit secret plain text vao Git." in roadmap
    assert "- [x] Cai Sealed Secrets." in roadmap
    assert "- [x] Cai `kubeseal` tren may local." in roadmap
    assert "- [x] Seal secret thanh `SealedSecret`." in roadmap
    assert "- [x] Commit `SealedSecret` vao GitOps repo." in roadmap
    assert "Secrets duoc quan ly theo GitOps ma khong lo plain text leak." in roadmap


def test_tutorial_phase_8_explains_kubeseal_workflow():
    tutorial = read_repo_file("docs/tutorial-phase-0-3.md")

    assert "## Phase 8: Secrets Management" in tutorial
    assert "kubectl apply -n argocd -f gitops/platform/50-secrets/sealed-secrets.yaml" in tutorial
    assert "kubeseal --version" in tutorial
    assert "sample-api-demo-secret" in tutorial
    assert "sealed-secret.example.yaml" in tutorial
```

- [ ] **Step 2: Run the doc tests once to see the current gaps**

Run:

```bash
python3 -m pytest tests/test_deployment_roadmap.py tests/test_phase8_secrets_management.py -q
```

Expected: fail until the docs and manifest files match the assertions.

- [ ] **Step 3: Update the roadmap and tutorial text**

Make the phase 8 roadmap checklist complete and keep the wording aligned with the spec:

```markdown
## Phase 8: Secrets Management

Muc tieu:

- Khong commit secret plain text vao Git.

Checklist:

- [x] Cai Sealed Secrets.
- [x] Cai `kubeseal` tren may local.
- [x] Tao Kubernetes Secret tam thoi.
- [x] Seal secret thanh `SealedSecret`.
- [x] Commit `SealedSecret` vao GitOps repo.
- [x] Verify app doc duoc secret sau khi ArgoCD sync.

Ket qua mong doi:

- Secrets duoc quan ly theo GitOps ma khong lo plain text leak.
```

Update the tutorial so it explains the actual lab flow:
- apply `gitops/platform/50-secrets/sealed-secrets.yaml`
- verify `sealed-secrets` controller is running
- run `kubeseal --version`
- create a temp Secret outside the repo
- seal it to a manifest for the overlay/example path
- sync ArgoCD
- verify the pod receives the env var without exposing secret value

- [ ] **Step 4: Re-run the doc tests**

Run:

```bash
python3 -m pytest tests/test_deployment_roadmap.py tests/test_phase8_secrets_management.py -q
```

Expected: pass.

- [ ] **Step 5: Commit the docs update**

Use a focused commit message such as:

```bash
git add docs/deployment-roadmap.md docs/tutorial-phase-0-3.md tests/test_deployment_roadmap.py tests/test_phase8_secrets_management.py
git commit -m "docs(secrets): complete phase 8 guidance"
```

## Final verification

After all tasks are complete, run the focused regression set:

```bash
python3 -m pytest tests/test_platform_app_of_apps_ordering.py tests/test_phase8_secrets_management.py tests/test_deployment_roadmap.py -q
```

Then review `git status --short` and confirm only the intended phase 8 files changed.
