"""Core application routes."""

from fastapi import APIRouter

router = APIRouter(tags=["core"])


@router.get("/")
async def root():
    return {
        "message": "Welcome to AWS Cost Optimizer API",
        "version": "1.0.0",
        "endpoints": {
            "scan": "/scan - Scan EC2 instances and get cost optimization report",
            "health": "/health - Health check",
            "docs": "/docs - Interactive API documentation",
        },
    }


@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "aws-cost-optimizer"}
