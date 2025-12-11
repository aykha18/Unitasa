#!/usr/bin/env python3
"""
Clean startup script for Unitasa backend
Suppresses asyncpg warnings and starts the server cleanly
"""

import os
import warnings
import asyncio
import uvicorn
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Suppress asyncpg connection termination warnings
warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*coroutine.*was never awaited.*")
warnings.filterwarnings("ignore", message=".*Event loop is closed.*")
warnings.filterwarnings("ignore", message=".*Exception terminating connection.*")

# Set database URL (override if needed)
# DATABASE_URL should be set in environment variables only

# Verify Razorpay keys are loaded
razorpay_key_id = os.getenv("RAZORPAY_KEY_ID", "")
razorpay_key_secret = os.getenv("RAZORPAY_KEY_SECRET", "")
print(f"Razorpay Key ID: {razorpay_key_id}")
print(f"Razorpay Key Secret: {'*' * len(razorpay_key_secret) if razorpay_key_secret else 'NOT SET'}")

if __name__ == "__main__":
    print("Starting Unitasa backend with clean configuration...")
    
    # Verify DATABASE_URL is loaded
    database_url = os.getenv("DATABASE_URL", "")
    print(f"Database URL: {database_url[:50]}..." if database_url else "DATABASE_URL not set")
    
    # Ensure DATABASE_URL is set (fallback for development)
    if not database_url:
        os.environ["DATABASE_URL"] = "postgresql+asyncpg://postgres:aykha123@localhost:5432/unitas"
        print("Set fallback DATABASE_URL for development")
    
    # Import the app after setting environment variables
    from app.main import app
    
    # Start the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info",
        access_log=False  # Reduce log noise
    )