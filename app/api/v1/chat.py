"""
Chat API endpoints for conversational AI agent system
"""

import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, Request, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.core.database import get_db, get_sync_db
from app.core.chat_service import ChatService
from app.models.chat_session import ChatSession, ChatMessage
from app.models.lead import Lead


router = APIRouter()


# Pydantic models for API requests/responses
class ChatSessionCreateRequest(BaseModel):
    """Request to create a new chat session"""
    lead_id: Optional[int] = None
    user_id: Optional[int] = None
    user_agent: Optional[str] = None
    referrer: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class ChatSessionResponse(BaseModel):
    """Chat session response"""
    session_id: str
    status: str
    started_at: datetime
    lead_id: Optional[int]
    user_id: Optional[int]
    qualification_score: float
    crm_interest_level: str
    identified_crm: Optional[str]
    total_messages: int


class ChatMessageRequest(BaseModel):
    """Request to send a chat message"""
    content: str = Field(..., min_length=1, max_length=2000)
    message_type: str = Field(default="text")
    audio_duration_seconds: Optional[float] = None
    transcription_confidence: Optional[float] = None


class ChatMessageResponse(BaseModel):
    """Chat message response"""
    success: bool
    response: str
    session_id: str
    message_id: str
    processing_time_ms: int
    requires_handoff: bool
    handoff_reason: Optional[str]
    analytics: Dict[str, Any]


class ChatHistoryResponse(BaseModel):
    """Chat history response"""
    session_id: str
    messages: List[Dict[str, Any]]
    total_messages: int
    session_analytics: Dict[str, Any]


class VoiceMessageRequest(BaseModel):
    """Request for voice-to-text message processing"""
    audio_data: str  # Base64 encoded audio
    audio_format: str = "wav"
    language: str = "en-US"


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]

    async def send_message(self, session_id: str, message: dict):
        if session_id in self.active_connections:
            try:
                await self.active_connections[session_id].send_json(message)
            except:
                # Connection closed, remove it
                self.disconnect(session_id)

    async def broadcast_to_session(self, session_id: str, message: dict):
        await self.send_message(session_id, message)


manager = ConnectionManager()


@router.post("/initialize")
async def initialize_chat_session(
    request: Optional[ChatSessionCreateRequest] = None,
    http_request: Request = None
) -> Dict[str, Any]:
    """
    Create a new chat session (simplified version)
    """
    try:
        import uuid
        from datetime import datetime
        
        # Generate a simple session ID
        session_id = str(uuid.uuid4())
        
        # Return a basic session response
        response_data = {
            "session_id": session_id,
            "status": "active",
            "started_at": datetime.utcnow().isoformat(),
            "lead_id": None,
            "user_id": None,
            "qualification_score": 0.0,
            "crm_interest_level": "unknown",
            "identified_crm": None,
            "total_messages": 0,
            "messages": [],
            "id": session_id  # Add id field that frontend expects
        }

        return response_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create chat session: {str(e)}")


@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
async def get_chat_session(
    session_id: str,
    db: Session = Depends(get_sync_db)
) -> ChatSessionResponse:
    """
    Get chat session details
    """
    chat_service = ChatService(db)
    session = chat_service.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    return ChatSessionResponse(
        session_id=session.session_id,
        status=session.status,
        started_at=session.started_at,
        lead_id=session.lead_id,
        user_id=session.user_id,
        qualification_score=session.qualification_score,
        crm_interest_level=session.crm_interest_level,
        identified_crm=session.identified_crm,
        total_messages=session.total_messages
    )


@router.post("/sessions/{session_id}/messages", response_model=ChatMessageResponse)
async def send_chat_message(
    session_id: str,
    request: ChatMessageRequest,
    db: Session = Depends(get_sync_db)
) -> ChatMessageResponse:
    """
    Send a message to the conversational AI agent
    """
    try:
        chat_service = ChatService(db)
        
        result = await chat_service.process_message(
            session_id=session_id,
            content=request.content,
            message_type=request.message_type,
            audio_duration=request.audio_duration_seconds,
            transcription_confidence=request.transcription_confidence
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error", "Failed to process message"))
        
        # Send real-time update via WebSocket if connected
        await manager.send_message(session_id, {
            "type": "message_response",
            "response": result["response"],
            "analytics": result["analytics"],
            "requires_handoff": result["requires_handoff"]
        })
        
        return ChatMessageResponse(
            success=result["success"],
            response=result["response"],
            session_id=result["session_id"],
            message_id=result["message_id"],
            processing_time_ms=result["processing_time_ms"],
            requires_handoff=result["requires_handoff"],
            handoff_reason=result.get("handoff_reason"),
            analytics=result["analytics"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process message: {str(e)}")


@router.get("/sessions/{session_id}/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    session_id: str,
    limit: int = 50,
    db: Session = Depends(get_sync_db)
) -> ChatHistoryResponse:
    """
    Get chat history for a session
    """
    chat_service = ChatService(db)
    session = chat_service.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    # Get messages
    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session.id
    ).order_by(ChatMessage.timestamp.asc()).limit(limit).all()
    
    # Get session analytics
    analytics = chat_service.get_session_analytics(session_id)
    
    return ChatHistoryResponse(
        session_id=session_id,
        messages=[
            {
                "message_id": msg.message_id,
                "content": msg.content,
                "sender": msg.sender,
                "message_type": msg.message_type,
                "timestamp": msg.timestamp,
                "intent": msg.intent,
                "confidence": msg.confidence,
                "response_time_ms": msg.response_time_ms
            }
            for msg in messages
        ],
        total_messages=len(messages),
        session_analytics=analytics or {}
    )


@router.post("/sessions/{session_id}/end")
async def end_chat_session(
    session_id: str,
    reason: str = "user_ended",
    db: Session = Depends(get_sync_db)
) -> Dict[str, Any]:
    """
    End a chat session
    """
    chat_service = ChatService(db)
    success = chat_service.end_session(session_id, reason)
    
    if not success:
        raise HTTPException(status_code=404, detail="Chat session not found or already ended")
    
    # Notify via WebSocket
    await manager.send_message(session_id, {
        "type": "session_ended",
        "reason": reason
    })
    
    # Disconnect WebSocket
    manager.disconnect(session_id)
    
    return {
        "success": True,
        "message": "Chat session ended successfully",
        "session_id": session_id,
        "reason": reason
    }


@router.post("/sessions/{session_id}/voice", response_model=ChatMessageResponse)
async def process_voice_message(
    session_id: str,
    request: VoiceMessageRequest,
    db: Session = Depends(get_db)
) -> ChatMessageResponse:
    """
    Process voice-to-text message with transcription
    """
    try:
        chat_service = ChatService(db)
        
        # Process voice message with transcription
        result = await chat_service.process_voice_message(
            session_id=session_id,
            audio_data=request.audio_data,
            audio_format=request.audio_format,
            language=request.language
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error", "Failed to process voice message"))
        
        # Send real-time update via WebSocket if connected
        await manager.send_message(session_id, {
            "type": "voice_message_response",
            "response": result["response"],
            "voice_metadata": result.get("voice_metadata", {}),
            "analytics": result["analytics"],
            "requires_handoff": result["requires_handoff"]
        })
        
        return ChatMessageResponse(
            success=result["success"],
            response=result["response"],
            session_id=result["session_id"],
            message_id=result["message_id"],
            processing_time_ms=result["processing_time_ms"],
            requires_handoff=result["requires_handoff"],
            handoff_reason=result.get("handoff_reason"),
            analytics=result["analytics"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process voice message: {str(e)}")


@router.post("/sessions/{session_id}/associate-lead")
async def associate_session_with_lead(
    session_id: str,
    lead_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Associate a chat session with a lead
    """
    chat_service = ChatService(db)
    success = chat_service.associate_session_with_lead(session_id, lead_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Chat session or lead not found")
    
    return {
        "success": True,
        "message": "Session associated with lead successfully",
        "session_id": session_id,
        "lead_id": lead_id
    }


@router.get("/sessions/{session_id}/analytics")
async def get_session_analytics(
    session_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get detailed analytics for a chat session
    """
    chat_service = ChatService(db)
    analytics = chat_service.get_session_analytics(session_id)
    
    if not analytics:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    return analytics


@router.post("/sessions/{session_id}/request-handoff")
async def request_human_handoff(
    session_id: str,
    reason: str = "user_requested",
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Request human handoff for a chat session
    """
    try:
        chat_service = ChatService(db)
        result = await chat_service.request_human_handoff(
            session_id=session_id,
            reason=reason
        )
        
        if result["success"]:
            # Notify via WebSocket
            await manager.send_message(session_id, {
                "type": "handoff_requested",
                "reason": reason,
                "estimated_response_time": result.get("estimated_response_time")
            })
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to request handoff: {str(e)}")


@router.get("/handoff-queue")
async def get_handoff_queue(
    limit: int = 50,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get sessions requiring human handoff
    """
    chat_service = ChatService(db)
    sessions = chat_service.get_handoff_queue(limit)
    
    return {
        "total_sessions": len(sessions),
        "sessions": sessions
    }


@router.post("/handoff/{session_id}/assign")
async def assign_to_human_agent(
    session_id: str,
    agent_id: str,
    agent_name: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Assign a handoff session to a human agent
    """
    try:
        chat_service = ChatService(db)
        result = await chat_service.assign_to_human_agent(
            session_id=session_id,
            agent_id=agent_id,
            agent_name=agent_name
        )
        
        if result["success"]:
            # Notify via WebSocket
            await manager.send_message(session_id, {
                "type": "agent_assigned",
                "agent_name": agent_name,
                "message": f"You've been connected to {agent_name}"
            })
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to assign agent: {str(e)}")


@router.get("/handoff/analytics")
async def get_handoff_analytics(
    days: int = 30,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get handoff analytics and metrics
    """
    try:
        from datetime import datetime, timedelta
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        chat_service = ChatService(db)
        analytics = chat_service.handoff_service.get_handoff_analytics(start_date, end_date)
        
        return analytics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get handoff analytics: {str(e)}")


@router.get("/monitoring/performance")
async def get_chat_performance_metrics(
    days: int = 7,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get chat system performance metrics
    """
    try:
        from app.core.chat_monitoring import get_chat_monitoring_service
        from datetime import datetime, timedelta
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        monitoring_service = get_chat_monitoring_service(db)
        metrics = monitoring_service.get_chat_performance_metrics(start_date, end_date)
        
        return metrics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance metrics: {str(e)}")


@router.get("/monitoring/agent-effectiveness")
async def get_agent_effectiveness_metrics(
    days: int = 7,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get conversational agent effectiveness metrics
    """
    try:
        from app.core.chat_monitoring import get_chat_monitoring_service
        from datetime import datetime, timedelta
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        monitoring_service = get_chat_monitoring_service(db)
        metrics = monitoring_service.get_agent_effectiveness_metrics(start_date, end_date)
        
        return metrics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get effectiveness metrics: {str(e)}")


@router.get("/monitoring/health")
async def get_chat_system_health(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get current chat system health status
    """
    try:
        from app.core.chat_monitoring import get_chat_monitoring_service
        
        monitoring_service = get_chat_monitoring_service(db)
        health_status = monitoring_service.get_system_health_status()
        
        return health_status
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get system health: {str(e)}")


@router.get("/monitoring/daily-summary")
async def get_daily_chat_summary(
    date: Optional[str] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get daily summary of chat activity
    """
    try:
        from app.core.chat_monitoring import get_chat_monitoring_service
        from datetime import datetime
        
        target_date = None
        if date:
            target_date = datetime.fromisoformat(date).date()
        
        monitoring_service = get_chat_monitoring_service(db)
        summary = monitoring_service.get_daily_summary(target_date)
        
        return summary
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get daily summary: {str(e)}")


@router.get("/analytics/summary")
async def get_chat_analytics_summary(
    days: int = 30,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get summary analytics for chat system
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    chat_service = ChatService(db)
    analytics = chat_service.get_chat_analytics_summary(start_date, end_date)
    
    return analytics


@router.get("/leads/{lead_id}/chat-history")
async def get_lead_chat_history(
    lead_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get chat history for a specific lead
    """
    # Verify lead exists
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    chat_service = ChatService(db)
    history = chat_service.get_lead_chat_history(lead_id)
    
    return {
        "lead_id": lead_id,
        "total_sessions": len(history),
        "chat_history": history
    }


# WebSocket endpoint for real-time chat
@router.websocket("/sessions/{session_id}/ws")
async def websocket_chat_endpoint(websocket: WebSocket, session_id: str, db: Session = Depends(get_db)):
    """
    WebSocket endpoint for real-time chat communication
    """
    await manager.connect(websocket, session_id)
    chat_service = ChatService(db)
    
    try:
        # Verify session exists
        session = chat_service.get_session(session_id)
        if not session:
            await websocket.send_json({
                "type": "error",
                "message": "Chat session not found"
            })
            await websocket.close()
            return
        
        # Send connection confirmation
        await websocket.send_json({
            "type": "connected",
            "session_id": session_id,
            "message": "WebSocket connection established"
        })
        
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            
            if data.get("type") == "message":
                # Process the message
                result = await chat_service.process_message(
                    session_id=session_id,
                    content=data.get("content", ""),
                    message_type=data.get("message_type", "text")
                )
                
                if result["success"]:
                    # Send response back
                    await websocket.send_json({
                        "type": "message_response",
                        "response": result["response"],
                        "message_id": result["message_id"],
                        "processing_time_ms": result["processing_time_ms"],
                        "analytics": result["analytics"],
                        "requires_handoff": result["requires_handoff"],
                        "handoff_reason": result.get("handoff_reason")
                    })
                else:
                    await websocket.send_json({
                        "type": "error",
                        "message": result.get("error", "Failed to process message")
                    })
            
            elif data.get("type") == "voice_message":
                # Process voice message
                result = await chat_service.process_voice_message(
                    session_id=session_id,
                    audio_data=data.get("audio_data", ""),
                    audio_format=data.get("audio_format", "wav"),
                    language=data.get("language", "en-US")
                )
                
                if result["success"]:
                    await websocket.send_json({
                        "type": "voice_message_response",
                        "response": result["response"],
                        "message_id": result["message_id"],
                        "processing_time_ms": result["processing_time_ms"],
                        "voice_metadata": result.get("voice_metadata", {}),
                        "analytics": result["analytics"],
                        "requires_handoff": result["requires_handoff"],
                        "handoff_reason": result.get("handoff_reason")
                    })
                else:
                    await websocket.send_json({
                        "type": "error",
                        "message": result.get("error", "Failed to process voice message")
                    })
            
            elif data.get("type") == "request_handoff":
                # Request human handoff
                result = await chat_service.request_human_handoff(
                    session_id=session_id,
                    reason=data.get("reason", "user_requested")
                )
                
                if result["success"]:
                    await websocket.send_json({
                        "type": "handoff_requested",
                        "message": result["message"],
                        "estimated_response_time": result.get("estimated_response_time")
                    })
                else:
                    await websocket.send_json({
                        "type": "error",
                        "message": result.get("error", "Failed to request handoff")
                    })
            
            elif data.get("type") == "ping":
                # Respond to ping
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            elif data.get("type") == "end_session":
                # End the session
                chat_service.end_session(session_id, "user_ended")
                await websocket.send_json({
                    "type": "session_ended",
                    "message": "Session ended successfully"
                })
                break
                
    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": f"WebSocket error: {str(e)}"
        })
        manager.disconnect(session_id)


@router.get("/health")
async def chat_health_check() -> Dict[str, Any]:
    """
    Health check endpoint for chat service
    """
    return {
        "status": "healthy",
        "service": "chat_service",
        "message": "Chat service is operational",
        "timestamp": datetime.utcnow().isoformat()
    }
