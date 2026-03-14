"""
database.py — Sets up database connections.

We use two databases:
- PostgreSQL: For structured data (users, cases, audit logs)
- MongoDB: For flexible data (analysis results vary by media type)
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

# ── PostgreSQL Setup ───────────────────────────────────────────────────────────
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/astrashield")

# The engine is the connection to PostgreSQL
engine = create_engine(DATABASE_URL)

# SessionLocal is a factory that creates database sessions
# A "session" is like opening a conversation with the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class that all our database models will inherit from
Base = declarative_base()


def get_db():
    """
    FastAPI dependency — provides a database session to route handlers.
    
    Usage in a route:
        @app.get("/something")
        def my_route(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db  # Give the session to the route handler
    finally:
        db.close()  # Always close the session when done


# ── MongoDB Setup ──────────────────────────────────────────────────────────────
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "astrashield")

# MongoDB client (created once, reused everywhere)
mongo_client = AsyncIOMotorClient(MONGO_URL)
mongo_db = mongo_client[MONGO_DB]

# Collections (like tables in PostgreSQL)
analysis_collection = mongo_db["analyses"]   # Stores full analysis results
jobs_collection = mongo_db["jobs"]           # Tracks job status
