/*
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L3
Logic:       Geo-based routing — maps client IP to region,
             then filters providers to those serving that
             region. Supports data residency enforcement.
Root Cause:  Sprint task T096 — Geo-based routing.
Context:     Enterprise compliance (GDPR) requires data
             residency control. IP → region lookup is done
             via configurable CIDR ranges or external GeoIP.
Suitability: L3 — networking + compliance logic.
──────────────────────────────────────────────────────────────
*/

package routing

import (
	"net"
	"strings"
	"sync"

	"github.com/rs/zerolog"
)

// Region represents a geographic region for routing.
type Region string

const (
	RegionUSEast    Region = "us-east"
	RegionUSWest    Region = "us-west"
	RegionEUWest    Region = "eu-west"
	RegionEUCentral Region = "eu-central"
	RegionAPSE      Region = "ap-southeast"
	RegionAPNE      Region = "ap-northeast"
	RegionGlobal    Region = "global" // No restriction
)

// GeoRule maps an IP CIDR block to a region.
type GeoRule struct {
	CIDR    string `json:"cidr"`
	Region  Region `json:"region"`
	Comment string `json:"comment,omitempty"`
	net     *net.IPNet
}

// ProviderRegion declares which regions a provider is allowed to serve.
type ProviderRegion struct {
	Provider string   `json:"provider"`
	Regions  []Region `json:"regions"` // empty = global
}

// GeoConfig holds the geo-routing configuration.
type GeoConfig struct {
	// Enabled controls whether geo-routing is active.
	Enabled bool `json:"enabled"`
	// EnforceDataResidency blocks requests that would violate residency rules
	// (instead of just preferring closer providers).
	EnforceDataResidency bool `json:"enforce_data_residency"`
	// DefaultRegion when client IP doesn't match any rule.
	DefaultRegion Region `json:"default_region"`
	// IPRules are CIDR → region mappings (evaluated in order).
	IPRules []GeoRule `json:"ip_rules"`
	// ProviderRegions maps providers to their allowed regions.
	ProviderRegions []ProviderRegion `json:"provider_regions"`
}

// DefaultGeoConfig returns a disabled geo-routing config.
func DefaultGeoConfig() GeoConfig {
	return GeoConfig{
		Enabled:              false,
		EnforceDataResidency: false,
		DefaultRegion:        RegionGlobal,
	}
}

// ─── GeoRouter ──────────────────────────────────────────────

// GeoRouter filters providers based on client geographic location.
type GeoRouter struct {
	mu              sync.RWMutex
	cfg             GeoConfig
	logger          zerolog.Logger
	parsedRules     []GeoRule
	providerRegions map[string]map[Region]bool // provider → set of allowed regions
}

// NewGeoRouter creates a new geo-based router.
func NewGeoRouter(cfg GeoConfig, logger zerolog.Logger) (*GeoRouter, error) {
	gr := &GeoRouter{
		cfg:             cfg,
		logger:          logger.With().Str("component", "geo-router").Logger(),
		providerRegions: make(map[string]map[Region]bool),
	}

	if err := gr.loadRules(cfg); err != nil {
		return nil, err
	}

	gr.logger.Info().
		Bool("enabled", cfg.Enabled).
		Bool("enforce_residency", cfg.EnforceDataResidency).
		Int("ip_rules", len(gr.parsedRules)).
		Int("providers", len(gr.providerRegions)).
		Msg("Geo-router initialized")

	return gr, nil
}

// loadRules parses CIDR blocks and builds the provider→region map.
func (gr *GeoRouter) loadRules(cfg GeoConfig) error {
	gr.parsedRules = make([]GeoRule, 0, len(cfg.IPRules))
	for _, rule := range cfg.IPRules {
		_, ipNet, err := net.ParseCIDR(rule.CIDR)
		if err != nil {
			gr.logger.Warn().Str("cidr", rule.CIDR).Err(err).Msg("Invalid CIDR in geo rule — skipping")
			continue
		}
		parsed := rule
		parsed.net = ipNet
		gr.parsedRules = append(gr.parsedRules, parsed)
	}

	gr.providerRegions = make(map[string]map[Region]bool)
	for _, pr := range cfg.ProviderRegions {
		regionSet := make(map[Region]bool)
		for _, r := range pr.Regions {
			regionSet[r] = true
		}
		gr.providerRegions[pr.Provider] = regionSet
	}

	return nil
}

// UpdateConfig hot-reloads geo-routing configuration.
func (gr *GeoRouter) UpdateConfig(cfg GeoConfig) error {
	gr.mu.Lock()
	defer gr.mu.Unlock()
	gr.cfg = cfg
	return gr.loadRules(cfg)
}

// ─── Lookup ─────────────────────────────────────────────────

// ResolveRegion determines the region for a client IP address.
func (gr *GeoRouter) ResolveRegion(clientIP string) Region {
	if !gr.cfg.Enabled {
		return RegionGlobal
	}

	gr.mu.RLock()
	defer gr.mu.RUnlock()

	// Strip port if present
	host := clientIP
	if idx := strings.LastIndex(clientIP, ":"); idx != -1 {
		hostPart, _, err := net.SplitHostPort(clientIP)
		if err == nil {
			host = hostPart
		}
	}

	ip := net.ParseIP(host)
	if ip == nil {
		gr.logger.Debug().Str("ip", clientIP).Msg("Could not parse client IP — using default region")
		return gr.cfg.DefaultRegion
	}

	for _, rule := range gr.parsedRules {
		if rule.net.Contains(ip) {
			return rule.Region
		}
	}

	return gr.cfg.DefaultRegion
}

// FilterProviders returns only providers allowed to serve the given region.
// If geo-routing is disabled or no restrictions apply, returns all candidates.
func (gr *GeoRouter) FilterProviders(candidates []string, region Region) []string {
	if !gr.cfg.Enabled || region == RegionGlobal {
		return candidates
	}

	gr.mu.RLock()
	defer gr.mu.RUnlock()

	allowed := make([]string, 0, len(candidates))
	for _, provider := range candidates {
		regions, hasConfig := gr.providerRegions[provider]
		if !hasConfig {
			// No geo-config for provider — allow if not enforcing
			if !gr.cfg.EnforceDataResidency {
				allowed = append(allowed, provider)
			}
			continue
		}
		if regions[region] || regions[RegionGlobal] {
			allowed = append(allowed, provider)
		}
	}

	// If enforcement is on and nothing matched, this is a residency violation
	if gr.cfg.EnforceDataResidency && len(allowed) == 0 {
		gr.logger.Warn().
			Str("region", string(region)).
			Strs("candidates", candidates).
			Msg("Data residency violation — no provider available for region")
		return nil // Caller should block the request
	}

	// If non-enforcing and nothing matched, fall back to all candidates
	if len(allowed) == 0 {
		gr.logger.Debug().
			Str("region", string(region)).
			Msg("No geo-restricted providers — falling back to all candidates")
		return candidates
	}

	return allowed
}

// ─── Integration Helper ─────────────────────────────────────

// GeoRoutingDecision holds the result of geo-aware provider selection.
type GeoRoutingDecision struct {
	ClientIP          string   `json:"client_ip"`
	ResolvedRegion    Region   `json:"resolved_region"`
	AllowedProviders  []string `json:"allowed_providers"`
	FilteredProviders []string `json:"filtered_out"`
	Enforced          bool     `json:"enforced"`
}

// Apply runs geo-routing on a list of candidate providers for a given client IP.
func (gr *GeoRouter) Apply(clientIP string, candidates []string) GeoRoutingDecision {
	region := gr.ResolveRegion(clientIP)
	allowed := gr.FilterProviders(candidates, region)

	// Build filtered-out list
	allowedSet := make(map[string]bool)
	if allowed != nil {
		for _, p := range allowed {
			allowedSet[p] = true
		}
	}
	filtered := make([]string, 0)
	for _, c := range candidates {
		if !allowedSet[c] {
			filtered = append(filtered, c)
		}
	}

	return GeoRoutingDecision{
		ClientIP:          clientIP,
		ResolvedRegion:    region,
		AllowedProviders:  allowed,
		FilteredProviders: filtered,
		Enforced:          gr.cfg.EnforceDataResidency,
	}
}
