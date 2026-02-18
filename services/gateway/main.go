package main

import (
	"net/http"
	"os"

	"github.com/<org>/alfred/services/gateway/config"
	"github.com/<org>/alfred/services/gateway/logger"
	"github.com/<org>/alfred/services/gateway/redisclient"
	"github.com/<org>/alfred/services/gateway/router"
)

func main() {
	cfg := config.Load()
	log := logger.New(cfg)

	// Initialize Redis (example)
	rc, err := redisclient.New(cfg)
	if err != nil {
		log.Error().Err(err).Msg("redis init failed")
	} else {
		if err := rc.Ping(); err != nil {
			log.Error().Err(err).Msg("redis ping failed")
		} else {
			log.Info().Msg("redis connected")
		}
	}

	r := router.NewRouter(log)

	addr := os.Getenv("GATEWAY_ADDR")
	if addr == "" {
		addr = ":8080"
	}

	log.Info().Str("addr", addr).Msg("gateway starting")
	if err := http.ListenAndServe(addr, r); err != nil {
		log.Fatal().Err(err).Msg("server failed")
	}
}
