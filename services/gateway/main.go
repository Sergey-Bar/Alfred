/*
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L3
Logic:       Gateway entry point with graceful shutdown, provider
             registration, Redis connectivity, and periodic health
             checks. Implements T011 (HTTP server with graceful
             shutdown) and coordinates all gateway subsystems.
Root Cause:  Sprint task T011 — HTTP server with graceful shutdown.
Context:     Entry point wiring config → logger → Redis → providers
             → router → HTTP server with OS signal handling.
Suitability: L3 model for graceful shutdown and system wiring.
──────────────────────────────────────────────────────────────
*/

package main

import (
	"context"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/AlfredDev/alfred/services/gateway/analytics"
	"github.com/AlfredDev/alfred/services/gateway/config"
	"github.com/AlfredDev/alfred/services/gateway/logger"
	"github.com/AlfredDev/alfred/services/gateway/observability"
	"github.com/AlfredDev/alfred/services/gateway/provider"
	"github.com/AlfredDev/alfred/services/gateway/redisclient"
	"github.com/AlfredDev/alfred/services/gateway/router"
	"github.com/rs/zerolog"
)

func main() {
	cfg := config.Load()
	log := logger.New(cfg)

	log.Info().Str("env", cfg.Env).Msg("alfred gateway starting")

	// Initialize Redis
	rc, err := redisclient.New(cfg)
	if err != nil {
		log.Warn().Err(err).Msg("redis init failed — continuing without Redis")
	} else {
		if err := rc.Ping(); err != nil {
			log.Warn().Err(err).Msg("redis ping failed")
		} else {
			log.Info().Msg("redis connected")
		}
	}

	// Initialize provider registry
	registry := provider.NewRegistry()
	registerProviders(cfg, registry, log)

	// Start analytics pipeline (T116-T118)
	var analyticsSink analytics.Sink
	if chDSN := os.Getenv("CLICKHOUSE_DSN"); chDSN != "" {
		chSink, err := analytics.NewClickHouseSink(chDSN, log)
		if err != nil {
			log.Warn().Err(err).Msg("clickhouse sink init failed — falling back to log sink")
			analyticsSink = analytics.NewLogSink(log)
		} else {
			analyticsSink = chSink
			log.Info().Msg("clickhouse analytics sink connected")
		}
	} else {
		analyticsSink = analytics.NewLogSink(log)
		log.Info().Msg("analytics using log sink (set CLICKHOUSE_DSN for production)")
	}
	analyticsPipeline := analytics.NewPipeline(log, analyticsSink)
	analyticsPipeline.Start(context.Background())

	// Initialize observability (T144-T145)
	metrics := observability.NewMetrics(log)
	traceExporter := observability.NewLogExporter(log)
	tracer := observability.NewTracer(log, traceExporter, 1.0) // sample 100% in dev

	// Create router with all middleware and handlers
	r := router.NewRouter(cfg, log, registry, analyticsPipeline, metrics, tracer)

	// Create HTTP server with timeouts
	srv := &http.Server{
		Addr:         cfg.Addr,
		Handler:      r,
		ReadTimeout:  30 * time.Second,
		WriteTimeout: cfg.DefaultTimeout + 10*time.Second, // extra buffer for streaming
		IdleTimeout:  120 * time.Second,
	}

	// Start background provider health poller (T039)
	healthPoller := provider.NewHealthPoller(registry, log, 30*time.Second)
	healthPoller.OnStatusChange(func(name string, healthy bool, status provider.HealthStatus) {
		if healthy {
			log.Info().Str("provider", name).Msg("provider recovered")
		} else {
			log.Error().Str("provider", name).Str("error", status.Error).Msg("provider degraded")
		}
	})
	healthPoller.Start()

	// Start background model list syncer (T040)
	modelSyncer := provider.NewModelSyncer(registry, log, 5*time.Minute)
	modelSyncer.Start()

	// Graceful shutdown handling
	done := make(chan os.Signal, 1)
	signal.Notify(done, os.Interrupt, syscall.SIGTERM)

	go func() {
		log.Info().Str("addr", cfg.Addr).Msg("gateway listening")
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatal().Err(err).Msg("server failed")
		}
	}()

	<-done
	log.Info().Msg("shutdown signal received")

	// Stop background tasks
	healthPoller.Stop()
	modelSyncer.Stop()
	analyticsPipeline.Stop()
	tracer.Shutdown()

	ctx, cancel := context.WithTimeout(context.Background(), cfg.GracefulTimeout)
	defer cancel()

	if err := srv.Shutdown(ctx); err != nil {
		log.Error().Err(err).Msg("graceful shutdown failed")
	} else {
		log.Info().Msg("gateway stopped gracefully")
	}
}

func registerProviders(cfg *config.Config, registry *provider.Registry, log zerolog.Logger) {
	// Register OpenAI provider if API key is available
	if key := os.Getenv("OPENAI_API_KEY"); key != "" {
		openai := provider.NewOpenAIProvider(provider.ProviderConfig{
			Name:    "openai",
			APIKey:  key,
			Timeout: cfg.ProviderTimeout("openai"),
		})
		registry.Register(openai)
		log.Info().Msg("registered openai provider")
	}

	// Register Anthropic provider if API key is available
	if key := os.Getenv("ANTHROPIC_API_KEY"); key != "" {
		anthropic := provider.NewAnthropicProvider(provider.ProviderConfig{
			Name:    "anthropic",
			APIKey:  key,
			Timeout: cfg.ProviderTimeout("anthropic"),
		})
		registry.Register(anthropic)
		log.Info().Msg("registered anthropic provider")
	}

	// Register Google Gemini provider if API key is available
	if key := os.Getenv("GEMINI_API_KEY"); key != "" {
		gemini := provider.NewGeminiProvider(provider.ProviderConfig{
			Name:    "google",
			APIKey:  key,
			Timeout: cfg.ProviderTimeout("google"),
		})
		registry.Register(gemini)
		log.Info().Msg("registered google gemini provider")
	}

	// Register Azure OpenAI provider if endpoint and key are available
	if endpoint := os.Getenv("AZURE_OPENAI_ENDPOINT"); endpoint != "" {
		if key := os.Getenv("AZURE_OPENAI_KEY"); key != "" {
			azure := provider.NewAzureOpenAIProvider(provider.ProviderConfig{
				Name:    "azure",
				BaseURL: endpoint,
				APIKey:  key,
				Timeout: cfg.ProviderTimeout("azure"),
			})
			registry.Register(azure)
			log.Info().Msg("registered azure openai provider")
		}
	}

	// Register Mistral provider (T034)
	if key := os.Getenv("MISTRAL_API_KEY"); key != "" {
		mistral := provider.NewMistralProvider(provider.ProviderConfig{
			Name:    "mistral",
			APIKey:  key,
			Timeout: cfg.ProviderTimeout("mistral"),
		})
		registry.Register(mistral)
		log.Info().Msg("registered mistral provider")
	}

	// Register Together AI provider (T035)
	if key := os.Getenv("TOGETHER_API_KEY"); key != "" {
		together := provider.NewTogetherProvider(provider.ProviderConfig{
			Name:    "together",
			APIKey:  key,
			Timeout: cfg.ProviderTimeout("together"),
		})
		registry.Register(together)
		log.Info().Msg("registered together ai provider")
	}

	// Register Groq provider (T036)
	if key := os.Getenv("GROQ_API_KEY"); key != "" {
		groq := provider.NewGroqProvider(provider.ProviderConfig{
			Name:    "groq",
			APIKey:  key,
			Timeout: cfg.ProviderTimeout("groq"),
		})
		registry.Register(groq)
		log.Info().Msg("registered groq provider")
	}

	// Register Cohere provider (T033)
	if key := os.Getenv("COHERE_API_KEY"); key != "" {
		cohere := provider.NewCohereProvider(provider.ProviderConfig{
			Name:    "cohere",
			APIKey:  key,
			Timeout: cfg.ProviderTimeout("cohere"),
		})
		registry.Register(cohere)
		log.Info().Msg("registered cohere provider")
	}

	// Register AWS Bedrock provider (T032)
	if accessKey := os.Getenv("AWS_ACCESS_KEY_ID"); accessKey != "" {
		if secretKey := os.Getenv("AWS_SECRET_ACCESS_KEY"); secretKey != "" {
			region := os.Getenv("AWS_REGION")
			if region == "" {
				region = "us-east-1"
			}
			bedrock := provider.NewBedrockProvider(provider.BedrockConfig{
				ProviderConfig: provider.ProviderConfig{
					Name:    "bedrock",
					Timeout: cfg.ProviderTimeout("bedrock"),
				},
				Region:    region,
				AccessKey: accessKey,
				SecretKey: secretKey,
			})
			registry.Register(bedrock)
			log.Info().Str("region", region).Msg("registered aws bedrock provider")
		}
	}

	// Register Ollama self-hosted provider (T037)
	if baseURL := os.Getenv("OLLAMA_BASE_URL"); baseURL != "" {
		ollama := provider.NewOllamaProvider(provider.ProviderConfig{
			Name:    "ollama",
			BaseURL: baseURL,
			Timeout: cfg.ProviderTimeout("ollama"),
		})
		registry.Register(ollama)
		log.Info().Str("url", baseURL).Msg("registered ollama provider")
	}

	// Register vLLM self-hosted provider (T038)
	if baseURL := os.Getenv("VLLM_BASE_URL"); baseURL != "" {
		vllm := provider.NewVLLMProvider(provider.ProviderConfig{
			Name:    "vllm",
			BaseURL: baseURL,
			Timeout: cfg.ProviderTimeout("vllm"),
		})
		registry.Register(vllm)
		log.Info().Str("url", baseURL).Msg("registered vllm provider")
	}

	log.Info().Int("providers", len(registry.List())).Msg("provider registration complete")
}
