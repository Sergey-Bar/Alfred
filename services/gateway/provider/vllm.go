/*
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L2
Logic:       vLLM self-hosted connector implementing the Provider
             interface. vLLM exposes a fully OpenAI-compatible
             API server, so this is a thin wrapper identical in
             structure to the Ollama connector but pointed at a
             vLLM server with appropriate defaults.
Root Cause:  Sprint task T038 — vLLM self-hosted connector.
Context:     vLLM is a popular high-throughput serving engine
             for self-hosted models. Supports OpenAI-compatible
             /v1/chat/completions and /v1/embeddings endpoints.
Suitability: L2 — OpenAI-compatible API, minimal translation.
──────────────────────────────────────────────────────────────
*/

package provider

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"
)

const vllmDefaultBaseURL = "http://localhost:8000"

// VLLMProvider implements the Provider interface for vLLM.
type VLLMProvider struct {
	config ProviderConfig
	client *http.Client
}

// NewVLLMProvider creates a new vLLM provider connector.
func NewVLLMProvider(cfg ProviderConfig) *VLLMProvider {
	if cfg.BaseURL == "" {
		cfg.BaseURL = vllmDefaultBaseURL
	}
	if cfg.Timeout == 0 {
		cfg.Timeout = 120 * time.Second
	}
	if cfg.MaxRetries == 0 {
		cfg.MaxRetries = 2
	}

	transport := &http.Transport{
		MaxIdleConns:        100,
		MaxIdleConnsPerHost: 20,
		IdleConnTimeout:     90 * time.Second,
	}

	return &VLLMProvider{
		config: cfg,
		client: &http.Client{
			Transport: transport,
			Timeout:   cfg.Timeout,
		},
	}
}

func (p *VLLMProvider) Name() string { return "vllm" }

func (p *VLLMProvider) Models() []string {
	if len(p.config.Models) > 0 {
		return p.config.Models
	}
	return []string{
		"meta-llama/Meta-Llama-3.1-70B-Instruct",
		"meta-llama/Meta-Llama-3.1-8B-Instruct",
		"mistralai/Mistral-7B-Instruct-v0.3",
		"Qwen/Qwen2-72B-Instruct",
	}
}

func (p *VLLMProvider) ChatCompletion(ctx context.Context, req *ChatRequest) (*ChatResponse, error) {
	req.Stream = false
	body, err := json.Marshal(req)
	if err != nil {
		return nil, fmt.Errorf("marshal request: %w", err)
	}

	httpReq, err := http.NewRequestWithContext(ctx, http.MethodPost, p.config.BaseURL+"/v1/chat/completions", bytes.NewReader(body))
	if err != nil {
		return nil, fmt.Errorf("create request: %w", err)
	}
	p.setHeaders(httpReq)

	resp, err := p.client.Do(httpReq)
	if err != nil {
		return nil, fmt.Errorf("vllm request failed: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		respBody, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("vllm returned status %d: %s", resp.StatusCode, string(respBody))
	}

	var chatResp ChatResponse
	if err := json.NewDecoder(resp.Body).Decode(&chatResp); err != nil {
		return nil, fmt.Errorf("decode response: %w", err)
	}
	return &chatResp, nil
}

func (p *VLLMProvider) ChatCompletionStream(ctx context.Context, req *ChatRequest) (Stream, error) {
	req.Stream = true
	body, err := json.Marshal(req)
	if err != nil {
		return nil, fmt.Errorf("marshal request: %w", err)
	}

	httpReq, err := http.NewRequestWithContext(ctx, http.MethodPost, p.config.BaseURL+"/v1/chat/completions", bytes.NewReader(body))
	if err != nil {
		return nil, fmt.Errorf("create request: %w", err)
	}
	p.setHeaders(httpReq)

	resp, err := p.client.Do(httpReq)
	if err != nil {
		return nil, fmt.Errorf("vllm stream request failed: %w", err)
	}

	if resp.StatusCode != http.StatusOK {
		respBody, _ := io.ReadAll(resp.Body)
		resp.Body.Close()
		return nil, fmt.Errorf("vllm returned status %d: %s", resp.StatusCode, string(respBody))
	}

	return NewHTTPStream(resp), nil
}

func (p *VLLMProvider) Embeddings(ctx context.Context, req *EmbeddingsRequest) (*EmbeddingsResponse, error) {
	body, err := json.Marshal(req)
	if err != nil {
		return nil, fmt.Errorf("marshal request: %w", err)
	}

	httpReq, err := http.NewRequestWithContext(ctx, http.MethodPost, p.config.BaseURL+"/v1/embeddings", bytes.NewReader(body))
	if err != nil {
		return nil, fmt.Errorf("create request: %w", err)
	}
	p.setHeaders(httpReq)

	resp, err := p.client.Do(httpReq)
	if err != nil {
		return nil, fmt.Errorf("vllm embeddings request failed: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		respBody, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("vllm returned status %d: %s", resp.StatusCode, string(respBody))
	}

	var embResp EmbeddingsResponse
	if err := json.NewDecoder(resp.Body).Decode(&embResp); err != nil {
		return nil, fmt.Errorf("decode response: %w", err)
	}
	return &embResp, nil
}

func (p *VLLMProvider) HealthCheck(ctx context.Context) HealthStatus {
	start := time.Now()
	// vLLM serves health at /health or /v1/models
	httpReq, err := http.NewRequestWithContext(ctx, http.MethodGet, p.config.BaseURL+"/health", nil)
	if err != nil {
		return HealthStatus{Healthy: false, Error: err.Error(), LastCheck: time.Now()}
	}

	resp, err := p.client.Do(httpReq)
	latency := time.Since(start)
	if err != nil {
		return HealthStatus{Healthy: false, Latency: latency, Error: err.Error(), LastCheck: time.Now()}
	}
	defer resp.Body.Close()

	healthy := resp.StatusCode == http.StatusOK
	errMsg := ""
	if !healthy {
		errMsg = fmt.Sprintf("status %d", resp.StatusCode)
	}
	return HealthStatus{Healthy: healthy, Latency: latency, LastCheck: time.Now(), Error: errMsg}
}

func (p *VLLMProvider) setHeaders(req *http.Request) {
	req.Header.Set("Content-Type", "application/json")
	if p.config.APIKey != "" {
		req.Header.Set("Authorization", "Bearer "+p.config.APIKey)
	}
	for k, v := range p.config.Headers {
		req.Header.Set(k, v)
	}
}
