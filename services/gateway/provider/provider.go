/*
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L3
Logic:       Provider abstraction layer defining the Go interface
             for all LLM provider connectors. Includes provider
             registry, model detection, and health status tracking.
Root Cause:  Sprint task T025 — Provider interface / abstraction layer.
Context:     Interface design affects all downstream provider
             connectors (T026-T038). Must support streaming,
             non-streaming, embeddings, and function calling.
Suitability: L3 model for interface design affecting architecture.
──────────────────────────────────────────────────────────────
*/

package provider

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"
	"sync"
	"time"
)

// Provider defines the interface all LLM provider connectors must implement.
type Provider interface {
	// Name returns the provider identifier (e.g., "openai", "anthropic").
	Name() string

	// ChatCompletion sends a non-streaming chat completion request.
	ChatCompletion(ctx context.Context, req *ChatRequest) (*ChatResponse, error)

	// ChatCompletionStream sends a streaming chat completion request.
	// The caller must close the returned stream.
	ChatCompletionStream(ctx context.Context, req *ChatRequest) (Stream, error)

	// Embeddings generates embeddings for input text.
	Embeddings(ctx context.Context, req *EmbeddingsRequest) (*EmbeddingsResponse, error)

	// HealthCheck returns the current health status.
	HealthCheck(ctx context.Context) HealthStatus

	// Models returns the list of available models.
	Models() []string
}

// Stream represents a server-sent events stream from a provider.
type Stream interface {
	// Next returns the next chunk. Returns io.EOF when done.
	Next() ([]byte, error)
	// Close closes the stream.
	Close() error
}

// HealthStatus represents a provider's health state.
type HealthStatus struct {
	Healthy   bool      `json:"healthy"`
	Latency   time.Duration `json:"latency_ms"`
	LastCheck time.Time `json:"last_check"`
	Error     string    `json:"error,omitempty"`
}

// ChatRequest represents an OpenAI-compatible chat completion request.
type ChatRequest struct {
	Model       string        `json:"model"`
	Messages    []ChatMessage `json:"messages"`
	MaxTokens   *int          `json:"max_tokens,omitempty"`
	Temperature *float64      `json:"temperature,omitempty"`
	TopP        *float64      `json:"top_p,omitempty"`
	Stream      bool          `json:"stream,omitempty"`
	Stop        []string      `json:"stop,omitempty"`
	Tools       []Tool        `json:"tools,omitempty"`
	ToolChoice  interface{}   `json:"tool_choice,omitempty"`
	User        string        `json:"user,omitempty"`
	// Raw preserves the original request body for pass-through.
	Raw json.RawMessage `json:"-"`
}

// ChatMessage represents a single message in a chat completion request.
type ChatMessage struct {
	Role       string      `json:"role"`
	Content    interface{} `json:"content"`
	Name       string      `json:"name,omitempty"`
	ToolCalls  []ToolCall  `json:"tool_calls,omitempty"`
	ToolCallID string      `json:"tool_call_id,omitempty"`
}

// Tool represents a function/tool definition.
type Tool struct {
	Type     string   `json:"type"`
	Function Function `json:"function"`
}

// Function represents a function definition within a tool.
type Function struct {
	Name        string          `json:"name"`
	Description string          `json:"description,omitempty"`
	Parameters  json.RawMessage `json:"parameters,omitempty"`
}

// ToolCall represents a tool call in an assistant message.
type ToolCall struct {
	ID       string       `json:"id"`
	Type     string       `json:"type"`
	Function FunctionCall `json:"function"`
}

// FunctionCall represents a function call within a tool call.
type FunctionCall struct {
	Name      string `json:"name"`
	Arguments string `json:"arguments"`
}

// ChatResponse represents an OpenAI-compatible chat completion response.
type ChatResponse struct {
	ID      string   `json:"id"`
	Object  string   `json:"object"`
	Created int64    `json:"created"`
	Model   string   `json:"model"`
	Choices []Choice `json:"choices"`
	Usage   Usage    `json:"usage"`
}

// Choice represents a single choice in a chat completion response.
type Choice struct {
	Index        int         `json:"index"`
	Message      ChatMessage `json:"message"`
	FinishReason string      `json:"finish_reason"`
}

// Usage represents token usage statistics.
type Usage struct {
	PromptTokens     int `json:"prompt_tokens"`
	CompletionTokens int `json:"completion_tokens"`
	TotalTokens      int `json:"total_tokens"`
}

// EmbeddingsRequest represents an embeddings API request.
type EmbeddingsRequest struct {
	Model string      `json:"model"`
	Input interface{} `json:"input"`
	User  string      `json:"user,omitempty"`
}

// EmbeddingsResponse represents an embeddings API response.
type EmbeddingsResponse struct {
	Object string           `json:"object"`
	Data   []EmbeddingData  `json:"data"`
	Model  string           `json:"model"`
	Usage  EmbeddingsUsage  `json:"usage"`
}

// EmbeddingData represents a single embedding vector.
type EmbeddingData struct {
	Object    string    `json:"object"`
	Embedding []float64 `json:"embedding"`
	Index     int       `json:"index"`
}

// EmbeddingsUsage represents token usage for embeddings.
type EmbeddingsUsage struct {
	PromptTokens int `json:"prompt_tokens"`
	TotalTokens  int `json:"total_tokens"`
}

// ProviderConfig holds configuration for a provider connector.
type ProviderConfig struct {
	Name       string            `json:"name"`
	BaseURL    string            `json:"base_url"`
	APIKey     string            `json:"-"` // never serialized
	Models     []string          `json:"models"`
	Headers    map[string]string `json:"headers,omitempty"`
	Timeout    time.Duration     `json:"timeout"`
	MaxRetries int               `json:"max_retries"`
}

// Registry manages all registered provider connectors.
type Registry struct {
	mu        sync.RWMutex
	providers map[string]Provider
	health    map[string]HealthStatus
}

// NewRegistry creates a new provider registry.
func NewRegistry() *Registry {
	return &Registry{
		providers: make(map[string]Provider),
		health:    make(map[string]HealthStatus),
	}
}

// Register adds a provider to the registry.
func (r *Registry) Register(p Provider) {
	r.mu.Lock()
	defer r.mu.Unlock()
	r.providers[p.Name()] = p
}

// Get returns a provider by name.
func (r *Registry) Get(name string) (Provider, bool) {
	r.mu.RLock()
	defer r.mu.RUnlock()
	p, ok := r.providers[name]
	return p, ok
}

// GetForModel finds the appropriate provider for a given model name.
func (r *Registry) GetForModel(model string) (Provider, error) {
	providerName := DetectProvider(model)
	if providerName == "unknown" {
		return nil, fmt.Errorf("no provider found for model: %s", model)
	}
	p, ok := r.Get(providerName)
	if !ok {
		return nil, fmt.Errorf("provider %s not registered for model: %s", providerName, model)
	}
	return p, nil
}

// List returns all registered provider names.
func (r *Registry) List() []string {
	r.mu.RLock()
	defer r.mu.RUnlock()
	names := make([]string, 0, len(r.providers))
	for name := range r.providers {
		names = append(names, name)
	}
	return names
}

// HealthCheckAll runs health checks on all providers.
func (r *Registry) HealthCheckAll(ctx context.Context) map[string]HealthStatus {
	r.mu.RLock()
	providers := make(map[string]Provider, len(r.providers))
	for k, v := range r.providers {
		providers[k] = v
	}
	r.mu.RUnlock()

	results := make(map[string]HealthStatus)
	var wg sync.WaitGroup
	var mu sync.Mutex

	for name, p := range providers {
		wg.Add(1)
		go func(n string, prov Provider) {
			defer wg.Done()
			status := prov.HealthCheck(ctx)
			mu.Lock()
			results[n] = status
			mu.Unlock()
		}(name, p)
	}
	wg.Wait()

	r.mu.Lock()
	r.health = results
	r.mu.Unlock()

	return results
}

// DetectProvider maps a model name to a provider name.
func DetectProvider(model string) string {
	m := strings.ToLower(model)
	patterns := map[string][]string{
		"openai":    {"gpt", "o1", "o3", "davinci", "curie", "babbage", "text-embedding", "dall-e", "whisper", "tts"},
		"anthropic": {"claude"},
		"google":    {"gemini", "palm", "bison"},
		"azure":     {"azure/"},
		"mistral":   {"mistral", "mixtral", "codestral", "pixtral"},
		"meta":      {"llama"},
		"cohere":    {"command", "coral", "embed-"},
		"deepseek":  {"deepseek"},
		"together":  {"together/"},
		"groq":      {"groq/"},
		"bedrock":   {"anthropic.", "amazon.", "meta.", "cohere.", "mistral.", "ai21."},
		"ollama":    {"ollama/"},
		"vllm":      {"vllm/"},
	}
	for provider, prefixes := range patterns {
		for _, prefix := range prefixes {
			if strings.Contains(m, prefix) {
				return provider
			}
		}
	}
	return "unknown"
}

// HTTPStream implements a Stream backed by an HTTP response body.
type HTTPStream struct {
	body   io.ReadCloser
	reader *bufioReaderWrapper
}

type bufioReaderWrapper struct {
	body io.ReadCloser
	buf  []byte
}

func NewHTTPStream(resp *http.Response) *HTTPStream {
	return &HTTPStream{
		body: resp.Body,
	}
}

func (s *HTTPStream) Next() ([]byte, error) {
	buf := make([]byte, 4096)
	n, err := s.body.Read(buf)
	if n > 0 {
		return buf[:n], nil
	}
	if err != nil {
		return nil, err
	}
	return nil, io.EOF
}

func (s *HTTPStream) Close() error {
	return s.body.Close()
}
