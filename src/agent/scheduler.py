"""
Background Scheduler for the DPS Agent Booking System.
Uses APScheduler to run booking checks at configurable intervals.
"""

import asyncio
import logging
from typing import Dict, Optional, Callable, Awaitable
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore
from apscheduler.triggers.interval import IntervalTrigger  # type: ignore

from agent.booking_engine import BookingEngine  # type: ignore
from agent.decision_engine import DecisionEngine  # type: ignore
from db.database import Database  # type: ignore

logger = logging.getLogger(__name__)

# Type for WebSocket broadcast callback
BroadcastCallback = Callable[[Dict], Awaitable[None]]


class AgentScheduler:
    """
    Manages background booking jobs using APScheduler.
    Each active job runs periodic checks and auto-books when slots are found.
    """

    def __init__(self, db: Database, broadcast: Optional[BroadcastCallback] = None):
        self.db = db
        self.broadcast = broadcast
        self.decision_engine = DecisionEngine()
        self.scheduler = AsyncIOScheduler()
        self._active_engines: Dict[str, BookingEngine] = {}

    def start(self):
        """Start the scheduler."""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Agent scheduler started")

    def stop(self):
        """Shutdown the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            logger.info("Agent scheduler stopped")

    async def start_job(self, job_id: str) -> bool:
        """
        Start a booking monitoring job.

        Args:
            job_id: The database job ID to start.

        Returns:
            True if job was started successfully.
        """
        job = await self.db.get_job(job_id)
        if not job:
            logger.error(f"Job {job_id} not found")
            return False

        user = await self.db.get_user(job["user_id"])
        if not user:
            logger.error(f"User {job['user_id']} not found for job {job_id}")
            return False

        # Update job status to running
        await self.db.update_job(job_id, {"status": "running"})
        await self._log(job_id, "info", "Job started — monitoring for appointments")
        await self._broadcast_status(job_id, "running", "Monitoring started")

        # Build config from user profile
        config = self._build_config(user)

        # Get AI recommendation
        analysis = self.decision_engine.analyze_profile(user)
        button_keywords = analysis.get("button_keywords", ["apply", "first time"])

        # Schedule periodic check
        interval = job.get("check_interval_minutes", 5)
        self.scheduler.add_job(
            self._run_check,
            trigger=IntervalTrigger(minutes=interval),
            id=f"check_{job_id}",
            args=[job_id, config, button_keywords, bool(job.get("auto_book", True))],
            replace_existing=True,
            next_run_time=datetime.now(),  # Run immediately first time
        )

        logger.info(f"Job {job_id} scheduled every {interval} minutes")
        return True

    async def stop_job(self, job_id: str) -> bool:
        """Stop a running job."""
        scheduler_id = f"check_{job_id}"
        try:
            self.scheduler.remove_job(scheduler_id)
        except Exception:
            pass

        # Cleanup any active engine
        engine = self._active_engines.pop(job_id, None)
        if engine:
            await engine.cleanup()

        await self.db.update_job(job_id, {"status": "stopped"})
        await self._log(job_id, "info", "Job stopped by user")
        await self._broadcast_status(job_id, "stopped", "Monitoring stopped")
        return True

    async def _run_check(self, job_id: str, config: Dict,
                          button_keywords: list, auto_book: bool):
        """Execute a single check cycle for a job."""
        job = await self.db.get_job(job_id)
        if not job or job["status"] in ("stopped", "booked", "failed"):
            try:
                self.scheduler.remove_job(f"check_{job_id}")
            except:
                pass
            return

        # Check attempt limit
        attempts = job.get("attempts", 0)
        max_attempts = job.get("max_attempts", 100)
        if attempts >= max_attempts:
            await self.db.update_job(job_id, {"status": "failed"})
            await self._log(job_id, "error",
                          f"Max attempts ({max_attempts}) reached — stopping job")
            await self._broadcast_status(job_id, "failed", "Max attempts reached")
            try:
                self.scheduler.remove_job(f"check_{job_id}")
            except:
                pass
            return

        # Increment attempt counter
        await self.db.update_job(job_id, {
            "status": "monitoring",
            "attempts": attempts + 1,
            "last_check_at": datetime.now().isoformat()
        })

        await self._log(job_id, "info",
                       f"Check #{attempts + 1}/{max_attempts} starting...")
        await self._broadcast_status(job_id, "monitoring",
                                    f"Check #{attempts + 1} in progress")

        # Status callback that logs to DB and broadcasts
        async def on_status(level: str, message: str, screenshot_path: Optional[str] = None):
            await self._log(job_id, level, message, screenshot_path)
            await self._broadcast_status(job_id, "monitoring", message)

        # Run the booking engine
        engine = BookingEngine(config, on_status=on_status)
        self._active_engines[job_id] = engine

        try:
            result = await engine.run_check_and_book(
                button_keywords=button_keywords,
                auto_book=auto_book,
                slot_ranker=self.decision_engine.rank_slots
            )

            if result:
                # Appointment found!
                confirmed = result.get("booking_confirmed", False)
                status = "booked" if confirmed else "appointment_found"

                await self.db.update_job(job_id, {
                    "status": status,
                    "appointment_date": result.get("next_available"),
                    "appointment_location": result.get("location"),
                })

                await self.db.add_booking_result({
                    "job_id": job_id,
                    "location": result.get("location", "Unknown"),
                    "appointment_date": result.get("next_available", ""),
                    "available_dates": result.get("available_dates", []),
                    "total_slots": result.get("total_slots", 0),
                    "booking_confirmed": confirmed,
                })

                if confirmed:
                    await self._log(job_id, "success",
                                  f"🎉 BOOKED at {result['location']} on {result['next_available']}")
                    await self._broadcast_status(job_id, "booked",
                                               f"Booked: {result['next_available']}")
                    # Stop the job since we're booked
                    try:
                        self.scheduler.remove_job(f"check_{job_id}")
                    except:
                        pass
                else:
                    await self._log(job_id, "success",
                                  f"Appointments found at {result['location']}! "
                                  f"Next: {result['next_available']}")
                    await self._broadcast_status(job_id, "appointment_found",
                                               f"Found: {result['next_available']}")

                # Send email notification
                try:
                    from utils.notifier import EmailNotifier  # type: ignore
                    notifier = EmailNotifier(config)
                    subject = f"{'✅ BOOKED' if confirmed else '🔔 Found'}: DPS Appointment {result.get('next_available', '')}"
                    await notifier.send_notification(subject=subject, appointments=result)
                except Exception as e:
                    await self._log(job_id, "warning", f"Email notification failed: {e}")
            else:
                await self._log(job_id, "info", "No appointments available this check")

        except Exception as e:
            await self._log(job_id, "error", f"Check failed: {str(e)}")
        finally:
            self._active_engines.pop(job_id, None)

    # ─── Helpers ─────────────────────────────────────────────────

    def _build_config(self, user: Dict) -> Dict:
        """Build a booking engine config from a user profile."""
        return {
            'first_name': user.get('first_name', ''),
            'last_name': user.get('last_name', ''),
            'dob': user.get('dob', ''),
            'ssn_last4': user.get('ssn_last4', ''),
            'phone': user.get('phone', ''),
            'email': user.get('email', ''),
            'zip_code': user.get('zip_code', '76201'),
            'location_preference': user.get('location_preference', 'Denton'),
            'max_distance_miles': user.get('max_distance_miles', 25),
            'slot_priority': user.get('slot_priority', 'any'),
            'notify_email': user.get('notify_email') or user.get('email', ''),
            'smtp_server': user.get('smtp_server', 'smtp.gmail.com'),
            'smtp_port': user.get('smtp_port', 587),
            'smtp_user': user.get('smtp_user', ''),
            'smtp_password': user.get('smtp_password', ''),
            'headless': True,
            'screenshot_on_error': True,
        }

    async def _log(self, job_id: str, level: str, message: str, screenshot_path: Optional[str] = None):
        """Write a log entry to the database."""
        try:
            await self.db.add_log(job_id, message, level, screenshot_path)
        except Exception as e:
            logger.warning(f"DB log error: {e}")

    async def _broadcast_status(self, job_id: str, status: str, message: str):
        """Broadcast a status update via WebSocket."""
        if self.broadcast:
            try:
                await self.broadcast({  # type: ignore
                    "type": "job_status",
                    "job_id": job_id,
                    "status": status,
                    "message": message,
                    "timestamp": datetime.now().isoformat(),
                })
            except Exception as e:
                logger.warning(f"Broadcast error: {e}")
