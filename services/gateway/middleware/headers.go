/*
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L2
Logic:       Request/response header normalization middleware.
             Strips provider-specific headers from client requests,
             injects Alfred trace headers, normalizes content-type,
             and cleans upstream provider headers from responses
             before returning to clients.
Root Cause:  Sprint task T018 — Request/response header normalization.
Context:     Different LLM providers return different headers.
             This middleware ensures clients receive a consistent
             header set regardless of which provider served the
             request.
Suitability: L2 for straightforward header manipulation.
──────────────────────────────────────────────────────────────
*/

package middleware

import (
	"net/http"
	"strings"

	"github.com/rs/zerolog"
)

// HeaderNormalization performs request and response header normalization.
type HeaderNormalization struct {
	logger zerolog.Logger
}

// NewHeaderNormalization creates a new header normalization middleware.
func NewHeaderNormalization(logger zerolog.Logger) *HeaderNormalization {
	return &HeaderNormalization{logger: logger}
}

// headersToStripFromRequest are provider-specific headers that clients
// should not set directly — Alfred manages these.
var headersToStripFromRequest = []string{
	"x-api-key",               // Anthropic auth — managed by gateway
	"anthropic-version",       // Anthropic API version — managed by connector
	"anthropic-beta",          // Anthropic beta features
	"openai-organization",     // OpenAI org — managed per key
	"openai-project",          // OpenAI project
	"helicone-auth",           // Third-party proxy headers
	"x-stainless-lang",       // SDK telemetry
	"x-stainless-os",          // SDK telemetry
	"x-stainless-runtime",     // SDK telemetry
	"x-stainless-arch",        // SDK telemetry
	"x-stainless-package-version", // SDK telemetry
}

// headersToStripFromResponse are upstream headers that should not
// leak to the client.
var headersToStripFromResponse = []string{
	"x-api-key",
	"anthropic-version",
	"openai-organization",
	"openai-processing-ms",
	"x-ratelimit-limit-requests",
	"x-ratelimit-limit-tokens",
	"x-ratelimit-remaining-requests",
	"x-ratelimit-remaining-tokens",
	"x-ratelimit-reset-requests",
	"x-ratelimit-reset-tokens",
	"cf-ray",            // Cloudflare headers
	"cf-cache-status",
	"server",            // Don't leak provider's server software
	"x-request-id",      // Provider's internal request ID
}

// alfredResponseHeaders are headers Alfred always sets on responses.
var alfredResponseHeaders = map[string]string{
	"X-Alfred-Gateway":  "true",
	"X-Powered-By":      "Alfred AI Gateway",
}

// Handler returns the HTTP middleware handler.
func (h *HeaderNormalization) Handler(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// === Request normalization ===

		// Strip provider-specific headers that clients shouldn't send.
		for _, header := range headersToStripFromRequest {
			if r.Header.Get(header) != "" {
				h.logger.Debug().
					Str("header", header).
					Str("path", r.URL.Path).
					Msg("stripped provider header from request")
				r.Header.Del(header)
			}
		}

		// Normalize content-type for JSON bodies.
		ct := r.Header.Get("Content-Type")
		if ct != "" && strings.Contains(ct, "json") && ct != "application/json" {
			r.Header.Set("Content-Type", "application/json")
		}

		// Ensure Accept header is set for API requests.
		if r.Header.Get("Accept") == "" {
			r.Header.Set("Accept", "application/json")
		}

		// Propagate trace context if present.
		// (Correlation ID is handled by the router, this just ensures
		// standard W3C Trace Context headers pass through.)

		// === Response normalization via wrapper ===
		wrapped := &headerNormWriter{
			ResponseWriter: w,
			logger:         h.logger,
		}

		next.ServeHTTP(wrapped, r)
	})
}

// headerNormWriter wraps http.ResponseWriter to normalize response headers.
type headerNormWriter struct {
	http.ResponseWriter
	logger      zerolog.Logger
	wroteHeader bool
}

func (hw *headerNormWriter) WriteHeader(code int) {
	if hw.wroteHeader {
		return
	}
	hw.wroteHeader = true

	// Strip upstream provider headers.
	for _, header := range headersToStripFromResponse {
		hw.ResponseWriter.Header().Del(header)
	}

	// Set Alfred standard headers.
	for k, v := range alfredResponseHeaders {
		hw.ResponseWriter.Header().Set(k, v)
	}

	hw.ResponseWriter.WriteHeader(code)
}

func (hw *headerNormWriter) Write(b []byte) (int, error) {
	if !hw.wroteHeader {
		hw.WriteHeader(http.StatusOK)
	}
	return hw.ResponseWriter.Write(b)
}

// Flush supports streaming by delegating to the underlying writer.
func (hw *headerNormWriter) Flush() {
	if f, ok := hw.ResponseWriter.(http.Flusher); ok {
		f.Flush()
	}
}
