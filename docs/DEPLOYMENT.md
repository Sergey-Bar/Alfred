# Alfred Deployment Guide

Production deployment instructions for Alfred.

## Table of Contents

- [Overview](#overview)
- [Docker Deployment](#docker-deployment)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Production Checklist](#production-checklist)
- [Environment Configuration](#environment-configuration)
- [Database Setup](#database-setup)
- [Reverse Proxy](#reverse-proxy)
- [Monitoring](#monitoring)
- [Scaling](#scaling)

---

## Overview

Alfred can be deployed in several ways:

| Method | Best For | Complexity |
|--------|----------|------------|
| Docker Compose | Dev, small teams | Low |
| Kubernetes | Production, scale | Medium |
| Bare metal | Custom requirements | High |

---

## Docker Deployment

### Quick Start

```bash
# Clone repository
git clone https://github.com/your-org/alfred.git
cd alfred

# Configure environment
cp dev/backend/config/.env.example .env
# Edit .env with your API keys and settings

# Start with Docker Compose
cd dev/devops/docker && docker-compose up -d

# Check logs
docker-compose logs -f
```

### Build from Source

```bash
# Build image
docker build -t alfred -f dev/devops/docker/Dockerfile .

# Run container
docker run -d \
  --name alfred \
  -p 8000:8000 \
  -e DATABASE_URL=sqlite:///./dev/backend/data/alfred.db \
  -e OPENAI_API_KEY=sk-your-key \
  -v alfred-data:/app/data \
  alfred
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  alfred:
    build:
      context: ..
      dockerfile: dev/devops/docker/Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://alfred:password@postgres:5432/alfred
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - postgres
    restart: unless-stopped

  postgres:
    image: postgres:16-alpine
    environment:
      - POSTGRES_USER=alfred
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=alfred
    volumes:
      - postgres-data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres-data:
```

---

## Kubernetes Deployment

### Helm Chart (Coming Soon)

```bash
helm repo add alfred https://charts.alfred.io
helm install alfred alfred/alfred \
  --set database.url=postgresql://... \
  --set openai.apiKey=sk-...
```

### Manual Kubernetes

**Deployment:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: alfred
spec:
  replicas: 3
  selector:
    matchLabels:
      app: alfred
  template:
    metadata:
      labels:
        app: alfred
    spec:
      containers:
      - name: alfred
        image: ghcr.io/your-org/alfred:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: alfred-secrets
              key: database-url
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: alfred-secrets
              key: openai-api-key
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 15
          periodSeconds: 20
```

**Service:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: alfred
spec:
  selector:
    app: alfred
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP
```

**Ingress:**
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: alfred
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - alfred.company.com
    secretName: alfred-tls
  rules:
  - host: alfred.company.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: alfred
            port:
              number: 80
```

**Troubleshooting Tips:**
- **Issue**: Pods stuck in `CrashLoopBackOff`.
  **Solution**: Check logs using `kubectl logs <pod-name>`.
- **Issue**: Service not accessible.
  **Solution**: Verify Ingress configuration and DNS settings.

---

## Production Checklist

### Before Go-Live

- [ ] **Database**: PostgreSQL configured (not SQLite)
- [ ] **HTTPS**: TLS certificates installed
- [ ] **Secrets**: API keys in Vault or K8s secrets (not .env)
- [ ] **Backups**: Database backup strategy in place
- [ ] **Monitoring**: Health checks and alerting configured
- [ ] **Logging**: Centralized logging (ELK, CloudWatch, etc.)
- [ ] **Rate Limits**: Appropriate limits configured
- [ ] **CORS**: Restricted to your domains

### Security Hardening

```env
# Production security settings
DEBUG=false
ENVIRONMENT=production
CORS_ORIGINS=["https://alfred.company.com"]
FORCE_STRICT_PRIVACY=false
MASK_PII_IN_LOGS=true
SESSION_TOKEN_TTL_MINUTES=15
MFA_REQUIRED_THRESHOLD=10000.0
ANOMALY_DETECTION_ENABLED=true
```

---

## Environment Configuration

### Required Variables

```env
# Database (PostgreSQL for production)
DATABASE_URL=postgresql://user:password@host:5432/alfred

# At least one LLM provider
OPENAI_API_KEY=sk-...
```

### Recommended for Production

```env
# Application
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
LOG_FORMAT=json

# Security
CORS_ORIGINS=["https://your-domain.com"]
RATE_LIMIT_ENABLED=true

# Database
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20

# Notifications (choose one or more)
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
TEAMS_WEBHOOK_URL=https://outlook.office.com/...
```

---

## Database Setup

### PostgreSQL

```bash
# Create database
createdb alfred

# Or with Docker
docker run -d \
  --name alfred-postgres \
  -e POSTGRES_USER=alfred \
  -e POSTGRES_PASSWORD=secretpassword \
  -e POSTGRES_DB=alfred \
  -p 5432:5432 \
  -v postgres-data:/var/lib/postgresql/data \
  postgres:16-alpine
```

### Run Migrations

```bash
# With venv activated
alembic -c dev/backend/config/alembic.ini upgrade head
```

### Backup Strategy

```bash
# Daily backup cron job
0 2 * * * pg_dump -U alfred alfred > /backups/alfred-$(date +\%Y\%m\%d).sql

# Restore from backup
psql -U alfred alfred < /backups/alfred-20260212.sql
```

---

## Reverse Proxy

### Nginx

```nginx
upstream alfred {
    server 127.0.0.1:8000;
    keepalive 32;
}

server {
    listen 443 ssl http2;
    server_name alfred.company.com;

    ssl_certificate /etc/letsencrypt/live/alfred.company.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/alfred.company.com/privkey.pem;

    location / {
        proxy_pass http://alfred;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support (for streaming)
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts for long-running LLM requests
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
}

server {
    listen 80;
    server_name alfred.company.com;
    return 301 https://$host$request_uri;
}
```

### Caddy

```caddyfile
alfred.company.com {
    reverse_proxy localhost:8000
}
```

---

## Monitoring

### Health Checks

```bash
# Basic health check
curl http://localhost:8000/health

# Response
{"status": "healthy", "version": "1.0.0"}
```

### Prometheus Metrics

Alfred exposes Prometheus metrics at `/metrics`:

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'alfred'
    static_configs:
      - targets: ['alfred:8000']
```

### Key Metrics

| Metric | Description |
|--------|-------------|
| `alfred_requests_total` | Total API requests |
| `alfred_credits_used_total` | Total credits consumed |
| `alfred_request_duration_seconds` | Request latency |
| `alfred_active_users` | Currently active users |
| `alfred_quota_exceeded_total` | Quota exceeded events |

### Alerting

Example Prometheus alert rules:

```yaml
groups:
  - name: alfred
    rules:
      - alert: AlfredHighErrorRate
        expr: rate(alfred_requests_total{status="5xx"}[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: High error rate in Alfred

      - alert: AlfredHighLatency
        expr: histogram_quantile(0.95, alfred_request_duration_seconds) > 10
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: High latency in Alfred API
```

---

## Scaling

### Horizontal Scaling

Alfred is stateless and can be horizontally scaled:

```yaml
# Kubernetes HPA
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: alfred-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: alfred
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### Database Scaling

For high-traffic deployments:

1. **Connection Pooling**: Use PgBouncer
2. **Read Replicas**: Route analytics queries to replicas
3. **Sharding**: Partition by tenant (enterprise)

### Multi-Region

For global deployments:

```
US Alfred Instance ←→ EU Alfred Instance ←→ APAC Alfred Instance
         │                    │                      │
    US Azure OpenAI      EU Azure OpenAI        APAC Bedrock
```

Configure regional routing via DNS or load balancer.

---

*See also: [Architecture](architecture.md) | [Security](security.md) | [Installation](install.md)*

