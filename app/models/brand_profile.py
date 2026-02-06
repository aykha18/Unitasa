"""
Brand Profile model for storing client specific brand configurations
"""

from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin

class BrandProfile(Base, TimestampMixin):
    """Brand Profile model for storing brand identity and configuration"""
    __tablename__ = "brand_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    client_id = Column(String(255), unique=True, index=True, nullable=False)
    
    # Store the structured profile as JSON
    # This stores the structure: 
    # {
    #     "company_info": {...},
    #     "target_audience": {...},
    #     "features": [...],
    #     "how_it_works": [...]
    # }
    profile_data = Column(JSON, nullable=False, default={})
    
    # Relationship
    user = relationship("User", back_populates="brand_profile")

    def __repr__(self):
        return f"<BrandProfile(id={self.id}, client_id='{self.client_id}')>"
