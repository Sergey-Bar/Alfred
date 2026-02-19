/*
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L3
Logic:       Semantic caching engine (T105-T115). Uses Redis
             vector search for similarity matching. Generates
             embeddings via the provider registry, stores
             prompt→response pairs with per-team namespace
             isolation and configurable TTL. Includes cache
             poisoning prevention via response validation.
Root Cause:  Sprint tasks T105-T115 — Semantic Caching.
Context:     Core feature for 30%+ cost reduction target.
             Serves cached responses for semantically similar
             requests without calling upstream providers.
Suitability: L3 — vector similarity + cache architecture.
──────────────────────────────────────────────────────────────
*/

package caching

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"math"
	"strings"
	"sync"
	"sync/atomic"
	"time"

	"github.com/rs/zerolog"
)

// ─── Configuration ──────────────────────────────────────────

// CacheConfig holds per-team or global cache settings (T109, T110).
type CacheConfig struct {
	// Similarity threshold (0.0-1.0). Higher = stricter matching.
	SimilarityThreshold float64 `json:"similarity_threshold"`
	// Default TTL for cached entries.
	DefaultTTL time.Duration `json:"default_ttl"`
	// Per-model TTL overrides (T110).
	ModelTTLOverrides map[string]time.Duration `json:"model_ttl_overrides"`
	// Maximum cached entries per namespace.
	MaxEntries int `json:"max_entries"`
	// Enable/disable cache poisoning validation (T115).
	ValidateResponses bool `json:"validate_responses"`
	// Minimum response length to be considered valid.
	MinResponseLength int `json:"min_response_length"`
}

// DefaultCacheConfig returns production defaults.
func DefaultCacheConfig() CacheConfig {
	return CacheConfig{
		SimilarityThreshold: 0.92,
		DefaultTTL:          24 * time.Hour,
		ModelTTLOverrides:   make(map[string]time.Duration),
		MaxEntries:          10000,
		ValidateResponses:   true,
		MinResponseLength:   10,
	}
}

// ─── Types ──────────────────────────────────────────────────

// CacheEntry represents a stored prompt→response pair with its embedding.
type CacheEntry struct {
	ID         string    `json:"id"`
	Namespace  string    `json:"namespace"`   // Team ID for isolation (T109)
	Model      string    `json:"model"`
	PromptHash string    `json:"prompt_hash"` // SHA-256 of normalized prompt
	Embedding  []float64 `json:"embedding"`   // Prompt embedding vector
	Response   []byte    `json:"response"`    // Cached response body
	TokensSaved int      `json:"tokens_saved"` // Estimated tokens this cache saves
	CreatedAt  time.Time `json:"created_at"`
	ExpiresAt  time.Time `json:"expires_at"`
	HitCount   int64     `json:"hit_count"`
}

// CacheLookupResult represents the outcome of a cache query.
type CacheLookupResult struct {
	Hit        bool      `json:"hit"`
	Entry      *CacheEntry `json:"entry,omitempty"`
	Similarity float64   `json:"similarity"`
	Source     string    `json:"source"` // "exact" or "semantic"
}

// CacheStats tracks hit/miss metrics (T113).
type CacheStats struct {
	Hits         int64   `json:"hits"`
	Misses       int64   `json:"misses"`
	Evictions    int64   `json:"evictions"`
	Entries      int64   `json:"entries"`
	HitRate      float64 `json:"hit_rate_pct"`
	AvgSimilarity float64 `json:"avg_similarity"`
	TotalSaved   int64   `json:"total_tokens_saved"`
}

// EmbeddingFunc generates an embedding vector for a text string.
// Provided by the caller (wraps the provider registry's embedding endpoint).
type EmbeddingFunc func(ctx context.Context, text string, model string) ([]float64, error)

// ─── Semantic Cache Engine ──────────────────────────────────

// Engine is the in-process semantic cache (T105-T115).
// Production deployments should back this with Redis Vector Search;
// this implementation provides the full API contract with an in-memory store.
type Engine struct {
	mu     sync.RWMutex
	logger zerolog.Logger
	config CacheConfig

	// namespace → entries (T109: per-team segmentation)
	store map[string][]*CacheEntry

	// Exact-match index: namespace:promptHash → entry
	exactIndex map[string]*CacheEntry

	// Embedding function
	embedFn EmbeddingFunc

	// Metrics (T113)
	hits       int64
	misses     int64
	evictions  int64
	totalSaved int64
	simSum     float64
	simCount   int64
}

// NewEngine creates a new semantic cache engine.
func NewEngine(logger zerolog.Logger, embedFn EmbeddingFunc, config ...CacheConfig) *Engine {
	cfg := DefaultCacheConfig()
	if len(config) > 0 {
		cfg = config[0]
	}
	return &Engine{
		logger:     logger.With().Str("component", "semantic_cache").Logger(),
		config:     cfg,
		store:      make(map[string][]*CacheEntry),
		exactIndex: make(map[string]*CacheEntry),
		embedFn:    embedFn,
	}
}

// ─── T107: Similarity Search + Threshold ────────────────────

// Lookup checks the cache for a semantically similar prompt.
// Returns a CacheLookupResult with hit/miss status and similarity score.
//
// The lookup order is:
// 1. Exact hash match (fast path)
// 2. Vector similarity search (cosine distance)
func (e *Engine) Lookup(ctx context.Context, namespace, model, prompt string) (*CacheLookupResult, error) {
	promptHash := hashPrompt(normalizePrompt(prompt))
	exactKey := fmt.Sprintf("%s:%s", namespace, promptHash)

	// Fast path: exact match
	e.mu.RLock()
	if entry, ok := e.exactIndex[exactKey]; ok && entry.ExpiresAt.After(time.Now()) {
		e.mu.RUnlock()
		atomic.AddInt64(&e.hits, 1)
		atomic.AddInt64(&entry.HitCount, 1)
		atomic.AddInt64(&e.totalSaved, int64(entry.TokensSaved))
		return &CacheLookupResult{
			Hit:        true,
			Entry:      entry,
			Similarity: 1.0,
			Source:     "exact",
		}, nil
	}
	e.mu.RUnlock()

	// Generate embedding for similarity search
	embedding, err := e.embedFn(ctx, prompt, model)
	if err != nil {
		atomic.AddInt64(&e.misses, 1)
		e.logger.Debug().Err(err).Msg("embedding generation failed, cache miss")
		return &CacheLookupResult{Hit: false}, nil
	}

	// Search within namespace (T109)
	e.mu.RLock()
	entries := e.store[namespace]
	e.mu.RUnlock()

	var bestEntry *CacheEntry
	var bestSim float64

	now := time.Now()
	for _, entry := range entries {
		// Skip expired entries
		if entry.ExpiresAt.Before(now) {
			continue
		}
		// Skip different models (optional — some teams may want cross-model caching)
		if entry.Model != model {
			continue
		}

		sim := cosineSimilarity(embedding, entry.Embedding)
		if sim > bestSim {
			bestSim = sim
			bestEntry = entry
		}
	}

	// Check threshold (T107)
	if bestEntry != nil && bestSim >= e.config.SimilarityThreshold {
		// Validate response (T115: cache poisoning prevention)
		if e.config.ValidateResponses && !e.validateResponse(bestEntry) {
			e.logger.Warn().
				Str("entry_id", bestEntry.ID).
				Float64("similarity", bestSim).
				Msg("cache hit failed validation, treating as miss")
			e.evictEntry(bestEntry)
			atomic.AddInt64(&e.misses, 1)
			return &CacheLookupResult{Hit: false, Similarity: bestSim}, nil
		}

		atomic.AddInt64(&e.hits, 1)
		atomic.AddInt64(&bestEntry.HitCount, 1)
		atomic.AddInt64(&e.totalSaved, int64(bestEntry.TokensSaved))

		// Track similarity stats
		e.mu.Lock()
		e.simSum += bestSim
		e.simCount++
		e.mu.Unlock()

		return &CacheLookupResult{
			Hit:        true,
			Entry:      bestEntry,
			Similarity: bestSim,
			Source:     "semantic",
		}, nil
	}

	atomic.AddInt64(&e.misses, 1)
	return &CacheLookupResult{Hit: false, Similarity: bestSim}, nil
}

// ─── T108: Cache Write on Response ──────────────────────────

// Store writes a new prompt→response pair to the cache.
func (e *Engine) Store(
	ctx context.Context,
	namespace, model, prompt string,
	response []byte,
	tokensSaved int,
) (*CacheEntry, error) {
	normalized := normalizePrompt(prompt)
	promptHash := hashPrompt(normalized)

	// Generate embedding
	embedding, err := e.embedFn(ctx, prompt, model)
	if err != nil {
		return nil, fmt.Errorf("embedding generation failed: %w", err)
	}

	// Determine TTL (T110)
	ttl := e.config.DefaultTTL
	if override, ok := e.config.ModelTTLOverrides[model]; ok {
		ttl = override
	}

	now := time.Now()
	entry := &CacheEntry{
		ID:          fmt.Sprintf("%s-%s", namespace, promptHash[:12]),
		Namespace:   namespace,
		Model:       model,
		PromptHash:  promptHash,
		Embedding:   embedding,
		Response:    response,
		TokensSaved: tokensSaved,
		CreatedAt:   now,
		ExpiresAt:   now.Add(ttl),
		HitCount:    0,
	}

	e.mu.Lock()
	defer e.mu.Unlock()

	// Check capacity and evict if needed
	entries := e.store[namespace]
	if len(entries) >= e.config.MaxEntries {
		e.evictOldest(namespace)
	}

	// Add to store and exact index
	e.store[namespace] = append(e.store[namespace], entry)
	exactKey := fmt.Sprintf("%s:%s", namespace, promptHash)
	e.exactIndex[exactKey] = entry

	e.logger.Debug().
		Str("namespace", namespace).
		Str("model", model).
		Str("entry_id", entry.ID).
		Int("tokens_saved", tokensSaved).
		Msg("cached response")

	return entry, nil
}

// ─── T112: Cache Bypass ─────────────────────────────────────

// ShouldBypass checks request headers for cache bypass signals.
func ShouldBypass(headers map[string]string) bool {
	if v, ok := headers["X-Cache-Bypass"]; ok && strings.EqualFold(v, "true") {
		return true
	}
	if v, ok := headers["Cache-Control"]; ok && strings.Contains(strings.ToLower(v), "no-cache") {
		return true
	}
	return false
}

// ─── T114: Cache Invalidation ───────────────────────────────

// Invalidate removes a specific entry by ID.
func (e *Engine) Invalidate(namespace, entryID string) bool {
	e.mu.Lock()
	defer e.mu.Unlock()

	entries := e.store[namespace]
	for i, entry := range entries {
		if entry.ID == entryID {
			// Remove from exact index
			exactKey := fmt.Sprintf("%s:%s", namespace, entry.PromptHash)
			delete(e.exactIndex, exactKey)
			// Remove from store
			e.store[namespace] = append(entries[:i], entries[i+1:]...)
			atomic.AddInt64(&e.evictions, 1)
			return true
		}
	}
	return false
}

// FlushNamespace removes all entries for a namespace (T114).
func (e *Engine) FlushNamespace(namespace string) int {
	e.mu.Lock()
	defer e.mu.Unlock()

	entries := e.store[namespace]
	count := len(entries)

	for _, entry := range entries {
		exactKey := fmt.Sprintf("%s:%s", namespace, entry.PromptHash)
		delete(e.exactIndex, exactKey)
	}
	delete(e.store, namespace)
	atomic.AddInt64(&e.evictions, int64(count))

	return count
}

// FlushAll removes all entries from all namespaces.
func (e *Engine) FlushAll() int {
	e.mu.Lock()
	defer e.mu.Unlock()

	total := 0
	for ns, entries := range e.store {
		total += len(entries)
		for _, entry := range entries {
			exactKey := fmt.Sprintf("%s:%s", ns, entry.PromptHash)
			delete(e.exactIndex, exactKey)
		}
	}
	e.store = make(map[string][]*CacheEntry)
	atomic.AddInt64(&e.evictions, int64(total))

	return total
}

// ─── T113: Cache Metrics ────────────────────────────────────

// Stats returns current cache performance metrics.
func (e *Engine) Stats() CacheStats {
	hits := atomic.LoadInt64(&e.hits)
	misses := atomic.LoadInt64(&e.misses)
	evictions := atomic.LoadInt64(&e.evictions)
	totalSaved := atomic.LoadInt64(&e.totalSaved)

	total := hits + misses
	hitRate := float64(0)
	if total > 0 {
		hitRate = float64(hits) / float64(total) * 100
	}

	e.mu.RLock()
	var avgSim float64
	if e.simCount > 0 {
		avgSim = e.simSum / float64(e.simCount)
	}
	var entryCount int64
	for _, entries := range e.store {
		entryCount += int64(len(entries))
	}
	e.mu.RUnlock()

	return CacheStats{
		Hits:          hits,
		Misses:        misses,
		Evictions:     evictions,
		Entries:       entryCount,
		HitRate:       math.Round(hitRate*100) / 100,
		AvgSimilarity: math.Round(avgSim*1000) / 1000,
		TotalSaved:    totalSaved,
	}
}

// ─── T115: Cache Poisoning Prevention ───────────────────────

func (e *Engine) validateResponse(entry *CacheEntry) bool {
	// Check minimum length
	if len(entry.Response) < e.config.MinResponseLength {
		return false
	}

	// Validate JSON structure (responses should be valid JSON)
	var parsed map[string]interface{}
	if err := json.Unmarshal(entry.Response, &parsed); err != nil {
		return false
	}

	// Check for error responses that shouldn't be cached
	if errField, ok := parsed["error"]; ok && errField != nil {
		return false
	}

	// Check for empty choices array
	if choices, ok := parsed["choices"]; ok {
		if arr, ok := choices.([]interface{}); ok && len(arr) == 0 {
			return false
		}
	}

	return true
}

// ─── Internal Helpers ───────────────────────────────────────

func (e *Engine) evictEntry(entry *CacheEntry) {
	e.mu.Lock()
	defer e.mu.Unlock()

	entries := e.store[entry.Namespace]
	for i, e2 := range entries {
		if e2.ID == entry.ID {
			exactKey := fmt.Sprintf("%s:%s", entry.Namespace, entry.PromptHash)
			delete(e.exactIndex, exactKey)
			e.store[entry.Namespace] = append(entries[:i], entries[i+1:]...)
			atomic.AddInt64(&e.evictions, 1)
			return
		}
	}
}

func (e *Engine) evictOldest(namespace string) {
	entries := e.store[namespace]
	if len(entries) == 0 {
		return
	}

	// Find oldest by creation time
	oldest := 0
	for i, entry := range entries {
		if entry.CreatedAt.Before(entries[oldest].CreatedAt) {
			oldest = i
		}
	}

	entry := entries[oldest]
	exactKey := fmt.Sprintf("%s:%s", namespace, entry.PromptHash)
	delete(e.exactIndex, exactKey)
	e.store[namespace] = append(entries[:oldest], entries[oldest+1:]...)
	atomic.AddInt64(&e.evictions, 1)
}

// normalizePrompt strips whitespace and lowercases for consistent hashing.
func normalizePrompt(prompt string) string {
	return strings.ToLower(strings.TrimSpace(prompt))
}

// hashPrompt returns SHA-256 hex digest of a prompt string.
func hashPrompt(prompt string) string {
	h := sha256.Sum256([]byte(prompt))
	return hex.EncodeToString(h[:])
}

// cosineSimilarity computes the cosine similarity between two vectors.
func cosineSimilarity(a, b []float64) float64 {
	if len(a) != len(b) || len(a) == 0 {
		return 0
	}

	var dotProduct, normA, normB float64
	for i := range a {
		dotProduct += a[i] * b[i]
		normA += a[i] * a[i]
		normB += b[i] * b[i]
	}

	if normA == 0 || normB == 0 {
		return 0
	}

	return dotProduct / (math.Sqrt(normA) * math.Sqrt(normB))
}
