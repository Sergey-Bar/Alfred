import asyncio
import logging


def process_task(task_name: str, payload: dict):
    """Worker entrypoint called by RQ. Dispatches to async emitter functions.

    This function runs in a worker process and must be synchronous; it uses asyncio.run
    to execute async emitter coroutines.
    """
    logger = logging.getLogger("alfred.worker")
    try:
        # Import here to avoid heavy imports in the API process
        from .integrations import manager as integrations_manager

        fn = getattr(integrations_manager, f"emit_{task_name}", None)
        if fn is None:
            logger.error("No integration emitter for task: %s", task_name)
            return

        # Ensure payload is a dict
        if payload is None:
            payload = {}

        # Execute the async function synchronously in this worker
        asyncio.run(fn(**payload))
    except Exception:
        logger.exception("Failed to process task %s", task_name)
