"""
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L2
Logic:       Main Alfred SDK client with typed methods for all
             API endpoints, automatic retries, and rate limiting.
Root Cause:  Sprint task T184 — Python SDK.
Context:     Drop-in replacement for direct API calls.
Suitability: L2 — Standard HTTP client patterns.
──────────────────────────────────────────────────────────────
"""

import time
import json
from typing import Optional, Dict, Any, List, Iterator, Union
from urllib.parse import urljoin
import httpx

from .models import (
    User,
    Team,
    Wallet,
    Transaction,
    Transfer,
    APIKey,
    Provider,
    Policy,
    Experiment,
    UsageReport,
    CostBreakdown,
    CompletionRequest,
    CompletionResponse,
    PaginatedResponse,
)
from .exceptions import (
    AlfredError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ValidationError,
    QuotaExceededError,
    RateLimitError,
    ProviderError,
    PolicyViolationError,
)


class AlfredClient:
    """
    Alfred SDK Client — typed interface to the Alfred AI Credit Governance Platform.
    
    Usage:
        >>> from alfred_sdk import AlfredClient
        >>> client = AlfredClient(api_key="ak_...")
        >>> 
        >>> # Check wallet balance
        >>> wallet = client.get_wallet()
        >>> print(f"Balance: ${wallet.balance:.2f}")
        >>> 
        >>> # Make an AI request
        >>> response = client.chat_completion(
        ...     model="gpt-4o",
        ...     messages=[{"role": "user", "content": "Hello!"}]
        ... )
        >>> print(response.choices[0]["message"]["content"])
    """
    
    DEFAULT_BASE_URL = "http://localhost:8000"
    DEFAULT_TIMEOUT = 60.0
    MAX_RETRIES = 3
    
    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = MAX_RETRIES,
    ):
        """
        Initialize the Alfred client.
        
        Args:
            api_key: Alfred API key (starts with 'ak_')
            base_url: API base URL (default: http://localhost:8000)
            timeout: Request timeout in seconds
            max_retries: Number of retries on transient failures
        """
        self.api_key = api_key
        self.base_url = (base_url or self.DEFAULT_BASE_URL).rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": "alfred-sdk-python/1.0.0",
            },
            timeout=timeout,
        )
    
    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()
    
    def __enter__(self) -> "AlfredClient":
        return self
    
    def __exit__(self, *args) -> None:
        self.close()
    
    # ========================================================
    # Internal HTTP methods
    # ========================================================
    
    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make an HTTP request with retries and error handling."""
        last_error: Optional[Exception] = None
        
        for attempt in range(self.max_retries):
            try:
                response = self._client.request(
                    method=method,
                    url=path,
                    params=params,
                    json=json_data,
                )
                
                return self._handle_response(response)
                
            except httpx.HTTPStatusError as e:
                last_error = self._handle_http_error(e)
                if not self._should_retry(e.response.status_code):
                    raise last_error
                    
            except httpx.RequestError as e:
                last_error = AlfredError(f"Request failed: {e}")
                
            # Exponential backoff
            if attempt < self.max_retries - 1:
                time.sleep(2 ** attempt)
        
        raise last_error or AlfredError("Max retries exceeded")
    
    def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """Handle HTTP response and raise appropriate errors."""
        if response.status_code >= 400:
            self._raise_for_status(response)
        
        if response.status_code == 204:
            return {}
        
        return response.json()
    
    def _raise_for_status(self, response: httpx.Response) -> None:
        """Raise appropriate exception based on status code."""
        status = response.status_code
        try:
            data = response.json()
        except json.JSONDecodeError:
            data = {"detail": response.text}
        
        message = data.get("detail", data.get("message", "Unknown error"))
        
        if status == 401:
            raise AuthenticationError(message, status, data)
        elif status == 403:
            raise AuthorizationError(message, status, data)
        elif status == 404:
            raise NotFoundError(message, status, data)
        elif status == 422:
            raise ValidationError(message, errors=data.get("errors"), status_code=status, response=data)
        elif status == 429:
            retry_after = response.headers.get("Retry-After")
            if "quota" in message.lower() or "credit" in message.lower():
                raise QuotaExceededError(message, status_code=status, response=data)
            raise RateLimitError(
                message,
                retry_after=int(retry_after) if retry_after else None,
                status_code=status,
                response=data,
            )
        elif status >= 500:
            raise ProviderError(message, status_code=status, response=data)
        else:
            raise AlfredError(message, status, data)
    
    def _handle_http_error(self, error: httpx.HTTPStatusError) -> AlfredError:
        """Convert httpx error to Alfred error."""
        self._raise_for_status(error.response)
        return AlfredError(str(error))  # Should not reach here
    
    def _should_retry(self, status_code: int) -> bool:
        """Check if request should be retried based on status code."""
        return status_code in (429, 500, 502, 503, 504)
    
    # ========================================================
    # User Management
    # ========================================================
    
    def get_me(self) -> User:
        """Get current user profile."""
        data = self._request("GET", "/v1/users/me")
        return User(**data)
    
    def update_me(self, name: Optional[str] = None) -> User:
        """Update current user profile."""
        payload = {}
        if name is not None:
            payload["name"] = name
        data = self._request("PATCH", "/v1/users/me", json_data=payload)
        return User(**data)
    
    def list_users(self, page: int = 1, page_size: int = 20) -> PaginatedResponse:
        """List users (admin only)."""
        data = self._request("GET", "/v1/users", params={"page": page, "page_size": page_size})
        return PaginatedResponse(**data)
    
    def get_user(self, user_id: str) -> User:
        """Get user by ID."""
        data = self._request("GET", f"/v1/users/{user_id}")
        return User(**data)
    
    # ========================================================
    # Team Management
    # ========================================================
    
    def list_teams(self, page: int = 1, page_size: int = 20) -> PaginatedResponse:
        """List teams."""
        data = self._request("GET", "/v1/teams", params={"page": page, "page_size": page_size})
        return PaginatedResponse(**data)
    
    def get_team(self, team_id: str) -> Team:
        """Get team by ID."""
        data = self._request("GET", f"/v1/teams/{team_id}")
        return Team(**data)
    
    def create_team(self, name: str, description: Optional[str] = None) -> Team:
        """Create a new team."""
        data = self._request("POST", "/v1/teams", json_data={
            "name": name,
            "description": description,
        })
        return Team(**data)
    
    def add_team_member(self, team_id: str, user_id: str, role: str = "member") -> Dict[str, Any]:
        """Add a member to a team."""
        return self._request("POST", f"/v1/teams/{team_id}/members", json_data={
            "user_id": user_id,
            "role": role,
        })
    
    def remove_team_member(self, team_id: str, user_id: str) -> None:
        """Remove a member from a team."""
        self._request("DELETE", f"/v1/teams/{team_id}/members/{user_id}")
    
    # ========================================================
    # Wallet & Credits
    # ========================================================
    
    def get_wallet(self) -> Wallet:
        """Get current user's wallet."""
        data = self._request("GET", "/v1/wallets/me")
        return Wallet(**data)
    
    def get_wallet_by_id(self, wallet_id: str) -> Wallet:
        """Get wallet by ID."""
        data = self._request("GET", f"/v1/wallets/{wallet_id}")
        return Wallet(**data)
    
    def add_credits(self, wallet_id: str, amount: float, description: Optional[str] = None) -> Transaction:
        """Add credits to a wallet (admin only)."""
        data = self._request("POST", f"/v1/wallets/{wallet_id}/credit", json_data={
            "amount": amount,
            "description": description,
        })
        return Transaction(**data)
    
    def get_transactions(
        self,
        wallet_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResponse:
        """Get wallet transactions."""
        path = f"/v1/wallets/{wallet_id}/transactions" if wallet_id else "/v1/wallets/me/transactions"
        data = self._request("GET", path, params={"page": page, "page_size": page_size})
        return PaginatedResponse(**data)
    
    # ========================================================
    # Transfers
    # ========================================================
    
    def transfer_credits(
        self,
        to_user_id: str,
        amount: float,
        message: Optional[str] = None,
    ) -> Transfer:
        """Transfer credits to another user."""
        data = self._request("POST", "/v1/transfers", json_data={
            "to_user_id": to_user_id,
            "amount": amount,
            "message": message,
        })
        return Transfer(**data)
    
    def get_transfers(self, page: int = 1, page_size: int = 20) -> PaginatedResponse:
        """Get transfer history."""
        data = self._request("GET", "/v1/transfers", params={"page": page, "page_size": page_size})
        return PaginatedResponse(**data)
    
    # ========================================================
    # API Keys
    # ========================================================
    
    def list_api_keys(self) -> List[APIKey]:
        """List user's API keys."""
        data = self._request("GET", "/v1/api-keys")
        return [APIKey(**k) for k in data.get("items", data)]
    
    def create_api_key(
        self,
        name: str,
        scopes: Optional[List[str]] = None,
        expires_in_days: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Create a new API key. Returns the full key only once."""
        return self._request("POST", "/v1/api-keys", json_data={
            "name": name,
            "scopes": scopes or [],
            "expires_in_days": expires_in_days,
        })
    
    def revoke_api_key(self, key_id: str) -> None:
        """Revoke an API key."""
        self._request("DELETE", f"/v1/api-keys/{key_id}")
    
    def rotate_api_key(self, key_id: str) -> Dict[str, Any]:
        """Rotate an API key. Returns the new key."""
        return self._request("POST", f"/v1/api-keys/{key_id}/rotate")
    
    # ========================================================
    # AI Completions
    # ========================================================
    
    def chat_completion(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs,
    ) -> Union[CompletionResponse, Iterator[str]]:
        """
        Create a chat completion (OpenAI-compatible).
        
        Args:
            model: Model identifier (e.g., 'gpt-4o', 'claude-3.5-sonnet')
            messages: List of message objects with 'role' and 'content'
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            **kwargs: Additional parameters passed to the API
        
        Returns:
            CompletionResponse or iterator of chunks if streaming
        """
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": stream,
            **kwargs,
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
        if stream:
            return self._stream_completion(payload)
        
        data = self._request("POST", "/v1/chat/completions", json_data=payload)
        return CompletionResponse(**data)
    
    def _stream_completion(self, payload: Dict[str, Any]) -> Iterator[str]:
        """Stream a chat completion."""
        with self._client.stream(
            "POST",
            "/v1/chat/completions",
            json=payload,
        ) as response:
            for line in response.iter_lines():
                if line.startswith("data: "):
                    chunk = line[6:]
                    if chunk == "[DONE]":
                        break
                    yield chunk
    
    # ========================================================
    # Providers
    # ========================================================
    
    def list_providers(self) -> List[Provider]:
        """List available LLM providers."""
        data = self._request("GET", "/v1/providers")
        return [Provider(**p) for p in data.get("items", data)]
    
    def get_provider_health(self) -> Dict[str, Any]:
        """Get health status of all providers."""
        return self._request("GET", "/v1/providers/health")
    
    # ========================================================
    # Policies
    # ========================================================
    
    def list_policies(self) -> List[Policy]:
        """List governance policies."""
        data = self._request("GET", "/v1/policies")
        return [Policy(**p) for p in data.get("items", data)]
    
    def get_policy(self, policy_id: str) -> Policy:
        """Get policy by ID."""
        data = self._request("GET", f"/v1/policies/{policy_id}")
        return Policy(**data)
    
    def create_policy(
        self,
        name: str,
        rules: Dict[str, Any],
        action: str = "deny",
        description: Optional[str] = None,
    ) -> Policy:
        """Create a governance policy."""
        data = self._request("POST", "/v1/policies", json_data={
            "name": name,
            "rules": rules,
            "action": action,
            "description": description,
        })
        return Policy(**data)
    
    # ========================================================
    # Experiments
    # ========================================================
    
    def list_experiments(self) -> List[Experiment]:
        """List A/B experiments."""
        data = self._request("GET", "/v1/experiments")
        return [Experiment(**e) for e in data.get("items", data)]
    
    def get_experiment(self, experiment_id: str) -> Experiment:
        """Get experiment by ID."""
        data = self._request("GET", f"/v1/experiments/{experiment_id}")
        return Experiment(**data)
    
    def create_experiment(
        self,
        name: str,
        variants: List[Dict[str, Any]],
        traffic_split: Dict[str, float],
        description: Optional[str] = None,
    ) -> Experiment:
        """Create an A/B experiment."""
        data = self._request("POST", "/v1/experiments", json_data={
            "name": name,
            "variants": variants,
            "traffic_split": traffic_split,
            "description": description,
        })
        return Experiment(**data)
    
    def start_experiment(self, experiment_id: str) -> Experiment:
        """Start an experiment."""
        data = self._request("POST", f"/v1/experiments/{experiment_id}/start")
        return Experiment(**data)
    
    def conclude_experiment(self, experiment_id: str, winner: str) -> Experiment:
        """Conclude an experiment with a winner."""
        data = self._request("POST", f"/v1/experiments/{experiment_id}/conclude", json_data={
            "winner": winner,
        })
        return Experiment(**data)
    
    # ========================================================
    # Analytics
    # ========================================================
    
    def get_usage_report(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> UsageReport:
        """Get usage report for the current user."""
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        data = self._request("GET", "/v1/analytics/usage/me", params=params)
        return UsageReport(**data)
    
    def get_cost_breakdown(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> CostBreakdown:
        """Get cost breakdown for the current user."""
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        data = self._request("GET", "/v1/analytics/costs/me", params=params)
        return CostBreakdown(**data)
