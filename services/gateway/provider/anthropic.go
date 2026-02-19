/*
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L2
Logic:       Anthropic provider connector implementing the Provider
             interface. Maps OpenAI-compatible requests to
             Anthropic's Messages API format.
Root Cause:  Sprint task T027 — Anthropic provider connector.
Context:     Anthropic uses different auth (x-api-key header)
             and request schema (messages API).
Suitability: L2 model for well-documented Anthropic API.
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
	anthropicBaseURL  = "https://api.anthropic.com/v1"
	anthropicVersion  = "2023-06-01"
)

// AnthropicProvider implements the Provider interface for Anthropic.
type AnthropicProvider struct {
	config ProviderConfig
	client *http.Client
}

// anthropicRequest represents an Anthropic Messages API request.
type anthropicRequest struct {
	Model       string              `json:"model"`
	MaxTokens   int                 `json:"max_tokens"`
	Messages    []anthropicMessage  `json:"messages"`
	System      string              `json:"system,omitempty"`
	Temperature *float64            `json:"temperature,omitempty"`
	TopP        *float64            `json:"top_p,omitempty"`
	Stream      bool                `json:"stream,omitempty"`
	StopSeqs    []string            `json:"stop_sequences,omitempty"`
	Tools       []AnthropicTool     `json:"tools,omitempty"`
	ToolChoice  *AnthropicToolChoice `json:"tool_choice,omitempty"`
}

type anthropicMessage struct {
	Role    string      `json:"role"`
	Content interface{} `json:"content"` // string or []AnthropicContentBlock
}

// anthropicResponse represents an Anthropic Messages API response.
type anthropicResponse struct {
	ID      string `json:"id"`
	Type    string `json:"type"`
	Role    string `json:"role"`
	Model   string `json:"model"`
	Content []struct {
		Type  string          `json:"type"`            // "text" or "tool_use"
		Text  string          `json:"text,omitempty"`  // for type="text"
		ID    string          `json:"id,omitempty"`    // for type="tool_use"
		Name  string          `json:"name,omitempty"`  // for type="tool_use"
		Input json.RawMessage `json:"input,omitempty"` // for type="tool_use"
	} `json:"content"`
	StopReason string `json:"stop_reason"`
	Usage      struct {
		InputTokens  int `json:"input_tokens"`
		OutputTokens int `json:"output_tokens"`
	} `json:"usage"`
}

// NewAnthropicProvider creates a new Anthropic provider connector.
func NewAnthropicProvider(cfg ProviderConfig) *AnthropicProvider {
	if cfg.BaseURL == "" {
		cfg.BaseURL = anthropicBaseURL
	}
	if cfg.Timeout == 0 {
		cfg.Timeout = 120 * time.Second
	}

	transport := &http.Transport{
		MaxIdleConns:        50,
		MaxIdleConnsPerHost: 10,
		IdleConnTimeout:     90 * time.Second,
	}

	return &AnthropicProvider{
		config: cfg,
		client: &http.Client{
			Transport: transport,
			Timeout:   cfg.Timeout,
		},
	}
}

func (p *AnthropicProvider) Name() string { return "anthropic" }

func (p *AnthropicProvider) Models() []string {
	if len(p.config.Models) > 0 {
		return p.config.Models
	}
	return []string{
		"claude-3-opus-20240229", "claude-3-sonnet-20240229",
		"claude-3-haiku-20240307", "claude-3-5-sonnet-20241022",
	}
}

func (p *AnthropicProvider) ChatCompletion(ctx context.Context, req *ChatRequest) (*ChatResponse, error) {
	aReq := p.convertRequest(req)
	aReq.Stream = false

	body, err := json.Marshal(aReq)
	if err != nil {
		return nil, fmt.Errorf("marshal request: %w", err)
	}

	httpReq, err := http.NewRequestWithContext(ctx, http.MethodPost, p.config.BaseURL+"/messages", bytes.NewReader(body))
	if err != nil {
		return nil, fmt.Errorf("create request: %w", err)
	}
	p.setHeaders(httpReq)

	resp, err := p.client.Do(httpReq)
	if err != nil {
		return nil, fmt.Errorf("anthropic request failed: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		respBody, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("anthropic returned status %d: %s", resp.StatusCode, string(respBody))
	}

	var aResp anthropicResponse
	if err := json.NewDecoder(resp.Body).Decode(&aResp); err != nil {
		return nil, fmt.Errorf("decode response: %w", err)
	}

	return p.convertResponse(&aResp), nil
}

func (p *AnthropicProvider) ChatCompletionStream(ctx context.Context, req *ChatRequest) (Stream, error) {
	aReq := p.convertRequest(req)
	aReq.Stream = true

	body, err := json.Marshal(aReq)
	if err != nil {
		return nil, fmt.Errorf("marshal request: %w", err)
	}

	httpReq, err := http.NewRequestWithContext(ctx, http.MethodPost, p.config.BaseURL+"/messages", bytes.NewReader(body))
	if err != nil {
		return nil, fmt.Errorf("create request: %w", err)
	}
	p.setHeaders(httpReq)

	resp, err := p.client.Do(httpReq)
	if err != nil {
		return nil, fmt.Errorf("anthropic stream request failed: %w", err)
	}

	if resp.StatusCode != http.StatusOK {
		respBody, _ := io.ReadAll(resp.Body)
		resp.Body.Close()
		return nil, fmt.Errorf("anthropic returned status %d: %s", resp.StatusCode, string(respBody))
	}

	return NewHTTPStream(resp), nil
}

func (p *AnthropicProvider) Embeddings(ctx context.Context, req *EmbeddingsRequest) (*EmbeddingsResponse, error) {
	return nil, fmt.Errorf("anthropic does not support embeddings")
}

func (p *AnthropicProvider) HealthCheck(ctx context.Context) HealthStatus {
	start := time.Now()
	// Anthropic doesn't have a models endpoint — use a minimal request
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

	// Any non-5xx response indicates the service is reachable
	healthy := resp.StatusCode < 500
	errMsg := ""
	if !healthy {
		errMsg = fmt.Sprintf("status %d", resp.StatusCode)
	}
	return HealthStatus{Healthy: healthy, Latency: latency, LastCheck: time.Now(), Error: errMsg}
}

func (p *AnthropicProvider) convertRequest(req *ChatRequest) *anthropicRequest {
	aReq := &anthropicRequest{
		Model:       req.Model,
		MaxTokens:   1024,
		Temperature: req.Temperature,
		TopP:        req.TopP,
		StopSeqs:    req.Stop,
	}

	if req.MaxTokens != nil {
		aReq.MaxTokens = *req.MaxTokens
	}

	// Convert tools if present (T017 function calling pass-through).
	if len(req.Tools) > 0 {
		aReq.Tools = ConvertToolsToAnthropic(req.Tools)
		aReq.ToolChoice = ConvertToolChoiceToAnthropic(req.ToolChoice)
	}

	for _, msg := range req.Messages {
		if msg.Role == "system" {
			if content, ok := msg.Content.(string); ok {
				aReq.System = content
			}
			continue
		}

		// Handle tool result messages (role="tool" in OpenAI format).
		if msg.Role == "tool" && msg.ToolCallID != "" {
			content := ""
			if c, ok := msg.Content.(string); ok {
				content = c
			}
			aReq.Messages = append(aReq.Messages, anthropicMessage{
				Role: "user",
				Content: []map[string]interface{}{
					{
						"type":        "tool_result",
						"tool_use_id": msg.ToolCallID,
						"content":     content,
					},
				},
			})
			continue
		}

		// Handle assistant messages with tool calls.
		if msg.Role == "assistant" && len(msg.ToolCalls) > 0 {
			blocks := make([]map[string]interface{}, 0, len(msg.ToolCalls)+1)
			if content, ok := msg.Content.(string); ok && content != "" {
				blocks = append(blocks, map[string]interface{}{
					"type": "text",
					"text": content,
				})
			}
			for _, tc := range msg.ToolCalls {
				var input json.RawMessage
				_ = json.Unmarshal([]byte(tc.Function.Arguments), &input)
				blocks = append(blocks, map[string]interface{}{
					"type":  "tool_use",
					"id":    tc.ID,
					"name":  tc.Function.Name,
					"input": input,
				})
			}
			aReq.Messages = append(aReq.Messages, anthropicMessage{
				Role:    "assistant",
				Content: blocks,
			})
			continue
		}

		// Standard text messages.
		content := ""
		if c, ok := msg.Content.(string); ok {
			content = c
		}
		aReq.Messages = append(aReq.Messages, anthropicMessage{
			Role:    msg.Role,
			Content: content,
		})
	}

	return aReq
}

func (p *AnthropicProvider) convertResponse(aResp *anthropicResponse) *ChatResponse {
	// Parse content blocks for both text and tool_use.
	var textContent string
	var toolCalls []ToolCall

	for _, block := range aResp.Content {
		switch block.Type {
		case "text":
			textContent += block.Text
		case "tool_use":
			args, _ := json.Marshal(block.Input)
			toolCalls = append(toolCalls, ToolCall{
				ID:   block.ID,
				Type: "function",
				Function: FunctionCall{
					Name:      block.Name,
					Arguments: string(args),
				},
			})
		}
	}

	finishReason := mapStopReason(aResp.StopReason)
	if len(toolCalls) > 0 && aResp.StopReason == "tool_use" {
		finishReason = "tool_calls"
	}

	return &ChatResponse{
		ID:      aResp.ID,
		Object:  "chat.completion",
		Created: time.Now().Unix(),
		Model:   aResp.Model,
		Choices: []Choice{
			{
				Index: 0,
				Message: ChatMessage{
					Role:      "assistant",
					Content:   textContent,
					ToolCalls: toolCalls,
				},
				FinishReason: finishReason,
			},
		},
		Usage: Usage{
			PromptTokens:     aResp.Usage.InputTokens,
			CompletionTokens: aResp.Usage.OutputTokens,
			TotalTokens:      aResp.Usage.InputTokens + aResp.Usage.OutputTokens,
		},
	}
}

func mapStopReason(reason string) string {
	switch reason {
	case "end_turn":
		return "stop"
	case "max_tokens":
		return "length"
	case "stop_sequence":
		return "stop"
	default:
		return reason
	}
}

func (p *AnthropicProvider) setHeaders(req *http.Request) {
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("x-api-key", p.config.APIKey)
	req.Header.Set("anthropic-version", anthropicVersion)
	for k, v := range p.config.Headers {
		req.Header.Set(k, v)
	}
}
