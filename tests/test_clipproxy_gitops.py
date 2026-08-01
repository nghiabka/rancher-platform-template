from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_repo_file(relative_path: str) -> str:
    return (ROOT / relative_path).read_text()


def test_clipproxy_source_directory_replaces_cliprouter():
    assert (ROOT / "clipproxy").is_dir()
    assert not (ROOT / "cliprouter").exists()
    assert (ROOT / "clipproxy/config.yaml").is_file()
    assert (ROOT / "clipproxy/docker-compose.yml").is_file()

    compose = read_repo_file("clipproxy/docker-compose.yml")
    assert "clipproxy-api:" in compose
    assert "container_name: clipproxy-api" in compose
    assert "clipproxy-manager:" in compose
    assert "container_name: clipproxy-manager" in compose
    assert "CPA_UPSTREAM_URL: \"http://clipproxy-api:8317\"" in compose


def test_clipproxy_namespace_is_declared():
    namespaces = read_repo_file("gitops/platform/00-namespaces/namespaces.yaml")

    assert "name: clipproxy" in namespaces


def test_clipproxy_argocd_application_is_wired_into_local_cluster():
    app = read_repo_file("gitops/clusters/local/clipproxy.yaml")
    local = read_repo_file("gitops/clusters/local/kustomization.yaml")

    assert "kind: Application" in app
    assert "name: clipproxy-local" in app
    assert "namespace: argocd" in app
    assert "repoURL: https://github.com/nghiabka/rancher-platform-template.git" in app
    assert "targetRevision: main" in app
    assert "path: gitops/apps/clipproxy/overlays/local" in app
    assert "namespace: clipproxy" in app
    assert "prune: true" in app
    assert "selfHeal: true" in app
    assert "CreateNamespace=true" in app
    assert "- clipproxy.yaml" in local


def test_clipproxy_api_base_manifests_are_defined():
    kustomization = read_repo_file("gitops/apps/clipproxy/base/kustomization.yaml")
    configmap = read_repo_file("gitops/apps/clipproxy/base/configmap.yaml")
    pvc = read_repo_file("gitops/apps/clipproxy/base/pvc-api.yaml")
    deployment = read_repo_file("gitops/apps/clipproxy/base/deployment-api.yaml")
    service = read_repo_file("gitops/apps/clipproxy/base/service-api.yaml")
    overlay = read_repo_file("gitops/apps/clipproxy/overlays/local/kustomization.yaml")

    assert "- configmap.yaml" in kustomization
    assert "- pvc-api.yaml" in kustomization
    assert "- deployment-api.yaml" in kustomization
    assert "- service-api.yaml" in kustomization
    assert "app.kubernetes.io/name: clipproxy" in kustomization
    assert "app.kubernetes.io/part-of: rancher-platform-template" in kustomization

    assert "name: clipproxy-config" in configmap
    assert "config.yaml: |" in configmap
    assert "port: 8317" in configmap
    assert "allow-remote: true" in configmap

    assert "name: clipproxy-api-data" in pvc
    assert "ReadWriteOnce" in pvc
    assert "storage: 1Gi" in pvc

    assert "name: clipproxy-api" in deployment
    assert "image: eceasy/cli-proxy-api:latest" in deployment
    assert "containerPort: 8317" in deployment
    assert "mountPath: /CLIProxyAPI/config.yaml" in deployment
    assert "subPath: config.yaml" in deployment
    assert "mountPath: /root/.cli-proxy-api" in deployment
    assert "claimName: clipproxy-api-data" in deployment

    assert "name: clipproxy-api" in service
    assert "type: ClusterIP" in service
    assert "port: 8317" in service
    assert "targetPort: http" in service

    assert "- ../../base" in overlay
    assert "namespace: clipproxy" in overlay


def test_clipproxy_manager_secret_pvc_service_and_ingress_are_defined():
    kustomization = read_repo_file("gitops/apps/clipproxy/base/kustomization.yaml")
    pvc = read_repo_file("gitops/apps/clipproxy/base/pvc-manager.yaml")
    deployment = read_repo_file("gitops/apps/clipproxy/base/deployment-manager.yaml")
    service = read_repo_file("gitops/apps/clipproxy/base/service-manager.yaml")
    ingress = read_repo_file("gitops/apps/clipproxy/base/ingress.yaml")
    example_secret = read_repo_file("gitops/apps/clipproxy/overlays/local/secret.example.yaml")
    overlay = read_repo_file("gitops/apps/clipproxy/overlays/local/kustomization.yaml")

    assert "- pvc-manager.yaml" in kustomization
    assert "- deployment-manager.yaml" in kustomization
    assert "- service-manager.yaml" in kustomization
    assert "- ingress.yaml" in kustomization

    assert "name: clipproxy-manager-data" in pvc
    assert "ReadWriteOnce" in pvc
    assert "storage: 1Gi" in pvc

    assert "name: clipproxy-manager" in deployment
    assert "image: seakee/cpa-manager-plus:latest" in deployment
    assert "containerPort: 18317" in deployment
    assert "name: CPA_UPSTREAM_URL" in deployment
    assert "value: http://clipproxy-api:8317" in deployment
    assert "name: CPA_MANAGER_ADMIN_KEY" in deployment
    assert "name: CPA_MANAGEMENT_KEY" in deployment
    assert "secretKeyRef:" in deployment
    assert "name: clipproxy-secret" in deployment
    assert "key: CPA_MANAGER_ADMIN_KEY" in deployment
    assert "key: CPA_MANAGEMENT_KEY" in deployment
    assert "mountPath: /data" in deployment
    assert "claimName: clipproxy-manager-data" in deployment
    assert "CPA_MANAGER_ADMIN_KEY_TEST" not in deployment
    assert "CPA_MANAGEMENT_KEY_TEST" not in deployment

    assert "name: clipproxy-manager" in service
    assert "type: ClusterIP" in service
    assert "port: 18317" in service
    assert "targetPort: http" in service

    assert "kind: Ingress" in ingress
    assert "name: clipproxy" in ingress
    assert "ingressClassName: nginx" in ingress
    assert "host: clipproxy.local" in ingress
    assert "name: clipproxy-manager" in ingress
    assert "name: http" in ingress

    assert "kind: Secret" in example_secret
    assert "name: clipproxy-secret" in example_secret
    assert "namespace: clipproxy" in example_secret
    assert "CPA_MANAGER_ADMIN_KEY: example-admin-key-change-me" in example_secret
    assert "CPA_MANAGEMENT_KEY: example-management-key-change-me" in example_secret
    assert "- secret.example.yaml" not in overlay


def test_clipproxy_rancher_deploy_guide_documents_gitops_flow():
    guide = read_repo_file("docs/clipproxy-rancher-deploy.md")

    assert "# Deploy Clipproxy on Rancher/Kubernetes" in guide
    assert "clipproxy-local" in guide
    assert "gitops/apps/clipproxy/overlays/local" in guide
    assert "clipproxy-secret" in guide
    assert "kubectl -n clipproxy create secret generic clipproxy-secret" in guide
    assert "kubectl -n argocd get application clipproxy-local" in guide
    assert "kubectl -n clipproxy get pods,svc,ingress,pvc" in guide
    assert "kubectl -n clipproxy rollout status deploy/clipproxy-api" in guide
    assert "kubectl -n clipproxy rollout status deploy/clipproxy-manager" in guide
    assert "kubectl -n clipproxy port-forward svc/clipproxy-manager 18317:18317" in guide
    assert "http://clipproxy.local" in guide
    assert "Docker Compose is kept only as a local reference" in guide
