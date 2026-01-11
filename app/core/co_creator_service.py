"""
Co-Creator Program Service
Handles seat allocation, concurrency control, and program management
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, or_, func

from app.models.co_creator_program import CoCreatorProgram, CoCreator
from app.models.user import User
from app.models.lead import Lead


class CoCreatorProgramService:
    """Service for managing co-creator program operations with atomic seat allocation"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def get_or_create_active_program(self) -> CoCreatorProgram:
        """Get the active co-creator program or create one if none exists"""
        program = CoCreatorProgram.get_active_program(self.db)
        
        if not program:
            program = CoCreatorProgram(
                program_name="Unitasa Founding Co-Creator Program",
                total_seats=25,
                program_price=1.05, # UPDATED FOR TESTING: 1.05 USD (approx 87 INR)
                currency="USD",
                benefits=[
                    "Lifetime AI platform access (Value: $500+/month)",
                    "Personal AI strategy audit and setup (Value: $800)",
                    "Priority support and integration assistance (Value: $600)",
                    "Direct influence on AI product roadmap",
                    "Early access to AI features (3-6 months early)",
                    "Exclusive founder mastermind community access",
                    "Custom AI agent configuration",
                    "Monthly AI strategy sessions"
                ],
                features=[
                    "Custom CRM integration setup",
                    "White-glove onboarding",
                    "Monthly founder calls",
                    "Product roadmap influence",
                    "Beta feature access"
                ],
                urgency_message="🔥 Only 12 founding spots remaining - Founder pricing ends soon!",
                scarcity_message="Join 25 founding entrepreneurs who get lifetime access to unified marketing intelligence + direct product influence. Regular price increases to $2,000+ after founding phase."
            )
            self.db.add(program)
            self.db.commit()
            self.db.refresh(program)
        
        return program
    
    def reserve_seat_atomic(
        self, 
        email: str, 
        name: str, 
        company: Optional[str] = None,
        lead_id: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Atomically reserve a seat with concurrency control
        Returns: (success, message, reservation_data)
        """
        try:
            # Start transaction
            program = self.get_or_create_active_program()
            
            # Check program status
            if not program.is_active:
                return False, "Co-creator program is not currently active", None
            
            if program.is_full:
                if program.waitlist_enabled:
                    program.add_to_waitlist()
                    self.db.commit()
                    return False, f"Program is full. Added to waitlist (position {program.waitlist_count})", None
                else:
                    return False, "Co-creator program is full and waitlist is not available", None
            
            # Atomic seat reservation with row locking
            self.db.execute(
                "SELECT * FROM co_creator_programs WHERE id = :id FOR UPDATE",
                {"id": program.id}
            )
            
            # Re-fetch to get latest state
            program = self.db.query(CoCreatorProgram).filter(CoCreatorProgram.id == program.id).first()
            
            # Double-check availability after lock
            if program.seats_remaining <= 0:
                return False, "No seats available", None
            
            # Reserve the seat
            if not program.reserve_seat():
                return False, "Unable to reserve seat", None
            
            # Find or create lead
            lead = None
            if lead_id:
                lead = self.db.query(Lead).filter(Lead.id == lead_id).first()
            elif email:
                lead = self.db.query(Lead).filter(Lead.email == email).first()
            
            # Find or create user
            user = None
            if user_id:
                user = self.db.query(User).filter(User.id == user_id).first()
            elif email:
                user = self.db.query(User).filter(User.email == email).first()
            
            # Create co-creator record
            co_creator = CoCreator(
                program_id=program.id,
                user_id=user.id if user else None,
                lead_id=lead.id if lead else None,
                seat_number=program.seats_filled,
                status="reserved"  # Will be activated upon payment
            )
            
            self.db.add(co_creator)
            
            # Update user co-creator status if user exists
            if user:
                user.activate_co_creator_status(
                    seat_number=co_creator.seat_number,
                    benefits="Lifetime access, priority support, feature influence"
                )
            
            self.db.commit()
            
            reservation_data = {
                "seat_number": co_creator.seat_number,
                "program_id": program.id,
                "co_creator_id": co_creator.id,
                "reservation_expires_at": datetime.utcnow() + timedelta(hours=24),
                "program_price": program.program_price,
                "currency": program.currency
            }
            
            return True, f"Seat #{co_creator.seat_number} reserved successfully", reservation_data
            
        except IntegrityError as e:
            self.db.rollback()
            return False, "Seat reservation conflict - please try again", None
        except Exception as e:
            self.db.rollback()
            return False, f"Failed to reserve seat: {str(e)}", None
    
    def activate_co_creator(self, co_creator_id: int, payment_confirmed: bool = True) -> Tuple[bool, str]:
        """Activate a co-creator after payment confirmation"""
        try:
            co_creator = self.db.query(CoCreator).filter(CoCreator.id == co_creator_id).first()
            if not co_creator:
                return False, "Co-creator not found"
            
            if co_creator.status == "active":
                return True, "Co-creator already active"
            
            if payment_confirmed:
                co_creator.status = "active"
                co_creator.joined_at = datetime.utcnow()
                
                # Update user status if exists
                if co_creator.user:
                    co_creator.user.activate_co_creator_status(
                        seat_number=co_creator.seat_number,
                        benefits="Lifetime access, priority support, feature influence"
                    )
                
                self.db.commit()
                return True, "Co-creator activated successfully"
            else:
                return False, "Payment not confirmed"
                
        except Exception as e:
            self.db.rollback()
            return False, f"Failed to activate co-creator: {str(e)}"
    
    def cancel_reservation(self, co_creator_id: int, reason: str = "user_cancelled") -> Tuple[bool, str]:
        """Cancel a seat reservation and release the seat"""
        try:
            co_creator = self.db.query(CoCreator).filter(CoCreator.id == co_creator_id).first()
            if not co_creator:
                return False, "Co-creator not found"
            
            if co_creator.status == "active":
                return False, "Cannot cancel active co-creator - use deactivate instead"
            
            program = co_creator.program
            
            # Release the seat
            if program.release_seat():
                # Remove co-creator record
                self.db.delete(co_creator)
                
                # Update user status if exists
                if co_creator.user:
                    co_creator.user.deactivate_co_creator_status()
                
                self.db.commit()
                return True, "Reservation cancelled and seat released"
            else:
                return False, "Failed to release seat"
                
        except Exception as e:
            self.db.rollback()
            return False, f"Failed to cancel reservation: {str(e)}"
    
    def get_program_status_with_urgency(self) -> Dict[str, Any]:
        """Get program status with updated urgency messaging"""
        program = self.get_or_create_active_program()
        
        # Update urgency messaging
        program.update_urgency_messaging()
        self.db.commit()
        
        return {
            "program_id": program.id,
            "seats_remaining": program.seats_remaining,
            "total_seats": program.total_seats,
            "seats_filled": program.seats_filled,
            "fill_percentage": program.fill_percentage,
            "urgency_level": program.urgency_level,
            "urgency_message": program.urgency_message,
            "scarcity_message": program.scarcity_message,
            "program_price": program.program_price,
            "currency": program.currency,
            "is_active": program.is_active,
            "is_full": program.is_full,
            "program_status": program.program_status,
            "waitlist_enabled": program.waitlist_enabled,
            "waitlist_count": program.waitlist_count,
            "is_nearly_full": program.is_nearly_full,
            "is_almost_full": program.is_almost_full
        }
    
    def get_co_creator_benefits(self) -> List[Dict[str, Any]]:
        """Get detailed co-creator program benefits"""
        program = self.get_or_create_active_program()
        
        return [
            {
                "category": "Access & Support",
                "benefits": [
                    {
                        "title": "Lifetime Platform Access",
                        "description": "Never lose access to Unitasa, regardless of future pricing changes",
                        "icon": "infinity"
                    },
                    {
                        "title": "Priority Integration Support",
                        "description": "White-glove assistance setting up your CRM integrations",
                        "icon": "support"
                    },
                    {
                        "title": "Direct Founder Engagement",
                        "description": "Monthly calls and direct communication with the founder",
                        "icon": "user"
                    }
                ]
            },
            {
                "category": "Influence & Recognition",
                "benefits": [
                    {
                        "title": "Feature Influence & Voting",
                        "description": "Shape the product roadmap and vote on new features",
                        "icon": "vote"
                    },
                    {
                        "title": "Exclusive Co-Creator Badge",
                        "description": "Recognition as a founding supporter in the platform",
                        "icon": "badge"
                    },
                    {
                        "title": "Product Credits",
                        "description": "Recognition in product documentation and marketing",
                        "icon": "star"
                    }
                ]
            },
            {
                "category": "Early Access",
                "benefits": [
                    {
                        "title": "Beta Feature Access",
                        "description": "First access to new integrations and AI capabilities",
                        "icon": "rocket"
                    },
                    {
                        "title": "Custom Integration Requests",
                        "description": "Priority consideration for specific CRM integration needs",
                        "icon": "settings"
                    },
                    {
                        "title": "Advanced Analytics",
                        "description": "Early access to advanced reporting and insights features",
                        "icon": "chart"
                    }
                ]
            }
        ]
    
    def get_qualified_leads_for_program(self, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """Get leads qualified for co-creator program with detailed analysis"""
        # Get qualified leads (warm and hot segments with readiness >= 41)
        leads_query = self.db.query(Lead).filter(
            Lead.readiness_segment.in_(["warm", "hot"]),
            Lead.crm_integration_readiness >= 41
        ).order_by(Lead.crm_integration_readiness.desc())
        
        total_count = leads_query.count()
        leads = leads_query.offset(offset).limit(limit).all()
        
        # Check which leads are already co-creators
        existing_co_creators = self.db.query(CoCreator.lead_id).filter(
            CoCreator.lead_id.in_([lead.id for lead in leads]),
            CoCreator.status.in_(["active", "reserved"])
        ).all()
        existing_co_creator_lead_ids = {cc.lead_id for cc in existing_co_creators}
        
        program = self.get_or_create_active_program()
        
        qualified_leads = []
        for lead in leads:
            is_already_co_creator = lead.id in existing_co_creator_lead_ids
            
            # Calculate conversion probability based on segment and scores
            base_probability = 60 if lead.readiness_segment == "warm" else 85
            score_bonus = (lead.crm_integration_readiness - 41) * 0.5
            conversion_probability = min(95, base_probability + score_bonus)
            
            qualified_leads.append({
                "id": lead.id,
                "email": lead.email,
                "company": lead.company,
                "full_name": lead.full_name,
                "crm_integration_readiness": lead.crm_integration_readiness,
                "readiness_segment": lead.readiness_segment,
                "current_crm_system": lead.current_crm_system,
                "segment_confidence": lead.segment_confidence,
                "factor_scores": {
                    "technical_capability": lead.technical_capability_score,
                    "business_maturity": lead.business_maturity_score,
                    "investment_capacity": lead.investment_capacity_score
                },
                "last_scored_at": lead.last_scored_at,
                "is_already_co_creator": is_already_co_creator,
                "recommended_action": "priority_onboarding" if lead.readiness_segment == "hot" else "co_creator_invitation",
                "estimated_conversion_probability": conversion_probability,
                "qualification_reasons": self._get_qualification_reasons(lead)
            })
        
        return {
            "program_status": {
                "seats_remaining": program.seats_remaining,
                "urgency_level": program.urgency_level,
                "program_price": program.program_price,
                "fill_percentage": program.fill_percentage
            },
            "qualification_summary": {
                "total_qualified": total_count,
                "returned_count": len(leads),
                "offset": offset,
                "limit": limit,
                "qualification_criteria": {
                    "min_readiness_score": 41,
                    "required_segments": ["warm", "hot"]
                }
            },
            "leads": qualified_leads
        }
    
    def _get_qualification_reasons(self, lead: Lead) -> List[str]:
        """Get reasons why a lead qualifies for co-creator program"""
        reasons = []
        
        if lead.crm_integration_readiness >= 71:
            reasons.append("High CRM integration readiness (71%+)")
        elif lead.crm_integration_readiness >= 41:
            reasons.append("Good CRM integration readiness (41%+)")
        
        if lead.technical_capability_score >= 70:
            reasons.append("Strong technical capabilities")
        
        if lead.business_maturity_score >= 70:
            reasons.append("Mature business operations")
        
        if lead.investment_capacity_score >= 60:
            reasons.append("Adequate investment capacity")
        
        if lead.current_crm_system and lead.current_crm_system != "none":
            reasons.append(f"Already using {lead.current_crm_system}")
        
        if lead.readiness_segment == "hot":
            reasons.append("Hot lead segment - priority candidate")
        
        return reasons
    
    def get_program_analytics(self) -> Dict[str, Any]:
        """Get comprehensive program analytics"""
        program = self.get_or_create_active_program()
        
        # Get co-creators
        co_creators = self.db.query(CoCreator).filter(CoCreator.program_id == program.id).all()
        active_co_creators = [cc for cc in co_creators if cc.is_active]
        
        # Calculate engagement metrics
        total_logins = sum(cc.total_logins for cc in co_creators)
        total_features_suggested = sum(cc.features_suggested for cc in co_creators)
        total_votes_cast = sum(cc.votes_cast for cc in co_creators)
        total_feature_influences = sum(cc.feature_influence_count for cc in co_creators)
        
        # Calculate time-based metrics
        avg_days_as_co_creator = sum(cc.days_as_co_creator for cc in co_creators) / len(co_creators) if co_creators else 0
        
        # Status distribution
        status_distribution = {}
        for cc in co_creators:
            status_distribution[cc.status] = status_distribution.get(cc.status, 0) + 1
        
        # Conversion metrics
        qualified_leads_count = self.db.query(Lead).filter(
            Lead.readiness_segment.in_(["warm", "hot"]),
            Lead.crm_integration_readiness >= 41
        ).count()
        
        conversion_rate = (len(co_creators) / qualified_leads_count * 100) if qualified_leads_count > 0 else 0
        
        return {
            "program_overview": {
                "program_id": program.id,
                "program_name": program.program_name,
                "total_seats": program.total_seats,
                "seats_filled": program.seats_filled,
                "seats_remaining": program.seats_remaining,
                "fill_percentage": program.fill_percentage,
                "program_status": program.program_status,
                "launch_date": program.launch_date,
                "filled_date": program.filled_date,
                "urgency_level": program.urgency_level
            },
            "co_creator_metrics": {
                "total_co_creators": len(co_creators),
                "active_co_creators": len(active_co_creators),
                "status_distribution": status_distribution,
                "average_days_as_co_creator": avg_days_as_co_creator
            },
            "engagement_metrics": {
                "total_logins": total_logins,
                "average_logins_per_co_creator": total_logins / len(co_creators) if co_creators else 0,
                "total_features_suggested": total_features_suggested,
                "total_votes_cast": total_votes_cast,
                "total_feature_influences": total_feature_influences,
                "engagement_rate": (len(active_co_creators) / len(co_creators) * 100) if co_creators else 0
            },
            "conversion_metrics": {
                "qualified_leads": qualified_leads_count,
                "co_creator_conversion_rate": conversion_rate,
                "page_views": program.page_views,
                "program_conversion_rate": program.conversion_rate,
                "average_time_to_convert": program.average_time_to_convert
            },
            "waitlist_metrics": {
                "waitlist_enabled": program.waitlist_enabled,
                "waitlist_count": program.waitlist_count
            }
        }
    
    def record_page_view(self, program_id: Optional[int] = None) -> bool:
        """Record a page view for analytics"""
        try:
            if program_id:
                program = self.db.query(CoCreatorProgram).filter(CoCreatorProgram.id == program_id).first()
            else:
                program = self.get_or_create_active_program()
            
            if program:
                program.record_page_view()
                self.db.commit()
                return True
            return False
            
        except Exception:
            self.db.rollback()
            return False
