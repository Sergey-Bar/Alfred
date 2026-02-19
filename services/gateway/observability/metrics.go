/*
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L2
Logic:       Prometheus metrics endpoint for the Alfred gateway.
             Exposes request counters, latency histograms,
             token usage, cache hit rates, provider health,
             and wallet operation metrics via /metrics.
Root Cause:  Sprint task T144 — Prometheus /metrics endpoint.
Context:     Enables Grafana dashboards and alerting for SRE.
Suitability: L2 — standard Prometheus instrumentation pattern.
──────────────────────────────────────────────────────────────
*/

package observability

import (
	"fmt"
	"net/http"
	"sort"
	"strings"
	"sync"
	"sync/atomic"
	"time"

	"github.com/rs/zerolog"
)

// ─── Metric Types ───────────────────────────────────────────

// Counter is a monotonically increasing value.
type Counter struct {
	value int64
}

func (c *Counter) Inc()            { atomic.AddInt64(&c.value, 1) }
func (c *Counter) Add(n int64)     { atomic.AddInt64(&c.value, n) }
func (c *Counter) Value() int64    { return atomic.LoadInt64(&c.value) }

// Gauge is a value that can go up and down.
type Gauge struct {
	value int64 // stored as micros for float-like precision
}

func (g *Gauge) Set(v float64)   { atomic.StoreInt64(&g.value, int64(v*1e6)) }
func (g *Gauge) Inc()            { atomic.AddInt64(&g.value, 1e6) }
func (g *Gauge) Dec()            { atomic.AddInt64(&g.value, -1e6) }
func (g *Gauge) Value() float64  { return float64(atomic.LoadInt64(&g.value)) / 1e6 }

// Histogram tracks value distributions with configurable buckets.
type Histogram struct {
	mu      sync.Mutex
	buckets []float64
	counts  []int64  // per-bucket counts (+ Inf)
	sum     float64
	count   int64
}

func NewHistogram(buckets []float64) *Histogram {
	sorted := make([]float64, len(buckets))
	copy(sorted, buckets)
	sort.Float64s(sorted)
	return &Histogram{
		buckets: sorted,
		counts:  make([]int64, len(sorted)+1), // +1 for +Inf
	}
}

func (h *Histogram) Observe(v float64) {
	h.mu.Lock()
	defer h.mu.Unlock()
	h.sum += v
	h.count++
	// Store differential counts — only increment the first matching bucket.
	// The Handler accumulates these into cumulative Prometheus buckets.
	placed := false
	for i, b := range h.buckets {
		if v <= b {
			h.counts[i]++
			placed = true
			break
		}
	}
	if !placed {
		h.counts[len(h.buckets)]++ // +Inf bucket
	}
}

// ─── Label Key ──────────────────────────────────────────────

// labelKey creates a sorted label string for metric identification.
func labelKey(labels map[string]string) string {
	keys := make([]string, 0, len(labels))
	for k := range labels {
		keys = append(keys, k)
	}
	sort.Strings(keys)
	parts := make([]string, len(keys))
	for i, k := range keys {
		parts[i] = fmt.Sprintf("%s=%q", k, labels[k])
	}
	return strings.Join(parts, ",")
}

// ─── Metrics Registry ───────────────────────────────────────

// Metrics is the central Prometheus-compatible metrics registry.
type Metrics struct {
	mu         sync.RWMutex
	logger     zerolog.Logger
	counters   map[string]map[string]*Counter   // name → labelKey → counter
	gauges     map[string]map[string]*Gauge
	histograms map[string]map[string]*Histogram

	// Pre-defined metric names for documentation
	// (actual registration is implicit on first use)

	// Default histogram buckets for latency (ms)
	latencyBuckets []float64
	// Default histogram buckets for token counts
	tokenBuckets   []float64
}

// NewMetrics creates a new metrics registry.
func NewMetrics(logger zerolog.Logger) *Metrics {
	return &Metrics{
		logger:     logger.With().Str("component", "metrics").Logger(),
		counters:   make(map[string]map[string]*Counter),
		gauges:     make(map[string]map[string]*Gauge),
		histograms: make(map[string]map[string]*Histogram),
		latencyBuckets: []float64{5, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000, 10000},
		tokenBuckets:   []float64{10, 50, 100, 500, 1000, 5000, 10000, 50000},
	}
}

// ─── Counter Operations ─────────────────────────────────────

func (m *Metrics) CounterInc(name string, labels map[string]string) {
	m.getCounter(name, labels).Inc()
}

func (m *Metrics) CounterAdd(name string, labels map[string]string, n int64) {
	m.getCounter(name, labels).Add(n)
}

func (m *Metrics) getCounter(name string, labels map[string]string) *Counter {
	key := labelKey(labels)
	m.mu.RLock()
	if byName, ok := m.counters[name]; ok {
		if c, ok := byName[key]; ok {
			m.mu.RUnlock()
			return c
		}
	}
	m.mu.RUnlock()

	m.mu.Lock()
	defer m.mu.Unlock()
	if _, ok := m.counters[name]; !ok {
		m.counters[name] = make(map[string]*Counter)
	}
	if _, ok := m.counters[name][key]; !ok {
		m.counters[name][key] = &Counter{}
	}
	return m.counters[name][key]
}

// ─── Gauge Operations ───────────────────────────────────────

func (m *Metrics) GaugeSet(name string, labels map[string]string, v float64) {
	m.getGauge(name, labels).Set(v)
}

func (m *Metrics) GaugeInc(name string, labels map[string]string) {
	m.getGauge(name, labels).Inc()
}

func (m *Metrics) GaugeDec(name string, labels map[string]string) {
	m.getGauge(name, labels).Dec()
}

func (m *Metrics) getGauge(name string, labels map[string]string) *Gauge {
	key := labelKey(labels)
	m.mu.RLock()
	if byName, ok := m.gauges[name]; ok {
		if g, ok := byName[key]; ok {
			m.mu.RUnlock()
			return g
		}
	}
	m.mu.RUnlock()

	m.mu.Lock()
	defer m.mu.Unlock()
	if _, ok := m.gauges[name]; !ok {
		m.gauges[name] = make(map[string]*Gauge)
	}
	if _, ok := m.gauges[name][key]; !ok {
		m.gauges[name][key] = &Gauge{}
	}
	return m.gauges[name][key]
}

// ─── Histogram Operations ───────────────────────────────────

func (m *Metrics) HistogramObserve(name string, labels map[string]string, v float64) {
	m.getHistogram(name, labels).Observe(v)
}

func (m *Metrics) getHistogram(name string, labels map[string]string) *Histogram {
	key := labelKey(labels)
	m.mu.RLock()
	if byName, ok := m.histograms[name]; ok {
		if h, ok := byName[key]; ok {
			m.mu.RUnlock()
			return h
		}
	}
	m.mu.RUnlock()

	m.mu.Lock()
	defer m.mu.Unlock()
	if _, ok := m.histograms[name]; !ok {
		m.histograms[name] = make(map[string]*Histogram)
	}
	if _, ok := m.histograms[name][key]; !ok {
		m.histograms[name][key] = NewHistogram(m.latencyBuckets)
	}
	return m.histograms[name][key]
}

// ─── Pre-defined Metric Helpers ─────────────────────────────

// TrackRequest records a completed request with all relevant labels.
func (m *Metrics) TrackRequest(provider, model, endpoint string, statusCode int, latencyMs float64, tokens int64, cached bool) {
	labels := map[string]string{
		"provider": provider,
		"model":    model,
		"endpoint": endpoint,
		"status":   fmt.Sprintf("%d", statusCode),
	}

	m.CounterInc("alfred_gateway_requests_total", labels)
	m.HistogramObserve("alfred_gateway_request_duration_ms", labels, latencyMs)
	m.CounterAdd("alfred_gateway_tokens_total", labels, tokens)

	if cached {
		m.CounterInc("alfred_gateway_cache_hits_total", map[string]string{
			"provider": provider, "model": model,
		})
	}
}

// TrackWalletOperation records a wallet credit operation.
func (m *Metrics) TrackWalletOperation(opType, walletType string, amount float64) {
	labels := map[string]string{"type": opType, "wallet_type": walletType}
	m.CounterInc("alfred_wallet_operations_total", labels)
}

// TrackProviderHealth records provider health status.
func (m *Metrics) TrackProviderHealth(provider string, healthy bool) {
	val := 0.0
	if healthy {
		val = 1.0
	}
	m.GaugeSet("alfred_provider_healthy", map[string]string{"provider": provider}, val)
}

// TrackSafetyViolation records a safety pipeline violation.
func (m *Metrics) TrackSafetyViolation(category, severity string) {
	m.CounterInc("alfred_safety_violations_total", map[string]string{
		"category": category, "severity": severity,
	})
}

// ─── Prometheus Exposition Format ───────────────────────────

// Handler returns an http.HandlerFunc that serves /metrics in
// Prometheus text exposition format.
func (m *Metrics) Handler() http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "text/plain; version=0.0.4; charset=utf-8")

		var sb strings.Builder

		// Timestamp
		sb.WriteString(fmt.Sprintf("# Alfred Gateway Metrics - %s\n\n", time.Now().UTC().Format(time.RFC3339)))

		m.mu.RLock()
		defer m.mu.RUnlock()

		// Counters
		for name, byLabel := range m.counters {
			sb.WriteString(fmt.Sprintf("# TYPE %s counter\n", name))
			for lk, c := range byLabel {
				if lk == "" {
					sb.WriteString(fmt.Sprintf("%s %d\n", name, c.Value()))
				} else {
					sb.WriteString(fmt.Sprintf("%s{%s} %d\n", name, lk, c.Value()))
				}
			}
			sb.WriteString("\n")
		}

		// Gauges
		for name, byLabel := range m.gauges {
			sb.WriteString(fmt.Sprintf("# TYPE %s gauge\n", name))
			for lk, g := range byLabel {
				if lk == "" {
					sb.WriteString(fmt.Sprintf("%s %f\n", name, g.Value()))
				} else {
					sb.WriteString(fmt.Sprintf("%s{%s} %f\n", name, lk, g.Value()))
				}
			}
			sb.WriteString("\n")
		}

		// Histograms
		for name, byLabel := range m.histograms {
			sb.WriteString(fmt.Sprintf("# TYPE %s histogram\n", name))
			for lk, h := range byLabel {
				h.mu.Lock()
				prefix := name
				if lk != "" {
					prefix = fmt.Sprintf("%s{%s}", name, lk)
				}
				cumulative := int64(0)
				for i, b := range h.buckets {
					cumulative += h.counts[i]
					if lk != "" {
						sb.WriteString(fmt.Sprintf("%s_bucket{le=\"%g\",%s} %d\n", name, b, lk, cumulative))
					} else {
						sb.WriteString(fmt.Sprintf("%s_bucket{le=\"%g\"} %d\n", name, b, cumulative))
					}
				}
				cumulative += h.counts[len(h.buckets)]
				if lk != "" {
					sb.WriteString(fmt.Sprintf("%s_bucket{le=\"+Inf\",%s} %d\n", name, lk, cumulative))
				} else {
					sb.WriteString(fmt.Sprintf("%s_bucket{le=\"+Inf\"} %d\n", name, cumulative))
				}
				sb.WriteString(fmt.Sprintf("%s_sum %f\n", prefix, h.sum))
				sb.WriteString(fmt.Sprintf("%s_count %d\n", prefix, h.count))
				h.mu.Unlock()
			}
			sb.WriteString("\n")
		}

		_, _ = w.Write([]byte(sb.String()))
	}
}
