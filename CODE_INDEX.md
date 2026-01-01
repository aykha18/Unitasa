# Codebase Index

This document provides a high-level overview of the repository structure, file responsibilities, and key functions/classes.

## Backend (`app/`)

The backend is built with **FastAPI** and uses **SQLAlchemy** for ORM. It features a sophisticated AI agent system with RAG (Retrieval-Augmented Generation) capabilities.

### Entry Point
- [main.py](app/main.py): Application entry point. Configures FastAPI, middleware (CORS, GZip), and includes API routers.

### AI Agents (`app/agents/`)
Implements the autonomous agents powering the platform.
- [base.py](app/agents/base.py): `CostOptimizedAgent` base class. Handles LLM routing (OpenRouter/Groq/OpenAI) and fallback logic.
- [agentic_rag_agent.py](app/agents/agentic_rag_agent.py): `AgenticRAGAgent`. Advanced agent with tool use, reasoning (ReAct), and multi-source knowledge retrieval.
- [content_generation_agent.py](app/agents/content_generation_agent.py): `ContentGenerationAgent`. Generates marketing content (social posts, blogs, emails).
- [conversational_agent.py](app/agents/conversational_agent.py): `ConversationalAgent`. Handles chat support, lead qualification, and CRM guidance.

### API Endpoints (`app/api/v1/`)
RESTful API routes versioned under `v1`.
- [api.py](app/api/v1/api.py): Central router aggregating all other sub-routers.
- [auth.py](app/api/v1/auth.py): Authentication endpoints (`login`, `refresh_token`, `password_reset`).
- [chat.py](app/api/v1/chat.py): Chat operations (`create_session`, `send_message`) and WebSocket handling.
- [landing.py](app/api/v1/landing.py): Landing page specific endpoints (likely lead capture).
- [analytics.py](app/api/v1/analytics.py): Analytics data endpoints.

### Core Services (`app/core/`)
Shared utilities and business logic services.
- [config.py](app/core/config.py): `Settings` class managing env vars for DB, Security, and LLM providers.
- [database.py](app/core/database.py): Async database connection (`get_db`) and initialization (`init_database`).
- [analytics_service.py](app/core/analytics_service.py): `AnalyticsService`. Tracks lead capture and assessment events.
- [chat_service.py](app/core/chat_service.py): `ChatService`. Manages chat sessions, persistence, and AI response orchestration.
- [lead_scoring.py](app/core/lead_scoring.py): Logic for scoring leads based on interactions and data.
- [assessment_engine.py](app/core/assessment_engine.py): Engines for processing business readiness assessments.

### Data Models (`app/models/`)
SQLAlchemy ORM models defining the database schema.
- [base.py](app/models/base.py): `BaseModel` with `TimestampMixin` (created_at, updated_at).
- [user.py](app/models/user.py): `User` model (auth, profile, subscription status).
- [lead.py](app/models/lead.py): `Lead` model (contact info, qualification score, CRM preferences).
- [chat_session.py](app/models/chat_session.py): Stores chat history and metadata.
- [event.py](app/models/event.py): Generic event tracking model.

### RAG System (`app/rag/`)
Retrieval-Augmented Generation pipeline.
- [ingestion.py](app/rag/ingestion.py): `DocumentIngestionPipeline`. Processes files (PDF, MD, TXT) for the knowledge base.
- [lcel_chains.py](app/rag/lcel_chains.py): `ConfidenceRAGChain`. LangChain Expression Language chains with confidence scoring and citations.
- [vectorstore_manager.py](app/rag/vectorstore_manager.py): `VectorStoreManager`. Interface for ChromaDB operations.

---

## Frontend (`frontend/src/`)

The frontend is a **React** application using **TypeScript** and **Tailwind CSS**.

### Entry Points
- [App.tsx](frontend/src/App.tsx): Main component handling routing, global modals, and initialization.
- [index.tsx](frontend/src/index.tsx): React DOM entry point.
- [services/api.ts](frontend/src/services/api.ts): Axios instance configuration and interceptors.

### Components (`frontend/src/components/`)
Reusable UI building blocks.

#### Analytics
- [AnalyticsTracker.tsx](frontend/src/components/analytics/AnalyticsTracker.tsx): Displays real-time metrics (simulated) like views and conversion rates.

#### Assessment
- [AssessmentFlow.tsx](frontend/src/components/assessment/AssessmentFlow.tsx): Orchestrates the multi-step business assessment questionnaire.
- [LeadCaptureForm.tsx](frontend/src/components/assessment/LeadCaptureForm.tsx): Form to collect initial user details.

#### Booking
- [ConsultationBooking.tsx](frontend/src/components/booking/ConsultationBooking.tsx): Interface for scheduling consultation sessions.

#### Chat
- [ChatWidget.tsx](frontend/src/components/chat/ChatWidget.tsx): Floating chat interface with WebSocket integration.

#### CRM
- [CRMSetupWizard.tsx](frontend/src/components/crm/CRMSetupWizard.tsx): Wizard for connecting and configuring external CRMs.

### Pages (`frontend/src/pages/`)
Top-level page components.
- [LandingPage.tsx](frontend/src/pages/LandingPage.tsx): Main landing page aggregating Hero, Benefits, Assessment, and other sections.
- [Dashboard/UnifiedDashboard.tsx](frontend/src/pages/Dashboard/UnifiedDashboard.tsx): Main dashboard view for authenticated users.
