#!/usr/bin/env python3
"""Local test script to call enqueue_notification without Redis.

This uses the in-repo modules by adding `backend` to `sys.path` so
`app.notifications.enqueue_notification` can be imported and executed.
"""
import sys
from pathlib import Path

# Ensure we can import the `app` package from the repository `backend` directory
project_root = Path(__file__).resolve().parents[2]
backend_dir = project_root / "backend"
sys.path.insert(0, str(backend_dir))

from app.notifications import enqueue_notification

def main():
    payload = {
        "user_id": "local-test",
        "user_name": "Local Tester",
        "user_email": "local@test.example",
        "requested_credits": 3.5,
        "reason": "local integration test",
    }

    print("Calling enqueue_notification('approval_requested', payload)")
    enqueue_notification("approval_requested", payload)
    print("Done — if Redis is not configured, this ran in-process fallback.")


if __name__ == '__main__':
    main()
