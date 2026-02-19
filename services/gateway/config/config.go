/*
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L4
Logic:       Comprehensive gateway configuration with per-provider
             timeout, rate limiting, and upstream backend URL.
Root Cause:  Gateway needs full configuration to support proxy,
             auth, rate limiting, and provider routing.
Context:     Extends minimal config to support Sprint tasks T011-T024.
Suitability: L4 model used for security-critical config design.
──────────────────────────────────────────────────────────────
*/

package config

import (
	"os"
	"strconv"
	"time"

	"github.com/joho/godotenv"
)

// Config holds all gateway configuration values.
type Config struct {
	// Server
	Addr            string
	Env             string
	GracefulTimeout time.Duration

	// Database
	DatabaseURL string

	// Redis
	RedisURL string

	// Upstream backend (Python FastAPI)
	BackendURL string

	// Authentication
	APIKeyHeader string

	// Rate limiting
	RateLimitEnabled bool
	RateLimitRPM     int // requests per minute per key
	RateLimitBurst   int

	// Timeouts
	DefaultTimeout   time.Duration
	ProviderTimeouts map[string]time.Duration

	// Body limits
	MaxBodyBytes int64

	// Provider defaults
	DefaultProvider string

	// Logging
	LogLevel string
}

// Load reads configuration from environment variables and optional .env file.
func Load() *Config {
	_ = godotenv.Load()

	gracefulSec := getEnvInt("GATEWAY_GRACEFUL_TIMEOUT_SEC", 15)
	defaultTimeoutSec := getEnvInt("GATEWAY_DEFAULT_TIMEOUT_SEC", 120)

	cfg := &Config{
		Addr:            getEnv("GATEWAY_ADDR", ":8080"),
		Env:             getEnv("ENV", "development"),
		GracefulTimeout: time.Duration(gracefulSec) * time.Second,
		DatabaseURL:     getEnv("DATABASE_URL", "postgres://postgres:postgres@postgres:5432/ao?sslmode=disable"),
		RedisURL:        getEnv("REDIS_URL", "redis://redis:6379"),
		BackendURL:      getEnv("BACKEND_URL", "http://localhost:8000"),
		APIKeyHeader:    getEnv("API_KEY_HEADER", "Authorization"),
		RateLimitEnabled: getEnvBool("RATE_LIMIT_ENABLED", true),
		RateLimitRPM:    getEnvInt("RATE_LIMIT_RPM", 60),
		RateLimitBurst:  getEnvInt("RATE_LIMIT_BURST", 10),
		DefaultTimeout:  time.Duration(defaultTimeoutSec) * time.Second,
		MaxBodyBytes:    int64(getEnvInt("GATEWAY_MAX_BODY_BYTES", 1*1024*1024)),
		DefaultProvider: getEnv("DEFAULT_PROVIDER", "openai"),
		LogLevel:        getEnv("LOG_LEVEL", "info"),
		ProviderTimeouts: map[string]time.Duration{
			"openai":    time.Duration(getEnvInt("PROVIDER_TIMEOUT_OPENAI_SEC", 120)) * time.Second,
			"anthropic": time.Duration(getEnvInt("PROVIDER_TIMEOUT_ANTHROPIC_SEC", 120)) * time.Second,
			"google":    time.Duration(getEnvInt("PROVIDER_TIMEOUT_GOOGLE_SEC", 120)) * time.Second,
			"azure":     time.Duration(getEnvInt("PROVIDER_TIMEOUT_AZURE_SEC", 120)) * time.Second,
			"mistral":   time.Duration(getEnvInt("PROVIDER_TIMEOUT_MISTRAL_SEC", 60)) * time.Second,
			"cohere":    time.Duration(getEnvInt("PROVIDER_TIMEOUT_COHERE_SEC", 60)) * time.Second,
		},
	}
	return cfg
}

// IsDevelopment returns true if running in development mode.
func (c *Config) IsDevelopment() bool {
	return c.Env == "development"
}

// IsProduction returns true if running in production mode.
func (c *Config) IsProduction() bool {
	return c.Env == "production"
}

// ProviderTimeout returns the configured timeout for a given provider.
func (c *Config) ProviderTimeout(provider string) time.Duration {
	if t, ok := c.ProviderTimeouts[provider]; ok {
		return t
	}
	return c.DefaultTimeout
}

func getEnv(key, fallback string) string {
	if v, ok := os.LookupEnv(key); ok {
		return v
	}
	return fallback
}

func getEnvInt(key string, fallback int) int {
	if v, ok := os.LookupEnv(key); ok {
		if i, err := strconv.Atoi(v); err == nil {
			return i
		}
	}
	return fallback
}

func getEnvBool(key string, fallback bool) bool {
	if v, ok := os.LookupEnv(key); ok {
		if b, err := strconv.ParseBool(v); err == nil {
			return b
		}
	}
	return fallback
}
