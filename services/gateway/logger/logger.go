package logger

import (
    "os"

    "github.com/AlfredDev/alfred/services/gateway/config"
    "github.com/rs/zerolog"
)

// New returns a configured zerolog.Logger
func New(cfg *config.Config) zerolog.Logger {
    out := zerolog.ConsoleWriter{Out: os.Stderr}
    lvl := zerolog.InfoLevel
    if cfg.Env == "development" {
        lvl = zerolog.DebugLevel
    }
    zerolog.SetGlobalLevel(lvl)
    log := zerolog.New(out).With().Timestamp().Logger()
    return log
}
