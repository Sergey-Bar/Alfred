#!/usr/bin/env bash
set -euo pipefail

BACKUP_FILE=${1:-}
if [ -z "$BACKUP_FILE" ]; then
  echo "Usage: $0 <backup-file>"
  exit 1
fi

if [ -z "${DATABASE_URL:-}" ]; then
  echo "Please set DATABASE_URL"
  exit 1
fi

pg_restore -d "$DATABASE_URL" -c "$BACKUP_FILE"

echo "Restore complete"
