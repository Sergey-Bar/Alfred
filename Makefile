# Alfred - Makefile
# Common development tasks: install, lint, test, build, docker, and migrations.

.PHONY: install dev lint format test build docker-up migrate reset-db frontend-install frontend-test

install:
	python -m pip install --upgrade pip
	pip install -r services/backend/requirements/requirements.txt

dev:
	cd services/backend && uvicorn app.main:app --reload

lint:
	ruff check services/backend/
	ruff format --check services/backend/

format:
	ruff format services/backend/

test:
	pytest -v

frontend-install:
	cd services/frontend && npm ci

frontend-test:
	cd services/frontend && npm run test:unit

build:
	docker-compose build

docker-up:
	docker-compose up -d

migrate:
	alembic -c services/backend/config/alembic.ini upgrade head

reset-db:
	rm -f alfred.db || del alfred.db
	alembic -c services/backend/config/alembic.ini downgrade base || true
	alembic -c services/backend/config/alembic.ini upgrade head

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

