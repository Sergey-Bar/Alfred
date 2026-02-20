## Gateway-specific Makefile
# Targets: build, run, test, lint, tidy

.PHONY: build run test lint tidy vet

build:
	cd services/gateway && go build -o bin/gateway ./...

run:
	cd services/gateway && go run .

test:
	cd services/gateway && go test ./... -v

lint:
	cd services/gateway && golangci-lint run

tidy:
	cd services/gateway && go mod tidy

vet:
	cd services/gateway && go vet ./...
