# DevOps Script Documentation for Onboarding

This document lists and describes all DevOps scripts available in the project (see devops/scripts/). Each script is executable and intended to automate key setup, security, and operational tasks.

## Script Index

- **add_in_app_onboarding.sh**: Adds in-app onboarding and tooltips for new users in the frontend.
- **add_localization_support.sh**: Sets up localization/i18n support for global teams in the frontend.
- **add_onboarding_scripts.sh**: Generates onboarding scripts and a first PR guide for new contributors.
- **expand_storybook_coverage.sh**: Expands Storybook coverage and adds interactive documentation for frontend components.
- **implement_a11y_testing.sh**: Implements accessibility (a11y) testing using axe-core CLI and generates reports.
- **implement_audit_logging.sh**: Sets up audit logging for admin and sensitive actions in the backend.
- **optimize_database_jobs.sh**: Profiles and optimizes database queries and background jobs, with recommendations.
- **penetration_testing_plan.md**: Outlines the plan and schedule for regular penetration testing.
- **secret_rotation_plan.md**: Documents the plan for automated secret and credential rotation.
- **setup_autoscaling.sh**: Configures autoscaling policies for Kubernetes deployments.
- **setup_docker_compose_env.sh**: Sets up a local development environment using Docker Compose.
- **setup_secret_rotation.sh**: Automates secret and credential rotation using HashiCorp Vault.
- **setup_sharding_multi_region.sh**: Implements horizontal sharding and multi-region support for databases.

## Usage

All scripts are located in `devops/scripts/` and are executable. Run with:

```bash
./devops/scripts/<script_name>.sh
```

For onboarding, see also the generated `onboarding.sh` and `FIRST_PR_GUIDE.md` in the project root.

---

For more details, see each script's comments and the project onboarding checklist.
