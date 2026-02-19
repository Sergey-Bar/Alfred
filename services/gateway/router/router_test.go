/*
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L2
Logic:       Updated router tests to match new NewRouter(cfg, log, registry) signature.
Root Cause:  Gateway restructuring changed NewRouter parameters.
Context:     Tests must pass with the full middleware and provider stack.
Suitability: L2 model for standard test updates.
──────────────────────────────────────────────────────────────
*/

package router

import (
	"io"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/rs/zerolog"

	"github.com/AlfredDev/alfred/services/gateway/config"
	"github.com/AlfredDev/alfred/services/gateway/provider"
)

func testSetup() (http.Handler, *provider.Registry) {
	cfg := &config.Config{
		Addr:             ":0",
		Env:              "test",
		RateLimitEnabled: false,
		APIKeyHeader:     "Authorization",
		MaxBodyBytes:     1 << 20,
	}
	log := zerolog.New(io.Discard).With().Timestamp().Logger()
	reg := provider.NewRegistry()
	r := NewRouter(cfg, log, reg)
	return r, reg
}

func TestHealthEndpoints(t *testing.T) {
	r, _ := testSetup()

	tests := []struct {
		name   string
		path   string
		status int
	}{
		{"healthz", "/healthz", http.StatusOK},
		{"ready", "/ready", http.StatusOK},
		{"health", "/health", http.StatusOK},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			req := httptest.NewRequest(http.MethodGet, tc.path, nil)
			rw := httptest.NewRecorder()
			r.ServeHTTP(rw, req)
			if rw.Result().StatusCode != tc.status {
				t.Fatalf("expected %d for %s, got %d", tc.status, tc.path, rw.Result().StatusCode)
			}
		})
	}
}

func TestUnauthenticatedRouteReturns401(t *testing.T) {
	r, _ := testSetup()

	// /v1 routes require auth — request without Authorization header should get 401
	req := httptest.NewRequest(http.MethodGet, "/v1/models", nil)
	rw := httptest.NewRecorder()
	r.ServeHTTP(rw, req)

	if rw.Result().StatusCode != http.StatusUnauthorized {
		t.Fatalf("expected 401 for unauthenticated /v1/models, got %d", rw.Result().StatusCode)
	}
}

func TestCORSPreflight(t *testing.T) {
	r, _ := testSetup()

	req := httptest.NewRequest(http.MethodOptions, "/v1/chat/completions", nil)
	req.Header.Set("Origin", "http://localhost:3000")
	req.Header.Set("Access-Control-Request-Method", "POST")
	rw := httptest.NewRecorder()
	r.ServeHTTP(rw, req)

	if rw.Header().Get("Access-Control-Allow-Origin") == "" {
		t.Fatal("expected CORS Allow-Origin header on preflight response")
	}
}

func TestSecurityHeaders(t *testing.T) {
	r, _ := testSetup()

	req := httptest.NewRequest(http.MethodGet, "/healthz", nil)
	rw := httptest.NewRecorder()
	r.ServeHTTP(rw, req)

	headers := []string{
		"X-Content-Type-Options",
		"X-Frame-Options",
		"Strict-Transport-Security",
	}
	for _, h := range headers {
		if rw.Header().Get(h) == "" {
			t.Fatalf("expected security header %s to be set", h)
		}
	}
}
