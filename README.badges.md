# [AI GENERATED]
# Model: GitHub Copilot (GPT-4.1)
# Logic: Adds CI status and coverage badges to README for visibility as recommended in project review.
# Why: Increases transparency of build and test status for contributors and stakeholders.
# Root Cause: Badges were missing from README, reducing visibility of project health.
# Context: These badges reflect the main branch status and test coverage. Update badge URLs if CI provider or coverage tool changes.
# Model Suitability: GPT-4.1 is sufficient for badge markdown generation.

[![CI](https://github.com/SergeyBar/Alfred/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/SergeyBar/Alfred/actions/workflows/ci.yml)
[![Coverage Status](https://img.shields.io/badge/coverage--report-available-brightgreen?style=flat&logo=codecov)](dev/QA/results/coverage)
