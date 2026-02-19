/*
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L3
Logic:       HTTP proxy handler implementing POST /v1/chat/completions
             (non-streaming and SSE streaming), POST /v1/embeddings,
             and dry-run mode. Routes requests to the appropriate
             provider connector, injects X-Alfred-Model header,
             and supports per-provider configurable timeouts.
Root Cause:  Sprint tasks T014, T015, T016, T022, T024.
Context:     Core product endpoint — all AI traffic flows through
             this handler. Must handle streaming correctly with
             proper flushing and buffering.
Suitability: L3 model for SSE streaming in Go and proxy logic.
──────────────────────────────────────────────────────────────
*/

package handler

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"
	"time"

	"github.com/AlfredDev/alfred/services/gateway/middleware"
	"github.com/AlfredDev/alfred/services/gateway/provider"
	"github.com/rs/zerolog"
)

// ProxyHandler handles AI API proxy requests.
type ProxyHandler struct {
	logger   zerolog.Logger
	registry *provider.Registry
}

// NewProxyHandler creates a new proxy handler.
func NewProxyHandler(logger zerolog.Logger, registry *provider.Registry) *ProxyHandler {
	return &ProxyHandler{
		logger:   logger,
		registry: registry,
	}
}

// ChatCompletions handles POST /v1/chat/completions.
func (h *ProxyHandler) ChatCompletions(w http.ResponseWriter, r *http.Request) {
	start := time.Now()
	reqID := r.Header.Get("X-Request-ID")

	// Parse request body
	var req provider.ChatRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		h.writeError(w, http.StatusBadRequest, "invalid_request", "Failed to parse request body: "+err.Error())
		return
	}

	// Validate required fields
	if req.Model == "" {
		h.writeError(w, http.StatusBadRequest, "invalid_request", "Model field is required")
		return
	}
	if len(req.Messages) == 0 {
		h.writeError(w, http.StatusBadRequest, "invalid_request", "Messages field is required and must not be empty")
		return
	}

	// Validate tool definitions if present (T017).
	if len(req.Tools) > 0 {
		if err := provider.ValidateToolDefinitions(req.Tools); err != nil {
			h.writeError(w, http.StatusBadRequest, "invalid_tools", err.Error())
			return
		}
	}

	// Check for dry-run mode
	if r.Header.Get("X-Alfred-DryRun") == "true" {
		h.handleDryRun(w, &req)
		return
	}

	// Find the provider for this model
	prov, err := h.registry.GetForModel(req.Model)
	if err != nil {
		h.writeError(w, http.StatusBadRequest, "provider_not_found", err.Error())
		return
	}

	h.logger.Info().
		Str("req_id", reqID).
		Str("model", req.Model).
		Str("provider", prov.Name()).
		Bool("stream", req.Stream).
		Int("messages", len(req.Messages)).
		Msg("proxying chat completion")

	// Route to streaming or non-streaming handler
	if req.Stream {
		h.handleStreamingChat(w, r, prov, &req, start)
	} else {
		h.handleNonStreamingChat(w, r, prov, &req, start)
	}
}

// handleNonStreamingChat handles non-streaming chat completions (T014).
func (h *ProxyHandler) handleNonStreamingChat(w http.ResponseWriter, r *http.Request, prov provider.Provider, req *provider.ChatRequest, start time.Time) {
	resp, err := prov.ChatCompletion(r.Context(), req)
	if err != nil {
		h.logger.Error().Err(err).Str("provider", prov.Name()).Str("model", req.Model).Msg("provider error")
		h.writeError(w, http.StatusBadGateway, "provider_error", "Upstream provider error: "+err.Error())
		return
	}

	// Set response headers
	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("X-Alfred-Model", prov.Name()+"/"+req.Model)
	w.Header().Set("X-Alfred-Latency-Ms", fmt.Sprintf("%d", time.Since(start).Milliseconds()))

	if err := json.NewEncoder(w).Encode(resp); err != nil {
		h.logger.Error().Err(err).Msg("failed to encode response")
	}

	h.logger.Info().
		Str("provider", prov.Name()).
		Str("model", req.Model).
		Int("prompt_tokens", resp.Usage.PromptTokens).
		Int("completion_tokens", resp.Usage.CompletionTokens).
		Int64("latency_ms", time.Since(start).Milliseconds()).
		Msg("chat completion success")
}

// handleStreamingChat handles SSE streaming chat completions (T015).
func (h *ProxyHandler) handleStreamingChat(w http.ResponseWriter, r *http.Request, prov provider.Provider, req *provider.ChatRequest, start time.Time) {
	// Ensure the response writer supports flushing
	flusher, ok := w.(http.Flusher)
	if !ok {
		h.writeError(w, http.StatusInternalServerError, "streaming_unsupported", "Streaming not supported by server")
		return
	}

	stream, err := prov.ChatCompletionStream(r.Context(), req)
	if err != nil {
		h.logger.Error().Err(err).Str("provider", prov.Name()).Str("model", req.Model).Msg("stream error")
		h.writeError(w, http.StatusBadGateway, "provider_error", "Upstream provider streaming error: "+err.Error())
		return
	}
	defer stream.Close()

	// Set SSE headers
	w.Header().Set("Content-Type", "text/event-stream")
	w.Header().Set("Cache-Control", "no-cache")
	w.Header().Set("Connection", "keep-alive")
	w.Header().Set("X-Alfred-Model", prov.Name()+"/"+req.Model)
	w.WriteHeader(http.StatusOK)
	flusher.Flush()

	// Stream chunks to client
	for {
		chunk, err := stream.Next()
		if err != nil {
			if err == io.EOF {
				break
			}
			h.logger.Error().Err(err).Msg("stream read error")
			break
		}

		// Write chunk and flush immediately
		if _, writeErr := w.Write(chunk); writeErr != nil {
			h.logger.Debug().Err(writeErr).Msg("client disconnected during stream")
			break
		}
		flusher.Flush()
	}

	h.logger.Info().
		Str("provider", prov.Name()).
		Str("model", req.Model).
		Int64("latency_ms", time.Since(start).Milliseconds()).
		Msg("stream completion finished")
}

// Embeddings handles POST /v1/embeddings (T016).
func (h *ProxyHandler) Embeddings(w http.ResponseWriter, r *http.Request) {
	start := time.Now()

	var req provider.EmbeddingsRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		h.writeError(w, http.StatusBadRequest, "invalid_request", "Failed to parse request body: "+err.Error())
		return
	}

	if req.Model == "" {
		h.writeError(w, http.StatusBadRequest, "invalid_request", "Model field is required")
		return
	}

	prov, err := h.registry.GetForModel(req.Model)
	if err != nil {
		h.writeError(w, http.StatusBadRequest, "provider_not_found", err.Error())
		return
	}

	resp, err := prov.Embeddings(r.Context(), &req)
	if err != nil {
		h.writeError(w, http.StatusBadGateway, "provider_error", "Upstream provider error: "+err.Error())
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("X-Alfred-Model", prov.Name()+"/"+req.Model)
	w.Header().Set("X-Alfred-Latency-Ms", fmt.Sprintf("%d", time.Since(start).Milliseconds()))

	if err := json.NewEncoder(w).Encode(resp); err != nil {
		h.logger.Error().Err(err).Msg("failed to encode response")
	}
}

// handleDryRun estimates cost without calling the provider (T024).
func (h *ProxyHandler) handleDryRun(w http.ResponseWriter, req *provider.ChatRequest) {
	providerName := provider.DetectProvider(req.Model)

	// Rough token estimation: ~4 chars per token for English
	promptTokens := 0
	for _, msg := range req.Messages {
		if content, ok := msg.Content.(string); ok {
			promptTokens += len(content) / 4
		}
	}

	maxTokens := 1024
	if req.MaxTokens != nil {
		maxTokens = *req.MaxTokens
	}

	resp := map[string]interface{}{
		"dry_run": true,
		"model":   req.Model,
		"provider": providerName,
		"estimated_tokens": map[string]int{
			"prompt_tokens":     promptTokens,
			"max_completion":    maxTokens,
			"total_estimated":   promptTokens + maxTokens,
		},
		"message": "Dry run complete. No provider was called.",
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(resp)
}

// Models handles GET /v1/models.
func (h *ProxyHandler) Models(w http.ResponseWriter, r *http.Request) {
	providers := h.registry.List()
	models := make([]map[string]interface{}, 0)

	for _, name := range providers {
		prov, ok := h.registry.Get(name)
		if !ok {
			continue
		}
		for _, model := range prov.Models() {
			models = append(models, map[string]interface{}{
				"id":       model,
				"object":   "model",
				"provider": name,
				"owned_by": name,
			})
		}
	}

	resp := map[string]interface{}{
		"object": "list",
		"data":   models,
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(resp)
}

// ProviderHealth handles GET /v1/providers/health.
func (h *ProxyHandler) ProviderHealth(w http.ResponseWriter, r *http.Request) {
	health := h.registry.HealthCheckAll(r.Context())

	resp := make(map[string]interface{})
	for name, status := range health {
		resp[name] = map[string]interface{}{
			"healthy":    status.Healthy,
			"latency_ms": status.Latency.Milliseconds(),
			"last_check": status.LastCheck.Format(time.RFC3339),
			"error":      status.Error,
		}
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(resp)
}

func (h *ProxyHandler) writeError(w http.ResponseWriter, status int, errType, message string) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	json.NewEncoder(w).Encode(map[string]interface{}{
		"error": map[string]interface{}{
			"type":    errType,
			"message": message,
		},
	})
}

// GetAPIKeyFromRequest extracts the API key from the request context.
func GetAPIKeyFromRequest(r *http.Request) string {
	apiKey := middleware.GetAPIKey(r.Context())
	if apiKey != "" {
		return apiKey
	}
	// Fallback: read from Authorization header directly
	auth := r.Header.Get("Authorization")
	if strings.HasPrefix(auth, "Bearer ") {
		return auth[7:]
	}
	return auth
}
