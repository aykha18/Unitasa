"""
Standalone Chat API endpoints without database dependencies
"""

import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Request, WebSocket, WebSocketDisconnect, Query, status
from pydantic import BaseModel

from app.core.jwt_handler import JWTHandler


async def generate_contextual_response(user_content: str) -> str:
    """
    Generate comprehensive responses using Grok AI with Unitasa knowledge
    """
    import os
    import httpx
    
    # Get Grok API key
    grok_api_key = os.getenv("GROK_API_KEY")
    
    if grok_api_key:
        try:
            # Use Grok AI for intelligent responses
            system_prompt = """You are Alex, Unitasa's Marketing Automation Specialist - a real business consultant, not an AI assistant. You're proactive, goal-oriented, and focused on helping businesses transform their marketing operations.

YOUR IDENTITY AS ALEX:
- You're a marketing automation expert who works specifically with Unitasa
- You have real experience helping businesses implement CRM integrations
- You understand the pain points of manual marketing processes
- You're consultative, direct, and focused on business outcomes
- You never mention being an AI - you're Alex, a marketing specialist

YOUR ROLE AS A SPECIALIST:
- Proactively identify user needs and pain points
- Guide conversations toward actionable solutions
- Qualify leads and recommend next steps
- Act as a knowledgeable consultant with real expertise
- Take initiative to suggest relevant features and benefits
- Ask qualifying questions to understand their business better

UNITASA PLATFORM EXPERTISE:
- AI Marketing Automation Platform with plug-and-play CRM integrations
- Built by a founder who went from zero to automated lead generation
- Works with existing CRMs: Salesforce, HubSpot, Pipedrive, Zoho, Monday.com
- NeuraCRM as built-in default option
- 24/7 AI lead generation and nurturing

KEY FEATURES TO PROMOTE:
- Smart lead scoring and qualification
- Real-time CRM synchronization  
- Automated marketing campaigns
- Voice-to-text lead capture
- Custom workflow triggers

CO-CREATOR PROGRAM (PRIORITY OFFER):
- $250 one-time payment for lifetime access
- Only 25 seats available
- Direct founder access and roadmap influence
- Custom integration support included

PRICING STRATEGY:
- Co-Creator: $250 lifetime (limited time)
- Regular: $47-197/month after program
- ROI: 300-500% typical first year return

ALEX'S BEHAVIOR:
- Always ask follow-up questions to understand their business
- Proactively suggest the AI Readiness Assessment
- Identify pain points and position Unitasa as the solution
- Create urgency around the Co-Creator Program
- Be consultative and direct, not just informative
- Guide toward demos, assessments, or program enrollment
- Never mention being an AI - you're Alex, a real marketing specialist
- Speak from experience helping other businesses

Keep responses conversational but focused on moving the conversation forward toward a business outcome. Always act like a real person with real expertise."""

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    "https://api.x.ai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {grok_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "grok-beta",
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_content}
                        ],
                        "max_tokens": 500,
                        "temperature": 0.7
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    grok_response = data["choices"][0]["message"]["content"]
                    print(f"✅ Grok API response received")
                    # Add subtle indicator that this is from Grok
                    return f"{grok_response}\n\n*Powered by Grok AI*"
                else:
                    print(f"Grok API returned status code: {response.status_code}")
                    print(f"Response: {response.text}")
                    
        except Exception as e:
            print(f"Grok API error: {e}")
            print(f"Falling back to hardcoded responses")
    else:
        print(f"No GROK_API_KEY found, using fallback responses")
    
    # Fallback to contextual responses if Grok fails
    user_content = user_content.lower().strip()
    print(f"Processing fallback for: {user_content}")
    
    # Name/identity questions - FIRST PRIORITY
    if any(phrase in user_content for phrase in ["what's your name", "whats your name", "your name", "who are you", "what are you", "name"]):
        return """I'm Alex, your dedicated Unitasa Marketing Automation Specialist! 👋

I'm here because you're likely dealing with the same frustrations I help solve every day:
• Leads slipping through the cracks
• Manual follow-up eating up your time  
• Not knowing which marketing efforts actually work
• Wanting to scale but being stuck doing everything manually

**Here's what I do:** I help businesses like yours implement AI-powered marketing automation that works with your existing CRM - whether that's Salesforce, HubSpot, Pipedrive, or others.

**Quick question:** What brought you to Unitasa today? Are you currently using a CRM system, or are you looking to get your marketing more organized?

Once I understand your situation, I can show you exactly how we've helped similar businesses increase their qualified leads by 40% while saving 20+ hours per week."""
    
    # Features and capabilities questions
    if any(phrase in user_content for phrase in ["features", "capabilities", "what can", "what does", "how does", "functionality"]):
        return """Great question! Let me show you what makes Unitasa different from every other marketing tool you've tried. 🚀

**Core Capabilities That Drive Results:**
🎯 **Smart Lead Scoring** - AI analyzes behavior patterns to identify your hottest prospects
🎯 **24/7 Lead Nurturing** - Automated sequences that feel personal and convert better
🎯 **CRM Synchronization** - Real-time updates across all your systems
🎯 **Voice-to-Text Capture** - Turn phone calls into CRM entries automatically
🎯 **Custom Workflow Triggers** - Automate actions based on any customer behavior

**But here's what really matters - the BUSINESS IMPACT:**
• 40% increase in qualified leads (typical first 30 days)
• 20+ hours saved per week on manual tasks
• 60% faster lead response time
• 300-500% ROI in first year

**Now, let me ask you this:** Which of these capabilities would have the biggest impact on YOUR business right now?
• Getting more qualified leads?
• Saving time on manual follow-up?
• Better tracking and analytics?
• Scaling without hiring more staff?

Once I know your priority, I can show you exactly how that feature works in your specific situation. What's most important to you?"""
    
    # Demo or show me questions
    if any(phrase in user_content for phrase in ["demo", "show me", "see it", "example", "how it works"]):
        return """Perfect! I love showing how Unitasa works in real business scenarios. 🎬

**Here's what I can show you:**
🎯 **Live CRM Integration** - Watch us connect to your actual CRM in under 5 minutes
🎯 **Lead Scoring in Action** - See how AI identifies your best prospects instantly
🎯 **Automation Workflows** - Real examples of campaigns that convert
🎯 **ROI Calculator** - Input your numbers and see projected results

**But first, let me ask a few quick questions so the demo is relevant to YOU:**
1. **Which CRM are you using?** (Salesforce, HubSpot, Pipedrive, etc.)
2. **How many leads do you generate monthly?**
3. **What's your biggest marketing challenge right now?**

**Two options for your demo:**
• **Quick Assessment First** (3 minutes) - Then I'll show you features specific to your score
• **Direct Demo** - I'll show you everything and you can ask questions live

**The assessment helps me customize the demo to your exact needs.** Which would you prefer - assessment first, or jump straight into the demo?"""
    
    # Greeting responses - more agent-like
    if any(word in user_content for word in ["hi", "hello", "hey", "good morning", "good afternoon"]):
        return "Hey there! 👋 I'm Alex, your Unitasa Marketing Automation Specialist. I help businesses like yours automate their marketing and boost lead generation through smart CRM integrations.\n\nBefore we dive in - are you currently using a CRM system like Salesforce, HubSpot, or Pipedrive? I'd love to understand your current setup so I can show you exactly how Unitasa can transform your marketing operations!"
    
    # Personal questions - redirect to business focus
    if any(phrase in user_content for phrase in ["how are you", "what's up", "how's it going"]):
        return "I'm doing fantastic, thanks for asking! I'm energized because I get to help businesses transform their marketing operations every day. 🚀\n\nSpeaking of transformations - I'm curious about your business. Are you currently struggling with:\n• Manual lead follow-up taking too much time?\n• Leads falling through the cracks in your CRM?\n• Difficulty tracking which marketing efforts actually convert?\n\nI specialize in solving exactly these problems with AI automation. What's your biggest marketing challenge right now?"
    
    # What is Unitasa / Platform overview - more agent-focused
    if any(phrase in user_content for phrase in ["what is unitasa", "what's unitasa", "tell me about unitasa", "unitasa platform", "what do you do"]):
        return """Great question! Unitasa is the AI Marketing Automation Platform that finally makes CRM integration simple and profitable. 🚀

**Here's what makes us different:**
• **2-Click CRM Integration** - Works with Salesforce, HubSpot, Pipedrive, Zoho, Monday.com
• **24/7 AI Lead Nurturing** - Never lose another lead to slow follow-up
• **Smart Lead Scoring** - Focus your time on prospects most likely to buy
• **Automated Campaigns** - Personalized marketing that runs itself

**Built by a founder who solved his own problem** - going from zero to automated lead generation.

**Now, let me ask you this:** What's driving you to look for a marketing automation solution? Are you:
• Losing leads due to slow manual follow-up?
• Struggling to track which marketing efforts actually work?
• Spending too much time on repetitive tasks?
• Ready to scale but don't want to hire more staff?

Understanding your specific pain point helps me show you exactly how Unitasa solves YOUR problem. What's your biggest challenge right now?"""
    
    # CRM Integration questions - more consultative
    if any(word in user_content for word in ["crm", "integration", "connect", "sync", "salesforce", "hubspot", "pipedrive", "zoho", "monday"]):
        return """Perfect! CRM integration is exactly where Unitasa shines - and where most businesses are losing money. 💰

**Here's the reality:** Most businesses are only using 20% of their CRM's potential. They're manually entering leads, forgetting follow-ups, and missing opportunities.

**Unitasa changes that completely:**
✅ **2-Click Integration** - Salesforce, HubSpot, Pipedrive, Zoho, Monday.com
✅ **Real-Time Sync** - Every lead, contact, and interaction automatically updated
✅ **Smart Lead Scoring** - AI identifies your hottest prospects instantly
✅ **Automated Nurturing** - Personalized follow-up sequences that never stop
✅ **Custom Workflows** - Trigger actions based on any CRM event

**Here's what I need to know to help you:**
1. **Which CRM are you using?** (or considering?)
2. **What's your biggest frustration** with your current setup?
3. **How many leads** are you generating per month?

Once I understand your specific situation, I can show you exactly how much time and money Unitasa will save you. Most clients see 40% more qualified leads within 30 days.

**Quick question:** Are you ready to see how this works with YOUR CRM, or do you want to take our 3-minute AI Readiness Assessment first?"""
    
    # Assessment questions - more urgent and benefit-focused
    if any(phrase in user_content for phrase in ["assessment", "test", "quiz", "evaluate", "ready", "score"]):
        return """Excellent choice! The AI Readiness Assessment is the fastest way to see exactly how much money you're leaving on the table. 📊💰

**Here's what happens in just 3 minutes:**
🎯 **Instant Analysis** - We evaluate your current CRM setup and identify gaps
🎯 **Revenue Impact Calculator** - See exactly how much more you could be making
🎯 **Personalized Roadmap** - Get specific steps to implement AI automation
🎯 **Integration Complexity Score** - Know exactly what's involved for YOUR business

**Real Results from Recent Assessments:**
• Marketing agency discovered they were losing $15K/month in follow-up gaps
• SaaS company found 60% of leads weren't being properly scored
• Consulting firm identified automation opportunities worth 25 hours/week

**Your Score Determines Your Next Steps:**
• **71-100%** → Priority demo with our founder + Co-Creator Program access
• **41-70%** → Co-Creator Program eligibility ($250 lifetime vs $97/month)
• **0-40%** → Free strategy guide + gradual implementation plan

**The best part?** Even if you don't choose Unitasa, you'll walk away with a clear action plan to improve your marketing ROI.

**Ready to discover what you're missing?** The assessment takes 3 minutes and could save you thousands. Should we start now?"""
    
    # Co-creator program questions
    if any(phrase in user_content for phrase in ["co-creator", "program", "founding", "lifetime", "$250", "early adopter"]):
        return """🌟 **Co-Creator Program - Shape the Future of AI Marketing!**

**Exclusive Benefits (Only 25 Seats Available):**
🎯 **Lifetime Platform Access** - Never pay monthly fees again
🎯 **Direct Founder Access** - Weekly calls and direct communication
🎯 **Roadmap Influence** - Vote on features and suggest improvements
🎯 **Custom Integration Support** - We'll personally help set up your CRM
🎯 **Early Feature Access** - Get new capabilities before anyone else
🎯 **Supporter Recognition** - Featured as a founding supporter (with permission)

**Investment:** $250 one-time (vs $97/month regular pricing)
**ROI Timeline:** Pays for itself in 3 months
**Commitment:** Help us improve through feedback and testimonials

**Who Qualifies:**
✅ Businesses ready to implement AI marketing automation
✅ Current CRM users looking to enhance their setup
✅ Teams willing to provide feedback and suggestions
✅ Assessment score of 41-70% (warm leads)

This isn't just software access - you're becoming a partner in building the future of AI marketing automation. Your input directly shapes our product development!

Want to check if you qualify? Take our assessment first!"""
    
    # Signup/registration questions
    if any(phrase in user_content for phrase in ["signup", "sign up", "register", "join", "get started", "how to start", "onboard"]):
        return """Great question! I'm excited to help you get started with Unitasa. Here's exactly how to sign up:

**🚀 FASTEST PATH - Co-Creator Program (Limited Time):**
• **$250 one-time payment** → Lifetime access
• Only 25 seats left
• Includes personal onboarding call with me
• Custom CRM integration setup included
• Direct access to our founder

**� REgGULAR SIGNUP PROCESS:**
1. **Take our AI Readiness Assessment** (3 minutes) → Get your personalized plan
2. **Choose your plan** based on your assessment score
3. **Connect your CRM** (Salesforce, HubSpot, Pipedrive, etc.)
4. **Onboarding call** with me to set up your automation

**🎯 RECOMMENDED NEXT STEP:**
Let's start with the assessment so I can recommend the best signup path for YOUR business. It takes 3 minutes and shows you exactly what you'll get.

**Quick question:** Are you currently using a CRM system? This helps me know which integration we'll set up for you.

Ready to take the assessment and see your personalized signup plan?"""
    
    # Pricing questions
    if any(word in user_content for word in ["price", "cost", "pricing", "expensive", "cheap", "money", "payment"]):
        return """💰 **Unitasa Pricing - Flexible Options for Every Business**

**🌟 Co-Creator Program (Limited Time)**
• **$250 one-time** → Lifetime access + founder support
• Only 25 seats available
• Includes custom CRM integration setup
• Direct influence on product roadmap
• Best value: Saves $1,164+ annually vs regular pricing

**📈 Regular Pricing (After Co-Creator Program)**
• **Starter:** $47/month - Basic CRM integration + automation
• **Professional:** $97/month - Advanced AI features + multi-CRM
• **Enterprise:** $197/month - Custom integrations + dedicated support

**💡 ROI Calculator:**
• Average customer saves 20+ hours/week on manual tasks
• 40% increase in qualified leads
• 60% improvement in lead response time
• Typical ROI: 300-500% in first year

Ready to transform your marketing ROI? The Co-Creator Program won't last long!"""
    
    
    # Default response - more agent-like and qualifying
    return f"""I can definitely help you with that! Let me make sure I give you the most relevant information for your specific business situation.

**Here's what I'm thinking:** Based on your question, you're probably evaluating marketing automation solutions, which means you're likely dealing with:
• Too much manual work in your current process
• Leads not getting proper follow-up
• Difficulty tracking what's actually working
• Need to scale without hiring more people

**Quick qualifying question:** What's your current marketing setup? Are you:
• Using a CRM but struggling with manual processes?
• Generating leads but losing them in follow-up?
• Spending too much time on repetitive marketing tasks?
• Looking to scale your lead generation without hiring more staff?

Once I understand your specific challenges, I can show you exactly how Unitasa's AI Marketing Automation Platform addresses your pain points. We've helped businesses increase qualified leads by 40% while saving 20+ hours per week.

**Want to see how ready your business is for AI automation?** Our free 10-question assessment takes 3 minutes and gives you a personalized roadmap. Should we start there?

*[Fallback Response - Grok AI not available]*"""

router = APIRouter()


class ChatSessionCreateRequest(BaseModel):
    """Request to create a new chat session"""
    lead_id: Optional[int] = None
    user_id: Optional[int] = None
    user_agent: Optional[str] = None
    referrer: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


@router.get("/health")
async def chat_health_check() -> Dict[str, Any]:
    """
    Health check endpoint for chat service
    """
    return {
        "status": "healthy",
        "service": "chat_service_standalone",
        "message": "Chat service is operational",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.post("/initialize")
async def initialize_chat_session(
    request: Optional[ChatSessionCreateRequest] = None,
    http_request: Request = None
) -> Dict[str, Any]:
    """
    Create a new chat session (standalone version)
    """
    try:
        # Generate a simple session ID
        session_id = str(uuid.uuid4())
        
        # Return a basic session response that matches frontend expectations
        response_data = {
            "session_id": session_id,
            "id": session_id,  # Frontend uses session.id for WebSocket URL
            "active": True,  # Frontend expects 'active' boolean instead of 'status'
            "messages": [
                {
                    "id": str(uuid.uuid4()),
                    "content": "Hey! I'm Alex, your Unitasa Marketing Automation Specialist. 🚀\n\nI help businesses automate their marketing and boost lead generation through smart CRM integrations. Before we dive into features, I'd love to understand your current situation:\n\n**Quick question:** What's your biggest marketing challenge right now?\n• Manual lead follow-up taking too much time?\n• Leads falling through the cracks?\n• Difficulty tracking marketing ROI?\n• Need to scale without hiring more staff?\n\nOnce I understand your specific needs, I can show you exactly how Unitasa solves your problems!",
                    "sender": "agent",
                    "timestamp": datetime.utcnow().isoformat(),
                    "type": "text"
                }
            ],
            "context": request.context if request and request.context else {},
            "voiceEnabled": True
        }

        return response_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create chat session: {str(e)}")


@router.post("/sessions/{session_id}/messages")
async def send_chat_message(
    session_id: str,
    message_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Send a message to the chat (standalone version)
    """
    try:
        user_content = message_data.get("content", "").lower()
        
        # Generate contextual responses based on user input
        response_content = await generate_contextual_response(user_content)
        
        response_message = {
            "id": str(uuid.uuid4()),
            "content": response_content,
            "sender": "agent",
            "timestamp": datetime.utcnow().isoformat(),
            "type": "text"
        }
        return response_message
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process message: {str(e)}")


@router.post("/{session_id}/message")
async def send_chat_message_fallback(
    session_id: str,
    message_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Fallback message endpoint (standalone version)
    """
    try:
        user_content = message_data.get("content", "")
        
        # Generate contextual responses based on user input using the knowledge base
        response_content = await generate_contextual_response(user_content)
        
        response_message = {
            "id": str(uuid.uuid4()),
            "content": response_content,
            "sender": "agent",
            "timestamp": datetime.utcnow().isoformat(),
            "type": "text"
        }
        return response_message
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process message: {str(e)}")


@router.websocket("/ws/{session_id}")
async def websocket_chat_endpoint(
    websocket: WebSocket, 
    session_id: str,
    token: Optional[str] = Query(None)
):
    """
    Basic WebSocket endpoint for chat (standalone version)
    """
    # Authenticate user if token provided
    if token:
        try:
            JWTHandler.verify_token(token)
        except Exception:
            # Invalid token - close connection with policy violation
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

    await websocket.accept()
    
    try:
        # Send connection confirmation
        await websocket.send_json({
            "type": "connected",
            "session_id": session_id,
            "message": "WebSocket connection established"
        })
        
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            print(f"[WEBSOCKET] Received data: {data}")
            
            if data.get("type") == "message":
                user_content = data.get("content", "").lower()
                
                # Generate agent-like contextual responses
                response_content = await generate_contextual_response(user_content)
                
                # Send back a proper chat message
                response_message = {
                    "id": str(uuid.uuid4()),
                    "content": response_content,
                    "sender": "agent",
                    "timestamp": datetime.utcnow().isoformat(),
                    "type": "text"
                }
                print(f"[WEBSOCKET] Sending response: {response_message}")
                await websocket.send_json(response_message)
                
            elif data.get("type") == "ping":
                # Respond to ping
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat()
                })
                
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": f"WebSocket error: {str(e)}"
        })


@router.get("/test")
async def test_endpoint() -> Dict[str, Any]:
    """
    Test endpoint to verify chat router is working
    """
    return {
        "success": True,
        "message": "Standalone chat router is working correctly",
        "timestamp": datetime.utcnow().isoformat()
    }