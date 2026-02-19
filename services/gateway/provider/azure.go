/*
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L2
Logic:       Azure OpenAI provider connector. Uses the same
             OpenAI API format but with different auth (api-key
             header) and URL pattern (resource/deployment).
Root Cause:  Sprint task T031 — Azure OpenAI provider connector.
Context:     Azure OpenAI is OpenAI-compatible but with different
             base URL format and api-key authentication header.
Suitability: L2 for OpenAI-compatible API with auth variation.
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

// AzureOpenAIProvider implements the Provider interface for Azure OpenAI.
// Azure uses a different URL pattern: {resource}.openai.azure.com/openai/deployments/{deployment}
type AzureOpenAIProvider struct {
	config     ProviderConfig
	client     *http.Client
	apiVersion string
}

// NewAzureOpenAIProvider creates a new Azure OpenAI provider connector.
// BaseURL should be: https://{resource-name}.openai.azure.com
func NewAzureOpenAIProvider(cfg ProviderConfig) *AzureOpenAIProvider {
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

	apiVersion := "2024-08-01-preview"
	if v, ok := cfg.Headers["api-version"]; ok {
		apiVersion = v
	}

	return &AzureOpenAIProvider{
		config: cfg,
		client: &http.Client{
			Transport: transport,
			Timeout:   cfg.Timeout,
		},
		apiVersion: apiVersion,
	}
}

func (p *AzureOpenAIProvider) Name() string { return "azure" }

func (p *AzureOpenAIProvider) Models() []string {
	if len(p.config.Models) > 0 {
		return p.config.Models
	}
	return []string{"gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-4"}
}

// deploymentURL builds the Azure deployment URL for a given model/deployment.
// Azure format: {base_url}/openai/deployments/{model}/chat/completions?api-version={version}
func (p *AzureOpenAIProvider) deploymentURL(model, endpoint string) string {
	return fmt.Sprintf("%s/openai/deployments/%s/%s?api-version=%s",
		p.config.BaseURL, model, endpoint, p.apiVersion)
}

func (p *AzureOpenAIProvider) ChatCompletion(ctx context.Context, req *ChatRequest) (*ChatResponse, error) {
	req.Stream = false

	// Azure doesn't use the model field in the body — the deployment name is in the URL
	bodyReq := *req
	bodyReq.Model = "" // Remove model from body for Azure

	body, err := json.Marshal(bodyReq)
	if err != nil {
		return nil, fmt.Errorf("marshal request: %w", err)
	}

	url := p.deploymentURL(req.Model, "chat/completions")
	httpReq, err := http.NewRequestWithContext(ctx, http.MethodPost, url, bytes.NewReader(body))
	if err != nil {
		return nil, fmt.Errorf("create request: %w", err)
	}
	p.setHeaders(httpReq)

	resp, err := p.client.Do(httpReq)
	if err != nil {
		return nil, fmt.Errorf("azure openai request failed: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		respBody, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("azure openai returned status %d: %s", resp.StatusCode, string(respBody))
	}

	var chatResp ChatResponse
	if err := json.NewDecoder(resp.Body).Decode(&chatResp); err != nil {
		return nil, fmt.Errorf("decode response: %w", err)
	}
	return &chatResp, nil
}

func (p *AzureOpenAIProvider) ChatCompletionStream(ctx context.Context, req *ChatRequest) (Stream, error) {
	req.Stream = true

	bodyReq := *req
	bodyReq.Model = ""

	body, err := json.Marshal(bodyReq)
	if err != nil {
		return nil, fmt.Errorf("marshal request: %w", err)
	}

	url := p.deploymentURL(req.Model, "chat/completions")
	httpReq, err := http.NewRequestWithContext(ctx, http.MethodPost, url, bytes.NewReader(body))
	if err != nil {
		return nil, fmt.Errorf("create request: %w", err)
	}
	p.setHeaders(httpReq)

	resp, err := p.client.Do(httpReq)
	if err != nil {
		return nil, fmt.Errorf("azure openai stream request failed: %w", err)
	}

	if resp.StatusCode != http.StatusOK {
		respBody, _ := io.ReadAll(resp.Body)
		resp.Body.Close()
		return nil, fmt.Errorf("azure openai returned status %d: %s", resp.StatusCode, string(respBody))
	}

	return NewHTTPStream(resp), nil
}

func (p *AzureOpenAIProvider) Embeddings(ctx context.Context, req *EmbeddingsRequest) (*EmbeddingsResponse, error) {
	body, err := json.Marshal(req)
	if err != nil {
		return nil, fmt.Errorf("marshal request: %w", err)
	}

	url := p.deploymentURL(req.Model, "embeddings")
	httpReq, err := http.NewRequestWithContext(ctx, http.MethodPost, url, bytes.NewReader(body))
	if err != nil {
		return nil, fmt.Errorf("create request: %w", err)
	}
	p.setHeaders(httpReq)

	resp, err := p.client.Do(httpReq)
	if err != nil {
		return nil, fmt.Errorf("azure openai embeddings request failed: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		respBody, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("azure openai returned status %d: %s", resp.StatusCode, string(respBody))
	}

	var embResp EmbeddingsResponse
	if err := json.NewDecoder(resp.Body).Decode(&embResp); err != nil {
		return nil, fmt.Errorf("decode response: %w", err)
	}
	return &embResp, nil
}

func (p *AzureOpenAIProvider) HealthCheck(ctx context.Context) HealthStatus {
	start := time.Now()
	// Azure health check: list deployments
	url := fmt.Sprintf("%s/openai/models?api-version=%s", p.config.BaseURL, p.apiVersion)

	httpReq, err := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
	if err != nil {
		return HealthStatus{Healthy: false, Error: err.Error(), LastCheck: time.Now()}
	}
	p.setHeaders(httpReq)

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

func (p *AzureOpenAIProvider) setHeaders(req *http.Request) {
	req.Header.Set("Content-Type", "application/json")
	// Azure uses api-key header instead of Bearer token
	req.Header.Set("api-key", p.config.APIKey)
	for k, v := range p.config.Headers {
		if k != "api-version" { // Already handled in URL
			req.Header.Set(k, v)
		}
	}
}
