---
name: kubernetes-beginner-architecture-report-design
description: Design for updating the architecture report so Kubernetes beginners can understand the Rancher/K3s/ArgoCD/GitOps/clipproxy platform
metadata:
  type: project
---

# Kubernetes Beginner Architecture Report Design

## Goal

Update `docs/architecture.md` so a reader new to Kubernetes can understand this repository's local Rancher/K3s platform, ArgoCD GitOps flow, and the new `clipproxy` application architecture.

## Scope

### In scope

- Rewrite or expand `docs/architecture.md` as a beginner-friendly architecture report.
- Explain the roles of Rancher, K3s/Kubernetes, ArgoCD, GitOps, Ingress, and application manifests.
- Explain how `sample-api` and `clipproxy` are deployed.
- Add a `clipproxy` architecture section covering API, manager, ConfigMap, Secret, PVCs, Service, and Ingress.
- Include runtime request flow for `http://clipproxy.local`.
- Include a troubleshooting map for common ArgoCD/Kubernetes states such as `NotFound`, `Synced`, `Degraded`, `CrashLoopBackOff`, `Pending`, and `too many open files`.
- Add lightweight tests that pin key educational content in `docs/architecture.md`.

### Out of scope

- Changing Kubernetes manifests.
- Changing application code.
- Running deployment commands.
- Printing or inspecting secret values.
- Adding a full Kubernetes textbook.

## Proposed structure

`docs/architecture.md` should become a report with these sections:

1. Executive summary.
2. Beginner mental model.
3. Repository map.
4. Cluster and GitOps architecture.
5. GitOps deployment flow.
6. Runtime request flow.
7. Kubernetes object glossary using this repo's concrete examples.
8. Platform components.
9. Application architecture for `sample-api` and `clipproxy`.
10. Troubleshooting map.
11. Read-only command cheat sheet.

## Success criteria

- A beginner can explain why Git is the source of truth and ArgoCD syncs the cluster.
- A beginner can trace a request from `clipproxy.local` through Ingress, Service, and Pod.
- A beginner can identify where ConfigMap, Secret, and PVC fit in `clipproxy`.
- A beginner can distinguish GitOps issues from runtime Kubernetes issues.
- Tests pass with `python3 -m pytest tests/test_architecture_report.py -q` and the root test suite remains green.
