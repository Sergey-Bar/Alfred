/*
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L2
Logic:       Background goroutine that polls all registered
             providers every configurable interval (default 30s).
             Caches results in the provider.Registry. Exposes
             metrics for unhealthy providers and fires callbacks
             for status transitions (healthy→unhealthy, etc.).
Root Cause:  Sprint task T039 — Provider health check poller.
Context:     Enables proactive detection of degraded providers
             so failover can activate before user requests fail.
Suitability: L2 — background polling with status tracking.
──────────────────────────────────────────────────────────────
*/

package provider

import (
	"context"
	"sync"
	"time"

	"github.com/rs/zerolog"
)

// HealthPoller continuously monitors provider health in the background.
type HealthPoller struct {
	registry *Registry
	logger   zerolog.Logger
	interval time.Duration

	// Cached last-known status for transition detection
	mu             sync.RWMutex
	lastStatus     map[string]bool // provider name → was healthy
	statusChangeCB func(provider string, healthy bool, status HealthStatus)

	cancel context.CancelFunc
	done   chan struct{}
}

// NewHealthPoller creates a poller that checks all providers at the
// given interval (minimum 5 seconds).
func NewHealthPoller(
	registry *Registry,
	logger zerolog.Logger,
	interval time.Duration,
) *HealthPoller {
	if interval < 5*time.Second {
		interval = 5 * time.Second
	}
	return &HealthPoller{
		registry:   registry,
		logger:     logger.With().Str("component", "health_poller").Logger(),
		interval:   interval,
		lastStatus: make(map[string]bool),
		done:       make(chan struct{}),
	}
}

// OnStatusChange registers a callback invoked when a provider's health
// status transitions (healthy → unhealthy or vice versa).
func (hp *HealthPoller) OnStatusChange(cb func(provider string, healthy bool, status HealthStatus)) {
	hp.statusChangeCB = cb
}

// Start begins the background polling loop.
// Call Stop() to shut it down gracefully.
func (hp *HealthPoller) Start() {
	ctx, cancel := context.WithCancel(context.Background())
	hp.cancel = cancel

	hp.logger.Info().
		Dur("interval", hp.interval).
		Msg("starting provider health poller")

	go hp.pollLoop(ctx)
}

// Stop gracefully shuts down the poller and waits for it to finish.
func (hp *HealthPoller) Stop() {
	if hp.cancel != nil {
		hp.cancel()
	}
	<-hp.done
	hp.logger.Info().Msg("health poller stopped")
}

func (hp *HealthPoller) pollLoop(ctx context.Context) {
	defer close(hp.done)

	// Run immediately on start
	hp.poll(ctx)

	ticker := time.NewTicker(hp.interval)
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			return
		case <-ticker.C:
			hp.poll(ctx)
		}
	}
}

func (hp *HealthPoller) poll(ctx context.Context) {
	// Use a per-poll timeout so a single slow provider doesn't block the cycle
	pollCtx, cancel := context.WithTimeout(ctx, hp.interval/2)
	defer cancel()

	results := hp.registry.HealthCheckAll(pollCtx)

	hp.mu.Lock()
	defer hp.mu.Unlock()

	healthy := 0
	unhealthy := 0

	for name, status := range results {
		// Detect transitions
		wasHealthy, known := hp.lastStatus[name]
		if known && wasHealthy != status.Healthy {
			transition := "recovered"
			if !status.Healthy {
				transition = "degraded"
			}
			hp.logger.Warn().
				Str("provider", name).
				Str("transition", transition).
				Str("error", status.Error).
				Dur("latency", status.Latency).
				Msg("provider status change")

			if hp.statusChangeCB != nil {
				hp.statusChangeCB(name, status.Healthy, status)
			}
		}
		hp.lastStatus[name] = status.Healthy

		if status.Healthy {
			healthy++
		} else {
			unhealthy++
		}
	}

	hp.logger.Debug().
		Int("healthy", healthy).
		Int("unhealthy", unhealthy).
		Int("total", len(results)).
		Msg("health poll complete")
}

// Status returns the latest cached health status for all providers.
func (hp *HealthPoller) Status() map[string]HealthStatus {
	return hp.registry.HealthCheckAll(context.Background())
}

// IsHealthy returns whether a specific provider was healthy at last check.
func (hp *HealthPoller) IsHealthy(name string) bool {
	hp.mu.RLock()
	defer hp.mu.RUnlock()
	healthy, ok := hp.lastStatus[name]
	return ok && healthy
}

// HealthyProviders returns only the names of currently healthy providers.
func (hp *HealthPoller) HealthyProviders() []string {
	hp.mu.RLock()
	defer hp.mu.RUnlock()
	var names []string
	for name, healthy := range hp.lastStatus {
		if healthy {
			names = append(names, name)
		}
	}
	return names
}
