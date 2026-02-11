"""
API route definitions for the DPS Agent Booking System.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from models.models import (
    UserProfileCreate, UserProfileResponse,
    BookingJobCreate, BookingJobResponse,
    AgentLogResponse, BookingResultResponse,
    AnalyzeRequest, AnalyzeResponse,
    ServiceType
)
from agent.decision_engine import DecisionEngine
from db.database import Database


router = APIRouter(prefix="/api", tags=["DPS Agent"])

# These will be injected by the main app
_db: Optional[Database] = None
_scheduler = None
_decision_engine = DecisionEngine()


def set_dependencies(db: Database, scheduler):
    """Set shared dependencies from the main app."""
    global _db, _scheduler
    _db = db
    _scheduler = scheduler


def get_db() -> Database:
    if _db is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
    return _db


# ─── User Endpoints ─────────────────────────────────────────────

@router.post("/users", response_model=UserProfileResponse)
async def create_user(user: UserProfileCreate):
    """Create a new user profile."""
    db = get_db()
    data = user.model_dump()

    # Auto-calculate age from DOB
    if not data.get("age") and data.get("dob"):
        try:
            from datetime import datetime
            dob = datetime.strptime(data["dob"], "%m/%d/%Y")
            today = datetime.today()
            data["age"] = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        except:
            pass

    # Run AI analysis to get recommended service
    analysis = _decision_engine.analyze_profile(data)
    data["recommended_service"] = analysis["recommended_service"]

    result = await db.create_user(data)
    if result is None:
        raise HTTPException(status_code=500, detail="Failed to create user")
    return _user_response(result)


@router.get("/users", response_model=List[UserProfileResponse])
async def list_users():
    """List all user profiles."""
    db = get_db()
    users = await db.get_all_users()
    return [_user_response(u) for u in users]


@router.get("/users/{user_id}", response_model=UserProfileResponse)
async def get_user(user_id: str):
    """Get a user profile by ID."""
    db = get_db()
    user = await db.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return _user_response(user)


@router.put("/users/{user_id}", response_model=UserProfileResponse)
async def update_user(user_id: str, user: UserProfileCreate):
    """Update an existing user profile."""
    db = get_db()
    existing = await db.get_user(user_id)
    if not existing:
        raise HTTPException(status_code=404, detail="User not found")

    data = user.model_dump()
    analysis = _decision_engine.analyze_profile(data)
    data["recommended_service"] = analysis["recommended_service"]

    result = await db.update_user(user_id, data)
    if result is None:
        raise HTTPException(status_code=500, detail="Failed to update user")
    return _user_response(result)


@router.delete("/users/{user_id}")
async def delete_user(user_id: str):
    """Delete a user profile."""
    db = get_db()
    deleted = await db.delete_user(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return {"status": "deleted", "id": user_id}


# ─── AI Analysis Endpoint ───────────────────────────────────────

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_profile(request: AnalyzeRequest):
    """Analyze a user profile and recommend the best DPS service."""
    data = request.model_dump()
    analysis = _decision_engine.analyze_profile(data)
    return AnalyzeResponse(
        recommended_service=ServiceType(analysis["recommended_service"]),
        confidence=analysis["confidence"],
        reasoning=analysis["reasoning"],
        booking_tips=analysis["booking_tips"],
    )


# ─── Job Endpoints ──────────────────────────────────────────────

@router.post("/jobs", response_model=BookingJobResponse)
async def create_job(job: BookingJobCreate):
    """Create and start a new booking monitoring job."""
    db = get_db()

    user = await db.get_user(job.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Determine service type
    if job.service_type:
        service_type = job.service_type.value
    else:
        analysis = _decision_engine.analyze_profile(user)
        service_type = analysis["recommended_service"]

    data = {
        "user_id": job.user_id,
        "service_type": service_type,
        "check_interval_minutes": job.check_interval_minutes,
        "auto_book": job.auto_book,
        "max_attempts": job.max_attempts,
        "status": "pending",
    }

    result = await db.create_job(data)
    if result is None:
        raise HTTPException(status_code=500, detail="Failed to create job")

    # Start the job in the background scheduler
    if _scheduler:
        await _scheduler.start_job(result["id"])

    return _job_response(result)


@router.get("/jobs", response_model=List[BookingJobResponse])
async def list_jobs():
    """List all booking jobs."""
    db = get_db()
    jobs = await db.get_all_jobs()
    return [_job_response(j) for j in jobs]


@router.get("/jobs/{job_id}", response_model=BookingJobResponse)
async def get_job(job_id: str):
    """Get a specific job's status."""
    db = get_db()
    job = await db.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return _job_response(job)


@router.delete("/jobs/{job_id}")
async def stop_job(job_id: str):
    """Stop and remove a monitoring job."""
    db = get_db()
    job = await db.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if _scheduler:
        await _scheduler.stop_job(job_id)

    return {"status": "stopped", "id": job_id}


@router.get("/jobs/{job_id}/logs", response_model=List[AgentLogResponse])
async def get_job_logs(job_id: str, limit: int = 50):
    """Get agent activity logs for a job."""
    db = get_db()
    job = await db.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    logs = await db.get_logs(job_id, limit)
    return [AgentLogResponse(**log) for log in logs]


# ─── Booking History ─────────────────────────────────────────────

@router.get("/bookings", response_model=List[BookingResultResponse])
async def list_bookings():
    """List all booking results."""
    db = get_db()
    results = await db.get_all_bookings()
    return [BookingResultResponse(**r) for r in results]


# ─── Health Check ────────────────────────────────────────────────

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    scheduler_running = False
    if _scheduler is not None and getattr(_scheduler, "scheduler", None) is not None:
        scheduler_running = getattr(_scheduler.scheduler, "running", False)
    return {
        "status": "healthy",
        "service": "DPS Agent Booking System",
        "scheduler_running": scheduler_running,
    }


# ─── Response Helpers ────────────────────────────────────────────

def _user_response(user: dict) -> UserProfileResponse:
    """Convert a user dict to a UserProfileResponse."""
    return UserProfileResponse(
        id=user["id"],
        first_name=user["first_name"],
        last_name=user["last_name"],
        dob=user["dob"],
        email=user["email"],
        zip_code=user.get("zip_code", "76201"),
        location_preference=user.get("location_preference", "Denton"),
        max_distance_miles=user.get("max_distance_miles", 25),
        slot_priority=user.get("slot_priority", "any"),
        recommended_service=user.get("recommended_service"),
        created_at=user.get("created_at", ""),
        updated_at=user.get("updated_at", ""),
    )


def _job_response(job: dict) -> BookingJobResponse:
    """Convert a job dict to a BookingJobResponse."""
    return BookingJobResponse(
        id=job["id"],
        user_id=job["user_id"],
        service_type=job["service_type"],
        status=job.get("status", "pending"),
        check_interval_minutes=job.get("check_interval_minutes", 5),
        auto_book=bool(job.get("auto_book", True)),
        attempts=job.get("attempts", 0),
        max_attempts=job.get("max_attempts", 100),
        last_check_at=job.get("last_check_at"),
        appointment_date=job.get("appointment_date"),
        appointment_location=job.get("appointment_location"),
        created_at=job.get("created_at", ""),
        updated_at=job.get("updated_at", ""),
    )
