"""
api/analyze.py — Analysis status and results endpoints.

After uploading, the frontend repeatedly asks "is it done yet?"
This file handles those status check requests.
"""

from fastapi import APIRouter, HTTPException
from database import jobs_collection, analysis_collection

router = APIRouter()


@router.get("/status/{job_id}")
async def get_job_status(job_id: str):
    """
    Check the status of an analysis job.
    
    The frontend calls this every 2 seconds until status = "completed" or "failed".
    
    Returns:
        status: "queued" | "processing" | "completed" | "failed"
        progress: 0-100 (percentage)
        steps: which steps are done
    """
    job = await jobs_collection.find_one({"job_id": job_id}, {"_id": 0})
    if not job:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found")

    return job


@router.get("/result/{job_id}")
async def get_analysis_result(job_id: str):
    """
    Get the full analysis result once a job is completed.
    
    Returns the complete fraud analysis including:
    - fraud_risk_score (0-100)
    - risk_category (LOW/MEDIUM/HIGH/CRITICAL)
    - per-module breakdown
    - forensic details
    """
    # Check the job exists and is done
    job = await jobs_collection.find_one({"job_id": job_id}, {"_id": 0})
    if not job:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found")

    if job["status"] != "completed":
        raise HTTPException(
            status_code=202,  # 202 = "Accepted but not ready yet"
            detail=f"Analysis is still {job['status']}. Please wait."
        )

    # Get the full analysis from MongoDB
    result = await analysis_collection.find_one({"job_id": job_id}, {"_id": 0})
    if not result:
        raise HTTPException(status_code=404, detail="Analysis result not found")

    return result
