import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class CyclePhase(str, enum.Enum):
    menstrual = "menstrual"
    follicular = "follicular"
    ovulatory = "ovulatory"
    luteal = "luteal"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    cycle_length = Column(Integer, default=28)
    period_length = Column(Integer, default=5)
    notifications_enabled = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    cycle_entries = relationship("CycleEntry", back_populates="user")
    check_ins = relationship("DailyCheckIn", back_populates="user")


class CycleEntry(Base):
    __tablename__ = "cycle_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    phase = Column(SAEnum(CyclePhase), nullable=False)
    notes = Column(Text, default="")

    user = relationship("User", back_populates="cycle_entries")


class DailyCheckIn(Base):
    __tablename__ = "daily_check_ins"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    sleep_hours = Column(Float, nullable=True)
    energy_level = Column(Integer, nullable=True)
    mood_level = Column(Integer, nullable=True)
    cravings = Column(Text, default="")
    notes = Column(Text, default="")

    user = relationship("User", back_populates="check_ins")


class CoachingMessage(Base):
    __tablename__ = "coaching_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    check_in_id = Column(Integer, nullable=True)
    phase = Column(String, nullable=True)
    user_message = Column(Text, nullable=False)
    coach_response = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    type = Column(String, nullable=False)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    sent_at = Column(DateTime, default=datetime.datetime.utcnow)
    read_at = Column(DateTime, nullable=True)