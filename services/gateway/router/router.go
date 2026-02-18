package router

import (
    "net/http"
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
