/*
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L2
Logic:       REST handler for semantic cache management.
             Exposes stats, invalidation, and flush endpoints.
Root Cause:  Sprint tasks T111-T114 — Cache REST API.
Context:     Admin endpoints for cache management.
Suitability: L2 — standard REST wrapping cache engine.
──────────────────────────────────────────────────────────────
*/

package handler

import (
	"net/http"

	"github.com/go-chi/chi/v5"
	"github.com/rs/zerolog"

	"github.com/AlfredDev/alfred/services/gateway/caching"
)

// CacheHandler handles cache management REST endpoints.
type CacheHandler struct {
	engine *caching.Engine
	logger zerolog.Logger
}

// NewCacheHandler creates a new cache handler.
func NewCacheHandler(engine *caching.Engine, logger zerolog.Logger) *CacheHandler {
	return &CacheHandler{
		engine: engine,
		logger: logger.With().Str("handler", "cache").Logger(),
	}
}

// Stats handles GET /v1/cache/stats (T113).
func (h *CacheHandler) Stats(w http.ResponseWriter, r *http.Request) {
	stats := h.engine.Stats()
	writeJSON(w, http.StatusOK, stats)
}

// FlushNamespace handles DELETE /v1/cache/{namespace} (T114).
func (h *CacheHandler) FlushNamespace(w http.ResponseWriter, r *http.Request) {
	namespace := chi.URLParam(r, "namespace")
	count := h.engine.FlushNamespace(namespace)
	h.logger.Info().Str("namespace", namespace).Int("evicted", count).Msg("cache namespace flushed")
	writeJSON(w, http.StatusOK, map[string]interface{}{
		"flushed":   true,
		"namespace": namespace,
		"evicted":   count,
	})
}

// FlushAll handles DELETE /v1/cache (T114).
func (h *CacheHandler) FlushAll(w http.ResponseWriter, r *http.Request) {
	count := h.engine.FlushAll()
	h.logger.Info().Int("evicted", count).Msg("full cache flush")
	writeJSON(w, http.StatusOK, map[string]interface{}{
		"flushed": true,
		"evicted": count,
	})
}

// InvalidateEntry handles DELETE /v1/cache/{namespace}/{entryId} (T114).
func (h *CacheHandler) InvalidateEntry(w http.ResponseWriter, r *http.Request) {
	namespace := chi.URLParam(r, "namespace")
	entryID := chi.URLParam(r, "entryId")

	found := h.engine.Invalidate(namespace, entryID)
	if !found {
		writeJSON(w, http.StatusNotFound, map[string]string{"error": "entry not found"})
		return
	}
	writeJSON(w, http.StatusOK, map[string]interface{}{
		"invalidated": true,
		"namespace":   namespace,
		"entry_id":    entryID,
	})
}
