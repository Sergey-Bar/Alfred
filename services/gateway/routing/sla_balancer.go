/*
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L3
Logic:       SLA-aware weighted load balancer. Routes requests
             based on provider latency, error rate, availability,
             and configured SLA targets. Uses exponential weighted
             moving average for latency tracking and automatic
             health degradation scoring.
Root Cause:  Sprint task T095 — SLA-aware load balancing.
Context:     Enables routing requests to the fastest healthy
             provider while respecting SLA guarantees.
Suitability: L3 — complex real-time scoring algorithm.
──────────────────────────────────────────────────────────────
*/

package routing

import (
	"math"
	"sort"
	"sync"
	"time"

	"github.com/rs/zerolog"
)

// SLATarget defines the SLA thresholds for a provider.
type SLATarget struct {
	// MaxP95LatencyMs is the P95 latency ceiling in ms. Exceeding this degrades the score.
	MaxP95LatencyMs float64 `json:"max_p95_latency_ms"`
	// MaxErrorRate is the acceptable error rate (0-1). E.g., 0.01 = 1%.
	MaxErrorRate float64 `json:"max_error_rate"`
	// MinAvailability is the minimum uptime ratio (0-1). E.g., 0.999 = 99.9%.
	MinAvailability float64 `json:"min_availability"`
	// Weight is a static preference weight (1.0 = neutral, >1 = preferred).
	Weight float64 `json:"weight"`
}

// DefaultSLATarget returns a standard SLA target.
func DefaultSLATarget() SLATarget {
	return SLATarget{
		MaxP95LatencyMs: 5000,
		MaxErrorRate:    0.05,
		MinAvailability: 0.99,
		Weight:          1.0,
	}
}

// ProviderHealth tracks real-time health metrics for a provider.
type ProviderHealth struct {
	mu sync.Mutex

	// Exponential weighted moving average latency (ms)
	ewmaLatencyMs float64
	ewmaAlpha     float64 // smoothing factor (default: 0.3)

	// Sliding window error tracking
	totalRequests int64
	totalErrors   int64
	windowStart   time.Time
	windowSize    time.Duration

	// Availability tracking
	lastHealthCheck time.Time
	healthy         bool
	failedChecks    int
	totalChecks     int

	// Penalty: temporary score reduction (decays over time)
	penalty     float64
	penaltyTime time.Time
}

// NewProviderHealth creates fresh health tracking for a provider.
func NewProviderHealth() *ProviderHealth {
	return &ProviderHealth{
		ewmaAlpha:   0.3,
		healthy:     true,
		windowStart: time.Now(),
		windowSize:  5 * time.Minute,
	}
}

// RecordLatency records a request latency observation.
func (ph *ProviderHealth) RecordLatency(ms float64) {
	ph.mu.Lock()
	defer ph.mu.Unlock()

	if ph.ewmaLatencyMs == 0 {
		ph.ewmaLatencyMs = ms
	} else {
		ph.ewmaLatencyMs = ph.ewmaAlpha*ms + (1-ph.ewmaAlpha)*ph.ewmaLatencyMs
	}
	ph.totalRequests++
}

// RecordError records a failed request.
func (ph *ProviderHealth) RecordError() {
	ph.mu.Lock()
	defer ph.mu.Unlock()
	ph.totalErrors++
	ph.totalRequests++
}

// RecordHealthCheck records a health check result.
func (ph *ProviderHealth) RecordHealthCheck(healthy bool) {
	ph.mu.Lock()
	defer ph.mu.Unlock()
	ph.lastHealthCheck = time.Now()
	ph.totalChecks++
	ph.healthy = healthy
	if !healthy {
		ph.failedChecks++
	}
}

// AddPenalty applies a temporary score penalty (0-1).
func (ph *ProviderHealth) AddPenalty(amount float64) {
	ph.mu.Lock()
	defer ph.mu.Unlock()
	ph.penalty = math.Min(1.0, ph.penalty+amount)
	ph.penaltyTime = time.Now()
}

// snapshot returns a copy of current metrics.
func (ph *ProviderHealth) snapshot() providerSnapshot {
	ph.mu.Lock()
	defer ph.mu.Unlock()

	// Reset window if expired
	if time.Since(ph.windowStart) > ph.windowSize {
		ph.totalRequests = 0
		ph.totalErrors = 0
		ph.windowStart = time.Now()
	}

	// Decay penalty over 5 minutes
	currentPenalty := ph.penalty
	if currentPenalty > 0 && !ph.penaltyTime.IsZero() {
		elapsed := time.Since(ph.penaltyTime).Minutes()
		currentPenalty = ph.penalty * math.Exp(-elapsed/5.0)
		if currentPenalty < 0.01 {
			currentPenalty = 0
		}
	}

	errorRate := 0.0
	if ph.totalRequests > 0 {
		errorRate = float64(ph.totalErrors) / float64(ph.totalRequests)
	}

	availability := 1.0
	if ph.totalChecks > 0 {
		availability = 1.0 - float64(ph.failedChecks)/float64(ph.totalChecks)
	}

	return providerSnapshot{
		ewmaLatencyMs: ph.ewmaLatencyMs,
		errorRate:     errorRate,
		availability:  availability,
		healthy:       ph.healthy,
		penalty:       currentPenalty,
		totalRequests: ph.totalRequests,
	}
}

type providerSnapshot struct {
	ewmaLatencyMs float64
	errorRate     float64
	availability  float64
	healthy       bool
	penalty       float64
	totalRequests int64
}

// ─── SLA-Aware Load Balancer ────────────────────────────────

// SLABalancer routes requests to the best available provider
// based on latency, error rate, availability, and SLA targets.
type SLABalancer struct {
	mu        sync.RWMutex
	providers map[string]*ProviderHealth
	targets   map[string]SLATarget
	logger    zerolog.Logger
}

// NewSLABalancer creates a new SLA-aware load balancer.
func NewSLABalancer(logger zerolog.Logger) *SLABalancer {
	return &SLABalancer{
		providers: make(map[string]*ProviderHealth),
		targets:   make(map[string]SLATarget),
		logger:    logger.With().Str("component", "sla-balancer").Logger(),
	}
}

// RegisterProvider registers a provider with an SLA target.
func (lb *SLABalancer) RegisterProvider(name string, target SLATarget) {
	lb.mu.Lock()
	defer lb.mu.Unlock()
	lb.providers[name] = NewProviderHealth()
	lb.targets[name] = target
}

// GetHealth returns the health tracker for a provider.
func (lb *SLABalancer) GetHealth(name string) *ProviderHealth {
	lb.mu.RLock()
	defer lb.mu.RUnlock()
	return lb.providers[name]
}

// ─── Scoring ────────────────────────────────────────────────

// providerScore holds the computed score and metadata for ranking.
type providerScore struct {
	Name  string
	Score float64
	snap  providerSnapshot
}

// SelectProvider picks the best provider from the given candidates.
// If candidates is empty, considers all registered providers.
// Returns the provider name and the computed score.
func (lb *SLABalancer) SelectProvider(candidates []string) (string, float64) {
	lb.mu.RLock()
	defer lb.mu.RUnlock()

	if len(candidates) == 0 {
		candidates = make([]string, 0, len(lb.providers))
		for name := range lb.providers {
			candidates = append(candidates, name)
		}
	}

	scores := make([]providerScore, 0, len(candidates))

	for _, name := range candidates {
		health, ok := lb.providers[name]
		if !ok {
			continue
		}
		target, ok := lb.targets[name]
		if !ok {
			target = DefaultSLATarget()
		}

		snap := health.snapshot()
		score := lb.computeScore(snap, target)
		scores = append(scores, providerScore{Name: name, Score: score, snap: snap})
	}

	if len(scores) == 0 {
		return "", 0
	}

	// Sort descending by score (highest = best)
	sort.Slice(scores, func(i, j int) bool {
		return scores[i].Score > scores[j].Score
	})

	best := scores[0]

	lb.logger.Debug().
		Str("selected", best.Name).
		Float64("score", best.Score).
		Float64("latency_ms", best.snap.ewmaLatencyMs).
		Float64("error_rate", best.snap.errorRate).
		Int("candidates", len(scores)).
		Msg("SLA balancer selected provider")

	return best.Name, best.Score
}

// computeScore calculates a 0-1 composite score for a provider.
//
// Formula:
//
//	score = weight × (latencyScore × 0.35 + errorScore × 0.30 + availScore × 0.25 + freshnessScore × 0.10) × (1 - penalty)
//
// Each sub-score is 0-1. Higher is better.
func (lb *SLABalancer) computeScore(snap providerSnapshot, target SLATarget) float64 {
	// If unhealthy, score is 0 (circuit-break style)
	if !snap.healthy {
		return 0
	}

	// 1. Latency score: 1.0 when at/below target, degrades as latency rises
	latencyScore := 1.0
	if snap.ewmaLatencyMs > 0 && target.MaxP95LatencyMs > 0 {
		ratio := snap.ewmaLatencyMs / target.MaxP95LatencyMs
		if ratio > 1.0 {
			// Exponential penalty beyond SLA
			latencyScore = math.Exp(-(ratio - 1.0) * 2.0)
		} else {
			latencyScore = 1.0
		}
	}

	// 2. Error rate score: 1.0 when at/below target
	errorScore := 1.0
	if snap.totalRequests > 10 { // Need minimum sample
		if target.MaxErrorRate > 0 {
			ratio := snap.errorRate / target.MaxErrorRate
			if ratio > 1.0 {
				errorScore = math.Exp(-(ratio - 1.0) * 3.0)
			}
		} else if snap.errorRate > 0 {
			errorScore = 1.0 - snap.errorRate
		}
	}

	// 3. Availability score: binary-ish — sharp dropoff below SLA
	availScore := 1.0
	if snap.availability < target.MinAvailability {
		availScore = snap.availability / target.MinAvailability
	}

	// 4. Freshness score: prefer providers with more recent data
	freshnessScore := 1.0
	if snap.totalRequests == 0 {
		freshnessScore = 0.5 // Unknown quality — give moderate score
	}

	// Weighted composite
	composite := latencyScore*0.35 + errorScore*0.30 + availScore*0.25 + freshnessScore*0.10

	// Apply static preference weight
	weight := target.Weight
	if weight <= 0 {
		weight = 1.0
	}

	// Apply penalty
	penaltyMult := 1.0 - snap.penalty

	return composite * weight * penaltyMult
}

// GetScores returns the current scores for all registered providers.
// Useful for dashboard display and debugging.
func (lb *SLABalancer) GetScores() []providerScore {
	lb.mu.RLock()
	defer lb.mu.RUnlock()

	scores := make([]providerScore, 0, len(lb.providers))
	for name, health := range lb.providers {
		target, ok := lb.targets[name]
		if !ok {
			target = DefaultSLATarget()
		}
		snap := health.snapshot()
		score := lb.computeScore(snap, target)
		scores = append(scores, providerScore{Name: name, Score: score, snap: snap})
	}

	sort.Slice(scores, func(i, j int) bool {
		return scores[i].Score > scores[j].Score
	})

	return scores
}

// RecordSuccess records a successful request to the named provider.
func (lb *SLABalancer) RecordSuccess(provider string, latencyMs float64) {
	lb.mu.RLock()
	health := lb.providers[provider]
	lb.mu.RUnlock()
	if health != nil {
		health.RecordLatency(latencyMs)
	}
}

// RecordFailure records a failed request.
func (lb *SLABalancer) RecordFailure(provider string) {
	lb.mu.RLock()
	health := lb.providers[provider]
	lb.mu.RUnlock()
	if health != nil {
		health.RecordError()
	}
}
