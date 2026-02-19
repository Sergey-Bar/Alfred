/*
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L1
Logic:       Together AI connector — fully OpenAI-compatible.
             Only changes: base URL and model list.
Root Cause:  Sprint task T035 — Together AI connector.
Context:     OpenAI-compatible; minimal adaptation needed.
Suitability: L1 — boilerplate adapter over OpenAI format.
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

const (
	togetherBaseURL = "https://api.together.xyz/v1"
)

// TogetherProvider implements the Provider interface for Together AI.
type TogetherProvider struct {
	config ProviderConfig
	client *http.Client
}

// NewTogetherProvider creates a new Together AI connector.
func NewTogetherProvider(cfg ProviderConfig) *TogetherProvider {
	if cfg.BaseURL == "" {
		cfg.BaseURL = togetherBaseURL
	}
	return &TogetherProvider{
		config: cfg,
		client: &http.Client{Timeout: time.Duration(cfg.TimeoutSec) * time.Second},
	}
}

func (p *TogetherProvider) Name() string { return "together" }

func (p *TogetherProvider) Models() []string {
	return []string{
		"meta-llama/Llama-3.3-70B-Instruct-Turbo",
		"meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
		"meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
		"meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
		"mistralai/Mixtral-8x22B-Instruct-v0.1",
		"Qwen/Qwen2.5-72B-Instruct-Turbo",
		"deepseek-ai/DeepSeek-R1",
		"google/gemma-2-27b-it",
	}
}

func (p *TogetherProvider) HealthCheck(ctx context.Context) HealthStatus {
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, p.config.BaseURL+"/models", nil)
	if err != nil {
		return HealthStatus{Healthy: false, Message: err.Error()}
	}
	req.Header.Set("Authorization", "Bearer "+p.config.APIKey)

	resp, err := p.client.Do(req)
	if err != nil {
		return HealthStatus{Healthy: false, Message: err.Error()}
	}
	defer resp.Body.Close()

	return HealthStatus{
		Healthy: resp.StatusCode == http.StatusOK,
		Message: fmt.Sprintf("status=%d", resp.StatusCode),
	}
}

func (p *TogetherProvider) ChatCompletion(ctx context.Context, req ChatCompletionRequest) (*ChatCompletionResponse, error) {
	body, err := json.Marshal(req)
	if err != nil {
		return nil, fmt.Errorf("together: marshal: %w", err)
	}

	httpReq, err := http.NewRequestWithContext(ctx, http.MethodPost, p.config.BaseURL+"/chat/completions", bytes.NewReader(body))
	if err != nil {
		return nil, fmt.Errorf("together: create request: %w", err)
	}
	httpReq.Header.Set("Content-Type", "application/json")
	httpReq.Header.Set("Authorization", "Bearer "+p.config.APIKey)

	resp, err := p.client.Do(httpReq)
	if err != nil {
		return nil, fmt.Errorf("together: request failed: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		respBody, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("together: API error %d: %s", resp.StatusCode, string(respBody))
	}

	var result ChatCompletionResponse
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, fmt.Errorf("together: decode: %w", err)
	}
	return &result, nil
}

func (p *TogetherProvider) ChatCompletionStream(ctx context.Context, req ChatCompletionRequest) (*HTTPStream, error) {
	req.Stream = true
	body, err := json.Marshal(req)
	if err != nil {
		return nil, fmt.Errorf("together: marshal stream: %w", err)
	}

	httpReq, err := http.NewRequestWithContext(ctx, http.MethodPost, p.config.BaseURL+"/chat/completions", bytes.NewReader(body))
	if err != nil {
		return nil, fmt.Errorf("together: create stream request: %w", err)
	}
	httpReq.Header.Set("Content-Type", "application/json")
	httpReq.Header.Set("Authorization", "Bearer "+p.config.APIKey)

	resp, err := p.client.Do(httpReq)
	if err != nil {
		return nil, fmt.Errorf("together: stream failed: %w", err)
	}

	if resp.StatusCode != http.StatusOK {
		respBody, _ := io.ReadAll(resp.Body)
		resp.Body.Close()
		return nil, fmt.Errorf("together: stream error %d: %s", resp.StatusCode, string(respBody))
	}

	return &HTTPStream{
		Reader:     resp.Body,
		StatusCode: resp.StatusCode,
		Headers:    resp.Header,
	}, nil
}

func (p *TogetherProvider) Embeddings(ctx context.Context, req EmbeddingRequest) (*EmbeddingResponse, error) {
	body, err := json.Marshal(req)
	if err != nil {
		return nil, fmt.Errorf("together: marshal embedding: %w", err)
	}

	httpReq, err := http.NewRequestWithContext(ctx, http.MethodPost, p.config.BaseURL+"/embeddings", bytes.NewReader(body))
	if err != nil {
		return nil, fmt.Errorf("together: create embedding request: %w", err)
	}
	httpReq.Header.Set("Content-Type", "application/json")
	httpReq.Header.Set("Authorization", "Bearer "+p.config.APIKey)

	resp, err := p.client.Do(httpReq)
	if err != nil {
		return nil, fmt.Errorf("together: embedding failed: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		respBody, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("together: embedding error %d: %s", resp.StatusCode, string(respBody))
	}

	var result EmbeddingResponse
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, fmt.Errorf("together: decode embedding: %w", err)
	}
	return &result, nil
}
