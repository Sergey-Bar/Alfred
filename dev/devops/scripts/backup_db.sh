#!/usr/bin/env bash
set -euo pipefail

OUT=${1:-backups/alfred-$(date +"%Y%m%d%H%M%S").sql}
mkdir -p $(dirname "$OUT")

if [ -z "${DATABASE_URL:-}" ]; then
  echo "Please set DATABASE_URL"
  exit 1
fi

pg_dump "$DATABASE_URL" -Fc -f "$OUT"

echo "Backup saved to $OUT"
