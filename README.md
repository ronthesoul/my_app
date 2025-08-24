# my_app

A tiny Python web service (listens on **port 8000**) containerized with Docker and deployed to Kubernetes.     CI builds and pushes Docker images via **GitHub Actions**; CD is handled by **Argo CD** using a GitOps flow.     Works great on **Minikube** for local testing.

---

## Quick start

```bash
# 1) Run locally with Docker
docker build -t m4gapower/my_app:latest .
docker run --rm -p 8000:8000 m4gapower/my_app:latest
curl -i http://localhost:8000/

# 2) Deploy to Minikube
minikube start

# Apply Kubernetes manifests (adjust the folder if needed)
# Common paths in this repo: Deployment/, config/k8s/
kubectl apply -f Deployment/my-app-deployment
kubectl apply -f Deployment/my-app-service

kubectl get svc,pods
```

> The app inside the container must bind to **0.0.0.0:8000** (not 127.0.0.1) so Kubernetes can route traffic to it.

---

## Accessing the app on Minikube — `minikube service <service> --url`

If Ingress is not set up yet, if `kubectl port-forward` is flaky, or if NodePorts are not reachable from your host, use Minikube’s built‑in service access helper:

```bash
# Prints a reachable URL for the Service (ClusterIP/NodePort) and opens a local proxy/tunnel if needed
minikube service my-app --url -n default

# You can pipe the URL straight into curl:
curl -i "$(minikube service my-app --url -n default)"
```

**What it does:**  
- For **ClusterIP**/**NodePort** Services, it exposes a local, reachable URL (e.g., `http://127.0.0.1:<port>` or `http://<minikube-ip>:<nodePort>`).  
- For **LoadBalancer** Services, run `minikube tunnel` to allocate an external IP locally (may require admin privileges).

**Why this “fixes” access issues:**  
It bypasses missing/broken Ingress and the occasional `port-forward` proxy issues by giving you a reliable, direct URL to the Service—without changing anything inside the cluster.

---

## GitHub Actions — what the workflow does

The workflow under `.github/workflows/` typically:
1. **Triggers** on pushes (e.g., to `main`) and/or **tags** (e.g., `v1.7.0`).  
2. **Checks out** the repo.  
3. **Builds** the Docker image for `m4gapower/my_app`.  
4. **Tags & pushes** to Docker Hub using repo‑encrypted secrets (e.g., `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`).  
5. (Optional) Updates the **image tag** in k8s manifests (e.g., via `yq`/`sed`) and commits it back so Argo CD can pick up the change.

> Notes
> - CI produces versioned tags (like `1.6.0`, `1.7.0`) and often `latest`.  
> - If your cluster shows `1.6.0` while CI pushed `1.7.0`, the **manifests still point to 1.6.0**. Update the tag in the Deployment YAML (or automate it in CI).

---

## Argo CD — how it works here

**Concept:** Argo CD continuously syncs the cluster to the **desired state** defined in this repo (GitOps).  
- An Argo CD **Application** points to this repository (e.g., `config/k8s/` or `Deployment/`) and a target namespace.  
- With **Auto‑Sync** enabled, changes merged to Git are automatically applied to the cluster.  
- With **Prune**/**Self‑Heal**, Argo CD removes resources deleted from Git and reverts drift from manual `kubectl` changes.

**Typical flow:**  
1. You push a commit (or CI updates manifests) that bumps the image tag to `m4gapower/my_app:1.7.0`.  
2. Argo CD detects the Git change and marks the app **OutOfSync**.  
3. Auto‑Sync applies the new manifests and your pods roll out with the new image.  
4. Health checks in Argo CD turn **Healthy** once the Deployment is ready.

**Important:** Argo CD **does not build images**. It deploys whatever **tag** your manifests specify. To deploy a new version, either:  
- Update the tag in Git (manual or via CI), or  
- Use a companion like **argocd-image-updater** to bump tags automatically.

---

## Troubleshooting

- **App up but not reachable:** Use `minikube service my-app --url -n default`.  
- **Readiness/Liveness probe failing:** Make sure your web app listens on `0.0.0.0:8000`, and the `Service` `targetPort` matches the container’s listening port.  
- **New image not deployed:** Check the Deployment image tag in Git matches the tag you pushed to Docker Hub.  
- **Argo CD shows Synced but old image:** The manifests still point to an older tag; bump the tag and let Argo CD sync.  
- **Debug:** `kubectl describe pod <pod>`, `kubectl logs -f deploy/my-app`.

---

## Repository structure (overview)

```text
.
├─ .github/workflows/      # CI (build & push Docker image, optional manifest bump)
├─ argoCD/                 # Argo CD app/config (path may vary)
├─ Deployment/             # Kubernetes manifests (Deployment, Service, etc.)
├─ config/                 # Alternative k8s path (e.g., config/k8s/)
├─ src/my_app/             # Application source code
├─ lib/                    # Libraries/helpers (if used)
├─ Dockerfile
├─ requirements.txt
├─ index.html              # Static page (if served)
└─ README.md
```

---

## Commands you’ll use often

```bash
# Build & run locally
docker build -t m4gapower/my_app:latest .
docker run --rm -p 8000:8000 m4gapower/my_app:latest

# Apply/rollout
kubectl apply -f Deployment/
kubectl rollout status deploy/my-app
kubectl get svc my-app

# Fast access on Minikube
minikube service my-app --url -n default

# Force Argo to re-fetch and re-diff Git (clears cache)
kubectl -n argocd annotate app my-app argocd.argoproj.io/refresh=hard --overwrite

# Inspect what Argo CD deployed (replace with your app name/namespace)
kubectl -n argocd get app my-app -o jsonpath='{.status.sync.status}{"\t"}{.status.health.status}{"\t"}{.status.summary.images}{"\t"}{.status.sync.revision}{"\n"}'
```

---

## Links

- Docker Hub: https://hub.docker.com/repository/docker/m4gapower/my_app/general
- Argo CD docs: https://argo-cd.readthedocs.io/
- Minikube Service docs: https://minikube.sigs.k8s.io/docs/handbook/accessing/
```

