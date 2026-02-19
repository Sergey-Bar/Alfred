// Package alfred provides a Go client for the Alfred AI Credit Governance API.
//
// [AI GENERATED - GOVERNANCE PROTOCOL]
// ──────────────────────────────────────────────────────────────
// Model:       Claude Opus 4.6
// Tier:        L2
// Logic:       Go SDK with typed methods for all Alfred API endpoints.
// Root Cause:  Sprint task T186 — Go SDK implementation.
// Context:     Provides Go developers with native SDK for Alfred.
// Suitability: L2 — Standard HTTP client patterns with Go idioms.
// ──────────────────────────────────────────────────────────────
package alfred

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"time"
)

// Version is the SDK version.
const Version = "1.0.0"

// DefaultBaseURL is the default Alfred API base URL.
const DefaultBaseURL = "http://localhost:8000"

// ============================================================
// Client
// ============================================================

// Client is the Alfred API client.
type Client struct {
	baseURL    string
	apiKey     string
	httpClient *http.Client
	userAgent  string
}

// ClientOption configures the client.
type ClientOption func(*Client)

// WithBaseURL sets a custom base URL.
func WithBaseURL(url string) ClientOption {
	return func(c *Client) {
		c.baseURL = url
	}
}

// WithHTTPClient sets a custom HTTP client.
func WithHTTPClient(client *http.Client) ClientOption {
	return func(c *Client) {
		c.httpClient = client
	}
}

// WithTimeout sets request timeout.
func WithTimeout(timeout time.Duration) ClientOption {
	return func(c *Client) {
		c.httpClient.Timeout = timeout
	}
}

// NewClient creates a new Alfred API client.
func NewClient(apiKey string, opts ...ClientOption) *Client {
	c := &Client{
		baseURL:   DefaultBaseURL,
		apiKey:    apiKey,
		userAgent: fmt.Sprintf("alfred-go-sdk/%s", Version),
		httpClient: &http.Client{
			Timeout: 30 * time.Second,
		},
	}

	for _, opt := range opts {
		opt(c)
	}

	return c
}

// request performs an HTTP request.
func (c *Client) request(ctx context.Context, method, path string, body interface{}, result interface{}) error {
	var bodyReader io.Reader
	if body != nil {
		jsonBody, err := json.Marshal(body)
		if err != nil {
			return fmt.Errorf("marshal body: %w", err)
		}
		bodyReader = bytes.NewReader(jsonBody)
	}

	req, err := http.NewRequestWithContext(ctx, method, c.baseURL+path, bodyReader)
	if err != nil {
		return fmt.Errorf("create request: %w", err)
	}

	req.Header.Set("Authorization", "Bearer "+c.apiKey)
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("User-Agent", c.userAgent)

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return fmt.Errorf("do request: %w", err)
	}
	defer resp.Body.Close()

	// Read response body
	respBody, err := io.ReadAll(resp.Body)
	if err != nil {
		return fmt.Errorf("read response: %w", err)
	}

	// Handle errors
	if resp.StatusCode >= 400 {
		return parseError(resp.StatusCode, respBody)
	}

	// Parse result
	if result != nil && len(respBody) > 0 {
		if err := json.Unmarshal(respBody, result); err != nil {
			return fmt.Errorf("unmarshal response: %w", err)
		}
	}

	return nil
}

// ============================================================
// Error Types
// ============================================================

// Error represents an API error.
type Error struct {
	StatusCode int    `json:"status_code"`
	Message    string `json:"message"`
	Code       string `json:"code,omitempty"`
}

func (e *Error) Error() string {
	return fmt.Sprintf("alfred: %s (status %d)", e.Message, e.StatusCode)
}

// AuthenticationError indicates invalid credentials.
type AuthenticationError struct{ Error }

// AuthorizationError indicates insufficient permissions.
type AuthorizationError struct{ Error }

// NotFoundError indicates resource not found.
type NotFoundError struct{ Error }

// ValidationError indicates invalid request.
type ValidationError struct{ Error }

// QuotaExceededError indicates credit limit reached.
type QuotaExceededError struct{ Error }

// RateLimitError indicates too many requests.
type RateLimitError struct{ Error }

func parseError(statusCode int, body []byte) error {
	var apiErr struct {
		Detail string `json:"detail"`
		Code   string `json:"code"`
	}
	_ = json.Unmarshal(body, &apiErr)

	baseErr := Error{
		StatusCode: statusCode,
		Message:    apiErr.Detail,
		Code:       apiErr.Code,
	}

	if baseErr.Message == "" {
		baseErr.Message = http.StatusText(statusCode)
	}

	switch statusCode {
	case 401:
		return &AuthenticationError{Error: baseErr}
	case 403:
		return &AuthorizationError{Error: baseErr}
	case 404:
		return &NotFoundError{Error: baseErr}
	case 422:
		return &ValidationError{Error: baseErr}
	case 429:
		if apiErr.Code == "quota_exceeded" {
			return &QuotaExceededError{Error: baseErr}
		}
		return &RateLimitError{Error: baseErr}
	default:
		return &baseErr
	}
}

// ============================================================
// Models
// ============================================================

// User represents a user.
type User struct {
	ID        string     `json:"id"`
	Email     string     `json:"email"`
	Name      string     `json:"name"`
	Role      string     `json:"role"`
	TeamID    *string    `json:"team_id,omitempty"`
	CreatedAt time.Time  `json:"created_at"`
	UpdatedAt *time.Time `json:"updated_at,omitempty"`
}

// Team represents a team.
type Team struct {
	ID          string     `json:"id"`
	Name        string     `json:"name"`
	Description string     `json:"description,omitempty"`
	CreatedAt   time.Time  `json:"created_at"`
	UpdatedAt   *time.Time `json:"updated_at,omitempty"`
}

// Wallet represents a credit wallet.
type Wallet struct {
	ID        string     `json:"id"`
	OwnerID   string     `json:"owner_id"`
	OwnerType string     `json:"owner_type"`
	Balance   float64    `json:"balance"`
	SoftLimit float64    `json:"soft_limit"`
	HardLimit float64    `json:"hard_limit"`
	Currency  string     `json:"currency"`
	CreatedAt time.Time  `json:"created_at"`
	UpdatedAt *time.Time `json:"updated_at,omitempty"`
}

// Transaction represents a ledger transaction.
type Transaction struct {
	ID          string    `json:"id"`
	WalletID    string    `json:"wallet_id"`
	Type        string    `json:"type"`
	Amount      float64   `json:"amount"`
	Balance     float64   `json:"balance"`
	Description string    `json:"description,omitempty"`
	Metadata    JSONMap   `json:"metadata,omitempty"`
	CreatedAt   time.Time `json:"created_at"`
}

// Transfer represents a credit transfer.
type Transfer struct {
	ID              string     `json:"id"`
	FromWalletID    string     `json:"from_wallet_id"`
	ToWalletID      string     `json:"to_wallet_id"`
	Amount          float64    `json:"amount"`
	Status          string     `json:"status"`
	RequireApproval bool       `json:"require_approval"`
	ApprovedBy      *string    `json:"approved_by,omitempty"`
	ApprovedAt      *time.Time `json:"approved_at,omitempty"`
	CreatedAt       time.Time  `json:"created_at"`
}

// APIKey represents an API key.
type APIKey struct {
	ID        string     `json:"id"`
	Name      string     `json:"name"`
	Prefix    string     `json:"prefix"`
	UserID    string     `json:"user_id"`
	Scopes    []string   `json:"scopes"`
	ExpiresAt *time.Time `json:"expires_at,omitempty"`
	CreatedAt time.Time  `json:"created_at"`
	LastUsed  *time.Time `json:"last_used,omitempty"`
}

// APIKeyWithSecret includes the full key (only on creation).
type APIKeyWithSecret struct {
	APIKey
	Key string `json:"key"`
}

// Provider represents an LLM provider.
type Provider struct {
	ID        string  `json:"id"`
	Name      string  `json:"name"`
	BaseURL   string  `json:"base_url"`
	Status    string  `json:"status"`
	Latency   float64 `json:"latency_ms,omitempty"`
	ErrorRate float64 `json:"error_rate,omitempty"`
}

// Policy represents a governance policy.
type Policy struct {
	ID          string    `json:"id"`
	Name        string    `json:"name"`
	Description string    `json:"description,omitempty"`
	Rules       []string  `json:"rules"`
	Priority    int       `json:"priority"`
	Enabled     bool      `json:"enabled"`
	CreatedAt   time.Time `json:"created_at"`
}

// Experiment represents an A/B routing experiment.
type Experiment struct {
	ID           string                 `json:"id"`
	Name         string                 `json:"name"`
	Description  string                 `json:"description,omitempty"`
	Status       string                 `json:"status"`
	TrafficSplit map[string]int         `json:"traffic_split"`
	Metrics      map[string]interface{} `json:"metrics,omitempty"`
	StartedAt    *time.Time             `json:"started_at,omitempty"`
	EndedAt      *time.Time             `json:"ended_at,omitempty"`
	CreatedAt    time.Time              `json:"created_at"`
}

// UsageReport contains usage analytics.
type UsageReport struct {
	TotalRequests int                   `json:"total_requests"`
	TotalTokens   int                   `json:"total_tokens"`
	TotalCost     float64               `json:"total_cost"`
	ByModel       map[string]ModelUsage `json:"by_model,omitempty"`
	ByProvider    map[string]float64    `json:"by_provider,omitempty"`
	Period        string                `json:"period"`
	StartDate     time.Time             `json:"start_date"`
	EndDate       time.Time             `json:"end_date"`
}

// ModelUsage contains per-model usage.
type ModelUsage struct {
	Requests int     `json:"requests"`
	Tokens   int     `json:"tokens"`
	Cost     float64 `json:"cost"`
}

// JSONMap is a generic JSON object.
type JSONMap map[string]interface{}

// ============================================================
// Chat Completion
// ============================================================

// Message represents a chat message.
type Message struct {
	Role      string      `json:"role"`
	Content   interface{} `json:"content"`
	Name      string      `json:"name,omitempty"`
	ToolCalls []ToolCall  `json:"tool_calls,omitempty"`
}

// ToolCall represents a tool usage.
type ToolCall struct {
	ID       string       `json:"id"`
	Type     string       `json:"type"`
	Function FunctionCall `json:"function"`
}

// FunctionCall represents a function call.
type FunctionCall struct {
	Name      string `json:"name"`
	Arguments string `json:"arguments"`
}

// Tool represents an available tool.
type Tool struct {
	Type     string       `json:"type"`
	Function ToolFunction `json:"function"`
}

// ToolFunction describes a tool function.
type ToolFunction struct {
	Name        string  `json:"name"`
	Description string  `json:"description,omitempty"`
	Parameters  JSONMap `json:"parameters,omitempty"`
}

// CompletionRequest is a chat completion request.
type CompletionRequest struct {
	Model            string    `json:"model"`
	Messages         []Message `json:"messages"`
	MaxTokens        int       `json:"max_tokens,omitempty"`
	Temperature      float64   `json:"temperature,omitempty"`
	TopP             float64   `json:"top_p,omitempty"`
	Stop             []string  `json:"stop,omitempty"`
	Stream           bool      `json:"stream,omitempty"`
	Tools            []Tool    `json:"tools,omitempty"`
	ToolChoice       string    `json:"tool_choice,omitempty"`
	FrequencyPenalty float64   `json:"frequency_penalty,omitempty"`
	PresencePenalty  float64   `json:"presence_penalty,omitempty"`
}

// CompletionResponse is a chat completion response.
type CompletionResponse struct {
	ID      string   `json:"id"`
	Object  string   `json:"object"`
	Created int64    `json:"created"`
	Model   string   `json:"model"`
	Choices []Choice `json:"choices"`
	Usage   Usage    `json:"usage"`
}

// Choice represents a completion choice.
type Choice struct {
	Index        int     `json:"index"`
	Message      Message `json:"message"`
	FinishReason string  `json:"finish_reason"`
}

// Usage contains token usage.
type Usage struct {
	PromptTokens     int `json:"prompt_tokens"`
	CompletionTokens int `json:"completion_tokens"`
	TotalTokens      int `json:"total_tokens"`
}

// ============================================================
// User Methods
// ============================================================

// GetCurrentUser returns the authenticated user.
func (c *Client) GetCurrentUser(ctx context.Context) (*User, error) {
	var user User
	if err := c.request(ctx, "GET", "/v1/users/me", nil, &user); err != nil {
		return nil, err
	}
	return &user, nil
}

// GetUser returns a user by ID.
func (c *Client) GetUser(ctx context.Context, id string) (*User, error) {
	var user User
	if err := c.request(ctx, "GET", "/v1/users/"+id, nil, &user); err != nil {
		return nil, err
	}
	return &user, nil
}

// ListUsers returns all users.
func (c *Client) ListUsers(ctx context.Context, limit, offset int) ([]User, error) {
	path := fmt.Sprintf("/v1/users?limit=%d&offset=%d", limit, offset)
	var users []User
	if err := c.request(ctx, "GET", path, nil, &users); err != nil {
		return nil, err
	}
	return users, nil
}

// ============================================================
// Team Methods
// ============================================================

// ListTeams returns all teams.
func (c *Client) ListTeams(ctx context.Context) ([]Team, error) {
	var teams []Team
	if err := c.request(ctx, "GET", "/v1/teams", nil, &teams); err != nil {
		return nil, err
	}
	return teams, nil
}

// GetTeam returns a team by ID.
func (c *Client) GetTeam(ctx context.Context, id string) (*Team, error) {
	var team Team
	if err := c.request(ctx, "GET", "/v1/teams/"+id, nil, &team); err != nil {
		return nil, err
	}
	return &team, nil
}

// CreateTeamRequest is the request to create a team.
type CreateTeamRequest struct {
	Name        string `json:"name"`
	Description string `json:"description,omitempty"`
}

// CreateTeam creates a new team.
func (c *Client) CreateTeam(ctx context.Context, req *CreateTeamRequest) (*Team, error) {
	var team Team
	if err := c.request(ctx, "POST", "/v1/teams", req, &team); err != nil {
		return nil, err
	}
	return &team, nil
}

// ============================================================
// Wallet Methods
// ============================================================

// GetCurrentWallet returns the authenticated user's wallet.
func (c *Client) GetCurrentWallet(ctx context.Context) (*Wallet, error) {
	var wallet Wallet
	if err := c.request(ctx, "GET", "/v1/wallets/me", nil, &wallet); err != nil {
		return nil, err
	}
	return &wallet, nil
}

// GetWallet returns a wallet by ID.
func (c *Client) GetWallet(ctx context.Context, id string) (*Wallet, error) {
	var wallet Wallet
	if err := c.request(ctx, "GET", "/v1/wallets/"+id, nil, &wallet); err != nil {
		return nil, err
	}
	return &wallet, nil
}

// GetWalletTransactions returns wallet transactions.
func (c *Client) GetWalletTransactions(ctx context.Context, walletID string, limit, offset int) ([]Transaction, error) {
	path := fmt.Sprintf("/v1/wallets/%s/transactions?limit=%d&offset=%d", walletID, limit, offset)
	var transactions []Transaction
	if err := c.request(ctx, "GET", path, nil, &transactions); err != nil {
		return nil, err
	}
	return transactions, nil
}

// UpdateWalletRequest is the request to update wallet limits.
type UpdateWalletRequest struct {
	SoftLimit float64 `json:"soft_limit,omitempty"`
	HardLimit float64 `json:"hard_limit,omitempty"`
}

// UpdateWallet updates wallet settings.
func (c *Client) UpdateWallet(ctx context.Context, id string, req *UpdateWalletRequest) (*Wallet, error) {
	var wallet Wallet
	if err := c.request(ctx, "PATCH", "/v1/wallets/"+id, req, &wallet); err != nil {
		return nil, err
	}
	return &wallet, nil
}

// ============================================================
// Transfer Methods
// ============================================================

// CreateTransferRequest is the request to create a transfer.
type CreateTransferRequest struct {
	ToWalletID      string  `json:"to_wallet_id"`
	Amount          float64 `json:"amount"`
	Reason          string  `json:"reason,omitempty"`
	RequireApproval bool    `json:"require_approval,omitempty"`
}

// CreateTransfer creates a credit transfer.
func (c *Client) CreateTransfer(ctx context.Context, req *CreateTransferRequest) (*Transfer, error) {
	var transfer Transfer
	if err := c.request(ctx, "POST", "/v1/transfers", req, &transfer); err != nil {
		return nil, err
	}
	return &transfer, nil
}

// GetTransfer returns a transfer by ID.
func (c *Client) GetTransfer(ctx context.Context, id string) (*Transfer, error) {
	var transfer Transfer
	if err := c.request(ctx, "GET", "/v1/transfers/"+id, nil, &transfer); err != nil {
		return nil, err
	}
	return &transfer, nil
}

// ListTransfers returns transfers.
func (c *Client) ListTransfers(ctx context.Context, status string, limit, offset int) ([]Transfer, error) {
	path := fmt.Sprintf("/v1/transfers?limit=%d&offset=%d", limit, offset)
	if status != "" {
		path += "&status=" + url.QueryEscape(status)
	}
	var transfers []Transfer
	if err := c.request(ctx, "GET", path, nil, &transfers); err != nil {
		return nil, err
	}
	return transfers, nil
}

// ApproveTransfer approves a pending transfer.
func (c *Client) ApproveTransfer(ctx context.Context, id string) (*Transfer, error) {
	var transfer Transfer
	if err := c.request(ctx, "POST", "/v1/transfers/"+id+"/approve", nil, &transfer); err != nil {
		return nil, err
	}
	return &transfer, nil
}

// RejectTransfer rejects a pending transfer.
func (c *Client) RejectTransfer(ctx context.Context, id string, reason string) (*Transfer, error) {
	body := map[string]string{"reason": reason}
	var transfer Transfer
	if err := c.request(ctx, "POST", "/v1/transfers/"+id+"/reject", body, &transfer); err != nil {
		return nil, err
	}
	return &transfer, nil
}

// ============================================================
// API Key Methods
// ============================================================

// ListAPIKeys returns the user's API keys.
func (c *Client) ListAPIKeys(ctx context.Context) ([]APIKey, error) {
	var keys []APIKey
	if err := c.request(ctx, "GET", "/v1/api-keys", nil, &keys); err != nil {
		return nil, err
	}
	return keys, nil
}

// CreateAPIKeyRequest is the request to create an API key.
type CreateAPIKeyRequest struct {
	Name      string     `json:"name"`
	Scopes    []string   `json:"scopes,omitempty"`
	ExpiresAt *time.Time `json:"expires_at,omitempty"`
}

// CreateAPIKey creates a new API key.
func (c *Client) CreateAPIKey(ctx context.Context, req *CreateAPIKeyRequest) (*APIKeyWithSecret, error) {
	var key APIKeyWithSecret
	if err := c.request(ctx, "POST", "/v1/api-keys", req, &key); err != nil {
		return nil, err
	}
	return &key, nil
}

// RevokeAPIKey revokes an API key.
func (c *Client) RevokeAPIKey(ctx context.Context, id string) error {
	return c.request(ctx, "DELETE", "/v1/api-keys/"+id, nil, nil)
}

// ============================================================
// Provider Methods
// ============================================================

// ListProviders returns available providers.
func (c *Client) ListProviders(ctx context.Context) ([]Provider, error) {
	var providers []Provider
	if err := c.request(ctx, "GET", "/v1/providers", nil, &providers); err != nil {
		return nil, err
	}
	return providers, nil
}

// GetProvider returns a provider by ID.
func (c *Client) GetProvider(ctx context.Context, id string) (*Provider, error) {
	var provider Provider
	if err := c.request(ctx, "GET", "/v1/providers/"+id, nil, &provider); err != nil {
		return nil, err
	}
	return &provider, nil
}

// ============================================================
// Policy Methods
// ============================================================

// ListPolicies returns governance policies.
func (c *Client) ListPolicies(ctx context.Context) ([]Policy, error) {
	var policies []Policy
	if err := c.request(ctx, "GET", "/v1/policies", nil, &policies); err != nil {
		return nil, err
	}
	return policies, nil
}

// GetPolicy returns a policy by ID.
func (c *Client) GetPolicy(ctx context.Context, id string) (*Policy, error) {
	var policy Policy
	if err := c.request(ctx, "GET", "/v1/policies/"+id, nil, &policy); err != nil {
		return nil, err
	}
	return &policy, nil
}

// CreatePolicyRequest is the request to create a policy.
type CreatePolicyRequest struct {
	Name        string   `json:"name"`
	Description string   `json:"description,omitempty"`
	Rules       []string `json:"rules"`
	Priority    int      `json:"priority,omitempty"`
	Enabled     bool     `json:"enabled"`
}

// CreatePolicy creates a new policy.
func (c *Client) CreatePolicy(ctx context.Context, req *CreatePolicyRequest) (*Policy, error) {
	var policy Policy
	if err := c.request(ctx, "POST", "/v1/policies", req, &policy); err != nil {
		return nil, err
	}
	return &policy, nil
}

// ============================================================
// Experiment Methods
// ============================================================

// ListExperiments returns routing experiments.
func (c *Client) ListExperiments(ctx context.Context) ([]Experiment, error) {
	var experiments []Experiment
	if err := c.request(ctx, "GET", "/v1/experiments", nil, &experiments); err != nil {
		return nil, err
	}
	return experiments, nil
}

// GetExperiment returns an experiment by ID.
func (c *Client) GetExperiment(ctx context.Context, id string) (*Experiment, error) {
	var experiment Experiment
	if err := c.request(ctx, "GET", "/v1/experiments/"+id, nil, &experiment); err != nil {
		return nil, err
	}
	return &experiment, nil
}

// CreateExperimentRequest is the request to create an experiment.
type CreateExperimentRequest struct {
	Name         string         `json:"name"`
	Description  string         `json:"description,omitempty"`
	TrafficSplit map[string]int `json:"traffic_split"`
}

// CreateExperiment creates a new experiment.
func (c *Client) CreateExperiment(ctx context.Context, req *CreateExperimentRequest) (*Experiment, error) {
	var experiment Experiment
	if err := c.request(ctx, "POST", "/v1/experiments", req, &experiment); err != nil {
		return nil, err
	}
	return &experiment, nil
}

// StartExperiment starts an experiment.
func (c *Client) StartExperiment(ctx context.Context, id string) (*Experiment, error) {
	var experiment Experiment
	if err := c.request(ctx, "POST", "/v1/experiments/"+id+"/start", nil, &experiment); err != nil {
		return nil, err
	}
	return &experiment, nil
}

// StopExperiment stops an experiment.
func (c *Client) StopExperiment(ctx context.Context, id string) (*Experiment, error) {
	var experiment Experiment
	if err := c.request(ctx, "POST", "/v1/experiments/"+id+"/stop", nil, &experiment); err != nil {
		return nil, err
	}
	return &experiment, nil
}

// ============================================================
// Analytics Methods
// ============================================================

// GetUsageReport returns usage analytics.
func (c *Client) GetUsageReport(ctx context.Context, startDate, endDate time.Time) (*UsageReport, error) {
	path := fmt.Sprintf(
		"/v1/analytics/usage?start_date=%s&end_date=%s",
		startDate.Format("2006-01-02"),
		endDate.Format("2006-01-02"),
	)
	var report UsageReport
	if err := c.request(ctx, "GET", path, nil, &report); err != nil {
		return nil, err
	}
	return &report, nil
}

// GetCostBreakdown returns cost breakdown by dimension.
type CostBreakdown struct {
	ByModel    map[string]float64 `json:"by_model"`
	ByProvider map[string]float64 `json:"by_provider"`
	ByTeam     map[string]float64 `json:"by_team"`
	Total      float64            `json:"total"`
}

// GetCostBreakdown returns cost analytics.
func (c *Client) GetCostBreakdown(ctx context.Context, startDate, endDate time.Time) (*CostBreakdown, error) {
	path := fmt.Sprintf(
		"/v1/analytics/costs?start_date=%s&end_date=%s",
		startDate.Format("2006-01-02"),
		endDate.Format("2006-01-02"),
	)
	var breakdown CostBreakdown
	if err := c.request(ctx, "GET", path, nil, &breakdown); err != nil {
		return nil, err
	}
	return &breakdown, nil
}

// ============================================================
// Chat Completion Methods
// ============================================================

// ChatCompletion creates a chat completion.
func (c *Client) ChatCompletion(ctx context.Context, req *CompletionRequest) (*CompletionResponse, error) {
	var resp CompletionResponse
	if err := c.request(ctx, "POST", "/v1/chat/completions", req, &resp); err != nil {
		return nil, err
	}
	return &resp, nil
}

// QuickChat sends a simple message and returns the response.
func (c *Client) QuickChat(ctx context.Context, model, prompt string) (string, error) {
	req := &CompletionRequest{
		Model: model,
		Messages: []Message{
			{Role: "user", Content: prompt},
		},
	}

	resp, err := c.ChatCompletion(ctx, req)
	if err != nil {
		return "", err
	}

	if len(resp.Choices) == 0 {
		return "", fmt.Errorf("no choices in response")
	}

	content, ok := resp.Choices[0].Message.Content.(string)
	if !ok {
		return "", fmt.Errorf("unexpected content type")
	}

	return content, nil
}

// ============================================================
// Health Check
// ============================================================

// Health represents service health.
type Health struct {
	Status    string            `json:"status"`
	Version   string            `json:"version"`
	Providers map[string]string `json:"providers,omitempty"`
}

// HealthCheck checks service health.
func (c *Client) HealthCheck(ctx context.Context) (*Health, error) {
	var health Health
	if err := c.request(ctx, "GET", "/health", nil, &health); err != nil {
		return nil, err
	}
	return &health, nil
}
