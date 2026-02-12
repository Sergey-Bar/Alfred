"""Custom Prometheus metrics for Alfred"""

try:
    from prometheus_client import Counter, Histogram, Gauge
except ImportError:
    # Prometheus client not installed, create dummy classes
    class Counter:
        def __init__(self, *args, **kwargs):
            pass
        def labels(self, **kwargs):
            return self
        def inc(self, amount=1):
            pass
    
    class Histogram:
        def __init__(self, *args, **kwargs):
            pass
        def labels(self, **kwargs):
            return self
        def observe(self, amount):
            pass
    
    class Gauge:
        def __init__(self, *args, **kwargs):
            pass
        def labels(self, **kwargs):
            return self
        def set(self, value):
            pass

# LLM Request Metrics
llm_requests_total = Counter(
    'alfred_llm_requests_total',
    'Total LLM API requests',
    ['model', 'provider', 'user_id', 'status']
)

llm_request_duration = Histogram(
    'alfred_llm_request_duration_seconds',
    'LLM request duration in seconds',
    ['model', 'provider']
)

llm_tokens_used = Counter(
    'alfred_llm_tokens_used_total',
    'Total tokens consumed',
    ['model', 'user_id', 'type']  # type: prompt|completion
)

# Quota Metrics
quota_exceeded_total = Counter(
    'alfred_quota_exceeded_total',
    'Total quota exceeded events',
    ['user_id', 'quota_type']  # personal|team
)

quota_utilization = Gauge(
    'alfred_quota_utilization_percent',
    'Current quota utilization percentage',
    ['user_id']
)

# Credit Metrics
credits_transferred_total = Counter(
    'alfred_credits_transferred_total',
    'Total credits transferred between users',
    ['from_user_id', 'to_user_id']
)

# Approval Metrics
approval_requests_total = Counter(
    'alfred_approval_requests_total',
    'Total approval requests',
    ['status']  # pending|approved|rejected
)

# Vacation Mode Metrics
vacation_mode_activations = Counter(
    'alfred_vacation_mode_activations_total',
    'Total vacation mode activations',
    ['user_id']
)
