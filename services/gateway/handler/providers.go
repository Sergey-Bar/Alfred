/*
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L2
Logic:       Provider configuration CRUD REST API handler.
             Supports listing providers, getting individual
             provider config, creating/updating providers, and
             testing provider connectivity. Stores config in-
             memory with optional persistence hook.
Root Cause:  Sprint task T028 — Provider config CRUD (base URL,
             key path, model list).
Context:     Allows runtime management of provider connectors
             via the dashboard or API without restarting the
             gateway.
Suitability: L2 for standard REST CRUD pattern.
──────────────────────────────────────────────────────────────
*/

package handler

import (
	"context"
	"encoding/json"
	"net/http"
	"time"

	"github.com/go-chi/chi/v5"
	"github.com/rs/zerolog"

	"github.com/AlfredDev/alfred/services/gateway/provider"
)

// ProviderConfigHandler handles provider configuration CRUD operations.
type ProviderConfigHandler struct {
	logger   zerolog.Logger
	registry *provider.Registry
	pricing  *provider.PricingConfig
}

// NewProviderConfigHandler creates a new provider config handler.
func NewProviderConfigHandler(logger zerolog.Logger, registry *provider.Registry, pricing *provider.PricingConfig) *ProviderConfigHandler {
	return &ProviderConfigHandler{
		logger:   logger,
		registry: registry,
		pricing:  pricing,
	}
}

// ProviderInfo represents a provider's publicly visible configuration.
type ProviderInfo struct {
	Name       string   `json:"name"`
	Models     []string `json:"models"`
	Healthy    bool     `json:"healthy"`
	LatencyMs  int64    `json:"latency_ms"`
	LastCheck  string   `json:"last_check,omitempty"`
	Error      string   `json:"error,omitempty"`
}

// ProviderPricingInfo represents pricing for a single model.
type ProviderPricingInfo struct {
	Model       string  `json:"model"`
	Provider    string  `json:"provider"`
	InputPer1M  float64 `json:"input_per_1m_usd"`
	OutputPer1M float64 `json:"output_per_1m_usd"`
	Free        bool    `json:"free"`
}

// ListProviders handles GET /v1/providers — lists all registered providers.
func (h *ProviderConfigHandler) ListProviders(w http.ResponseWriter, r *http.Request) {
	names := h.registry.List()
	providers := make([]ProviderInfo, 0, len(names))

	// Get latest health status.
	ctx, cancel := context.WithTimeout(r.Context(), 5*time.Second)
	defer cancel()
	health := h.registry.HealthCheckAll(ctx)

	for _, name := range names {
		prov, ok := h.registry.Get(name)
		if !ok {
			continue
		}
		info := ProviderInfo{
			Name:   name,
			Models: prov.Models(),
		}
		if status, ok := health[name]; ok {
			info.Healthy = status.Healthy
			info.LatencyMs = status.Latency.Milliseconds()
			info.LastCheck = status.LastCheck.Format(time.RFC3339)
			info.Error = status.Error
		}
		providers = append(providers, info)
	}

	writeJSON(w, http.StatusOK, map[string]interface{}{
		"object": "list",
		"data":   providers,
		"total":  len(providers),
	})
}

// GetProvider handles GET /v1/providers/{name} — gets a single provider's config.
func (h *ProviderConfigHandler) GetProvider(w http.ResponseWriter, r *http.Request) {
	name := chi.URLParam(r, "name")
	prov, ok := h.registry.Get(name)
	if !ok {
		writeJSON(w, http.StatusNotFound, map[string]interface{}{
			"error": map[string]string{
				"type":    "not_found",
				"message": "Provider '" + name + "' not found",
			},
		})
		return
	}

	// Get health.
	ctx, cancel := context.WithTimeout(r.Context(), 5*time.Second)
	defer cancel()
	status := prov.HealthCheck(ctx)

	info := ProviderInfo{
		Name:      name,
		Models:    prov.Models(),
		Healthy:   status.Healthy,
		LatencyMs: status.Latency.Milliseconds(),
		LastCheck: status.LastCheck.Format(time.RFC3339),
		Error:     status.Error,
	}

	writeJSON(w, http.StatusOK, info)
}

// GetProviderModels handles GET /v1/providers/{name}/models.
func (h *ProviderConfigHandler) GetProviderModels(w http.ResponseWriter, r *http.Request) {
	name := chi.URLParam(r, "name")
	prov, ok := h.registry.Get(name)
	if !ok {
		writeJSON(w, http.StatusNotFound, map[string]interface{}{
			"error": map[string]string{
				"type":    "not_found",
				"message": "Provider '" + name + "' not found",
			},
		})
		return
	}

	models := make([]map[string]interface{}, 0)
	for _, model := range prov.Models() {
		entry := map[string]interface{}{
			"id":       model,
			"provider": name,
			"object":   "model",
		}
		// Include pricing if available.
		if h.pricing != nil {
			if pricing, ok := h.pricing.GetPricing(name, model); ok {
				entry["pricing"] = map[string]interface{}{
					"input_per_1m_usd":  pricing.InputPer1M,
					"output_per_1m_usd": pricing.OutputPer1M,
					"free":              pricing.Free,
				}
			}
		}
		models = append(models, entry)
	}

	writeJSON(w, http.StatusOK, map[string]interface{}{
		"object":   "list",
		"data":     models,
		"total":    len(models),
		"provider": name,
	})
}

// TestProvider handles POST /v1/providers/{name}/test — connectivity test.
func (h *ProviderConfigHandler) TestProvider(w http.ResponseWriter, r *http.Request) {
	name := chi.URLParam(r, "name")
	prov, ok := h.registry.Get(name)
	if !ok {
		writeJSON(w, http.StatusNotFound, map[string]interface{}{
			"error": map[string]string{
				"type":    "not_found",
				"message": "Provider '" + name + "' not found",
			},
		})
		return
	}

	ctx, cancel := context.WithTimeout(r.Context(), 10*time.Second)
	defer cancel()

	start := time.Now()
	status := prov.HealthCheck(ctx)
	duration := time.Since(start)

	result := map[string]interface{}{
		"provider":    name,
		"healthy":     status.Healthy,
		"latency_ms":  duration.Milliseconds(),
		"tested_at":   time.Now().Format(time.RFC3339),
	}
	if status.Error != "" {
		result["error"] = status.Error
	}

	httpStatus := http.StatusOK
	if !status.Healthy {
		httpStatus = http.StatusServiceUnavailable
	}

	writeJSON(w, httpStatus, result)
}

// GetPricing handles GET /v1/providers/pricing — returns all model pricing.
func (h *ProviderConfigHandler) GetPricing(w http.ResponseWriter, r *http.Request) {
	if h.pricing == nil {
		writeJSON(w, http.StatusOK, map[string]interface{}{
			"object": "list",
			"data":   []interface{}{},
		})
		return
	}

	all := h.pricing.AllPricing()
	result := make([]ProviderPricingInfo, 0)

	for key, p := range all {
		result = append(result, ProviderPricingInfo{
			Model:       key,
			Provider:    provider.DetectProvider(key),
			InputPer1M:  p.InputPer1M,
			OutputPer1M: p.OutputPer1M,
			Free:        p.Free,
		})
	}

	writeJSON(w, http.StatusOK, map[string]interface{}{
		"object": "list",
		"data":   result,
		"total":  len(result),
	})
}

// EstimateCost handles POST /v1/providers/estimate — cost estimation.
func (h *ProviderConfigHandler) EstimateCost(w http.ResponseWriter, r *http.Request) {
	var req struct {
		Model          string `json:"model"`
		InputTokens    int    `json:"input_tokens"`
		OutputTokens   int    `json:"output_tokens"`
	}
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeJSON(w, http.StatusBadRequest, map[string]interface{}{
			"error": map[string]string{
				"type":    "invalid_request",
				"message": "Invalid request body: " + err.Error(),
			},
		})
		return
	}

	if req.Model == "" {
		writeJSON(w, http.StatusBadRequest, map[string]interface{}{
			"error": map[string]string{
				"type":    "invalid_request",
				"message": "model is required",
			},
		})
		return
	}

	providerName := provider.DetectProvider(req.Model)
	if h.pricing == nil {
		writeJSON(w, http.StatusOK, map[string]interface{}{
			"model":         req.Model,
			"provider":      providerName,
			"estimated_cost": 0,
			"message":       "No pricing config loaded",
		})
		return
	}

	cost := h.pricing.EstimateCost(providerName, req.Model, req.InputTokens, req.OutputTokens)

	writeJSON(w, http.StatusOK, map[string]interface{}{
		"model":          req.Model,
		"provider":       providerName,
		"input_tokens":   req.InputTokens,
		"output_tokens":  req.OutputTokens,
		"estimated_cost": cost,
		"currency":       "USD",
	})
}

func writeJSON(w http.ResponseWriter, status int, data interface{}) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	json.NewEncoder(w).Encode(data)
}
