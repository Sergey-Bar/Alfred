# Alfred Helm Chart

![Version: 0.1.0](https://img.shields.io/badge/Version-0.1.0-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: 1.0.0](https://img.shields.io/badge/AppVersion-1.0.0-informational?style=flat-square)

## Description

Alfred Helm Chart for deploying the Enterprise AI Credit Governance Platform on Kubernetes.

**Technology Stack (Updated per CODE REVIEW):**
- Kubernetes 1.24+
- Helm 3.8+
- PostgreSQL 16
- Redis 7
- Python 3.12
- FastAPI (latest)

## Prerequisites

- Kubernetes 1.24+
- Helm 3.8+
- PostgreSQL 16+ (external database recommended for production)
- Optional: Prometheus Operator for monitoring

## Installation

### Quick Start

```bash
# Add the repository (if published)
helm repo add alfred https://charts.alfred.dev
helm repo update

# Install with default values
helm install alfred alfred/alfred
```

### Local Installation

```bash
# From the repository root
helm install alfred ./dev/devops/charts/alfred

# With custom values
helm install alfred ./dev/devops/charts/alfred -f custom-values.yaml
```

### Production Installation

```bash
# Create namespace
kubectl create namespace alfred

# Install with production values
helm install alfred ./dev/devops/charts/alfred \
  --namespace alfred \
  --set image.tag=v1.0.0 \
  --set replicaCount=3 \
  --set autoscaling.enabled=true \
  --set postgresql.enabled=false \
  --set postgresql.external.host=postgres.production.svc.cluster.local
```

## Configuration

### Key Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount` | Number of Alfred replicas | `2` |
| `image.repository` | Container image repository | `ghcr.io/AlfredDev/alfred` |
| `image.tag` | Container image tag | `latest` |
| `resources.requests.memory` | Memory request | `512Mi` |
| `resources.limits.memory` | Memory limit | `1Gi` |
| `resources.requests.cpu` | CPU request | `250m` |
| `resources.limits.cpu` | CPU limit | `1000m` |
| `redis.enabled` | Enable Redis for caching | `true` |
| `worker.enabled` | Enable background worker | `true` |
| `monitoring.enabled` | Enable Prometheus monitoring | `true` |
| `autoscaling.enabled` | Enable horizontal pod autoscaling | `false` |
| `postgresql.enabled` | Use internal PostgreSQL (not recommended for prod) | `false` |

### Full Configuration

See [values.yaml](values.yaml) for the complete list of configuration options.

## Upgrades

### Standard Upgrade

```bash
# Upgrade to new version
helm upgrade alfred ./dev/devops/charts/alfred

# Upgrade with new values
helm upgrade alfred ./dev/devops/charts/alfred -f new-values.yaml
```

### Rolling Back

```bash
# View release history
helm history alfred

# Rollback to previous version
helm rollback alfred

# Rollback to specific revision
helm rollback alfred 2
```

## Monitoring

The chart includes Prometheus ServiceMonitor resources for monitoring:

```yaml
monitoring:
  enabled: true
  serviceMonitor:
    enabled: true
    interval: 30s
    scrapeTimeout: 10s
```

Access metrics at: `http://alfred-service:8000/metrics`

## High Availability

### Recommended Production Setup

```yaml
# High availability configuration
replicaCount: 3

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70

affinity:
  podAntiAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
    - labelSelector:
        matchExpressions:
        - key: app.kubernetes.io/name
          operator: In
          values:
          - alfred
      topologyKey: kubernetes.io/hostname

redis:
  enabled: true
  sentinel:
    enabled: true
  persistence:
    enabled: true
    size: 5Gi

postgresql:
  enabled: false  # Use external managed database
```

## Security

### Security Best Practices (CODE REVIEW Compliant)

```yaml
# Run as non-root user
securityContext:
  runAsNonRoot: true
  runAsUser: 1001
  fsGroup: 1001
  capabilities:
    drop:
      - ALL

# Network policies
networkPolicy:
  enabled: true
  ingress:
    - from:
      - podSelector:
          matchLabels:
            app: ingress-nginx

# Pod Security Standards
podSecurityStandards:
  enforce: restricted
```

## Troubleshooting

### Check Pod Status

```bash
kubectl get pods -n alfred
kubectl describe pod alfred-xxx -n alfred
kubectl logs alfred-xxx -n alfred
```

### Check Services

```bash
kubectl get svc -n alfred
kubectl describe svc alfred -n alfred
```

### Test Health Endpoint

```bash
kubectl port-forward svc/alfred 8000:8000 -n alfred
curl http://localhost:8000/health
```

### Common Issues

1. **Database Connection Fails**
   - Check DATABASE_URL environment variable
   - Verify database credentials in secrets
   - Ensure network policies allow database access

2. **High Memory Usage**
   - Increase memory limits in values.yaml
   - Enable autoscaling for horizontal scaling
   - Review worker queue configuration

3. **Slow Response Times**
   - Enable Redis caching
   - Increase replica count
   - Check database query performance

## Development

### Local Testing with Minikube

```bash
# Start minikube
minikube start

# Install chart
helm install alfred ./dev/devops/charts/alfred \
  --set image.pullPolicy=Never \
  --set postgresql.enabled=true

# Access service
minikube service alfred
```

### Template Rendering

```bash
# Render templates without installing
helm template alfred ./dev/devops/charts/alfred

# Render with custom values
helm template alfred ./dev/devops/charts/alfred -f custom-values.yaml
```

## Contributing

See the main [CONTRIBUTING.md](../../../../docs/CONTRIBUTING.md) for contribution guidelines.

## License

MIT License. See [LICENSE](../../../../LICENSE) for details.

## Support

- Documentation: https://github.com/AlfredDev/alfred/docs
- Issues: https://github.com/AlfredDev/alfred/issues
- Discussions: https://github.com/AlfredDev/alfred/discussions

## Maintainers

| Name | Email |
|------|-------|
| Sergey Bar | Sergeybaris@gmail.com |

---

**Last Updated:** February 12, 2026  
**Chart Version:** 0.1.0  
**App Version:** 1.0.0
