"""
Task Scheduler Module
====================
Handles scheduled tasks and automation.
"""

import asyncio
import logging
from typing import Optional
from sqlmodel import Session
from .task_automation import update_overdue_tasks
from .database import engine

logger = logging.getLogger(__name__)

CHECK_INTERVAL_SECONDS = 3600  # 1 hour
RETRY_INTERVAL_SECONDS = 300   # 5 minutes


def _run_overdue_update() -> int:
    with Session(engine) as session:
        return update_overdue_tasks(session)


class TaskScheduler:
    """Scheduler for automated task updates"""

    def __init__(self):
        self.running = False
        self.task: Optional[asyncio.Task] = None

    async def start(self):
        """Start the scheduler"""
        if self.running:
            logger.warning("Scheduler is already running")
            return

        self.running = True
        self.task = asyncio.create_task(self._run_scheduler())
        logger.info("Task scheduler started")

    async def stop(self):
        """Stop the scheduler"""
        if not self.running:
            return

        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info("Task scheduler stopped")

    async def _run_scheduler(self):
        """Main scheduler loop"""
        while self.running:
            try:
                await self._check_and_update_overdue_tasks()
                await asyncio.sleep(CHECK_INTERVAL_SECONDS)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in scheduler: {e}")
                await asyncio.sleep(RETRY_INTERVAL_SECONDS)

    async def _check_and_update_overdue_tasks(self):
        """Check and update overdue tasks without blocking the event loop"""
        try:
            updated_count = await asyncio.to_thread(_run_overdue_update)

            if updated_count > 0:
                logger.info(f"Updated {updated_count} tasks to overdue status")
            else:
                logger.debug("No tasks needed to be updated to overdue status")

        except Exception as e:
            logger.error(f"Error updating overdue tasks: {e}")


# Global scheduler instance
scheduler = TaskScheduler()


async def start_scheduler():
    """Start the global scheduler"""
    await scheduler.start()


async def stop_scheduler():
    """Stop the global scheduler"""
    await scheduler.stop()
