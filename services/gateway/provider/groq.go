/*
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L1
Logic:       Groq connector — OpenAI-compatible inference API.
             Ultra-fast LPU inference for open models.
Root Cause:  Sprint task T036 — Groq connector.
Context:     OpenAI-compatible; minimal adaptation. Some models
             are free tier (tracked by metering engine IsFree).
Suitability: L1 — boilerplate adapter.
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
	groqBaseURL = "https://api.groq.com/openai/v1"
)

// GroqProvider implements the Provider interface for Groq.
type GroqProvider struct {
	config ProviderConfig
	client *http.Client
}

// NewGroqProvider creates a new Groq provider connector.
func NewGroqProvider(cfg ProviderConfig) *GroqProvider {
	if cfg.BaseURL == "" {
		cfg.BaseURL = groqBaseURL
	}
	return &GroqProvider{
		config: cfg,
		client: &http.Client{Timeout: time.Duration(cfg.TimeoutSec) * time.Second},
	}
}

func (p *GroqProvider) Name() string { return "groq" }

func (p *GroqProvider) Models() []string {
	return []string{
		"llama-3.3-70b-versatile",
		"llama-3.1-8b-instant",
		"llama-3.2-90b-vision-preview",
		"mixtral-8x7b-32768",
		"gemma2-9b-it",
		"deepseek-r1-distill-llama-70b",
	}
}

func (p *GroqProvider) HealthCheck(ctx context.Context) HealthStatus {
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

func (p *GroqProvider) ChatCompletion(ctx context.Context, req ChatCompletionRequest) (*ChatCompletionResponse, error) {
	body, err := json.Marshal(req)
	if err != nil {
		return nil, fmt.Errorf("groq: marshal: %w", err)
	}

	httpReq, err := http.NewRequestWithContext(ctx, http.MethodPost, p.config.BaseURL+"/chat/completions", bytes.NewReader(body))
	if err != nil {
		return nil, fmt.Errorf("groq: create request: %w", err)
	}
	httpReq.Header.Set("Content-Type", "application/json")
	httpReq.Header.Set("Authorization", "Bearer "+p.config.APIKey)

	resp, err := p.client.Do(httpReq)
	if err != nil {
		return nil, fmt.Errorf("groq: request failed: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		respBody, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("groq: API error %d: %s", resp.StatusCode, string(respBody))
	}

	var result ChatCompletionResponse
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, fmt.Errorf("groq: decode: %w", err)
	}
	return &result, nil
}

func (p *GroqProvider) ChatCompletionStream(ctx context.Context, req ChatCompletionRequest) (*HTTPStream, error) {
	req.Stream = true
	body, err := json.Marshal(req)
	if err != nil {
		return nil, fmt.Errorf("groq: marshal stream: %w", err)
	}

	httpReq, err := http.NewRequestWithContext(ctx, http.MethodPost, p.config.BaseURL+"/chat/completions", bytes.NewReader(body))
	if err != nil {
		return nil, fmt.Errorf("groq: create stream request: %w", err)
	}
	httpReq.Header.Set("Content-Type", "application/json")
	httpReq.Header.Set("Authorization", "Bearer "+p.config.APIKey)

	resp, err := p.client.Do(httpReq)
	if err != nil {
		return nil, fmt.Errorf("groq: stream failed: %w", err)
	}

	if resp.StatusCode != http.StatusOK {
		respBody, _ := io.ReadAll(resp.Body)
		resp.Body.Close()
		return nil, fmt.Errorf("groq: stream error %d: %s", resp.StatusCode, string(respBody))
	}

	return &HTTPStream{
		Reader:     resp.Body,
		StatusCode: resp.StatusCode,
		Headers:    resp.Header,
	}, nil
}

func (p *GroqProvider) Embeddings(ctx context.Context, req EmbeddingRequest) (*EmbeddingResponse, error) {
	// Groq does not currently offer embeddings, but we implement the interface.
	return nil, fmt.Errorf("groq: embeddings not supported")
}
