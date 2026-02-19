/*
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L2
Logic:       Function calling / tool use normalization layer.
             Translates OpenAI-format tool definitions and tool
             calls to/from provider-specific formats (Anthropic,
             Gemini). Ensures consistent tool calling experience
             regardless of which provider serves the request.
Root Cause:  Sprint task T017 — Function calling / tool use
             pass-through.
Context:     OpenAI, Anthropic, and Gemini each have different
             schemas for tool definitions and tool call responses.
             This module normalizes them to the OpenAI format at
             the gateway layer.
Suitability: L2 for well-documented API schema translation.
──────────────────────────────────────────────────────────────
*/

package provider

import (
	"encoding/json"
	"fmt"
)

// --- Anthropic Tool Types ---

// AnthropicTool represents a tool definition in Anthropic's format.
type AnthropicTool struct {
	Name        string          `json:"name"`
	Description string          `json:"description,omitempty"`
	InputSchema json.RawMessage `json:"input_schema"`
}

// AnthropicToolChoice represents Anthropic's tool_choice parameter.
type AnthropicToolChoice struct {
	Type string `json:"type"`           // "auto", "any", "tool"
	Name string `json:"name,omitempty"` // only when type="tool"
}

// AnthropicContentBlock represents a content block in Anthropic responses.
type AnthropicContentBlock struct {
	Type  string          `json:"type"`            // "text", "tool_use"
	Text  string          `json:"text,omitempty"`  // for type="text"
	ID    string          `json:"id,omitempty"`    // for type="tool_use"
	Name  string          `json:"name,omitempty"`  // for type="tool_use"
	Input json.RawMessage `json:"input,omitempty"` // for type="tool_use"
}

// AnthropicToolResult represents a tool_result content block for Anthropic.
type AnthropicToolResult struct {
	Type      string `json:"type"` // "tool_result"
	ToolUseID string `json:"tool_use_id"`
	Content   string `json:"content"`
}

// --- Gemini Tool Types ---

// GeminiTool represents a tool (function declaration) in Gemini's format.
type GeminiTool struct {
	FunctionDeclarations []GeminiFunctionDeclaration `json:"function_declarations"`
}

// GeminiFunctionDeclaration represents a function declaration in Gemini's format.
type GeminiFunctionDeclaration struct {
	Name        string          `json:"name"`
	Description string          `json:"description"`
	Parameters  json.RawMessage `json:"parameters"` // JSON Schema subset
}

// GeminiFunctionCall represents a function call in Gemini responses.
type GeminiFunctionCall struct {
	Name string          `json:"name"`
	Args json.RawMessage `json:"args"`
}

// GeminiFunctionResponse represents a function response to send back.
type GeminiFunctionResponse struct {
	Name     string          `json:"name"`
	Response json.RawMessage `json:"response"`
}

// --- Conversion Functions ---

// ConvertToolsToAnthropic converts OpenAI tool definitions to Anthropic format.
func ConvertToolsToAnthropic(tools []Tool) []AnthropicTool {
	if len(tools) == 0 {
		return nil
	}
	result := make([]AnthropicTool, 0, len(tools))
	for _, t := range tools {
		if t.Type != "function" {
			continue
		}
		result = append(result, AnthropicTool{
			Name:        t.Function.Name,
			Description: t.Function.Description,
			InputSchema: t.Function.Parameters,
		})
	}
	return result
}

// ConvertToolChoiceToAnthropic converts OpenAI tool_choice to Anthropic format.
func ConvertToolChoiceToAnthropic(toolChoice interface{}) *AnthropicToolChoice {
	if toolChoice == nil {
		return nil
	}

	switch v := toolChoice.(type) {
	case string:
		switch v {
		case "auto":
			return &AnthropicToolChoice{Type: "auto"}
		case "none":
			return nil // Anthropic doesn't have "none" — omit tools
		case "required":
			return &AnthropicToolChoice{Type: "any"}
		default:
			return &AnthropicToolChoice{Type: "auto"}
		}
	case map[string]interface{}:
		// OpenAI format: {"type": "function", "function": {"name": "fn_name"}}
		if fn, ok := v["function"].(map[string]interface{}); ok {
			if name, ok := fn["name"].(string); ok {
				return &AnthropicToolChoice{Type: "tool", Name: name}
			}
		}
	}

	return &AnthropicToolChoice{Type: "auto"}
}

// ConvertAnthropicToolCallsToOpenAI converts Anthropic tool_use content blocks
// to OpenAI-format tool calls.
func ConvertAnthropicToolCallsToOpenAI(contentBlocks []AnthropicContentBlock) (string, []ToolCall) {
	var textContent string
	var toolCalls []ToolCall

	for _, block := range contentBlocks {
		switch block.Type {
		case "text":
			textContent += block.Text
		case "tool_use":
			args, _ := json.Marshal(block.Input)
			toolCalls = append(toolCalls, ToolCall{
				ID:   block.ID,
				Type: "function",
				Function: FunctionCall{
					Name:      block.Name,
					Arguments: string(args),
				},
			})
		}
	}

	return textContent, toolCalls
}

// ConvertToolResultToAnthropicMessage converts an OpenAI-format tool response
// message to Anthropic's tool_result content block format.
func ConvertToolResultToAnthropicMessage(msg ChatMessage) map[string]interface{} {
	content := ""
	if c, ok := msg.Content.(string); ok {
		content = c
	}
	return map[string]interface{}{
		"role": "user",
		"content": []map[string]interface{}{
			{
				"type":        "tool_result",
				"tool_use_id": msg.ToolCallID,
				"content":     content,
			},
		},
	}
}

// ConvertToolsToGemini converts OpenAI tool definitions to Gemini format.
func ConvertToolsToGemini(tools []Tool) []GeminiTool {
	if len(tools) == 0 {
		return nil
	}
	declarations := make([]GeminiFunctionDeclaration, 0, len(tools))
	for _, t := range tools {
		if t.Type != "function" {
			continue
		}
		declarations = append(declarations, GeminiFunctionDeclaration{
			Name:        t.Function.Name,
			Description: t.Function.Description,
			Parameters:  t.Function.Parameters,
		})
	}
	return []GeminiTool{{FunctionDeclarations: declarations}}
}

// ConvertGeminiFunctionCallToOpenAI converts a Gemini function call to OpenAI format.
func ConvertGeminiFunctionCallToOpenAI(fc GeminiFunctionCall, callID string) ToolCall {
	args, _ := json.Marshal(fc.Args)
	return ToolCall{
		ID:   callID,
		Type: "function",
		Function: FunctionCall{
			Name:      fc.Name,
			Arguments: string(args),
		},
	}
}

// HasToolCalls checks if a ChatRequest contains tool definitions.
func HasToolCalls(req *ChatRequest) bool {
	return len(req.Tools) > 0
}

// HasToolMessages checks if any messages in the request are tool responses.
func HasToolMessages(req *ChatRequest) bool {
	for _, msg := range req.Messages {
		if msg.Role == "tool" || msg.ToolCallID != "" {
			return true
		}
	}
	return false
}

// ValidateToolDefinitions checks that tool definitions are well-formed.
func ValidateToolDefinitions(tools []Tool) error {
	seen := make(map[string]bool)
	for i, t := range tools {
		if t.Type != "function" {
			return fmt.Errorf("tool[%d]: unsupported type %q (only 'function' is supported)", i, t.Type)
		}
		if t.Function.Name == "" {
			return fmt.Errorf("tool[%d]: function name is required", i)
		}
		if seen[t.Function.Name] {
			return fmt.Errorf("tool[%d]: duplicate function name %q", i, t.Function.Name)
		}
		seen[t.Function.Name] = true
		// Validate parameters is valid JSON if present.
		if len(t.Function.Parameters) > 0 {
			var js json.RawMessage
			if err := json.Unmarshal(t.Function.Parameters, &js); err != nil {
				return fmt.Errorf("tool[%d] %q: parameters is not valid JSON: %w", i, t.Function.Name, err)
			}
		}
	}
	return nil
}
