import time
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlmodel import Session

from ..dependencies import get_current_user, get_privacy_mode, get_session
from ..logic import CreditCalculator, LLMProxy, QuotaManager
from ..metrics import (
    llm_request_duration,
    llm_requests_total,
    llm_tokens_used,
    quota_exceeded_total,
    quota_utilization
)
from ..models import ChatCompletionRequest, ProjectPriority, User, RequestLog
from ..security import InputValidator

router = APIRouter(prefix="/v1", tags=["AI Gateway"])

def _detect_provider(model: str) -> str:
    """
    [BUG-018 FIX] Expanded provider detection matrix to include modern models.
    """
    model_lower = model.lower()
    mapping = {
        "openai": ["gpt", "o1", "o3", "davinci", "curie", "babbage", "text-embedding"],
        "anthropic": ["claude"],
        "google": ["gemini", "palm"],
        "mistral": ["mistral", "mixtral"],
        "meta": ["llama"],
        "deepseek": ["deepseek"],
        "cohere": ["command", "coral"]
    }
    for provider, patterns in mapping.items():
        if any(p in model_lower for p in patterns):
            return provider
    return "unknown"

@router.post("/chat/completions")
async def chat_completions(
    request: ChatCompletionRequest,
    user: User = Depends(get_current_user),
    strict_privacy: bool = Depends(get_privacy_mode),
    session: Session = Depends(get_session),
    x_project_priority: Optional[str] = Header(None, alias="X-Project-Priority")
):
    """
    OpenAI-Compatible Governance Proxy.
    
    [THE ORCHESTRATION PIPELINE]
    1. Priority Resolution: Determine if this is a standard or critical request.
    2. Cost Forecasting: Estimate token consumption before calling the vendor.
    3. Quota Guardrail: Multi-tier check (Personal -> Team -> Vacation Share).
    4. Compliance Scan: Input validation for prompt injection and security threats.
    5. Execution: Forward to provider with automatic retries and tracing.
    6. Settlement: Atomic credit deduction and immutable audit log generation.
    """
    start_time = time.perf_counter()
    
    # 1. Resolve Project Context
    # Clients can override priority via headers for specifically tagged tasks.
    priority = user.default_priority
    if x_project_priority:
        try:
            priority = ProjectPriority(x_project_priority.lower())
        except ValueError:
            pass

    # 2. Pre-flight Forecasting
    # [BUG-008 FIX] Accurate token estimation using tiktoken
    import tiktoken
    try:
        enc = tiktoken.encoding_for_model(request.model)
        num_tokens = sum(len(enc.encode(m.content)) for m in request.messages)
    except Exception:
        # Fallback to conservative heuristic (approx 4 chars per token)
        num_tokens = sum(len(m.content) // 3 for m in request.messages)
    
    forecast_tokens = num_tokens + (request.max_tokens or 1000)
    estimated_cost = CreditCalculator.estimate_cost(request.model, forecast_tokens)

    # 3. Governance Evaluation
    qm = QuotaManager(session)
    quota_result = qm.check_quota(user, estimated_cost, priority=priority)
    
    if not quota_result.allowed:
        from ..exceptions import QuotaExceededException
        quota_exceeded_total.labels(user_id=str(user.id), quota_type=quota_result.source).inc()
        raise QuotaExceededException(
            message=quota_result.message,
            quota_remaining=float(quota_result.available_credits)
        )

    # 4. Security Scrubbing
    InputValidator.validate_chat_messages(request.messages)

    # 5. Inference Orchestration
    # Forward the request to the upstream provider (OpenAI, Anthropic, Google, etc.)
    # The LLMProxy handles connectivity, timeouts, and exponential backoff.
    try:
        response = await LLMProxy.forward_request(request)
    except Exception as e:
        from ..exceptions import LLMProviderException
        provider = _detect_provider(request.model)
        llm_requests_total.labels(
            model=request.model,
            provider=provider,
            user_id=str(user.id),
            status="error"
        ).inc()
        raise LLMProviderException(f"Upstream Provider Error: {str(e)}")

    # 6. Lifecycle Finalization
    actual_cost = CreditCalculator.calculate_cost(
        model=request.model,
        prompt_tokens=response["usage"]["prompt_tokens"],
        completion_tokens=response["usage"]["completion_tokens"],
        response=response
    )

    # Atomic settlement in the credit ledger
    qm.deduct_quota(user, actual_cost, source=quota_result.source)
    
    # Immutable transactional logging
    from ..logic import RequestLogger
    rl = RequestLogger(session)
    duration_ms = int((time.perf_counter() - start_time) * 1000)
    
    provider = _detect_provider(request.model)
    log = rl.log_request(
        user=user, request=request, response=response,
        cost_credits=actual_cost, quota_source=quota_result.source,
        strict_privacy=strict_privacy, latency_ms=duration_ms,
        provider=provider
    )

    # Asynchronous gamification updates
    from ..dependencies import create_background_task
    from ..logic import EfficiencyScorer
    es = EfficiencyScorer(session)
    create_background_task(es.update_leaderboard(user, log, period_type="daily"))
    create_background_task(es.update_leaderboard(user, log, period_type="monthly"))

    # Telemetry dispatch
    provider = _detect_provider(request.model)
    llm_requests_total.labels(
        model=request.model,
        provider=provider,
        user_id=str(user.id),
        status="success"
    ).inc()
    
    llm_request_duration.labels(
        model=request.model,
        provider=provider
    ).observe(duration_ms / 1000.0)
    
    llm_tokens_used.labels(
        model=request.model,
        user_id=str(user.id),
        type="prompt"
    ).inc(response["usage"]["prompt_tokens"])
    
    llm_tokens_used.labels(
        model=request.model,
        user_id=str(user.id),
        type="completion"
    ).inc(response["usage"]["completion_tokens"])
    
    if user.personal_quota > 0:
        utilization = float(user.used_tokens / user.personal_quota * 100)
        quota_utilization.labels(user_id=str(user.id)).set(utilization)
    
    return response
