/*
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L2
Logic:       PagerDuty Events API v2 integration for Alfred.
             Fires alerts on critical provider failures,
             wallet exhaustion, and safety pipeline blocks.
Root Cause:  Sprint task T148 — PagerDuty alert integration.
Context:     SRE needs pager escalation for P1 incidents.
Suitability: L2 — standard HTTP webhook integration.
──────────────────────────────────────────────────────────────
*/

package observability

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"

	"github.com/rs/zerolog"
)

// PagerDutyConfig holds configuration for PagerDuty Events API v2.
type PagerDutyConfig struct {
	// RoutingKey is the PagerDuty Events API v2 integration key.
	RoutingKey string
	// Enabled controls whether alerts are sent.
	Enabled bool
	// SourceName identifies this gateway instance (e.g., "alfred-gw-prod-01").
	SourceName string
	// HTTPTimeout for the PagerDuty API call.
	HTTPTimeout time.Duration
}

// DefaultPagerDutyConfig returns defaults.
func DefaultPagerDutyConfig() PagerDutyConfig {
	return PagerDutyConfig{
		RoutingKey:  "",
		Enabled:     false,
		SourceName:  "alfred-gateway",
		HTTPTimeout: 10 * time.Second,
	}
}

// PagerDutySeverity maps to PagerDuty alert severity.
type PagerDutySeverity string

const (
	PDSeverityCritical PagerDutySeverity = "critical"
	PDSeverityError    PagerDutySeverity = "error"
	PDSeverityWarning  PagerDutySeverity = "warning"
	PDSeverityInfo     PagerDutySeverity = "info"
)

// PagerDutyClient sends incidents to PagerDuty Events API v2.
type PagerDutyClient struct {
	cfg    PagerDutyConfig
	client *http.Client
	logger zerolog.Logger
}

const pagerDutyEventsURL = "https://events.pagerduty.com/v2/enqueue"

// NewPagerDutyClient creates a PagerDuty alerting client.
func NewPagerDutyClient(cfg PagerDutyConfig, logger zerolog.Logger) *PagerDutyClient {
	return &PagerDutyClient{
		cfg: cfg,
		client: &http.Client{
			Timeout: cfg.HTTPTimeout,
		},
		logger: logger.With().Str("component", "pagerduty").Logger(),
	}
}

// TriggerAlert fires a PagerDuty alert.
func (pd *PagerDutyClient) TriggerAlert(
	severity PagerDutySeverity,
	summary string,
	dedupKey string,
	details map[string]interface{},
) error {
	if !pd.cfg.Enabled || pd.cfg.RoutingKey == "" {
		pd.logger.Debug().Str("summary", summary).Msg("PagerDuty disabled — alert suppressed")
		return nil
	}

	payload := map[string]interface{}{
		"routing_key":  pd.cfg.RoutingKey,
		"event_action": "trigger",
		"dedup_key":    dedupKey,
		"payload": map[string]interface{}{
			"summary":   summary,
			"severity":  string(severity),
			"source":    pd.cfg.SourceName,
			"component": "alfred-gateway",
			"group":     "ai-platform",
			"class":     "infrastructure",
			"timestamp": time.Now().UTC().Format(time.RFC3339),
			"custom_details": details,
		},
	}

	body, err := json.Marshal(payload)
	if err != nil {
		return fmt.Errorf("pagerduty: marshal failed: %w", err)
	}

	resp, err := pd.client.Post(pagerDutyEventsURL, "application/json", bytes.NewReader(body))
	if err != nil {
		pd.logger.Error().Err(err).Str("dedup_key", dedupKey).Msg("PagerDuty API call failed")
		return fmt.Errorf("pagerduty: API call failed: %w", err)
	}
	defer resp.Body.Close()
	io.Copy(io.Discard, resp.Body)

	if resp.StatusCode >= 400 {
		pd.logger.Error().Int("status", resp.StatusCode).Str("dedup_key", dedupKey).Msg("PagerDuty API error")
		return fmt.Errorf("pagerduty: HTTP %d", resp.StatusCode)
	}

	pd.logger.Info().Str("dedup_key", dedupKey).Str("severity", string(severity)).Msg("PagerDuty alert triggered")
	return nil
}

// ResolveAlert resolves a previously triggered alert.
func (pd *PagerDutyClient) ResolveAlert(dedupKey string) error {
	if !pd.cfg.Enabled || pd.cfg.RoutingKey == "" {
		return nil
	}

	payload := map[string]interface{}{
		"routing_key":  pd.cfg.RoutingKey,
		"event_action": "resolve",
		"dedup_key":    dedupKey,
	}

	body, err := json.Marshal(payload)
	if err != nil {
		return fmt.Errorf("pagerduty: marshal failed: %w", err)
	}

	resp, err := pd.client.Post(pagerDutyEventsURL, "application/json", bytes.NewReader(body))
	if err != nil {
		return fmt.Errorf("pagerduty: resolve call failed: %w", err)
	}
	defer resp.Body.Close()
	io.Copy(io.Discard, resp.Body)

	pd.logger.Info().Str("dedup_key", dedupKey).Msg("PagerDuty alert resolved")
	return nil
}

// ─── Convenience Wrappers for Common Alerts ─────────────────

// AlertProviderDown fires a critical alert when a provider fails health checks.
func (pd *PagerDutyClient) AlertProviderDown(provider string, errorMsg string) error {
	return pd.TriggerAlert(
		PDSeverityCritical,
		fmt.Sprintf("Alfred: LLM provider %s is DOWN", provider),
		fmt.Sprintf("alfred-provider-down-%s", provider),
		map[string]interface{}{
			"provider": provider,
			"error":    errorMsg,
		},
	)
}

// AlertProviderRecovered resolves a provider-down alert.
func (pd *PagerDutyClient) AlertProviderRecovered(provider string) error {
	return pd.ResolveAlert(fmt.Sprintf("alfred-provider-down-%s", provider))
}

// AlertWalletExhausted fires when a wallet hits its hard limit.
func (pd *PagerDutyClient) AlertWalletExhausted(walletID, ownerName string, balance float64) error {
	return pd.TriggerAlert(
		PDSeverityError,
		fmt.Sprintf("Alfred: Wallet exhausted for %s (balance: $%.2f)", ownerName, balance),
		fmt.Sprintf("alfred-wallet-exhausted-%s", walletID),
		map[string]interface{}{
			"wallet_id": walletID,
			"owner":     ownerName,
			"balance":   balance,
		},
	)
}

// AlertHighErrorRate fires when the gateway error rate exceeds threshold.
func (pd *PagerDutyClient) AlertHighErrorRate(errorPct float64, window string) error {
	return pd.TriggerAlert(
		PDSeverityCritical,
		fmt.Sprintf("Alfred: Gateway error rate %.1f%% over %s", errorPct, window),
		"alfred-high-error-rate",
		map[string]interface{}{
			"error_percentage": errorPct,
			"window":           window,
		},
	)
}

// AlertSafetyBlock fires when the safety pipeline blocks a request with critical violations.
func (pd *PagerDutyClient) AlertSafetyBlock(userID string, violationCount int, categories []string) error {
	return pd.TriggerAlert(
		PDSeverityWarning,
		fmt.Sprintf("Alfred: Safety pipeline blocked request from user %s (%d violations)", userID, violationCount),
		fmt.Sprintf("alfred-safety-block-%s-%d", userID, time.Now().Unix()/300), // dedup per 5-min window
		map[string]interface{}{
			"user_id":         userID,
			"violation_count": violationCount,
			"categories":      categories,
		},
	)
}
