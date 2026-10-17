import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum


class CyclePhase(str, Enum):
    menstrual = "menstrual"
    follicular = "follicular"
    ovulatory = "ovulatory"
    luteal = "luteal"


# ── Auth ──
class UserRegister(BaseModel):
    email: EmailStr
    name: str
    password: str
    cycle_length: int = 28
    period_length: int = 5

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserOut"

class UserOut(BaseModel):
    id: int
    email: str
    name: str
    cycle_length: int
    period_length: int
    notifications_enabled: int

    class Config:
        from_attributes = True


# ── Cycle ──
class CycleEntryCreate(BaseModel):
    phase: CyclePhase
    date: datetime.date
    notes: str = ""

class CycleEntryOut(BaseModel):
    id: int
    phase: CyclePhase
    date: datetime.datetime
    notes: str

    class Config:
        from_attributes = True


# ── Check-in ──
class CheckInCreate(BaseModel):
    sleep_hours: Optional[float] = None
    energy_level: Optional[int] = None
    mood_level: Optional[int] = None
    cravings: str = ""
    notes: str = ""

class CheckInOut(BaseModel):
    id: int
    date: datetime.datetime
    sleep_hours: Optional[float]
    energy_level: Optional[int]
    mood_level: Optional[int]
    cravings: str
    notes: str

    class Config:
        from_attributes = True


# ── Coaching ──
class CoachingRequest(BaseModel):
    check_in_id: Optional[int] = None
    message: str = ""
    phase: Optional[CyclePhase] = None

class CoachingResponse(BaseModel):
    advice: str
    phase: Optional[str]


# ── Notifications ──
class NotificationOut(BaseModel):
    id: int
    type: str
    title: str
    message: str
    sent_at: datetime.datetime
    read_at: Optional[datetime.datetime]

    class Config:
        from_attributes = True