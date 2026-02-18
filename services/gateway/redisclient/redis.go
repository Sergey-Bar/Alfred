package redisclient

import (
    "context"
    "fmt"
    "time"

    "github.com/<org>/alfred/services/gateway/config"
    "github.com/redis/go-redis/v9"
)

type Client struct {
    c *redis.Client
}

// New creates a Redis client from the provided config. Returns an error
// if the Redis URL cannot be parsed.
func New(cfg *config.Config) (*Client, error) {
    opt, err := redis.ParseURL(cfg.RedisURL)
    if err != nil {
        return nil, fmt.Errorf("invalid REDIS_URL: %w", err)
    }
    r := redis.NewClient(opt)
    return &Client{c: r}, nil
}

func (r *Client) Ping() error {
    ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
    defer cancel()
    return r.c.Ping(ctx).Err()
}
