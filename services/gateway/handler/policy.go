/*
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L3
Logic:       HTTP handlers for OPA policy CRUD, evaluation,
             and built-in policy template listing.
Root Cause:  Sprint tasks T132-T137 — Policy management API.
Context:     REST endpoints for the OPA policy engine in policy/.
Suitability: L3 — policy evaluation with enforcement decisions.
──────────────────────────────────────────────────────────────
*/

package handler

import (
	"encoding/json"
	"net/http"

	"github.com/go-chi/chi/v5"
	"github.com/rs/zerolog"

	"github.com/AlfredDev/alfred/services/gateway/policy"
)

// PolicyHandler provides HTTP handlers for policy management.
type PolicyHandler struct {
	client *policy.OPAClient
	logger zerolog.Logger
}

// NewPolicyHandler creates a new policy handler.
func NewPolicyHandler(client *policy.OPAClient, logger zerolog.Logger) *PolicyHandler {
	return &PolicyHandler{client: client, logger: logger}
}

// ListPolicies handles GET /v1/policies.
func (h *PolicyHandler) ListPolicies(w http.ResponseWriter, r *http.Request) {
	policies := h.client.ListPolicies()
	writeJSON(w, http.StatusOK, policies)
}

// CreatePolicy handles POST /v1/policies.
func (h *PolicyHandler) CreatePolicy(w http.ResponseWriter, r *http.Request) {
	var pol policy.Policy
	if err := json.NewDecoder(r.Body).Decode(&pol); err != nil {
		writeError(w, http.StatusBadRequest, "invalid_json", err.Error())
		return
	}

	created, err := h.client.CreatePolicy(pol)
	if err != nil {
		writeError(w, http.StatusBadRequest, "create_failed", err.Error())
		return
	}

	h.logger.Info().Str("id", created.ID).Str("name", created.Name).Msg("policy created")
	writeJSON(w, http.StatusCreated, created)
}

// GetPolicy handles GET /v1/policies/{id}.
func (h *PolicyHandler) GetPolicy(w http.ResponseWriter, r *http.Request) {
	id := chi.URLParam(r, "id")
	pol, err := h.client.GetPolicy(id)
	if err != nil {
		writeError(w, http.StatusNotFound, "not_found", err.Error())
		return
	}
	writeJSON(w, http.StatusOK, pol)
}

// UpdatePolicy handles PUT /v1/policies/{id}.
func (h *PolicyHandler) UpdatePolicy(w http.ResponseWriter, r *http.Request) {
	id := chi.URLParam(r, "id")
	var pol policy.Policy
	if err := json.NewDecoder(r.Body).Decode(&pol); err != nil {
		writeError(w, http.StatusBadRequest, "invalid_json", err.Error())
		return
	}
	pol.ID = id

	updated, err := h.client.UpdatePolicy(pol)
	if err != nil {
		writeError(w, http.StatusBadRequest, "update_failed", err.Error())
		return
	}

	h.logger.Info().Str("id", id).Msg("policy updated")
	writeJSON(w, http.StatusOK, updated)
}

// DeletePolicy handles DELETE /v1/policies/{id}.
func (h *PolicyHandler) DeletePolicy(w http.ResponseWriter, r *http.Request) {
	id := chi.URLParam(r, "id")
	if err := h.client.DeletePolicy(id); err != nil {
		writeError(w, http.StatusNotFound, "not_found", err.Error())
		return
	}
	h.logger.Info().Str("id", id).Msg("policy deleted")
	w.WriteHeader(http.StatusNoContent)
}

// EvaluatePolicy handles POST /v1/policies/evaluate.
func (h *PolicyHandler) EvaluatePolicy(w http.ResponseWriter, r *http.Request) {
	var input policy.PolicyInput
	if err := json.NewDecoder(r.Body).Decode(&input); err != nil {
		writeError(w, http.StatusBadRequest, "invalid_json", err.Error())
		return
	}

	result := h.client.Evaluate(input)
	writeJSON(w, http.StatusOK, result)
}

// GetEvaluationLog handles GET /v1/policies/evaluations.
func (h *PolicyHandler) GetEvaluationLog(w http.ResponseWriter, r *http.Request) {
	logs := h.client.GetEvaluationLog()
	writeJSON(w, http.StatusOK, logs)
}

// ListTemplates handles GET /v1/policies/templates.
func (h *PolicyHandler) ListTemplates(w http.ResponseWriter, r *http.Request) {
	templates := h.client.ListBuiltinTemplates()
	writeJSON(w, http.StatusOK, templates)
}

// ToggleDryRun handles POST /v1/policies/{id}/dry-run.
func (h *PolicyHandler) ToggleDryRun(w http.ResponseWriter, r *http.Request) {
	id := chi.URLParam(r, "id")
	var body struct {
		DryRun bool `json:"dry_run"`
	}
	if err := json.NewDecoder(r.Body).Decode(&body); err != nil {
		writeError(w, http.StatusBadRequest, "invalid_json", err.Error())
		return
	}

	pol, err := h.client.GetPolicy(id)
	if err != nil {
		writeError(w, http.StatusNotFound, "not_found", err.Error())
		return
	}

	pol.DryRun = body.DryRun
	updated, err := h.client.UpdatePolicy(*pol)
	if err != nil {
		writeError(w, http.StatusInternalServerError, "update_failed", err.Error())
		return
	}

	writeJSON(w, http.StatusOK, updated)
}
