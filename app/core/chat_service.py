"""
Chat Service for managing conversational AI interactions
Handles session management, message processing, and lead qualification
"""

import uuid
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.chat_session import ChatSession, ChatMessage
from app.models.lead import Lead
from app.models.user import User
from app.agents.stubs import get_conversational_agent, process_chat_message
from app.core.lead_scoring import lead_scoring_engine
from app.core.assessment_engine import assessment_engine
from app.core.voice_service import get_voice_service
from app.core.handoff_service import get_handoff_service


class ChatService:
    """Service for managing chat sessions and conversational AI"""

    def __init__(self, db: Session):
        self.db = db
        self.conversational_agent = get_conversational_agent()
        self.voice_service = get_voice_service()
        self.handoff_service = get_handoff_service(db)

    def create_session(self,
                       lead_id: Optional[int] = None,
                       user_id: Optional[int] = None,
                       ip_address: Optional[str] = None,
                       user_agent: Optional[str] = None,
                       referrer: Optional[str] = None,
                       context: Optional[Dict[str, Any]] = None) -> ChatSession:
        """Create a new chat session"""
        
        session = ChatSession(
            session_id=str(uuid.uuid4()),
            lead_id=lead_id,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            referrer=referrer,
            status="active"
        )
        
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        
        return session

    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Get chat session by ID"""
        return self.db.query(ChatSession).filter(
            ChatSession.session_id == session_id
        ).first()

    def get_active_session(self, session_id: str) -> Optional[ChatSession]:
        """Get active chat session by ID"""
        return self.db.query(ChatSession).filter(
            and_(
                ChatSession.session_id == session_id,
                ChatSession.status == "active"
            )
        ).first()

    async def process_message(self, 
                            session_id: str, 
                            content: str,
                            message_type: str = "text",
                            audio_duration: Optional[float] = None,
                            transcription_confidence: Optional[float] = None) -> Dict[str, Any]:
        """Process a user message and generate AI response"""
        
        # Get or create session
        session = self.get_active_session(session_id)
        if not session:
            # Try to create session if it doesn't exist
            session = self.create_session()
            session_id = session.session_id
        
        try:
            # Create user message record
            user_message = ChatMessage(
                session_id=session.id,
                message_id=str(uuid.uuid4()),
                content=content,
                message_type=message_type,
                sender="user",
                audio_duration_seconds=audio_duration,
                transcription_confidence=transcription_confidence
            )
            
            # Get conversation history
            conversation_history = self._get_conversation_history(session.id)
            
            # Process message with conversational agent
            start_time = datetime.utcnow()
            
            response_data = await process_chat_message(
                session_id=session_id,
                user_message=content,
                conversation_history=conversation_history
            )
            
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Create AI response message
            ai_message = ChatMessage(
                session_id=session.id,
                message_id=str(uuid.uuid4()),
                content=response_data["response"],
                message_type="text",
                sender="agent",
                response_time_ms=int(processing_time),
                model_used="conversational_agent",
                intent=response_data["analytics"].get("intent_distribution", {})
            )
            
            # Update session with analytics
            analytics = response_data["analytics"]
            session.update_qualification_data(
                score=analytics.get("qualification_score", 0.0),
                crm_interest=analytics.get("crm_interest_level", "unknown"),
                identified_crm=analytics.get("identified_crm"),
                pain_points=analytics.get("pain_points", [])
            )
            
            # Handle handoff request
            if response_data.get("requires_handoff"):
                handoff_reason = response_data.get("handoff_reason", "high_value_lead")
                session.request_handoff(handoff_reason)
                
                # Request handoff through handoff service
                await self.handoff_service.request_handoff(
                    session_id=session_id,
                    reason=handoff_reason,
                    priority="high" if analytics.get("qualification_score", 0) >= 80 else "medium",
                    context=analytics
                )
            
            # Update message counts
            session.increment_message_count(True)  # User message
            session.increment_message_count(False)  # Agent message
            
            # Save messages and session
            self.db.add(user_message)
            self.db.add(ai_message)
            self.db.commit()
            
            # Update lead qualification if associated
            if session.lead_id and analytics.get("qualification_score", 0) > 0:
                await self._update_lead_qualification(session.lead_id, analytics)
            
            return {
                "success": True,
                "response": response_data["response"],
                "session_id": session_id,
                "message_id": ai_message.message_id,
                "analytics": analytics,
                "requires_handoff": response_data.get("requires_handoff", False),
                "handoff_reason": response_data.get("handoff_reason"),
                "processing_time_ms": int(processing_time)
            }
            
        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "error": str(e),
                "session_id": session_id
            }

    def _get_conversation_history(self, session_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """Get conversation history for a session"""
        messages = self.db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).order_by(ChatMessage.timestamp.asc()).limit(limit).all()
        
        history = []
        for msg in messages:
            history.append({
                "role": "user" if msg.sender == "user" else "assistant",
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "message_type": msg.message_type,
                "intent": msg.intent
            })
        
        return history

    async def _update_lead_qualification(self, lead_id: int, analytics: Dict[str, Any]):
        """Update lead qualification based on chat analytics"""
        lead = self.db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            return
        
        # Update CRM integration readiness
        chat_score = analytics.get("qualification_score", 0.0)
        if chat_score > lead.crm_integration_readiness:
            lead.crm_integration_readiness = chat_score
        
        # Update CRM system if identified
        identified_crm = analytics.get("identified_crm")
        if identified_crm and not lead.current_crm_system:
            lead.current_crm_system = identified_crm
            lead.preferred_crm = identified_crm
        
        # Update pain points
        pain_points = analytics.get("pain_points", [])
        if pain_points:
            existing_pain_points = lead.pain_points or []
            combined_pain_points = list(set(existing_pain_points + pain_points))
            lead.pain_points = combined_pain_points
        
        # Update segment based on score
        if chat_score >= 71:
            lead.readiness_segment = "hot"
        elif chat_score >= 41:
            lead.readiness_segment = "warm"
        else:
            lead.readiness_segment = "cold"
        
        # Add chat-related tags
        lead.add_tag("chat_engaged")
        if chat_score >= 50:
            lead.add_tag("chat_qualified")
        
        lead.last_scored_at = datetime.utcnow()
        self.db.commit()

    def end_session(self, session_id: str, reason: str = "user_ended") -> bool:
        """End a chat session"""
        session = self.get_active_session(session_id)
        if not session:
            return False
        
        session.end_session(reason)
        
        # Clear agent context
        self.conversational_agent.clear_session_context(session_id)
        
        self.db.commit()
        return True

    def get_session_analytics(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get analytics for a chat session"""
        session = self.get_session(session_id)
        if not session:
            return None
        
        # Get message analytics
        messages = self.db.query(ChatMessage).filter(
            ChatMessage.session_id == session.id
        ).all()
        
        # Calculate metrics
        user_messages = [m for m in messages if m.sender == "user"]
        agent_messages = [m for m in messages if m.sender == "agent"]
        
        avg_response_time = 0
        if agent_messages:
            response_times = [m.response_time_ms for m in agent_messages if m.response_time_ms]
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Intent distribution
        intent_counts = {}
        for msg in messages:
            if msg.intent:
                intent_counts[msg.intent] = intent_counts.get(msg.intent, 0) + 1
        
        return {
            "session_id": session_id,
            "status": session.status,
            "duration_minutes": session.duration_minutes,
            "total_messages": session.total_messages,
            "user_messages": len(user_messages),
            "agent_messages": len(agent_messages),
            "qualification_score": session.qualification_score,
            "crm_interest_level": session.crm_interest_level,
            "identified_crm": session.identified_crm,
            "pain_points": session.pain_points,
            "requires_handoff": session.requires_human_handoff,
            "handoff_reason": session.handoff_reason,
            "avg_response_time_ms": avg_response_time,
            "intent_distribution": intent_counts,
            "lead_id": session.lead_id,
            "user_id": session.user_id
        }

    def get_sessions_requiring_handoff(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get sessions that require human handoff"""
        sessions = self.db.query(ChatSession).filter(
            and_(
                ChatSession.requires_human_handoff == True,
                ChatSession.status == "active"
            )
        ).order_by(ChatSession.handoff_requested_at.desc()).limit(limit).all()
        
        return [
            {
                "session_id": session.session_id,
                "handoff_reason": session.handoff_reason,
                "qualification_score": session.qualification_score,
                "crm_interest_level": session.crm_interest_level,
                "identified_crm": session.identified_crm,
                "handoff_requested_at": session.handoff_requested_at,
                "duration_minutes": session.duration_minutes,
                "total_messages": session.total_messages,
                "lead_id": session.lead_id
            }
            for session in sessions
        ]

    def get_chat_analytics_summary(self, 
                                 start_date: Optional[datetime] = None,
                                 end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Get summary analytics for chat system"""
        
        # Default to last 30 days if no dates provided
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # Base query for sessions in date range
        sessions_query = self.db.query(ChatSession).filter(
            and_(
                ChatSession.started_at >= start_date,
                ChatSession.started_at <= end_date
            )
        )
        
        total_sessions = sessions_query.count()
        active_sessions = sessions_query.filter(ChatSession.status == "active").count()
        ended_sessions = sessions_query.filter(ChatSession.status == "ended").count()
        
        # Qualification metrics
        qualified_sessions = sessions_query.filter(ChatSession.qualification_score >= 50).count()
        high_value_sessions = sessions_query.filter(ChatSession.qualification_score >= 80).count()
        
        # CRM interest distribution
        crm_interest_counts = self.db.query(
            ChatSession.crm_interest_level,
            self.db.func.count(ChatSession.id)
        ).filter(
            and_(
                ChatSession.started_at >= start_date,
                ChatSession.started_at <= end_date,
                ChatSession.crm_interest_level.isnot(None)
            )
        ).group_by(ChatSession.crm_interest_level).all()
        
        # Handoff metrics
        handoff_sessions = sessions_query.filter(ChatSession.requires_human_handoff == True).count()
        
        # Message metrics
        total_messages = self.db.query(ChatMessage).join(ChatSession).filter(
            and_(
                ChatSession.started_at >= start_date,
                ChatSession.started_at <= end_date
            )
        ).count()
        
        # Average session duration
        avg_duration = self.db.query(
            self.db.func.avg(ChatSession.session_duration_seconds)
        ).filter(
            and_(
                ChatSession.started_at >= start_date,
                ChatSession.started_at <= end_date,
                ChatSession.session_duration_seconds.isnot(None)
            )
        ).scalar() or 0
        
        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "session_metrics": {
                "total_sessions": total_sessions,
                "active_sessions": active_sessions,
                "ended_sessions": ended_sessions,
                "avg_duration_minutes": round(avg_duration / 60, 2) if avg_duration else 0
            },
            "qualification_metrics": {
                "qualified_sessions": qualified_sessions,
                "qualification_rate": (qualified_sessions / total_sessions * 100) if total_sessions > 0 else 0,
                "high_value_sessions": high_value_sessions,
                "high_value_rate": (high_value_sessions / total_sessions * 100) if total_sessions > 0 else 0
            },
            "crm_interest_distribution": {
                level: count for level, count in crm_interest_counts
            },
            "handoff_metrics": {
                "handoff_requests": handoff_sessions,
                "handoff_rate": (handoff_sessions / total_sessions * 100) if total_sessions > 0 else 0
            },
            "message_metrics": {
                "total_messages": total_messages,
                "avg_messages_per_session": round(total_messages / total_sessions, 2) if total_sessions > 0 else 0
            }
        }

    def associate_session_with_lead(self, session_id: str, lead_id: int) -> bool:
        """Associate a chat session with a lead"""
        session = self.get_session(session_id)
        if not session:
            return False
        
        # Verify lead exists
        lead = self.db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            return False
        
        session.lead_id = lead_id
        self.db.commit()
        return True

    def get_lead_chat_history(self, lead_id: int) -> List[Dict[str, Any]]:
        """Get chat history for a specific lead"""
        sessions = self.db.query(ChatSession).filter(
            ChatSession.lead_id == lead_id
        ).order_by(ChatSession.started_at.desc()).all()
        
        history = []
        for session in sessions:
            messages = self.db.query(ChatMessage).filter(
                ChatMessage.session_id == session.id
            ).order_by(ChatMessage.timestamp.asc()).all()
            
            history.append({
                "session_id": session.session_id,
                "started_at": session.started_at,
                "ended_at": session.ended_at,
                "status": session.status,
                "qualification_score": session.qualification_score,
                "messages": [
                    {
                        "content": msg.content,
                        "sender": msg.sender,
                        "timestamp": msg.timestamp,
                        "message_type": msg.message_type
                    }
                    for msg in messages
                ]
            })
        
        return history

    async def process_voice_message(self,
                                  session_id: str,
                                  audio_data: str,
                                  audio_format: str = "wav",
                                  language: str = "en-US") -> Dict[str, Any]:
        """Process a voice message with transcription"""
        try:
            # Transcribe voice message
            transcription_result = await self.voice_service.process_voice_message(
                audio_data=audio_data,
                audio_format=audio_format,
                language=language,
                session_id=session_id
            )
            
            if not transcription_result["success"]:
                return {
                    "success": False,
                    "error": transcription_result.get("error", "Voice transcription failed")
                }
            
            # Process transcribed text as regular message
            result = await self.process_message(
                session_id=session_id,
                content=transcription_result["transcribed_text"],
                message_type="voice",
                audio_duration=transcription_result.get("audio_duration_seconds"),
                transcription_confidence=transcription_result.get("transcription_confidence")
            )
            
            # Add voice-specific metadata
            if result["success"]:
                result["voice_metadata"] = {
                    "transcribed_text": transcription_result["transcribed_text"],
                    "transcription_confidence": transcription_result["transcription_confidence"],
                    "audio_duration_seconds": transcription_result["audio_duration_seconds"],
                    "audio_format": audio_format,
                    "language": language
                }
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Voice message processing failed: {str(e)}"
            }

    async def request_human_handoff(self,
                                  session_id: str,
                                  reason: str = "user_requested",
                                  context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Request human handoff for a session"""
        return await self.handoff_service.request_handoff(
            session_id=session_id,
            reason=reason,
            priority="medium",
            context=context
        )

    def get_handoff_queue(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get sessions requiring human handoff"""
        return self.handoff_service.get_handoff_queue(limit=limit)

    async def assign_to_human_agent(self,
                                   session_id: str,
                                   agent_id: str,
                                   agent_name: str) -> Dict[str, Any]:
        """Assign session to human agent"""
        return await self.handoff_service.assign_agent(
            session_id=session_id,
            agent_id=agent_id,
            agent_name=agent_name
        )
