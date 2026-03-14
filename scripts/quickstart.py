#!/usr/bin/env python3
"""
scripts/quickstart.py — One-script local development setup.

This script checks your setup and gives you exactly the commands to run.
It does NOT require Docker.

Run from the project root:
  python scripts/quickstart.py
"""

import subprocess
import sys
import os


def check(name: str, cmd: list, version_flag="--version") -> bool:
    """Check if a command is available."""
    try:
        result = subprocess.run(cmd + [version_flag], capture_output=True, text=True, timeout=5)
        version = result.stdout.strip() or result.stderr.strip()
        print(f"  ✅ {name}: {version[:60]}")
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print(f"  ❌ {name}: NOT FOUND")
        return False


def main():
    print("=" * 60)
    print("  AstraShield — Local Development Setup Check")
    print("=" * 60)
    print()

    print("Checking required tools...")
    has_python = check("Python",  [sys.executable])
    has_node   = check("Node.js", ["node"])
    has_npm    = check("npm",     ["npm"])
    has_redis  = check("Redis",   ["redis-cli"], "ping")

    print()

    if not has_node:
        print("📦 INSTALL Node.js:")
        print("   https://nodejs.org  → Download LTS version")
        print()

    if not has_redis:
        print("📦 INSTALL Redis:")
        print("   Windows: https://github.com/tporadowski/redis/releases")
        print("   Mac:     brew install redis && brew services start redis")
        print("   Linux:   sudo apt install redis-server && sudo service redis start")
        print()

    print("=" * 60)
    print("  Quick Start — Open 3 terminal windows and run:")
    print("=" * 60)
    print()
    print("TERMINAL 1 — Backend API:")
    print("  cd backend")
    print("  pip install -r requirements.txt")
    print("  cp .env.example .env")
    print("  uvicorn main:app --reload --port 8000")
    print()
    print("TERMINAL 2 — Celery Worker (background task processor):")
    print("  cd backend")
    print("  celery -A celery_app worker --loglevel=info")
    print()
    print("TERMINAL 3 — Frontend:")
    print("  cd frontend")
    print("  npm install")
    print("  npm run dev")
    print()
    print("Then open: http://localhost:3000")
    print()
    print("NOTE: For the first run, generate demo data to see the dashboard:")
    print("  cd backend")
    print("  python ../scripts/generate_demo_data.py")
    print()
    print("=" * 60)
    print("  API Docs: http://localhost:8000/docs")
    print("=" * 60)


if __name__ == "__main__":
    main()
