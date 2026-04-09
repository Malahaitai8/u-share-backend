# app/models.py

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.sql import func
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)


class ClassificationRecord(Base):
    __tablename__ = "classification_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    garbage_type = Column(String(50), nullable=True)
    recognition_method = Column(String(20), nullable=True)
    points_earned = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())


class UserPoints(Base):
    __tablename__ = "user_points"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    current_points = Column(Integer, default=0)
    total_points = Column(Integer, default=0)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class VolunteerHourRequest(Base):
    __tablename__ = "volunteer_hour_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    points_spent = Column(Integer, nullable=False)
    hours_requested = Column(Float, nullable=False)
    status = Column(String(50), nullable=False, default="pending_school_review")
    created_at = Column(DateTime, server_default=func.now())
