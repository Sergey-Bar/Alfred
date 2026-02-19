dev:
test:
docker-up:
# [AI GENERATED]
# Model: GitHub Copilot (GPT-4.1)
# Logic: Makefile for backend/frontend install, lint, test, build, DB migration, and Docker orchestration.
# Why: Automates common dev and CI tasks for consistency and speed.
# Root Cause: Manual commands are error-prone and slow down onboarding.
# Context: Used by all devs and CI. Future: add coverage, security, and release targets.
# Model Suitability: Makefile logic is standard; GPT-4.1 is sufficient.
.PHONY: install dev lint format test build docker-up migrate reset-db frontend-install frontend-test

install:
	python -m pip install --upgrade pip
	pip install -r src/backend/requirements/requirements.txt

dev:
	cd src/backend && uvicorn app.main:app --reload

lint:
	ruff check src/backend/
	ruff format --check src/backend/

format:
	ruff format src/backend/

test:
	pytest -v

frontend-install:
	cd src/frontend && npm ci

frontend-test:
	cd src/frontend && npm run test:unit

build:
	docker-compose build

docker-up:
	docker-compose up -d

migrate:
	alembic -c src/backend/config/alembic.ini upgrade head

reset-db:
	rm -f alfred.db || del alfred.db
	alembic -c src/backend/config/alembic.ini downgrade base || true
	alembic -c src/backend/config/alembic.ini upgrade head

# Gateway local targets
.PHONY: build-gateway gateway-run up down logs

build-gateway:
	cd services/gateway && go build -o bin/gateway .

gateway-run:
	cd services/gateway && go run .

up:
	docker-compose up -d --build

down:
	docker-compose down

logs:
	docker-compose logs -f

