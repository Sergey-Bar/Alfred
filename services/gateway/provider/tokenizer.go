/*
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L2
Logic:       Per-provider tokenizer support. Different providers
             count tokens differently — OpenAI uses tiktoken (BPE),
             Anthropic uses their own tokenizer, Gemini counts
             differently, etc. This module provides a unified
             token counting interface that dispatches to the
             correct counting strategy per provider/model.
Root Cause:  Sprint task T048 — Provider tokenizer support
             (Anthropic, Gemini differ from tiktoken).
Context:     Accurate token counting is essential for correct
             billing. Overcount wastes budget, undercount leaks.
Suitability: L2 — known counting rules per provider.
──────────────────────────────────────────────────────────────
*/

package provider

import (
	"strings"
	"unicode/utf8"
)

// TokenCounter provides per-provider token counting strategies.
type TokenCounter struct {
	strategy TokenStrategy
}

// TokenStrategy defines the counting algorithm for a provider.
type TokenStrategy int

const (
	// StrategyTiktoken is the BPE-based tokenizer used by OpenAI models.
	StrategyTiktoken TokenStrategy = iota

	// StrategyAnthropic uses Anthropic's counting rules (~3.5 chars/token).
	StrategyAnthropic

	// StrategyGemini uses Google's counting (~4 chars/token with different overhead).
	StrategyGemini

	// StrategyMistral uses Mistral's SentencePiece variant (~3.8 chars/token).
	StrategyMistral

	// StrategyDefault uses a conservative 4 chars/token estimate.
	StrategyDefault
)

// TokenCountResult holds the result of a token counting operation.
type TokenCountResult struct {
	PromptTokens    int    `json:"prompt_tokens"`
	EstimatedOutput int    `json:"estimated_output_tokens"`
	Strategy        string `json:"strategy"`
	IsEstimate      bool   `json:"is_estimate"`
}

// NewTokenCounter creates a counter for the given provider name.
func NewTokenCounter(providerName string) *TokenCounter {
	strategy := resolveStrategy(providerName)
	return &TokenCounter{strategy: strategy}
}

// resolveStrategy maps provider names to their token counting strategy.
func resolveStrategy(name string) TokenStrategy {
	normalized := strings.ToLower(name)
	switch {
	case strings.Contains(normalized, "openai"):
		return StrategyTiktoken
	case strings.Contains(normalized, "anthropic"), strings.Contains(normalized, "claude"):
		return StrategyAnthropic
	case strings.Contains(normalized, "gemini"), strings.Contains(normalized, "google"):
		return StrategyGemini
	case strings.Contains(normalized, "mistral"):
		return StrategyMistral
	case strings.Contains(normalized, "groq"):
		// Groq serves OpenAI-compatible models, uses tiktoken-equivalent
		return StrategyTiktoken
	case strings.Contains(normalized, "together"):
		// Together AI serves various models; use default
		return StrategyDefault
	case strings.Contains(normalized, "azure"):
		// Azure OpenAI uses the same tokenizer as OpenAI
		return StrategyTiktoken
	default:
		return StrategyDefault
	}
}

// CountMessages estimates token count for a slice of chat messages.
func (tc *TokenCounter) CountMessages(messages []ChatMessage) TokenCountResult {
	total := 0
	for _, msg := range messages {
		total += tc.countMessage(msg)
	}

	return TokenCountResult{
		PromptTokens:    total,
		EstimatedOutput: 0,
		Strategy:        tc.strategyName(),
		IsEstimate:      true,
	}
}

// CountText estimates token count for raw text.
func (tc *TokenCounter) CountText(text string) int {
	return tc.estimateTokens(text)
}

// countMessage estimates tokens for a single message including
// the per-message overhead that each provider adds.
func (tc *TokenCounter) countMessage(msg ChatMessage) int {
	tokens := 0

	// Per-message overhead varies by provider
	tokens += tc.messageOverhead()

	// Role token (always 1)
	tokens += 1

	// Content tokens
	switch content := msg.Content.(type) {
	case string:
		tokens += tc.estimateTokens(content)
	case []interface{}:
		// Multi-modal content parts (e.g., text + image)
		for _, part := range content {
			if m, ok := part.(map[string]interface{}); ok {
				if text, exists := m["text"]; exists {
					if s, ok := text.(string); ok {
						tokens += tc.estimateTokens(s)
					}
				}
				if m["type"] == "image_url" {
					// Image tokens vary by resolution; use conservative estimate
					tokens += tc.imageTokenEstimate()
				}
			}
		}
	}

	// Name field
	if msg.Name != "" {
		tokens += tc.estimateTokens(msg.Name) + 1 // +1 for separator
	}

	// Tool calls
	for _, tc2 := range msg.ToolCalls {
		tokens += tc.estimateTokens(tc2.Function.Name)
		tokens += tc.estimateTokens(tc2.Function.Arguments)
		tokens += 4 // overhead for tool call structure
	}

	// Tool call ID
	if msg.ToolCallID != "" {
		tokens += tc.estimateTokens(msg.ToolCallID)
	}

	return tokens
}

// estimateTokens applies the provider-specific chars-per-token ratio.
func (tc *TokenCounter) estimateTokens(text string) int {
	if text == "" {
		return 0
	}

	charCount := utf8.RuneCountInString(text)

	switch tc.strategy {
	case StrategyTiktoken:
		// OpenAI BPE: ~3.3 chars per token for English, ~1.5 for CJK
		// Use 3.3 as average, with minimum of 1 token
		tokens := int(float64(charCount) / 3.3)
		if tokens == 0 {
			return 1
		}
		return tokens

	case StrategyAnthropic:
		// Anthropic: typically ~3.5 chars per token
		tokens := int(float64(charCount) / 3.5)
		if tokens == 0 {
			return 1
		}
		return tokens

	case StrategyGemini:
		// Gemini: ~4 chars per token, slightly different encoding
		tokens := int(float64(charCount) / 4.0)
		if tokens == 0 {
			return 1
		}
		return tokens

	case StrategyMistral:
		// Mistral SentencePiece: ~3.8 chars per token
		tokens := int(float64(charCount) / 3.8)
		if tokens == 0 {
			return 1
		}
		return tokens

	default:
		// Conservative: 4 chars per token
		tokens := charCount / 4
		if tokens == 0 {
			return 1
		}
		return tokens
	}
}

// messageOverhead returns the per-message token overhead for the provider.
// OpenAI adds ~4 tokens per message, Anthropic adds ~3, etc.
func (tc *TokenCounter) messageOverhead() int {
	switch tc.strategy {
	case StrategyTiktoken:
		return 4 // <|im_start|>role\n...content<|im_end|>\n
	case StrategyAnthropic:
		return 3 // \n\nHuman: / \n\nAssistant:
	case StrategyGemini:
		return 3
	case StrategyMistral:
		return 4 // similar to OpenAI format
	default:
		return 4
	}
}

// imageTokenEstimate returns a conservative token estimate for an image.
func (tc *TokenCounter) imageTokenEstimate() int {
	switch tc.strategy {
	case StrategyTiktoken:
		return 85 // OpenAI: 85 tokens for low-res, up to 1105 for high-res
	case StrategyAnthropic:
		return 1024 // Anthropic charges ~1024 tokens per image
	case StrategyGemini:
		return 258 // Gemini: 258 tokens per image
	default:
		return 512 // conservative default
	}
}

// strategyName returns a human-readable name for the current strategy.
func (tc *TokenCounter) strategyName() string {
	switch tc.strategy {
	case StrategyTiktoken:
		return "tiktoken"
	case StrategyAnthropic:
		return "anthropic"
	case StrategyGemini:
		return "gemini"
	case StrategyMistral:
		return "mistral"
	default:
		return "default"
	}
}

// CountToolDefinitions estimates token count for tool/function definitions.
// Tool definitions add tokens to the system prompt area.
func (tc *TokenCounter) CountToolDefinitions(tools []Tool) int {
	if len(tools) == 0 {
		return 0
	}

	tokens := 0
	for _, tool := range tools {
		tokens += tc.estimateTokens(tool.Function.Name)
		tokens += tc.estimateTokens(tool.Function.Description)
		if tool.Function.Parameters != nil {
			tokens += tc.estimateTokens(string(tool.Function.Parameters))
		}
		tokens += 8 // overhead per tool definition
	}
	tokens += 12 // system-level tool overhead
	return tokens
}

// EstimateChatRequest provides a complete token estimate for a chat request.
func (tc *TokenCounter) EstimateChatRequest(req *ChatRequest) TokenCountResult {
	result := tc.CountMessages(req.Messages)

	// Add tool definitions
	if len(req.Tools) > 0 {
		result.PromptTokens += tc.CountToolDefinitions(req.Tools)
	}

	// Add assistant reply priming (3 tokens for each provider)
	result.PromptTokens += 3

	// Estimate output tokens based on max_tokens or default
	if req.MaxTokens != nil {
		result.EstimatedOutput = *req.MaxTokens
	} else {
		result.EstimatedOutput = 1024 // default assumption
	}

	return result
}
