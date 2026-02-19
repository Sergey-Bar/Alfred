/*
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L2
Logic:       Cohere provider connector implementing the Provider
             interface.  Cohere uses a different request/response
             format (command-r models, embed-v3) — this adapter
             translates OpenAI-compatible requests to Cohere's
             Chat API and back.
Root Cause:  Sprint task T033 — Cohere provider connector.
Context:     Adds Cohere (Command R+, Embed v3) to Alfred's
             multi-provider routing pool.
Suitability: L2 — well-documented API with clear mapping.
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

const cohereBaseURL = "https://api.cohere.com/v1"

// CohereProvider implements the Provider interface for Cohere.
type CohereProvider struct {
	config ProviderConfig
	client *http.Client
}

// NewCohereProvider creates a new Cohere provider connector.
func NewCohereProvider(cfg ProviderConfig) *CohereProvider {
	if cfg.BaseURL == "" {
		cfg.BaseURL = cohereBaseURL
	}
	if cfg.Timeout == 0 {
		cfg.Timeout = 120 * time.Second
	}
	if cfg.MaxRetries == 0 {
		cfg.MaxRetries = 2
	}

	transport := &http.Transport{
		MaxIdleConns:        50,
		MaxIdleConnsPerHost: 10,
		IdleConnTimeout:     90 * time.Second,
	}

	return &CohereProvider{
		config: cfg,
		client: &http.Client{
			Transport: transport,
			Timeout:   cfg.Timeout,
		},
	}
}

func (p *CohereProvider) Name() string { return "cohere" }

func (p *CohereProvider) Models() []string {
	if len(p.config.Models) > 0 {
		return p.config.Models
	}
	return []string{
		"command-r-plus", "command-r", "command-light",
		"command", "embed-english-v3.0", "embed-multilingual-v3.0",
		"embed-english-light-v3.0", "embed-multilingual-light-v3.0",
	}
}

// ─── Cohere-specific request/response types ─────────────────

type cohereChatRequest struct {
	Model       string              `json:"model"`
	Message     string              `json:"message"`
	ChatHistory []cohereChatMessage `json:"chat_history,omitempty"`
	Stream      bool                `json:"stream,omitempty"`
	MaxTokens   *int                `json:"max_tokens,omitempty"`
	Temperature *float64            `json:"temperature,omitempty"`
	TopP        *float64            `json:"p,omitempty"`
	StopSeqs    []string            `json:"stop_sequences,omitempty"`
}

type cohereChatMessage struct {
	Role    string `json:"role"` // USER or CHATBOT
	Message string `json:"message"`
}

type cohereChatResponse struct {
	ResponseID    string                 `json:"response_id"`
	Text          string                 `json:"text"`
	GenerationID  string                 `json:"generation_id"`
	TokenCount    *cohereTokenCount      `json:"token_count,omitempty"`
	Meta          map[string]interface{} `json:"meta,omitempty"`
	FinishReason  string                 `json:"finish_reason"`
}

type cohereTokenCount struct {
	PromptTokens   int `json:"prompt_tokens"`
	ResponseTokens int `json:"response_tokens"`
	TotalTokens    int `json:"total_tokens"`
}

type cohereEmbedRequest struct {
	Texts     []string `json:"texts"`
	Model     string   `json:"model"`
	InputType string   `json:"input_type"` // search_document, search_query, classification, clustering
}

type cohereEmbedResponse struct {
	ID         string      `json:"id"`
	Embeddings [][]float64 `json:"embeddings"`
	Texts      []string    `json:"texts"`
	Meta       *struct {
		BilledUnits *struct {
			InputTokens int `json:"input_tokens"`
		} `json:"billed_units,omitempty"`
	} `json:"meta,omitempty"`
}

// ─── Provider interface implementation ──────────────────────

func (p *CohereProvider) ChatCompletion(ctx context.Context, req *ChatRequest) (*ChatResponse, error) {
	cohReq := p.toCohereChat(req)
	cohReq.Stream = false

	body, err := json.Marshal(cohReq)
	if err != nil {
		return nil, fmt.Errorf("marshal cohere request: %w", err)
	}

	httpReq, err := http.NewRequestWithContext(ctx, http.MethodPost, p.config.BaseURL+"/chat", bytes.NewReader(body))
	if err != nil {
		return nil, fmt.Errorf("create request: %w", err)
	}
	p.setHeaders(httpReq)

	resp, err := p.client.Do(httpReq)
	if err != nil {
		return nil, fmt.Errorf("cohere request failed: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		respBody, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("cohere returned status %d: %s", resp.StatusCode, string(respBody))
	}

	var cohResp cohereChatResponse
	if err := json.NewDecoder(resp.Body).Decode(&cohResp); err != nil {
		return nil, fmt.Errorf("decode cohere response: %w", err)
	}

	return p.toOpenAIResponse(&cohResp, req.Model), nil
}

func (p *CohereProvider) ChatCompletionStream(ctx context.Context, req *ChatRequest) (Stream, error) {
	cohReq := p.toCohereChat(req)
	cohReq.Stream = true

	body, err := json.Marshal(cohReq)
	if err != nil {
		return nil, fmt.Errorf("marshal cohere request: %w", err)
	}

	httpReq, err := http.NewRequestWithContext(ctx, http.MethodPost, p.config.BaseURL+"/chat", bytes.NewReader(body))
	if err != nil {
		return nil, fmt.Errorf("create request: %w", err)
	}
	p.setHeaders(httpReq)

	resp, err := p.client.Do(httpReq)
	if err != nil {
		return nil, fmt.Errorf("cohere stream request failed: %w", err)
	}

	if resp.StatusCode != http.StatusOK {
		respBody, _ := io.ReadAll(resp.Body)
		resp.Body.Close()
		return nil, fmt.Errorf("cohere returned status %d: %s", resp.StatusCode, string(respBody))
	}

	return NewHTTPStream(resp), nil
}

func (p *CohereProvider) Embeddings(ctx context.Context, req *EmbeddingsRequest) (*EmbeddingsResponse, error) {
	texts := inputToStrings(req.Input)

	cohReq := cohereEmbedRequest{
		Texts:     texts,
		Model:     req.Model,
		InputType: "search_document",
	}

	body, err := json.Marshal(cohReq)
	if err != nil {
		return nil, fmt.Errorf("marshal cohere embed request: %w", err)
	}

	httpReq, err := http.NewRequestWithContext(ctx, http.MethodPost, p.config.BaseURL+"/embed", bytes.NewReader(body))
	if err != nil {
		return nil, fmt.Errorf("create request: %w", err)
	}
	p.setHeaders(httpReq)

	resp, err := p.client.Do(httpReq)
	if err != nil {
		return nil, fmt.Errorf("cohere embed request failed: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		respBody, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("cohere returned status %d: %s", resp.StatusCode, string(respBody))
	}

	var cohResp cohereEmbedResponse
	if err := json.NewDecoder(resp.Body).Decode(&cohResp); err != nil {
		return nil, fmt.Errorf("decode cohere embed response: %w", err)
	}

	data := make([]EmbeddingData, len(cohResp.Embeddings))
	for i, emb := range cohResp.Embeddings {
		data[i] = EmbeddingData{
			Object:    "embedding",
			Embedding: emb,
			Index:     i,
		}
	}

	promptTokens := 0
	if cohResp.Meta != nil && cohResp.Meta.BilledUnits != nil {
		promptTokens = cohResp.Meta.BilledUnits.InputTokens
	}

	return &EmbeddingsResponse{
		Object: "list",
		Data:   data,
		Model:  req.Model,
		Usage: EmbeddingsUsage{
			PromptTokens: promptTokens,
			TotalTokens:  promptTokens,
		},
	}, nil
}

func (p *CohereProvider) HealthCheck(ctx context.Context) HealthStatus {
	start := time.Now()
	httpReq, err := http.NewRequestWithContext(ctx, http.MethodGet, p.config.BaseURL+"/models", nil)
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

// ─── Helpers ────────────────────────────────────────────────

func (p *CohereProvider) setHeaders(req *http.Request) {
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer "+p.config.APIKey)
	req.Header.Set("X-Client-Name", "alfred-gateway")
	for k, v := range p.config.Headers {
		req.Header.Set(k, v)
	}
}

// toCohereChat converts an OpenAI-compatible ChatRequest to Cohere's format.
func (p *CohereProvider) toCohereChat(req *ChatRequest) cohereChatRequest {
	var history []cohereChatMessage
	var lastMessage string

	for i, msg := range req.Messages {
		content := ""
		switch v := msg.Content.(type) {
		case string:
			content = v
		default:
			b, _ := json.Marshal(v)
			content = string(b)
		}

		if i == len(req.Messages)-1 && msg.Role == "user" {
			lastMessage = content
		} else {
			role := "USER"
			if msg.Role == "assistant" {
				role = "CHATBOT"
			} else if msg.Role == "system" {
				role = "SYSTEM"
			}
			history = append(history, cohereChatMessage{Role: role, Message: content})
		}
	}

	return cohereChatRequest{
		Model:       req.Model,
		Message:     lastMessage,
		ChatHistory: history,
		MaxTokens:   req.MaxTokens,
		Temperature: req.Temperature,
		TopP:        req.TopP,
		StopSeqs:    req.Stop,
	}
}

// toOpenAIResponse converts a Cohere response to OpenAI-compatible format.
func (p *CohereProvider) toOpenAIResponse(cohResp *cohereChatResponse, model string) *ChatResponse {
	usage := Usage{}
	if cohResp.TokenCount != nil {
		usage.PromptTokens = cohResp.TokenCount.PromptTokens
		usage.CompletionTokens = cohResp.TokenCount.ResponseTokens
		usage.TotalTokens = cohResp.TokenCount.TotalTokens
	}

	return &ChatResponse{
		ID:      cohResp.ResponseID,
		Object:  "chat.completion",
		Created: time.Now().Unix(),
		Model:   model,
		Choices: []Choice{
			{
				Index: 0,
				Message: ChatMessage{
					Role:    "assistant",
					Content: cohResp.Text,
				},
				FinishReason: p.mapFinishReason(cohResp.FinishReason),
			},
		},
		Usage: usage,
	}
}

func (p *CohereProvider) mapFinishReason(reason string) string {
	switch reason {
	case "COMPLETE":
		return "stop"
	case "MAX_TOKENS":
		return "length"
	case "ERROR", "ERROR_TOXIC", "ERROR_LIMIT":
		return "stop"
	default:
		return "stop"
	}
}

// inputToStrings converts the embeddings Input field to a string slice.
func inputToStrings(input interface{}) []string {
	switch v := input.(type) {
	case string:
		return []string{v}
	case []interface{}:
		result := make([]string, 0, len(v))
		for _, item := range v {
			if s, ok := item.(string); ok {
				result = append(result, s)
			}
		}
		return result
	case []string:
		return v
	default:
		return []string{fmt.Sprintf("%v", input)}
	}
}
