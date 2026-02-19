/*
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L2
Logic:       Google Gemini provider connector using the Generative
             Language API (AI Studio REST). Translates OpenAI-format
             requests to Gemini's generateContent format and back.
Root Cause:  Sprint task T030 — Google Gemini provider connector.
Context:     Gemini uses different request/response schema than
             OpenAI. Requires role mapping (assistant→model),
             different content structure, and separate streaming
             format.
Suitability: L2 for well-documented API with schema translation.
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
	"strings"
	"time"
)

const (
	geminiBaseURL = "https://generativelanguage.googleapis.com/v1beta"
)

// GeminiProvider implements the Provider interface for Google Gemini.
type GeminiProvider struct {
	config ProviderConfig
	client *http.Client
}

// NewGeminiProvider creates a new Google Gemini provider connector.
func NewGeminiProvider(cfg ProviderConfig) *GeminiProvider {
	if cfg.BaseURL == "" {
		cfg.BaseURL = geminiBaseURL
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

	return &GeminiProvider{
		config: cfg,
		client: &http.Client{
			Transport: transport,
			Timeout:   cfg.Timeout,
		},
	}
}

func (p *GeminiProvider) Name() string { return "google" }

func (p *GeminiProvider) Models() []string {
	if len(p.config.Models) > 0 {
		return p.config.Models
	}
	return []string{
		"gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash",
		"gemini-2.0-flash-lite", "text-embedding-004",
	}
}

// --- Gemini-specific request/response types ---

type geminiRequest struct {
	Contents         []geminiContent        `json:"contents"`
	GenerationConfig *geminiGenerationConfig `json:"generationConfig,omitempty"`
	SafetySettings   []geminiSafetySetting  `json:"safetySettings,omitempty"`
}

type geminiContent struct {
	Role  string       `json:"role"`
	Parts []geminiPart `json:"parts"`
}

type geminiPart struct {
	Text string `json:"text,omitempty"`
}

type geminiGenerationConfig struct {
	MaxOutputTokens *int     `json:"maxOutputTokens,omitempty"`
	Temperature     *float64 `json:"temperature,omitempty"`
	TopP            *float64 `json:"topP,omitempty"`
	StopSequences   []string `json:"stopSequences,omitempty"`
}

type geminiSafetySetting struct {
	Category  string `json:"category"`
	Threshold string `json:"threshold"`
}

type geminiResponse struct {
	Candidates    []geminiCandidate    `json:"candidates"`
	UsageMetadata *geminiUsageMetadata `json:"usageMetadata,omitempty"`
}

type geminiCandidate struct {
	Content      geminiContent `json:"content"`
	FinishReason string        `json:"finishReason"`
	Index        int           `json:"index"`
}

type geminiUsageMetadata struct {
	PromptTokenCount     int `json:"promptTokenCount"`
	CandidatesTokenCount int `json:"candidatesTokenCount"`
	TotalTokenCount      int `json:"totalTokenCount"`
}

// --- Translation helpers ---

func openAIRoleToGemini(role string) string {
	switch role {
	case "assistant":
		return "model"
	case "system":
		return "user" // Gemini handles system prompts via system_instruction or as user context
	default:
		return role
	}
}

func geminiRoleToOpenAI(role string) string {
	switch role {
	case "model":
		return "assistant"
	default:
		return role
	}
}

func (p *GeminiProvider) toGeminiRequest(req *ChatRequest) geminiRequest {
	contents := make([]geminiContent, 0, len(req.Messages))
	for _, msg := range req.Messages {
		text := ""
		switch v := msg.Content.(type) {
		case string:
			text = v
		default:
			b, _ := json.Marshal(v)
			text = string(b)
		}

		contents = append(contents, geminiContent{
			Role:  openAIRoleToGemini(msg.Role),
			Parts: []geminiPart{{Text: text}},
		})
	}

	gemReq := geminiRequest{Contents: contents}
	if req.MaxTokens != nil || req.Temperature != nil || req.TopP != nil || len(req.Stop) > 0 {
		gemReq.GenerationConfig = &geminiGenerationConfig{
			MaxOutputTokens: req.MaxTokens,
			Temperature:     req.Temperature,
			TopP:            req.TopP,
			StopSequences:   req.Stop,
		}
	}
	return gemReq
}

func (p *GeminiProvider) toOpenAIResponse(gemResp *geminiResponse, model string) *ChatResponse {
	choices := make([]Choice, 0, len(gemResp.Candidates))
	for _, c := range gemResp.Candidates {
		text := ""
		for _, part := range c.Content.Parts {
			text += part.Text
		}

		finishReason := strings.ToLower(c.FinishReason)
		if finishReason == "stop" || finishReason == "" {
			finishReason = "stop"
		} else if finishReason == "max_tokens" {
			finishReason = "length"
		}

		choices = append(choices, Choice{
			Index: c.Index,
			Message: ChatMessage{
				Role:    geminiRoleToOpenAI(c.Content.Role),
				Content: text,
			},
			FinishReason: finishReason,
		})
	}

	usage := Usage{}
	if gemResp.UsageMetadata != nil {
		usage.PromptTokens = gemResp.UsageMetadata.PromptTokenCount
		usage.CompletionTokens = gemResp.UsageMetadata.CandidatesTokenCount
		usage.TotalTokens = gemResp.UsageMetadata.TotalTokenCount
	}

	return &ChatResponse{
		ID:      fmt.Sprintf("gemini-%d", time.Now().UnixNano()),
		Object:  "chat.completion",
		Created: time.Now().Unix(),
		Model:   model,
		Choices: choices,
		Usage:   usage,
	}
}

// --- Provider interface implementation ---

func (p *GeminiProvider) ChatCompletion(ctx context.Context, req *ChatRequest) (*ChatResponse, error) {
	gemReq := p.toGeminiRequest(req)
	body, err := json.Marshal(gemReq)
	if err != nil {
		return nil, fmt.Errorf("marshal gemini request: %w", err)
	}

	model := req.Model
	url := fmt.Sprintf("%s/models/%s:generateContent?key=%s", p.config.BaseURL, model, p.config.APIKey)

	httpReq, err := http.NewRequestWithContext(ctx, http.MethodPost, url, bytes.NewReader(body))
	if err != nil {
		return nil, fmt.Errorf("create request: %w", err)
	}
	httpReq.Header.Set("Content-Type", "application/json")

	resp, err := p.client.Do(httpReq)
	if err != nil {
		return nil, fmt.Errorf("gemini request failed: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		respBody, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("gemini returned status %d: %s", resp.StatusCode, string(respBody))
	}

	var gemResp geminiResponse
	if err := json.NewDecoder(resp.Body).Decode(&gemResp); err != nil {
		return nil, fmt.Errorf("decode gemini response: %w", err)
	}

	return p.toOpenAIResponse(&gemResp, model), nil
}

func (p *GeminiProvider) ChatCompletionStream(ctx context.Context, req *ChatRequest) (Stream, error) {
	gemReq := p.toGeminiRequest(req)
	body, err := json.Marshal(gemReq)
	if err != nil {
		return nil, fmt.Errorf("marshal gemini request: %w", err)
	}

	model := req.Model
	url := fmt.Sprintf("%s/models/%s:streamGenerateContent?key=%s&alt=sse", p.config.BaseURL, model, p.config.APIKey)

	httpReq, err := http.NewRequestWithContext(ctx, http.MethodPost, url, bytes.NewReader(body))
	if err != nil {
		return nil, fmt.Errorf("create request: %w", err)
	}
	httpReq.Header.Set("Content-Type", "application/json")

	resp, err := p.client.Do(httpReq)
	if err != nil {
		return nil, fmt.Errorf("gemini stream request failed: %w", err)
	}

	if resp.StatusCode != http.StatusOK {
		respBody, _ := io.ReadAll(resp.Body)
		resp.Body.Close()
		return nil, fmt.Errorf("gemini returned status %d: %s", resp.StatusCode, string(respBody))
	}

	return NewHTTPStream(resp), nil
}

func (p *GeminiProvider) Embeddings(ctx context.Context, req *EmbeddingsRequest) (*EmbeddingsResponse, error) {
	// Gemini uses a different embeddings endpoint
	input := ""
	switch v := req.Input.(type) {
	case string:
		input = v
	case []interface{}:
		if len(v) > 0 {
			if s, ok := v[0].(string); ok {
				input = s
			}
		}
	}

	gemEmbReq := map[string]interface{}{
		"model": "models/" + req.Model,
		"content": map[string]interface{}{
			"parts": []map[string]string{
				{"text": input},
			},
		},
	}

	body, err := json.Marshal(gemEmbReq)
	if err != nil {
		return nil, fmt.Errorf("marshal embedding request: %w", err)
	}

	model := req.Model
	url := fmt.Sprintf("%s/models/%s:embedContent?key=%s", p.config.BaseURL, model, p.config.APIKey)

	httpReq, err := http.NewRequestWithContext(ctx, http.MethodPost, url, bytes.NewReader(body))
	if err != nil {
		return nil, fmt.Errorf("create request: %w", err)
	}
	httpReq.Header.Set("Content-Type", "application/json")

	resp, err := p.client.Do(httpReq)
	if err != nil {
		return nil, fmt.Errorf("gemini embeddings request failed: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		respBody, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("gemini returned status %d: %s", resp.StatusCode, string(respBody))
	}

	// Parse Gemini embedding response
	var gemEmbResp struct {
		Embedding struct {
			Values []float64 `json:"values"`
		} `json:"embedding"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&gemEmbResp); err != nil {
		return nil, fmt.Errorf("decode embedding response: %w", err)
	}

	return &EmbeddingsResponse{
		Object: "list",
		Data: []EmbeddingData{{
			Object:    "embedding",
			Embedding: gemEmbResp.Embedding.Values,
			Index:     0,
		}},
		Model: model,
		Usage: EmbeddingsUsage{
			PromptTokens: 0, // Gemini doesn't always return token counts for embeddings
			TotalTokens:  0,
		},
	}, nil
}

func (p *GeminiProvider) HealthCheck(ctx context.Context) HealthStatus {
	start := time.Now()
	url := fmt.Sprintf("%s/models?key=%s", p.config.BaseURL, p.config.APIKey)

	httpReq, err := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
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
