/*
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L3
Logic:       Full gateway router with middleware chain:
             CORS → Security Headers → Request ID → Rate Limit
             → Auth → Body Size Limit → Request Logger.
             Routes: /v1/chat/completions, /v1/embeddings,
             /v1/models, /healthz, /ready, /v1/providers/health.
Root Cause:  Sprint tasks T011-T024 — Gateway core.
Context:     Router design affects all downstream handlers.
Suitability: L3 model for proper middleware chain design.
──────────────────────────────────────────────────────────────
*/

package router

import (
	"net/http"
	"os"
	"strconv"
	"time"

	"github.com/go-chi/chi/v5"
	chimw "github.com/go-chi/chi/v5/middleware"
	"github.com/rs/zerolog"

	"github.com/AlfredDev/alfred/services/gateway/analytics"
	"github.com/AlfredDev/alfred/services/gateway/caching"
	"github.com/AlfredDev/alfred/services/gateway/config"
	"github.com/AlfredDev/alfred/services/gateway/handler"
	"github.com/AlfredDev/alfred/services/gateway/intelligence"
	gwmw "github.com/AlfredDev/alfred/services/gateway/middleware"
	"github.com/AlfredDev/alfred/services/gateway/observability"
	"github.com/AlfredDev/alfred/services/gateway/policy"
	"github.com/AlfredDev/alfred/services/gateway/provider"
	"github.com/AlfredDev/alfred/services/gateway/routing"
)

// NewRouter returns a configured chi Router with the full middleware chain
// and all API routes mounted.
// Optional variadic args: pipeline *analytics.Pipeline, metrics *observability.Metrics, tracer *observability.Tracer
func NewRouter(cfg *config.Config, appLogger zerolog.Logger, registry *provider.Registry, opts ...interface{}) http.Handler {
	r := chi.NewRouter()

	// Extract optional dependencies
	var analyticsPipe *analytics.Pipeline
	var metrics *observability.Metrics
	var tracer *observability.Tracer
	for _, opt := range opts {
		switch v := opt.(type) {
		case *analytics.Pipeline:
			analyticsPipe = v
		case *observability.Metrics:
			metrics = v
		case *observability.Tracer:
			tracer = v
		}
	}

	// --- Middleware Chain (order matters) ---
	// 1. CORS — must be first so preflight responses succeed
	r.Use(gwmw.CORSMiddleware([]string{"*"}))

	// 2. Security headers
	r.Use(gwmw.SecurityHeadersMiddleware)

	// 3. Request ID injection (chi built-in)
	r.Use(chimw.RequestID)

	// 4. Panic recovery
	r.Use(chimw.Recoverer)

	// 5. Request logger
	r.Use(mwRequestLogger(appLogger))

	// 5b. OpenTelemetry tracing (T145)
	if tracer != nil {
		r.Use(observability.TracingMiddleware(tracer))
	}

	// 6. Body size limit
	r.Use(mwMaxBodySize(cfg.MaxBodyBytes))

	// --- Health endpoints (no auth required) ---
	r.Get("/healthz", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		_, _ = w.Write([]byte(`{"status":"ok","service":"alfred-gateway"}`))
	})

	r.Get("/ready", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		_, _ = w.Write([]byte(`{"status":"ready","service":"alfred-gateway"}`))
	})

	r.Get("/health", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		_, _ = w.Write([]byte(`{"status":"healthy","service":"alfred-gateway"}`))
	})

	// Prometheus metrics endpoint (T144) — no auth required
	if metrics != nil {
		r.Get("/metrics", metrics.Handler())
	}

	// OpenAPI spec + Swagger UI (T191) — no auth required
	r.Get("/openapi.json", handler.OpenAPIHandler())
	r.Get("/docs", handler.SwaggerUIHandler())

	// --- API Routes (auth + rate limiting required) ---
	proxyHandler := handler.NewProxyHandler(appLogger, registry)
	pricingCfg := provider.DefaultPricing()
	providerCfgHandler := handler.NewProviderConfigHandler(appLogger, registry, pricingCfg)
	authMW := gwmw.NewAuthMiddleware(appLogger, cfg.APIKeyHeader)
	rateLimiter := gwmw.NewRateLimiter(appLogger, cfg.RateLimitEnabled, cfg.RateLimitRPM, cfg.RateLimitBurst)
	headerNorm := gwmw.NewHeaderNormalization(appLogger)
	timeoutMW := gwmw.NewTimeoutMiddleware(appLogger, cfg)

	// Routing engine + handler (T091-T098)
	routingEngine := routing.NewEngine(appLogger)
	failoverState := routing.NewFailoverState(5, 30*time.Second) // 5 failures, 30s cooldown
	routingHandler := handler.NewRoutingHandler(routingEngine, failoverState, appLogger)

	// Semantic cache engine + handler (T105-T115)
	// EmbeddingFunc is nil here; proxy handler wires the real provider at runtime.
	// When a real embedding provider is configured, replace nil with:
	//   func(ctx context.Context, text, model string) ([]float64, error) { ... }
	cacheEngine := caching.NewEngine(appLogger, nil)
	cacheHandler := handler.NewCacheHandler(cacheEngine, appLogger)

	// Analytics handler (T116-T118) — optional, uses pipeline if provided
	var analyticsHandler *handler.AnalyticsHandler
	if analyticsPipe != nil {
		analyticsHandler = handler.NewAnalyticsHandler(analyticsPipe, appLogger)
	}

	r.Route("/v1", func(r chi.Router) {
		r.Use(authMW.Handler)
		r.Use(rateLimiter.Handler)
		r.Use(headerNorm.Handler)   // T018: Header normalization
		r.Use(timeoutMW.Handler)    // T022: Per-provider timeout

		// Core AI endpoints (T014, T015, T016)
		r.Post("/chat/completions", proxyHandler.ChatCompletions)
		r.Post("/embeddings", proxyHandler.Embeddings)

		// Model listing
		r.Get("/models", proxyHandler.Models)

		// Provider health (T039)
		r.Get("/providers/health", proxyHandler.ProviderHealth)

		// Provider config CRUD (T028)
		r.Get("/providers", providerCfgHandler.ListProviders)
		r.Get("/providers/{name}", providerCfgHandler.GetProvider)
		r.Get("/providers/{name}/models", providerCfgHandler.GetProviderModels)
		r.Post("/providers/{name}/test", providerCfgHandler.TestProvider)
		r.Get("/providers/pricing", providerCfgHandler.GetPricing)
		r.Post("/providers/estimate", providerCfgHandler.EstimateCost)

		// Routing rules CRUD + evaluation (T091-T098)
		r.Get("/routing/rules", routingHandler.ListRules)
		r.Post("/routing/rules", routingHandler.CreateRule)
		r.Get("/routing/rules/{id}", routingHandler.GetRule)
		r.Put("/routing/rules/{id}", routingHandler.UpdateRule)
		r.Delete("/routing/rules/{id}", routingHandler.DeleteRule)
		r.Post("/routing/evaluate", routingHandler.EvaluateRouting)

		// Semantic cache management (T111-T114)
		r.Get("/cache/stats", cacheHandler.Stats)
		r.Delete("/cache", cacheHandler.FlushAll)
		r.Delete("/cache/{namespace}", cacheHandler.FlushNamespace)
		r.Delete("/cache/{namespace}/{entryId}", cacheHandler.InvalidateEntry)

		// Analytics (T116-T122)
		if analyticsHandler != nil {
			r.Post("/analytics/cost", analyticsHandler.QueryCost)
			r.Post("/analytics/latency", analyticsHandler.QueryLatency)
			r.Get("/analytics/cache", analyticsHandler.CacheAnalytics)
			r.Get("/analytics/pipeline", analyticsHandler.PipelineStats)
			r.Get("/analytics/daily", analyticsHandler.DailyCostAggregation)
			r.Get("/analytics/export/csv", analyticsHandler.ExportCostCSV)
		}

		// Experiment management (T099-T104)
		experimentEngine := routing.NewExperimentEngine(appLogger)
		experimentHandler := handler.NewExperimentHandler(experimentEngine, appLogger)
		r.Get("/experiments", experimentHandler.ListExperiments)
		r.Post("/experiments", experimentHandler.CreateExperiment)
		r.Get("/experiments/{id}", experimentHandler.GetExperiment)
		r.Post("/experiments/{id}/start", experimentHandler.StartExperiment)
		r.Post("/experiments/{id}/pause", experimentHandler.PauseExperiment)
		r.Post("/experiments/{id}/conclude", experimentHandler.ConcludeExperiment)
		r.Delete("/experiments/{id}", experimentHandler.DeleteExperiment)
		r.Post("/experiments/{id}/assign", experimentHandler.AssignVariant)
		r.Post("/experiments/{id}/result", experimentHandler.RecordResult)
		r.Get("/experiments/{id}/metrics", experimentHandler.GetMetrics)
		r.Get("/experiments/{id}/compare", experimentHandler.CompareVariants)

		// Policy management (T132-T137)
		opaClient := policy.NewOPAClient(policy.OPAConfig{}, appLogger)
		policyHandler := handler.NewPolicyHandler(opaClient, appLogger)
		r.Get("/policies", policyHandler.ListPolicies)
		r.Post("/policies", policyHandler.CreatePolicy)
		r.Get("/policies/templates", policyHandler.ListTemplates)
		r.Get("/policies/evaluations", policyHandler.GetEvaluationLog)
		r.Post("/policies/evaluate", policyHandler.EvaluatePolicy)
		r.Get("/policies/{id}", policyHandler.GetPolicy)
		r.Put("/policies/{id}", policyHandler.UpdatePolicy)
		r.Delete("/policies/{id}", policyHandler.DeletePolicy)
		r.Post("/policies/{id}/dry-run", policyHandler.ToggleDryRun)

		// Intelligence (T155-T164)
		classifier := intelligence.NewClassifier(nil)
		forecaster := intelligence.NewForecaster()
		anomalyDetector := intelligence.NewAnomalyDetector(0, 0)
		featureTracker := intelligence.NewFeatureTracker()
		arbitrageEngine := intelligence.NewArbitrageEngine()
		trafficRecorder := intelligence.NewTrafficRecorder(0)
		intelHandler := handler.NewIntelligenceHandler(
			classifier, forecaster, anomalyDetector,
			featureTracker, arbitrageEngine, trafficRecorder, appLogger,
		)
		r.Post("/intelligence/classify", intelHandler.Classify)
		r.Post("/intelligence/forecast", intelHandler.Forecast)
		r.Post("/intelligence/anomaly", intelHandler.DetectAnomaly)
		r.Post("/intelligence/features/cost", intelHandler.RecordFeatureCost)
		r.Get("/intelligence/features", intelHandler.GetFeatureCosts)
		r.Post("/intelligence/roi", intelHandler.CalculateROI)
		r.Post("/intelligence/efficiency", intelHandler.CalculateEfficiency)
		r.Get("/intelligence/arbitrage", intelHandler.FindArbitrage)
		r.Post("/intelligence/arbitrage/prices", intelHandler.UpdateArbitragePrices)
		r.Post("/intelligence/traffic/record", intelHandler.RecordTraffic)
		r.Post("/intelligence/traffic/simulate", intelHandler.SimulateTraffic)
	})

	return r
}

// mwMaxBodySize returns middleware that limits the request body size.
func mwMaxBodySize(maxBytes int64) func(http.Handler) http.Handler {
	if maxBytes <= 0 {
		maxBytes = 1 * 1024 * 1024 // default 1MB
	}

	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			// Allow env override
			max := maxBytes
			if v := os.Getenv("GATEWAY_MAX_BODY_BYTES"); v != "" {
				if parsed, err := strconv.ParseInt(v, 10, 64); err == nil && parsed > 0 {
					max = parsed
				}
			}

			if r.ContentLength > 0 && r.ContentLength > max {
				http.Error(w, `{"error":"request_too_large","message":"request body too large"}`, http.StatusRequestEntityTooLarge)
				return
			}

			r.Body = http.MaxBytesReader(w, r.Body, max)
			next.ServeHTTP(w, r)
		})
	}
}

func mwRequestLogger(appLogger zerolog.Logger) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			start := time.Now()
			rw := chimw.NewWrapResponseWriter(w, r.ProtoMajor)
			next.ServeHTTP(rw, r)
			dur := time.Since(start)
			reqID := chimw.GetReqID(r.Context())
			appLogger.Info().
				Str("method", r.Method).
				Str("path", r.URL.Path).
				Str("req_id", reqID).
				Int("status", rw.Status()).
				Dur("duration", dur).
				Msg("request completed")
		})
	}
}
