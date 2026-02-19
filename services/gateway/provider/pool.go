/*
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L3
Logic:       Shared HTTP connection pool manager with per-provider
             configuration, connection reuse metrics, and
             configurable pool sizes. Centralizes transport
             creation to avoid each provider creating its own
             isolated pool, improving connection reuse across
             the gateway.
Root Cause:  Sprint task T020 — Connection pooling to upstream
             providers.
Context:     Each provider connector previously created its own
             http.Transport. This module provides a shared pool
             manager with observability and tuning knobs.
Suitability: L3 for connection pool design with concurrency.
──────────────────────────────────────────────────────────────
*/

package provider

import (
	"crypto/tls"
	"net"
	"net/http"
	"sync"
	"sync/atomic"
	"time"
)

// PoolConfig holds connection pool configuration.
type PoolConfig struct {
	// MaxIdleConns is the maximum number of idle connections across all hosts.
	MaxIdleConns int `json:"max_idle_conns"`
	// MaxIdleConnsPerHost is the maximum idle connections per host.
	MaxIdleConnsPerHost int `json:"max_idle_conns_per_host"`
	// MaxConnsPerHost limits total connections per host (0 = unlimited).
	MaxConnsPerHost int `json:"max_conns_per_host"`
	// IdleConnTimeout is how long idle connections remain in the pool.
	IdleConnTimeout time.Duration `json:"idle_conn_timeout"`
	// TLSHandshakeTimeout limits TLS handshake time.
	TLSHandshakeTimeout time.Duration `json:"tls_handshake_timeout"`
	// DialTimeout limits TCP connection establishment time.
	DialTimeout time.Duration `json:"dial_timeout"`
	// KeepAlive sets the interval for TCP keep-alive probes.
	KeepAlive time.Duration `json:"keep_alive"`
	// ResponseHeaderTimeout limits time waiting for response headers.
	ResponseHeaderTimeout time.Duration `json:"response_header_timeout"`
	// ExpectContinueTimeout limits time waiting for 100-continue.
	ExpectContinueTimeout time.Duration `json:"expect_continue_timeout"`
	// DisableCompression disables transport compression.
	DisableCompression bool `json:"disable_compression"`
	// ForceHTTP2 forces HTTP/2 negotiation via ALPN.
	ForceHTTP2 bool `json:"force_http2"`
}

// DefaultPoolConfig returns production-grade pool defaults.
func DefaultPoolConfig() PoolConfig {
	return PoolConfig{
		MaxIdleConns:          256,
		MaxIdleConnsPerHost:   32,
		MaxConnsPerHost:       64,
		IdleConnTimeout:       90 * time.Second,
		TLSHandshakeTimeout:  10 * time.Second,
		DialTimeout:          10 * time.Second,
		KeepAlive:            30 * time.Second,
		ResponseHeaderTimeout: 0, // handled by context deadline per request
		ExpectContinueTimeout: 1 * time.Second,
		DisableCompression:    false,
		ForceHTTP2:            true,
	}
}

// PoolMetrics tracks connection pool utilization metrics.
type PoolMetrics struct {
	// ActiveConnections is the current number of in-flight requests per provider.
	ActiveConnections sync.Map // map[string]*int64
	// TotalRequests is the cumulative request count per provider.
	TotalRequests sync.Map // map[string]*int64
	// TotalErrors is the cumulative error count per provider.
	TotalErrors sync.Map // map[string]*int64
	// ConnectionReuses counts how many requests reused an idle connection.
	ConnectionReuses sync.Map // map[string]*int64
}

// ConnectionPool manages shared HTTP transports and clients for providers.
type ConnectionPool struct {
	mu         sync.RWMutex
	transports map[string]*http.Transport
	clients    map[string]*http.Client
	configs    map[string]PoolConfig
	defaults   PoolConfig
	metrics    *PoolMetrics
}

// NewConnectionPool creates a new connection pool manager.
func NewConnectionPool(defaults PoolConfig) *ConnectionPool {
	return &ConnectionPool{
		transports: make(map[string]*http.Transport),
		clients:    make(map[string]*http.Client),
		configs:    make(map[string]PoolConfig),
		defaults:   defaults,
		metrics:    &PoolMetrics{},
	}
}

// DefaultConnectionPool returns a pool with production defaults.
func DefaultConnectionPool() *ConnectionPool {
	return NewConnectionPool(DefaultPoolConfig())
}

// Configure sets a custom pool configuration for a specific provider.
func (p *ConnectionPool) Configure(providerName string, cfg PoolConfig) {
	p.mu.Lock()
	defer p.mu.Unlock()
	p.configs[providerName] = cfg
	// Invalidate existing transport so it gets recreated with new config.
	delete(p.transports, providerName)
	delete(p.clients, providerName)
}

// GetTransport returns the shared HTTP transport for a provider.
// Creates one on first access using the provider's config (or defaults).
func (p *ConnectionPool) GetTransport(providerName string) *http.Transport {
	p.mu.RLock()
	if t, ok := p.transports[providerName]; ok {
		p.mu.RUnlock()
		return t
	}
	p.mu.RUnlock()

	// Upgrade to write lock to create transport.
	p.mu.Lock()
	defer p.mu.Unlock()

	// Double-check after acquiring write lock.
	if t, ok := p.transports[providerName]; ok {
		return t
	}

	cfg := p.configFor(providerName)
	t := p.createTransport(cfg)
	p.transports[providerName] = t

	return t
}

// GetClient returns a shared HTTP client for a provider with the given timeout.
// The client uses the provider's shared transport.
func (p *ConnectionPool) GetClient(providerName string, timeout time.Duration) *http.Client {
	p.mu.RLock()
	if c, ok := p.clients[providerName]; ok {
		p.mu.RUnlock()
		return c
	}
	p.mu.RUnlock()

	p.mu.Lock()
	defer p.mu.Unlock()

	if c, ok := p.clients[providerName]; ok {
		return c
	}

	cfg := p.configFor(providerName)
	transport := p.createTransport(cfg)
	p.transports[providerName] = transport

	client := &http.Client{
		Transport: &metricsRoundTripper{
			inner:        transport,
			providerName: providerName,
			metrics:      p.metrics,
		},
		Timeout: timeout,
	}
	p.clients[providerName] = client

	return client
}

// Metrics returns the current pool metrics snapshot.
func (p *ConnectionPool) Metrics() map[string]map[string]int64 {
	result := make(map[string]map[string]int64)

	p.metrics.TotalRequests.Range(func(key, value interface{}) bool {
		name := key.(string)
		if _, ok := result[name]; !ok {
			result[name] = make(map[string]int64)
		}
		result[name]["total_requests"] = atomic.LoadInt64(value.(*int64))
		return true
	})

	p.metrics.TotalErrors.Range(func(key, value interface{}) bool {
		name := key.(string)
		if _, ok := result[name]; !ok {
			result[name] = make(map[string]int64)
		}
		result[name]["total_errors"] = atomic.LoadInt64(value.(*int64))
		return true
	})

	p.metrics.ActiveConnections.Range(func(key, value interface{}) bool {
		name := key.(string)
		if _, ok := result[name]; !ok {
			result[name] = make(map[string]int64)
		}
		result[name]["active_connections"] = atomic.LoadInt64(value.(*int64))
		return true
	})

	p.metrics.ConnectionReuses.Range(func(key, value interface{}) bool {
		name := key.(string)
		if _, ok := result[name]; !ok {
			result[name] = make(map[string]int64)
		}
		result[name]["connection_reuses"] = atomic.LoadInt64(value.(*int64))
		return true
	})

	return result
}

// Close gracefully closes all idle connections.
func (p *ConnectionPool) Close() {
	p.mu.Lock()
	defer p.mu.Unlock()
	for _, t := range p.transports {
		t.CloseIdleConnections()
	}
}

// configFor returns the pool config for a provider, falling back to defaults.
func (p *ConnectionPool) configFor(providerName string) PoolConfig {
	if cfg, ok := p.configs[providerName]; ok {
		return cfg
	}
	return p.defaults
}

// createTransport builds an http.Transport from pool config.
func (p *ConnectionPool) createTransport(cfg PoolConfig) *http.Transport {
	dialer := &net.Dialer{
		Timeout:   cfg.DialTimeout,
		KeepAlive: cfg.KeepAlive,
	}

	t := &http.Transport{
		DialContext:           dialer.DialContext,
		MaxIdleConns:          cfg.MaxIdleConns,
		MaxIdleConnsPerHost:   cfg.MaxIdleConnsPerHost,
		MaxConnsPerHost:       cfg.MaxConnsPerHost,
		IdleConnTimeout:       cfg.IdleConnTimeout,
		TLSHandshakeTimeout:  cfg.TLSHandshakeTimeout,
		ResponseHeaderTimeout: cfg.ResponseHeaderTimeout,
		ExpectContinueTimeout: cfg.ExpectContinueTimeout,
		DisableCompression:    cfg.DisableCompression,
	}

	if cfg.ForceHTTP2 {
		t.TLSClientConfig = &tls.Config{
			NextProtos: []string{"h2", "http/1.1"},
			MinVersion: tls.VersionTLS12,
		}
		t.ForceAttemptHTTP2 = true
	}

	return t
}

// metricsRoundTripper wraps an http.RoundTripper to track connection metrics.
type metricsRoundTripper struct {
	inner        http.RoundTripper
	providerName string
	metrics      *PoolMetrics
}

func (m *metricsRoundTripper) RoundTrip(req *http.Request) (*http.Response, error) {
	// Increment active connections.
	active := m.getOrCreateCounter(&m.metrics.ActiveConnections, m.providerName)
	atomic.AddInt64(active, 1)
	defer atomic.AddInt64(active, -1)

	// Increment total requests.
	total := m.getOrCreateCounter(&m.metrics.TotalRequests, m.providerName)
	atomic.AddInt64(total, 1)

	resp, err := m.inner.RoundTrip(req)
	if err != nil {
		errCount := m.getOrCreateCounter(&m.metrics.TotalErrors, m.providerName)
		atomic.AddInt64(errCount, 1)
		return nil, err
	}

	// Track connection reuse via response header.
	if !resp.Close {
		reuses := m.getOrCreateCounter(&m.metrics.ConnectionReuses, m.providerName)
		atomic.AddInt64(reuses, 1)
	}

	return resp, nil
}

func (m *metricsRoundTripper) getOrCreateCounter(store *sync.Map, key string) *int64 {
	if val, ok := store.Load(key); ok {
		return val.(*int64)
	}
	counter := new(int64)
	actual, _ := store.LoadOrStore(key, counter)
	return actual.(*int64)
}
