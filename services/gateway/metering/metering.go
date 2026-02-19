/*
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L3
Logic:       Token metering engine foundation implementing token
             counting, cost calculation, streaming token accumulation,
             and async request logging. Uses character-based
             estimation (tiktoken requires CGo/WASM, deferred to
             production). Implements reserve-then-settle pattern
             for wallet integration.
Root Cause:  Sprint tasks T041-T046 — Token Metering Engine.
Context:     Financial correctness is critical. Token counts
             directly impact wallet deductions and billing.
             Must handle streaming (count-as-you-go) and
             non-streaming (count-from-usage) modes.
Suitability: L3 for metering engine with concurrency patterns.
──────────────────────────────────────────────────────────────
*/

package metering

import (
	"context"
	"sync"
	"sync/atomic"
	"time"
)

// TokenCounter estimates and counts tokens for metering purposes.
// T041: Token counting (character-based estimation; tiktoken deferred).
type TokenCounter struct {
	// charsPerToken is the average characters per token estimate.
	// English averages ~4 chars/token; code ~3.5; multilingual ~2.5.
	charsPerToken float64
}

// NewTokenCounter creates a token counter with configurable ratio.
func NewTokenCounter(charsPerToken float64) *TokenCounter {
	if charsPerToken <= 0 {
		charsPerToken = 4.0 // default: English text
	}
	return &TokenCounter{charsPerToken: charsPerToken}
}

// EstimateTokens estimates the token count for a text string.
func (tc *TokenCounter) EstimateTokens(text string) int {
	if len(text) == 0 {
		return 0
	}
	tokens := float64(len(text)) / tc.charsPerToken
	// Add overhead for special tokens (BOS, EOS, formatting).
	return int(tokens) + 3
}

// EstimateMessagesTokens estimates total tokens for a chat conversation.
func (tc *TokenCounter) EstimateMessagesTokens(messages []Message) int {
	total := 0
	for _, msg := range messages {
		// Each message has overhead: role token + separator.
		total += 4 // <im_start>, role, \n, content
		total += tc.EstimateTokens(msg.Content)
		if msg.Name != "" {
			total += tc.EstimateTokens(msg.Name)
		}
	}
	total += 2 // <im_start>assistant, final separator
	return total
}

// Message represents a simplified chat message for token counting.
type Message struct {
	Role    string `json:"role"`
	Content string `json:"content"`
	Name    string `json:"name,omitempty"`
}

// --- Cost Calculation Engine (T042) ---

// CostEngine calculates request costs based on token usage and pricing.
type CostEngine struct {
	mu      sync.RWMutex
	pricing map[string]ModelPrice
}

// ModelPrice holds per-model pricing.
type ModelPrice struct {
	Provider    string  `json:"provider"`
	Model       string  `json:"model"`
	InputPer1M  float64 `json:"input_per_1m"`  // USD per 1M input tokens
	OutputPer1M float64 `json:"output_per_1m"` // USD per 1M output tokens
	Free        bool    `json:"free"`
}

// NewCostEngine creates a cost engine with default pricing.
func NewCostEngine() *CostEngine {
	return &CostEngine{
		pricing: defaultPricing(),
	}
}

// Calculate computes the USD cost for a completed request.
func (ce *CostEngine) Calculate(provider, model string, inputTokens, outputTokens int) float64 {
	ce.mu.RLock()
	defer ce.mu.RUnlock()

	key := provider + "/" + model
	if p, ok := ce.pricing[key]; ok {
		if p.Free {
			return 0
		}
		inputCost := float64(inputTokens) / 1_000_000 * p.InputPer1M
		outputCost := float64(outputTokens) / 1_000_000 * p.OutputPer1M
		return inputCost + outputCost
	}

	// Fallback: try model name only.
	if p, ok := ce.pricing[model]; ok {
		if p.Free {
			return 0
		}
		inputCost := float64(inputTokens) / 1_000_000 * p.InputPer1M
		outputCost := float64(outputTokens) / 1_000_000 * p.OutputPer1M
		return inputCost + outputCost
	}

	return 0 // Unknown model — no cost
}

// Estimate estimates cost before the request completes (T043).
func (ce *CostEngine) Estimate(provider, model string, inputTokens, maxOutputTokens int) float64 {
	return ce.Calculate(provider, model, inputTokens, maxOutputTokens)
}

// IsFree returns true if the model is free to use (T049).
func (ce *CostEngine) IsFree(model string) bool {
	ce.mu.RLock()
	defer ce.mu.RUnlock()
	if p, ok := ce.pricing[model]; ok {
		return p.Free
	}
	return false
}

// UpdatePricing updates the pricing for a specific model.
func (ce *CostEngine) UpdatePricing(provider, model string, price ModelPrice) {
	ce.mu.Lock()
	defer ce.mu.Unlock()
	ce.pricing[provider+"/"+model] = price
}

func defaultPricing() map[string]ModelPrice {
	return map[string]ModelPrice{
		// OpenAI
		"openai/gpt-4o":             {Provider: "openai", Model: "gpt-4o", InputPer1M: 2.50, OutputPer1M: 10.00},
		"openai/gpt-4o-mini":        {Provider: "openai", Model: "gpt-4o-mini", InputPer1M: 0.15, OutputPer1M: 0.60},
		"openai/gpt-4-turbo":        {Provider: "openai", Model: "gpt-4-turbo", InputPer1M: 10.00, OutputPer1M: 30.00},
		"openai/gpt-3.5-turbo":      {Provider: "openai", Model: "gpt-3.5-turbo", InputPer1M: 0.50, OutputPer1M: 1.50},
		"openai/o1":                 {Provider: "openai", Model: "o1", InputPer1M: 15.00, OutputPer1M: 60.00},
		"openai/o1-mini":            {Provider: "openai", Model: "o1-mini", InputPer1M: 3.00, OutputPer1M: 12.00},
		// Anthropic
		"anthropic/claude-3-opus":    {Provider: "anthropic", Model: "claude-3-opus", InputPer1M: 15.00, OutputPer1M: 75.00},
		"anthropic/claude-3-sonnet":  {Provider: "anthropic", Model: "claude-3-sonnet", InputPer1M: 3.00, OutputPer1M: 15.00},
		"anthropic/claude-3-haiku":   {Provider: "anthropic", Model: "claude-3-haiku", InputPer1M: 0.25, OutputPer1M: 1.25},
		"anthropic/claude-3.5-sonnet": {Provider: "anthropic", Model: "claude-3.5-sonnet", InputPer1M: 3.00, OutputPer1M: 15.00},
		// Google
		"google/gemini-1.5-pro":     {Provider: "google", Model: "gemini-1.5-pro", InputPer1M: 1.25, OutputPer1M: 5.00},
		"google/gemini-1.5-flash":   {Provider: "google", Model: "gemini-1.5-flash", InputPer1M: 0.075, OutputPer1M: 0.30},
		"google/gemini-2.0-flash":   {Provider: "google", Model: "gemini-2.0-flash", InputPer1M: 0.10, OutputPer1M: 0.40},
		// Groq (free tier models)
		"groq/llama-3.1-70b":        {Provider: "groq", Model: "llama-3.1-70b", Free: true},
		"groq/llama-3.1-8b":         {Provider: "groq", Model: "llama-3.1-8b", Free: true},
		"groq/mixtral-8x7b":         {Provider: "groq", Model: "mixtral-8x7b", Free: true},
	}
}

// --- Streaming Token Counter (T044) ---

// StreamMeter counts tokens as SSE chunks arrive during streaming.
type StreamMeter struct {
	counter       *TokenCounter
	inputTokens   int
	outputTokens  int64 // atomic for concurrent access
	chunkCount    int64
	startTime     time.Time
}

// NewStreamMeter creates a stream meter pre-loaded with input token count.
func NewStreamMeter(counter *TokenCounter, inputTokens int) *StreamMeter {
	return &StreamMeter{
		counter:     counter,
		inputTokens: inputTokens,
		startTime:   time.Now(),
	}
}

// AddChunk processes a streaming chunk and accumulates output tokens.
func (sm *StreamMeter) AddChunk(text string) {
	tokens := sm.counter.EstimateTokens(text)
	atomic.AddInt64(&sm.outputTokens, int64(tokens))
	atomic.AddInt64(&sm.chunkCount, 1)
}

// InputTokens returns the pre-calculated input token count.
func (sm *StreamMeter) InputTokens() int {
	return sm.inputTokens
}

// OutputTokens returns the accumulated output token count.
func (sm *StreamMeter) OutputTokens() int {
	return int(atomic.LoadInt64(&sm.outputTokens))
}

// TotalTokens returns input + output tokens.
func (sm *StreamMeter) TotalTokens() int {
	return sm.inputTokens + sm.OutputTokens()
}

// ChunkCount returns the number of chunks processed.
func (sm *StreamMeter) ChunkCount() int {
	return int(atomic.LoadInt64(&sm.chunkCount))
}

// Duration returns the time since metering started.
func (sm *StreamMeter) Duration() time.Duration {
	return time.Since(sm.startTime)
}

// --- Reserve-Settle Pattern (T045) ---

// Reservation represents a pre-flight wallet hold for a request.
type Reservation struct {
	ID             string    `json:"id"`
	WalletID       string    `json:"wallet_id"`
	UserID         string    `json:"user_id"`
	Model          string    `json:"model"`
	Provider       string    `json:"provider"`
	EstimatedCost  float64   `json:"estimated_cost"`
	ActualCost     float64   `json:"actual_cost"`
	InputTokens    int       `json:"input_tokens"`
	OutputTokens   int       `json:"output_tokens"`
	Status         string    `json:"status"` // "reserved", "settled", "refunded", "expired"
	CreatedAt      time.Time `json:"created_at"`
	SettledAt      *time.Time `json:"settled_at,omitempty"`
}

// ReservationStore manages cost reservations.
type ReservationStore struct {
	mu           sync.RWMutex
	reservations map[string]*Reservation
}

// NewReservationStore creates a new reservation store.
func NewReservationStore() *ReservationStore {
	return &ReservationStore{
		reservations: make(map[string]*Reservation),
	}
}

// Reserve creates a cost reservation before calling the provider.
func (rs *ReservationStore) Reserve(id, walletID, userID, provider, model string, estimatedCost float64, inputTokens int) *Reservation {
	r := &Reservation{
		ID:            id,
		WalletID:      walletID,
		UserID:        userID,
		Model:         model,
		Provider:      provider,
		EstimatedCost: estimatedCost,
		InputTokens:   inputTokens,
		Status:        "reserved",
		CreatedAt:     time.Now(),
	}

	rs.mu.Lock()
	rs.reservations[id] = r
	rs.mu.Unlock()

	return r
}

// Settle finalizes a reservation with actual usage.
func (rs *ReservationStore) Settle(id string, actualCost float64, outputTokens int) (*Reservation, error) {
	rs.mu.Lock()
	defer rs.mu.Unlock()

	r, ok := rs.reservations[id]
	if !ok {
		return nil, ErrReservationNotFound
	}
	if r.Status != "reserved" {
		return nil, ErrReservationAlreadySettled
	}

	now := time.Now()
	r.ActualCost = actualCost
	r.OutputTokens = outputTokens
	r.Status = "settled"
	r.SettledAt = &now

	return r, nil
}

// Refund cancels a reservation (e.g., provider error).
func (rs *ReservationStore) Refund(id string) (*Reservation, error) {
	rs.mu.Lock()
	defer rs.mu.Unlock()

	r, ok := rs.reservations[id]
	if !ok {
		return nil, ErrReservationNotFound
	}

	now := time.Now()
	r.Status = "refunded"
	r.ActualCost = 0
	r.SettledAt = &now

	return r, nil
}

// Get returns a reservation by ID.
func (rs *ReservationStore) Get(id string) (*Reservation, bool) {
	rs.mu.RLock()
	defer rs.mu.RUnlock()
	r, ok := rs.reservations[id]
	return r, ok
}

// --- Async Request Logger (T046) ---

// RequestLog represents a completed request log entry.
type RequestLog struct {
	RequestID      string    `json:"request_id"`
	UserID         string    `json:"user_id"`
	WalletID       string    `json:"wallet_id"`
	Provider       string    `json:"provider"`
	Model          string    `json:"model"`
	InputTokens    int       `json:"input_tokens"`
	OutputTokens   int       `json:"output_tokens"`
	TotalTokens    int       `json:"total_tokens"`
	Cost           float64   `json:"cost"`
	LatencyMs      int64     `json:"latency_ms"`
	Stream         bool      `json:"stream"`
	StatusCode     int       `json:"status_code"`
	Error          string    `json:"error,omitempty"`
	CacheHit       bool      `json:"cache_hit"`
	ToolCalls      int       `json:"tool_calls"`
	CreatedAt      time.Time `json:"created_at"`
}

// AsyncLogger writes request logs asynchronously via a buffered channel.
type AsyncLogger struct {
	ch     chan RequestLog
	wg     sync.WaitGroup
	writer LogWriter
}

// LogWriter is the interface for persisting request logs.
type LogWriter interface {
	WriteLog(ctx context.Context, log RequestLog) error
	WriteBatch(ctx context.Context, logs []RequestLog) error
}

// NewAsyncLogger creates an async logger with configurable buffer size.
func NewAsyncLogger(writer LogWriter, bufferSize int) *AsyncLogger {
	if bufferSize <= 0 {
		bufferSize = 10000
	}
	al := &AsyncLogger{
		ch:     make(chan RequestLog, bufferSize),
		writer: writer,
	}
	al.wg.Add(1)
	go al.drain()
	return al
}

// Log queues a request log entry for async writing.
func (al *AsyncLogger) Log(entry RequestLog) {
	select {
	case al.ch <- entry:
		// Successfully queued.
	default:
		// Buffer full — drop the log (counter should be incremented).
	}
}

// Close flushes pending logs and stops the async writer.
func (al *AsyncLogger) Close() {
	close(al.ch)
	al.wg.Wait()
}

// drain processes log entries from the channel in batches.
func (al *AsyncLogger) drain() {
	defer al.wg.Done()

	batch := make([]RequestLog, 0, 100)
	ticker := time.NewTicker(1 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case entry, ok := <-al.ch:
			if !ok {
				// Channel closed — flush remaining.
				if len(batch) > 0 {
					al.flushBatch(batch)
				}
				return
			}
			batch = append(batch, entry)
			if len(batch) >= 100 {
				al.flushBatch(batch)
				batch = batch[:0]
			}
		case <-ticker.C:
			if len(batch) > 0 {
				al.flushBatch(batch)
				batch = batch[:0]
			}
		}
	}
}

func (al *AsyncLogger) flushBatch(batch []RequestLog) {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	_ = al.writer.WriteBatch(ctx, batch)
}

// --- Sentinel Errors ---

type meteringError string

func (e meteringError) Error() string { return string(e) }

const (
	ErrReservationNotFound      = meteringError("reservation not found")
	ErrReservationAlreadySettled = meteringError("reservation already settled")
	ErrInsufficientBalance      = meteringError("insufficient wallet balance")
)
