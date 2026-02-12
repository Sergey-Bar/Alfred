import os
import logging
from typing import Optional



def _get_redis_conn():
    url = os.getenv("REDIS_URL") or os.getenv("REDIS_URL_LOCAL")
    if not url:
        return None
    try:
        from redis import Redis
    except Exception:
        logging.getLogger("alfred.notifications").warning("redis package not installed; treating Redis as unavailable")
        return None

    try:
        return Redis.from_url(url)
    except Exception:
        logging.getLogger("alfred.notifications").exception("Failed to connect to Redis at %s", url)
        return None


def enqueue_notification(task_name: str, payload: dict):
    """Enqueue a notification task. If Redis is not configured, fall back to in-process execution.

    task_name: short name like 'approval_requested' or 'approval_resolved'
    payload: serializable dict passed to the worker
    """
    conn = _get_redis_conn()
    if not conn:
        logging.getLogger("alfred.notifications").warning("Redis not configured; running notification in-process")
        # In-process fallback: import the async emitter and run it (best-effort)
        try:
            import asyncio
            from .integrations import manager as integrations_manager

            fn = getattr(integrations_manager, f"emit_{task_name}", None)
            if fn is None:
                logging.getLogger("alfred.notifications").error("No emitter found for %s", task_name)
                return
            coro = fn(**payload)
            try:
                asyncio.create_task(coro)
            except RuntimeError:
                # No running loop; run synchronously
                asyncio.run(coro)
        except Exception:
            logging.getLogger("alfred.notifications").exception("In-process notification failed")
        return

    # Ensure RQ is available
    try:
        from rq import Queue
    except Exception:
        logging.getLogger("alfred.notifications").warning("rq package not installed; running notification in-process")
        # Fall back to in-process
        try:
            import asyncio
            from .integrations import manager as integrations_manager

            fn = getattr(integrations_manager, f"emit_{task_name}", None)
            if fn is None:
                logging.getLogger("alfred.notifications").error("No emitter found for %s", task_name)
                return
            coro = fn(**payload)
            try:
                asyncio.create_task(coro)
            except RuntimeError:
                asyncio.run(coro)
        except Exception:
            logging.getLogger("alfred.notifications").exception("In-process notification failed")
        return

    try:
        q = Queue("default", connection=conn)
        # Use the module path for the worker function to avoid import-time side effects
        q.enqueue("backend.app.workers.process_task", task_name, payload, job_timeout=300)
    except Exception:
        logging.getLogger("alfred.notifications").exception("Failed to enqueue notification; falling back to in-process")
        try:
            import asyncio
            from .integrations import manager as integrations_manager

            fn = getattr(integrations_manager, f"emit_{task_name}", None)
            if fn is None:
                logging.getLogger("alfred.notifications").error("No emitter found for %s", task_name)
                return
            coro = fn(**payload)
            try:
                asyncio.create_task(coro)
            except RuntimeError:
                asyncio.run(coro)
        except Exception:
            logging.getLogger("alfred.notifications").exception("In-process notification failed")
        return
    
