"""
Conversational AI Agent for Landing Page Chat Support
Provides real-time assistance, CRM guidance, and lead qualification
"""

import uuid
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage

from app.agents.base_agent import BaseAgent
from app.agents.state import MarketingAgentState, update_state_timestamp
from app.llm.router import get_optimal_llm
from app.rag.lcel_chains import get_confidence_rag_chain
from app.core.assessment_engine import assessment_engine
from app.core.lead_scoring import lead_scoring_engine
from app.core.crm_knowledge_base import get_crm_knowledge_base, query_crm_knowledge


class ConversationalAgent(BaseAgent):
    """Agent for handling general conversation and routing"""

    def __init__(self, llm=None):
        # Get optimal LLM for conversational tasks
        if not llm:
            llm = get_optimal_llm("Provide helpful conversational responses about CRM integration and marketing automation")
        
        super().__init__(
            name="conversational_agent",
            llm=llm,
            tools=[],
            memory=None
        )
        
        # Initialize RAG chain for knowledge base queries
        self.rag_chain = get_confidence_rag_chain()
        
        # Initialize CRM knowledge base
        self.crm_kb = get_crm_knowledge_base()
        
        # Conversation context tracking
        self.conversation_contexts = {}
        
        # Intent classification patterns
        self.intent_patterns = {
            "crm_inquiry": ["crm", "customer relationship", "salesforce", "hubspot", "pipedrive", "zoho", "monday"],
            "integration_help": ["integrate", "connect", "setup", "api", "webhook", "sync"],
            "assessment_help": ["assessment", "questions", "evaluate", "score", "readiness"],
            "pricing_inquiry": ["price", "cost", "payment", "co-creator", "program", "$497", "founder", "discount"],
            "technical_support": ["technical", "api", "developer", "documentation", "sdk"],
            "general_inquiry": ["what is", "how does", "tell me about", "explain"]
        }

    def get_system_prompt(self) -> ChatPromptTemplate:
        """Get conversational agent system prompt"""
        return ChatPromptTemplate.from_messages([
            ("system", """You are a helpful AI assistant for Unitasa, a Unified Marketing Intelligence Platform that replaces fragmented marketing tools with one complete solution. Your role is to:
1. Answer general questions about Unitasa's capabilities
2. Guide users to specific features (Analysis, Ad Management, Lead Gen)
3. Collect initial requirements for other agents
4. Maintain a helpful and professional tone

Unitasa Capabilities:
- Brand Analysis: Website auditing, brand voice detection, competitor analysis
- Ad Management: Multi-channel campaign creation and optimization
- Lead Generation: B2B lead discovery and qualification
- Content Strategy: AI-driven content planning and generation

Current conversation context: {context}
User's detected intent: {intent}
CRM interest level: {crm_interest}"""),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

    def create_agent(self):
        """Create the conversational agent chain"""
        prompt = self.get_system_prompt()
        
        # Create the main conversation chain
        conversation_chain = (
            prompt
            | self.llm
            | StrOutputParser()
        )
        
        return conversation_chain

    def build_input(self, state: MarketingAgentState) -> Dict[str, Any]:
        """Build input for conversational agent"""
        session_id = state.get("session_id", "unknown")
        user_message = state.get("user_message", "")
        conversation_history = state.get("conversation_history", [])
        
        # Get or create conversation context
        context = self.conversation_contexts.get(session_id, {
            "session_id": session_id,
            "started_at": datetime.utcnow().isoformat(),
            "message_count": 0,
            "identified_crm": None,
            "qualification_score": 0.0,
            "intent_history": [],
            "pain_points": [],
            "crm_interest_level": "unknown"
        })
        
        # Detect intent from user message
        detected_intent = self._detect_intent(user_message)
        context["intent_history"].append(detected_intent)
        context["message_count"] += 1
        
        # Update qualification score based on conversation
        qualification_data = self._analyze_qualification_signals(user_message, context)
        context.update(qualification_data)
        
        # Store updated context
        self.conversation_contexts[session_id] = context
        
        return {
            "input": user_message,
            "context": self._format_context(context, conversation_history),
            "intent": detected_intent,
            "crm_interest": context.get("crm_interest_level", "unknown")
        }

    def update_state(self, state: MarketingAgentState, result) -> MarketingAgentState:
        """Update state with conversation results"""
        session_id = state.get("session_id", "unknown")
        context = self.conversation_contexts.get(session_id, {})
        
        # Add agent response to conversation history
        conversation_history = state.get("conversation_history", [])
        conversation_history.append({
            "role": "user",
            "content": state.get("user_message", ""),
            "timestamp": datetime.utcnow().isoformat()
        })
        conversation_history.append({
            "role": "assistant", 
            "content": result,
            "timestamp": datetime.utcnow().isoformat(),
            "intent": context.get("intent_history", [])[-1] if context.get("intent_history") else "general"
        })
        
        # Update state
        state["conversation_history"] = conversation_history
        state["agent_response"] = result
        state["conversation_context"] = context
        state["qualification_score"] = context.get("qualification_score", 0.0)
        state["detected_intent"] = context.get("intent_history", [])[-1] if context.get("intent_history") else "general"
        
        # Determine if handoff is needed
        if self._should_request_handoff(context, result):
            state["requires_handoff"] = True
            state["handoff_reason"] = self._get_handoff_reason(context)
        
        return update_state_timestamp(state)

    def _detect_intent(self, message: str) -> str:
        """Detect user intent from message"""
        message_lower = message.lower()
        
        # Check each intent pattern
        for intent, keywords in self.intent_patterns.items():
            if any(keyword in message_lower for keyword in keywords):
                return intent
        
        return "general_inquiry"

    def _analyze_qualification_signals(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze message for lead qualification signals"""
        message_lower = message.lower()
        updates = {}
        
        # CRM system identification
        crm_mentions = {
            "salesforce": ["salesforce", "sfdc"],
            "hubspot": ["hubspot", "hub spot"],
            "pipedrive": ["pipedrive", "pipe drive"],
            "zoho": ["zoho"],
            "monday": ["monday.com", "monday"],
            "neuracrm": ["neuracrm", "neura crm"],
            "other": ["custom crm", "proprietary", "in-house"]
        }
        
        for crm, keywords in crm_mentions.items():
            if any(keyword in message_lower for keyword in keywords):
                updates["identified_crm"] = crm
                break
        
        # Business maturity signals
        maturity_signals = {
            "high": ["enterprise", "large team", "multiple departments", "complex workflows"],
            "medium": ["growing business", "scaling", "team of", "established"],
            "low": ["startup", "small business", "just starting", "new company"]
        }
        
        # Investment capacity signals
        investment_signals = {
            "high": ["budget approved", "ready to invest", "enterprise budget"],
            "medium": ["considering investment", "budget planning", "quarterly budget"],
            "low": ["tight budget", "cost-conscious", "free trial", "limited budget"]
        }
        
        # Pain points identification
        pain_points = []
        pain_point_keywords = {
            "manual_processes": ["manual", "time-consuming", "repetitive tasks"],
            "data_silos": ["disconnected", "data silos", "not integrated"],
            "lead_leakage": ["losing leads", "follow-up issues", "missed opportunities"],
            "reporting_gaps": ["no visibility", "reporting issues", "can't track"],
            "scaling_challenges": ["can't scale", "growth challenges", "team overwhelmed"]
        }
        
        for pain_point, keywords in pain_point_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                pain_points.append(pain_point)
        
        if pain_points:
            existing_pain_points = context.get("pain_points", [])
            updates["pain_points"] = list(set(existing_pain_points + pain_points))
        
        # Calculate qualification score
        current_score = context.get("qualification_score", 0.0)
        score_adjustments = 0
        
        # CRM identification adds points
        if updates.get("identified_crm"):
            score_adjustments += 15
        
        # Pain points add points
        score_adjustments += len(pain_points) * 10
        
        # Business maturity signals
        for level, keywords in maturity_signals.items():
            if any(keyword in message_lower for keyword in keywords):
                if level == "high":
                    score_adjustments += 20
                elif level == "medium":
                    score_adjustments += 10
                break
        
        # Investment capacity signals
        for level, keywords in investment_signals.items():
            if any(keyword in message_lower for keyword in keywords):
                if level == "high":
                    score_adjustments += 25
                elif level == "medium":
                    score_adjustments += 15
                break
        
        # Update qualification score
        new_score = min(100.0, current_score + score_adjustments)
        updates["qualification_score"] = new_score
        
        # Determine CRM interest level
        if new_score >= 70:
            updates["crm_interest_level"] = "high"
        elif new_score >= 40:
            updates["crm_interest_level"] = "medium"
        else:
            updates["crm_interest_level"] = "low"
        
        return updates

    def _format_context(self, context: Dict[str, Any], conversation_history: List[Dict[str, Any]]) -> str:
        """Format conversation context for prompt"""
        context_parts = []
        
        # Session info
        context_parts.append(f"Session: {context.get('message_count', 0)} messages")
        
        # Identified CRM
        if context.get("identified_crm"):
            context_parts.append(f"Identified CRM: {context['identified_crm']}")
        
        # Qualification score
        score = context.get("qualification_score", 0.0)
        context_parts.append(f"Qualification Score: {score:.1f}/100")
        
        # Pain points
        pain_points = context.get("pain_points", [])
        if pain_points:
            context_parts.append(f"Pain Points: {', '.join(pain_points)}")
        
        # Recent conversation
        if conversation_history:
            recent_messages = conversation_history[-4:]  # Last 4 messages
            context_parts.append("Recent conversation:")
            for msg in recent_messages:
                role = "User" if msg["role"] == "user" else "Assistant"
                content = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
                context_parts.append(f"  {role}: {content}")
        
        return "\n".join(context_parts)

    def _should_request_handoff(self, context: Dict[str, Any], response: str) -> bool:
        """Determine if human handoff is needed"""
        # High-value leads should be handed off
        if context.get("qualification_score", 0) >= 80:
            return True
        
        # Complex technical questions
        if "technical" in context.get("intent_history", [])[-1:]:
            technical_keywords = ["api documentation", "custom integration", "enterprise setup"]
            if any(keyword in response.lower() for keyword in technical_keywords):
                return True
        
        # Pricing negotiations or enterprise inquiries
        enterprise_signals = ["enterprise", "custom pricing", "volume discount", "contract"]
        if any(signal in response.lower() for signal in enterprise_signals):
            return True
        
        return False

    def _get_handoff_reason(self, context: Dict[str, Any]) -> str:
        """Get reason for handoff request"""
        score = context.get("qualification_score", 0)
        
        if score >= 80:
            return "high_value_lead"
        elif "technical" in context.get("intent_history", [])[-1:]:
            return "technical_complexity"
        else:
            return "enterprise_inquiry"

    async def get_rag_response(self, query: str) -> Dict[str, Any]:
        """Get response from RAG system for knowledge-based queries"""
        try:
            return await self.rag_chain.ainvoke({"question": query})
        except Exception as e:
            self.log_agent_activity("rag_query_failed", {"error": str(e), "query": query[:100]})
            return {
                "answer": "I apologize, but I'm having trouble accessing our knowledge base right now. Let me help you with what I know directly.",
                "confidence": 0.0
            }

    def get_conversation_analytics(self, session_id: str) -> Dict[str, Any]:
        """Get analytics for a conversation session"""
        context = self.conversation_contexts.get(session_id, {})
        
        return {
            "session_id": session_id,
            "message_count": context.get("message_count", 0),
            "qualification_score": context.get("qualification_score", 0.0),
            "crm_interest_level": context.get("crm_interest_level", "unknown"),
            "identified_crm": context.get("identified_crm"),
            "pain_points": context.get("pain_points", []),
            "intent_distribution": self._get_intent_distribution(context.get("intent_history", [])),
            "session_duration": self._calculate_session_duration(context),
            "requires_handoff": self._should_request_handoff(context, "")
        }

    def _get_intent_distribution(self, intent_history: List[str]) -> Dict[str, int]:
        """Get distribution of intents in conversation"""
        distribution = {}
        for intent in intent_history:
            distribution[intent] = distribution.get(intent, 0) + 1
        return distribution

    def _calculate_session_duration(self, context: Dict[str, Any]) -> float:
        """Calculate session duration in minutes"""
        started_at_str = context.get("started_at")
        if not started_at_str:
            return 0.0
        
        try:
            started_at = datetime.fromisoformat(started_at_str)
            duration = (datetime.utcnow() - started_at).total_seconds() / 60
            return round(duration, 2)
        except:
            return 0.0

    def clear_session_context(self, session_id: str):
        """Clear conversation context for a session"""
        if session_id in self.conversation_contexts:
            del self.conversation_contexts[session_id]


# Global conversational agent instance
_conversational_agent = None


def get_conversational_agent() -> ConversationalAgent:
    """Get the global conversational agent instance"""
    global _conversational_agent
    if _conversational_agent is None:
        _conversational_agent = ConversationalAgent()
    return _conversational_agent


async def process_chat_message(session_id: str, user_message: str, conversation_history: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Process a chat message and return response with analytics"""
    agent = get_conversational_agent()
    
    # Create state for processing
    state = MarketingAgentState(
        campaign_config={"name": "chat_session"},
        current_agent="conversational_agent",
        session_id=session_id,
        user_message=user_message,
        conversation_history=conversation_history or []
    )
    
    # Process message
    result_state = await agent.execute(state)
    
    # Get conversation analytics
    analytics = agent.get_conversation_analytics(session_id)
    
    return {
        "response": result_state.get("agent_response", "I apologize, but I'm having trouble processing your message right now."),
        "session_id": session_id,
        "analytics": analytics,
        "requires_handoff": result_state.get("requires_handoff", False),
        "handoff_reason": result_state.get("handoff_reason"),
        "conversation_context": result_state.get("conversation_context", {})
    }
