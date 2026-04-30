"""Scan routes."""

from datetime import datetime, timedelta
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse, PlainTextResponse

from api.schemas.scan import ScanRequest, ScanResponse
from api.services.scan_service import get_mock_instances, run_scan

router = APIRouter(tags=["scans"])
def _scan_query_payload(
    region: str,
    cpu_threshold: float,
    days: int,
    use_mock_data: bool,
) -> ScanRequest:
    return ScanRequest(
        region=region,
        cpu_threshold=cpu_threshold,
        days=days,
        use_mock_data=use_mock_data,
    )


@router.get("/scan", response_model=ScanResponse)
async def scan_instances(
    region: str = Query(default="us-east-1", description="AWS region to scan"),
    cpu_threshold: float = Query(default=5.0, description="CPU threshold for idle detection"),
    days: int = Query(default=7, description="Number of days for metrics analysis"),
    use_mock_data: bool = Query(default=False, description="Use mock data for testing"),
):
    """Legacy GET scan endpoint kept for compatibility."""
    try:
        return run_scan(_scan_query_payload(region, cpu_threshold, days, use_mock_data), None).response
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/scan", response_model=ScanResponse)
async def scan_with_credentials(
    payload: ScanRequest,
):
    try:
        return run_scan(payload, None).response
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/scan/text")
async def scan_instances_text(
    region: str = Query(default="us-east-1", description="AWS region to scan"),
    cpu_threshold: float = Query(default=5.0, description="CPU threshold for idle detection"),
    days: int = Query(default=7, description="Number of days for metrics analysis"),
    use_mock_data: bool = Query(default=True, description="Use mock data for testing"),
):
    try:
        artifacts = run_scan(_scan_query_payload(region, cpu_threshold, days, use_mock_data), None)
        return PlainTextResponse(artifacts.response.report_text, media_type="text/plain")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/scan/text")
async def scan_instances_text_post(
    payload: ScanRequest,
):
    try:
        artifacts = run_scan(payload, None)
        return PlainTextResponse(artifacts.response.report_text, media_type="text/plain")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/scan/summary")
async def scan_instances_summary(
    region: str = Query(default="us-east-1", description="AWS region to scan"),
    use_mock_data: bool = Query(default=True, description="Use mock data for testing"),
):
    try:
        artifacts = run_scan(_scan_query_payload(region, 5.0, 7, use_mock_data), None)
        return PlainTextResponse(artifacts.response.summary_card, media_type="text/plain")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/scan/summary")
async def scan_instances_summary_post(
    payload: ScanRequest,
):
    try:
        artifacts = run_scan(payload, None)
        return PlainTextResponse(artifacts.response.summary_card, media_type="text/plain")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/scan/json")
async def scan_instances_json(
    region: str = Query(default="us-east-1", description="AWS region to scan"),
    cpu_threshold: float = Query(default=5.0, description="CPU threshold for idle detection"),
    days: int = Query(default=7, description="Number of days for metrics analysis"),
    use_mock_data: bool = Query(default=True, description="Use mock data for testing"),
):
    try:
        artifacts = run_scan(_scan_query_payload(region, cpu_threshold, days, use_mock_data), None)
        return JSONResponse(content=artifacts.cost_analysis)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/scan/json")
async def scan_instances_json_post(
    payload: ScanRequest,
):
    try:
        artifacts = run_scan(payload, None)
        return JSONResponse(content=artifacts.cost_analysis)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
