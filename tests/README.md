# 🧪 Alfred Testing Documentation

**Project:** Alfred — Enterprise AI Control & Economy Platform  
**Purpose:** Unified testing framework for all test types  
**Last Updated:** 2026-02-19  
**Coverage Goal:** 90%+ (Currently: 39%)

See full documentation above for complete testing guide.

This is a consolidated testing structure that replaces the previous split between qa/ and tests/.

## Structure

tests/
├── unit/ - Unit tests (backend & frontend)
├── integration/ - Integration tests  
├── e2e/ - End-to-end tests (JavaScript & Python)
├── performance/ - Performance & load tests
├── security/ - Security tests
├── fixtures/ - Shared test data
├── results/ - Test results & reports
└── scripts/ - Test automation

## Quick Start

pytest tests/unit/ -v              # Unit tests
pytest tests/integration/ -v       # Integration tests
pytest tests/e2e/python/ -v        # E2E (Python)
pytest tests/performance/ -v       # Performance
pytest tests/security/ -v          # Security

## Coverage

pytest tests/ --cov=src/backend/app --cov-report=html

See TEST_INVENTORY.md for complete test list.
