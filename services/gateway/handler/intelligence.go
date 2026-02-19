/*
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L3
Logic:       HTTP handlers for intelligence features: classification,
             forecasting, anomaly detection, ROI, efficiency,
             arbitrage, and traffic replay.
Root Cause:  Sprint tasks T155-T164 — Intelligence module API.
Context:     REST endpoints for intelligence engine features.
Suitability: L3 — analytics + ML intelligence endpoints.
──────────────────────────────────────────────────────────────
*/

package handler

import (
	"encoding/json"
	"net/http"

	"github.com/rs/zerolog"

	"github.com/AlfredDev/alfred/services/gateway/intelligence"
)

// IntelligenceHandler provides HTTP handlers for intelligence features.
type IntelligenceHandler struct {
	classifier      *intelligence.Classifier
	forecaster      *intelligence.Forecaster
	anomalyDetector *intelligence.AnomalyDetector
	featureTracker  *intelligence.FeatureTracker
	arbitrageEngine *intelligence.ArbitrageEngine
	trafficRecorder *intelligence.TrafficRecorder
	logger          zerolog.Logger
}

// NewIntelligenceHandler creates a new intelligence handler.
func NewIntelligenceHandler(
	classifier *intelligence.Classifier,
	forecaster *intelligence.Forecaster,
	anomalyDetector *intelligence.AnomalyDetector,
	featureTracker *intelligence.FeatureTracker,
	arbitrageEngine *intelligence.ArbitrageEngine,
	trafficRecorder *intelligence.TrafficRecorder,
	logger zerolog.Logger,
) *IntelligenceHandler {
	return &IntelligenceHandler{
		classifier:      classifier,
		forecaster:      forecaster,
		anomalyDetector: anomalyDetector,
		featureTracker:  featureTracker,
		arbitrageEngine: arbitrageEngine,
		trafficRecorder: trafficRecorder,
		logger:          logger,
	}
}

// Classify handles POST /v1/intelligence/classify.
func (h *IntelligenceHandler) Classify(w http.ResponseWriter, r *http.Request) {
	var body struct {
		Prompt string `json:"prompt"`
	}
	if err := json.NewDecoder(r.Body).Decode(&body); err != nil {
		writeError(w, http.StatusBadRequest, "invalid_json", err.Error())
		return
	}

	category := h.classifier.Classify(body.Prompt)
	scores := h.classifier.ClassifyWithScores(body.Prompt)

	writeJSON(w, http.StatusOK, map[string]interface{}{
		"category": category,
		"scores":   scores,
	})
}

// Forecast handles POST /v1/intelligence/forecast.
func (h *IntelligenceHandler) Forecast(w http.ResponseWriter, r *http.Request) {
	var body struct {
		BudgetLimit float64                       `json:"budget_limit"`
		History     []intelligence.SpendDataPoint `json:"history"`
	}
	if err := json.NewDecoder(r.Body).Decode(&body); err != nil {
		writeError(w, http.StatusBadRequest, "invalid_json", err.Error())
		return
	}

	result := h.forecaster.Forecast(body.History, body.BudgetLimit)
	writeJSON(w, http.StatusOK, result)
}

// DetectAnomaly handles POST /v1/intelligence/anomaly.
func (h *IntelligenceHandler) DetectAnomaly(w http.ResponseWriter, r *http.Request) {
	var body struct {
		Values []float64 `json:"values"`
		Latest float64   `json:"latest"`
	}
	if err := json.NewDecoder(r.Body).Decode(&body); err != nil {
		writeError(w, http.StatusBadRequest, "invalid_json", err.Error())
		return
	}

	result := h.anomalyDetector.Check(body.Values, body.Latest)
	writeJSON(w, http.StatusOK, result)
}

// RecordFeatureCost handles POST /v1/intelligence/features/cost.
func (h *IntelligenceHandler) RecordFeatureCost(w http.ResponseWriter, r *http.Request) {
	var body struct {
		FeatureID string  `json:"feature_id"`
		Cost      float64 `json:"cost"`
		Tokens    int64   `json:"tokens"`
	}
	if err := json.NewDecoder(r.Body).Decode(&body); err != nil {
		writeError(w, http.StatusBadRequest, "invalid_json", err.Error())
		return
	}

	h.featureTracker.Record(body.FeatureID, body.Cost, body.Tokens)
	writeJSON(w, http.StatusOK, map[string]string{"status": "recorded"})
}

// GetFeatureCosts handles GET /v1/intelligence/features.
func (h *IntelligenceHandler) GetFeatureCosts(w http.ResponseWriter, r *http.Request) {
	features := h.featureTracker.GetAll()
	writeJSON(w, http.StatusOK, features)
}

// CalculateROI handles POST /v1/intelligence/roi.
func (h *IntelligenceHandler) CalculateROI(w http.ResponseWriter, r *http.Request) {
	var input intelligence.ROIInput
	if err := json.NewDecoder(r.Body).Decode(&input); err != nil {
		writeError(w, http.StatusBadRequest, "invalid_json", err.Error())
		return
	}

	result := intelligence.CalculateROI(input)
	writeJSON(w, http.StatusOK, result)
}

// CalculateEfficiency handles POST /v1/intelligence/efficiency.
func (h *IntelligenceHandler) CalculateEfficiency(w http.ResponseWriter, r *http.Request) {
	var input intelligence.EfficiencyInput
	if err := json.NewDecoder(r.Body).Decode(&input); err != nil {
		writeError(w, http.StatusBadRequest, "invalid_json", err.Error())
		return
	}

	result := intelligence.CalculateEfficiency(input)
	writeJSON(w, http.StatusOK, result)
}

// FindArbitrage handles GET /v1/intelligence/arbitrage.
func (h *IntelligenceHandler) FindArbitrage(w http.ResponseWriter, r *http.Request) {
	opportunities := h.arbitrageEngine.FindOpportunities()
	writeJSON(w, http.StatusOK, opportunities)
}

// UpdateArbitragePrices handles POST /v1/intelligence/arbitrage/prices.
func (h *IntelligenceHandler) UpdateArbitragePrices(w http.ResponseWriter, r *http.Request) {
	var body struct {
		Model     string  `json:"model"`
		Provider  string  `json:"provider"`
		InputPer1K  float64 `json:"input_per_1k"`
		OutputPer1K float64 `json:"output_per_1k"`
	}
	if err := json.NewDecoder(r.Body).Decode(&body); err != nil {
		writeError(w, http.StatusBadRequest, "invalid_json", err.Error())
		return
	}

	h.arbitrageEngine.UpdatePrices(body.Model, body.Provider, body.InputPer1K, body.OutputPer1K)
	writeJSON(w, http.StatusOK, map[string]string{"status": "updated"})
}

// RecordTraffic handles POST /v1/intelligence/traffic/record.
func (h *IntelligenceHandler) RecordTraffic(w http.ResponseWriter, r *http.Request) {
	var req intelligence.RecordedRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeError(w, http.StatusBadRequest, "invalid_json", err.Error())
		return
	}

	h.trafficRecorder.Record(req)
	writeJSON(w, http.StatusOK, map[string]string{"status": "recorded"})
}

// SimulateTraffic handles POST /v1/intelligence/traffic/simulate.
func (h *IntelligenceHandler) SimulateTraffic(w http.ResponseWriter, r *http.Request) {
	var body struct {
		AlternativeModel string `json:"alternative_model"`
	}
	if err := json.NewDecoder(r.Body).Decode(&body); err != nil {
		writeError(w, http.StatusBadRequest, "invalid_json", err.Error())
		return
	}

	result := h.trafficRecorder.Simulate(body.AlternativeModel, h.arbitrageEngine)
	writeJSON(w, http.StatusOK, result)
}
