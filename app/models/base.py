"""
Base SQLAlchemy model with common functionality
"""

from datetime import datetime
from typing import Any, Dict

from sqlalchemy import Column, Integer, DateTime
from app.core.database import Base

# Removed declarative_base() call as we use the one from app.core.database


class TimestampMixin:
    """Mixin to add timestamp columns to models"""

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class BaseModel(Base, TimestampMixin):
    """Enhanced base model with common functionality"""

    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)

    def to_dict(self) -> Dict[str, Any]:
        """Convert model instance to dictionary"""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            result[column.name] = value
        return result

    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """Update model instance from dictionary"""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseModel':
        """Create model instance from dictionary"""
        instance = cls()
        instance.update_from_dict(data)
        return instance

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"
