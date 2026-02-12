# Changelog

All notable changes to this project will be documented in this file.

## [0.2.0] - 2026-02-12

### Added
- **Notification System**: Implemented asynchronous notification queue using Redis and RQ, with automatic in-process fallback for development.
- **Audit Logging**: Added comprehensive audit logging for all admin actions (user/team management), stored in `audit_logs` table.
- **Security**: Added `gitleaks` secret scanning to CI, configured `securityHeaders`, and implemented request rate limiting.
- **DevOps**: Added Helm templates for Redis and Worker services; consolidated CI workflow to include linting, testing, and security scans.
- **Monitoring**: Added `/health` and `/ready` endpoints; implemented structured logging with request IDs.
- **Playbooks**: Added `dev/support/PLAYBOOK.md` with detailed operational runbooks and `dev/devops/README.md`.

### Fixed
- **Timezones**: Migrated all datetime fields to use timezone-aware UTC timestamps (`datetime.now(timezone.utc)`).
- **Frontend**: Replaced silent demo fallbacks with explicit error banners and "Contact Support" flows in Dashboard, Transfers, and Teams pages.
- **Database**: Added indexes for `request_logs.created_at` and `token_transfers.created_at` to improve query performance.
- **Testing**: Fixed backend test suite reliability and time-dependent test failures.

### Changed
- Refactored `backend/app/notifications.py` to be robust against missing dependencies.
- Updated `docker-compose.yml` (profile: `with-cache`) to support full stack validation locally.
- Removed legacy role-specific documentation files as tasks were completed.

## [0.1.0] - 2024-01-15
- Initial repository scaffold and core features

