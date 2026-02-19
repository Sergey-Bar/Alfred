/*
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L2
Logic:       Mistral provider connector — OpenAI-compatible API
             with different base URL and Bearer auth.
Root Cause:  Sprint task T034 — Mistral connector.
Context:     OpenAI-compatible; reuses OpenAI request format.
Suitability: L2 — straightforward adaptation of OpenAI pattern.
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
	mistralBaseURL = "https://api.mistral.ai/v1"
)

// MistralProvider implements the Provider interface for Mistral AI.
type MistralProvider struct {
	config ProviderConfig
	client *http.Client
}

// NewMistralProvider creates a new Mistral provider connector.
func NewMistralProvider(cfg ProviderConfig) *MistralProvider {
	if cfg.BaseURL == "" {
		cfg.BaseURL = mistralBaseURL
	}
	return &MistralProvider{
		config: cfg,
		client: &http.Client{Timeout: time.Duration(cfg.TimeoutSec) * time.Second},
	}
}

func (p *MistralProvider) Name() string { return "mistral" }

func (p *MistralProvider) Models() []string {
	return []string{
		"mistral-large-latest",
		"mistral-medium-latest",
		"mistral-small-latest",
		"codestral-latest",
		"mistral-embed",
		"open-mistral-nemo",
		"open-mixtral-8x22b",
	}
}

func (p *MistralProvider) HealthCheck(ctx context.Context) HealthStatus {
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

func (p *MistralProvider) ChatCompletion(ctx context.Context, req ChatCompletionRequest) (*ChatCompletionResponse, error) {
	body, err := json.Marshal(req)
	if err != nil {
		return nil, fmt.Errorf("mistral: marshal request: %w", err)
	}

	httpReq, err := http.NewRequestWithContext(ctx, http.MethodPost, p.config.BaseURL+"/chat/completions", bytes.NewReader(body))
	if err != nil {
		return nil, fmt.Errorf("mistral: create request: %w", err)
	}
	httpReq.Header.Set("Content-Type", "application/json")
	httpReq.Header.Set("Authorization", "Bearer "+p.config.APIKey)

	resp, err := p.client.Do(httpReq)
	if err != nil {
		return nil, fmt.Errorf("mistral: request failed: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		respBody, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("mistral: API error %d: %s", resp.StatusCode, string(respBody))
	}

	var result ChatCompletionResponse
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, fmt.Errorf("mistral: decode response: %w", err)
	}
	return &result, nil
}

func (p *MistralProvider) ChatCompletionStream(ctx context.Context, req ChatCompletionRequest) (*HTTPStream, error) {
	req.Stream = true
	body, err := json.Marshal(req)
	if err != nil {
		return nil, fmt.Errorf("mistral: marshal stream request: %w", err)
	}

	httpReq, err := http.NewRequestWithContext(ctx, http.MethodPost, p.config.BaseURL+"/chat/completions", bytes.NewReader(body))
	if err != nil {
		return nil, fmt.Errorf("mistral: create stream request: %w", err)
	}
	httpReq.Header.Set("Content-Type", "application/json")
	httpReq.Header.Set("Authorization", "Bearer "+p.config.APIKey)

	resp, err := p.client.Do(httpReq)
	if err != nil {
		return nil, fmt.Errorf("mistral: stream request failed: %w", err)
	}

	if resp.StatusCode != http.StatusOK {
		respBody, _ := io.ReadAll(resp.Body)
		resp.Body.Close()
		return nil, fmt.Errorf("mistral: stream API error %d: %s", resp.StatusCode, string(respBody))
	}

	return &HTTPStream{
		Reader:     resp.Body,
		StatusCode: resp.StatusCode,
		Headers:    resp.Header,
	}, nil
}

func (p *MistralProvider) Embeddings(ctx context.Context, req EmbeddingRequest) (*EmbeddingResponse, error) {
	body, err := json.Marshal(req)
	if err != nil {
		return nil, fmt.Errorf("mistral: marshal embedding request: %w", err)
	}

	httpReq, err := http.NewRequestWithContext(ctx, http.MethodPost, p.config.BaseURL+"/embeddings", bytes.NewReader(body))
	if err != nil {
		return nil, fmt.Errorf("mistral: create embedding request: %w", err)
	}
	httpReq.Header.Set("Content-Type", "application/json")
	httpReq.Header.Set("Authorization", "Bearer "+p.config.APIKey)

	resp, err := p.client.Do(httpReq)
	if err != nil {
		return nil, fmt.Errorf("mistral: embedding request failed: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		respBody, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("mistral: embedding API error %d: %s", resp.StatusCode, string(respBody))
	}

	var result EmbeddingResponse
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, fmt.Errorf("mistral: decode embedding response: %w", err)
	}
	return &result, nil
}
