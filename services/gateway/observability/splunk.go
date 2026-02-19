/*
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L2
Logic:       Splunk HTTP Event Collector (HEC) log forwarder.
             Batches structured JSON log events and POSTs them
             to a Splunk HEC endpoint over HTTP/S.
Root Cause:  Sprint task T149 — Splunk log forwarding.
Context:     Enterprise customers need SIEM integration.
Suitability: L2 — standard HTTP POST batching.
──────────────────────────────────────────────────────────────
*/

package observability

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"sync"
	"time"

	"github.com/rs/zerolog"
)

// SplunkConfig holds Splunk HEC connection settings.
type SplunkConfig struct {
	// HECURL is the Splunk HEC endpoint URL (e.g., "https://splunk.example.com:8088/services/collector/event")
	HECURL string
	// Token is the Splunk HEC authentication token.
	Token string
	// Index is the target Splunk index (optional, uses default if empty).
	Index string
	// Source identifies the log source.
	Source string
	// SourceType for structured JSON logs.
	SourceType string
	// FlushInterval controls periodic batch flush (default: 5s).
	FlushInterval time.Duration
	// BatchSize is the max events per batch before flush (default: 100).
	BatchSize int
	// Enabled controls whether logs are sent.
	Enabled bool
	// InsecureSkipVerify disables TLS verification (dev only).
	InsecureSkipVerify bool
}

// DefaultSplunkConfig returns sane defaults.
func DefaultSplunkConfig() SplunkConfig {
	return SplunkConfig{
		HECURL:        "",
		Token:         "",
		Index:         "alfred",
		Source:        "alfred-gateway",
		SourceType:    "_json",
		FlushInterval: 5 * time.Second,
		BatchSize:     100,
		Enabled:       false,
	}
}

// SplunkForwarder sends structured log events to Splunk HEC.
type SplunkForwarder struct {
	cfg    SplunkConfig
	client *http.Client
	logger zerolog.Logger

	mu     sync.Mutex
	buffer []splunkEvent
	stopCh chan struct{}
	wg     sync.WaitGroup
}

// splunkEvent is a single Splunk HEC event payload.
type splunkEvent struct {
	Time       float64                `json:"time"`
	Host       string                 `json:"host,omitempty"`
	Source     string                 `json:"source,omitempty"`
	SourceType string                 `json:"sourcetype,omitempty"`
	Index      string                 `json:"index,omitempty"`
	Event      map[string]interface{} `json:"event"`
}

// NewSplunkForwarder creates and starts a Splunk forwarder.
func NewSplunkForwarder(cfg SplunkConfig, logger zerolog.Logger) *SplunkForwarder {
	sf := &SplunkForwarder{
		cfg:    cfg,
		logger: logger.With().Str("component", "splunk").Logger(),
		buffer: make([]splunkEvent, 0, cfg.BatchSize),
		stopCh: make(chan struct{}),
		client: &http.Client{Timeout: 15 * time.Second},
	}

	if !cfg.Enabled {
		sf.logger.Info().Msg("Splunk forwarder disabled — logs will not be shipped")
		return sf
	}

	sf.wg.Add(1)
	go sf.flushLoop()

	sf.logger.Info().
		Str("hec_url", cfg.HECURL).
		Str("index", cfg.Index).
		Int("batch_size", cfg.BatchSize).
		Msg("Splunk forwarder started")

	return sf
}

// Stop gracefully shuts down the forwarder.
func (sf *SplunkForwarder) Stop() {
	if !sf.cfg.Enabled {
		return
	}
	close(sf.stopCh)
	sf.wg.Wait()
	sf.flush()
	sf.logger.Info().Msg("Splunk forwarder stopped")
}

// ─── Public API ─────────────────────────────────────────────

// Log sends a structured log event to Splunk.
func (sf *SplunkForwarder) Log(event map[string]interface{}) {
	if !sf.cfg.Enabled {
		return
	}

	se := splunkEvent{
		Time:       float64(time.Now().UnixMilli()) / 1000.0,
		Source:     sf.cfg.Source,
		SourceType: sf.cfg.SourceType,
		Index:      sf.cfg.Index,
		Event:      event,
	}

	sf.mu.Lock()
	sf.buffer = append(sf.buffer, se)
	shouldFlush := len(sf.buffer) >= sf.cfg.BatchSize
	sf.mu.Unlock()

	if shouldFlush {
		sf.flush()
	}
}

// LogRequest logs a gateway request event.
func (sf *SplunkForwarder) LogRequest(provider, model, status string, latencyMs float64, tokens int64, userID string) {
	sf.Log(map[string]interface{}{
		"event_type": "request",
		"provider":   provider,
		"model":      model,
		"status":     status,
		"latency_ms": latencyMs,
		"tokens":     tokens,
		"user_id":    userID,
	})
}

// LogSecurityEvent logs a safety pipeline event.
func (sf *SplunkForwarder) LogSecurityEvent(eventType, category, severity, userID string, details map[string]interface{}) {
	event := map[string]interface{}{
		"event_type": "security",
		"sub_type":   eventType,
		"category":   category,
		"severity":   severity,
		"user_id":    userID,
	}
	for k, v := range details {
		event[k] = v
	}
	sf.Log(event)
}

// LogAudit logs an audit trail event.
func (sf *SplunkForwarder) LogAudit(action, actorID, targetType, targetID string, details map[string]interface{}) {
	event := map[string]interface{}{
		"event_type":  "audit",
		"action":      action,
		"actor_id":    actorID,
		"target_type": targetType,
		"target_id":   targetID,
	}
	for k, v := range details {
		event[k] = v
	}
	sf.Log(event)
}

// LogWalletEvent logs wallet operations.
func (sf *SplunkForwarder) LogWalletEvent(operation, walletID, userID string, amount float64) {
	sf.Log(map[string]interface{}{
		"event_type": "wallet",
		"operation":  operation,
		"wallet_id":  walletID,
		"user_id":    userID,
		"amount":     amount,
	})
}

// ─── Internal ───────────────────────────────────────────────

func (sf *SplunkForwarder) flushLoop() {
	defer sf.wg.Done()
	ticker := time.NewTicker(sf.cfg.FlushInterval)
	defer ticker.Stop()

	for {
		select {
		case <-ticker.C:
			sf.flush()
		case <-sf.stopCh:
			return
		}
	}
}

func (sf *SplunkForwarder) flush() {
	sf.mu.Lock()
	if len(sf.buffer) == 0 {
		sf.mu.Unlock()
		return
	}
	events := sf.buffer
	sf.buffer = make([]splunkEvent, 0, sf.cfg.BatchSize)
	sf.mu.Unlock()

	// Splunk HEC accepts newline-delimited JSON events
	var buf bytes.Buffer
	encoder := json.NewEncoder(&buf)
	for _, ev := range events {
		if err := encoder.Encode(ev); err != nil {
			sf.logger.Warn().Err(err).Msg("Failed to encode Splunk event")
		}
	}

	req, err := http.NewRequest("POST", sf.cfg.HECURL, &buf)
	if err != nil {
		sf.logger.Error().Err(err).Msg("Failed to create Splunk HEC request")
		return
	}
	req.Header.Set("Authorization", fmt.Sprintf("Splunk %s", sf.cfg.Token))
	req.Header.Set("Content-Type", "application/json")

	resp, err := sf.client.Do(req)
	if err != nil {
		sf.logger.Error().Err(err).Int("events", len(events)).Msg("Failed to send events to Splunk HEC")
		return
	}
	defer resp.Body.Close()
	io.Copy(io.Discard, resp.Body)

	if resp.StatusCode >= 400 {
		sf.logger.Error().Int("status", resp.StatusCode).Int("events", len(events)).Msg("Splunk HEC returned error")
		return
	}

	sf.logger.Debug().Int("events", len(events)).Msg("Flushed events to Splunk HEC")
}
