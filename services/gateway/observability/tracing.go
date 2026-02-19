/*
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L3
Logic:       OpenTelemetry distributed tracing middleware for
             the Alfred gateway. Creates trace spans for full
             request lifecycle, propagates trace context via
             W3C Traceparent, and adds Alfred-specific attributes.
Root Cause:  Sprint task T145 — OpenTelemetry tracing.
Context:     Enables distributed tracing across gateway→provider.
Suitability: L3 — trace context propagation + span design.
──────────────────────────────────────────────────────────────
*/

package observability

import (
	"context"
	"crypto/rand"
	"encoding/hex"
	"fmt"
	"net/http"
	"strings"
	"sync"
	"time"

	chimw "github.com/go-chi/chi/v5/middleware"
	"github.com/rs/zerolog"
)

// ─── Trace / Span Types ────────────────────────────────────

// TraceID is a 128-bit trace identifier.
type TraceID [16]byte

func (t TraceID) String() string { return hex.EncodeToString(t[:]) }

// SpanID is a 64-bit span identifier.
type SpanID [8]byte

func (s SpanID) String() string { return hex.EncodeToString(s[:]) }

// GenerateTraceID creates a new random trace ID.
func GenerateTraceID() TraceID {
	var id TraceID
	_, _ = rand.Read(id[:])
	return id
}

// GenerateSpanID creates a new random span ID.
func GenerateSpanID() SpanID {
	var id SpanID
	_, _ = rand.Read(id[:])
	return id
}

// SpanContext holds trace propagation data.
type SpanContext struct {
	TraceID  TraceID
	SpanID   SpanID
	ParentID SpanID
	Sampled  bool
}

// Span represents a single operation in a distributed trace.
type Span struct {
	mu         sync.Mutex
	Name       string
	Context    SpanContext
	StartTime  time.Time
	EndTime    time.Time
	Attributes map[string]string
	Events     []SpanEvent
	StatusCode string // "OK", "ERROR", "UNSET"
	StatusMsg  string
	finished   bool
}

// SpanEvent is a time-stamped annotation on a span.
type SpanEvent struct {
	Name       string
	Timestamp  time.Time
	Attributes map[string]string
}

// SetAttribute adds a key-value attribute to the span.
func (s *Span) SetAttribute(key, value string) {
	s.mu.Lock()
	defer s.mu.Unlock()
	s.Attributes[key] = value
}

// AddEvent adds a timestamped event to the span.
func (s *Span) AddEvent(name string, attrs map[string]string) {
	s.mu.Lock()
	defer s.mu.Unlock()
	s.Events = append(s.Events, SpanEvent{
		Name:       name,
		Timestamp:  time.Now().UTC(),
		Attributes: attrs,
	})
}

// SetStatus sets the span's status.
func (s *Span) SetStatus(code, msg string) {
	s.mu.Lock()
	defer s.mu.Unlock()
	s.StatusCode = code
	s.StatusMsg = msg
}

// End marks the span as finished.
func (s *Span) End() {
	s.mu.Lock()
	defer s.mu.Unlock()
	if !s.finished {
		s.EndTime = time.Now().UTC()
		s.finished = true
	}
}

// Duration returns the span duration.
func (s *Span) Duration() time.Duration {
	s.mu.Lock()
	defer s.mu.Unlock()
	if s.finished {
		return s.EndTime.Sub(s.StartTime)
	}
	return time.Since(s.StartTime)
}

// ─── Trace Context Propagation (W3C Traceparent) ────────────

// ParseTraceparent extracts trace context from the W3C Traceparent header.
// Format: 00-{trace_id}-{parent_id}-{flags}
func ParseTraceparent(header string) (*SpanContext, error) {
	parts := strings.Split(header, "-")
	if len(parts) != 4 || parts[0] != "00" {
		return nil, fmt.Errorf("invalid traceparent format")
	}

	traceBytes, err := hex.DecodeString(parts[1])
	if err != nil || len(traceBytes) != 16 {
		return nil, fmt.Errorf("invalid trace ID")
	}

	parentBytes, err := hex.DecodeString(parts[2])
	if err != nil || len(parentBytes) != 8 {
		return nil, fmt.Errorf("invalid parent ID")
	}

	var traceID TraceID
	var parentID SpanID
	copy(traceID[:], traceBytes)
	copy(parentID[:], parentBytes)

	sampled := parts[3] == "01"

	return &SpanContext{
		TraceID:  traceID,
		ParentID: parentID,
		Sampled:  sampled,
	}, nil
}

// FormatTraceparent creates a W3C Traceparent header value.
func FormatTraceparent(ctx SpanContext) string {
	flags := "00"
	if ctx.Sampled {
		flags = "01"
	}
	return fmt.Sprintf("00-%s-%s-%s", ctx.TraceID, ctx.SpanID, flags)
}

// ─── Tracer ─────────────────────────────────────────────────

// SpanExporter receives completed spans for export to a backend.
type SpanExporter interface {
	Export(spans []*Span) error
	Shutdown() error
}

// Tracer creates and manages distributed trace spans.
type Tracer struct {
	mu       sync.Mutex
	logger   zerolog.Logger
	exporter SpanExporter
	sampler  float64 // 0.0-1.0 sampling rate
	buffer   []*Span
	bufSize  int
	stopCh   chan struct{} // signals periodic flush goroutine to stop
}

// NewTracer creates a new distributed tracer.
func NewTracer(logger zerolog.Logger, exporter SpanExporter, sampleRate float64) *Tracer {
	if sampleRate <= 0 {
		sampleRate = 1.0 // default: sample everything
	}
	t := &Tracer{
		logger:   logger.With().Str("component", "tracer").Logger(),
		exporter: exporter,
		sampler:  sampleRate,
		buffer:   make([]*Span, 0, 1000),
		bufSize:  1000,
		stopCh:   make(chan struct{}),
	}
	// Start periodic flush to avoid spans lingering in memory under low traffic.
	go t.periodicFlush()
	return t
}

// periodicFlush drains the span buffer every 10 seconds.
func (t *Tracer) periodicFlush() {
	ticker := time.NewTicker(10 * time.Second)
	defer ticker.Stop()
	for {
		select {
		case <-ticker.C:
			t.flush()
		case <-t.stopCh:
			return
		}
	}
}

// Stop shuts down the periodic flush goroutine and exports remaining spans.
func (t *Tracer) Stop() {
	close(t.stopCh)
	t.flush()
}

// StartSpan creates a new span.
func (t *Tracer) StartSpan(name string, parent *SpanContext) *Span {
	span := &Span{
		Name:       name,
		StartTime:  time.Now().UTC(),
		Attributes: make(map[string]string),
		StatusCode: "UNSET",
	}

	if parent != nil {
		span.Context = SpanContext{
			TraceID:  parent.TraceID,
			SpanID:   GenerateSpanID(),
			ParentID: parent.SpanID,
			Sampled:  parent.Sampled,
		}
	} else {
		// Apply sampling rate for root spans.
		sampled := t.sampler >= 1.0
		if !sampled && t.sampler > 0 {
			// Use deterministic sampling based on trace ID.
			traceID := GenerateTraceID()
			// Use the last 4 bytes of trace ID for deterministic sampling.
			if len(traceID) >= 4 {
				v := uint32(traceID[len(traceID)-1]) | uint32(traceID[len(traceID)-2])<<8
				sampled = float64(v)/float64(0xFFFF) < t.sampler
			}
			span.Context = SpanContext{
				TraceID: traceID,
				SpanID:  GenerateSpanID(),
				Sampled: sampled,
			}
		} else {
			span.Context = SpanContext{
				TraceID: GenerateTraceID(),
				SpanID:  GenerateSpanID(),
				Sampled: sampled,
			}
		}
	}

	return span
}

// EndSpan finishes a span and buffers it for export.
func (t *Tracer) EndSpan(span *Span) {
	span.End()
	if !span.Context.Sampled {
		return
	}

	t.mu.Lock()
	t.buffer = append(t.buffer, span)
	shouldFlush := len(t.buffer) >= t.bufSize
	t.mu.Unlock()

	if shouldFlush {
		t.flush()
	}
}

func (t *Tracer) flush() {
	t.mu.Lock()
	if len(t.buffer) == 0 {
		t.mu.Unlock()
		return
	}
	spans := t.buffer
	t.buffer = make([]*Span, 0, t.bufSize)
	t.mu.Unlock()

	if t.exporter != nil {
		if err := t.exporter.Export(spans); err != nil {
			t.logger.Error().Err(err).Int("spans", len(spans)).Msg("span export failed")
		}
	}
}

// Shutdown flushes remaining spans and closes the exporter.
func (t *Tracer) Shutdown() {
	t.flush()
	if t.exporter != nil {
		_ = t.exporter.Shutdown()
	}
}

// ─── Log Exporter (development) ─────────────────────────────

// LogExporter writes spans as structured log entries.
type LogExporter struct {
	logger zerolog.Logger
}

func NewLogExporter(logger zerolog.Logger) *LogExporter {
	return &LogExporter{logger: logger.With().Str("exporter", "log").Logger()}
}

func (e *LogExporter) Export(spans []*Span) error {
	for _, s := range spans {
		e.logger.Debug().
			Str("name", s.Name).
			Str("trace_id", s.Context.TraceID.String()).
			Str("span_id", s.Context.SpanID.String()).
			Str("parent_id", s.Context.ParentID.String()).
			Dur("duration", s.Duration()).
			Str("status", s.StatusCode).
			Int("attributes", len(s.Attributes)).
			Int("events", len(s.Events)).
			Msg("span")
	}
	return nil
}

func (e *LogExporter) Shutdown() error { return nil }

// ─── Tracing Context Key ───────────────────────────────────

type traceCtxKey struct{}

// SpanFromContext retrieves the current span from context.
func SpanFromContext(ctx context.Context) *Span {
	if s, ok := ctx.Value(traceCtxKey{}).(*Span); ok {
		return s
	}
	return nil
}

// ContextWithSpan stores a span in context.
func ContextWithSpan(ctx context.Context, span *Span) context.Context {
	return context.WithValue(ctx, traceCtxKey{}, span)
}

// ─── Tracing Middleware ─────────────────────────────────────

// TracingMiddleware creates spans for each HTTP request.
func TracingMiddleware(tracer *Tracer) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			// Extract trace context from incoming request
			var parent *SpanContext
			if tp := r.Header.Get("Traceparent"); tp != "" {
				parsed, err := ParseTraceparent(tp)
				if err == nil {
					parent = parsed
				}
			}

			// Start span for this request
			spanName := fmt.Sprintf("%s %s", r.Method, r.URL.Path)
			span := tracer.StartSpan(spanName, parent)

			// Set standard HTTP attributes
			span.SetAttribute("http.method", r.Method)
			span.SetAttribute("http.url", r.URL.String())
			span.SetAttribute("http.target", r.URL.Path)
			span.SetAttribute("http.host", r.Host)
			span.SetAttribute("http.user_agent", r.UserAgent())
			if reqID := chimw.GetReqID(r.Context()); reqID != "" {
				span.SetAttribute("alfred.request_id", reqID)
			}

			// Propagate trace context downstream
			w.Header().Set("Traceparent", FormatTraceparent(span.Context))
			w.Header().Set("X-Alfred-Trace-ID", span.Context.TraceID.String())

			// Store span in context
			ctx := ContextWithSpan(r.Context(), span)

			// Wrap response writer to capture status code
			rw := chimw.NewWrapResponseWriter(w, r.ProtoMajor)
			next.ServeHTTP(rw, r.WithContext(ctx))

			// Record response attributes
			span.SetAttribute("http.status_code", fmt.Sprintf("%d", rw.Status()))
			if rw.Status() >= 500 {
				span.SetStatus("ERROR", fmt.Sprintf("HTTP %d", rw.Status()))
			} else {
				span.SetStatus("OK", "")
			}

			// Finish span
			tracer.EndSpan(span)
		})
	}
}
