from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.sql import func
from app.models.base import Base


class ScheduleRule(Base):
    __tablename__ = "schedule_rules"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(200))
    platforms = Column(JSON, default=list)
    frequency = Column(String(20), nullable=False)
    time_of_day = Column(String(10), nullable=False)
    timezone = Column(String(100), default="UTC")
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    days_of_week = Column(JSON, default=list)
    recurrence_config = Column(JSON, default=dict)  # For advanced recurrence (nth weekday, etc.)
    skip_dates = Column(JSON, default=list)  # List of dates to skip
    theme_preset = Column(String(50))  # Theme preset name
    content_variation = Column(JSON, default=dict)  # Content variation settings
    generation_mode = Column(String(20), default="automatic")
    autopost = Column(Boolean, default=True)
    template_id = Column(Integer)
    content_seed = Column(Text)
    topic = Column(String(200))
    tone = Column(String(50))
    content_type = Column(String(50))
    last_run_at = Column(DateTime)
    next_run_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
