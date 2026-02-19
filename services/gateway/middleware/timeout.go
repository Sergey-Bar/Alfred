/*
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L2
Logic:       Per-provider configurable timeout middleware using
             Go context cancellation. Extracts provider from the
             request model, looks up per-provider timeout from
             config, and wraps the request context with a deadline.
             Also supports client-specified timeout headers.
Root Cause:  Sprint task T022 — Timeout handling (per-provider
             configurable).
Context:     Different providers have different latency profiles.
             OpenAI may need 120s for large completions, while
             Groq might only need 30s. Context cancellation in
             Go propagates cleanly through the proxy chain.
Suitability: L2 for Go context patterns; well-understood.
──────────────────────────────────────────────────────────────
*/

package middleware

import (
	"context"
	"encoding/json"
	"net/http"
	"strconv"
	"sync"
	"time"

	"github.com/AlfredDev/alfred/services/gateway/config"
	"github.com/rs/zerolog"
)

// TimeoutMiddleware applies per-provider configurable timeouts to requests.
type TimeoutMiddleware struct {
	logger zerolog.Logger
	cfg    *config.Config
}

// NewTimeoutMiddleware creates a new timeout middleware.
func NewTimeoutMiddleware(logger zerolog.Logger, cfg *config.Config) *TimeoutMiddleware {
	return &TimeoutMiddleware{
		logger: logger,
		cfg:    cfg,
	}
}

// Handler returns the HTTP middleware handler.
func (t *TimeoutMiddleware) Handler(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		timeout := t.resolveTimeout(r)

		if timeout <= 0 {
			// No timeout — pass through.
			next.ServeHTTP(w, r)
			return
		}

		ctx, cancel := context.WithTimeout(r.Context(), timeout)
		defer cancel()

		// Track whether the handler completed or timed out.
		done := make(chan struct{})
		tw := &timeoutWriter{
			ResponseWriter: w,
		}

		go func() {
			next.ServeHTTP(tw, r.WithContext(ctx))
			close(done)
		}()

		select {
		case <-done:
			// Handler completed normally. Check it wasn't also timed out.
			tw.mu.Lock()
			alreadyTimedOut := tw.timedOut
			tw.mu.Unlock()
			if alreadyTimedOut {
				t.logger.Debug().
					Str("path", r.URL.Path).
					Msg("handler goroutine finished after timeout")
			}
			return
		case <-ctx.Done():
			// Context deadline exceeded — mark timedOut to suppress further
			// writes from the still-running handler goroutine.
			tw.mu.Lock()
			tw.timedOut = true
			if !tw.wroteHeader {
				w.Header().Set("Content-Type", "application/json")
				w.WriteHeader(http.StatusGatewayTimeout)
				json.NewEncoder(w).Encode(map[string]interface{}{
					"error": map[string]interface{}{
						"type":    "timeout",
						"message": "Request timed out after " + timeout.String(),
					},
				})
				tw.wroteHeader = true
			}
			tw.mu.Unlock()

			t.logger.Warn().
				Str("path", r.URL.Path).
				Dur("timeout", timeout).
				Msg("request timed out — handler goroutine still running with cancelled context")

			// Wait for the handler goroutine to finish. The cancelled context
			// should cause well-behaved handlers to return promptly.
			<-done
		}
	})
}

// resolveTimeout determines the timeout for this request.
// Priority: X-Alfred-Timeout header > provider config > default.
func (t *TimeoutMiddleware) resolveTimeout(r *http.Request) time.Duration {
	// 1. Client-specified timeout via header (capped at 5 minutes).
	if headerVal := r.Header.Get("X-Alfred-Timeout"); headerVal != "" {
		if seconds, err := strconv.Atoi(headerVal); err == nil && seconds > 0 {
			timeout := time.Duration(seconds) * time.Second
			maxTimeout := 5 * time.Minute
			if timeout > maxTimeout {
				timeout = maxTimeout
			}
			return timeout
		}
	}

	// 2. Per-provider timeout from config.
	// We need to peek at the model to determine the provider.
	// For non-chat endpoints, use default timeout.
	if r.URL.Path == "/v1/chat/completions" || r.URL.Path == "/v1/embeddings" {
		// Try to determine provider from query param or default.
		provider := r.URL.Query().Get("provider")
		if provider != "" {
			return t.cfg.ProviderTimeout(provider)
		}
	}

	// 3. Default timeout.
	return t.cfg.DefaultTimeout
}

// timeoutWriter wraps http.ResponseWriter for safe concurrent access
// between the handler goroutine and the timeout goroutine.
type timeoutWriter struct {
	http.ResponseWriter
	mu          sync.Mutex
	wroteHeader bool
	timedOut    bool // set when context deadline exceeded; suppresses further writes
}

func (tw *timeoutWriter) WriteHeader(code int) {
	tw.mu.Lock()
	defer tw.mu.Unlock()
	if tw.timedOut || tw.wroteHeader {
		return
	}
	tw.wroteHeader = true
	tw.ResponseWriter.WriteHeader(code)
}

func (tw *timeoutWriter) Write(b []byte) (int, error) {
	tw.mu.Lock()
	defer tw.mu.Unlock()
	if tw.timedOut {
		// Suppress writes from the handler goroutine after timeout.
		return 0, context.DeadlineExceeded
	}
	if !tw.wroteHeader {
		tw.wroteHeader = true
		tw.ResponseWriter.WriteHeader(http.StatusOK)
	}
	return tw.ResponseWriter.Write(b)
}

func (tw *timeoutWriter) Flush() {
	tw.mu.Lock()
	defer tw.mu.Unlock()
	if f, ok := tw.ResponseWriter.(http.Flusher); ok {
		f.Flush()
	}
}
