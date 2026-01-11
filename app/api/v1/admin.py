import os
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, desc, select
from typing import Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.lead import Lead
from app.models.assessment import Assessment
from app.models.payment_transaction import PaymentTransaction
from app.models.pricing_plan import PricingPlan
from app.models.user import User
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(tags=["admin"])

class PlanUpdateRequest(BaseModel):
    price_usd: Optional[float] = None
    price_inr: Optional[float] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    features: Optional[List[str]] = None
    is_active: Optional[bool] = None

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

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None
    subscription_tier: Optional[str] = None
    is_co_creator: Optional[bool] = None
    
    class Config:
        from_attributes = True

# Simple password-based auth (in production, use proper JWT auth)
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "unitasa2025")  # Change this to a secure password in production

def verify_admin(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    token = authorization.replace("Bearer ", "")
    if token != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return True

@router.get("/stats")
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_admin)
):
    """Get dashboard statistics"""
    
    # Total leads
    total_leads_result = await db.execute(select(func.count()).select_from(Lead))
    total_leads = total_leads_result.scalar() or 0
    
    # Assessments completed
    assessments_result = await db.execute(
        select(func.count()).select_from(Assessment).where(Assessment.is_completed == True)
    )
    assessments_completed = assessments_result.scalar() or 0
    
    # Consultations booked
    consultations_result = await db.execute(
        select(func.count()).select_from(Lead).where(Lead.consultation_booked == True)
    )
    consultations_booked = consultations_result.scalar() or 0
    
    # Payments completed
    payments_result = await db.execute(
        select(func.count()).select_from(PaymentTransaction).where(
            PaymentTransaction.status == 'completed'
        )
    )
    payments_completed = payments_result.scalar() or 0
    
    # Total revenue by currency
    # Get USD revenue
    usd_revenue_result = await db.execute(
        select(func.sum(PaymentTransaction.amount)).where(
            PaymentTransaction.status == 'completed',
            PaymentTransaction.currency == 'USD'
        )
    )
    usd_revenue_value = usd_revenue_result.scalar()
    usd_revenue = float(usd_revenue_value) if usd_revenue_value else 0.0
    
    # Get INR revenue
    inr_revenue_result = await db.execute(
        select(func.sum(PaymentTransaction.amount)).where(
            PaymentTransaction.status == 'completed',
            PaymentTransaction.currency == 'INR'
        )
    )
    inr_revenue_value = inr_revenue_result.scalar()
    inr_revenue = float(inr_revenue_value) if inr_revenue_value else 0.0
    
    # Conversion rate (payments / total leads)
    conversion_rate = (payments_completed / total_leads * 100) if total_leads > 0 else 0.0
    
    return {
        "totalLeads": total_leads,
        "assessmentsCompleted": assessments_completed,
        "consultationsBooked": consultations_booked,
        "paymentsCompleted": payments_completed,
        "totalRevenueUSD": usd_revenue,
        "totalRevenueINR": inr_revenue,
        "conversionRate": conversion_rate
    }

@router.get("/leads")
async def get_leads(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_admin)
):
    """Get all leads with details"""

    try:
        # Get leads using ORM to ensure compatibility
        leads_query = select(Lead).order_by(Lead.created_at.desc()).limit(limit).offset(offset)
        leads_result = await db.execute(leads_query)
        leads = leads_result.scalars().all()

        leads_data = []
        for lead in leads:
            # Get assessment score if exists
            assessment_result = await db.execute(
                select(Assessment).where(
                    Assessment.lead_id == lead.id,
                    Assessment.is_completed == True
                )
            )
            assessment = assessment_result.scalar_one_or_none()

            # Check payment status
            payment_result = await db.execute(
                select(PaymentTransaction).where(
                    PaymentTransaction.customer_email == lead.email,
                    PaymentTransaction.status == 'completed'
                )
            )
            payment = payment_result.scalar_one_or_none()

            leads_data.append({
                "id": lead.id,
                "name": getattr(lead, 'full_name', None) or lead.email,
                "email": lead.email,
                "company": lead.company,
                "phone": getattr(lead, 'phone', None),
                "crm_system": getattr(lead, 'preferred_crm', None),
                "assessment_score": assessment.overall_score if assessment else None,
                "consultation_booked": getattr(lead, 'consultation_booked', False),
                "payment_completed": payment is not None,
                "created_at": lead.created_at.isoformat() if lead.created_at else None
            })

        # Get total count
        total_result = await db.execute(select(func.count()).select_from(Lead))
        total = total_result.scalar() or 0

        return {
            "leads": leads_data,
            "total": total
        }
    except Exception as e:
        # Return empty data if there's any issue
        print(f"Error fetching leads: {e}")
        return {
            "leads": [],
            "total": 0,
            "error": str(e)
        }

@router.get("/recent-activity")
async def get_recent_activity(
    days: int = 7,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_admin)
):
    """Get recent activity for the last N days"""
    
    since_date = datetime.utcnow() - timedelta(days=days)
    
    # New leads
    new_leads_result = await db.execute(
        select(func.count()).select_from(Lead).where(Lead.created_at >= since_date)
    )
    new_leads = new_leads_result.scalar() or 0
    
    # New assessments
    new_assessments_result = await db.execute(
        select(func.count()).select_from(Assessment).where(
            Assessment.created_at >= since_date,
            Assessment.is_completed == True
        )
    )
    new_assessments = new_assessments_result.scalar() or 0
    
    # New payments
    new_payments_result = await db.execute(
        select(func.count()).select_from(PaymentTransaction).where(
            PaymentTransaction.created_at >= since_date,
            PaymentTransaction.status == 'completed'
        )
    )
    new_payments = new_payments_result.scalar() or 0
    
    # Revenue in period
    revenue_result = await db.execute(
        select(func.sum(PaymentTransaction.amount)).where(
            PaymentTransaction.created_at >= since_date,
            PaymentTransaction.status == 'completed'
        )
    )
    revenue_value = revenue_result.scalar()
    revenue = float(revenue_value) if revenue_value else 0.0
    
    return {
        "period_days": days,
        "new_leads": new_leads,
        "new_assessments": new_assessments,
        "new_payments": new_payments,
        "revenue": revenue
    }

@router.get("/lead/{lead_id}")
async def get_lead_details(
    lead_id: int,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_admin)
):
    """Get detailed information about a specific lead"""
    
    # Get lead
    lead_result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = lead_result.scalar_one_or_none()
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Get assessment
    assessment_result = await db.execute(
        select(Assessment).where(
            Assessment.lead_id == lead_id,
            Assessment.is_completed == True
        )
    )
    assessment = assessment_result.scalar_one_or_none()
    
    # Get payment
    payment_result = await db.execute(
        select(PaymentTransaction).where(
            PaymentTransaction.customer_email == lead.email
        )
    )
    payment = payment_result.scalar_one_or_none()
    
    return {
        "lead": {
            "id": lead.id,
            "name": getattr(lead, 'name', None) or getattr(lead, 'full_name', None) or lead.email,
            "email": lead.email,
            "company": lead.company,
            "phone": getattr(lead, 'phone', None),
            "crm_system": getattr(lead, 'crm_system', None) or getattr(lead, 'preferred_crm', None),
            "consultation_booked": getattr(lead, 'consultation_booked', False),
            "created_at": lead.created_at.isoformat() if lead.created_at else None
        },
        "assessment": {
            "score": assessment.overall_score,
            "completed_at": assessment.completed_at.isoformat() if assessment and assessment.completed_at else None
        } if assessment else None,
        "payment": {
            "amount": payment.amount,
            "currency": payment.currency,
            "status": payment.status,
            "created_at": payment.created_at.isoformat() if payment and payment.created_at else None
        } if payment else None
    }

@router.get("/plans", response_model=List[PricingPlanResponse])
async def get_plans(
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_admin)
):
    """Get all pricing plans"""
    result = await db.execute(select(PricingPlan).order_by(PricingPlan.id))
    plans = result.scalars().all()
    return plans

@router.put("/plans/{plan_id}", response_model=PricingPlanResponse)
async def update_plan(
    plan_id: int,
    plan_update: PlanUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_admin)
):
    """Update a pricing plan"""
    result = await db.execute(select(PricingPlan).where(PricingPlan.id == plan_id))
    plan = result.scalar_one_or_none()
    
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    update_data = plan_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(plan, key, value)
    
    await db.commit()
    await db.refresh(plan)
    return plan

@router.get("/users", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_admin)
):
    """Get all users"""
    result = await db.execute(select(User).offset(skip).limit(limit))
    users = result.scalars().all()
    return users

@router.post("/users/{user_id}/upgrade")
async def upgrade_user_plan(
    user_id: int,
    plan_name: str,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_admin)
):
    """Upgrade user's plan"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.subscription_tier = plan_name
    if plan_name == 'co_creator':
        user.is_co_creator = True
    else:
        user.is_co_creator = False
    
    await db.commit()
    await db.refresh(user)
    
    return {"message": "User plan updated successfully"}
