from sqlalchemy import Column, Integer, String, Boolean, JSON, Float
from app.core.database import Base
from app.models.base import TimestampMixin

class PricingPlan(Base, TimestampMixin):
    __tablename__ = "pricing_plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True)  # free, pro, enterprise, co_creator
    display_name = Column(String(100))
    price_usd = Column(Float, default=0.0)
    price_inr = Column(Float, default=0.0)
    features = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    description = Column(String(255), nullable=True)
