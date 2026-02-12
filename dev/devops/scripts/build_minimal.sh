#!/usr/bin/env bash
set -euo pipefail

# Build a minimal deployable artifact in ./dist
# Copies only runtime files: app, alembic, config, static, Dockerfile, requirements/requirements.txt

OUT_DIR=${1:-dist}
rm -rf "$OUT_DIR"
mkdir -p "$OUT_DIR"

echo "Creating minimal bundle in $OUT_DIR"

# Copy application
rsync -av --progress --exclude='__pycache__' dev/backend/app/ "$OUT_DIR/app/"

# Copy migrations
rsync -av --progress dev/backend/alembic/ "$OUT_DIR/alembic/"

# Copy config
rsync -av --progress dev/backend/config/ "$OUT_DIR/config/"

# Copy static assets
rsync -av --progress dev/frontend/static/ "$OUT_DIR/static/"

# Copy Docker and docker-compose
cp dev/devops/docker/Dockerfile "$OUT_DIR/"
cp dev/devops/docker/docker-compose.yml "$OUT_DIR/" || true

# Copy requirements
cp dev/backend/requirements/requirements.txt "$OUT_DIR/" || true
cp dev/backend/requirements/requirements-dev.txt "$OUT_DIR/" || true

# Copy Helm chart if present
if [ -d dev/devops/charts/alfred ]; then
  rsync -av --progress dev/devops/charts/alfred/ "$OUT_DIR/charts/alfred/"
fi

# Clean up any node_modules or build artifacts accidentally copied
find "$OUT_DIR" -name 'node_modules' -prune -exec rm -rf {} + || true

echo "Minimal bundle created: $OUT_DIR"
