"""
SQLite database layer for the DPS Agent Booking System.
Uses aiosqlite for async operations.
"""

import os
import json
import uuid
import aiosqlite  # type: ignore
from datetime import datetime
from typing import Optional, List, Dict
from pathlib import Path


# Database file location
DB_DIR = Path(__file__).parent.parent.parent / "data"
DB_PATH = DB_DIR / "dps_agent.db"


class Database:
    """Async SQLite database manager."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or str(DB_PATH)
        self._connection: Optional[aiosqlite.Connection] = None

    async def connect(self):
        """Open database connection and create tables."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._connection = await aiosqlite.connect(self.db_path)
        if self._connection:
            self._connection.row_factory = aiosqlite.Row  # type: ignore
        await self._create_tables()

    async def close(self):
        """Close database connection."""
        if self._connection:
            await self._connection.close()  # type: ignore
            self._connection = None

    @property
    def conn(self) -> aiosqlite.Connection:
        if not self._connection:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self._connection

    # ─── Table creation ──────────────────────────────────────────

    async def _create_tables(self):
        await self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                dob TEXT NOT NULL,
                ssn_last4 TEXT NOT NULL,
                phone TEXT NOT NULL,
                email TEXT NOT NULL,
                zip_code TEXT DEFAULT '76201',
                location_preference TEXT DEFAULT 'Denton',
                max_distance_miles INTEGER DEFAULT 25,
                slot_priority TEXT DEFAULT 'any',
                has_texas_license INTEGER DEFAULT 0,
                has_out_of_state_license INTEGER DEFAULT 0,
                license_expired INTEGER DEFAULT 0,
                license_lost_stolen INTEGER DEFAULT 0,
                is_commercial INTEGER DEFAULT 0,
                id_only INTEGER DEFAULT 0,
                needs_permit INTEGER DEFAULT 0,
                age INTEGER,
                notify_email TEXT,
                smtp_server TEXT DEFAULT 'smtp.gmail.com',
                smtp_port INTEGER DEFAULT 587,
                smtp_user TEXT,
                smtp_password TEXT,
                recommended_service TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                service_type TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                check_interval_minutes INTEGER DEFAULT 5,
                auto_book INTEGER DEFAULT 1,
                attempts INTEGER DEFAULT 0,
                max_attempts INTEGER DEFAULT 100,
                last_check_at TEXT,
                appointment_date TEXT,
                appointment_location TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS agent_logs (
                id TEXT PRIMARY KEY,
                job_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                level TEXT DEFAULT 'info',
                message TEXT NOT NULL,
                screenshot_path TEXT,
                FOREIGN KEY (job_id) REFERENCES jobs(id)
            );

            CREATE TABLE IF NOT EXISTS booking_results (
                id TEXT PRIMARY KEY,
                job_id TEXT NOT NULL,
                location TEXT NOT NULL,
                appointment_date TEXT NOT NULL,
                available_dates TEXT NOT NULL,
                total_slots INTEGER DEFAULT 0,
                booking_confirmed INTEGER DEFAULT 0,
                confirmation_id TEXT,
                checked_at TEXT NOT NULL,
                FOREIGN KEY (job_id) REFERENCES jobs(id)
            );

            CREATE INDEX IF NOT EXISTS idx_jobs_user_id ON jobs(user_id);
            CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
            CREATE INDEX IF NOT EXISTS idx_agent_logs_job_id ON agent_logs(job_id);
            CREATE INDEX IF NOT EXISTS idx_booking_results_job_id ON booking_results(job_id);
        """)
        await self.conn.commit()

    # ─── User CRUD ───────────────────────────────────────────────

    async def create_user(self, data: Dict) -> Optional[Dict]:
        user_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        await self.conn.execute(
            """INSERT INTO users (id, first_name, last_name, dob, ssn_last4, phone, email,
                zip_code, location_preference, max_distance_miles, slot_priority,
                has_texas_license, has_out_of_state_license, license_expired,
                license_lost_stolen, is_commercial, id_only, needs_permit, age,
                notify_email, smtp_server, smtp_port, smtp_user, smtp_password,
                recommended_service, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, data["first_name"], data["last_name"], data["dob"],
             data["ssn_last4"], data["phone"], data["email"],
             data.get("zip_code", "76201"), data.get("location_preference", "Denton"),
             data.get("max_distance_miles", 25), data.get("slot_priority", "any"),
             int(data.get("has_texas_license", False)),
             int(data.get("has_out_of_state_license", False)),
             int(data.get("license_expired", False)),
             int(data.get("license_lost_stolen", False)),
             int(data.get("is_commercial", False)),
             int(data.get("id_only", False)),
             int(data.get("needs_permit", False)),
             data.get("age"),
             data.get("notify_email", data["email"]),
             data.get("smtp_server", "smtp.gmail.com"),
             data.get("smtp_port", 587),
             data.get("smtp_user"),
             data.get("smtp_password"),
             data.get("recommended_service"),
             now, now)
        )
        await self.conn.commit()
        return await self.get_user(user_id)

    async def get_user(self, user_id: str) -> Optional[Dict]:
        cursor = await self.conn.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = await cursor.fetchone()
        if row:
            return self._row_to_dict(row)
        return None

    async def get_all_users(self) -> List[Dict]:
        cursor = await self.conn.execute("SELECT * FROM users ORDER BY created_at DESC")
        rows = await cursor.fetchall()
        return [self._row_to_dict(r) for r in rows]

    async def update_user(self, user_id: str, data: Dict) -> Optional[Dict]:
        fields = []
        values = []
        for key, value in data.items():
            if key in ("id", "created_at"):
                continue
            if isinstance(value, bool):
                value = int(value)
            fields.append(f"{key} = ?")
            values.append(value)
        fields.append("updated_at = ?")
        values.append(datetime.now().isoformat())
        values.append(user_id)

        await self.conn.execute(
            f"UPDATE users SET {', '.join(fields)} WHERE id = ?", values
        )
        await self.conn.commit()
        return await self.get_user(user_id)

    async def delete_user(self, user_id: str) -> bool:
        cursor = await self.conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        await self.conn.commit()
        return cursor.rowcount > 0

    # ─── Job CRUD ────────────────────────────────────────────────

    async def create_job(self, data: Dict) -> Optional[Dict]:
        job_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        await self.conn.execute(
            """INSERT INTO jobs (id, user_id, service_type, status,
                check_interval_minutes, auto_book, attempts, max_attempts,
                created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (job_id, data["user_id"], data["service_type"],
             data.get("status", "pending"),
             data.get("check_interval_minutes", 5),
             int(data.get("auto_book", True)),
             0, data.get("max_attempts", 100),
             now, now)
        )
        await self.conn.commit()
        return await self.get_job(job_id)

    async def get_job(self, job_id: str) -> Optional[Dict]:
        cursor = await self.conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
        row = await cursor.fetchone()
        if row:
            return self._row_to_dict(row)
        return None

    async def get_all_jobs(self) -> List[Dict]:
        cursor = await self.conn.execute("SELECT * FROM jobs ORDER BY created_at DESC")
        rows = await cursor.fetchall()
        return [self._row_to_dict(r) for r in rows]

    async def get_jobs_by_user(self, user_id: str) -> List[Dict]:
        cursor = await self.conn.execute(
            "SELECT * FROM jobs WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        )
        rows = await cursor.fetchall()
        return [self._row_to_dict(r) for r in rows]

    async def get_active_jobs(self) -> List[Dict]:
        cursor = await self.conn.execute(
            "SELECT * FROM jobs WHERE status IN ('pending', 'running', 'monitoring', 'appointment_found', 'booking', 'otp_waiting')"
        )
        rows = await cursor.fetchall()
        return [self._row_to_dict(r) for r in rows]

    async def update_job(self, job_id: str, data: Dict) -> Optional[Dict]:
        fields = []
        values = []
        for key, value in data.items():
            if key in ("id", "created_at"):
                continue
            if isinstance(value, bool):
                value = int(value)
            fields.append(f"{key} = ?")
            values.append(value)
        fields.append("updated_at = ?")
        values.append(datetime.now().isoformat())
        values.append(job_id)

        await self.conn.execute(
            f"UPDATE jobs SET {', '.join(fields)} WHERE id = ?", values
        )
        await self.conn.commit()
        return await self.get_job(job_id)

    async def delete_job(self, job_id: str) -> bool:
        cursor = await self.conn.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
        await self.conn.commit()
        return cursor.rowcount > 0

    # ─── Agent Logs ──────────────────────────────────────────────

    async def add_log(self, job_id: str, message: str, level: str = "info",
                      screenshot_path: Optional[str] = None) -> Dict:
        log_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        await self.conn.execute(
            """INSERT INTO agent_logs (id, job_id, timestamp, level, message, screenshot_path)
            VALUES (?, ?, ?, ?, ?, ?)""",
            (log_id, job_id, now, level, message, screenshot_path)
        )
        await self.conn.commit()
        return {"id": log_id, "job_id": job_id, "timestamp": now,
                "level": level, "message": message, "screenshot_path": screenshot_path}

    async def get_logs(self, job_id: str, limit: int = 50) -> List[Dict]:
        cursor = await self.conn.execute(
            "SELECT * FROM agent_logs WHERE job_id = ? ORDER BY timestamp DESC LIMIT ?",
            (job_id, limit)
        )
        rows = await cursor.fetchall()
        return [self._row_to_dict(r) for r in rows]

    # ─── Booking Results ─────────────────────────────────────────

    async def add_booking_result(self, data: Dict) -> Optional[Dict]:
        result_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        available_dates = json.dumps(data.get("available_dates", []))
        await self.conn.execute(
            """INSERT INTO booking_results (id, job_id, location, appointment_date,
                available_dates, total_slots, booking_confirmed, confirmation_id, checked_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (result_id, data["job_id"], data["location"], data["appointment_date"],
             available_dates, data.get("total_slots", 0),
             int(data.get("booking_confirmed", False)),
             data.get("confirmation_id"),
             now)
        )
        await self.conn.commit()
        return await self.get_booking_result(result_id)

    async def get_booking_result(self, result_id: str) -> Optional[Dict]:
        cursor = await self.conn.execute(
            "SELECT * FROM booking_results WHERE id = ?", (result_id,)
        )
        row = await cursor.fetchone()
        if row:
            d = self._row_to_dict(row)
            if isinstance(d.get("available_dates"), str):
                d["available_dates"] = json.loads(d["available_dates"])
            return d
        return None

    async def get_booking_results_by_job(self, job_id: str) -> List[Dict]:
        cursor = await self.conn.execute(
            "SELECT * FROM booking_results WHERE job_id = ? ORDER BY checked_at DESC",
            (job_id,)
        )
        rows = await cursor.fetchall()
        results = []
        for r in rows:
            d = self._row_to_dict(r)
            if isinstance(d.get("available_dates"), str):
                d["available_dates"] = json.loads(d["available_dates"])
            results.append(d)
        return results

    async def get_all_bookings(self) -> List[Dict]:
        cursor = await self.conn.execute(
            "SELECT * FROM booking_results ORDER BY checked_at DESC"
        )
        rows = await cursor.fetchall()
        results = []
        for r in rows:
            d = self._row_to_dict(r)
            if isinstance(d.get("available_dates"), str):
                d["available_dates"] = json.loads(d["available_dates"])
            results.append(d)
        return results

    # ─── Helpers ─────────────────────────────────────────────────

    @staticmethod
    def _row_to_dict(row) -> Dict:
        """Convert an aiosqlite Row to a regular dict."""
        return dict(row)
