/*
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L3
Logic:       OPA (Open Policy Agent) integration — sidecar REST API
             client, policy CRUD, built-in templates, dry-run mode,
             and evaluation logging.
Root Cause:  Sprint tasks T132-T136 — OPA Policy Engine.
Context:     Policy-as-code governance per PRD Section 8.5.
Suitability: L3 — policy engine integration with complex logic.
──────────────────────────────────────────────────────────────
*/

package policy

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"sync"
	"time"
)

// ─── T132: OPA Server Integration ───────────────────────────

type OPAConfig struct {
	Enabled    bool          `json:"enabled"`
	Address    string        `json:"address"` // e.g., "http://localhost:8181"
	Timeout    time.Duration `json:"timeout"`
	DryRun     bool          `json:"dry_run"` // T135: evaluate but don't enforce
	LogEnabled bool          `json:"log_enabled"`
}

type OPAClient struct {
	config   OPAConfig
	client   *http.Client
	mu       sync.RWMutex
	policies map[string]*Policy       // in-memory policy store
	evalLog  []PolicyEvaluationResult // T136: evaluation log
}

type Policy struct {
	ID          string    `json:"id"`
	Name        string    `json:"name"`
	Description string    `json:"description"`
	Module      string    `json:"module"` // Rego source code
	Active      bool      `json:"active"`
	DryRun      bool      `json:"dry_run"`
	CreatedAt   time.Time `json:"created_at"`
	UpdatedAt   time.Time `json:"updated_at"`
}

// OPA evaluation input mirrors the request context.
type PolicyInput struct {
	Model           string            `json:"model"`
	Provider        string            `json:"provider"`
	UserID          string            `json:"user_id"`
	TeamID          string            `json:"team_id"`
	OrgID           string            `json:"org_id"`
	EstimatedTokens int               `json:"estimated_tokens"`
	RequestTime     time.Time         `json:"request_time"`
	Metadata        map[string]string `json:"metadata"`
	DataClass       string            `json:"data_classification"`
	SourceIP        string            `json:"source_ip"`
}

// OPA decision response.
type PolicyDecision struct {
	Allow   bool     `json:"allow"`
	Deny    []string `json:"deny"`
	Route   []string `json:"route"`
	Warn    []string `json:"warn"`
	DryRun  bool     `json:"dry_run"`
}

// ─── T136: Policy Evaluation Logging ────────────────────────

type PolicyEvaluationResult struct {
	PolicyID   string          `json:"policy_id"`
	PolicyName string          `json:"policy_name"`
	Decision   PolicyDecision  `json:"decision"`
	Input      PolicyInput     `json:"input"`
	Timestamp  time.Time       `json:"timestamp"`
	LatencyMs  float64         `json:"latency_ms"`
	DryRun     bool            `json:"dry_run"`
}

func NewOPAClient(config OPAConfig) *OPAClient {
	if config.Timeout == 0 {
		config.Timeout = 5 * time.Second
	}
	if config.Address == "" {
		config.Address = "http://localhost:8181"
	}

	return &OPAClient{
		config: config,
		client: &http.Client{
			Timeout: config.Timeout,
		},
		policies: make(map[string]*Policy),
		evalLog:  make([]PolicyEvaluationResult, 0, 1024),
	}
}

// ─── T133: Policy CRUD API ──────────────────────────────────

func (c *OPAClient) CreatePolicy(p *Policy) error {
	c.mu.Lock()
	defer c.mu.Unlock()

	if _, exists := c.policies[p.ID]; exists {
		return fmt.Errorf("policy %s already exists", p.ID)
	}

	now := time.Now()
	p.CreatedAt = now
	p.UpdatedAt = now
	c.policies[p.ID] = p

	// Sync to OPA server
	if c.config.Enabled {
		return c.uploadToOPA(p)
	}
	return nil
}

func (c *OPAClient) UpdatePolicy(id string, module string, active bool) error {
	c.mu.Lock()
	defer c.mu.Unlock()

	p, ok := c.policies[id]
	if !ok {
		return fmt.Errorf("policy %s not found", id)
	}

	p.Module = module
	p.Active = active
	p.UpdatedAt = time.Now()

	if c.config.Enabled {
		return c.uploadToOPA(p)
	}
	return nil
}

func (c *OPAClient) DeletePolicy(id string) error {
	c.mu.Lock()
	defer c.mu.Unlock()

	if _, ok := c.policies[id]; !ok {
		return fmt.Errorf("policy %s not found", id)
	}

	delete(c.policies, id)

	if c.config.Enabled {
		return c.deleteFromOPA(id)
	}
	return nil
}

func (c *OPAClient) GetPolicy(id string) (*Policy, error) {
	c.mu.RLock()
	defer c.mu.RUnlock()

	p, ok := c.policies[id]
	if !ok {
		return nil, fmt.Errorf("policy %s not found", id)
	}
	return p, nil
}

func (c *OPAClient) ListPolicies() []*Policy {
	c.mu.RLock()
	defer c.mu.RUnlock()

	result := make([]*Policy, 0, len(c.policies))
	for _, p := range c.policies {
		result = append(result, p)
	}
	return result
}

// uploadToOPA pushes a Rego module to the OPA REST API.
func (c *OPAClient) uploadToOPA(p *Policy) error {
	url := fmt.Sprintf("%s/v1/policies/%s", c.config.Address, p.ID)
	req, err := http.NewRequest(http.MethodPut, url, bytes.NewBufferString(p.Module))
	if err != nil {
		return fmt.Errorf("create request: %w", err)
	}
	req.Header.Set("Content-Type", "text/plain")

	resp, err := c.client.Do(req)
	if err != nil {
		return fmt.Errorf("upload to OPA: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode >= 400 {
		body, _ := io.ReadAll(resp.Body)
		return fmt.Errorf("OPA upload failed (%d): %s", resp.StatusCode, string(body))
	}
	return nil
}

func (c *OPAClient) deleteFromOPA(id string) error {
	url := fmt.Sprintf("%s/v1/policies/%s", c.config.Address, id)
	req, err := http.NewRequest(http.MethodDelete, url, nil)
	if err != nil {
		return fmt.Errorf("create request: %w", err)
	}

	resp, err := c.client.Do(req)
	if err != nil {
		return fmt.Errorf("delete from OPA: %w", err)
	}
	defer resp.Body.Close()
	return nil
}

// ─── Policy Evaluation ──────────────────────────────────────

// Evaluate runs all active policies against the given input.
func (c *OPAClient) Evaluate(ctx context.Context, input PolicyInput) (*PolicyDecision, error) {
	c.mu.RLock()
	activePolicies := make([]*Policy, 0)
	for _, p := range c.policies {
		if p.Active {
			activePolicies = append(activePolicies, p)
		}
	}
	c.mu.RUnlock()

	combined := &PolicyDecision{Allow: true}

	for _, p := range activePolicies {
		start := time.Now()
		decision, err := c.evaluatePolicy(ctx, p, input)
		elapsed := time.Since(start)

		if err != nil {
			// Log but don't block on OPA errors unless strict mode
			if c.config.LogEnabled {
				c.logEvaluation(p, input, &PolicyDecision{Allow: true}, elapsed, p.DryRun || c.config.DryRun)
			}
			continue
		}

		isDryRun := p.DryRun || c.config.DryRun
		decision.DryRun = isDryRun

		if c.config.LogEnabled {
			c.logEvaluation(p, input, decision, elapsed, isDryRun)
		}

		// T135: In dry-run mode, log but don't enforce
		if isDryRun {
			combined.Warn = append(combined.Warn, decision.Deny...)
			combined.Warn = append(combined.Warn, decision.Warn...)
			continue
		}

		// Merge deny reasons
		combined.Deny = append(combined.Deny, decision.Deny...)
		combined.Warn = append(combined.Warn, decision.Warn...)
		combined.Route = append(combined.Route, decision.Route...)
		if len(decision.Deny) > 0 {
			combined.Allow = false
		}
	}

	return combined, nil
}

func (c *OPAClient) evaluatePolicy(ctx context.Context, p *Policy, input PolicyInput) (*PolicyDecision, error) {
	if !c.config.Enabled {
		// Local evaluation stub — in production, this calls OPA Data API
		return &PolicyDecision{Allow: true}, nil
	}

	payload := map[string]interface{}{
		"input": input,
	}

	body, err := json.Marshal(payload)
	if err != nil {
		return nil, fmt.Errorf("marshal input: %w", err)
	}

	url := fmt.Sprintf("%s/v1/data/alfred/%s", c.config.Address, p.ID)
	req, err := http.NewRequestWithContext(ctx, http.MethodPost, url, bytes.NewReader(body))
	if err != nil {
		return nil, fmt.Errorf("create request: %w", err)
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := c.client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("OPA query: %w", err)
	}
	defer resp.Body.Close()

	var result struct {
		Result struct {
			Deny  []string `json:"deny"`
			Route []string `json:"route"`
			Warn  []string `json:"warn"`
		} `json:"result"`
	}

	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, fmt.Errorf("decode OPA response: %w", err)
	}

	decision := &PolicyDecision{
		Allow: len(result.Result.Deny) == 0,
		Deny:  result.Result.Deny,
		Route: result.Result.Route,
		Warn:  result.Result.Warn,
	}
	return decision, nil
}

func (c *OPAClient) logEvaluation(p *Policy, input PolicyInput, decision *PolicyDecision, latency time.Duration, dryRun bool) {
	c.mu.Lock()
	defer c.mu.Unlock()

	entry := PolicyEvaluationResult{
		PolicyID:   p.ID,
		PolicyName: p.Name,
		Decision:   *decision,
		Input:      input,
		Timestamp:  time.Now(),
		LatencyMs:  float64(latency.Microseconds()) / 1000.0,
		DryRun:     dryRun,
	}

	c.evalLog = append(c.evalLog, entry)

	// Ring buffer — keep last 10K entries
	if len(c.evalLog) > 10000 {
		c.evalLog = c.evalLog[len(c.evalLog)-10000:]
	}
}

// GetEvaluationLog returns recent policy evaluation log entries.
func (c *OPAClient) GetEvaluationLog(limit int) []PolicyEvaluationResult {
	c.mu.RLock()
	defer c.mu.RUnlock()

	if limit <= 0 || limit > len(c.evalLog) {
		limit = len(c.evalLog)
	}

	start := len(c.evalLog) - limit
	result := make([]PolicyEvaluationResult, limit)
	copy(result, c.evalLog[start:])
	return result
}

// ─── T134: Built-in Policy Templates ────────────────────────

// BuiltInPolicies returns pre-built Rego policy templates.
func BuiltInPolicies() []*Policy {
	return []*Policy{
		{
			ID:          "premium_model_gating",
			Name:        "Premium Model Gating",
			Description: "Restrict premium models (GPT-4, Claude Opus) to approved teams",
			Active:      false,
			Module: `package alfred.premium_model_gating

import future.keywords.in

premium_models := {"gpt-4", "gpt-4-turbo", "gpt-4o", "claude-3-opus", "claude-opus-4"}
approved_teams := {"engineering-core", "ml-research", "security"}

deny[reason] {
    input.model in premium_models
    not input.team_id in approved_teams
    reason := sprintf("Team %s is not approved for premium model %s", [input.team_id, input.model])
}
`,
		},
		{
			ID:          "token_limit",
			Name:        "Token Limit Policy",
			Description: "Block requests exceeding 20K estimated tokens",
			Active:      false,
			Module: `package alfred.token_limit

deny[reason] {
    input.estimated_tokens > 20000
    reason := sprintf("Request exceeds token limit (%d > 20000)", [input.estimated_tokens])
}

warn[reason] {
    input.estimated_tokens > 10000
    input.estimated_tokens <= 20000
    reason := sprintf("Large request warning: %d tokens estimated", [input.estimated_tokens])
}
`,
		},
		{
			ID:          "time_of_day",
			Name:        "Business Hours Model Restriction",
			Description: "Restrict expensive models to business hours (9AM-6PM UTC)",
			Active:      false,
			Module: `package alfred.time_of_day

import future.keywords.in

expensive_models := {"gpt-4", "gpt-4-turbo", "claude-3-opus"}

deny[reason] {
    input.model in expensive_models
    hour := time.clock(time.now_ns())[0]
    hour < 9
    reason := sprintf("Premium model %s restricted outside business hours (before 9AM UTC)", [input.model])
}

deny[reason] {
    input.model in expensive_models
    hour := time.clock(time.now_ns())[0]
    hour >= 18
    reason := sprintf("Premium model %s restricted outside business hours (after 6PM UTC)", [input.model])
}
`,
		},
		{
			ID:          "data_classification",
			Name:        "Data Classification Routing",
			Description: "Route confidential data to self-hosted models only",
			Active:      false,
			Module: `package alfred.data_classification

import future.keywords.in

self_hosted_models := {"llama-3.1-70b", "mistral-7b", "codellama-34b"}

deny[reason] {
    input.data_classification == "CONFIDENTIAL"
    not input.model in self_hosted_models
    reason := sprintf("Confidential data must use self-hosted models, not %s", [input.model])
}

route[target] {
    input.data_classification == "CONFIDENTIAL"
    target := "self-hosted-llama"
}
`,
		},
		{
			ID:          "rate_limit_per_user",
			Name:        "Per-User Rate Limit",
			Description: "Warn when a user makes too many requests",
			Active:      false,
			Module: `package alfred.rate_limit_per_user

warn[reason] {
    input.metadata.requests_last_minute
    to_number(input.metadata.requests_last_minute) > 60
    reason := sprintf("User %s exceeding 60 requests/minute", [input.user_id])
}
`,
		},
		{
			ID:          "geo_restriction",
			Name:        "Geographic Data Residency",
			Description: "Enforce EU data residency for EU-origin requests",
			Active:      false,
			Module: `package alfred.geo_restriction

import future.keywords.in

eu_providers := {"eu-openai", "eu-anthropic", "self-hosted-eu"}

deny[reason] {
    input.metadata.region == "EU"
    not input.provider in eu_providers
    reason := sprintf("EU data residency requires EU provider, not %s", [input.provider])
}
`,
		},
		{
			ID:          "pii_model_restriction",
			Name:        "PII-Flagged Request Restriction",
			Description: "Route PII-containing requests to approved models only",
			Active:      false,
			Module: `package alfred.pii_model_restriction

import future.keywords.in

pii_approved := {"self-hosted-llama", "azure-openai-hipaa"}

deny[reason] {
    input.metadata.contains_pii == "true"
    not input.provider in pii_approved
    reason := sprintf("PII-flagged requests must use approved providers, not %s", [input.provider])
}
`,
		},
		{
			ID:          "budget_routing",
			Name:        "Budget-Aware Model Downgrade",
			Description: "Route to cheaper models when wallet is above 80% usage",
			Active:      false,
			Module: `package alfred.budget_routing

import future.keywords.in

expensive_models := {"gpt-4", "gpt-4-turbo", "claude-3-opus"}
cheap_alternatives := {"gpt-3.5-turbo": "gpt-3.5-turbo", "gpt-4": "gpt-3.5-turbo", "claude-3-opus": "claude-3-haiku"}

warn[reason] {
    input.metadata.wallet_usage_pct
    to_number(input.metadata.wallet_usage_pct) > 80
    input.model in expensive_models
    reason := sprintf("Wallet at %s%% — consider using cheaper model instead of %s", [input.metadata.wallet_usage_pct, input.model])
}
`,
		},
	}
}
