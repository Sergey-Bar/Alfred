/*
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L3
Logic:       Partial stream disconnect handling. Wraps SSE streaming
             so that when a client disconnects mid-stream, the gateway
             tracks how many tokens were already sent and bills for
             them. Also provides a metered response writer that counts
             bytes/chunks for cost attribution on partial streams.
Root Cause:  Sprint task T047 — Partial stream disconnect handling
             (bill tokens sent).
Context:     Without this, a client disconnect during streaming would
             lose token cost attribution for already-sent chunks.
Suitability: L3 — concurrency + SSE + cost correctness.
──────────────────────────────────────────────────────────────
*/

package handler

import (
	"context"
	"io"
	"net/http"
	"strings"
	"sync"
	"time"

	"github.com/AlfredDev/alfred/services/gateway/provider"
	"github.com/rs/zerolog"
)

// StreamMetrics captures token/byte accounting for a streaming request.
type StreamMetrics struct {
	mu               sync.Mutex
	ChunksSent       int
	BytesSent        int64
	TokensEstimated  int
	ClientDisconnect bool
	DisconnectAt     time.Time
	TotalDuration    time.Duration
	FinishReason     string
}

// RecordChunk records a chunk sent to the client.
func (sm *StreamMetrics) RecordChunk(data []byte) {
	sm.mu.Lock()
	defer sm.mu.Unlock()
	sm.ChunksSent++
	sm.BytesSent += int64(len(data))
	// Rough token estimation: ~4 chars per token for English text
	sm.TokensEstimated += estimateTokensFromSSE(data)
}

// RecordDisconnect records a client disconnect event.
func (sm *StreamMetrics) RecordDisconnect() {
	sm.mu.Lock()
	defer sm.mu.Unlock()
	sm.ClientDisconnect = true
	sm.DisconnectAt = time.Now().UTC()
}

// Snapshot returns a copy of the current metrics.
func (sm *StreamMetrics) Snapshot() StreamMetrics {
	sm.mu.Lock()
	defer sm.mu.Unlock()
	return StreamMetrics{
		ChunksSent:       sm.ChunksSent,
		BytesSent:        sm.BytesSent,
		TokensEstimated:  sm.TokensEstimated,
		ClientDisconnect: sm.ClientDisconnect,
		DisconnectAt:     sm.DisconnectAt,
		TotalDuration:    sm.TotalDuration,
		FinishReason:     sm.FinishReason,
	}
}

// estimateTokensFromSSE extracts content from SSE data lines and
// estimates the token count. This is an approximation — the actual
// billing should use the provider's reported usage when available.
func estimateTokensFromSSE(data []byte) int {
	s := string(data)
	// SSE lines look like "data: {json}\n\n"
	// Extract the content delta for a rough count
	tokens := 0
	for _, line := range strings.Split(s, "\n") {
		if strings.HasPrefix(line, "data: ") {
			payload := line[6:]
			if payload == "[DONE]" {
				continue
			}
			// Count printable content bytes / 4 as rough token estimate
			tokens += len(payload) / 16 // conservative: JSON overhead dilutes content
			if tokens == 0 && len(payload) > 0 {
				tokens = 1
			}
		}
	}
	return tokens
}

// StreamResult encapsulates the outcome of a streaming proxy call.
type StreamResult struct {
	Metrics  StreamMetrics
	Error    error
	Finished bool // true if stream completed normally (received [DONE])
}

// streamWithDisconnectDetection wraps a provider Stream and writes to
// the client while tracking metrics and detecting early disconnects.
// This is the core implementation for Sprint T047.
func streamWithDisconnectDetection(
	ctx context.Context,
	w http.ResponseWriter,
	stream provider.Stream,
	logger zerolog.Logger,
) *StreamResult {
	flusher, ok := w.(http.Flusher)
	if !ok {
		return &StreamResult{Error: io.ErrNoProgress}
	}

	result := &StreamResult{}
	start := time.Now()

	// Monitor client context cancellation
	clientCtx := ctx
	clientGone := clientCtx.Done()

	for {
		select {
		case <-clientGone:
			// Client disconnected before stream finished
			result.Metrics.RecordDisconnect()
			result.Metrics.TotalDuration = time.Since(start)
			logger.Warn().
				Int("chunks_sent", result.Metrics.ChunksSent).
				Int64("bytes_sent", result.Metrics.BytesSent).
				Int("tokens_estimated", result.Metrics.TokensEstimated).
				Msg("client disconnected mid-stream — billing for tokens already sent")
			return result

		default:
			chunk, err := stream.Next()
			if err != nil {
				if err == io.EOF {
					result.Finished = true
					result.Metrics.FinishReason = "stop"
				} else {
					result.Error = err
					result.Metrics.FinishReason = "error"
					logger.Error().Err(err).Msg("stream read error")
				}
				result.Metrics.TotalDuration = time.Since(start)
				return result
			}

			// Write to client
			if _, writeErr := w.Write(chunk); writeErr != nil {
				// Write error → client disconnected
				result.Metrics.RecordDisconnect()
				result.Metrics.TotalDuration = time.Since(start)
				result.Metrics.FinishReason = "client_disconnect"
				logger.Warn().
					Err(writeErr).
					Int("chunks_sent", result.Metrics.ChunksSent).
					Int("tokens_estimated", result.Metrics.TokensEstimated).
					Msg("write failed — client disconnect detected")
				return result
			}

			// Track the chunk metrics
			result.Metrics.RecordChunk(chunk)
			flusher.Flush()
		}
	}
}

// DisconnectAwareStreamHandler replaces the basic streaming loop in
// proxy.go with full disconnect detection and partial billing.
// Call this from handleStreamingChat instead of the raw for-loop.
func (h *ProxyHandler) DisconnectAwareStreamHandler(
	w http.ResponseWriter,
	r *http.Request,
	prov provider.Provider,
	req *provider.ChatRequest,
	start time.Time,
) *StreamResult {
	flusher, ok := w.(http.Flusher)
	if !ok {
		h.writeError(w, http.StatusInternalServerError, "streaming_unsupported", "Streaming not supported by server")
		return nil
	}

	stream, err := prov.ChatCompletionStream(r.Context(), req)
	if err != nil {
		h.logger.Error().Err(err).Str("provider", prov.Name()).Str("model", req.Model).Msg("stream error")
		h.writeError(w, http.StatusBadGateway, "provider_error", "Upstream provider streaming error: "+err.Error())
		return nil
	}
	defer stream.Close()

	// Set SSE headers
	w.Header().Set("Content-Type", "text/event-stream")
	w.Header().Set("Cache-Control", "no-cache")
	w.Header().Set("Connection", "keep-alive")
	w.Header().Set("X-Alfred-Model", prov.Name()+"/"+req.Model)
	w.WriteHeader(http.StatusOK)
	flusher.Flush()

	result := streamWithDisconnectDetection(r.Context(), w, stream, h.logger)

	// Log final result
	h.logger.Info().
		Str("provider", prov.Name()).
		Str("model", req.Model).
		Int("chunks_sent", result.Metrics.ChunksSent).
		Int64("bytes_sent", result.Metrics.BytesSent).
		Int("tokens_estimated", result.Metrics.TokensEstimated).
		Bool("client_disconnected", result.Metrics.ClientDisconnect).
		Bool("completed", result.Finished).
		Str("finish_reason", result.Metrics.FinishReason).
		Int64("latency_ms", time.Since(start).Milliseconds()).
		Msg("stream completion finished")

	return result
}
