"""
Alfred Outbound Notification Dispatcher

[ARCHITECTURAL ROLE]
This module serves as the primary gateway for enqueuing outbound alerts (Slack, 
Teams, Email). It provides a decoupled architecture where the API remains 
high-performance by offloading potentially high-latency network calls (webhooks) 
 to a background worker pool using Redis and RQ (Redis Queue).

[RESILIENCE STRATEGY]
Alfred implements a "Degraded Graceful Fallback":
1. Preferred: Enqueue into Redis for background worker 'consumption'.
2. Fallback: If Redis/RQ is missing or unreachable, execution happens 
   in-process via an async background task to ensure the alert is still sent.
"""

import logging
import os

# Internal logger initialization for diagnostic context
log = logging.getLogger("alfred.notifications")


def _get_redis_conn():
    """
    Establish a connection to the organizational Redis layer.
    
    Returns:
    - redis.Redis: Active connection.
    - None: If Redis is unavailable or misconfigured.
    """
    url = os.getenv("REDIS_URL") or os.getenv("REDIS_URL_LOCAL")
    if not url:
        return None
    try:
        from redis import Redis
    except ImportError:
        log.warning("Dependency Missing: 'redis-py' not detected. Background queuing disabled.")
        return None

    try:
        return Redis.from_url(url, socket_timeout=5)
    except Exception:
        log.warning("Connectivity Failure: Unable to bind to Redis at specified URL.")
        return None


def enqueue_notification(task_name: str, payload: dict):
    """
    Fire-and-Forget Notification Router.
    
    Optimistically attempts to offload work to a distributed queue.
    If the queueing infrastructure is unavailable, it gracefully 
    falls back to localized in-process execution.
    
    Arguments:
    - task_name: Canonical identifier (e.g., 'quota_exceeded', 'approval_requested').
    - payload: Serialized parameters required by the notification template.
    """
    conn = _get_redis_conn()
    
    # --- PHASE 1: Attempt Distributed Queuing (RQ) ---
    if conn:
        try:
            from rq import Queue
            q = Queue("default", connection=conn)
            # Enqueue to the 'workers' module to satisfy module resolution in separate processes
            q.enqueue("backend.app.workers.process_task", task_name, payload, job_timeout=300)
            return
        except ImportError:
            log.warning("Dependency Missing: 'rq' not detected. Redirecting to in-process execution.")
        except Exception:
            log.exception("Infrastructure Error: Redis enqueuing failed.")

    # --- PHASE 2: In-Process Fallback (Best Effort) ---
    # This ensures that even if Redis is down, critical financial alerts 
    # are still attempted before the request cycle terminates.
    log.info(f"Fallback Execution: Routing '{task_name}' through local task runner.")
    try:
        import asyncio
        from .integrations import manager as integrations_manager

        # Dynamic target resolution based on task name
        fn = getattr(integrations_manager, f"emit_{task_name}", None)
        if fn is None:
            log.error(f"Routing Error: No emitter logic found for '{task_name}'.")
            return
            
        coro = fn(**payload)
        try:
            # Fire-and-forget within the existing FastAPI event loop
            asyncio.create_task(coro)
        except RuntimeError:
            # Fallback for environments lacking an active event loop (CLI/Scripts)
            asyncio.run(coro)
            
    except Exception:
        log.exception(f"Critical Failure: Notification '{task_name}' failed both queue and fallback paths.")

