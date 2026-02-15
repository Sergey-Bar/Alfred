"""
Alfred Telemetry & Prometheus Instrumentation

[ARCHITECTURAL ROLE]
This module defines the real-time telemetry counters, gauges, and histograms 
used for monitoring the health and performance of the Alfred platform. It 
enables SRE and Engineering teams to visualize request flows, financial 
utilization, and provider latency via Grafana or Prometheus.

[KEY METRICS DOMAINS]
1. Throughput: Tracking LLM request volume per model/user.
2. Latency: Auditing upstream provider response times.
3. Financial: Real-time quota utilization and credit velocity.
4. Governance: Monitoring approval workflows and vacation sharing.
"""

try:
    from prometheus_client import Counter, Gauge, Histogram
except ImportError:
    # Prometheus client is optional; providing functional stubs to avoid 
    # runtime crashes in environments where monitoring is disabled.
    class Counter:
        def __init__(self, *args, **kwargs): pass
        def labels(self, **kwargs): return self
        def inc(self, amount=1): pass

    class Histogram:
        def __init__(self, *args, **kwargs): pass
        def labels(self, **kwargs): return self
        def observe(self, amount): pass

    class Gauge:
        def __init__(self, *args, **kwargs): pass
        def labels(self, **kwargs): return self
        def set(self, value): pass

# -------------------------------------------------------------------
# LLM Proxy Metrics (Throughput & Latency)
# -------------------------------------------------------------------

llm_requests_total = Counter(
    'alfred_llm_requests_total',
    'Volume of inference requests orchestrated through the gateway.',
    ['model', 'provider', 'user_id', 'status']
)

llm_request_duration = Histogram(
    'alfred_llm_request_duration_seconds',
    'End-to-end latency for upstream provider completion.',
    ['model', 'provider']
)

llm_tokens_used = Counter(
    'alfred_llm_tokens_used_total',
    'Aggregate token consumption for capacity planning.',
    ['model', 'user_id', 'type']  # type: prompt | completion
)


# -------------------------------------------------------------------
# Financial & Quota Governance Metrics
# -------------------------------------------------------------------

quota_exceeded_total = Counter(
    'alfred_quota_exceeded_total',
    'Incident rate of users hitting hard-cap limits.',
    ['user_id', 'quota_type']  # personal | team
)

quota_utilization = Gauge(
    'alfred_quota_utilization_percent',
    'Real-time burn rate of organizational credits.',
    ['user_id']
)

credits_transferred_total = Counter(
    'alfred_credits_transferred_total',
    'Total liquidity velocity within the organization.',
    ['from_user_id', 'to_user_id']
)


# -------------------------------------------------------------------
# Process & Lifecycle Metrics
# -------------------------------------------------------------------

approval_requests_total = Counter(
    'alfred_approval_requests_total',
    'Throughput of the Quota Approval workflow.',
    ['status']  # pending | approved | rejected
)

vacation_mode_activations = Counter(
    'alfred_vacation_mode_activations_total',
    'Volume of "Elastic Quota" transfers via vacation sharing.',
    ['user_id']
)
