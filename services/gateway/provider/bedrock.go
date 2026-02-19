/*
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L3
Logic:       AWS Bedrock provider connector implementing the
             Provider interface.  Bedrock uses AWS Signature V4
             auth, a different invoke endpoint per model, and
             a distinct streaming format (event-stream).  This
             adapter handles the translation layer.
Root Cause:  Sprint task T032 — AWS Bedrock provider connector.
Context:     Bedrock is a key enterprise provider; many orgs
             require it for data residency / compliance.
Suitability: L3 — AWS SigV4 auth + different streaming format
             requires careful implementation.
──────────────────────────────────────────────────────────────
*/

package provider

import (
	"bytes"
	"context"
	"crypto/hmac"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"
	"time"
)

// BedrockProvider implements the Provider interface for AWS Bedrock.
type BedrockProvider struct {
	config    ProviderConfig
	region    string
	accessKey string
	secretKey string
	client    *http.Client
}

// BedrockConfig holds AWS-specific configuration.
type BedrockConfig struct {
	ProviderConfig
	Region    string `json:"region"`
	AccessKey string `json:"-"`
	SecretKey string `json:"-"`
}

// NewBedrockProvider creates a new AWS Bedrock provider connector.
func NewBedrockProvider(cfg BedrockConfig) *BedrockProvider {
	region := cfg.Region
	if region == "" {
		region = "us-east-1"
	}
	if cfg.BaseURL == "" {
		cfg.BaseURL = fmt.Sprintf("https://bedrock-runtime.%s.amazonaws.com", region)
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

	return &BedrockProvider{
		config:    cfg.ProviderConfig,
		region:    region,
		accessKey: cfg.AccessKey,
		secretKey: cfg.SecretKey,
		client: &http.Client{
			Transport: transport,
			Timeout:   cfg.Timeout,
		},
	}
}

func (p *BedrockProvider) Name() string { return "bedrock" }

func (p *BedrockProvider) Models() []string {
	if len(p.config.Models) > 0 {
		return p.config.Models
	}
	return []string{
		"anthropic.claude-3-5-sonnet-20241022-v2:0",
		"anthropic.claude-3-haiku-20240307-v1:0",
		"anthropic.claude-3-opus-20240229-v1:0",
		"amazon.titan-text-express-v1",
		"amazon.titan-text-lite-v1",
		"amazon.titan-embed-text-v2:0",
		"meta.llama3-1-70b-instruct-v1:0",
		"meta.llama3-1-8b-instruct-v1:0",
		"cohere.command-r-plus-v1:0",
		"mistral.mistral-large-2407-v1:0",
	}
}

// ─── Bedrock request/response types ─────────────────────────

type bedrockInvokeBody struct {
	Messages      []bedrockMessage `json:"messages"`
	System        string           `json:"system,omitempty"`
	MaxTokens     int              `json:"max_tokens,omitempty"`
	Temperature   *float64         `json:"temperature,omitempty"`
	TopP          *float64         `json:"top_p,omitempty"`
	StopSequences []string         `json:"stop_sequences,omitempty"`
	// Anthropic-on-Bedrock specific
	AnthropicVersion string `json:"anthropic_version,omitempty"`
}

type bedrockMessage struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}

type bedrockResponse struct {
	ID      string          `json:"id"`
	Type    string          `json:"type"`
	Role    string          `json:"role"`
	Content []bedrockBlock  `json:"content"`
	Model   string          `json:"model"`
	Usage   *bedrockUsage   `json:"usage,omitempty"`
	Stop    string          `json:"stop_reason,omitempty"`
}

type bedrockBlock struct {
	Type string `json:"type"`
	Text string `json:"text"`
}

type bedrockUsage struct {
	InputTokens  int `json:"input_tokens"`
	OutputTokens int `json:"output_tokens"`
}

// ─── Provider interface implementation ──────────────────────

func (p *BedrockProvider) ChatCompletion(ctx context.Context, req *ChatRequest) (*ChatResponse, error) {
	modelID := req.Model
	body := p.buildInvokeBody(req)

	payload, err := json.Marshal(body)
	if err != nil {
		return nil, fmt.Errorf("marshal bedrock request: %w", err)
	}

	endpoint := fmt.Sprintf("%s/model/%s/invoke", p.config.BaseURL, modelID)
	httpReq, err := http.NewRequestWithContext(ctx, http.MethodPost, endpoint, bytes.NewReader(payload))
	if err != nil {
		return nil, fmt.Errorf("create request: %w", err)
	}
	p.signRequest(httpReq, payload)

	resp, err := p.client.Do(httpReq)
	if err != nil {
		return nil, fmt.Errorf("bedrock request failed: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		respBody, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("bedrock returned status %d: %s", resp.StatusCode, string(respBody))
	}

	var brResp bedrockResponse
	if err := json.NewDecoder(resp.Body).Decode(&brResp); err != nil {
		return nil, fmt.Errorf("decode bedrock response: %w", err)
	}

	return p.toOpenAIResponse(&brResp, modelID), nil
}

func (p *BedrockProvider) ChatCompletionStream(ctx context.Context, req *ChatRequest) (Stream, error) {
	modelID := req.Model
	body := p.buildInvokeBody(req)

	payload, err := json.Marshal(body)
	if err != nil {
		return nil, fmt.Errorf("marshal bedrock request: %w", err)
	}

	endpoint := fmt.Sprintf("%s/model/%s/invoke-with-response-stream", p.config.BaseURL, modelID)
	httpReq, err := http.NewRequestWithContext(ctx, http.MethodPost, endpoint, bytes.NewReader(payload))
	if err != nil {
		return nil, fmt.Errorf("create request: %w", err)
	}
	p.signRequest(httpReq, payload)

	resp, err := p.client.Do(httpReq)
	if err != nil {
		return nil, fmt.Errorf("bedrock stream request failed: %w", err)
	}

	if resp.StatusCode != http.StatusOK {
		respBody, _ := io.ReadAll(resp.Body)
		resp.Body.Close()
		return nil, fmt.Errorf("bedrock returned status %d: %s", resp.StatusCode, string(respBody))
	}

	return NewHTTPStream(resp), nil
}

func (p *BedrockProvider) Embeddings(ctx context.Context, req *EmbeddingsRequest) (*EmbeddingsResponse, error) {
	texts := inputToStrings(req.Input)
	modelID := req.Model

	// Bedrock Titan embeddings: one text at a time
	var allData []EmbeddingData
	totalTokens := 0

	for i, text := range texts {
		embedBody := map[string]interface{}{
			"inputText": text,
		}

		payload, err := json.Marshal(embedBody)
		if err != nil {
			return nil, fmt.Errorf("marshal bedrock embed request: %w", err)
		}

		endpoint := fmt.Sprintf("%s/model/%s/invoke", p.config.BaseURL, modelID)
		httpReq, err := http.NewRequestWithContext(ctx, http.MethodPost, endpoint, bytes.NewReader(payload))
		if err != nil {
			return nil, fmt.Errorf("create request: %w", err)
		}
		p.signRequest(httpReq, payload)

		resp, err := p.client.Do(httpReq)
		if err != nil {
			return nil, fmt.Errorf("bedrock embed request failed: %w", err)
		}

		if resp.StatusCode != http.StatusOK {
			respBody, _ := io.ReadAll(resp.Body)
			resp.Body.Close()
			return nil, fmt.Errorf("bedrock returned status %d: %s", resp.StatusCode, string(respBody))
		}

		var embedResp struct {
			Embedding      []float64 `json:"embedding"`
			InputTextTokenCount int  `json:"inputTextTokenCount"`
		}
		if err := json.NewDecoder(resp.Body).Decode(&embedResp); err != nil {
			resp.Body.Close()
			return nil, fmt.Errorf("decode bedrock embed response: %w", err)
		}
		resp.Body.Close()

		allData = append(allData, EmbeddingData{
			Object:    "embedding",
			Embedding: embedResp.Embedding,
			Index:     i,
		})
		totalTokens += embedResp.InputTextTokenCount
	}

	return &EmbeddingsResponse{
		Object: "list",
		Data:   allData,
		Model:  modelID,
		Usage: EmbeddingsUsage{
			PromptTokens: totalTokens,
			TotalTokens:  totalTokens,
		},
	}, nil
}

func (p *BedrockProvider) HealthCheck(ctx context.Context) HealthStatus {
	start := time.Now()
	// List foundation models to verify connectivity
	endpoint := strings.Replace(p.config.BaseURL, "bedrock-runtime", "bedrock", 1) + "/foundation-models"
	httpReq, err := http.NewRequestWithContext(ctx, http.MethodGet, endpoint, nil)
	if err != nil {
		return HealthStatus{Healthy: false, Error: err.Error(), LastCheck: time.Now()}
	}
	p.signRequest(httpReq, nil)

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

func (p *BedrockProvider) buildInvokeBody(req *ChatRequest) bedrockInvokeBody {
	var messages []bedrockMessage
	var system string

	for _, msg := range req.Messages {
		content := ""
		switch v := msg.Content.(type) {
		case string:
			content = v
		default:
			b, _ := json.Marshal(v)
			content = string(b)
		}

		if msg.Role == "system" {
			system = content
			continue
		}
		messages = append(messages, bedrockMessage{
			Role:    msg.Role,
			Content: content,
		})
	}

	maxTokens := 4096
	if req.MaxTokens != nil {
		maxTokens = *req.MaxTokens
	}

	return bedrockInvokeBody{
		Messages:         messages,
		System:           system,
		MaxTokens:        maxTokens,
		Temperature:      req.Temperature,
		TopP:             req.TopP,
		StopSequences:    req.Stop,
		AnthropicVersion: "bedrock-2023-05-31",
	}
}

func (p *BedrockProvider) toOpenAIResponse(brResp *bedrockResponse, model string) *ChatResponse {
	text := ""
	for _, block := range brResp.Content {
		if block.Type == "text" {
			text += block.Text
		}
	}

	usage := Usage{}
	if brResp.Usage != nil {
		usage.PromptTokens = brResp.Usage.InputTokens
		usage.CompletionTokens = brResp.Usage.OutputTokens
		usage.TotalTokens = brResp.Usage.InputTokens + brResp.Usage.OutputTokens
	}

	finishReason := "stop"
	if brResp.Stop == "max_tokens" {
		finishReason = "length"
	}

	return &ChatResponse{
		ID:      brResp.ID,
		Object:  "chat.completion",
		Created: time.Now().Unix(),
		Model:   model,
		Choices: []Choice{
			{
				Index: 0,
				Message: ChatMessage{
					Role:    "assistant",
					Content: text,
				},
				FinishReason: finishReason,
			},
		},
		Usage: usage,
	}
}

// signRequest applies AWS Signature V4 to the HTTP request.
// This is a simplified implementation for Bedrock.
func (p *BedrockProvider) signRequest(req *http.Request, payload []byte) {
	now := time.Now().UTC()
	dateStamp := now.Format("20060102")
	amzDate := now.Format("20060102T150405Z")

	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("X-Amz-Date", amzDate)

	if len(payload) == 0 {
		payload = []byte{}
	}

	// Canonical request components
	payloadHash := sha256Hex(payload)
	req.Header.Set("X-Amz-Content-Sha256", payloadHash)

	service := "bedrock"
	if strings.Contains(req.URL.Host, "bedrock-runtime") {
		service = "bedrock-runtime"
	}

	credentialScope := fmt.Sprintf("%s/%s/%s/aws4_request", dateStamp, p.region, service)

	signedHeaders := "content-type;host;x-amz-content-sha256;x-amz-date"
	canonicalHeaders := fmt.Sprintf("content-type:%s\nhost:%s\nx-amz-content-sha256:%s\nx-amz-date:%s\n",
		req.Header.Get("Content-Type"),
		req.URL.Host,
		payloadHash,
		amzDate,
	)

	canonicalRequest := fmt.Sprintf("%s\n%s\n%s\n%s\n%s\n%s",
		req.Method,
		req.URL.Path,
		req.URL.RawQuery,
		canonicalHeaders,
		signedHeaders,
		payloadHash,
	)

	stringToSign := fmt.Sprintf("AWS4-HMAC-SHA256\n%s\n%s\n%s",
		amzDate,
		credentialScope,
		sha256Hex([]byte(canonicalRequest)),
	)

	// Derive signing key
	kDate := hmacSHA256([]byte("AWS4"+p.secretKey), []byte(dateStamp))
	kRegion := hmacSHA256(kDate, []byte(p.region))
	kService := hmacSHA256(kRegion, []byte(service))
	kSigning := hmacSHA256(kService, []byte("aws4_request"))

	signature := hex.EncodeToString(hmacSHA256(kSigning, []byte(stringToSign)))

	authHeader := fmt.Sprintf("AWS4-HMAC-SHA256 Credential=%s/%s, SignedHeaders=%s, Signature=%s",
		p.accessKey,
		credentialScope,
		signedHeaders,
		signature,
	)
	req.Header.Set("Authorization", authHeader)
}

func sha256Hex(data []byte) string {
	h := sha256.Sum256(data)
	return hex.EncodeToString(h[:])
}

func hmacSHA256(key, data []byte) []byte {
	h := hmac.New(sha256.New, key)
	h.Write(data)
	return h.Sum(nil)
}
