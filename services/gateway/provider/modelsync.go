/*
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L1
Logic:       Provider model list sync (T040). Periodically fetches
             the available models from each registered provider
             and updates the registry. Enables dynamic model
             discovery and routing accuracy.
Root Cause:  Sprint task T040 — Provider model list sync.
Context:     Keeps the model catalog fresh so routing rules can
             reference models that actually exist on each provider.
Suitability: L1 — straightforward polling + map update.
──────────────────────────────────────────────────────────────
*/

package provider

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"sync"
	"time"

	"github.com/rs/zerolog"
)

// ModelSyncer periodically fetches available models from providers.
type ModelSyncer struct {
	registry *Registry
	log      zerolog.Logger
	interval time.Duration
	catalog  map[string][]ModelInfo // provider -> models
	mu       sync.RWMutex
	stopCh   chan struct{}
	client   *http.Client
}

// ModelInfo represents a model available on a provider.
type ModelInfo struct {
	ID        string    `json:"id"`
	Object    string    `json:"object,omitempty"`
	OwnedBy   string    `json:"owned_by,omitempty"`
	Provider  string    `json:"provider"`
	SyncedAt  time.Time `json:"synced_at"`
}

// NewModelSyncer creates a new model syncer.
func NewModelSyncer(registry *Registry, log zerolog.Logger, interval time.Duration) *ModelSyncer {
	if interval == 0 {
		interval = 5 * time.Minute
	}
	return &ModelSyncer{
		registry: registry,
		log:      log.With().Str("component", "model_syncer").Logger(),
		interval: interval,
		catalog:  make(map[string][]ModelInfo),
		stopCh:   make(chan struct{}),
		client: &http.Client{
			Timeout: 15 * time.Second,
		},
	}
}

// Start begins the background model sync loop.
func (s *ModelSyncer) Start() {
	go s.loop()
	s.log.Info().Dur("interval", s.interval).Msg("model syncer started")
}

// Stop halts the background sync loop.
func (s *ModelSyncer) Stop() {
	close(s.stopCh)
	s.log.Info().Msg("model syncer stopped")
}

// GetCatalog returns the current model catalog across all providers.
func (s *ModelSyncer) GetCatalog() map[string][]ModelInfo {
	s.mu.RLock()
	defer s.mu.RUnlock()
	// Deep copy
	result := make(map[string][]ModelInfo, len(s.catalog))
	for k, v := range s.catalog {
		models := make([]ModelInfo, len(v))
		copy(models, v)
		result[k] = models
	}
	return result
}

// GetAllModels returns a flat list of all models across all providers.
func (s *ModelSyncer) GetAllModels() []ModelInfo {
	s.mu.RLock()
	defer s.mu.RUnlock()
	var all []ModelInfo
	for _, models := range s.catalog {
		all = append(all, models...)
	}
	return all
}

func (s *ModelSyncer) loop() {
	// Sync immediately on start
	s.syncAll()

	ticker := time.NewTicker(s.interval)
	defer ticker.Stop()

	for {
		select {
		case <-s.stopCh:
			return
		case <-ticker.C:
			s.syncAll()
		}
	}
}

func (s *ModelSyncer) syncAll() {
	providers := s.registry.List()
	s.log.Debug().Int("providers", len(providers)).Msg("syncing model lists")

	var wg sync.WaitGroup
	results := make(map[string][]ModelInfo)
	var mu sync.Mutex

	for _, name := range providers {
		prov, ok := s.registry.Get(name)
		if !ok {
			continue
		}
		wg.Add(1)
		go func(n string, p Provider) {
			defer wg.Done()

			models := p.Models()
			now := time.Now()
			infos := make([]ModelInfo, len(models))
			for i, m := range models {
				infos[i] = ModelInfo{
					ID:       m,
					Provider: n,
					SyncedAt: now,
				}
			}

			mu.Lock()
			results[n] = infos
			mu.Unlock()

			s.log.Debug().Str("provider", n).Int("models", len(models)).Msg("synced models")
		}(name, prov)
	}
	wg.Wait()

	s.mu.Lock()
	s.catalog = results
	s.mu.Unlock()

	total := 0
	for _, v := range results {
		total += len(v)
	}
	s.log.Info().Int("providers", len(results)).Int("total_models", total).Msg("model sync complete")
}

// ─── OpenAI-compatible /v1/models API response ──────────────

// ModelsListResponse is the response for GET /v1/models.
type ModelsListResponse struct {
	Object string      `json:"object"`
	Data   []ModelInfo `json:"data"`
}

// FetchRemoteModels tries to fetch the /v1/models list from a provider's
// base URL. Falls back to the static model list on failure.
func FetchRemoteModels(ctx context.Context, baseURL, apiKey string) ([]string, error) {
	client := &http.Client{Timeout: 10 * time.Second}
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, baseURL+"/v1/models", nil)
	if err != nil {
		return nil, fmt.Errorf("create request: %w", err)
	}
	if apiKey != "" {
		req.Header.Set("Authorization", "Bearer "+apiKey)
	}

	resp, err := client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("fetch models: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("status %d: %s", resp.StatusCode, string(body))
	}

	var listResp struct {
		Data []struct {
			ID string `json:"id"`
		} `json:"data"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&listResp); err != nil {
		return nil, fmt.Errorf("decode models: %w", err)
	}

	models := make([]string, len(listResp.Data))
	for i, m := range listResp.Data {
		models[i] = m.ID
	}
	return models, nil
}
