#!/usr/bin/env bash
# deploy-portal.sh — Build and deploy the Next.js portal container.
# Routes: marketingmcp.statika.net/* (catch-all, lower priority than /mcp)

set -euo pipefail

REPO_DIR="/home/ubuntu/MCP-Marketing"
IMAGE_NAME="marketing-mcp-portal"
CONTAINER_NAME="marketing-mcp-portal"
ENV_FILE="${REPO_DIR}/portal/.env"

cd "$REPO_DIR"

# ── 1. Git: pull latest from GitHub ──
echo "[deploy-portal] Pulling latest from GitHub..."
git fetch origin main
git reset --hard origin/main
echo "[deploy-portal] Synced to $(git rev-parse --short HEAD)"

# ── 2. Docker: rebuild and redeploy ──
TIMESTAMP=$(date +%s)
TAG="v${TIMESTAMP}"

docker build -t "${IMAGE_NAME}:${TAG}" -f portal/Dockerfile portal/

# Stop old container (ignore if not running)
docker stop "$CONTAINER_NAME" 2>/dev/null || true
docker rm "$CONTAINER_NAME" 2>/dev/null || true

docker run -d \
    --name "$CONTAINER_NAME" \
    --network coolify \
    --restart unless-stopped \
    --env-file "$ENV_FILE" \
    -l "traefik.enable=true" \
    -l "traefik.http.routers.portal-http.entryPoints=http" \
    -l "traefik.http.routers.portal-http.rule=Host(\`marketingmcp.statika.net\`)" \
    -l "traefik.http.routers.portal-http.middlewares=redirect-to-https" \
    -l "traefik.http.routers.portal-http.priority=50" \
    -l "traefik.http.middlewares.redirect-to-https.redirectscheme.scheme=https" \
    -l "traefik.http.routers.portal-https.entryPoints=https" \
    -l "traefik.http.routers.portal-https.rule=Host(\`marketingmcp.statika.net\`)" \
    -l "traefik.http.routers.portal-https.tls=true" \
    -l "traefik.http.routers.portal-https.tls.certresolver=letsencrypt" \
    -l "traefik.http.routers.portal-https.priority=50" \
    -l "traefik.http.services.portal.loadbalancer.server.port=3000" \
    "${IMAGE_NAME}:${TAG}"

echo "[deploy-portal] Container redeployed with image ${IMAGE_NAME}:${TAG}"

# ── 3. Cleanup old images (keep last 3) ──
docker images "$IMAGE_NAME" --format '{{.Repository}}:{{.Tag}}' \
    | sort -r | tail -n +4 | xargs -r docker rmi 2>/dev/null || true

echo "[deploy-portal] Done."
