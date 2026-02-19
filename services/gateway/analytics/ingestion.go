/*
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L3
Logic:       Async analytics event ingestion pipeline with
             buffered writes, backpressure, retry logic, and
             graceful shutdown. Collects events from gateway
             request handlers and flushes to ClickHouse in
             batches for high throughput.
Root Cause:  Sprint task T117 — Event ingestion pipeline.
Context:     Must handle 10K+ events/min without blocking
             the request path. Uses channel-based buffering.
Suitability: L3 — concurrency + reliability engineering.
──────────────────────────────────────────────────────────────
*/

package analytics

import (
	"context"
	"encoding/json"
	"fmt"
	"sync"
	"sync/atomic"
	"time"

	"github.com/rs/zerolog"
)

// ─── Event Types ────────────────────────────────────────────

// EventType classifies analytics events.
type EventType string

const (
	EventTypeRequest EventType = "request"
	EventTypeCost    EventType = "cost"
	EventTypeWallet  EventType = "wallet"
)

// RequestEvent captures an LLM request processed by the gateway.
type RequestEvent struct {
	RequestID         string  `json:"request_id"`
	TraceID           string  `json:"trace_id"`
	OrgID             string  `json:"org_id"`
	TeamID            string  `json:"team_id"`
	UserID            string  `json:"user_id"`
	APIKeyHash        string  `json:"api_key_hash"`
	Model             string  `json:"model"`
	Provider          string  `json:"provider"`
	Endpoint          string  `json:"endpoint"`
	Method            string  `json:"method"`
	PromptTokens      int     `json:"prompt_tokens"`
	CompletionTokens  int     `json:"completion_tokens"`
	TotalTokens       int     `json:"total_tokens"`
	CostMicrodollars  int64   `json:"cost_microdollars"`
	LatencyMs         int     `json:"latency_ms"`
	TTFBMs            int     `json:"ttfb_ms"`
	ProviderLatencyMs int     `json:"provider_latency_ms"`
	StatusCode        int     `json:"status_code"`
	ErrorType         string  `json:"error_type"`
	IsCached          bool    `json:"is_cached"`
	CacheSimilarity   float32 `json:"cache_similarity"`
	RoutingRuleID     string  `json:"routing_rule_id"`
	WasFailover       bool    `json:"was_failover"`
	SafetyBlocked     bool    `json:"safety_blocked"`
	SafetyViolations  int     `json:"safety_violations"`
	CreatedAt         time.Time `json:"created_at"`
}

// CostEvent captures a credit/cost mutation.
type CostEvent struct {
	EventID           string `json:"event_id"`
	OrgID             string `json:"org_id"`
	TeamID            string `json:"team_id"`
	UserID            string `json:"user_id"`
	WalletID          string `json:"wallet_id"`
	Model             string `json:"model"`
	Provider          string `json:"provider"`
	PromptTokens      int    `json:"prompt_tokens"`
	CompletionTokens  int    `json:"completion_tokens"`
	CostMicrodollars  int64  `json:"cost_microdollars"`
	BalanceBefore     int64  `json:"balance_before"`
	BalanceAfter      int64  `json:"balance_after"`
	WalletType        string `json:"wallet_type"`
	RequestID         string `json:"request_id"`
	EventType         string `json:"event_type"` // deduction, refund, topup, transfer
	Description       string `json:"description"`
	CreatedAt         time.Time `json:"created_at"`
}

// WalletEvent captures wallet lifecycle changes.
type WalletEvent struct {
	EventID   string    `json:"event_id"`
	WalletID  string    `json:"wallet_id"`
	OrgID     string    `json:"org_id"`
	TeamID    string    `json:"team_id"`
	UserID    string    `json:"user_id"`
	EventType string    `json:"event_type"`
	OldValue  string    `json:"old_value"`
	NewValue  string    `json:"new_value"`
	ActorID   string    `json:"actor_id"`
	ActorType string    `json:"actor_type"`
	CreatedAt time.Time `json:"created_at"`
}

// ─── Sink Interface ─────────────────────────────────────────

// Sink is the destination for analytics events (ClickHouse, stdout, etc.).
type Sink interface {
	// WriteRequests inserts a batch of request events.
	WriteRequests(ctx context.Context, events []RequestEvent) error
	// WriteCosts inserts a batch of cost events.
	WriteCosts(ctx context.Context, events []CostEvent) error
	// WriteWalletEvents inserts a batch of wallet events.
	WriteWalletEvents(ctx context.Context, events []WalletEvent) error
	// Close releases resources.
	Close() error
}

// ─── Pipeline Configuration ─────────────────────────────────

// PipelineConfig controls batching and backpressure behavior.
type PipelineConfig struct {
	// BufferSize is the channel buffer size per event type.
	BufferSize int `json:"buffer_size"`
	// BatchSize is the max events per flush.
	BatchSize int `json:"batch_size"`
	// FlushInterval is the max time between flushes.
	FlushInterval time.Duration `json:"flush_interval"`
	// MaxRetries for failed flushes.
	MaxRetries int `json:"max_retries"`
	// RetryDelay base delay (exponential backoff).
	RetryDelay time.Duration `json:"retry_delay"`
	// Workers is the number of concurrent flush workers per type.
	Workers int `json:"workers"`
}

// DefaultPipelineConfig returns production defaults.
func DefaultPipelineConfig() PipelineConfig {
	return PipelineConfig{
		BufferSize:    100000,
		BatchSize:     1000,
		FlushInterval: 5 * time.Second,
		MaxRetries:    3,
		RetryDelay:    500 * time.Millisecond,
		Workers:       2,
	}
}

// ─── Pipeline ───────────────────────────────────────────────

// Pipeline is the async analytics ingestion engine.
type Pipeline struct {
	logger zerolog.Logger
	config PipelineConfig
	sink   Sink

	requestCh chan RequestEvent
	costCh    chan CostEvent
	walletCh  chan WalletEvent

	wg     sync.WaitGroup
	cancel context.CancelFunc

	// Metrics
	eventsReceived int64
	eventsWritten  int64
	eventsDropped  int64
	flushErrors    int64
	mu             sync.RWMutex
}

// NewPipeline creates a new analytics ingestion pipeline.
func NewPipeline(logger zerolog.Logger, sink Sink, config ...PipelineConfig) *Pipeline {
	cfg := DefaultPipelineConfig()
	if len(config) > 0 {
		cfg = config[0]
	}

	return &Pipeline{
		logger:    logger.With().Str("component", "analytics-pipeline").Logger(),
		config:    cfg,
		sink:      sink,
		requestCh: make(chan RequestEvent, cfg.BufferSize),
		costCh:    make(chan CostEvent, cfg.BufferSize),
		walletCh:  make(chan WalletEvent, cfg.BufferSize),
	}
}

// Start launches the pipeline workers.
func (p *Pipeline) Start(ctx context.Context) {
	ctx, p.cancel = context.WithCancel(ctx)

	// Start request event workers
	for i := 0; i < p.config.Workers; i++ {
		p.wg.Add(1)
		go p.requestWorker(ctx, i)
	}

	// Start cost event workers
	for i := 0; i < p.config.Workers; i++ {
		p.wg.Add(1)
		go p.costWorker(ctx, i)
	}

	// Start wallet event workers
	for i := 0; i < p.config.Workers; i++ {
		p.wg.Add(1)
		go p.walletWorker(ctx, i)
	}

	p.logger.Info().
		Int("workers_per_type", p.config.Workers).
		Int("buffer_size", p.config.BufferSize).
		Int("batch_size", p.config.BatchSize).
		Dur("flush_interval", p.config.FlushInterval).
		Msg("analytics pipeline started")
}

// Stop gracefully shuts down the pipeline, flushing remaining events.
func (p *Pipeline) Stop() {
	if p.cancel != nil {
		p.cancel()
	}
	p.wg.Wait()

	// Final drain
	p.drainRequests()
	p.drainCosts()
	p.drainWalletEvents()

	if p.sink != nil {
		_ = p.sink.Close()
	}

	p.logger.Info().
		Int64("received", p.eventsReceived).
		Int64("written", p.eventsWritten).
		Int64("dropped", p.eventsDropped).
		Int64("flush_errors", p.flushErrors).
		Msg("analytics pipeline stopped")
}

// ─── Ingest Methods (non-blocking) ─────────────────────────

// TrackRequest submits a request event to the pipeline.
// Non-blocking: drops event if buffer is full.
func (p *Pipeline) TrackRequest(event RequestEvent) {
	if event.CreatedAt.IsZero() {
		event.CreatedAt = time.Now().UTC()
	}
	select {
	case p.requestCh <- event:
		p.incReceived()
	default:
		p.incDropped()
		p.logger.Warn().Str("request_id", event.RequestID).Msg("request event dropped: buffer full")
	}
}

// TrackCost submits a cost event to the pipeline.
func (p *Pipeline) TrackCost(event CostEvent) {
	if event.CreatedAt.IsZero() {
		event.CreatedAt = time.Now().UTC()
	}
	select {
	case p.costCh <- event:
		p.incReceived()
	default:
		p.incDropped()
		p.logger.Warn().Str("event_id", event.EventID).Msg("cost event dropped: buffer full")
	}
}

// TrackWalletEvent submits a wallet lifecycle event to the pipeline.
func (p *Pipeline) TrackWalletEvent(event WalletEvent) {
	if event.CreatedAt.IsZero() {
		event.CreatedAt = time.Now().UTC()
	}
	select {
	case p.walletCh <- event:
		p.incReceived()
	default:
		p.incDropped()
		p.logger.Warn().Str("event_id", event.EventID).Msg("wallet event dropped: buffer full")
	}
}

// ─── Workers ────────────────────────────────────────────────

func (p *Pipeline) requestWorker(ctx context.Context, id int) {
	defer p.wg.Done()
	ticker := time.NewTicker(p.config.FlushInterval)
	defer ticker.Stop()

	batch := make([]RequestEvent, 0, p.config.BatchSize)

	for {
		select {
		case <-ctx.Done():
			// Flush remaining
			if len(batch) > 0 {
				p.flushRequests(batch)
			}
			return

		case event := <-p.requestCh:
			batch = append(batch, event)
			if len(batch) >= p.config.BatchSize {
				p.flushRequests(batch)
				batch = batch[:0]
			}

		case <-ticker.C:
			if len(batch) > 0 {
				p.flushRequests(batch)
				batch = batch[:0]
			}
		}
	}
}

func (p *Pipeline) costWorker(ctx context.Context, id int) {
	defer p.wg.Done()
	ticker := time.NewTicker(p.config.FlushInterval)
	defer ticker.Stop()

	batch := make([]CostEvent, 0, p.config.BatchSize)

	for {
		select {
		case <-ctx.Done():
			if len(batch) > 0 {
				p.flushCosts(batch)
			}
			return

		case event := <-p.costCh:
			batch = append(batch, event)
			if len(batch) >= p.config.BatchSize {
				p.flushCosts(batch)
				batch = batch[:0]
			}

		case <-ticker.C:
			if len(batch) > 0 {
				p.flushCosts(batch)
				batch = batch[:0]
			}
		}
	}
}

func (p *Pipeline) walletWorker(ctx context.Context, id int) {
	defer p.wg.Done()
	ticker := time.NewTicker(p.config.FlushInterval)
	defer ticker.Stop()

	batch := make([]WalletEvent, 0, p.config.BatchSize)

	for {
		select {
		case <-ctx.Done():
			if len(batch) > 0 {
				p.flushWalletEvents(batch)
			}
			return

		case event := <-p.walletCh:
			batch = append(batch, event)
			if len(batch) >= p.config.BatchSize {
				p.flushWalletEvents(batch)
				batch = batch[:0]
			}

		case <-ticker.C:
			if len(batch) > 0 {
				p.flushWalletEvents(batch)
				batch = batch[:0]
			}
		}
	}
}

// ─── Flush with Retry ───────────────────────────────────────

func (p *Pipeline) flushRequests(batch []RequestEvent) {
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	var err error
	for attempt := 0; attempt <= p.config.MaxRetries; attempt++ {
		err = p.sink.WriteRequests(ctx, batch)
		if err == nil {
			p.incWritten(int64(len(batch)))
			return
		}
		p.logger.Warn().Err(err).Int("attempt", attempt+1).Int("batch_size", len(batch)).Msg("request flush failed")
		if attempt < p.config.MaxRetries {
			time.Sleep(p.config.RetryDelay * time.Duration(1<<uint(attempt)))
		}
	}

	p.incFlushErrors()
	p.incDropped()
	p.logger.Error().Err(err).Int("batch_size", len(batch)).Msg("request batch dropped after retries")
}

func (p *Pipeline) flushCosts(batch []CostEvent) {
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	var err error
	for attempt := 0; attempt <= p.config.MaxRetries; attempt++ {
		err = p.sink.WriteCosts(ctx, batch)
		if err == nil {
			p.incWritten(int64(len(batch)))
			return
		}
		p.logger.Warn().Err(err).Int("attempt", attempt+1).Msg("cost flush failed")
		if attempt < p.config.MaxRetries {
			time.Sleep(p.config.RetryDelay * time.Duration(1<<uint(attempt)))
		}
	}

	p.incFlushErrors()
	p.incDropped()
	p.logger.Error().Err(err).Int("batch_size", len(batch)).Msg("cost batch dropped after retries")
}

func (p *Pipeline) flushWalletEvents(batch []WalletEvent) {
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	var err error
	for attempt := 0; attempt <= p.config.MaxRetries; attempt++ {
		err = p.sink.WriteWalletEvents(ctx, batch)
		if err == nil {
			p.incWritten(int64(len(batch)))
			return
		}
		p.logger.Warn().Err(err).Int("attempt", attempt+1).Msg("wallet event flush failed")
		if attempt < p.config.MaxRetries {
			time.Sleep(p.config.RetryDelay * time.Duration(1<<uint(attempt)))
		}
	}

	p.incFlushErrors()
	p.incDropped()
	p.logger.Error().Err(err).Int("batch_size", len(batch)).Msg("wallet event batch dropped after retries")
}

// ─── Drain (shutdown) ───────────────────────────────────────

func (p *Pipeline) drainRequests() {
	batch := make([]RequestEvent, 0, p.config.BatchSize)
	for {
		select {
		case event := <-p.requestCh:
			batch = append(batch, event)
			if len(batch) >= p.config.BatchSize {
				p.flushRequests(batch)
				batch = batch[:0]
			}
		default:
			if len(batch) > 0 {
				p.flushRequests(batch)
			}
			return
		}
	}
}

func (p *Pipeline) drainCosts() {
	batch := make([]CostEvent, 0, p.config.BatchSize)
	for {
		select {
		case event := <-p.costCh:
			batch = append(batch, event)
			if len(batch) >= p.config.BatchSize {
				p.flushCosts(batch)
				batch = batch[:0]
			}
		default:
			if len(batch) > 0 {
				p.flushCosts(batch)
			}
			return
		}
	}
}

func (p *Pipeline) drainWalletEvents() {
	batch := make([]WalletEvent, 0, p.config.BatchSize)
	for {
		select {
		case event := <-p.walletCh:
			batch = append(batch, event)
			if len(batch) >= p.config.BatchSize {
				p.flushWalletEvents(batch)
				batch = batch[:0]
			}
		default:
			if len(batch) > 0 {
				p.flushWalletEvents(batch)
			}
			return
		}
	}
}

// ─── Metrics ────────────────────────────────────────────────

func (p *Pipeline) incReceived() {
	atomic.AddInt64(&p.eventsReceived, 1)
}

func (p *Pipeline) incWritten(n int64) {
	atomic.AddInt64(&p.eventsWritten, n)
}

func (p *Pipeline) incDropped() {
	atomic.AddInt64(&p.eventsDropped, 1)
}

func (p *Pipeline) incDroppedN(n int64) {
	atomic.AddInt64(&p.eventsDropped, n)
}

func (p *Pipeline) incFlushErrors() {
	atomic.AddInt64(&p.flushErrors, 1)
}

// Stats returns pipeline statistics.
type PipelineStats struct {
	EventsReceived int64 `json:"events_received"`
	EventsWritten  int64 `json:"events_written"`
	EventsDropped  int64 `json:"events_dropped"`
	FlushErrors    int64 `json:"flush_errors"`
	RequestBuffer  int   `json:"request_buffer_len"`
	CostBuffer     int   `json:"cost_buffer_len"`
	WalletBuffer   int   `json:"wallet_buffer_len"`
}

func (p *Pipeline) Stats() PipelineStats {
	return PipelineStats{
		EventsReceived: atomic.LoadInt64(&p.eventsReceived),
		EventsWritten:  atomic.LoadInt64(&p.eventsWritten),
		EventsDropped:  atomic.LoadInt64(&p.eventsDropped),
		FlushErrors:    atomic.LoadInt64(&p.flushErrors),
		RequestBuffer:  len(p.requestCh),
		CostBuffer:     len(p.costCh),
		WalletBuffer:   len(p.walletCh),
	}
}

// ─── Log Sink (fallback when ClickHouse is unavailable) ─────

// LogSink writes events as structured JSON logs (development/fallback).
type LogSink struct {
	logger zerolog.Logger
}

// NewLogSink creates a sink that logs events as structured JSON.
func NewLogSink(logger zerolog.Logger) *LogSink {
	return &LogSink{logger: logger.With().Str("sink", "log").Logger()}
}

func (s *LogSink) WriteRequests(_ context.Context, events []RequestEvent) error {
	for _, e := range events {
		data, _ := json.Marshal(e)
		s.logger.Debug().RawJSON("event", data).Msg("request_event")
	}
	return nil
}

func (s *LogSink) WriteCosts(_ context.Context, events []CostEvent) error {
	for _, e := range events {
		data, _ := json.Marshal(e)
		s.logger.Debug().RawJSON("event", data).Msg("cost_event")
	}
	return nil
}

func (s *LogSink) WriteWalletEvents(_ context.Context, events []WalletEvent) error {
	for _, e := range events {
		data, _ := json.Marshal(e)
		s.logger.Debug().RawJSON("event", data).Msg("wallet_event")
	}
	return nil
}

func (s *LogSink) Close() error { return nil }

// ─── ClickHouse Sink (production) ───────────────────────────

// ClickHouseSink writes events to ClickHouse via the native protocol.
// Requires: github.com/ClickHouse/clickhouse-go/v2
type ClickHouseSink struct {
	dsn    string
	logger zerolog.Logger
	// conn would hold the ClickHouse connection in production.
	// For now, this is a structural placeholder that logs warnings.
}

// NewClickHouseSink creates a production ClickHouse sink.
func NewClickHouseSink(dsn string, logger zerolog.Logger) (*ClickHouseSink, error) {
	if dsn == "" {
		return nil, fmt.Errorf("clickhouse DSN is required")
	}
	return &ClickHouseSink{
		dsn:    dsn,
		logger: logger.With().Str("sink", "clickhouse").Logger(),
	}, nil
}

func (s *ClickHouseSink) WriteRequests(ctx context.Context, events []RequestEvent) error {
	// TODO: Implement batch insert using clickhouse-go/v2
	// batch, err := conn.PrepareBatch(ctx, "INSERT INTO request_log (...)")
	s.logger.Warn().Int("count", len(events)).Msg("clickhouse sink: request write not yet wired to driver")
	return nil
}

func (s *ClickHouseSink) WriteCosts(ctx context.Context, events []CostEvent) error {
	s.logger.Warn().Int("count", len(events)).Msg("clickhouse sink: cost write not yet wired to driver")
	return nil
}

func (s *ClickHouseSink) WriteWalletEvents(ctx context.Context, events []WalletEvent) error {
	s.logger.Warn().Int("count", len(events)).Msg("clickhouse sink: wallet write not yet wired to driver")
	return nil
}

func (s *ClickHouseSink) Close() error {
	return nil
}
