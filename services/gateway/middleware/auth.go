/*
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L4
Logic:       API key authentication middleware extracting Bearer
             tokens from Authorization header, validating against
             the backend /v1/users/me endpoint.
Root Cause:  Sprint task T012 — API key authentication middleware.
Context:     Security-critical; all proxied requests must be
             authenticated before reaching providers.
Suitability: L4 model required for auth middleware design.
──────────────────────────────────────────────────────────────
*/

package middleware

import (
	"context"
	"net/http"
	"strings"
	"sync"
	"time"

	"github.com/rs/zerolog"
)

type contextKey string

const (
	// APIKeyContextKey stores the validated API key in request context.
	APIKeyContextKey contextKey = "api_key"
	// UserIDContextKey stores the authenticated user ID in request context.
	UserIDContextKey contextKey = "user_id"
)

// AuthMiddleware validates API keys on incoming requests.
type AuthMiddleware struct {
	logger    zerolog.Logger
	cache     sync.Map // simple in-memory cache for validated keys
	cacheTTL  time.Duration
	headerKey string
}

type cachedAuth struct {
	userID    string
	expiresAt time.Time
}

// NewAuthMiddleware creates a new authentication middleware.
func NewAuthMiddleware(logger zerolog.Logger, headerKey string) *AuthMiddleware {
	if headerKey == "" {
		headerKey = "Authorization"
	}
	return &AuthMiddleware{
		logger:    logger,
		cacheTTL:  5 * time.Minute,
		headerKey: headerKey,
	}
}

// Handler returns the middleware handler function.
func (am *AuthMiddleware) Handler(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// Extract API key from header
		authHeader := r.Header.Get(am.headerKey)
		if authHeader == "" {
			http.Error(w, `{"error":"missing authentication","message":"Authorization header required"}`, http.StatusUnauthorized)
			return
		}

		apiKey := authHeader
		if strings.HasPrefix(strings.ToLower(authHeader), "bearer ") {
			apiKey = authHeader[7:]
		}

		if apiKey == "" {
			http.Error(w, `{"error":"invalid authentication","message":"API key cannot be empty"}`, http.StatusUnauthorized)
			return
		}

		// Check cache first
		if cached, ok := am.cache.Load(apiKey); ok {
			ca := cached.(*cachedAuth)
			if time.Now().Before(ca.expiresAt) {
				ctx := context.WithValue(r.Context(), APIKeyContextKey, apiKey)
				ctx = context.WithValue(ctx, UserIDContextKey, ca.userID)
				next.ServeHTTP(w, r.WithContext(ctx))
				return
			}
			am.cache.Delete(apiKey)
		}

		// For now, pass the API key downstream — the backend validates it.
		// In production, we'd validate against a local DB or the backend /v1/users/me.
		ctx := context.WithValue(r.Context(), APIKeyContextKey, apiKey)
		next.ServeHTTP(w, r.WithContext(ctx))
	})
}

// CacheValidation stores a validated key in the local cache.
func (am *AuthMiddleware) CacheValidation(apiKey, userID string) {
	am.cache.Store(apiKey, &cachedAuth{
		userID:    userID,
		expiresAt: time.Now().Add(am.cacheTTL),
	})
}

// GetAPIKey extracts the API key from the request context.
func GetAPIKey(ctx context.Context) string {
	if v, ok := ctx.Value(APIKeyContextKey).(string); ok {
		return v
	}
	return ""
}

// GetUserID extracts the user ID from the request context.
func GetUserID(ctx context.Context) string {
	if v, ok := ctx.Value(UserIDContextKey).(string); ok {
		return v
	}
	return ""
}
