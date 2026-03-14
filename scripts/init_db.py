"""
scripts/init_db.py — Creates all database tables and initial setup.

Run this ONCE before starting the backend for the first time:
  cd backend
  python ../scripts/init_db.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "backend", ".env"))

from database import engine, Base
import models  # Import models so SQLAlchemy knows about them

def init():
    print("Creating PostgreSQL tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created successfully!")
        print("   Tables: users, cases")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure PostgreSQL is running and DATABASE_URL is set in backend/.env")
        print("If you don't have PostgreSQL installed, use Docker:")
        print("  docker compose up postgres -d")

if __name__ == "__main__":
    init()
