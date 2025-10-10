"""
Task Scheduler Module
====================
Handles scheduled tasks and automation.
"""

import asyncio
import logging
from datetime import datetime, time
from typing import Optional
from .task_automation import update_overdue_tasks
from .database import get_session

logger = logging.getLogger(__name__)


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
                # Wait 1 hour before next check
                await asyncio.sleep(3600)  # 3600 seconds = 1 hour
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in scheduler: {e}")
                # Wait 5 minutes before retrying on error
                await asyncio.sleep(300)  # 300 seconds = 5 minutes
                
    async def _check_and_update_overdue_tasks(self):
        """Check and update overdue tasks"""
        try:
            # Get a new database session for this operation
            session = next(get_session())
            updated_count = update_overdue_tasks(session)
            session.close()
            
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
