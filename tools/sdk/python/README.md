# Alfred Python SDK

Official Python SDK for the Alfred AI Credit Governance Platform.

## Installation

```bash
pip install alfred-sdk
```

Or install from source:

```bash
pip install -e tools/sdk/python
```

## Quick Start

```python
from alfred_sdk import AlfredClient

# Initialize the client
client = AlfredClient(api_key="ak_your_api_key_here")

# Check your wallet balance
wallet = client.get_wallet()
print(f"Balance: ${wallet.balance:.2f}")

# Make an AI request
response = client.chat_completion(
    model="gpt-4o",
    messages=[
        {"role": "user", "content": "What is the capital of France?"}
    ]
)
print(response.choices[0]["message"]["content"])
# Output: The capital of France is Paris.

# Check usage
print(f"Tokens used: {response.usage['total_tokens']}")
print(f"Cost: ${response.cost:.4f}")
```

## Features

- **Type-safe**: Full type hints and Pydantic models
- **Automatic retries**: Handles transient failures with exponential backoff
- **Rate limiting**: Respects API rate limits automatically
- **Streaming**: Stream chat completions for real-time responses
- **Error handling**: Typed exceptions for all error conditions

## API Reference

### Initialization

```python
from alfred_sdk import AlfredClient

# Basic usage
client = AlfredClient(api_key="ak_...")

# Custom configuration
client = AlfredClient(
    api_key="ak_...",
    base_url="https://alfred.example.com",  # Custom API URL
    timeout=120.0,  # Request timeout in seconds
    max_retries=5,  # Number of retries on failure
)

# Context manager (auto-closes connection)
with AlfredClient(api_key="ak_...") as client:
    response = client.chat_completion(...)
```

### Chat Completions

```python
# Basic completion
response = client.chat_completion(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello!"}]
)

# With options
response = client.chat_completion(
    model="claude-3.5-sonnet",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain quantum computing."}
    ],
    temperature=0.3,
    max_tokens=500,
)

# Streaming
for chunk in client.chat_completion(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Write a poem."}],
    stream=True,
):
    print(chunk, end="", flush=True)
```

### Wallet & Credits

```python
# Get your wallet
wallet = client.get_wallet()
print(f"Balance: ${wallet.balance:.2f}")
print(f"Soft limit: ${wallet.soft_limit:.2f}")
print(f"Hard limit: ${wallet.hard_limit:.2f}")

# Get transactions
transactions = client.get_transactions(page=1, page_size=50)
for tx in transactions.items:
    print(f"{tx.type}: ${tx.amount:.4f}")

# Transfer credits
transfer = client.transfer_credits(
    to_user_id="user_abc123",
    amount=10.0,
    message="For the Q4 project",
)
```

### Teams

```python
# List teams
teams = client.list_teams()

# Create a team
team = client.create_team(
    name="Engineering",
    description="Engineering department",
)

# Add member
client.add_team_member(team.id, user_id="user_xyz", role="admin")
```

### API Keys

```python
# List keys
keys = client.list_api_keys()

# Create a key
new_key = client.create_api_key(
    name="CI Pipeline",
    scopes=["read", "completions"],
    expires_in_days=90,
)
print(f"New key: {new_key['key']}")  # Only shown once!

# Rotate a key
rotated = client.rotate_api_key(key_id="key_abc")
```

### Analytics

```python
# Usage report
usage = client.get_usage_report(
    start_date="2024-01-01",
    end_date="2024-01-31",
)
print(f"Total requests: {usage.total_requests}")
print(f"Total cost: ${usage.total_cost:.2f}")

# Cost breakdown
costs = client.get_cost_breakdown()
for model, cost in costs.by_model.items():
    print(f"{model}: ${cost:.2f}")
```

## Error Handling

```python
from alfred_sdk import (
    AlfredClient,
    AuthenticationError,
    QuotaExceededError,
    RateLimitError,
    ValidationError,
)

client = AlfredClient(api_key="ak_...")

try:
    response = client.chat_completion(
        model="gpt-4o",
        messages=[{"role": "user", "content": "Hello"}]
    )
except AuthenticationError:
    print("Invalid API key")
except QuotaExceededError as e:
    print(f"Out of credits! Balance: ${e.current_balance:.2f}")
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds")
except ValidationError as e:
    print(f"Invalid request: {e.errors}")
```

## License

MIT
