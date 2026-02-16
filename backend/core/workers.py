"""
Alfred Background Task Consumer (RQ Worker)

[ARCHITECTURAL ROLE]
This module defines the execution logic for background workers (orchestrated
via Redis/RQ). It isolates high-latency side effects—such as sending alerts
to third-party APIs (Slack, Teams)—from the core request-response cycle.
This ensures that even if Slack is slow or unreachable, the AI gateway
remains responsive to the end user.

[EXECUTION CONTEXT]
RQ workers run in a standard synchronous Python process. This module bridges
the gap by using 'asyncio.run' to execute our async integration emitters
in an isolated, ephemeral event loop.
"""

import asyncio
import logging


def process_task(task_name: str, payload: dict):
    """
    Standardized Task Dispatcher Interface.

    This function is the 'Target' for all enqueued jobs. It performs
    late-bound discovery of the appropriate integration logic to
    minimize memory overhead in the worker process.

    Arguments:
    - task_name: Canonical name of the event (maps to manager.emit_{name}).
    - payload: Fully-serialized parameters required for the task.
    """
    logger = logging.getLogger("alfred.worker")

    try:
        # Late-bound import: Only load integration logic when a task is actually being processed.
        # This prevents the worker from crashing on startup if an integration has a circular dependency.
        from .integrations import manager as integrations_manager

        # Resolution: Identify the specific notification/alerting logic to trigger.
        fn = getattr(integrations_manager, f"emit_{task_name}", None)
        if fn is None:
            logger.error(f"Worker Error: No implementation found for task '{task_name}'.")
            return

        # Sanity check: Ensure the payload is a valid dictionary before unpacking.
        if payload is None:
            payload = {}

        # Bridge: Execute the asynchronous integration logic within a synchronous worker context.
        logger.info(f"Worker Execution: Starting '{task_name}'...")
        asyncio.run(fn(**payload))
        logger.info(f"Worker Success: Task '{task_name}' completed.")

    except Exception as e:
        logger.exception(f"Worker Critical Failure: Task '{task_name}' aborted ({str(e)}).")
