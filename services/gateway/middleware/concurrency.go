/*
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L4
Logic:       Concurrent request handling middleware ensuring no race
             conditions on shared state (wallets, rate limits, cache).
             Implements per-key request serialization for wallet
             mutations, request deduplication, semaphore-based
             concurrency control per org/team, and atomic operations
             for all shared counters.
Root Cause:  Sprint task T060 — Concurrent request handling without
             race conditions.
Context:     At 1000+ concurrent requests, naive shared state access
             leads to credit leakage (double-spend) or lost updates.
             This module provides the concurrency primitives to prevent
             those issues at the gateway layer.
Suitability: L4 — concurrency correctness is critical for financial
             integrity.

ROLLBACK: To revert this change:
1. Remove import from router.go
2. Remove middleware from router chain
3. Notify: Sergey Bar + on-call engineer
──────────────────────────────────────────────────────────────
*/

package middleware

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"net/http"
	"sync"
	"sync/atomic"
	"time"

	"github.com/rs/zerolog"
)

// ──────────────────────────────────────────────────────────────
// 1. Per-Key Mutex — serialize wallet mutations for same org/user
// ──────────────────────────────────────────────────────────────

// KeyedMutex provides per-key locking to serialize access to shared
// resources (e.g., wallet balances) without a global lock.
// This prevents double-spend on concurrent requests from the same user.
type KeyedMutex struct {
	mu    sync.Mutex
	locks map[string]*keyEntry
}

type keyEntry struct {
	mu      sync.Mutex
	waiters int32
}

// NewKeyedMutex creates a new per-key mutex manager.
func NewKeyedMutex() *KeyedMutex {
	return &KeyedMutex{
		locks: make(map[string]*keyEntry),
	}
}

// Lock acquires a lock for the given key. Returns an unlock function.
func (km *KeyedMutex) Lock(key string) func() {
	km.mu.Lock()
	entry, ok := km.locks[key]
	if !ok {
		entry = &keyEntry{}
		km.locks[key] = entry
	}
	atomic.AddInt32(&entry.waiters, 1)
	km.mu.Unlock()

	entry.mu.Lock()

	return func() {
		entry.mu.Unlock()
		km.mu.Lock()
		if atomic.AddInt32(&entry.waiters, -1) == 0 {
			delete(km.locks, key)
		}
		km.mu.Unlock()
	}
}

// ──────────────────────────────────────────────────────────────
// 2. Semaphore — per-org concurrency limiting
// ──────────────────────────────────────────────────────────────

// Semaphore provides bounded concurrency control per key (org/team).
// This prevents any single tenant from monopolizing gateway capacity.
type Semaphore struct {
	mu    sync.Mutex
	semas map[string]chan struct{}
	limit int
}

// NewSemaphore creates a new per-key semaphore with the given concurrency limit.
func NewSemaphore(limit int) *Semaphore {
	if limit <= 0 {
		limit = 100 // default
	}
	return &Semaphore{
		semas: make(map[string]chan struct{}),
		limit: limit,
	}
}

// Acquire attempts to acquire a slot for the given key.
// Returns true if acquired, false if the limit is reached.
// The caller must call Release when done.
func (s *Semaphore) Acquire(key string, timeout time.Duration) bool {
	s.mu.Lock()
	ch, ok := s.semas[key]
	if !ok {
		ch = make(chan struct{}, s.limit)
		s.semas[key] = ch
	}
	s.mu.Unlock()

	select {
	case ch <- struct{}{}:
		return true
	case <-time.After(timeout):
		return false
	}
}

// Release releases a slot for the given key.
func (s *Semaphore) Release(key string) {
	s.mu.Lock()
	ch, ok := s.semas[key]
	s.mu.Unlock()

	if ok {
		select {
		case <-ch:
		default:
		}
	}
}

// ActiveCount returns the number of active requests for a key.
func (s *Semaphore) ActiveCount(key string) int {
	s.mu.Lock()
	ch, ok := s.semas[key]
	s.mu.Unlock()
	if !ok {
		return 0
	}
	return len(ch)
}

// ──────────────────────────────────────────────────────────────
// 3. Request Deduplication — prevent duplicate in-flight requests
// ──────────────────────────────────────────────────────────────

// Deduplicator prevents duplicate in-flight requests by fingerprinting
// request content and collapsing identical concurrent requests into one.
type Deduplicator struct {
	mu       sync.Mutex
	inflight map[string]*inflightEntry
}

type inflightEntry struct {
	done chan struct{}
	resp []byte
	code int
	err  error
}

// NewDeduplicator creates a new request deduplicator.
func NewDeduplicator() *Deduplicator {
	return &Deduplicator{
		inflight: make(map[string]*inflightEntry),
	}
}

// Fingerprint generates a request fingerprint from key fields.
func Fingerprint(apiKey, model, contentHash string) string {
	h := sha256.Sum256([]byte(apiKey + "|" + model + "|" + contentHash))
	return hex.EncodeToString(h[:16]) // 128-bit fingerprint
}

// TryStart checks if an identical request is already in-flight.
// Returns (entry, isNew). If isNew is false, wait on entry.done.
func (d *Deduplicator) TryStart(fingerprint string) (*inflightEntry, bool) {
	d.mu.Lock()
	defer d.mu.Unlock()

	if entry, exists := d.inflight[fingerprint]; exists {
		return entry, false
	}

	entry := &inflightEntry{
		done: make(chan struct{}),
	}
	d.inflight[fingerprint] = entry
	return entry, true
}

// Complete marks a request as finished and removes it from tracking.
func (d *Deduplicator) Complete(fingerprint string, resp []byte, code int, err error) {
	d.mu.Lock()
	entry, exists := d.inflight[fingerprint]
	delete(d.inflight, fingerprint)
	d.mu.Unlock()

	if exists {
		entry.resp = resp
		entry.code = code
		entry.err = err
		close(entry.done)
	}
}

// InFlightCount returns the number of in-flight deduplicated requests.
func (d *Deduplicator) InFlightCount() int {
	d.mu.Lock()
	defer d.mu.Unlock()
	return len(d.inflight)
}

// ──────────────────────────────────────────────────────────────
// 4. Atomic Counters — thread-safe request/cost tracking
// ──────────────────────────────────────────────────────────────

// AtomicCounter provides a thread-safe counter using atomic operations.
type AtomicCounter struct {
	value int64
}

// Inc increments the counter by 1 and returns the new value.
func (c *AtomicCounter) Inc() int64 {
	return atomic.AddInt64(&c.value, 1)
}

// Add increments the counter by n and returns the new value.
func (c *AtomicCounter) Add(n int64) int64 {
	return atomic.AddInt64(&c.value, n)
}

// Get returns the current value.
func (c *AtomicCounter) Get() int64 {
	return atomic.LoadInt64(&c.value)
}

// Reset sets the counter to 0 and returns the old value.
func (c *AtomicCounter) Reset() int64 {
	return atomic.SwapInt64(&c.value, 0)
}

// ──────────────────────────────────────────────────────────────
// 5. Concurrency Middleware — chi-compatible HTTP middleware
// ──────────────────────────────────────────────────────────────

// ConcurrencyGuard is the combined concurrency control middleware.
type ConcurrencyGuard struct {
	semaphore *Semaphore
	logger    zerolog.Logger
	timeout   time.Duration
}

// NewConcurrencyGuard creates a new concurrency guard middleware.
func NewConcurrencyGuard(maxConcurrentPerOrg int, timeout time.Duration, logger zerolog.Logger) *ConcurrencyGuard {
	return &ConcurrencyGuard{
		semaphore: NewSemaphore(maxConcurrentPerOrg),
		logger:    logger,
		timeout:   timeout,
	}
}

// Middleware returns an http.Handler middleware that enforces per-org
// concurrency limits. If the org exceeds the limit, requests get a 429.
func (cg *ConcurrencyGuard) Middleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// Extract org key from context (set by auth middleware)
		orgKey := extractOrgKey(r)
		if orgKey == "" {
			orgKey = "default"
		}

		// Try to acquire a slot
		if !cg.semaphore.Acquire(orgKey, cg.timeout) {
			cg.logger.Warn().
				Str("org", orgKey).
				Int("active", cg.semaphore.ActiveCount(orgKey)).
				Msg("concurrency limit reached — rejecting request")

			w.Header().Set("Content-Type", "application/json")
			w.Header().Set("Retry-After", "1")
			w.WriteHeader(http.StatusTooManyRequests)
			fmt.Fprintf(w, `{"error":{"type":"rate_limit","message":"Too many concurrent requests for this organization"}}`)
			return
		}
		defer cg.semaphore.Release(orgKey)

		// Inject active count into context for downstream logging
		ctx := context.WithValue(r.Context(), concurrencyActiveKey, cg.semaphore.ActiveCount(orgKey))
		next.ServeHTTP(w, r.WithContext(ctx))
	})
}

// Stats returns current concurrency statistics.
func (cg *ConcurrencyGuard) Stats() map[string]int {
	// Return current semaphore state — in production this would
	// iterate tracked keys. For now return aggregate metrics.
	return map[string]int{
		"configured_limit": cg.semaphore.limit,
	}
}

type contextKey string

const concurrencyActiveKey contextKey = "concurrency_active"

// extractOrgKey gets the org identifier from the request for concurrency bucketing.
func extractOrgKey(r *http.Request) string {
	// Try org from context (set by auth middleware)
	if orgID := r.Header.Get("X-Alfred-Org-ID"); orgID != "" {
		return orgID
	}
	// Fallback: use hashed API key prefix as org identifier.
	// Never use raw API key material in metrics or logs.
	apiKey := GetAPIKey(r.Context())
	if len(apiKey) > 0 {
		h := sha256.Sum256([]byte(apiKey))
		return "keyhash:" + hex.EncodeToString(h[:8])
	}
	return ""
}

// GetConcurrencyActive retrieves the active concurrent request count
// from the request context.
func GetConcurrencyActive(ctx context.Context) int {
	if v, ok := ctx.Value(concurrencyActiveKey).(int); ok {
		return v
	}
	return 0
}
