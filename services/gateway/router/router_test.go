package router

import (
    "net/http"
    "net/http/httptest"
    "testing"
    "time"
    "io"

    "github.com/rs/zerolog"
)

func TestHealthEndpoints(t *testing.T) {
    // create a logger that discards output for test
    zlog := zerolog.New(io.Discard).With().Timestamp().Logger()
    r := NewRouter(zlog)

    req := httptest.NewRequest(http.MethodGet, "/healthz", nil)
    req.Header.Set("X-Request-Id", "test-req-123")
    rw := httptest.NewRecorder()

    r.ServeHTTP(rw, req)
    if rw.Result().StatusCode != http.StatusOK {
        t.Fatalf("expected 200 OK, got %d", rw.Result().StatusCode)
    }

    // quick test for readiness
    req2 := httptest.NewRequest(http.MethodGet, "/ready", nil)
    rw2 := httptest.NewRecorder()
    r.ServeHTTP(rw2, req2)
    if rw2.Result().StatusCode != http.StatusOK {
        t.Fatalf("expected 200 OK for /ready, got %d", rw2.Result().StatusCode)
    }

    // ensure middleware runs quickly (no sleep needed — middleware is synchronous in tests)
}
