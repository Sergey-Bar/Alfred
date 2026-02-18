package integration_test

import (
	"os"
	"testing"
)

// Integration tests require external services and are skipped by default.
// To run them locally set RUN_GATEWAY_INTEGRATION=1 and start postgres+redis via docker-compose.
func TestIntegrationSkipByDefault(t *testing.T) {
	if os.Getenv("RUN_GATEWAY_INTEGRATION") != "1" {
		t.Skip("integration tests skipped; set RUN_GATEWAY_INTEGRATION=1 to run")
	}
	// placeholder: add integration tests that exercise migrations, Redis, and HTTP endpoints.
}
