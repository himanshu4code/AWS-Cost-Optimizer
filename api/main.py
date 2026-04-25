"""
AWS Cost Optimizer API
FastAPI application for EC2 cost optimization analysis.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os

from ec2_scanner import EC2Scanner
from idle_detector import IdleDetector
from cost_calculator import CostCalculator
from report_generator import ReportGenerator


# Pydantic models for API responses
class SavingsSummary(BaseModel):
    total_instances: int
    total_current_monthly_cost_inr: float
    potential_monthly_savings_inr: float
    potential_annual_savings_inr: float
    savings_percentage: float


class InstanceRecommendation(BaseModel):
    InstanceId: str
    InstanceType: str
    Action: str
    Priority: str
    Reason: str
    EstimatedSavings: str


class CostOptimizationReport(BaseModel):
    summary: SavingsSummary
    recommendations: List[InstanceRecommendation]
    message: str


# Initialize FastAPI app
app = FastAPI(
    title="AWS Cost Optimizer API",
    description="API for scanning EC2 instances and identifying cost savings opportunities",
    version="1.0.0"
)

# Global instances (in production, use dependency injection)
scanner = None
detector = None
calculator = None
generator = None


def get_scanner(region: str = "us-east-1"):
    """Get or create EC2Scanner instance."""
    global scanner
    if scanner is None or scanner.region != region:
        scanner = EC2Scanner(region=region)
    return scanner


def get_detector(cpu_threshold: float = 5.0):
    """Get or create IdleDetector instance."""
    global detector
    if detector is None or detector.cpu_threshold != cpu_threshold:
        detector = IdleDetector(cpu_threshold=cpu_threshold)
    return detector


def get_calculator(usd_to_inr: float = 83.0):
    """Get or create CostCalculator instance."""
    global calculator
    if calculator is None:
        calculator = CostCalculator(usd_to_inr_rate=usd_to_inr)
    return calculator


def get_generator():
    """Get or create ReportGenerator instance."""
    global generator
    if generator is None:
        generator = ReportGenerator()
    return generator


@app.get("/")
async def root():
    """API welcome endpoint."""
    return {
        "message": "Welcome to AWS Cost Optimizer API",
        "version": "1.0.0",
        "endpoints": {
            "scan": "/scan - Scan EC2 instances and get cost optimization report",
            "health": "/health - Health check",
            "docs": "/docs - Interactive API documentation"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "aws-cost-optimizer"}


@app.get("/scan", response_model=CostOptimizationReport)
async def scan_instances(
    region: str = Query(default="us-east-1", description="AWS region to scan"),
    cpu_threshold: float = Query(default=5.0, description="CPU threshold for idle detection"),
    days: int = Query(default=7, description="Number of days for metrics analysis"),
    use_mock_data: bool = Query(default=False, description="Use mock data for testing")
):
    """
    Scan EC2 instances and generate cost optimization report.
    
    Returns a comprehensive report with:
    - Current monthly costs
    - Potential savings (₹ per month)
    - Specific recommendations for each instance
    """
    try:
        # Initialize components
        ec2_scanner = get_scanner(region)
        idle_detector = get_detector(cpu_threshold)
        cost_calc = get_calculator()
        report_gen = get_generator()
        
        # Get instances (mock or real)
        if use_mock_data:
            instances = get_mock_instances()
        else:
            instances = ec2_scanner.scan_all_instances(days=days)
        
        if not instances:
            return CostOptimizationReport(
                summary=SavingsSummary(
                    total_instances=0,
                    total_current_monthly_cost_inr=0,
                    potential_monthly_savings_inr=0,
                    potential_annual_savings_inr=0,
                    savings_percentage=0
                ),
                recommendations=[],
                message="No instances found in the specified region."
            )
        
        # Analyze for idle instances
        analysis_result = idle_detector.analyze_instances(instances)
        
        # Calculate costs and savings
        cost_analysis = cost_calc.analyze_costs(instances, analysis_result)
        
        # Get recommendations
        recommendations = idle_detector.get_recommendations(analysis_result)
        
        # Build response
        summary = cost_analysis['summary']
        
        return CostOptimizationReport(
            summary=SavingsSummary(
                total_instances=summary['total_instances'],
                total_current_monthly_cost_inr=summary['potential_monthly_savings_inr'],
                potential_monthly_savings_inr=summary['potential_monthly_savings_inr'],
                potential_annual_savings_inr=summary['potential_annual_savings_inr'],
                savings_percentage=summary['savings_percentage']
            ),
            recommendations=[
                InstanceRecommendation(
                    InstanceId=rec['InstanceId'],
                    InstanceType=rec['InstanceType'],
                    Action=rec['Action'],
                    Priority=rec['Priority'],
                    Reason=rec['Reason'],
                    EstimatedSavings=rec['EstimatedSavings']
                )
                for rec in recommendations
            ],
            message=f"🎯 Saved ₹{summary['potential_monthly_savings_inr']:,.2f} per month"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/scan/text")
async def scan_instances_text(
    region: str = Query(default="us-east-1", description="AWS region to scan"),
    cpu_threshold: float = Query(default=5.0, description="CPU threshold for idle detection"),
    days: int = Query(default=7, description="Number of days for metrics analysis"),
    use_mock_data: bool = Query(default=True, description="Use mock data for testing")
):
    """
    Scan EC2 instances and return a formatted text report.
    
    This endpoint returns a human-readable text report with the famous 
    "Saved ₹X per month" simulation.
    """
    try:
        # Initialize components
        ec2_scanner = get_scanner(region)
        idle_detector = get_detector(cpu_threshold)
        cost_calc = get_calculator()
        report_gen = get_generator()
        
        # Get instances
        if use_mock_data:
            instances = get_mock_instances()
        else:
            instances = ec2_scanner.scan_all_instances(days=days)
        
        # Analyze
        analysis_result = idle_detector.analyze_instances(instances)
        cost_analysis = cost_calc.analyze_costs(instances, analysis_result)
        
        # Generate text report
        text_report = report_gen.generate_text_report(cost_analysis)
        
        return PlainTextResponse(text_report, media_type="text/plain")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/scan/summary")
async def scan_instances_summary(
    region: str = Query(default="us-east-1", description="AWS region to scan"),
    use_mock_data: bool = Query(default=True, description="Use mock data for testing")
):
    """
    Get a quick summary card of potential savings.
    """
    try:
        ec2_scanner = get_scanner(region)
        idle_detector = get_detector()
        cost_calc = get_calculator()
        report_gen = get_generator()
        
        if use_mock_data:
            instances = get_mock_instances()
        else:
            instances = ec2_scanner.scan_all_instances(days=7)
        
        analysis_result = idle_detector.analyze_instances(instances)
        cost_analysis = cost_calc.analyze_costs(instances, analysis_result)
        
        summary_card = report_gen.generate_summary_card(cost_analysis)
        
        return PlainTextResponse(summary_card, media_type="text/plain")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/scan/json")
async def scan_instances_json(
    region: str = Query(default="us-east-1", description="AWS region to scan"),
    cpu_threshold: float = Query(default=5.0, description="CPU threshold for idle detection"),
    days: int = Query(default=7, description="Number of days for metrics analysis"),
    use_mock_data: bool = Query(default=True, description="Use mock data for testing")
):
    """
    Scan EC2 instances and return full JSON report.
    """
    try:
        ec2_scanner = get_scanner(region)
        idle_detector = get_detector(cpu_threshold)
        cost_calc = get_calculator()
        report_gen = get_generator()
        
        if use_mock_data:
            instances = get_mock_instances()
        else:
            instances = ec2_scanner.scan_all_instances(days=days)
        
        analysis_result = idle_detector.analyze_instances(instances)
        cost_analysis = cost_calc.analyze_costs(instances, analysis_result)
        
        return JSONResponse(content=cost_analysis)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_mock_instances() -> List[Dict[str, Any]]:
    """
    Return mock instance data for testing/demo purposes.
    """
    from datetime import datetime, timedelta
    
    return [
        {
            'InstanceId': 'i-mock001',
            'InstanceType': 't3.medium',
            'State': 'running',
            'LaunchTime': datetime.utcnow() - timedelta(days=30),
            'Tags': {'Name': 'Dev-Server-1'},
            'Metrics': {
                'CPU': {'average': 2.5, 'maximum': 5.0, 'minimum': 0.5, 'datapoint_count': 168},
                'Network': {'avg_network_in_bytes': 50000, 'avg_network_out_bytes': 30000, 'datapoint_count': 7}
            }
        },
        {
            'InstanceId': 'i-mock002',
            'InstanceType': 'm5.large',
            'State': 'running',
            'LaunchTime': datetime.utcnow() - timedelta(days=60),
            'Tags': {'Name': 'Prod-Web-1'},
            'Metrics': {
                'CPU': {'average': 45.0, 'maximum': 80.0, 'minimum': 20.0, 'datapoint_count': 168},
                'Network': {'avg_network_in_bytes': 5000000, 'avg_network_out_bytes': 3000000, 'datapoint_count': 7}
            }
        },
        {
            'InstanceId': 'i-mock003',
            'InstanceType': 't2.micro',
            'State': 'stopped',
            'LaunchTime': datetime.utcnow() - timedelta(days=90),
            'Tags': {'Name': 'Old-Test-Server'},
            'Metrics': {
                'CPU': {'average': 0, 'maximum': 0, 'minimum': 0, 'datapoint_count': 0},
                'Network': {'avg_network_in_bytes': 0, 'avg_network_out_bytes': 0, 'datapoint_count': 0}
            }
        },
        {
            'InstanceId': 'i-mock004',
            'InstanceType': 't3.large',
            'State': 'running',
            'LaunchTime': datetime.utcnow() - timedelta(days=45),
            'Tags': {'Name': 'Staging-App'},
            'Metrics': {
                'CPU': {'average': 8.0, 'maximum': 25.0, 'minimum': 2.0, 'datapoint_count': 168},
                'Network': {'avg_network_in_bytes': 200000, 'avg_network_out_bytes': 150000, 'datapoint_count': 7}
            }
        },
        {
            'InstanceId': 'i-mock005',
            'InstanceType': 'c5.xlarge',
            'State': 'running',
            'LaunchTime': datetime.utcnow() - timedelta(days=20),
            'Tags': {'Name': 'Compute-Heavy'},
            'Metrics': {
                'CPU': {'average': 3.0, 'maximum': 15.0, 'minimum': 0.5, 'datapoint_count': 168},
                'Network': {'avg_network_in_bytes': 80000, 'avg_network_out_bytes': 60000, 'datapoint_count': 7}
            }
        }
    ]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
