"""
Unitasa - Unified Marketing Intelligence Platform
Main FastAPI application entry point
"""

import logging
import os
import sys
import warnings
import asyncio

# Force reload trigger
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Suppress asyncpg connection termination warnings on Windows
warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*coroutine.*was never awaited.*")
warnings.filterwarnings("ignore", message=".*Event loop is closed.*")
warnings.filterwarnings("ignore", message=".*Exception terminating connection.*")
from fastapi import FastAPI, Request, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager

from app.core.database import Base, init_database
from app.core.logging import setup_logging
from app.core.security_middleware import SecurityHeadersMiddleware

print("Importing API modules...")
try:
    print("Importing health module...")
    from app.api.v1 import health
    print("Health module imported successfully")
    
    print("Importing landing module...")
    try:
        from app.api.v1 import landing
        print("Landing module imported successfully")
        print(f"Landing router object: {landing.router}")
        print(f"Landing router routes: {[route.path for route in landing.router.routes]}")
    except Exception as e:
        print(f"ERROR importing landing module: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        raise
    
    print("Importing chat module...")
    try:
        from app.api.v1 import chat
        print("Chat module imported successfully")
    except ImportError as e:
        print(f"Chat module import failed (AI dependencies missing): {e}")
        print("Skipping chat module for minimal deployment")

    print("Importing analytics module...")
    try:
        from app.api.v1 import analytics
        print("Analytics module imported successfully")
    except ImportError as e:
        print(f"Analytics module import failed: {e}")
        print("Skipping analytics module")

    print("Importing working assessment module...")
    try:
        from app.api.v1 import assessment_working
        print("Working assessment module imported successfully")
    except ImportError as e:
        print(f"Assessment module import failed: {e}")
        print("Skipping assessment module")

    print("Importing crm_marketplace module...")
    try:
        from app.api.v1 import crm_marketplace
        print("CRM marketplace module imported successfully")
    except ImportError as e:
        print(f"CRM marketplace module import failed: {e}")
        print("Skipping CRM marketplace module")
    
    # Wise payments temporarily disabled due to dependency issues
    # print("Importing wise_payments module...")
    # from app.api.v1 import wise_payments
    # print("Wise payments module imported successfully")
    
    print("Importing razorpay_payments module...")
    razorpay_payments = None
    try:
        from app.api.v1 import razorpay_payments
        print("Razorpay payments module imported successfully")
    except Exception as e:
        print(f"Razorpay payments module import failed: {e}")
    
    print("Importing consultation module...")
    consultation = None
    try:
        from app.api.v1 import consultation
        print("Consultation module imported successfully")
    except Exception as e:
        print(f"Consultation module import failed: {e}")
    
    print("Importing pricing module...")
    pricing = None
    try:
        from app.api.v1 import pricing
        print("Pricing module imported successfully")
    except Exception as e:
        print(f"Pricing module import failed: {e}")

    print("Importing user_registration module...")
    user_registration = None
    try:
        from app.api.v1 import user_registration
        print("User registration module imported successfully")
    except Exception as e:
        print(f"User registration module import failed: {e}")

    print("Importing auth module...")
    auth = None
    try:
        from app.api.v1 import auth
        print("Auth module imported successfully")
    except Exception as e:
        print(f"Auth module import failed: {e}")
    
    print("Importing admin module...")
    admin = None
    try:
        from app.api.v1 import admin
        print("Admin module imported successfully")
    except Exception as e:
        print(f"Admin module import failed: {e}")

    print("Importing social module...")
    try:
        from app.api.v1 import social
        print("Social module imported successfully")
        print(f"Social router object: {social.router}")
        print(f"Social router type: {type(social.router)}")
    except Exception as e:
        print(f"ERROR importing social module: {e}")
        import traceback
        print(f"Social import traceback: {traceback.format_exc()}")
        raise

    print("All API modules imported successfully")
except Exception as e:
    print(f"Error importing API modules: {e}")
    import traceback
    traceback.print_exc()

# Import all models to ensure they are registered with SQLAlchemy
from app.models import *


async def create_default_data(engine):
    """Create default user and campaign data"""
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import select
    from app.models.user import User
    from app.models.campaign import Campaign
    from app.models.pricing_plan import PricingPlan
    
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    try:
        async with async_session() as session:
            # Check if system user exists
            result = await session.execute(select(User).where(User.id == 1))
            user = result.scalar_one_or_none()
            
            if not user:
                print("Creating system user...")
                # Generate a proper hash for the system user password
                from app.core.jwt_handler import get_password_hash
                system_password = os.getenv("SYSTEM_USER_PASSWORD", "change_this_system_password_in_production")
                hashed_system_password = get_password_hash(system_password)

                user = User(
                    id=1,
                    email="system@unitasa.com",
                    hashed_password=hashed_system_password,
                    full_name="System User",
                    is_active=True,
                    role="admin"
                )
                session.add(user)
                await session.flush()
                print(f"SUCCESS Created system user with ID: {user.id}")
            else:
                print(f"SUCCESS System user already exists with ID: {user.id}")

            # Seed Default Pricing Plans
            default_plans = [
                {
                    "name": "free",
                    "display_name": "Free Plan",
                    "price_usd": 0.0,
                    "price_inr": 0.0,
                    "description": "Basic access for individuals",
                    "features": ["Basic Analytics", "1 Social Account", "Community Support"]
                },
                {
                    "name": "pro",
                    "display_name": "Pro Plan",
                    "price_usd": 49.0,
                    "price_inr": 3999.0,
                    "description": "For growing businesses",
                    "features": ["Advanced Analytics", "5 Social Accounts", "Priority Support"]
                },
                {
                    "name": "enterprise",
                    "display_name": "Enterprise Plan",
                    "price_usd": 199.0,
                    "price_inr": 15999.0,
                    "description": "For large organizations",
                    "features": ["Custom Analytics", "Unlimited Accounts", "Dedicated Manager"]
                },
                {
                    "name": "co_creator",
                    "display_name": "Co-Creator Program",
                    "price_usd": 497.0,
                    "price_inr": 29999.0,
                    "description": "Exclusive founding member access",
                    "features": ["Lifetime Access", "Roadmap Influence", "Direct Founder Access"]
                }
            ]

            for plan_data in default_plans:
                result = await session.execute(select(PricingPlan).where(PricingPlan.name == plan_data["name"]))
                plan = result.scalar_one_or_none()
                if not plan:
                    print(f"Creating default plan: {plan_data['name']}")
                    new_plan = PricingPlan(**plan_data)
                    session.add(new_plan)
                else:
                    print(f"Plan {plan_data['name']} already exists")
            
            await session.commit()
            
            # Check if default campaign exists
            result = await session.execute(select(Campaign).where(Campaign.id == 1))
            campaign = result.scalar_one_or_none()
            
            if not campaign:
                print("Creating default campaign...")
                campaign = Campaign(
                    id=1,
                    campaign_id="default_landing_page_campaign",
                    user_id=user.id,
                    name="Landing Page Assessments",
                    description="Default campaign for landing page assessment leads",
                    status="active",
                    campaign_type="landing_page",
                    target_audience={}
                )
                session.add(campaign)
                await session.flush()
                print(f"SUCCESS Created default campaign with ID: {campaign.id}")
            else:
                print(f"SUCCESS Default campaign already exists with ID: {campaign.id}")
            
            await session.commit()
            print("SUCCESS Default data creation completed successfully")
            
    except Exception as e:
        print(f"ERROR creating default data: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("Setting up logging...")
    setup_logging()
    print("Starting Unitasa application...")
    engine = None
    background_tasks = []

    try:
        print("Attempting database connection...")
        engine, _ = init_database()
        print(f"Database URL: {engine.url}")

        # Test connection with proper cleanup
        try:
            async with engine.begin() as conn:
                print("Creating database tables...")
                await conn.run_sync(Base.metadata.create_all)
                print(f"Created tables: {list(Base.metadata.tables.keys())}")

            # Create default data
            print("Creating default user and campaign...")
            await create_default_data(engine)
            print("Database initialized successfully")

            # Start background services
            print("Starting background services...")

            # Import background services
            try:
                from app.core.token_refresh_service import scheduled_token_refresh
                from app.core.client_notification_service import scheduled_client_notifications
                from app.core.scheduler import start_scheduler

                # Create background tasks
                token_refresh_task = asyncio.create_task(scheduled_token_refresh())
                client_notification_task = asyncio.create_task(scheduled_client_notifications())
                scheduler_task = asyncio.create_task(start_scheduler())

                background_tasks.extend([token_refresh_task, client_notification_task, scheduler_task])

                print("✅ Background services started:")
                print("   • Token refresh service (runs every 4 hours)")
                print("   • Client notification service (runs daily)")
                print("   • Social media scheduler (runs every 60 seconds)")

            except ImportError as e:
                print(f"⚠️  Background services not available: {e}")
                print("   This is normal for minimal deployments")

        except Exception as conn_error:
            print(f"Database connection error: {conn_error}")
            # Don't fail startup, just continue without database

    except Exception as e:
        print(f"Database initialization failed: {e}")
        print("Application will continue without database initialization")

    print("Application startup complete")
    yield

    # Shutdown - cancel background tasks
    print("Shutting down background services...")
    for task in background_tasks:
        if not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
    print("Background services shut down")

    # Shutdown
    print("Shutting down application...")
    if engine:
        try:
            # Suppress asyncpg warnings during shutdown
            import warnings
            
            # Filter out asyncpg connection termination warnings
            warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*coroutine.*was never awaited.*")
            warnings.filterwarnings("ignore", message=".*Event loop is closed.*")
            
            # Give connections time to close gracefully
            await asyncio.sleep(0.1)
            await engine.dispose()
            print("Database connection disposed successfully")
        except Exception as e:
            print(f"Error disposing database connection: {e}")
            # Suppress the error to avoid startup issues


# Create FastAPI application
print("Creating FastAPI application...")
app = FastAPI(
    title="Unitasa API",
    description="Unified Marketing Intelligence Platform - Everything you need IN one platform",
    version="1.0.0",
    lifespan=lifespan
)
print("FastAPI application created")

# Add security middleware (commented out for debugging)
# app.add_middleware(SecurityHeadersMiddleware)

# Add CORS middleware
# Configure CORS for Railway deployment
def get_allowed_origins():
    """Get allowed origins based on environment"""
    # Base allowed origins
    origins = [
        "http://localhost:3000",  # Local development
        "http://localhost:3001",  # Alternative local port
        "https://www.unitasa.in",  # Production website
        "https://unitasa.in",      # Production website (without www)
        "https://unitas.up.railway.app",  # Railway frontend
        "https://railway.com",     # Railway domain for CORS
        "https://*.railway.app",   # Railway wildcard for subdomains
    ]

    # Add environment-specific origins
    frontend_url = os.getenv("FRONTEND_URL")
    if frontend_url:
        origins.append(frontend_url)

    # Check for Railway deployment
    railway_env = os.getenv("RAILWAY_ENVIRONMENT")
    railway_project_id = os.getenv("RAILWAY_PROJECT_ID")

    if railway_env or railway_project_id:
        # In Railway environment, also allow Railway-specific origins
        origins.extend([
            "https://railway.com",
            "https://*.railway.app",
            "https://railway.app",
        ])

    # In development or if no specific environment, allow all
    environment = os.getenv("ENVIRONMENT", "development")
    if environment == "development" and not railway_env and not railway_project_id:
        return ["*"]

    return origins

allowed_origins = get_allowed_origins()
print(f"CORS allowed origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include API routers
print("Including API routers...")
try:
    # Include health router FIRST to ensure it's available immediately
    print("Including health router...")
    app.include_router(health.router, prefix="/api/v1", tags=["health"])
    print("Health router included successfully")

    print("Including landing router directly...")
    from app.api.v1 import landing
    app.include_router(landing.router, prefix="/api/v1/landing", tags=["landing"])
    print("Landing router included successfully")
    
    # Conditionally include routers that may depend on AI packages
    if 'chat' in globals():
        print("Including chat router...")
        try:
            app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
            print("Chat router included successfully")
        except Exception as e:
            print(f"ERROR including chat router: {e}")
            print("Skipping chat router")
    else:
        print("Chat module not available, skipping router")

    if 'analytics' in globals():
        print("Including analytics router...")
        try:
            app.include_router(analytics.router, prefix="/api/v1", tags=["analytics"])
            print("Analytics router included successfully")
        except Exception as e:
            print(f"ERROR including analytics router: {e}")
            print("Skipping analytics router")
    else:
        print("Analytics module not available, skipping router")

    if 'crm_marketplace' in globals():
        print("Including crm_marketplace router...")
        try:
            app.include_router(crm_marketplace.router, prefix="/api/v1", tags=["crm"])
            print("CRM marketplace router included successfully")
        except Exception as e:
            print(f"ERROR including CRM marketplace router: {e}")
            print("Skipping CRM marketplace router")
    else:
        print("CRM marketplace module not available, skipping router")

    if 'assessment_working' in globals():
        print("Including working assessment router...")
        try:
            app.include_router(assessment_working.router, prefix="/api/v1/landing/assessment", tags=["assessment"])
            print("Working assessment router included successfully")
        except Exception as e:
            print(f"ERROR including assessment router: {e}")
            print("Skipping assessment router")
    else:
        print("Assessment module not available, skipping router")
    
    # Wise payments temporarily disabled due to dependency issues
    # print("Including wise payments router...")
    # app.include_router(wise_payments.router, prefix="/api/v1/payments/wise", tags=["payments"])
    # print("Wise payments router included successfully")
    
    print("Including razorpay payments router...")
    if razorpay_payments:
        try:
            app.include_router(razorpay_payments.router, prefix="/api/v1/payments/razorpay", tags=["payments"])
            print("Razorpay payments router included successfully")
        except Exception as e:
            print(f"ERROR including razorpay payments router: {e}")
            import traceback
            print(f"Razorpay router traceback: {traceback.format_exc()}")
            print("Skipping razorpay payments router")
    else:
        print("Razorpay payments module not available, skipping router")
    
    print("Including consultation router...")
    if consultation:
        try:
            app.include_router(consultation.router, prefix="/api/v1/consultation", tags=["consultation"])
            print("Consultation router included successfully")
        except Exception as e:
            print(f"ERROR including consultation router: {e}")
            print("Skipping consultation router")
    else:
        print("Consultation module not available, skipping router")
    
    print("Including user registration router...")
    if user_registration:
        try:
            app.include_router(user_registration.router, prefix="/api/v1/auth", tags=["authentication"])
            print("User registration router included successfully")
        except Exception as e:
            print(f"ERROR including user registration router: {e}")
            print("Skipping user registration router")
    else:
        print("User registration module not available, skipping router")

    print("Including auth router...")
    if auth:
        try:
            app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
            print("Auth router included successfully")
        except Exception as e:
            print(f"ERROR including auth router: {e}")
            print("Skipping auth router")
    else:
        print("Auth module not available, skipping router")
    
    print("Importing ai_report module...")
    try:
        from app.api.v1 import ai_report
        print("AI report module imported successfully")

        print("Including ai_report router...")
        app.include_router(ai_report.router, prefix="/api/v1/ai-report", tags=["ai_report"])
        print("AI report router included successfully")
    except ImportError as e:
        print(f"AI report module import failed: {e}")
        print("Skipping AI report module")
    
    print("Including pricing router...")
    if pricing:
        try:
            app.include_router(pricing.router, prefix="/api/v1", tags=["pricing"])
            print("Pricing router included successfully")
        except Exception as e:
            print(f"ERROR including pricing router: {e}")
            print("Skipping pricing router")
    else:
        print("Pricing module not available, skipping router")

    print("Including admin router...")
    try:
        app.include_router(admin.router, prefix="/api/v1", tags=["admin"])
        print("Admin router included successfully")
    except Exception as e:
        print(f"ERROR including admin router: {e}")
        import traceback
        print(f"Admin router traceback: {traceback.format_exc()}")
        print("Skipping admin router")

    print("Including social router...")
    try:
        app.include_router(social.router, prefix="/api/v1/social", tags=["social"])
        print("Social router included successfully")
        print(f"Social router routes: {[route.path for route in social.router.routes]}")
    except Exception as e:
        print(f"ERROR including social router: {e}")
        import traceback
        print(f"Social router traceback: {traceback.format_exc()}")
        raise

    print("Including client onboarding router...")
    try:
        from app.api import client_onboarding
        app.include_router(client_onboarding.router, prefix="/api/v1/clients", tags=["clients"])
        print("Client onboarding router included successfully")
    except Exception as e:
        print(f"ERROR including client onboarding router: {e}")
        import traceback
        print(f"Client onboarding router traceback: {traceback.format_exc()}")
        print("Skipping client onboarding router")

    print("Including dashboard router...")
    try:
        from app.api.v1 import dashboard
        app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["dashboard"])
        print("Dashboard router included successfully")
    except Exception as e:
        print(f"ERROR including dashboard router: {e}")
        import traceback
        print(f"Dashboard router traceback: {traceback.format_exc()}")
        print("Skipping dashboard router")

    print("All API routers included successfully")
except Exception as e:
    print(f"Error including API routers: {e}")
    import traceback
    traceback.print_exc()

# Serve static files from React build (optional for development)
print("Checking for frontend build...")
if os.path.exists("frontend/build") and os.path.exists("frontend/build/static"):
    print("Frontend build found, mounting static files")
    # Only mount /static directory, not root (root is handled by catch-all route)
    app.mount("/static", StaticFiles(directory="frontend/build/static"), name="static")
    print("Static files mounted at /static")
    # Note: Root path "/" is handled by catch-all route at the end of the file
else:
    print("Frontend build not found - running in API-only mode")
    print("Use 'cd frontend && npm run build' to create frontend build")

@app.get("/api/v1/health")
async def railway_health_check():
    """Railway health check endpoint - ultra simple, never fails"""
    print("HEALTH CHECK CALLED: /api/v1/health")
    return {
        "status": "healthy",
        "service": "unitasa-api",
        "timestamp": "2025-01-01T00:00:00.000000",
        "version": "1.0.0",
        "ready": True
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for Railway"""
    from datetime import datetime
    return {
        "status": "healthy",
        "service": "unitasa-api",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "features": {
            "database": True,
            "co_creator_program": True,
            "assessment_engine": True,
            "payment_processing": True
        }
    }

@app.get("/cors-debug")
async def cors_debug(request: Request):
    """Debug CORS configuration"""
    return {
        "allowed_origins": get_allowed_origins(),
        "request_origin": request.headers.get("origin"),
        "environment": os.getenv("ENVIRONMENT", "development"),
        "railway_environment": os.getenv("RAILWAY_ENVIRONMENT"),
        "frontend_url": os.getenv("FRONTEND_URL"),
        "all_headers": dict(request.headers)
    }

@app.get("/api/v1/config/google-client-id")
async def get_google_client_id():
    """Serve Google Client ID to frontend"""
    google_client_id = os.getenv("GOOGLE_CLIENT_ID")
    if not google_client_id:
        return {"error": "Google OAuth not configured"}
    return {"googleClientId": google_client_id}

@app.get("/debug/routes")
async def debug_routes():
    """Debug available routes"""
    routes = []
    for route in app.routes:
        if hasattr(route, 'path'):
            routes.append({
                "path": route.path,
                "methods": getattr(route, 'methods', []),
                "name": getattr(route, 'name', '')
            })
    return {
        "total_routes": len(routes),
        "routes": routes,
        "chat_routes": [r for r in routes if 'chat' in r['path']]
    }

@app.middleware("http")
async def track_conversion_funnel(request, call_next):
    """Middleware to track conversion funnel analytics"""
    from datetime import datetime

    # Track page views and user journey
    path = request.url.path
    user_agent = request.headers.get("user-agent", "")
    referrer = request.headers.get("referer", "")

    # Could store this data for analytics
    # For now, just pass through
    response = await call_next(request)

    # Add tracking headers for analytics
    response.headers["X-Conversion-Stage"] = get_conversion_stage(path)

    return response

def get_conversion_stage(path: str) -> str:
    """Determine conversion stage based on URL path"""
    if path == "/":
        return "landing"
    elif "assessment" in path:
        return "assessment"
    elif "co-creator" in path:
        return "co_creator_interest"
    elif "payment" in path:
        return "payment"
    else:
        return "other"

# OAuth callback redirect routes
@app.get("/auth/{platform}/callback")
async def oauth_callback_redirect(
    platform: str,
    code: str = Query(..., description="Authorization code from OAuth provider"),
    state: str = Query(..., description="State parameter for security"),
    error: str = Query(None, description="Error from OAuth provider"),
    user_id: int = Query(1, description="User ID")
):
    """Redirect OAuth callbacks to the API endpoints"""
    from fastapi.responses import RedirectResponse

    # Redirect to the actual API endpoint
    redirect_url = f"/api/v1/social/auth/{platform}/callback?code={code}&state={state}&user_id={user_id}"
    if error:
        redirect_url += f"&error={error}"

    return RedirectResponse(url=redirect_url, status_code=302)


# Catch-all route for SPA - serves index.html for all non-API routes
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    """Serve React app for all non-API routes (SPA routing)"""
    # If path starts with /api, let it 404 naturally
    if full_path.startswith("api/"):
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="API endpoint not found")

    # Check if it's a static file request (has file extension)
    if "." in full_path.split("/")[-1]:
        # Try to serve the actual file from build directory
        file_path = f"frontend/build/{full_path}"
        if os.path.exists(file_path):
            return FileResponse(file_path)

    # For all other paths (routes), serve index.html (React will handle routing)
    index_path = "frontend/build/index.html"
    if os.path.exists(index_path):
        return FileResponse(index_path)
    else:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Frontend not built")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 3000))
    print(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
