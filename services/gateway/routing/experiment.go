/*
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L3
Logic:       Routing experiment engine — A/B traffic splitting with
             consistent hashing, metric aggregation, statistical
             significance (z-test), and auto-promotion.
Root Cause:  Sprint tasks T099-T103 — Routing experiment engine.
Context:     Integrates with routing engine for traffic splitting.
Suitability: L3 — complex algorithm design with stats.
──────────────────────────────────────────────────────────────
*/

package routing

import (
	"crypto/sha256"
	"encoding/binary"
	"fmt"
	"math"
	"sync"
	"time"
)

// ─── T099: Experiment Data Model ────────────────────────────

type ExperimentStatus string

const (
	ExperimentDraft     ExperimentStatus = "draft"
	ExperimentRunning   ExperimentStatus = "running"
	ExperimentPaused    ExperimentStatus = "paused"
	ExperimentConcluded ExperimentStatus = "concluded"
)

type ExperimentVariant struct {
	Name          string  `json:"name"`
	Model         string  `json:"model"`
	Provider      string  `json:"provider"`
	TrafficWeight float64 `json:"traffic_weight"` // 0.0–1.0, must sum to 1.0
}

type Experiment struct {
	ID          string              `json:"id"`
	Name        string              `json:"name"`
	Description string              `json:"description"`
	Status      ExperimentStatus    `json:"status"`
	Variants    []ExperimentVariant `json:"variants"`
	CreatedAt   time.Time           `json:"created_at"`
	StartedAt   *time.Time          `json:"started_at,omitempty"`
	ConcludedAt *time.Time          `json:"concluded_at,omitempty"`
	WinnerIdx   int                 `json:"winner_idx"`

	// Auto-switch config
	AutoSwitch           bool    `json:"auto_switch"`
	SignificanceThreshold float64 `json:"significance_threshold"` // default 0.95
	MinSampleSize        int     `json:"min_sample_size"`        // default 100
}

// ─── T101: Metric Aggregation ───────────────────────────────

type VariantMetrics struct {
	Requests     int64         `json:"requests"`
	Errors       int64         `json:"errors"`
	TotalCost    float64       `json:"total_cost"`
	TotalLatency time.Duration `json:"-"`
	TotalTokens  int64         `json:"total_tokens"`

	// Derived
	AvgCost     float64 `json:"avg_cost"`
	AvgLatency  float64 `json:"avg_latency_ms"`
	ErrorRate   float64 `json:"error_rate"`
	AvgTokens   float64 `json:"avg_tokens"`

	// For z-test: track sum of squared latencies for variance
	SumLatencySq float64 `json:"-"`
}

func (m *VariantMetrics) Recalculate() {
	if m.Requests > 0 {
		m.AvgCost = m.TotalCost / float64(m.Requests)
		m.AvgLatency = float64(m.TotalLatency.Milliseconds()) / float64(m.Requests)
		m.ErrorRate = float64(m.Errors) / float64(m.Requests)
		m.AvgTokens = float64(m.TotalTokens) / float64(m.Requests)
	}
}

func (m *VariantMetrics) LatencyVariance() float64 {
	if m.Requests < 2 {
		return 0
	}
	mean := m.AvgLatency
	return m.SumLatencySq/float64(m.Requests) - mean*mean
}

// ─── T100: A/B Traffic Splitting (Consistent Hashing) ──────

type ExperimentEngine struct {
	mu          sync.RWMutex
	experiments map[string]*Experiment
	metrics     map[string][]VariantMetrics // experimentID -> per-variant metrics
}

func NewExperimentEngine() *ExperimentEngine {
	return &ExperimentEngine{
		experiments: make(map[string]*Experiment),
		metrics:     make(map[string][]VariantMetrics),
	}
}

// CreateExperiment registers a new experiment.
func (e *ExperimentEngine) CreateExperiment(exp *Experiment) error {
	e.mu.Lock()
	defer e.mu.Unlock()

	if _, exists := e.experiments[exp.ID]; exists {
		return fmt.Errorf("experiment %s already exists", exp.ID)
	}

	// Validate traffic weights sum to 1.0
	var totalWeight float64
	for _, v := range exp.Variants {
		totalWeight += v.TrafficWeight
	}
	if math.Abs(totalWeight-1.0) > 0.01 {
		return fmt.Errorf("variant traffic weights must sum to 1.0, got %.3f", totalWeight)
	}

	if exp.SignificanceThreshold == 0 {
		exp.SignificanceThreshold = 0.95
	}
	if exp.MinSampleSize == 0 {
		exp.MinSampleSize = 100
	}

	exp.Status = ExperimentDraft
	exp.CreatedAt = time.Now()
	exp.WinnerIdx = -1
	e.experiments[exp.ID] = exp
	e.metrics[exp.ID] = make([]VariantMetrics, len(exp.Variants))
	return nil
}

// StartExperiment transitions to running status.
func (e *ExperimentEngine) StartExperiment(id string) error {
	e.mu.Lock()
	defer e.mu.Unlock()

	exp, ok := e.experiments[id]
	if !ok {
		return fmt.Errorf("experiment %s not found", id)
	}
	if exp.Status != ExperimentDraft && exp.Status != ExperimentPaused {
		return fmt.Errorf("experiment %s is %s, cannot start", id, exp.Status)
	}

	now := time.Now()
	exp.StartedAt = &now
	exp.Status = ExperimentRunning
	return nil
}

// AssignVariant determines which variant to use for a given request key
// using consistent hashing (SHA-256 of the key mapped to traffic weights).
func (e *ExperimentEngine) AssignVariant(experimentID, requestKey string) (*ExperimentVariant, int, error) {
	e.mu.RLock()
	defer e.mu.RUnlock()

	exp, ok := e.experiments[experimentID]
	if !ok {
		return nil, -1, fmt.Errorf("experiment %s not found", experimentID)
	}
	if exp.Status != ExperimentRunning {
		return nil, -1, fmt.Errorf("experiment %s is not running", experimentID)
	}

	// Consistent hash: SHA-256 of (experimentID + requestKey) → [0.0, 1.0)
	hash := sha256.Sum256([]byte(experimentID + ":" + requestKey))
	hashVal := float64(binary.BigEndian.Uint64(hash[:8])) / float64(math.MaxUint64)

	// Map to variant based on cumulative weights
	cumulative := 0.0
	for i, v := range exp.Variants {
		cumulative += v.TrafficWeight
		if hashVal < cumulative {
			return &v, i, nil
		}
	}

	// Fallback to last variant (floating point edge case)
	last := len(exp.Variants) - 1
	return &exp.Variants[last], last, nil
}

// RecordResult records the outcome of a request assigned to a variant.
func (e *ExperimentEngine) RecordResult(experimentID string, variantIdx int, cost float64, latency time.Duration, tokens int64, isError bool) {
	e.mu.Lock()
	defer e.mu.Unlock()

	metrics, ok := e.metrics[experimentID]
	if !ok || variantIdx < 0 || variantIdx >= len(metrics) {
		return
	}

	m := &metrics[variantIdx]
	m.Requests++
	m.TotalCost += cost
	m.TotalLatency += latency
	m.TotalTokens += tokens
	latMs := float64(latency.Milliseconds())
	m.SumLatencySq += latMs * latMs
	if isError {
		m.Errors++
	}
	m.Recalculate()

	// T103: Check auto-switch after recording
	exp := e.experiments[experimentID]
	if exp != nil && exp.AutoSwitch && exp.Status == ExperimentRunning {
		e.checkAutoSwitch(exp, metrics)
	}
}

// ─── T102: Statistical Significance Detection (Z-Test) ─────

// ZTestResult contains the result of a two-proportion z-test.
type ZTestResult struct {
	ZScore       float64 `json:"z_score"`
	PValue       float64 `json:"p_value"`
	Significant  bool    `json:"significant"`
	BetterIdx    int     `json:"better_idx"`
	Metric       string  `json:"metric"`
}

// CompareErrorRates performs a two-proportion z-test on error rates.
func (e *ExperimentEngine) CompareErrorRates(experimentID string) (*ZTestResult, error) {
	e.mu.RLock()
	defer e.mu.RUnlock()

	metrics, ok := e.metrics[experimentID]
	if !ok {
		return nil, fmt.Errorf("experiment %s not found", experimentID)
	}
	if len(metrics) < 2 {
		return nil, fmt.Errorf("need at least 2 variants")
	}

	exp := e.experiments[experimentID]

	// Compare first two variants (control vs treatment)
	m0, m1 := metrics[0], metrics[1]
	if m0.Requests < int64(exp.MinSampleSize) || m1.Requests < int64(exp.MinSampleSize) {
		return &ZTestResult{Significant: false, Metric: "error_rate"}, nil
	}

	p1 := m0.ErrorRate
	p2 := m1.ErrorRate
	n1 := float64(m0.Requests)
	n2 := float64(m1.Requests)

	// Pooled proportion
	pPool := (float64(m0.Errors) + float64(m1.Errors)) / (n1 + n2)
	if pPool == 0 || pPool == 1 {
		return &ZTestResult{Significant: false, Metric: "error_rate"}, nil
	}

	se := math.Sqrt(pPool * (1 - pPool) * (1/n1 + 1/n2))
	if se == 0 {
		return &ZTestResult{Significant: false, Metric: "error_rate"}, nil
	}

	z := (p1 - p2) / se
	pValue := 2 * normalCDF(-math.Abs(z)) // two-tailed

	betterIdx := 0
	if p2 < p1 {
		betterIdx = 1
	}

	return &ZTestResult{
		ZScore:      z,
		PValue:      pValue,
		Significant: pValue < (1 - exp.SignificanceThreshold),
		BetterIdx:   betterIdx,
		Metric:      "error_rate",
	}, nil
}

// CompareCosts performs a two-sample z-test on average costs.
func (e *ExperimentEngine) CompareCosts(experimentID string) (*ZTestResult, error) {
	e.mu.RLock()
	defer e.mu.RUnlock()

	metrics, ok := e.metrics[experimentID]
	if !ok {
		return nil, fmt.Errorf("experiment %s not found", experimentID)
	}
	if len(metrics) < 2 {
		return nil, fmt.Errorf("need at least 2 variants")
	}

	exp := e.experiments[experimentID]
	m0, m1 := metrics[0], metrics[1]
	if m0.Requests < int64(exp.MinSampleSize) || m1.Requests < int64(exp.MinSampleSize) {
		return &ZTestResult{Significant: false, Metric: "cost"}, nil
	}

	// Use latency variance as proxy for cost variance
	var0 := m0.LatencyVariance()
	var1 := m1.LatencyVariance()
	n1, n2 := float64(m0.Requests), float64(m1.Requests)

	se := math.Sqrt(var0/n1 + var1/n2)
	if se == 0 {
		return &ZTestResult{Significant: false, Metric: "cost"}, nil
	}

	z := (m0.AvgCost - m1.AvgCost) / se
	pValue := 2 * normalCDF(-math.Abs(z))

	betterIdx := 0
	if m1.AvgCost < m0.AvgCost {
		betterIdx = 1
	}

	return &ZTestResult{
		ZScore:      z,
		PValue:      pValue,
		Significant: pValue < (1 - exp.SignificanceThreshold),
		BetterIdx:   betterIdx,
		Metric:      "cost",
	}, nil
}

// ─── T103: Auto-Switch on Threshold ─────────────────────────

// checkAutoSwitch promotes the winning variant if statistically significant.
// Must be called with e.mu held.
func (e *ExperimentEngine) checkAutoSwitch(exp *Experiment, metrics []VariantMetrics) {
	if len(metrics) < 2 {
		return
	}

	// Check minimum sample size for all variants
	for _, m := range metrics {
		if m.Requests < int64(exp.MinSampleSize) {
			return
		}
	}

	// Find best variant by composite score (lower error rate + lower cost)
	bestIdx := 0
	bestScore := math.MaxFloat64
	for i, m := range metrics {
		// Composite: cost weight 0.6, error rate weight 0.4
		score := m.AvgCost*0.6 + m.ErrorRate*100*0.4
		if score < bestScore {
			bestScore = score
			bestIdx = i
		}
	}

	// Verify with z-test on error rates between best and others
	p1 := metrics[bestIdx].ErrorRate
	n1 := float64(metrics[bestIdx].Requests)

	for i, m := range metrics {
		if i == bestIdx {
			continue
		}
		p2 := m.ErrorRate
		n2 := float64(m.Requests)

		pPool := (float64(metrics[bestIdx].Errors) + float64(m.Errors)) / (n1 + n2)
		if pPool == 0 || pPool == 1 {
			continue
		}
		se := math.Sqrt(pPool * (1 - pPool) * (1/n1 + 1/n2))
		if se == 0 {
			continue
		}
		z := (p2 - p1) / se
		pValue := normalCDF(-z) // one-tailed: is bestIdx better?
		if pValue > (1 - exp.SignificanceThreshold) {
			return // not significant enough
		}
	}

	// Promote winner
	now := time.Now()
	exp.ConcludedAt = &now
	exp.Status = ExperimentConcluded
	exp.WinnerIdx = bestIdx
}

// GetExperiment returns an experiment by ID.
func (e *ExperimentEngine) GetExperiment(id string) (*Experiment, []VariantMetrics, error) {
	e.mu.RLock()
	defer e.mu.RUnlock()

	exp, ok := e.experiments[id]
	if !ok {
		return nil, nil, fmt.Errorf("experiment %s not found", id)
	}

	metricsCopy := make([]VariantMetrics, len(e.metrics[id]))
	copy(metricsCopy, e.metrics[id])
	return exp, metricsCopy, nil
}

// ListExperiments returns all experiments.
func (e *ExperimentEngine) ListExperiments() []*Experiment {
	e.mu.RLock()
	defer e.mu.RUnlock()

	result := make([]*Experiment, 0, len(e.experiments))
	for _, exp := range e.experiments {
		result = append(result, exp)
	}
	return result
}

// ConcludeExperiment manually concludes an experiment.
func (e *ExperimentEngine) ConcludeExperiment(id string, winnerIdx int) error {
	e.mu.Lock()
	defer e.mu.Unlock()

	exp, ok := e.experiments[id]
	if !ok {
		return fmt.Errorf("experiment %s not found", id)
	}
	if winnerIdx < 0 || winnerIdx >= len(exp.Variants) {
		return fmt.Errorf("invalid winner index %d", winnerIdx)
	}

	now := time.Now()
	exp.ConcludedAt = &now
	exp.Status = ExperimentConcluded
	exp.WinnerIdx = winnerIdx
	return nil
}

// DeleteExperiment removes an experiment.
func (e *ExperimentEngine) DeleteExperiment(id string) error {
	e.mu.Lock()
	defer e.mu.Unlock()

	if _, ok := e.experiments[id]; !ok {
		return fmt.Errorf("experiment %s not found", id)
	}
	delete(e.experiments, id)
	delete(e.metrics, id)
	return nil
}

// ─── Helper: Normal CDF approximation ──────────────────────

// normalCDF approximates the cumulative distribution function
// of the standard normal distribution using the Abramowitz & Stegun formula.
func normalCDF(x float64) float64 {
	if x < -8 {
		return 0
	}
	if x > 8 {
		return 1
	}

	t := 1.0 / (1.0 + 0.2316419*math.Abs(x))
	d := 0.3989422804014327 // 1/sqrt(2*pi)
	prob := d * math.Exp(-x*x/2.0) *
		(t * (0.3193815 + t*(-0.3565638+t*(1.781478+t*(-1.821256+t*1.330274)))))

	if x > 0 {
		return 1 - prob
	}
	return prob
}
