/*
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L3
Logic:       HTTP handlers for experiment CRUD, variant assignment,
             result recording, and auto-switch evaluation.
Root Cause:  Sprint tasks T099-T104 — Experiment management API.
Context:     REST endpoints for the experiment engine in routing/.
Suitability: L3 — routing experimentation logic with significance tests.
──────────────────────────────────────────────────────────────
*/

package handler

import (
	"encoding/json"
	"net/http"

	"github.com/go-chi/chi/v5"
	"github.com/rs/zerolog"

	"github.com/AlfredDev/alfred/services/gateway/routing"
)

// ExperimentHandler provides HTTP handlers for experiment management.
type ExperimentHandler struct {
	engine *routing.ExperimentEngine
	logger zerolog.Logger
}

// NewExperimentHandler creates a new experiment handler.
func NewExperimentHandler(engine *routing.ExperimentEngine, logger zerolog.Logger) *ExperimentHandler {
	return &ExperimentHandler{engine: engine, logger: logger}
}

// ListExperiments handles GET /v1/experiments.
func (h *ExperimentHandler) ListExperiments(w http.ResponseWriter, r *http.Request) {
	experiments := h.engine.ListExperiments()
	writeJSON(w, http.StatusOK, experiments)
}

// CreateExperiment handles POST /v1/experiments.
func (h *ExperimentHandler) CreateExperiment(w http.ResponseWriter, r *http.Request) {
	var exp routing.Experiment
	if err := json.NewDecoder(r.Body).Decode(&exp); err != nil {
		writeError(w, http.StatusBadRequest, "invalid_json", err.Error())
		return
	}

	created, err := h.engine.CreateExperiment(exp)
	if err != nil {
		writeError(w, http.StatusBadRequest, "create_failed", err.Error())
		return
	}

	h.logger.Info().Str("id", created.ID).Str("name", created.Name).Msg("experiment created")
	writeJSON(w, http.StatusCreated, created)
}

// GetExperiment handles GET /v1/experiments/{id}.
func (h *ExperimentHandler) GetExperiment(w http.ResponseWriter, r *http.Request) {
	id := chi.URLParam(r, "id")
	exp, err := h.engine.GetExperiment(id)
	if err != nil {
		writeError(w, http.StatusNotFound, "not_found", err.Error())
		return
	}
	writeJSON(w, http.StatusOK, exp)
}

// StartExperiment handles POST /v1/experiments/{id}/start.
func (h *ExperimentHandler) StartExperiment(w http.ResponseWriter, r *http.Request) {
	id := chi.URLParam(r, "id")
	if err := h.engine.StartExperiment(id); err != nil {
		writeError(w, http.StatusBadRequest, "start_failed", err.Error())
		return
	}
	h.logger.Info().Str("id", id).Msg("experiment started")
	writeJSON(w, http.StatusOK, map[string]string{"status": "running", "id": id})
}

// PauseExperiment handles POST /v1/experiments/{id}/pause.
func (h *ExperimentHandler) PauseExperiment(w http.ResponseWriter, r *http.Request) {
	id := chi.URLParam(r, "id")
	if err := h.engine.PauseExperiment(id); err != nil {
		writeError(w, http.StatusBadRequest, "pause_failed", err.Error())
		return
	}
	writeJSON(w, http.StatusOK, map[string]string{"status": "paused", "id": id})
}

// ConcludeExperiment handles POST /v1/experiments/{id}/conclude.
func (h *ExperimentHandler) ConcludeExperiment(w http.ResponseWriter, r *http.Request) {
	id := chi.URLParam(r, "id")
	winner := r.URL.Query().Get("winner")
	if err := h.engine.ConcludeExperiment(id, winner); err != nil {
		writeError(w, http.StatusBadRequest, "conclude_failed", err.Error())
		return
	}
	h.logger.Info().Str("id", id).Str("winner", winner).Msg("experiment concluded")
	writeJSON(w, http.StatusOK, map[string]string{"status": "concluded", "id": id, "winner": winner})
}

// DeleteExperiment handles DELETE /v1/experiments/{id}.
func (h *ExperimentHandler) DeleteExperiment(w http.ResponseWriter, r *http.Request) {
	id := chi.URLParam(r, "id")
	if err := h.engine.DeleteExperiment(id); err != nil {
		writeError(w, http.StatusNotFound, "not_found", err.Error())
		return
	}
	w.WriteHeader(http.StatusNoContent)
}

// AssignVariant handles POST /v1/experiments/{id}/assign.
func (h *ExperimentHandler) AssignVariant(w http.ResponseWriter, r *http.Request) {
	id := chi.URLParam(r, "id")
	var body struct {
		RequestKey string `json:"request_key"`
	}
	if err := json.NewDecoder(r.Body).Decode(&body); err != nil {
		writeError(w, http.StatusBadRequest, "invalid_json", err.Error())
		return
	}

	variant, err := h.engine.AssignVariant(id, body.RequestKey)
	if err != nil {
		writeError(w, http.StatusBadRequest, "assign_failed", err.Error())
		return
	}
	writeJSON(w, http.StatusOK, variant)
}

// RecordResult handles POST /v1/experiments/{id}/result.
func (h *ExperimentHandler) RecordResult(w http.ResponseWriter, r *http.Request) {
	id := chi.URLParam(r, "id")
	var body struct {
		VariantName string  `json:"variant_name"`
		Latency     float64 `json:"latency_ms"`
		Cost        float64 `json:"cost"`
		IsError     bool    `json:"is_error"`
	}
	if err := json.NewDecoder(r.Body).Decode(&body); err != nil {
		writeError(w, http.StatusBadRequest, "invalid_json", err.Error())
		return
	}

	if err := h.engine.RecordResult(id, body.VariantName, body.Latency, body.Cost, body.IsError); err != nil {
		writeError(w, http.StatusBadRequest, "record_failed", err.Error())
		return
	}
	writeJSON(w, http.StatusOK, map[string]string{"status": "recorded"})
}

// GetMetrics handles GET /v1/experiments/{id}/metrics.
func (h *ExperimentHandler) GetMetrics(w http.ResponseWriter, r *http.Request) {
	id := chi.URLParam(r, "id")
	exp, err := h.engine.GetExperiment(id)
	if err != nil {
		writeError(w, http.StatusNotFound, "not_found", err.Error())
		return
	}

	metrics := make(map[string]interface{})
	metrics["experiment_id"] = id
	metrics["metrics"] = exp.Metrics
	writeJSON(w, http.StatusOK, metrics)
}

// CompareVariants handles GET /v1/experiments/{id}/compare.
func (h *ExperimentHandler) CompareVariants(w http.ResponseWriter, r *http.Request) {
	id := chi.URLParam(r, "id")
	exp, err := h.engine.GetExperiment(id)
	if err != nil {
		writeError(w, http.StatusNotFound, "not_found", err.Error())
		return
	}

	if len(exp.Variants) < 2 {
		writeError(w, http.StatusBadRequest, "insufficient_variants", "need at least 2 variants")
		return
	}

	v1 := exp.Variants[0].Name
	v2 := exp.Variants[1].Name

	errorSig, errorZScore := h.engine.CompareErrorRates(id, v1, v2)
	costSig, costZScore := h.engine.CompareCosts(id, v1, v2)

	writeJSON(w, http.StatusOK, map[string]interface{}{
		"experiment_id":            id,
		"variant_a":               v1,
		"variant_b":               v2,
		"error_rate_significant":   errorSig,
		"error_rate_z_score":       errorZScore,
		"cost_significant":         costSig,
		"cost_z_score":             costZScore,
	})
}
