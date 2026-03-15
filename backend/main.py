"""
main.py — The entry point of the AstraShield backend.

This file creates the FastAPI app and registers all the API routes.
Think of it as the "front door" of your backend server.

To run: uvicorn main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Import our route handlers (defined in the api/ folder)
from api.upload import router as upload_router
from api.analyze import router as analyze_router
from api.report import router as report_router
from api.auth import router as auth_router

# ── Create the FastAPI application ────────────────────────────────────────────
# FastAPI automatically creates interactive API docs at /docs
app = FastAPI(
    title="AstraShield API",
    description="AI-Powered Deepfake & Identity Fraud Detection",
    version="1.0.0",
    docs_url="/docs",      # Visit http://localhost:8000/docs to see all endpoints
    redoc_url="/redoc"
)
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

class CORSFixMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"
        return response

app.add_middleware(CORSFixMiddleware)

# ── CORS Middleware ────────────────────────────────────────────────────────────
# CORS = Cross-Origin Resource Sharing
# This allows your Next.js frontend (port 3000) to talk to this backend (port 8000)
# Without this, the browser would block the requests for security reasons
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
) 

# ── Register Routes ────────────────────────────────────────────────────────────
# Each router handles a specific group of endpoints
app.include_router(auth_router,     prefix="/api/auth",    tags=["Authentication"])
app.include_router(upload_router,   prefix="/api/upload",  tags=["File Upload"])
app.include_router(analyze_router,  prefix="/api/analyze", tags=["Analysis"])
app.include_router(report_router,   prefix="/api/report",  tags=["Reports"])


# ── Root endpoint ─────────────────────────────────────────────────────────────
@app.get("/")
async def root():
    """Health check — visit http://localhost:8000 to confirm the server is running."""
    return {
        "status": "online",
        "message": "AstraShield API is running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Used by monitoring tools to check if the server is healthy."""
    return {"status": "healthy"}
