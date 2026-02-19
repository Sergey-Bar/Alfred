/*
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L4
Logic:       HashiCorp Vault integration for provider key storage,
             rotation, and dynamic secrets. mTLS cert management.
             BYOK encryption key hierarchy.
Root Cause:  Sprint tasks T192-T194 — Security hardening.
Context:     Per PRD Section 14, all keys in Vault, mTLS between
             services, BYOK for tenant isolation.
Suitability: L4 — security-critical infrastructure.
──────────────────────────────────────────────────────────────
*/

package security

import (
	"context"
	"crypto/aes"
	"crypto/cipher"
	"crypto/rand"
	"crypto/tls"
	"crypto/x509"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"strings"
	"sync"
	"time"
)

// ─── T192: HashiCorp Vault Integration ──────────────────────

type VaultConfig struct {
	Enabled    bool          `json:"enabled"`
	Address    string        `json:"address"` // e.g., "https://vault.internal:8200"
	Token      string        `json:"-"`       // Never log
	MountPath  string        `json:"mount_path"` // e.g., "secret"
	Namespace  string        `json:"namespace"`
	RenewTTL   time.Duration `json:"renew_ttl"`
	MaxRetries int           `json:"max_retries"`
}

type VaultClient struct {
	config VaultConfig
	client *http.Client
	mu     sync.RWMutex
	cache  map[string]*cachedSecret
}

type cachedSecret struct {
	Value     map[string]string
	ExpiresAt time.Time
}

func NewVaultClient(config VaultConfig) *VaultClient {
	if config.MountPath == "" {
		config.MountPath = "secret"
	}
	if config.MaxRetries == 0 {
		config.MaxRetries = 3
	}
	if config.RenewTTL == 0 {
		config.RenewTTL = 5 * time.Minute
	}

	return &VaultClient{
		config: config,
		client: &http.Client{Timeout: 10 * time.Second},
		cache:  make(map[string]*cachedSecret),
	}
}

// GetProviderKey retrieves a provider API key from Vault.
func (v *VaultClient) GetProviderKey(ctx context.Context, provider string) (string, error) {
	if !v.config.Enabled {
		// Fallback to env var
		envKey := fmt.Sprintf("%s_API_KEY", strings.ToUpper(provider))
		if key := os.Getenv(envKey); key != "" {
			return key, nil
		}
		return "", fmt.Errorf("vault disabled and no env var %s", envKey)
	}

	path := fmt.Sprintf("providers/%s", provider)

	// Check cache
	v.mu.RLock()
	if cached, ok := v.cache[path]; ok && time.Now().Before(cached.ExpiresAt) {
		v.mu.RUnlock()
		return cached.Value["api_key"], nil
	}
	v.mu.RUnlock()

	// Fetch from Vault
	secret, err := v.readSecret(ctx, path)
	if err != nil {
		return "", fmt.Errorf("read provider key: %w", err)
	}

	apiKey, ok := secret["api_key"]
	if !ok {
		return "", fmt.Errorf("no api_key field in vault path %s", path)
	}

	// Cache
	v.mu.Lock()
	v.cache[path] = &cachedSecret{
		Value:     secret,
		ExpiresAt: time.Now().Add(v.config.RenewTTL),
	}
	v.mu.Unlock()

	return apiKey, nil
}

// WriteProviderKey stores a provider API key in Vault.
func (v *VaultClient) WriteProviderKey(ctx context.Context, provider, apiKey string) error {
	path := fmt.Sprintf("providers/%s", provider)
	data := map[string]string{"api_key": apiKey}
	return v.writeSecret(ctx, path, data)
}

// RotateProviderKey replaces the key and returns the new one.
func (v *VaultClient) RotateProviderKey(ctx context.Context, provider, newKey string) error {
	if err := v.WriteProviderKey(ctx, provider, newKey); err != nil {
		return fmt.Errorf("rotate key: %w", err)
	}

	// Invalidate cache
	v.mu.Lock()
	path := fmt.Sprintf("providers/%s", provider)
	delete(v.cache, path)
	v.mu.Unlock()

	return nil
}

// ListProviders returns all stored provider names.
func (v *VaultClient) ListProviders(ctx context.Context) ([]string, error) {
	if !v.config.Enabled {
		return nil, fmt.Errorf("vault not enabled")
	}

	url := fmt.Sprintf("%s/v1/%s/metadata/providers?list=true", v.config.Address, v.config.MountPath)
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
	if err != nil {
		return nil, err
	}
	req.Header.Set("X-Vault-Token", v.config.Token)
	if v.config.Namespace != "" {
		req.Header.Set("X-Vault-Namespace", v.config.Namespace)
	}

	resp, err := v.client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("vault list: %w", err)
	}
	defer resp.Body.Close()

	var result struct {
		Data struct {
			Keys []string `json:"keys"`
		} `json:"data"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, fmt.Errorf("decode vault list: %w", err)
	}
	return result.Data.Keys, nil
}

func (v *VaultClient) readSecret(ctx context.Context, path string) (map[string]string, error) {
	url := fmt.Sprintf("%s/v1/%s/data/%s", v.config.Address, v.config.MountPath, path)

	var lastErr error
	for attempt := 0; attempt <= v.config.MaxRetries; attempt++ {
		req, err := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
		if err != nil {
			return nil, err
		}
		req.Header.Set("X-Vault-Token", v.config.Token)
		if v.config.Namespace != "" {
			req.Header.Set("X-Vault-Namespace", v.config.Namespace)
		}

		resp, err := v.client.Do(req)
		if err != nil {
			lastErr = err
			time.Sleep(time.Duration(attempt+1) * 100 * time.Millisecond)
			continue
		}
		defer resp.Body.Close()

		if resp.StatusCode == http.StatusNotFound {
			return nil, fmt.Errorf("secret not found: %s", path)
		}
		if resp.StatusCode != http.StatusOK {
			body, _ := io.ReadAll(resp.Body)
			return nil, fmt.Errorf("vault error (%d): %s", resp.StatusCode, string(body))
		}

		var result struct {
			Data struct {
				Data map[string]string `json:"data"`
			} `json:"data"`
		}
		if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
			return nil, fmt.Errorf("decode secret: %w", err)
		}
		return result.Data.Data, nil
	}

	return nil, fmt.Errorf("vault read failed after %d retries: %w", v.config.MaxRetries, lastErr)
}

func (v *VaultClient) writeSecret(ctx context.Context, path string, data map[string]string) error {
	url := fmt.Sprintf("%s/v1/%s/data/%s", v.config.Address, v.config.MountPath, path)

	payload := map[string]interface{}{
		"data": data,
	}
	body, err := json.Marshal(payload)
	if err != nil {
		return err
	}

	req, err := http.NewRequestWithContext(ctx, http.MethodPost, url, strings.NewReader(string(body)))
	if err != nil {
		return err
	}
	req.Header.Set("X-Vault-Token", v.config.Token)
	req.Header.Set("Content-Type", "application/json")
	if v.config.Namespace != "" {
		req.Header.Set("X-Vault-Namespace", v.config.Namespace)
	}

	resp, err := v.client.Do(req)
	if err != nil {
		return fmt.Errorf("vault write: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode >= 400 {
		respBody, _ := io.ReadAll(resp.Body)
		return fmt.Errorf("vault write error (%d): %s", resp.StatusCode, string(respBody))
	}
	return nil
}

// InvalidateCache clears all cached secrets.
func (v *VaultClient) InvalidateCache() {
	v.mu.Lock()
	defer v.mu.Unlock()
	v.cache = make(map[string]*cachedSecret)
}

// ─── T193: mTLS Between Internal Services ───────────────────

type MTLSConfig struct {
	Enabled    bool   `json:"enabled"`
	CertFile   string `json:"cert_file"`
	KeyFile    string `json:"key_file"`
	CAFile     string `json:"ca_file"`
	ServerName string `json:"server_name"`
}

// NewMTLSTransport creates an HTTP transport with mutual TLS.
func NewMTLSTransport(config MTLSConfig) (*http.Transport, error) {
	if !config.Enabled {
		return http.DefaultTransport.(*http.Transport).Clone(), nil
	}

	// Load client cert
	cert, err := tls.LoadX509KeyPair(config.CertFile, config.KeyFile)
	if err != nil {
		return nil, fmt.Errorf("load client cert: %w", err)
	}

	// Load CA cert
	caCert, err := os.ReadFile(config.CAFile)
	if err != nil {
		return nil, fmt.Errorf("load CA cert: %w", err)
	}

	caCertPool := x509.NewCertPool()
	if !caCertPool.AppendCertsFromPEM(caCert) {
		return nil, fmt.Errorf("failed to append CA cert")
	}

	tlsConfig := &tls.Config{
		Certificates: []tls.Certificate{cert},
		RootCAs:      caCertPool,
		MinVersion:   tls.VersionTLS13,
	}
	if config.ServerName != "" {
		tlsConfig.ServerName = config.ServerName
	}

	return &http.Transport{
		TLSClientConfig: tlsConfig,
	}, nil
}

// NewMTLSTLSConfig creates a TLS config for an HTTPS server with client cert verification.
func NewMTLSTLSConfig(config MTLSConfig) (*tls.Config, error) {
	if !config.Enabled {
		return nil, nil
	}

	cert, err := tls.LoadX509KeyPair(config.CertFile, config.KeyFile)
	if err != nil {
		return nil, fmt.Errorf("load server cert: %w", err)
	}

	caCert, err := os.ReadFile(config.CAFile)
	if err != nil {
		return nil, fmt.Errorf("load CA cert: %w", err)
	}

	caCertPool := x509.NewCertPool()
	if !caCertPool.AppendCertsFromPEM(caCert) {
		return nil, fmt.Errorf("failed to append CA cert")
	}

	return &tls.Config{
		Certificates: []tls.Certificate{cert},
		ClientAuth:   tls.RequireAndVerifyClientCert,
		ClientCAs:    caCertPool,
		MinVersion:   tls.VersionTLS13,
	}, nil
}

// ─── T194: BYOK Encryption ─────────────────────────────────

type BYOKConfig struct {
	Enabled    bool   `json:"enabled"`
	MasterKey  string `json:"-"` // base64-encoded 256-bit key
	KeySource  string `json:"key_source"` // "env", "vault", "kms"
}

type BYOKEncryptor struct {
	config    BYOKConfig
	masterKey []byte
	mu        sync.RWMutex
	dekCache  map[string][]byte // org_id -> DEK
}

func NewBYOKEncryptor(config BYOKConfig) (*BYOKEncryptor, error) {
	e := &BYOKEncryptor{
		config:   config,
		dekCache: make(map[string][]byte),
	}

	if config.Enabled && config.MasterKey != "" {
		key, err := base64.StdEncoding.DecodeString(config.MasterKey)
		if err != nil {
			return nil, fmt.Errorf("decode master key: %w", err)
		}
		if len(key) != 32 {
			return nil, fmt.Errorf("master key must be 256 bits (32 bytes), got %d", len(key))
		}
		e.masterKey = key
	}

	return e, nil
}

// GenerateDEK creates a new data encryption key for an org, encrypted with the master key.
func (e *BYOKEncryptor) GenerateDEK(orgID string) (encryptedDEK string, err error) {
	// Generate random 256-bit DEK
	dek := make([]byte, 32)
	if _, err := rand.Read(dek); err != nil {
		return "", fmt.Errorf("generate DEK: %w", err)
	}

	// Encrypt DEK with master key
	block, err := aes.NewCipher(e.masterKey)
	if err != nil {
		return "", fmt.Errorf("create cipher: %w", err)
	}

	gcm, err := cipher.NewGCM(block)
	if err != nil {
		return "", fmt.Errorf("create GCM: %w", err)
	}

	nonce := make([]byte, gcm.NonceSize())
	if _, err := rand.Read(nonce); err != nil {
		return "", fmt.Errorf("generate nonce: %w", err)
	}

	encDEK := gcm.Seal(nonce, nonce, dek, []byte(orgID))

	// Cache the plaintext DEK
	e.mu.Lock()
	e.dekCache[orgID] = dek
	e.mu.Unlock()

	return base64.StdEncoding.EncodeToString(encDEK), nil
}

// Encrypt encrypts data using the org's DEK.
func (e *BYOKEncryptor) Encrypt(orgID string, plaintext []byte) (string, error) {
	dek, err := e.getDEK(orgID)
	if err != nil {
		return "", err
	}

	block, err := aes.NewCipher(dek)
	if err != nil {
		return "", fmt.Errorf("create cipher: %w", err)
	}

	gcm, err := cipher.NewGCM(block)
	if err != nil {
		return "", fmt.Errorf("create GCM: %w", err)
	}

	nonce := make([]byte, gcm.NonceSize())
	if _, err := rand.Read(nonce); err != nil {
		return "", fmt.Errorf("generate nonce: %w", err)
	}

	ciphertext := gcm.Seal(nonce, nonce, plaintext, nil)
	return base64.StdEncoding.EncodeToString(ciphertext), nil
}

// Decrypt decrypts data using the org's DEK.
func (e *BYOKEncryptor) Decrypt(orgID string, ciphertextB64 string) ([]byte, error) {
	dek, err := e.getDEK(orgID)
	if err != nil {
		return nil, err
	}

	ciphertext, err := base64.StdEncoding.DecodeString(ciphertextB64)
	if err != nil {
		return nil, fmt.Errorf("decode ciphertext: %w", err)
	}

	block, err := aes.NewCipher(dek)
	if err != nil {
		return nil, fmt.Errorf("create cipher: %w", err)
	}

	gcm, err := cipher.NewGCM(block)
	if err != nil {
		return nil, fmt.Errorf("create GCM: %w", err)
	}

	nonceSize := gcm.NonceSize()
	if len(ciphertext) < nonceSize {
		return nil, fmt.Errorf("ciphertext too short")
	}

	nonce, ciphertext := ciphertext[:nonceSize], ciphertext[nonceSize:]
	return gcm.Open(nil, nonce, ciphertext, nil)
}

func (e *BYOKEncryptor) getDEK(orgID string) ([]byte, error) {
	e.mu.RLock()
	dek, ok := e.dekCache[orgID]
	e.mu.RUnlock()

	if ok {
		return dek, nil
	}

	return nil, fmt.Errorf("DEK not found for org %s — call GenerateDEK or LoadDEK first", orgID)
}

// LoadDEK decrypts and caches an org's DEK from its encrypted form.
func (e *BYOKEncryptor) LoadDEK(orgID, encryptedDEKB64 string) error {
	encDEK, err := base64.StdEncoding.DecodeString(encryptedDEKB64)
	if err != nil {
		return fmt.Errorf("decode encrypted DEK: %w", err)
	}

	block, err := aes.NewCipher(e.masterKey)
	if err != nil {
		return fmt.Errorf("create cipher: %w", err)
	}

	gcm, err := cipher.NewGCM(block)
	if err != nil {
		return fmt.Errorf("create GCM: %w", err)
	}

	nonceSize := gcm.NonceSize()
	if len(encDEK) < nonceSize {
		return fmt.Errorf("encrypted DEK too short")
	}

	nonce, ciphertext := encDEK[:nonceSize], encDEK[nonceSize:]
	dek, err := gcm.Open(nil, nonce, ciphertext, []byte(orgID))
	if err != nil {
		return fmt.Errorf("decrypt DEK: %w", err)
	}

	e.mu.Lock()
	e.dekCache[orgID] = dek
	e.mu.Unlock()

	return nil
}

// ─── T195: Data Residency Routing Enforcement ───────────────

type ResidencyConfig struct {
	OrgRegions      map[string]string   `json:"org_regions"`       // org_id -> region
	ProviderRegions map[string][]string `json:"provider_regions"`  // provider -> allowed regions
}

type ResidencyEnforcer struct {
	mu     sync.RWMutex
	config ResidencyConfig
}

func NewResidencyEnforcer(config ResidencyConfig) *ResidencyEnforcer {
	return &ResidencyEnforcer{config: config}
}

// IsAllowed checks if a provider can serve a request for the given org.
func (r *ResidencyEnforcer) IsAllowed(orgID, provider string) (bool, string) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	orgRegion, ok := r.config.OrgRegions[orgID]
	if !ok {
		return true, "" // No restriction
	}

	providerRegions, ok := r.config.ProviderRegions[provider]
	if !ok {
		return false, fmt.Sprintf("provider %s has no region config", provider)
	}

	for _, region := range providerRegions {
		if region == orgRegion || region == "global" {
			return true, ""
		}
	}

	return false, fmt.Sprintf("provider %s not available in org region %s", provider, orgRegion)
}

// FilterProviders returns only providers allowed for the given org's region.
func (r *ResidencyEnforcer) FilterProviders(orgID string, providers []string) []string {
	r.mu.RLock()
	defer r.mu.RUnlock()

	orgRegion, ok := r.config.OrgRegions[orgID]
	if !ok {
		return providers // No restriction
	}

	var allowed []string
	for _, p := range providers {
		regions := r.config.ProviderRegions[p]
		for _, region := range regions {
			if region == orgRegion || region == "global" {
				allowed = append(allowed, p)
				break
			}
		}
	}
	return allowed
}

func (r *ResidencyEnforcer) SetOrgRegion(orgID, region string) {
	r.mu.Lock()
	defer r.mu.Unlock()
	r.config.OrgRegions[orgID] = region
}
