#!/usr/bin/env bash
# deploy.sh — Auto-commit, push to GitHub, rebuild and redeploy the MCP container.
# Triggered by the systemd file watcher or run manually.

set -euo pipefail

REPO_DIR="/home/ubuntu/MCP-Marketing"
IMAGE_NAME="marketing-mcp"
CONTAINER_NAME="marketing-mcp"
ENV_FILE="${REPO_DIR}/.env"

cd "$REPO_DIR"

# ── 1. Git: commit and push any changes ──
if [[ -n "$(git status --porcelain)" ]]; then
    git add -A
    # Use the list of changed files as the commit message
    CHANGED=$(git diff --cached --name-only | head -10 | tr '\n' ', ' | sed 's/,$//')
    git commit -m "Auto-sync: ${CHANGED}" \
        -m "Pushed automatically from server via deploy.sh"
    git push origin main
    echo "[deploy] Pushed changes to GitHub."
else
    echo "[deploy] No changes to push."
fi

# ── 2. Docker: rebuild and redeploy ──
TIMESTAMP=$(date +%s)
TAG="v${TIMESTAMP}"

docker build -t "${IMAGE_NAME}:${TAG}" .

# Stop old container (ignore if not running)
docker stop "$CONTAINER_NAME" 2>/dev/null || true
docker rm "$CONTAINER_NAME" 2>/dev/null || true

docker run -d \
    --name "$CONTAINER_NAME" \
    --network coolify \
    --restart unless-stopped \
    --env-file "$ENV_FILE" \
    -l "traefik.enable=true" \
    -l "traefik.http.routers.marketingmcp-http.entryPoints=http" \
    -l "traefik.http.routers.marketingmcp-http.rule=Host(\`marketingmcp.statika.net\`)" \
    -l "traefik.http.routers.marketingmcp-http.middlewares=redirect-to-https" \
    -l "traefik.http.middlewares.redirect-to-https.redirectscheme.scheme=https" \
    -l "traefik.http.routers.marketingmcp-https.entryPoints=https" \
    -l "traefik.http.routers.marketingmcp-https.rule=Host(\`marketingmcp.statika.net\`)" \
    -l "traefik.http.routers.marketingmcp-https.tls=true" \
    -l "traefik.http.routers.marketingmcp-https.tls.certresolver=letsencrypt" \
    -l "traefik.http.services.marketingmcp.loadbalancer.server.port=8000" \
    "${IMAGE_NAME}:${TAG}"

echo "[deploy] Container redeployed with image ${IMAGE_NAME}:${TAG}"

# ── 3. Cleanup old images (keep last 3) ──
docker images "$IMAGE_NAME" --format '{{.Repository}}:{{.Tag}}' \
    | sort -r | tail -n +4 | xargs -r docker rmi 2>/dev/null || true

echo "[deploy] Done."
