"""
models.py — Database table definitions.

SQLAlchemy lets us define database tables as Python classes.
Each class = one table. Each attribute = one column.
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, Text
from sqlalchemy.sql import func
from database import Base
import uuid


def generate_uuid():
    """Generate a unique ID string like 'abc123-...' """
    return str(uuid.uuid4())


class User(Base):
    """
    The 'users' table — stores analyst accounts.
    """
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)   # Never store plain passwords!
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Case(Base):
    """
    The 'cases' table — each upload creates a case.
    Think of it like a police case file for one analyzed piece of media.
    """
    __tablename__ = "cases"

    id = Column(String, primary_key=True, default=generate_uuid)
    job_id = Column(String, unique=True, nullable=False, index=True)
    user_id = Column(String, nullable=True)          # Null if not logged in
    filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)        # "image", "audio", "document"
    file_size_bytes = Column(Integer, nullable=False)
    status = Column(String, default="queued")         # queued / processing / completed / failed
    fraud_risk_score = Column(Float, nullable=True)  # 0-100, null until analysis is done
    risk_category = Column(String, nullable=True)    # LOW / MEDIUM / HIGH / CRITICAL
    processing_time_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)               # Analyst notes
