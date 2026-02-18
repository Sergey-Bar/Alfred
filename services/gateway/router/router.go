package router

import (
    "net/http"
    "os"
    "strconv"
    "time"

    "github.com/go-chi/chi/v5"
    "github.com/go-chi/chi/v5/middleware"
    "github.com/rs/zerolog"
)

// NewRouter returns a configured chi Router with middleware
func NewRouter(appLogger zerolog.Logger) http.Handler {
    r := chi.NewRouter()

    r.Use(middleware.RequestID)
    r.Use(middleware.Recoverer)
    r.Use(mwRequestLogger(appLogger))

    // Body size limit middleware (default 1MB) — override with GATEWAY_MAX_BODY_BYTES
    r.Use(mwMaxBodySize())

    r.Get("/healthz", func(w http.ResponseWriter, r *http.Request) {
        w.WriteHeader(http.StatusOK)
        _, _ = w.Write([]byte("ok"))
    })

    r.Get("/ready", func(w http.ResponseWriter, r *http.Request) {
        w.WriteHeader(http.StatusOK)
        _, _ = w.Write([]byte("ready"))
    })

    return r
}

// mwMaxBodySize returns middleware that limits the request body size.
// Default is 1MB; override with env var GATEWAY_MAX_BODY_BYTES (bytes).
func mwMaxBodySize() func(http.Handler) http.Handler {
    const defaultMax int64 = 1 * 1024 * 1024

    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            max := defaultMax
            if v := os.Getenv("GATEWAY_MAX_BODY_BYTES"); v != "" {
                if parsed, err := strconv.ParseInt(v, 10, 64); err == nil && parsed > 0 {
                    max = parsed
                }
            }

            if r.ContentLength > 0 && r.ContentLength > max {
                http.Error(w, "request body too large", http.StatusRequestEntityTooLarge)
                return
            }

            r.Body = http.MaxBytesReader(w, r.Body, max)
            next.ServeHTTP(w, r)
        })
    }
}

func mwRequestLogger(appLogger zerolog.Logger) func(http.Handler) http.Handler {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            start := time.Now()
            rw := middleware.NewWrapResponseWriter(w, r.ProtoMajor)
            next.ServeHTTP(rw, r)
            dur := time.Since(start)
            reqID := middleware.GetReqID(r.Context())
            appLogger.Info().Str("method", r.Method).Str("path", r.URL.Path).Str("req_id", reqID).Int("status", rw.Status()).Dur("duration", dur).Msg("request completed")
        })
    }
}
