# Monitoring with Prometheus

This document explains how to enable monitoring for Alfred and provides a small kustomize example.

## Prerequisites
- A Kubernetes cluster with Prometheus Operator (kube-prometheus-stack) installed.
- `kubectl` configured to access the cluster.

## Helm Chart Support
The Helm chart includes optional `ServiceMonitor` support. In `charts/alfred/values.yaml`:

```yaml
monitoring:
  enabled: true
  serviceMonitor:
    enabled: true
    interval: 30s
    scrapeTimeout: 10s
```

When `monitoring.enabled` and `monitoring.serviceMonitor.enabled` are set to `true`, the chart will render a `ServiceMonitor` that points at the application's `/metrics` endpoint.

### RBAC / Permissions
- `ServiceMonitor` is a CRD provided by the Prometheus Operator. The application does not need extra RBAC to expose `/metrics`.
- Ensure the Prometheus Operator (or the kube-prometheus-stack) is installed in the cluster and has permission to discover `ServiceMonitor` resources.

## Kustomize example (deploy ServiceMonitor directly)
You can create a `kustomize` overlay to apply the `ServiceMonitor` resource. Example layout:

monitoring/
  kustomization.yaml
  servicemonitor.yaml

`kustomization.yaml`:

```yaml
resources:
  - servicemonitor.yaml
```

`servicemonitor.yaml` (example):

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: alfred-staging-sm
  namespace: alfred
spec:
  selector:
    matchLabels:
      app: alfred-api
  endpoints:
    - port: http
      path: /metrics
      interval: 30s
      scrapeTimeout: 10s
```

Apply with:

```bash
kubectl apply -k monitoring/
```

## Verify
- Check Prometheus targets UI (port-forward or Grafana) and look for the `alfred` target.
- Hit `/metrics` on the pod to ensure metrics are exposed:

```bash
kubectl port-forward deployment/alfred-api 8000:8000 -n alfred
curl http://localhost:8000/metrics
```

## Notes
- The chart exposes `/metrics` via `prometheus-fastapi-instrumentator` by default.
- For production, secure access to metrics endpoints (network policies or Prometheus scrape configs).
