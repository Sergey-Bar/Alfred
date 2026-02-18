package config

import (
    "os"

    "github.com/joho/godotenv"
)

type Config struct {
    DatabaseURL string
    RedisURL    string
    Env         string
}

// Load reads configuration from environment variables and optional .env file
func Load() *Config {
    // try load .env if present
    _ = godotenv.Load()

    cfg := &Config{
        DatabaseURL: getEnv("DATABASE_URL", "postgres://postgres:postgres@postgres:5432/ao?sslmode=disable"),
        RedisURL:    getEnv("REDIS_URL", "redis://redis:6379"),
        Env:         getEnv("ENV", "development"),
    }
    return cfg
}

func getEnv(key, fallback string) string {
    if v, ok := os.LookupEnv(key); ok {
        return v
    }
    return fallback
}
