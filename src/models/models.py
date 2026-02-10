"""
Data models for the DPS Agent Booking System.
Pydantic models for API validation + SQLAlchemy ORM for persistence.
"""

import enum
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr


# ─── Enums ───────────────────────────────────────────────────────────

class ServiceType(str, enum.Enum):
    FIRST_TIME_DL = "Apply for first time Texas DL/Permit"
    RENEW_DL = "Renew Texas DL/ID"
    REPLACE_DL = "Replace Texas DL/ID"
    TRANSFER_OOS = "Transfer out-of-state DL to Texas"
    CDL = "Commercial Driver License (CDL)"
    TEXAS_ID = "Apply for Texas ID card"
    CHANGE_UPDATE = "Change/update information on DL/ID"
    PERMIT = "Apply for Learner Permit"


class JobStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    MONITORING = "monitoring"
    APPOINTMENT_FOUND = "appointment_found"
    BOOKING = "booking"
    OTP_WAITING = "otp_waiting"
    BOOKED = "booked"
    FAILED = "failed"
    STOPPED = "stopped"


class LogLevel(str, enum.Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"


class SlotPriority(str, enum.Enum):
    SAME_DAY = "same_day"
    NEXT_DAY = "next_day"
    THIS_WEEK = "this_week"
    ANY = "any"


# ─── Pydantic Schemas (API layer) ────────────────────────────────────

class UserProfileCreate(BaseModel):
    """Schema for creating/updating a user profile."""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    dob: str = Field(..., pattern=r"^\d{2}/\d{2}/\d{4}$", description="MM/DD/YYYY")
    ssn_last4: str = Field(..., min_length=4, max_length=4, pattern=r"^\d{4}$")
    phone: str = Field(..., min_length=10)
    email: str = Field(...)
    zip_code: str = Field(default="76201", pattern=r"^\d{5}$")
    
    # Preferences
    location_preference: str = Field(default="Denton")
    max_distance_miles: int = Field(default=25, ge=5, le=100)
    slot_priority: SlotPriority = Field(default=SlotPriority.ANY)
    
    # License situation (used by AI decision engine)
    has_texas_license: bool = Field(default=False)
    has_out_of_state_license: bool = Field(default=False)
    license_expired: bool = Field(default=False)
    license_lost_stolen: bool = Field(default=False)
    is_commercial: bool = Field(default=False)
    id_only: bool = Field(default=False)
    needs_permit: bool = Field(default=False)
    age: Optional[int] = Field(default=None, ge=14, le=120)
    
    # Notification / SMTP
    notify_email: Optional[str] = None
    smtp_server: str = Field(default="smtp.gmail.com")
    smtp_port: int = Field(default=587)
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None


class UserProfileResponse(BaseModel):
    """Schema for returning a user profile."""
    id: str
    first_name: str
    last_name: str
    dob: str
    email: str
    zip_code: str
    location_preference: str
    max_distance_miles: int
    slot_priority: SlotPriority
    recommended_service: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class BookingJobCreate(BaseModel):
    """Schema for starting a new booking job."""
    user_id: str
    service_type: Optional[ServiceType] = None  # None = let AI decide
    check_interval_minutes: int = Field(default=5, ge=1, le=30)
    auto_book: bool = Field(default=True)
    max_attempts: int = Field(default=100, ge=1, le=1000)


class BookingJobResponse(BaseModel):
    """Schema for returning a booking job."""
    id: str
    user_id: str
    service_type: str
    status: JobStatus
    check_interval_minutes: int
    auto_book: bool
    attempts: int
    max_attempts: int
    last_check_at: Optional[datetime] = None
    appointment_date: Optional[str] = None
    appointment_location: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class AgentLogResponse(BaseModel):
    """Schema for returning an agent log entry."""
    id: str
    job_id: str
    timestamp: datetime
    level: LogLevel
    message: str
    screenshot_path: Optional[str] = None


class BookingResultResponse(BaseModel):
    """Schema for returning a booking result."""
    id: str
    job_id: str
    location: str
    appointment_date: str
    available_dates: List[str]
    total_slots: int
    booking_confirmed: bool
    confirmation_id: Optional[str] = None
    checked_at: datetime


class AnalyzeRequest(BaseModel):
    """Schema for requesting AI analysis of a user profile."""
    has_texas_license: bool = False
    has_out_of_state_license: bool = False
    license_expired: bool = False
    license_lost_stolen: bool = False
    is_commercial: bool = False
    id_only: bool = False
    needs_permit: bool = False
    age: Optional[int] = None


class AnalyzeResponse(BaseModel):
    """Schema for AI analysis result."""
    recommended_service: ServiceType
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str
    booking_tips: List[str]


# ─── ORM Models (SQLAlchemy) ─────────────────────────────────────────

# We use raw SQL via aiosqlite for simplicity rather than full 
# SQLAlchemy ORM, keeping the project lean. The schemas above
# define the table shapes.

class UserProfile:
    """Runtime data class for a stored user profile."""
    def __init__(self, **kwargs):
        self.id: str = kwargs.get("id", "")
        self.first_name: str = kwargs.get("first_name", "")
        self.last_name: str = kwargs.get("last_name", "")
        self.dob: str = kwargs.get("dob", "")
        self.ssn_last4: str = kwargs.get("ssn_last4", "")
        self.phone: str = kwargs.get("phone", "")
        self.email: str = kwargs.get("email", "")
        self.zip_code: str = kwargs.get("zip_code", "76201")
        self.location_preference: str = kwargs.get("location_preference", "Denton")
        self.max_distance_miles: int = kwargs.get("max_distance_miles", 25)
        self.slot_priority: str = kwargs.get("slot_priority", "any")
        self.has_texas_license: bool = kwargs.get("has_texas_license", False)
        self.has_out_of_state_license: bool = kwargs.get("has_out_of_state_license", False)
        self.license_expired: bool = kwargs.get("license_expired", False)
        self.license_lost_stolen: bool = kwargs.get("license_lost_stolen", False)
        self.is_commercial: bool = kwargs.get("is_commercial", False)
        self.id_only: bool = kwargs.get("id_only", False)
        self.needs_permit: bool = kwargs.get("needs_permit", False)
        self.age: Optional[int] = kwargs.get("age")
        self.notify_email: Optional[str] = kwargs.get("notify_email")
        self.smtp_server: str = kwargs.get("smtp_server", "smtp.gmail.com")
        self.smtp_port: int = kwargs.get("smtp_port", 587)
        self.smtp_user: Optional[str] = kwargs.get("smtp_user")
        self.smtp_password: Optional[str] = kwargs.get("smtp_password")
        self.recommended_service: Optional[str] = kwargs.get("recommended_service")
        self.created_at: datetime = kwargs.get("created_at", datetime.now())
        self.updated_at: datetime = kwargs.get("updated_at", datetime.now())


class BookingJob:
    """Runtime data class for a booking job."""
    def __init__(self, **kwargs):
        self.id: str = kwargs.get("id", "")
        self.user_id: str = kwargs.get("user_id", "")
        self.service_type: str = kwargs.get("service_type", "")
        self.status: str = kwargs.get("status", JobStatus.PENDING.value)
        self.check_interval_minutes: int = kwargs.get("check_interval_minutes", 5)
        self.auto_book: bool = kwargs.get("auto_book", True)
        self.attempts: int = kwargs.get("attempts", 0)
        self.max_attempts: int = kwargs.get("max_attempts", 100)
        self.last_check_at: Optional[datetime] = kwargs.get("last_check_at")
        self.appointment_date: Optional[str] = kwargs.get("appointment_date")
        self.appointment_location: Optional[str] = kwargs.get("appointment_location")
        self.created_at: datetime = kwargs.get("created_at", datetime.now())
        self.updated_at: datetime = kwargs.get("updated_at", datetime.now())


class AgentLog:
    """Runtime data class for an agent log entry."""
    def __init__(self, **kwargs):
        self.id: str = kwargs.get("id", "")
        self.job_id: str = kwargs.get("job_id", "")
        self.timestamp: datetime = kwargs.get("timestamp", datetime.now())
        self.level: str = kwargs.get("level", LogLevel.INFO.value)
        self.message: str = kwargs.get("message", "")
        self.screenshot_path: Optional[str] = kwargs.get("screenshot_path")


class BookingResult:
    """Runtime data class for a booking result."""
    def __init__(self, **kwargs):
        self.id: str = kwargs.get("id", "")
        self.job_id: str = kwargs.get("job_id", "")
        self.location: str = kwargs.get("location", "")
        self.appointment_date: str = kwargs.get("appointment_date", "")
        self.available_dates: List[str] = kwargs.get("available_dates", [])
        self.total_slots: int = kwargs.get("total_slots", 0)
        self.booking_confirmed: bool = kwargs.get("booking_confirmed", False)
        self.confirmation_id: Optional[str] = kwargs.get("confirmation_id")
        self.checked_at: datetime = kwargs.get("checked_at", datetime.now())
