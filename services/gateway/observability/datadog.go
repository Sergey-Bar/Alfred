/*
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L2
Logic:       DogStatsD metrics exporter for Datadog APM.
             Sends counters, gauges, histograms over UDP
             to a local Datadog Agent (default 127.0.0.1:8125).
Root Cause:  Sprint task T147 — Datadog integration.
Context:     Complements Prometheus with push-based metrics.
Suitability: L2 — standard StatsD UDP protocol.
──────────────────────────────────────────────────────────────
*/

package observability

import (
	"fmt"
	"net"
	"strings"
	"sync"
	"time"

	"github.com/rs/zerolog"
)

// DatadogConfig holds Datadog Agent connection settings.
type DatadogConfig struct {
	// Address of the DogStatsD agent (default: "127.0.0.1:8125")
	Address string
	// Namespace prefix for all metrics (default: "alfred.gateway")
	Namespace string
	// Global tags added to every metric
	GlobalTags []string
	// FlushInterval controls how often buffered metrics ship (default: 10s)
	FlushInterval time.Duration
	// BufferSize is the max number of metrics buffered before flush (default: 256)
	BufferSize int
	// Enabled controls whether metrics are sent at all
	Enabled bool
}

// DefaultDatadogConfig returns sane defaults.
func DefaultDatadogConfig() DatadogConfig {
	return DatadogConfig{
		Address:       "127.0.0.1:8125",
		Namespace:     "alfred.gateway",
		GlobalTags:    nil,
		FlushInterval: 10 * time.Second,
		BufferSize:    256,
		Enabled:       false,
	}
}

// DatadogExporter sends metrics to a DogStatsD agent over UDP.
type DatadogExporter struct {
	cfg    DatadogConfig
	conn   net.Conn
	logger zerolog.Logger

	mu     sync.Mutex
	buffer []string
	stopCh chan struct{}
	wg     sync.WaitGroup
}

// NewDatadogExporter creates and starts a Datadog exporter.
// The exporter is a no-op if cfg.Enabled is false.
func NewDatadogExporter(cfg DatadogConfig, logger zerolog.Logger) (*DatadogExporter, error) {
	dd := &DatadogExporter{
		cfg:    cfg,
		logger: logger.With().Str("component", "datadog").Logger(),
		buffer: make([]string, 0, cfg.BufferSize),
		stopCh: make(chan struct{}),
	}

	if !cfg.Enabled {
		dd.logger.Info().Msg("Datadog exporter disabled — metrics will not be sent")
		return dd, nil
	}

	conn, err := net.Dial("udp", cfg.Address)
	if err != nil {
		return nil, fmt.Errorf("datadog: cannot connect to %s: %w", cfg.Address, err)
	}
	dd.conn = conn

	// Start the periodic flush goroutine
	dd.wg.Add(1)
	go dd.flushLoop()

	dd.logger.Info().
		Str("address", cfg.Address).
		Str("namespace", cfg.Namespace).
		Dur("flush_interval", cfg.FlushInterval).
		Msg("Datadog exporter started")

	return dd, nil
}

// Stop gracefully shuts down the exporter.
func (dd *DatadogExporter) Stop() {
	if !dd.cfg.Enabled {
		return
	}
	close(dd.stopCh)
	dd.wg.Wait()

	// Final flush
	dd.flush()
	if dd.conn != nil {
		dd.conn.Close()
	}
	dd.logger.Info().Msg("Datadog exporter stopped")
}

// ─── Public API ─────────────────────────────────────────────

// Count sends a counter metric.
func (dd *DatadogExporter) Count(name string, value int64, tags ...string) {
	dd.send(name, fmt.Sprintf("%d", value), "c", tags)
}

// Gauge sends a gauge metric.
func (dd *DatadogExporter) Gauge(name string, value float64, tags ...string) {
	dd.send(name, fmt.Sprintf("%f", value), "g", tags)
}

// Histogram sends a histogram/distribution metric.
func (dd *DatadogExporter) Histogram(name string, value float64, tags ...string) {
	dd.send(name, fmt.Sprintf("%f", value), "h", tags)
}

// Distribution sends a Datadog distribution metric (DDSketch).
func (dd *DatadogExporter) Distribution(name string, value float64, tags ...string) {
	dd.send(name, fmt.Sprintf("%f", value), "d", tags)
}

// Timing sends a timing metric in milliseconds.
func (dd *DatadogExporter) Timing(name string, duration time.Duration, tags ...string) {
	dd.send(name, fmt.Sprintf("%f", float64(duration.Milliseconds())), "ms", tags)
}

// ServiceCheck sends a Datadog service check.
// status: 0=OK, 1=WARNING, 2=CRITICAL, 3=UNKNOWN
func (dd *DatadogExporter) ServiceCheck(name string, status int, tags ...string) {
	if !dd.cfg.Enabled {
		return
	}
	fullName := dd.namespaced(name)
	tagStr := dd.formatTags(tags)
	line := fmt.Sprintf("_sc|%s|%d%s", fullName, status, tagStr)
	dd.buffer_line(line)
}

// Event sends a Datadog event.
func (dd *DatadogExporter) Event(title, text string, tags ...string) {
	if !dd.cfg.Enabled {
		return
	}
	tagStr := dd.formatTags(tags)
	line := fmt.Sprintf("_e{%d,%d}:%s|%s%s", len(title), len(text), title, text, tagStr)
	dd.buffer_line(line)
}

// ─── Convenience Wrappers for Gateway Metrics ───────────────

// RecordRequest records a gateway request with standard tags.
func (dd *DatadogExporter) RecordRequest(provider, model, status string, latencyMs float64) {
	tags := []string{
		"provider:" + provider,
		"model:" + model,
		"status:" + status,
	}
	dd.Count("request.count", 1, tags...)
	dd.Histogram("request.latency_ms", latencyMs, tags...)
}

// RecordTokens records token usage.
func (dd *DatadogExporter) RecordTokens(provider, model string, prompt, completion int64) {
	tags := []string{"provider:" + provider, "model:" + model}
	dd.Count("tokens.prompt", prompt, tags...)
	dd.Count("tokens.completion", completion, tags...)
	dd.Count("tokens.total", prompt+completion, tags...)
}

// RecordCacheResult records a cache hit or miss.
func (dd *DatadogExporter) RecordCacheResult(hit bool) {
	if hit {
		dd.Count("cache.hits", 1)
	} else {
		dd.Count("cache.misses", 1)
	}
}

// RecordWalletOp records a wallet operation.
func (dd *DatadogExporter) RecordWalletOp(op string, success bool) {
	status := "success"
	if !success {
		status = "failure"
	}
	dd.Count("wallet.ops", 1, "operation:"+op, "status:"+status)
}

// RecordSafetyViolation records a safety pipeline violation.
func (dd *DatadogExporter) RecordSafetyViolation(category, severity string) {
	dd.Count("safety.violations", 1, "category:"+category, "severity:"+severity)
}

// ─── Internal ───────────────────────────────────────────────

func (dd *DatadogExporter) send(name, value, metricType string, tags []string) {
	if !dd.cfg.Enabled {
		return
	}
	fullName := dd.namespaced(name)
	tagStr := dd.formatTags(tags)
	line := fmt.Sprintf("%s:%s|%s%s", fullName, value, metricType, tagStr)
	dd.buffer_line(line)
}

func (dd *DatadogExporter) namespaced(name string) string {
	if dd.cfg.Namespace != "" {
		return dd.cfg.Namespace + "." + name
	}
	return name
}

func (dd *DatadogExporter) formatTags(tags []string) string {
	allTags := make([]string, 0, len(dd.cfg.GlobalTags)+len(tags))
	allTags = append(allTags, dd.cfg.GlobalTags...)
	allTags = append(allTags, tags...)
	if len(allTags) == 0 {
		return ""
	}
	return "|#" + strings.Join(allTags, ",")
}

func (dd *DatadogExporter) buffer_line(line string) {
	dd.mu.Lock()
	dd.buffer = append(dd.buffer, line)
	shouldFlush := len(dd.buffer) >= dd.cfg.BufferSize
	dd.mu.Unlock()

	if shouldFlush {
		dd.flush()
	}
}

func (dd *DatadogExporter) flushLoop() {
	defer dd.wg.Done()
	ticker := time.NewTicker(dd.cfg.FlushInterval)
	defer ticker.Stop()

	for {
		select {
		case <-ticker.C:
			dd.flush()
		case <-dd.stopCh:
			return
		}
	}
}

func (dd *DatadogExporter) flush() {
	dd.mu.Lock()
	if len(dd.buffer) == 0 {
		dd.mu.Unlock()
		return
	}
	lines := dd.buffer
	dd.buffer = make([]string, 0, dd.cfg.BufferSize)
	dd.mu.Unlock()

	if dd.conn == nil {
		return
	}

	// DogStatsD supports multi-line payloads separated by \n
	payload := strings.Join(lines, "\n")
	_, err := dd.conn.Write([]byte(payload))
	if err != nil {
		dd.logger.Warn().Err(err).Int("lines", len(lines)).Msg("Failed to send metrics to Datadog")
	}
}
