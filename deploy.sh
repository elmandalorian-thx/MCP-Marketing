#!/usr/bin/env bash
# deploy.sh — Pull from GitHub (source of truth), rebuild and redeploy the MCP container.
# Triggered by systemd file watcher or run manually.
#
# WORKFLOW: GitHub is the single source of truth.
# - Local PC or server Claude Code CLI → commit → push to GitHub
# - This script: pull from GitHub → build → deploy
# - Never auto-commits or pushes from here.

set -euo pipefail

REPO_DIR="/home/ubuntu/MCP-Marketing"
IMAGE_NAME="marketing-mcp"
CONTAINER_NAME="marketing-mcp"
ENV_FILE="${REPO_DIR}/.env"

cd "$REPO_DIR"

# ── 1. Git: pull latest from GitHub ──
echo "[deploy] Pulling latest from GitHub..."
git fetch origin main
git reset --hard origin/main
echo "[deploy] Synced to $(git rev-parse --short HEAD)"

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
    -l "traefik.http.routers.marketingmcp-http.rule=Host(\`marketingmcp.statika.net\`) && PathPrefix(\`/mcp\`)" \
    -l "traefik.http.routers.marketingmcp-http.middlewares=redirect-to-https" \
    -l "traefik.http.routers.marketingmcp-http.priority=100" \
    -l "traefik.http.middlewares.redirect-to-https.redirectscheme.scheme=https" \
    -l "traefik.http.routers.marketingmcp-https.entryPoints=https" \
    -l "traefik.http.routers.marketingmcp-https.rule=Host(\`marketingmcp.statika.net\`) && PathPrefix(\`/mcp\`)" \
    -l "traefik.http.routers.marketingmcp-https.tls=true" \
    -l "traefik.http.routers.marketingmcp-https.tls.certresolver=letsencrypt" \
    -l "traefik.http.routers.marketingmcp-https.priority=100" \
    -l "traefik.http.services.marketingmcp.loadbalancer.server.port=8000" \
    "${IMAGE_NAME}:${TAG}"

echo "[deploy] Container redeployed with image ${IMAGE_NAME}:${TAG}"

# ── 3. Cleanup old images (keep last 3) ──
docker images "$IMAGE_NAME" --format '{{.Repository}}:{{.Tag}}' \
    | sort -r | tail -n +4 | xargs -r docker rmi 2>/dev/null || true

echo "[deploy] Done."
