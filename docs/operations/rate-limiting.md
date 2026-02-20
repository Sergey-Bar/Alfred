# API Rate Limiting

**Task**: T217 (P0 - Launch Blocker)  
**Status**: ✅ COMPLETE  
**Implementation**: Redis sliding window + per-key/IP rate limiting

## Overview

Alfred implements enterprise-grade API rate limiting to prevent abuse and ensure fair usage across all clients. The system supports:

- **Dual-mode**: In-memory (dev) + Redis distributed (production)
- **Sliding window algorithm**: Precise request tracking
- **Multi-tier limiting**: Per-API-key + Per-IP enforcement
- **Burst allowance**: Handles legitimate traffic spikes
- **Graceful degradation**: Fails open if Redis is unavailable
- **Security**: SHA-256 hashed identifiers (no key leakage in logs)

## Architecture

### Rate Limiting Modes

| Mode | Use Case | Storage | Distributed | Performance |
|------|----------|---------|-------------|-------------|
| `RateLimitMiddleware` | Development | In-memory | ❌ No | Very Fast |
| `RedisRateLimitMiddleware` | Production | Redis | ✅ Yes | Fast |
| SlowAPI (legacy, main.py) | Simple use cases | Redis | ✅ Yes | Fast |

**Production uses**: `RedisRateLimitMiddleware` (configured in `middleware.py`)

### Sliding Window Algorithm

```
Window: [---------- 60 seconds ---------]
Requests:  |  |  |  |  |  |  |  |  current time
           ↑                       ↑
     oldest request          newest request

Count = number of requests within window
Rate limit = 100 requests / 60 seconds
```

**Advantages over fixed window:**
- No reset spikes (gradual expiration)
- Precise enforcement
- Handles burst traffic naturally

## Configuration

### Environment Variables

```bash
# Enable/disable rate limiting
RATE_LIMIT_ENABLED=true

# Base rate limit (applies globally unless overridden)
RATE_LIMIT_REQUESTS=100      # Requests per window
RATE_LIMIT_WINDOW_SECONDS=60 # Window size in seconds
RATE_LIMIT_BURST=20          # Extra allowance for spikes

# Redis configuration (required for distributed mode)
REDIS_ENABLED=true
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=your_redis_password  # optional
```

### Rate Limit Tiers

**Coming soon**: Per-user tier configuration

| Tier | Requests/min | Burst | Use Case |
|------|--------------|-------|----------|
| Free | 60 | 10 | Trials, demos |
| Starter | 300 | 50 | Small teams |
| Professional | 1000 | 200 | Growing companies |
| Enterprise | 10000 | 500 | Large organizations |
| Unlimited | ∞ | ∞ | Internal/admin access |

## Client Identification

Rate limits are enforced per **client identifier**:

### Priority Order

1. **API Key** (from `Authorization: Bearer <key>` or `X-API-Key` header)
   - Hashed with SHA-256 → `key:abc123...` (16 chars)
   - Most specific, highest priority

2. **IP Address** (from `X-Forwarded-For` or `request.client.host`)
   - Format: `ip:192.168.1.1`
   - Fallback when no API key provided

### Security: Key Hashing

```python
# Original key: your_api_key_here_example_12345
# Logged identifier: key:a1b2c3d4e5f6g7h8
#
# ✅ Logs are safe (no key exposure)
# ✅ Unique per key (collision-resistant SHA-256)
# ✅ Consistent across requests (deterministic hash)
```

## HTTP Headers

### Request Headers (Client → Server)

```http
Authorization: Bearer <api_key>
X-API-Key: <api_key>
X-Forwarded-For: <client_ip>
```

### Response Headers (Server → Client)

```http
X-RateLimit-Limit: 100       # Maximum requests per window
X-RateLimit-Remaining: 73    # Requests left in current window
X-RateLimit-Reset: 1708387200 # Unix timestamp when window resets
Retry-After: 42               # Seconds to wait (only on 429)
```

### Rate Limit Error (429)

```http
HTTP/1.1 429 Too Many Requests
Content-Type: application/json
Retry-After: 42
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1708387200

{
  "error": "Rate limit exceeded",
  "code": "rate_limit_exceeded",
  "message": "Global limit reached. Retry in 42s."
}
```

## Client Implementation

### Python (with exponential backoff)

```python
import time
import requests

def call_alfred_api(api_key, prompt):
    headers = {"Authorization": f"Bearer {api_key}"}
    max_retries = 5

    for attempt in range(max_retries):
        response = requests.post(
            "https://api.alfred.ai/v1/completions",
            headers=headers,
            json={"prompt": prompt}
        )

        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 60))
            print(f"Rate limited. Waiting {retry_after}s...")
            time.sleep(retry_after)
            continue

        return response.json()

    raise Exception("Max retries exceeded")
```

### JavaScript/TypeScript

```typescript
async function callAlfredAPI(apiKey: string, prompt: string) {
  const maxRetries = 5;

  for (let attempt = 0; attempt < maxRetries; attempt++) {
    const response = await fetch("https://api.alfred.ai/v1/completions", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ prompt }),
    });

    if (response.status === 429) {
      const retryAfter = parseInt(response.headers.get("Retry-After") || "60");
      console.log(`Rate limited. Waiting ${retryAfter}s...`);
      await new Promise((resolve) => setTimeout(resolve, retryAfter * 1000));
      continue;
    }

    return await response.json();
  }

  throw new Error("Max retries exceeded");
}
```

### cURL

```bash
# Check rate limit status
curl -H "Authorization: Bearer YOUR_API_KEY" \
     -I https://api.alfred.ai/v1/me

# Response headers:
# X-RateLimit-Limit: 100
# X-RateLimit-Remaining: 73
# X-RateLimit-Reset: 1708387200
```

## Monitoring & Observability

### Prometheus Metrics (Coming Soon)

```prometheus
# Total requests rate limited
alfred_rate_limit_exceeded_total{client_type="api_key"}

# Current rate limit usage
alfred_rate_limit_usage{client_id="key:abc123"}

# Rate limit window resets
alfred_rate_limit_resets_total
```

### Log Events

```json
{
  "timestamp": "2026-02-19T14:23:01Z",
  "level": "WARNING",
  "message": "Inbound Traffic: RATE LIMITED",
  "client_id": "key:a1b2c3d4e5f6g7h8",
  "path": "/v1/completions",
  "requests_in_window": 120,
  "limit": 100
}
```

### Admin Queries (Redis)

```bash
# View all rate limit keys
redis-cli KEYS "alfred:ratelimit:*"

# Check specific client's request count
redis-cli ZCARD "alfred:ratelimit:key:abc123"

# View request timestamps for a client
redis-cli ZRANGE "alfred:ratelimit:key:abc123" 0 -1 WITHSCORES

# Manually reset a client's rate limit
redis-cli DEL "alfred:ratelimit:key:abc123"
```

## Operational Procedures

### Temporarily Increase Limits for VIP Client

```bash
# Option 1: Environment variable (requires restart)
RATE_LIMIT_REQUESTS=10000 uvicorn app.main:app

# Option 2: Redis manual adjustment (temporary until window expires)
# Delete their current window to reset
redis-cli DEL "alfred:ratelimit:key:vip_client_hash"

# Option 3: Whitelist in code (permanent)
# Add to middleware.py skip_paths or create tier system
```

### Emergency: Disable Rate Limiting

```bash
# Method 1: Environment variable
export RATE_LIMIT_ENABLED=false
# Restart service

# Method 2: Hot-reload config (if implemented)
curl -X PATCH https://api.alfred.ai/admin/config \
     -H "Authorization: Bearer $ADMIN_KEY" \
     -d '{"rate_limit_enabled": false}'
```

## Troubleshooting

### "Rate limit exceeded but I haven't sent many requests"

**Cause**: Multiple clients sharing the same IP (NAT, corporate proxy)

**Solution**:
1. Use API key authentication (unique per client)
2. Contact support for IP exemption
3. Request higher tier plan

### "Rate limit headers missing in response"

**Cause**: middleware.py not configured or rate limiting disabled

**Check**:
```bash
# Verify middleware is active
curl -I https://api.alfred.ai/health
# Should see:
# X-RateLimit-Limit: 100
```

**Fix**: Ensure `setup_middleware(app)` is called in `main.py`

### "Redis connection errors causing 500s"

**Cause**: RedisRateLimitMiddleware failing closed instead of open

**Temporary workaround**:
```bash
# Switch to in-memory mode
export REDIS_ENABLED=false
# Restart service
```

**Permanent fix**: Ensure Redis is highly available (replica set)

## Configuration Reference

### Complete config.py Settings

```python
# Traffic Control (Rate Limiting)
rate_limit_enabled: bool = True       # Master switch
rate_limit_requests: int = 100        # Requests per window
rate_limit_window_seconds: int = 60   # Window size (seconds)
rate_limit_burst: int = 20            # Burst allowance

# Redis (required for distributed rate limiting)
redis_enabled: bool = True
redis_host: str = "localhost"
redis_port: int = 6379
redis_db: int = 0
redis_password: Optional[str] = None
```

### Recommended Production Settings

```bash
# High-traffic production
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=1000
RATE_LIMIT_WINDOW_SECONDS=60
RATE_LIMIT_BURST=200
REDIS_ENABLED=true
REDIS_URL=redis://redis-cluster:6379/0

# Development
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW_SECONDS=60
RATE_LIMIT_BURST=20
REDIS_ENABLED=false  # In-memory OK for dev
```

---

**For questions or rate limit adjustments**: Contact DevOps team or Sergey Bar
