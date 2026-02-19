/*
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L1
Logic:       Auto-generated OpenAPI 3.0 specification from gateway
             handler definitions. Embeds the spec as a Go constant
             and serves it at /openapi.json and /docs (Swagger UI).
Root Cause:  Sprint task T191 — OpenAPI spec.
Context:     Enables API documentation, client codegen, and
             integration testing from the gateway service.
Suitability: L1 — specification writing.
──────────────────────────────────────────────────────────────
*/

package handler

import (
	"encoding/json"
	"fmt"
	"net/http"
)

// OpenAPISpec returns the OpenAPI 3.0 specification for the Alfred Gateway.
func OpenAPISpec() map[string]interface{} {
	return map[string]interface{}{
		"openapi": "3.0.3",
		"info": map[string]interface{}{
			"title":       "Alfred AI Gateway",
			"description": "Enterprise AI Control & Economy Platform — Gateway API",
			"version":     "1.0.0",
			"contact": map[string]interface{}{
				"name": "Alfred Engineering",
			},
			"license": map[string]interface{}{
				"name": "Proprietary",
			},
		},
		"servers": []map[string]interface{}{
			{"url": "http://localhost:8080", "description": "Local development"},
			{"url": "https://api.alfred.ai", "description": "Production"},
		},
		"paths": openAPIPaths(),
		"components": map[string]interface{}{
			"securitySchemes": map[string]interface{}{
				"BearerAuth": map[string]interface{}{
					"type":         "http",
					"scheme":       "bearer",
					"bearerFormat": "API Key",
					"description":  "Alfred API key (alf_...)",
				},
			},
			"schemas": openAPISchemas(),
		},
		"security": []map[string]interface{}{
			{"BearerAuth": []string{}},
		},
		"tags": []map[string]interface{}{
			{"name": "Chat", "description": "AI chat completion endpoints"},
			{"name": "Embeddings", "description": "Text embedding endpoints"},
			{"name": "Models", "description": "Available model listing"},
			{"name": "Providers", "description": "Provider management and health"},
			{"name": "Routing", "description": "Intelligent routing rules"},
			{"name": "Cache", "description": "Semantic cache management"},
			{"name": "Analytics", "description": "Cost and usage analytics"},
			{"name": "Health", "description": "Service health checks"},
		},
	}
}

func openAPIPaths() map[string]interface{} {
	return map[string]interface{}{
		"/v1/chat/completions": map[string]interface{}{
			"post": map[string]interface{}{
				"tags":        []string{"Chat"},
				"summary":     "Create chat completion",
				"description": "Send a chat completion request through the Alfred gateway. Supports streaming via SSE.",
				"operationId": "createChatCompletion",
				"requestBody": map[string]interface{}{
					"required": true,
					"content": map[string]interface{}{
						"application/json": map[string]interface{}{
							"schema": map[string]interface{}{"$ref": "#/components/schemas/ChatRequest"},
						},
					},
				},
				"responses": map[string]interface{}{
					"200": map[string]interface{}{
						"description": "Successful completion",
						"content": map[string]interface{}{
							"application/json": map[string]interface{}{
								"schema": map[string]interface{}{"$ref": "#/components/schemas/ChatResponse"},
							},
						},
					},
					"400": map[string]interface{}{"description": "Invalid request"},
					"401": map[string]interface{}{"description": "Unauthorized — invalid API key"},
					"429": map[string]interface{}{"description": "Rate limit exceeded or quota exhausted"},
					"502": map[string]interface{}{"description": "Upstream provider error"},
				},
			},
		},
		"/v1/embeddings": map[string]interface{}{
			"post": map[string]interface{}{
				"tags":        []string{"Embeddings"},
				"summary":     "Create embeddings",
				"operationId": "createEmbeddings",
				"requestBody": map[string]interface{}{
					"required": true,
					"content": map[string]interface{}{
						"application/json": map[string]interface{}{
							"schema": map[string]interface{}{"$ref": "#/components/schemas/EmbeddingsRequest"},
						},
					},
				},
				"responses": map[string]interface{}{
					"200": map[string]interface{}{
						"description": "Successful embeddings",
						"content": map[string]interface{}{
							"application/json": map[string]interface{}{
								"schema": map[string]interface{}{"$ref": "#/components/schemas/EmbeddingsResponse"},
							},
						},
					},
				},
			},
		},
		"/v1/models": map[string]interface{}{
			"get": map[string]interface{}{
				"tags":        []string{"Models"},
				"summary":     "List available models",
				"operationId": "listModels",
				"responses": map[string]interface{}{
					"200": map[string]interface{}{
						"description": "List of models from all registered providers",
					},
				},
			},
		},
		"/v1/providers/health": map[string]interface{}{
			"get": map[string]interface{}{
				"tags":        []string{"Providers"},
				"summary":     "Check provider health",
				"operationId": "getProviderHealth",
				"responses": map[string]interface{}{
					"200": map[string]interface{}{
						"description": "Health status of all providers",
					},
				},
			},
		},
		"/v1/providers": map[string]interface{}{
			"get": map[string]interface{}{
				"tags":        []string{"Providers"},
				"summary":     "List providers",
				"operationId": "listProviders",
				"responses": map[string]interface{}{
					"200": map[string]interface{}{
						"description": "Registered provider configurations",
					},
				},
			},
		},
		"/v1/providers/{name}": map[string]interface{}{
			"get": map[string]interface{}{
				"tags":        []string{"Providers"},
				"summary":     "Get provider details",
				"operationId": "getProvider",
				"parameters": []map[string]interface{}{
					{"name": "name", "in": "path", "required": true, "schema": map[string]interface{}{"type": "string"}},
				},
				"responses": map[string]interface{}{
					"200": map[string]interface{}{"description": "Provider details"},
					"404": map[string]interface{}{"description": "Provider not found"},
				},
			},
		},
		"/v1/routing/rules": map[string]interface{}{
			"get": map[string]interface{}{
				"tags":        []string{"Routing"},
				"summary":     "List routing rules",
				"operationId": "listRoutingRules",
				"responses": map[string]interface{}{
					"200": map[string]interface{}{"description": "All routing rules"},
				},
			},
			"post": map[string]interface{}{
				"tags":        []string{"Routing"},
				"summary":     "Create routing rule",
				"operationId": "createRoutingRule",
				"requestBody": map[string]interface{}{
					"required": true,
					"content": map[string]interface{}{
						"application/json": map[string]interface{}{
							"schema": map[string]interface{}{"$ref": "#/components/schemas/RoutingRule"},
						},
					},
				},
				"responses": map[string]interface{}{
					"201": map[string]interface{}{"description": "Rule created"},
				},
			},
		},
		"/v1/cache/stats": map[string]interface{}{
			"get": map[string]interface{}{
				"tags":        []string{"Cache"},
				"summary":     "Get cache statistics",
				"operationId": "getCacheStats",
				"responses": map[string]interface{}{
					"200": map[string]interface{}{"description": "Cache hit/miss statistics"},
				},
			},
		},
		"/v1/analytics/cost": map[string]interface{}{
			"post": map[string]interface{}{
				"tags":        []string{"Analytics"},
				"summary":     "Query cost analytics",
				"operationId": "queryCostAnalytics",
				"requestBody": map[string]interface{}{
					"required": true,
					"content": map[string]interface{}{
						"application/json": map[string]interface{}{
							"schema": map[string]interface{}{"$ref": "#/components/schemas/CostQuery"},
						},
					},
				},
				"responses": map[string]interface{}{
					"200": map[string]interface{}{"description": "Cost analytics results"},
				},
			},
		},
		"/v1/analytics/pipeline": map[string]interface{}{
			"get": map[string]interface{}{
				"tags":        []string{"Analytics"},
				"summary":     "Get pipeline health stats",
				"operationId": "getPipelineStats",
				"responses": map[string]interface{}{
					"200": map[string]interface{}{"description": "Analytics pipeline health"},
				},
			},
		},
		"/healthz": map[string]interface{}{
			"get": map[string]interface{}{
				"tags":        []string{"Health"},
				"summary":     "Liveness probe",
				"operationId": "healthz",
				"security":    []map[string]interface{}{},
				"responses": map[string]interface{}{
					"200": map[string]interface{}{"description": "Service is alive"},
				},
			},
		},
		"/ready": map[string]interface{}{
			"get": map[string]interface{}{
				"tags":        []string{"Health"},
				"summary":     "Readiness probe",
				"operationId": "ready",
				"security":    []map[string]interface{}{},
				"responses": map[string]interface{}{
					"200": map[string]interface{}{"description": "Service is ready"},
				},
			},
		},
		"/metrics": map[string]interface{}{
			"get": map[string]interface{}{
				"tags":        []string{"Health"},
				"summary":     "Prometheus metrics",
				"operationId": "metrics",
				"security":    []map[string]interface{}{},
				"responses": map[string]interface{}{
					"200": map[string]interface{}{"description": "Prometheus text exposition format"},
				},
			},
		},
	}
}

func openAPISchemas() map[string]interface{} {
	return map[string]interface{}{
		"ChatRequest": map[string]interface{}{
			"type":     "object",
			"required": []string{"model", "messages"},
			"properties": map[string]interface{}{
				"model":       map[string]interface{}{"type": "string", "description": "Model ID (e.g. gpt-4o, claude-3.5-sonnet)"},
				"messages":    map[string]interface{}{"type": "array", "items": map[string]interface{}{"$ref": "#/components/schemas/ChatMessage"}},
				"max_tokens":  map[string]interface{}{"type": "integer", "description": "Maximum completion tokens"},
				"temperature": map[string]interface{}{"type": "number", "minimum": 0, "maximum": 2},
				"stream":      map[string]interface{}{"type": "boolean", "default": false},
				"tools":       map[string]interface{}{"type": "array", "items": map[string]interface{}{"$ref": "#/components/schemas/Tool"}},
				"user":        map[string]interface{}{"type": "string"},
			},
		},
		"ChatMessage": map[string]interface{}{
			"type":     "object",
			"required": []string{"role", "content"},
			"properties": map[string]interface{}{
				"role":         map[string]interface{}{"type": "string", "enum": []string{"system", "user", "assistant", "tool"}},
				"content":      map[string]interface{}{"description": "String or array of content parts"},
				"name":         map[string]interface{}{"type": "string"},
				"tool_calls":   map[string]interface{}{"type": "array", "items": map[string]interface{}{"$ref": "#/components/schemas/ToolCall"}},
				"tool_call_id": map[string]interface{}{"type": "string"},
			},
		},
		"ChatResponse": map[string]interface{}{
			"type": "object",
			"properties": map[string]interface{}{
				"id":      map[string]interface{}{"type": "string"},
				"object":  map[string]interface{}{"type": "string"},
				"created": map[string]interface{}{"type": "integer"},
				"model":   map[string]interface{}{"type": "string"},
				"choices": map[string]interface{}{"type": "array", "items": map[string]interface{}{"$ref": "#/components/schemas/Choice"}},
				"usage":   map[string]interface{}{"$ref": "#/components/schemas/Usage"},
			},
		},
		"Choice": map[string]interface{}{
			"type": "object",
			"properties": map[string]interface{}{
				"index":         map[string]interface{}{"type": "integer"},
				"message":       map[string]interface{}{"$ref": "#/components/schemas/ChatMessage"},
				"finish_reason": map[string]interface{}{"type": "string", "enum": []string{"stop", "length", "tool_calls", "content_filter"}},
			},
		},
		"Usage": map[string]interface{}{
			"type": "object",
			"properties": map[string]interface{}{
				"prompt_tokens":     map[string]interface{}{"type": "integer"},
				"completion_tokens": map[string]interface{}{"type": "integer"},
				"total_tokens":      map[string]interface{}{"type": "integer"},
			},
		},
		"Tool": map[string]interface{}{
			"type": "object",
			"properties": map[string]interface{}{
				"type":     map[string]interface{}{"type": "string", "enum": []string{"function"}},
				"function": map[string]interface{}{"$ref": "#/components/schemas/Function"},
			},
		},
		"Function": map[string]interface{}{
			"type": "object",
			"properties": map[string]interface{}{
				"name":        map[string]interface{}{"type": "string"},
				"description": map[string]interface{}{"type": "string"},
				"parameters":  map[string]interface{}{"type": "object"},
			},
		},
		"ToolCall": map[string]interface{}{
			"type": "object",
			"properties": map[string]interface{}{
				"id":       map[string]interface{}{"type": "string"},
				"type":     map[string]interface{}{"type": "string"},
				"function": map[string]interface{}{"type": "object", "properties": map[string]interface{}{"name": map[string]interface{}{"type": "string"}, "arguments": map[string]interface{}{"type": "string"}}},
			},
		},
		"EmbeddingsRequest": map[string]interface{}{
			"type":     "object",
			"required": []string{"model", "input"},
			"properties": map[string]interface{}{
				"model": map[string]interface{}{"type": "string"},
				"input": map[string]interface{}{"description": "String or array of strings to embed"},
				"user":  map[string]interface{}{"type": "string"},
			},
		},
		"EmbeddingsResponse": map[string]interface{}{
			"type": "object",
			"properties": map[string]interface{}{
				"object": map[string]interface{}{"type": "string"},
				"data":   map[string]interface{}{"type": "array", "items": map[string]interface{}{"type": "object"}},
				"model":  map[string]interface{}{"type": "string"},
				"usage":  map[string]interface{}{"type": "object"},
			},
		},
		"RoutingRule": map[string]interface{}{
			"type": "object",
			"properties": map[string]interface{}{
				"id":          map[string]interface{}{"type": "string"},
				"name":        map[string]interface{}{"type": "string"},
				"priority":    map[string]interface{}{"type": "integer"},
				"conditions":  map[string]interface{}{"type": "object"},
				"action":      map[string]interface{}{"type": "object"},
				"enabled":     map[string]interface{}{"type": "boolean"},
			},
		},
		"CostQuery": map[string]interface{}{
			"type": "object",
			"properties": map[string]interface{}{
				"group_by":   map[string]interface{}{"type": "string", "enum": []string{"model", "team", "provider", "date"}},
				"start_date": map[string]interface{}{"type": "string", "format": "date"},
				"end_date":   map[string]interface{}{"type": "string", "format": "date"},
				"org_id":     map[string]interface{}{"type": "string"},
				"team_id":    map[string]interface{}{"type": "string"},
				"limit":      map[string]interface{}{"type": "integer", "default": 100},
				"offset":     map[string]interface{}{"type": "integer", "default": 0},
			},
		},
		"Error": map[string]interface{}{
			"type": "object",
			"properties": map[string]interface{}{
				"error": map[string]interface{}{
					"type": "object",
					"properties": map[string]interface{}{
						"type":    map[string]interface{}{"type": "string"},
						"message": map[string]interface{}{"type": "string"},
					},
				},
			},
		},
	}
}

// OpenAPIHandler serves the OpenAPI spec at /openapi.json.
func OpenAPIHandler() http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		spec := OpenAPISpec()
		w.Header().Set("Content-Type", "application/json")
		w.Header().Set("Access-Control-Allow-Origin", "*")
		json.NewEncoder(w).Encode(spec)
	}
}

// SwaggerUIHandler serves a minimal Swagger UI page.
func SwaggerUIHandler() http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		html := `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Alfred Gateway API</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css">
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
    <script>
    SwaggerUI({
        url: '/openapi.json',
        dom_id: '#swagger-ui',
        deepLinking: true,
        presets: [SwaggerUIBundle.presets.apis, SwaggerUIBundle.SwaggerUIStandalonePreset],
        layout: "BaseLayout"
    });
    </script>
</body>
</html>`
		w.Header().Set("Content-Type", "text/html; charset=utf-8")
		fmt.Fprint(w, html)
	}
}
