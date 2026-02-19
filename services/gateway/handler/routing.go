/*
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L2
Logic:       REST API handler for routing rule CRUD (T091).
             Wraps the routing engine with HTTP endpoints.
Root Cause:  Sprint task T091 — Routing rule CRUD API.
Context:     Exposes rule management at /v1/routing/rules.
Suitability: L2 — standard REST handler wrapping engine.
──────────────────────────────────────────────────────────────
*/

package handler

import (
	"encoding/json"
	"fmt"
	"net/http"
	"time"

	"github.com/go-chi/chi/v5"
	"github.com/rs/zerolog"

	"github.com/AlfredDev/alfred/services/gateway/routing"
)

// RoutingHandler handles routing rule REST API requests.
type RoutingHandler struct {
	engine   *routing.Engine
	failover *routing.FailoverState
	logger   zerolog.Logger
}

// NewRoutingHandler creates a new routing handler.
func NewRoutingHandler(engine *routing.Engine, failover *routing.FailoverState, logger zerolog.Logger) *RoutingHandler {
	return &RoutingHandler{
		engine:   engine,
		failover: failover,
		logger:   logger.With().Str("handler", "routing").Logger(),
	}
}

// ListRules handles GET /v1/routing/rules (T091).
func (h *RoutingHandler) ListRules(w http.ResponseWriter, r *http.Request) {
	rules := h.engine.ListRules()
	writeJSON(w, http.StatusOK, map[string]interface{}{
		"rules": rules,
		"total": len(rules),
	})
}

// CreateRule handles POST /v1/routing/rules (T091).
func (h *RoutingHandler) CreateRule(w http.ResponseWriter, r *http.Request) {
	var rule routing.Rule
	if err := json.NewDecoder(r.Body).Decode(&rule); err != nil {
		writeJSON(w, http.StatusBadRequest, map[string]string{"error": "invalid rule JSON"})
		return
	}

	if rule.ID == "" || rule.Name == "" {
		writeJSON(w, http.StatusBadRequest, map[string]string{"error": "id and name are required"})
		return
	}

	h.engine.AddRule(rule)
	h.logger.Info().Str("rule_id", rule.ID).Str("name", rule.Name).Msg("routing rule created")
	writeJSON(w, http.StatusCreated, rule)
}

// GetRule handles GET /v1/routing/rules/{id}.
func (h *RoutingHandler) GetRule(w http.ResponseWriter, r *http.Request) {
	id := chi.URLParam(r, "id")
	rule, found := h.engine.GetRule(id)
	if !found {
		writeJSON(w, http.StatusNotFound, map[string]string{"error": "rule not found"})
		return
	}
	writeJSON(w, http.StatusOK, rule)
}

// UpdateRule handles PUT /v1/routing/rules/{id}.
func (h *RoutingHandler) UpdateRule(w http.ResponseWriter, r *http.Request) {
	id := chi.URLParam(r, "id")

	var rule routing.Rule
	if err := json.NewDecoder(r.Body).Decode(&rule); err != nil {
		writeJSON(w, http.StatusBadRequest, map[string]string{"error": "invalid rule JSON"})
		return
	}
	rule.ID = id

	if err := h.engine.UpdateRule(rule); err != nil {
		writeJSON(w, http.StatusNotFound, map[string]string{"error": err.Error()})
		return
	}
	writeJSON(w, http.StatusOK, rule)
}

// DeleteRule handles DELETE /v1/routing/rules/{id}.
func (h *RoutingHandler) DeleteRule(w http.ResponseWriter, r *http.Request) {
	id := chi.URLParam(r, "id")
	if err := h.engine.DeleteRule(id); err != nil {
		writeJSON(w, http.StatusNotFound, map[string]string{"error": err.Error()})
		return
	}
	w.WriteHeader(http.StatusNoContent)
}

// EvaluateRouting handles POST /v1/routing/evaluate (T092).
// Accepts a routing context and returns the routing decision.
func (h *RoutingHandler) EvaluateRouting(w http.ResponseWriter, r *http.Request) {
	var rc routing.RoutingContext
	if err := json.NewDecoder(r.Body).Decode(&rc); err != nil {
		writeJSON(w, http.StatusBadRequest, map[string]string{"error": "invalid context JSON"})
		return
	}

	if rc.RequestTime.IsZero() {
		rc.RequestTime = time.Now().UTC()
	}

	decision := h.engine.Evaluate(r.Context(), rc)

	// Apply failover if decision has fallbacks (T094).
	if decision != nil && decision.Provider != "" && h.failover != nil {
		actual := h.failover.SelectProvider(decision.Provider, decision.Fallbacks)
		if actual != decision.Provider {
			decision.Reason += fmt.Sprintf("; failover from %s to %s", decision.Provider, actual)
			decision.Provider = actual
		}
	}

	writeJSON(w, http.StatusOK, decision)
}
