# Supported LLM Providers

Alfred supports 100+ LLM providers through LiteLLM integration.

## Table of Contents

- [Overview](#overview)
- [Public APIs](#public-apis)
- [Enterprise Cloud](#enterprise-cloud)
- [Self-Hosted](#self-hosted)
- [Configuration Examples](#configuration-examples)
- [Pricing Reference](#pricing-reference)

---

## Overview

Alfred acts as a proxy gateway, routing requests to any supported LLM provider while maintaining unified quota management. All providers are accessed through the same OpenAI-compatible API.

| Category | Providers | Use Case |
|----------|-----------|----------|
| **Public APIs** | OpenAI, Anthropic, Google | General purpose, latest models |
| **Enterprise Cloud** | Azure, AWS Bedrock, Vertex AI | Data residency, enterprise contracts |
| **Self-Hosted** | vLLM, TGI, Ollama | Cost control, privacy, customization |

---

## Public APIs

### OpenAI

**Models:**
- `gpt-4o` - Latest multimodal model
- `gpt-4o-mini` - Fast, cost-effective
- `gpt-4-turbo` - Extended context
- `o1` / `o1-mini` - Reasoning models
- `gpt-3.5-turbo` - Legacy, low cost

**Configuration:**
```env
OPENAI_API_KEY=sk-...
```

### Anthropic

**Models:**
- `claude-3-5-sonnet-20241022` - Best overall
- `claude-3-5-haiku-20241022` - Fast, cheap
- `claude-3-opus-20240229` - Most capable

**Configuration:**
```env
ANTHROPIC_API_KEY=sk-ant-...
```

### Google AI

**Models:**
- `gemini-1.5-pro` - Extended context (1M tokens)
- `gemini-1.5-flash` - Fast responses
- `gemini-1.0-pro` - General purpose

**Configuration:**
```env
GOOGLE_API_KEY=...
```

---

## Enterprise Cloud

### Azure OpenAI

**Advantages:**
- Data residency compliance
- Enterprise SLAs
- Private network access

**Models:**
- Same as OpenAI (deployed to your resource)

**Configuration:**
```env
AZURE_API_KEY=...
AZURE_API_BASE=https://your-resource.openai.azure.com/
AZURE_API_VERSION=2024-02-15-preview
AZURE_DEPLOYMENT_NAME=gpt-4o
```

**Usage:**
```json
{
  "model": "azure/gpt-4o",
  "messages": [...]
}
```

### AWS Bedrock

**Advantages:**
- AWS security controls
- Pay-per-use pricing
- Multiple model providers

**Supported Models:**
- Claude (Anthropic)
- Llama (Meta)
- Mistral
- Amazon Titan

**Configuration:**
```env
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1
```

**Usage:**
```json
{
  "model": "bedrock/anthropic.claude-3-sonnet-20240229-v1:0",
  "messages": [...]
}
```

### Google Vertex AI

**Advantages:**
- GCP integration
- Enterprise features
- Managed infrastructure

**Configuration:**
```env
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
VERTEX_PROJECT=your-project-id
VERTEX_LOCATION=us-central1
```

---

## Self-Hosted

### vLLM

High-performance inference server for open models.

**Supported Models:**
- Llama 3.1 (8B, 70B, 405B)
- Mixtral 8x7B, 8x22B
- Mistral 7B
- DeepSeek Coder
- Qwen 2.5

**Configuration:**
```env
VLLM_API_BASE=http://gpu-server:8000/v1
```

**Usage:**
```json
{
  "model": "hosted_vllm/meta-llama/Llama-3.1-70B-Instruct",
  "messages": [...]
}
```

**Deployment:**
```bash
# Start vLLM server
python -m vllm.entrypoints.openai.api_server \
  --model meta-llama/Llama-3.1-70B-Instruct \
  --port 8000 \
  --tensor-parallel-size 4
```

### Text Generation Inference (TGI)

HuggingFace's production-ready inference server.

**Configuration:**
```env
TGI_API_BASE=http://tgi-server:8080
```

**Deployment:**
```bash
docker run --gpus all \
  -p 8080:80 \
  ghcr.io/huggingface/text-generation-inference:latest \
  --model-id mistralai/Mixtral-8x7B-Instruct-v0.1
```

### Ollama

Easy local model deployment.

**Configuration:**
```env
OLLAMA_API_BASE=http://localhost:11434
```

**Deployment:**
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull model
ollama pull llama3.1:70b

# Model available at localhost:11434
```

**Usage:**
```json
{
  "model": "ollama/llama3.1:70b",
  "messages": [...]
}
```

---

## Configuration Examples

### Multi-Provider Setup

```env
# Public APIs
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...

# Enterprise Cloud
AZURE_API_KEY=...
AZURE_API_BASE=https://your-resource.openai.azure.com/

# AWS Bedrock
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1

# Self-Hosted
VLLM_API_BASE=http://gpu-server:8000/v1
OLLAMA_API_BASE=http://localhost:11434
```

### Provider Fallback

Configure fallback providers for high availability:

```python
# Client code with fallback
models = ["gpt-4o", "azure/gpt-4o", "claude-3-5-sonnet"]

for model in models:
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[...]
        )
        break
    except:
        continue
```

---

## Pricing Reference

Alfred normalizes all costs to unified **Org-Credits** (1 USD = 100 credits).

### Public APIs

| Provider | Model | Input $/1K | Output $/1K | Credits/1K (avg) |
|----------|-------|------------|-------------|------------------|
| OpenAI | gpt-4o | $0.0025 | $0.01 | 0.625 |
| OpenAI | gpt-4o-mini | $0.00015 | $0.0006 | 0.0375 |
| OpenAI | o1 | $0.015 | $0.06 | 3.75 |
| Anthropic | claude-3-5-sonnet | $0.003 | $0.015 | 0.9 |
| Anthropic | claude-3-5-haiku | $0.00025 | $0.00125 | 0.075 |
| Google | gemini-1.5-pro | $0.00125 | $0.005 | 0.3125 |
| Google | gemini-1.5-flash | $0.000075 | $0.0003 | 0.01875 |

### Enterprise Cloud

| Provider | Model | Input $/1K | Output $/1K | Notes |
|----------|-------|------------|-------------|-------|
| Azure | gpt-4o | Same as OpenAI | | Enterprise pricing available |
| Bedrock | Claude 3 Sonnet | $0.003 | $0.015 | On-demand |
| Bedrock | Llama 3.1 70B | $0.00099 | $0.00099 | On-demand |

### Self-Hosted (Estimated)

| Setup | Model | Est. $/1K tokens | Credits/1K |
|-------|-------|------------------|------------|
| vLLM (H100) | Llama 3.1 70B | ~$0.0001 | 0.01 |
| vLLM (A100) | Llama 3.1 8B | ~$0.00005 | 0.005 |
| Ollama (local) | Llama 3.1 8B | ~$0 | 0.001 |

*Self-hosted costs are infrastructure-dependent*

---

## Model Selection Guide

### By Use Case

| Use Case | Recommended Models |
|----------|-------------------|
| General Chat | gpt-4o-mini, claude-3-5-haiku |
| Complex Reasoning | o1, claude-3-5-sonnet |
| Long Documents | gemini-1.5-pro (1M context) |
| Code Generation | claude-3-5-sonnet, gpt-4o |
| Cost-Sensitive | gpt-4o-mini, gemini-1.5-flash |
| Privacy-Critical | Self-hosted Llama 3.1 |

### By Budget

| Budget Level | Strategy |
|--------------|----------|
| Low | gpt-4o-mini, gemini-1.5-flash, self-hosted |
| Medium | gpt-4o, claude-3-5-sonnet |
| High | o1, claude-3-opus, gpt-4-turbo-128k |

---

*See also: [Architecture](ARCHITECTURE.md) | [API Reference](API.md) | [Deployment](DEPLOYMENT.md)*
