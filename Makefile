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
	pip install -r dev/backend/requirements/requirements.txt

dev:
	uvicorn app.main:app --reload

lint:
	black --check .
	ruff check .
	isort --check-only .

format:
	black .
	ruff format .
	isort .

test:
	pytest -v

frontend-install:
	cd frontend && npm ci

frontend-test:
	cd frontend && npm run test:unit

build:
	docker-compose build

docker-up:
	docker-compose up -d

migrate:
	alembic -c dev/backend/config/alembic.ini upgrade head

reset-db:
	rm -f alfred.db || del alfred.db
	alembic -c dev/backend/config/alembic.ini downgrade base || true
	alembic -c dev/backend/config/alembic.ini upgrade head

minimal:
	@echo "Building minimal artifact in ./dist"
	./scripts/build_minimal.sh dist

