"""
Database configuration for Unitasa
Supports both local development and Railway PostgreSQL
"""

import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

# Create declarative base
Base = declarative_base()

# Global variables for lazy initialization
engine = None
AsyncSessionLocal = None

# Synchronous session variables for legacy compatibility
sync_engine = None
SessionLocal = None


def get_database_url():
    """Get and validate database URL"""
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is required. For local development, set DATABASE_URL to a PostgreSQL connection string.")
    
    # Railway provides DATABASE_URL, but we need to ensure it's async
    if DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    return DATABASE_URL


def init_database():
    """Initialize database engine and session factory (lazy initialization)"""
    global engine, AsyncSessionLocal
    
    if engine is not None:
        return engine, AsyncSessionLocal
    
    try:
        DATABASE_URL = get_database_url()
        
        # Create async engine
        if DATABASE_URL.startswith("sqlite"):
            # SQLite doesn't support connection pooling
            engine = create_async_engine(
                DATABASE_URL,
                echo=False,  # Set to True for SQL logging in development
            )
        else:
            # PostgreSQL with connection pooling - Railway optimized settings
            engine = create_async_engine(
                DATABASE_URL,
                echo=False,  # Set to True for SQL logging in development
                pool_size=2,  # Small pool for Railway
                max_overflow=1,  # Limited overflow
                pool_pre_ping=True,  # Enable pre-ping for connection health
                pool_recycle=600,  # Longer recycle time for Railway
                pool_timeout=20,  # Longer timeout for Railway
                connect_args={
                    "server_settings": {
                        "application_name": "unitasa_app",
                    },
                    "command_timeout": 10  # Longer command timeout
                }
            )

        # Create async session factory
        AsyncSessionLocal = sessionmaker(
            engine, 
            class_=AsyncSession, 
            expire_on_commit=False
        )
        
        return engine, AsyncSessionLocal
        
    except Exception as e:
        print(f"Database initialization failed: {e}")
        raise


async def get_db():
    """Dependency to get database session"""
    # Initialize database if not already done
    engine, AsyncSessionLocal = init_database()
    
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database tables"""
    # Initialize database if not already done
    engine, _ = init_database()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def init_sync_database():
    """Initialize synchronous database engine and session factory"""
    global sync_engine, SessionLocal

    if sync_engine is not None:
        return sync_engine, SessionLocal

    try:
        DATABASE_URL = get_database_url()

        # Convert async URL back to sync for synchronous operations
        if DATABASE_URL.startswith("postgresql+asyncpg://"):
            DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://", 1)

        # Create sync engine
        if DATABASE_URL.startswith("sqlite"):
            sync_engine = create_engine(
                DATABASE_URL,
                echo=False,
                connect_args={"check_same_thread": False}
            )
        else:
            sync_engine = create_engine(
                DATABASE_URL,
                echo=False,
                pool_size=1,
                max_overflow=0,
                pool_pre_ping=False,
                pool_recycle=300,
                pool_timeout=10
            )

        # Create sync session factory
        SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=sync_engine
        )

        return sync_engine, SessionLocal

    except Exception as e:
        print(f"Synchronous database initialization failed: {e}")
        raise


def get_sync_db():
    """Dependency to get synchronous database session"""
    # Initialize database if not already done
    engine, SessionLocal = init_sync_database()

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()