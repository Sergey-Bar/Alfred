/*
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L1
Logic:       Provider pricing configuration for cost calculation.
             Maps model names to input/output token rates in USD.
Root Cause:  Sprint task T029 — Provider pricing config.
Context:     Used by metering engine for cost estimation and by
             dry-run mode for pre-flight cost preview.
Suitability: L1 for static config data.
──────────────────────────────────────────────────────────────
*/

package provider

import (
	"encoding/json"
	"fmt"
	"math"
	"os"
	"strings"
	"sync"
)

// ModelPricing holds per-model token pricing in USD per 1M tokens.
type ModelPricing struct {
	InputPer1M  float64 `json:"input_per_1m"`
	OutputPer1M float64 `json:"output_per_1m"`
	Free        bool    `json:"free,omitempty"`
}

// PricingConfig holds all provider pricing data.
type PricingConfig struct {
	mu      sync.RWMutex
	pricing map[string]ModelPricing // key: "provider/model" or just "model"
}

// DefaultPricing returns the built-in pricing table (Feb 2026 rates).
func DefaultPricing() *PricingConfig {
	pc := &PricingConfig{
		pricing: map[string]ModelPricing{
			// OpenAI
			"openai/gpt-4o":            {InputPer1M: 2.50, OutputPer1M: 10.00},
			"openai/gpt-4o-mini":       {InputPer1M: 0.15, OutputPer1M: 0.60},
			"openai/gpt-4-turbo":       {InputPer1M: 10.00, OutputPer1M: 30.00},
			"openai/gpt-4":             {InputPer1M: 30.00, OutputPer1M: 60.00},
			"openai/gpt-3.5-turbo":     {InputPer1M: 0.50, OutputPer1M: 1.50},
			"openai/o1":                {InputPer1M: 15.00, OutputPer1M: 60.00},
			"openai/o1-mini":           {InputPer1M: 3.00, OutputPer1M: 12.00},
			"openai/text-embedding-3-small": {InputPer1M: 0.02, OutputPer1M: 0.0},
			"openai/text-embedding-3-large": {InputPer1M: 0.13, OutputPer1M: 0.0},

			// Anthropic
			"anthropic/claude-3-5-sonnet-20241022": {InputPer1M: 3.00, OutputPer1M: 15.00},
			"anthropic/claude-3-5-haiku-20241022":  {InputPer1M: 0.80, OutputPer1M: 4.00},
			"anthropic/claude-3-opus-20240229":     {InputPer1M: 15.00, OutputPer1M: 75.00},
			"anthropic/claude-3-sonnet-20240229":   {InputPer1M: 3.00, OutputPer1M: 15.00},
			"anthropic/claude-3-haiku-20240307":    {InputPer1M: 0.25, OutputPer1M: 1.25},

			// Google
			"google/gemini-2.0-flash":    {InputPer1M: 0.10, OutputPer1M: 0.40},
			"google/gemini-1.5-pro":      {InputPer1M: 1.25, OutputPer1M: 5.00},
			"google/gemini-1.5-flash":    {InputPer1M: 0.075, OutputPer1M: 0.30},
			"google/gemini-2.0-flash-lite": {InputPer1M: 0.0, OutputPer1M: 0.0, Free: true},

			// Azure OpenAI (same pricing as OpenAI)
			"azure/gpt-4o":         {InputPer1M: 2.50, OutputPer1M: 10.00},
			"azure/gpt-4o-mini":    {InputPer1M: 0.15, OutputPer1M: 0.60},
			"azure/gpt-4-turbo":    {InputPer1M: 10.00, OutputPer1M: 30.00},

			// Mistral
			"mistral/mistral-large-latest":  {InputPer1M: 2.00, OutputPer1M: 6.00},
			"mistral/mistral-small-latest":  {InputPer1M: 0.20, OutputPer1M: 0.60},
			"mistral/codestral-latest":      {InputPer1M: 0.30, OutputPer1M: 0.90},
			"mistral/mistral-embed":         {InputPer1M: 0.10, OutputPer1M: 0.0},

			// Groq (hosted inference)
			"groq/llama-3.1-70b-versatile": {InputPer1M: 0.59, OutputPer1M: 0.79},
			"groq/llama-3.1-8b-instant":    {InputPer1M: 0.05, OutputPer1M: 0.08},
			"groq/mixtral-8x7b-32768":      {InputPer1M: 0.24, OutputPer1M: 0.24},

			// Together AI
			"together/meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo": {InputPer1M: 0.88, OutputPer1M: 0.88},
			"together/meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo":  {InputPer1M: 0.18, OutputPer1M: 0.18},

			// Cohere
			"cohere/command-r-plus": {InputPer1M: 2.50, OutputPer1M: 10.00},
			"cohere/command-r":      {InputPer1M: 0.15, OutputPer1M: 0.60},
			"cohere/embed-english-v3.0": {InputPer1M: 0.10, OutputPer1M: 0.0},
		},
	}
	return pc
}

// LoadFromFile loads pricing overrides from a JSON file.
func (pc *PricingConfig) LoadFromFile(path string) error {
	data, err := os.ReadFile(path)
	if err != nil {
		return fmt.Errorf("read pricing file: %w", err)
	}

	var overrides map[string]ModelPricing
	if err := json.Unmarshal(data, &overrides); err != nil {
		return fmt.Errorf("parse pricing file: %w", err)
	}

	pc.mu.Lock()
	defer pc.mu.Unlock()
	for k, v := range overrides {
		pc.pricing[k] = v
	}
	return nil
}

// GetPricing returns the pricing for a model. Tries "provider/model" first,
// then falls back to just "model" across all providers.
func (pc *PricingConfig) GetPricing(providerName, model string) (ModelPricing, bool) {
	pc.mu.RLock()
	defer pc.mu.RUnlock()

	// Exact match: "openai/gpt-4o"
	key := providerName + "/" + model
	if p, ok := pc.pricing[key]; ok {
		return p, true
	}

	// Fallback: search all entries for model suffix match
	lowerModel := strings.ToLower(model)
	for k, p := range pc.pricing {
		parts := strings.SplitN(k, "/", 2)
		if len(parts) == 2 && strings.ToLower(parts[1]) == lowerModel {
			return p, true
		}
	}

	return ModelPricing{}, false
}

// CalculateCost computes the cost for a request given token counts.
func (pc *PricingConfig) CalculateCost(providerName, model string, inputTokens, outputTokens int) float64 {
	pricing, found := pc.GetPricing(providerName, model)
	if !found || pricing.Free {
		return 0.0
	}

	inputCost := (float64(inputTokens) / 1_000_000.0) * pricing.InputPer1M
	outputCost := (float64(outputTokens) / 1_000_000.0) * pricing.OutputPer1M

	// Round to 8 decimal places for precision
	total := inputCost + outputCost
	return math.Round(total*1e8) / 1e8
}

// EstimateCost estimates cost from max_tokens (pre-request).
func (pc *PricingConfig) EstimateCost(providerName, model string, estimatedInputTokens, maxOutputTokens int) float64 {
	return pc.CalculateCost(providerName, model, estimatedInputTokens, maxOutputTokens)
}

// IsFreeModel returns true if the model is marked as free.
func (pc *PricingConfig) IsFreeModel(providerName, model string) bool {
	pricing, found := pc.GetPricing(providerName, model)
	return found && pricing.Free
}

// AllPricing returns all pricing entries (for API responses).
func (pc *PricingConfig) AllPricing() map[string]ModelPricing {
	pc.mu.RLock()
	defer pc.mu.RUnlock()

	result := make(map[string]ModelPricing, len(pc.pricing))
	for k, v := range pc.pricing {
		result[k] = v
	}
	return result
}

// SetPricing updates or adds pricing for a model.
func (pc *PricingConfig) SetPricing(key string, pricing ModelPricing) {
	pc.mu.Lock()
	defer pc.mu.Unlock()
	pc.pricing[key] = pricing
}
