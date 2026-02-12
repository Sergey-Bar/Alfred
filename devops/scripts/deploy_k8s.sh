#!/usr/bin/env bash
set -euo pipefail

ENV=${1:-staging}
K8S_DIR="devops/k8s/$ENV"

if [ ! -d "$K8S_DIR" ]; then
  echo "No manifests for environment: $ENV"
  exit 1
fi

kubectl apply -k $K8S_DIR
kubectl rollout status deployment/alfred-api -n alfred || true

echo "Deployed Alfred to $ENV"
