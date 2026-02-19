# Alfred Terraform Provider
#
# [AI GENERATED - GOVERNANCE PROTOCOL]
# ──────────────────────────────────────────────────────────────
# Model:       Claude Opus 4.6
# Tier:        L2
# Logic:       Terraform provider for Alfred infrastructure as code.
# Root Cause:  Sprint task T188 — Terraform provider.
# Context:     Enables IaC for Alfred policies, teams, and quotas.
# Suitability: L2 — Standard Terraform provider patterns.
# ──────────────────────────────────────────────────────────────

terraform {
  required_providers {
    alfred = {
      source  = "alfred-ai/alfred"
      version = "~> 1.0"
    }
  }
}

# Provider configuration example
provider "alfred" {
  api_key = var.alfred_api_key  # Or use ALFRED_API_KEY env var
  api_url = var.alfred_api_url  # Optional, defaults to https://api.alfred.ai
}

variable "alfred_api_key" {
  type        = string
  description = "Alfred API key"
  sensitive   = true
}

variable "alfred_api_url" {
  type        = string
  description = "Alfred API URL"
  default     = "https://api.alfred.ai"
}

# ============================================================
# Example: Team with budget allocation
# ============================================================

resource "alfred_team" "engineering" {
  name        = "Engineering"
  description = "Engineering department AI resources"
}

resource "alfred_wallet" "engineering_wallet" {
  owner_id    = alfred_team.engineering.id
  owner_type  = "team"
  hard_limit  = 1000.00
  soft_limit  = 800.00
  currency    = "USD"
}

# ============================================================
# Example: Governance policies
# ============================================================

resource "alfred_policy" "block_expensive_models" {
  name        = "Block Expensive Models for Interns"
  description = "Prevent intern accounts from using expensive models"
  action      = "deny"
  priority    = 10
  is_active   = true
  
  rules = {
    conditions = [
      {
        field    = "user.role"
        operator = "equals"
        value    = "intern"
      },
      {
        field    = "request.model"
        operator = "in"
        value    = ["gpt-4o", "claude-3-opus"]
      }
    ]
    logic = "AND"
  }
}

resource "alfred_policy" "daily_limit" {
  name        = "Daily Spend Limit"
  description = "Alert when daily spend exceeds threshold"
  action      = "warn"
  priority    = 5
  is_active   = true
  
  rules = {
    conditions = [
      {
        field    = "user.daily_spend"
        operator = "greater_than"
        value    = 50.00
      }
    ]
  }
}

# ============================================================
# Example: API key for CI/CD
# ============================================================

resource "alfred_api_key" "ci_pipeline" {
  name   = "GitHub Actions CI"
  scopes = ["read", "completions"]
  
  expires_in_days = 90
}

output "ci_api_key_prefix" {
  value       = alfred_api_key.ci_pipeline.key_prefix
  description = "Prefix of the CI API key (for identification)"
}

# ============================================================
# Example: Routing configuration
# ============================================================

resource "alfred_routing_rule" "cost_optimization" {
  name        = "Route simple queries to cheaper models"
  description = "Use GPT-4o-mini for simple classification tasks"
  priority    = 100
  is_active   = true
  
  conditions = [
    {
      field    = "request.intent"
      operator = "in"
      value    = ["classification", "extraction"]
    },
    {
      field    = "request.estimated_complexity"
      operator = "less_than"
      value    = 0.3
    }
  ]
  
  action = {
    type  = "route"
    model = "gpt-4o-mini"
  }
}

# ============================================================
# Data sources
# ============================================================

data "alfred_providers" "all" {}

output "available_providers" {
  value = data.alfred_providers.all.providers[*].name
}

data "alfred_usage" "current_month" {
  start_date = formatdate("YYYY-MM-01", timestamp())
  end_date   = formatdate("YYYY-MM-DD", timestamp())
}

output "monthly_cost" {
  value = data.alfred_usage.current_month.total_cost
}
