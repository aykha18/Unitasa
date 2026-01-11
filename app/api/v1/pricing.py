from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from app.core.database import get_db
from app.models.pricing_plan import PricingPlan

router = APIRouter(prefix="/pricing", tags=["pricing"])

class PricingPlanResponse(BaseModel):
    id: int
    name: str
    display_name: str
    price_usd: float
    price_inr: float
    features: Optional[List[str]] = None
    description: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True

@router.get("/plans", response_model=List[PricingPlanResponse])
async def get_active_plans(db: AsyncSession = Depends(get_db)):
    """Get all active pricing plans"""
    result = await db.execute(select(PricingPlan).where(PricingPlan.is_active == True))
    plans = result.scalars().all()
    return plans
