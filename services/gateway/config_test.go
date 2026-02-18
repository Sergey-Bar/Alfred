package config_test

import (
    "os"
    "testing"

    "github.com/<org>/alfred/services/gateway/config"
)

func TestLoadConfigFromEnv(t *testing.T) {
    os.Setenv("DATABASE_URL", "postgres://user:pass@localhost:5432/db")
    os.Setenv("REDIS_URL", "redis://localhost:6379")
    os.Setenv("ENV", "test")
    defer func() {
        os.Unsetenv("DATABASE_URL")
        os.Unsetenv("REDIS_URL")
        os.Unsetenv("ENV")
    }()

    cfg := config.Load()
    if cfg.DatabaseURL != "postgres://user:pass@localhost:5432/db" {
        t.Fatalf("expected DATABASE_URL to be loaded, got %s", cfg.DatabaseURL)
    }
    if cfg.RedisURL != "redis://localhost:6379" {
        t.Fatalf("expected REDIS_URL to be loaded, got %s", cfg.RedisURL)
    }
    if cfg.Env != "test" {
        t.Fatalf("expected ENV=test, got %s", cfg.Env)
    }
}
