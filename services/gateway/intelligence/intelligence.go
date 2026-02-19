/*
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L3
Logic:       AI Intelligence features — usage classification,
             budget forecasting, anomaly detection, cost arbitrage,
             ROI scoring, and traffic replay simulation.
Root Cause:  Sprint tasks T155-T164 — AI Intelligence Engine.
Context:     Per PRD Section 8.6, enables cost optimization.
Suitability: L3 — statistical algorithms + ML classification.
──────────────────────────────────────────────────────────────
*/

package intelligence

import (
	"fmt"
	"math"
	"sort"
	"strings"
	"sync"
	"time"
)

// ─── T155: AI Usage Classification ──────────────────────────

type RequestCategory string

const (
	CategoryCodeGen       RequestCategory = "code_generation"
	CategorySummarization RequestCategory = "summarization"
	CategoryLegal         RequestCategory = "legal_reasoning"
	CategorySupport       RequestCategory = "customer_support"
	CategoryContent       RequestCategory = "content_creation"
	CategoryExtraction    RequestCategory = "data_extraction"
	CategoryReasoning     RequestCategory = "reasoning"
	CategoryEmbeddings    RequestCategory = "embeddings"
	CategoryOther         RequestCategory = "other"
)

// ClassificationRule is a keyword-based classifier rule.
type ClassificationRule struct {
	Category RequestCategory
	Keywords []string
	Weight   float64
}

var defaultRules = []ClassificationRule{
	{CategoryCodeGen, []string{"code", "function", "implement", "debug", "refactor", "programming", "compile", "syntax", "algorithm", "class", "method", "variable", "api", "endpoint"}, 1.0},
	{CategorySummarization, []string{"summarize", "summary", "tldr", "key points", "brief", "condense", "overview", "digest"}, 1.0},
	{CategoryLegal, []string{"legal", "contract", "compliance", "regulation", "clause", "liability", "indemnity", "jurisdiction", "statute"}, 1.0},
	{CategorySupport, []string{"customer", "support", "ticket", "help", "issue", "complaint", "troubleshoot", "faq"}, 1.0},
	{CategoryContent, []string{"write", "blog", "article", "copy", "marketing", "email", "newsletter", "documentation", "draft"}, 0.8},
	{CategoryExtraction, []string{"extract", "parse", "classify", "tag", "categorize", "entity", "ner", "sentiment", "label"}, 1.0},
	{CategoryReasoning, []string{"analyze", "reason", "evaluate", "compare", "pros cons", "decision", "planning", "strategy", "research"}, 0.8},
	{CategoryEmbeddings, []string{"embed", "embedding", "vector", "similarity", "search", "clustering"}, 1.0},
}

type Classifier struct {
	rules []ClassificationRule
}

func NewClassifier() *Classifier {
	return &Classifier{rules: defaultRules}
}

// Classify returns the most likely category for the given prompt.
func (c *Classifier) Classify(prompt string) RequestCategory {
	lower := strings.ToLower(prompt)
	scores := make(map[RequestCategory]float64)

	for _, rule := range c.rules {
		for _, kw := range rule.Keywords {
			if strings.Contains(lower, kw) {
				scores[rule.Category] += rule.Weight
			}
		}
	}

	if len(scores) == 0 {
		return CategoryOther
	}

	best := CategoryOther
	bestScore := 0.0
	for cat, score := range scores {
		if score > bestScore {
			bestScore = score
			best = cat
		}
	}
	return best
}

// ClassifyWithScores returns all category scores for analysis.
func (c *Classifier) ClassifyWithScores(prompt string) map[RequestCategory]float64 {
	lower := strings.ToLower(prompt)
	scores := make(map[RequestCategory]float64)

	for _, rule := range c.rules {
		for _, kw := range rule.Keywords {
			if strings.Contains(lower, kw) {
				scores[rule.Category] += rule.Weight
			}
		}
	}
	return scores
}

// ─── T156: Budget Forecasting (Linear Regression) ───────────

type SpendDataPoint struct {
	Date   time.Time `json:"date"`
	Amount float64   `json:"amount"`
}

type ForecastResult struct {
	PredictedDaily    float64          `json:"predicted_daily"`
	PredictedMonthly  float64          `json:"predicted_monthly"`
	DaysUntilExhaust  int              `json:"days_until_exhaust"`
	ExhaustDate       *time.Time       `json:"exhaust_date,omitempty"`
	Trend             string           `json:"trend"` // increasing, decreasing, stable
	Confidence        float64          `json:"confidence"` // R²
	Forecast          []SpendDataPoint `json:"forecast"`
}

type Forecaster struct {
	windowDays int
}

func NewForecaster(windowDays int) *Forecaster {
	if windowDays <= 0 {
		windowDays = 14
	}
	return &Forecaster{windowDays: windowDays}
}

// Forecast uses linear regression on historical spend to predict future usage.
func (f *Forecaster) Forecast(history []SpendDataPoint, budgetRemaining float64) *ForecastResult {
	if len(history) < 3 {
		return &ForecastResult{Trend: "insufficient_data", Confidence: 0}
	}

	// Sort by date
	sorted := make([]SpendDataPoint, len(history))
	copy(sorted, history)
	sort.Slice(sorted, func(i, j int) bool { return sorted[i].Date.Before(sorted[j].Date) })

	// Use last N days
	if len(sorted) > f.windowDays {
		sorted = sorted[len(sorted)-f.windowDays:]
	}

	// Linear regression: y = mx + b
	n := float64(len(sorted))
	var sumX, sumY, sumXY, sumX2 float64

	baseDate := sorted[0].Date
	for i, dp := range sorted {
		x := float64(i)
		y := dp.Amount
		sumX += x
		sumY += y
		sumXY += x * y
		sumX2 += x * x
	}

	denom := n*sumX2 - sumX*sumX
	if denom == 0 {
		avg := sumY / n
		return &ForecastResult{
			PredictedDaily:   avg,
			PredictedMonthly: avg * 30,
			Trend:            "stable",
			Confidence:       1.0,
		}
	}

	slope := (n*sumXY - sumX*sumY) / denom
	intercept := (sumY - slope*sumX) / n

	// R² calculation
	meanY := sumY / n
	var ssRes, ssTot float64
	for i, dp := range sorted {
		predicted := slope*float64(i) + intercept
		ssRes += (dp.Amount - predicted) * (dp.Amount - predicted)
		ssTot += (dp.Amount - meanY) * (dp.Amount - meanY)
	}
	rSquared := 0.0
	if ssTot > 0 {
		rSquared = 1 - ssRes/ssTot
	}

	// Predict next 30 days
	var forecast []SpendDataPoint
	nextDay := int(n)
	for i := 0; i < 30; i++ {
		predicted := slope*float64(nextDay+i) + intercept
		if predicted < 0 {
			predicted = 0
		}
		forecast = append(forecast, SpendDataPoint{
			Date:   baseDate.AddDate(0, 0, nextDay+i),
			Amount: predicted,
		})
	}

	predictedDaily := slope*float64(nextDay) + intercept
	if predictedDaily < 0 {
		predictedDaily = 0
	}

	trend := "stable"
	if slope > 0.01*meanY {
		trend = "increasing"
	} else if slope < -0.01*meanY {
		trend = "decreasing"
	}

	result := &ForecastResult{
		PredictedDaily:   predictedDaily,
		PredictedMonthly: predictedDaily * 30,
		Trend:            trend,
		Confidence:       math.Max(0, rSquared),
		Forecast:         forecast,
	}

	// Days until budget exhausted
	if predictedDaily > 0 && budgetRemaining > 0 {
		days := int(budgetRemaining / predictedDaily)
		result.DaysUntilExhaust = days
		exhaustDate := time.Now().AddDate(0, 0, days)
		result.ExhaustDate = &exhaustDate
	}

	return result
}

// ─── T157: Anomaly Detection (Z-Score) ──────────────────────

type AnomalyResult struct {
	IsAnomaly  bool    `json:"is_anomaly"`
	ZScore     float64 `json:"z_score"`
	Value      float64 `json:"value"`
	Mean       float64 `json:"mean"`
	StdDev     float64 `json:"std_dev"`
	Threshold  float64 `json:"threshold"`
	Direction  string  `json:"direction"` // "spike" or "drop"
}

type AnomalyDetector struct {
	mu         sync.RWMutex
	windowSize int
	threshold  float64 // Z-score threshold (default: 2.0 = 2σ)
	history    map[string][]float64 // key -> rolling values
}

func NewAnomalyDetector(windowSize int, threshold float64) *AnomalyDetector {
	if windowSize <= 0 {
		windowSize = 24 // 24 hours
	}
	if threshold <= 0 {
		threshold = 2.0
	}
	return &AnomalyDetector{
		windowSize: windowSize,
		threshold:  threshold,
		history:    make(map[string][]float64),
	}
}

// Check evaluates whether a new data point is anomalous.
func (d *AnomalyDetector) Check(key string, value float64) *AnomalyResult {
	d.mu.Lock()
	defer d.mu.Unlock()

	h := d.history[key]
	h = append(h, value)

	// Maintain rolling window
	if len(h) > d.windowSize {
		h = h[len(h)-d.windowSize:]
	}
	d.history[key] = h

	if len(h) < 5 {
		return &AnomalyResult{IsAnomaly: false, Value: value, Threshold: d.threshold}
	}

	// Calculate mean and std dev (excluding the new value)
	n := float64(len(h) - 1)
	var sum float64
	for _, v := range h[:len(h)-1] {
		sum += v
	}
	mean := sum / n

	var variance float64
	for _, v := range h[:len(h)-1] {
		diff := v - mean
		variance += diff * diff
	}
	stdDev := math.Sqrt(variance / n)

	if stdDev == 0 {
		return &AnomalyResult{IsAnomaly: false, Value: value, Mean: mean, StdDev: 0, Threshold: d.threshold}
	}

	zScore := (value - mean) / stdDev
	direction := "spike"
	if zScore < 0 {
		direction = "drop"
	}

	return &AnomalyResult{
		IsAnomaly: math.Abs(zScore) > d.threshold,
		ZScore:    zScore,
		Value:     value,
		Mean:      mean,
		StdDev:    stdDev,
		Threshold: d.threshold,
		Direction: direction,
	}
}

// ─── T159: Cost Per Feature Attribution ─────────────────────

type FeatureCost struct {
	FeatureID   string  `json:"feature_id"`
	FeatureName string  `json:"feature_name"`
	TotalCost   float64 `json:"total_cost"`
	Requests    int64   `json:"requests"`
	AvgCost     float64 `json:"avg_cost"`
	TotalTokens int64   `json:"total_tokens"`
}

type FeatureTracker struct {
	mu       sync.RWMutex
	features map[string]*FeatureCost
}

func NewFeatureTracker() *FeatureTracker {
	return &FeatureTracker{
		features: make(map[string]*FeatureCost),
	}
}

func (t *FeatureTracker) Record(featureID, featureName string, cost float64, tokens int64) {
	t.mu.Lock()
	defer t.mu.Unlock()

	fc, ok := t.features[featureID]
	if !ok {
		fc = &FeatureCost{FeatureID: featureID, FeatureName: featureName}
		t.features[featureID] = fc
	}

	fc.FeatureName = featureName
	fc.TotalCost += cost
	fc.Requests++
	fc.TotalTokens += tokens
	fc.AvgCost = fc.TotalCost / float64(fc.Requests)
}

func (t *FeatureTracker) GetAll() []FeatureCost {
	t.mu.RLock()
	defer t.mu.RUnlock()

	result := make([]FeatureCost, 0, len(t.features))
	for _, fc := range t.features {
		result = append(result, *fc)
	}

	sort.Slice(result, func(i, j int) bool {
		return result[i].TotalCost > result[j].TotalCost
	})
	return result
}

func (t *FeatureTracker) Get(featureID string) (*FeatureCost, error) {
	t.mu.RLock()
	defer t.mu.RUnlock()

	fc, ok := t.features[featureID]
	if !ok {
		return nil, fmt.Errorf("feature %s not found", featureID)
	}
	cp := *fc
	return &cp, nil
}

// ─── T160: AI ROI Scoring ───────────────────────────────────

type ROIInput struct {
	FeatureID        string  `json:"feature_id"`
	AISpend          float64 `json:"ai_spend"`
	RevenueImpact    float64 `json:"revenue_impact"`    // $/month attributed
	ProductivityGain float64 `json:"productivity_gain"`  // hours saved/month
	HourlyRate       float64 `json:"hourly_rate"`        // $/hour for productivity
}

type ROIResult struct {
	FeatureID         string  `json:"feature_id"`
	ROIScore          float64 `json:"roi_score"`          // ratio
	MonthlyReturn     float64 `json:"monthly_return"`     // $ value generated
	MonthlySpend      float64 `json:"monthly_spend"`
	NetValue          float64 `json:"net_value"`
	PaybackDays       int     `json:"payback_days"`
	Recommendation    string  `json:"recommendation"`
}

func CalculateROI(input ROIInput) *ROIResult {
	monthlyReturn := input.RevenueImpact + (input.ProductivityGain * input.HourlyRate)
	netValue := monthlyReturn - input.AISpend

	roiScore := 0.0
	if input.AISpend > 0 {
		roiScore = monthlyReturn / input.AISpend
	}

	paybackDays := 0
	if monthlyReturn > 0 {
		paybackDays = int(input.AISpend / (monthlyReturn / 30))
	}

	rec := "invest_more"
	if roiScore < 0.5 {
		rec = "reduce_or_eliminate"
	} else if roiScore < 1.0 {
		rec = "optimize"
	} else if roiScore < 3.0 {
		rec = "maintain"
	}

	return &ROIResult{
		FeatureID:      input.FeatureID,
		ROIScore:       roiScore,
		MonthlyReturn:  monthlyReturn,
		MonthlySpend:   input.AISpend,
		NetValue:       netValue,
		PaybackDays:    paybackDays,
		Recommendation: rec,
	}
}

// ─── T161: Token Efficiency Score ───────────────────────────

type EfficiencyScore struct {
	TeamID          string  `json:"team_id"`
	TeamName        string  `json:"team_name"`
	TotalTokens     int64   `json:"total_tokens"`
	UsefulTokens    int64   `json:"useful_tokens"` // output tokens only
	TotalCost       float64 `json:"total_cost"`
	Requests        int64   `json:"requests"`
	EfficiencyScore float64 `json:"efficiency_score"` // 0-100
	Rank            int     `json:"rank"`
}

func CalculateEfficiency(totalTokens, usefulTokens int64, cost float64, requests int64) float64 {
	if totalTokens == 0 || cost == 0 {
		return 0
	}

	// Score = (useful_tokens / total_tokens) * (1 / cost_per_1k) * normalization
	ratio := float64(usefulTokens) / float64(totalTokens)
	costPer1k := (cost / float64(totalTokens)) * 1000
	if costPer1k == 0 {
		return 100
	}

	// Normalize: higher ratio and lower cost = better
	// Score capped at 100
	score := ratio * (1.0 / costPer1k) * 10 // scaling factor
	if score > 100 {
		score = 100
	}
	return score
}

// ─── T163: Cross-Model Cost Arbitrage ───────────────────────

type ModelPrice struct {
	Provider    string  `json:"provider"`
	Model       string  `json:"model"`
	InputPer1K  float64 `json:"input_per_1k"`
	OutputPer1K float64 `json:"output_per_1k"`
	UpdatedAt   time.Time `json:"updated_at"`
}

type ArbitrageOpportunity struct {
	CurrentProvider string  `json:"current_provider"`
	CurrentModel    string  `json:"current_model"`
	CurrentCost     float64 `json:"current_cost"`
	BetterProvider  string  `json:"better_provider"`
	BetterModel     string  `json:"better_model"`
	BetterCost      float64 `json:"better_cost"`
	SavingsPercent  float64 `json:"savings_percent"`
}

type ArbitrageEngine struct {
	mu           sync.RWMutex
	prices       []ModelPrice
	minSavings   float64 // minimum savings % to trigger (default 10%)
	equivalences map[string][]string // model capability groups
}

func NewArbitrageEngine(minSavingsPercent float64) *ArbitrageEngine {
	if minSavingsPercent <= 0 {
		minSavingsPercent = 10.0
	}
	return &ArbitrageEngine{
		minSavings: minSavingsPercent,
		equivalences: map[string][]string{
			"premium": {"gpt-4", "gpt-4-turbo", "gpt-4o", "claude-3-opus", "claude-opus-4", "gemini-1.5-pro"},
			"standard": {"gpt-3.5-turbo", "claude-3-sonnet", "claude-sonnet-4", "gemini-1.5-flash", "mistral-large"},
			"fast": {"gpt-3.5-turbo", "claude-3-haiku", "claude-haiku-4.5", "mistral-small", "groq-mixtral"},
			"embed": {"text-embedding-3-small", "text-embedding-3-large", "voyage-3", "cohere-embed-v3"},
		},
	}
}

func (e *ArbitrageEngine) UpdatePrices(prices []ModelPrice) {
	e.mu.Lock()
	defer e.mu.Unlock()
	e.prices = prices
}

// FindOpportunities identifies cheaper alternatives for a given model.
func (e *ArbitrageEngine) FindOpportunities(currentProvider, currentModel string, avgInputTokens, avgOutputTokens int) []ArbitrageOpportunity {
	e.mu.RLock()
	defer e.mu.RUnlock()

	// Find current cost
	var currentPrice *ModelPrice
	for i, p := range e.prices {
		if p.Provider == currentProvider && p.Model == currentModel {
			currentPrice = &e.prices[i]
			break
		}
	}
	if currentPrice == nil {
		return nil
	}

	currentCost := (currentPrice.InputPer1K * float64(avgInputTokens) / 1000) +
		(currentPrice.OutputPer1K * float64(avgOutputTokens) / 1000)

	// Find equivalent models
	var group string
	for g, models := range e.equivalences {
		for _, m := range models {
			if m == currentModel {
				group = g
				break
			}
		}
	}

	var opportunities []ArbitrageOpportunity

	equivalents := e.equivalences[group]
	for _, p := range e.prices {
		if p.Provider == currentProvider && p.Model == currentModel {
			continue
		}

		isEquivalent := false
		for _, eq := range equivalents {
			if eq == p.Model {
				isEquivalent = true
				break
			}
		}
		if !isEquivalent && group != "" {
			continue
		}

		altCost := (p.InputPer1K * float64(avgInputTokens) / 1000) +
			(p.OutputPer1K * float64(avgOutputTokens) / 1000)

		if currentCost > 0 {
			savings := ((currentCost - altCost) / currentCost) * 100
			if savings >= e.minSavings {
				opportunities = append(opportunities, ArbitrageOpportunity{
					CurrentProvider: currentProvider,
					CurrentModel:    currentModel,
					CurrentCost:     currentCost,
					BetterProvider:  p.Provider,
					BetterModel:     p.Model,
					BetterCost:      altCost,
					SavingsPercent:  savings,
				})
			}
		}
	}

	sort.Slice(opportunities, func(i, j int) bool {
		return opportunities[i].SavingsPercent > opportunities[j].SavingsPercent
	})
	return opportunities
}

// ─── T164: AI Traffic Replay & Simulation ───────────────────

type RecordedRequest struct {
	ID        string            `json:"id"`
	Timestamp time.Time         `json:"timestamp"`
	Model     string            `json:"model"`
	Provider  string            `json:"provider"`
	Prompt    string            `json:"prompt"`
	Tokens    int64             `json:"tokens"`
	Cost      float64           `json:"cost"`
	LatencyMs float64           `json:"latency_ms"`
	Metadata  map[string]string `json:"metadata"`
}

type SimulationResult struct {
	OriginalModel    string  `json:"original_model"`
	OriginalCost     float64 `json:"original_total_cost"`
	OriginalLatency  float64 `json:"original_avg_latency_ms"`
	SimulatedModel   string  `json:"simulated_model"`
	SimulatedCost    float64 `json:"simulated_total_cost"`
	SimulatedLatency float64 `json:"simulated_avg_latency_ms"`
	CostDiff         float64 `json:"cost_diff"`
	CostDiffPercent  float64 `json:"cost_diff_percent"`
	LatencyDiff      float64 `json:"latency_diff"`
	RequestCount     int     `json:"request_count"`
}

type TrafficRecorder struct {
	mu       sync.RWMutex
	buffer   []RecordedRequest
	maxSize  int
}

func NewTrafficRecorder(maxSize int) *TrafficRecorder {
	if maxSize <= 0 {
		maxSize = 10000
	}
	return &TrafficRecorder{
		buffer:  make([]RecordedRequest, 0, maxSize),
		maxSize: maxSize,
	}
}

func (r *TrafficRecorder) Record(req RecordedRequest) {
	r.mu.Lock()
	defer r.mu.Unlock()

	r.buffer = append(r.buffer, req)
	if len(r.buffer) > r.maxSize {
		r.buffer = r.buffer[len(r.buffer)-r.maxSize:]
	}
}

func (r *TrafficRecorder) GetRecordings(limit int) []RecordedRequest {
	r.mu.RLock()
	defer r.mu.RUnlock()

	if limit <= 0 || limit > len(r.buffer) {
		limit = len(r.buffer)
	}
	result := make([]RecordedRequest, limit)
	copy(result, r.buffer[len(r.buffer)-limit:])
	return result
}

// Simulate estimates what-if cost and latency for a different model.
func (r *TrafficRecorder) Simulate(targetModel string, prices map[string]ModelPrice, latencyEstimateMs float64) *SimulationResult {
	r.mu.RLock()
	records := make([]RecordedRequest, len(r.buffer))
	copy(records, r.buffer)
	r.mu.RUnlock()

	if len(records) == 0 {
		return &SimulationResult{SimulatedModel: targetModel}
	}

	var origTotalCost, origTotalLatency float64
	var simTotalCost float64

	targetPrice, hasPrice := prices[targetModel]

	for _, rec := range records {
		origTotalCost += rec.Cost
		origTotalLatency += rec.LatencyMs

		if hasPrice {
			// Estimate: use same token count with target model pricing
			simCost := (targetPrice.InputPer1K * float64(rec.Tokens) * 0.7 / 1000) + // ~70% input
				(targetPrice.OutputPer1K * float64(rec.Tokens) * 0.3 / 1000) // ~30% output
			simTotalCost += simCost
		}
	}

	n := float64(len(records))
	return &SimulationResult{
		OriginalModel:    records[0].Model,
		OriginalCost:     origTotalCost,
		OriginalLatency:  origTotalLatency / n,
		SimulatedModel:   targetModel,
		SimulatedCost:    simTotalCost,
		SimulatedLatency: latencyEstimateMs,
		CostDiff:         simTotalCost - origTotalCost,
		CostDiffPercent:  ((simTotalCost - origTotalCost) / origTotalCost) * 100,
		LatencyDiff:      latencyEstimateMs - origTotalLatency/n,
		RequestCount:     len(records),
	}
}
