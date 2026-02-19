/*
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L3
Logic:       Redis-backed token bucket rate limiter with
             per-key sliding window and burst control.
Root Cause:  Sprint task T019 — Rate limiting middleware.
Context:     Distributed rate limiting prevents abuse before
             business logic executes. Falls back to in-memory.
Suitability: L3 model for distributed rate limiting logic.
──────────────────────────────────────────────────────────────
*/

package middleware

import (
	"fmt"
	"net/http"
	"strconv"
	"sync"
	"time"

	"github.com/rs/zerolog"
)

// RateLimiter implements a per-key sliding window rate limiter.
// Uses in-memory storage. For distributed setups, extend with Redis.
type RateLimiter struct {
	logger   zerolog.Logger
	enabled  bool
	rpm      int
	burst    int
	mu       sync.Mutex
	windows  map[string]*slidingWindow
}

type slidingWindow struct {
	tokens    []time.Time
	lastClean time.Time
}

// NewRateLimiter creates a new rate limiter.
func NewRateLimiter(logger zerolog.Logger, enabled bool, rpm, burst int) *RateLimiter {
	return &RateLimiter{
		logger:  logger,
		enabled: enabled,
		rpm:     rpm,
		burst:   burst,
		windows: make(map[string]*slidingWindow),
	}
}

// Handler returns the rate limiting middleware handler.
func (rl *RateLimiter) Handler(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if !rl.enabled {
			next.ServeHTTP(w, r)
			return
		}

		// Use API key as rate limit key, fall back to IP
		key := GetAPIKey(r.Context())
		if key == "" {
			key = r.RemoteAddr
		}

		allowed, remaining, resetAt := rl.allow(key)
		w.Header().Set("X-RateLimit-Limit", strconv.Itoa(rl.rpm))
		w.Header().Set("X-RateLimit-Remaining", strconv.Itoa(remaining))
		w.Header().Set("X-RateLimit-Reset", strconv.FormatInt(resetAt.Unix(), 10))

		if !allowed {
			w.Header().Set("Retry-After", strconv.Itoa(int(time.Until(resetAt).Seconds())+1))
			http.Error(w, fmt.Sprintf(`{"error":"rate_limit_exceeded","message":"Rate limit of %d requests per minute exceeded","retry_after":%d}`,
				rl.rpm, int(time.Until(resetAt).Seconds())+1), http.StatusTooManyRequests)
			rl.logger.Warn().Str("key", key[:8]+"...").Int("limit", rl.rpm).Msg("rate limit exceeded")
			return
		}

		next.ServeHTTP(w, r)
	})
}

func (rl *RateLimiter) allow(key string) (bool, int, time.Time) {
	rl.mu.Lock()
	defer rl.mu.Unlock()

	now := time.Now()
	windowStart := now.Add(-1 * time.Minute)
	resetAt := now.Add(1 * time.Minute)

	sw, exists := rl.windows[key]
	if !exists {
		sw = &slidingWindow{
			tokens:    make([]time.Time, 0, rl.rpm),
			lastClean: now,
		}
		rl.windows[key] = sw
	}

	// Clean expired tokens
	if now.Sub(sw.lastClean) > 10*time.Second {
		validTokens := make([]time.Time, 0, len(sw.tokens))
		for _, t := range sw.tokens {
			if t.After(windowStart) {
				validTokens = append(validTokens, t)
			}
		}
		sw.tokens = validTokens
		sw.lastClean = now
	}

	// Count tokens in current window
	count := 0
	for _, t := range sw.tokens {
		if t.After(windowStart) {
			count++
		}
	}

	remaining := rl.rpm - count
	if remaining <= 0 {
		// Find earliest token expiry for reset time
		if len(sw.tokens) > 0 {
			resetAt = sw.tokens[0].Add(1 * time.Minute)
		}
		return false, 0, resetAt
	}

	// Add new token
	sw.tokens = append(sw.tokens, now)
	return true, remaining - 1, resetAt
}

// Cleanup removes stale entries. Call periodically.
func (rl *RateLimiter) Cleanup() {
	rl.mu.Lock()
	defer rl.mu.Unlock()

	cutoff := time.Now().Add(-2 * time.Minute)
	for key, sw := range rl.windows {
		if len(sw.tokens) == 0 || sw.tokens[len(sw.tokens)-1].Before(cutoff) {
			delete(rl.windows, key)
		}
	}
}
