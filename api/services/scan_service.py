"""Scan orchestration service."""

from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import HTTPException

from api.config.settings import get_settings
from api.models.scan import ScanArtifacts
from api.schemas.scan import AWSCredentials, InstanceRecommendation, SavingsSummary, ScanRequest, ScanResponse
from cost_calculator import CostCalculator
from ec2_scanner import EC2Scanner
from idle_detector import IdleDetector
from report_generator import ReportGenerator


def get_mock_instances() -> list[Dict[str, Any]]:
    """Return mock instance data for testing/demo purposes."""
    from datetime import timedelta

    now = datetime.now(timezone.utc)

    return [
        {
            'InstanceId': 'i-mock001',
            'InstanceType': 't3.medium',
            'State': 'running',
            'LaunchTime': now - timedelta(days=30),
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
            'LaunchTime': now - timedelta(days=60),
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
            'LaunchTime': now - timedelta(days=90),
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
            'LaunchTime': now - timedelta(days=45),
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
            'LaunchTime': now - timedelta(days=20),
            'Tags': {'Name': 'Compute-Heavy'},
            'Metrics': {
                'CPU': {'average': 3.0, 'maximum': 15.0, 'minimum': 0.5, 'datapoint_count': 168},
                'Network': {'avg_network_in_bytes': 80000, 'avg_network_out_bytes': 60000, 'datapoint_count': 7}
            }
        }
    ]


def _serialize_user(user: Dict[str, Any] | None) -> Dict[str, Any] | None:
    if user is None:
        return None
    return {
        "sub": user.get("sub"),
        "name": user.get("name") or user.get("nickname") or user.get("email"),
        "email": user.get("email"),
        "picture": user.get("picture"),
    }


def _build_scanner(region: str, credentials: AWSCredentials | None, profile_name: str | None = None) -> EC2Scanner:
    scanner_kwargs: Dict[str, Any] = {
        "region": region,
        "profile_name": profile_name,
    }
    if credentials is not None:
        scanner_kwargs.update(
            {
                "aws_access_key_id": credentials.access_key_id.get_secret_value(),
                "aws_secret_access_key": credentials.secret_access_key.get_secret_value(),
                "aws_session_token": credentials.session_token.get_secret_value() if credentials.session_token else None,
            }
        )
    return EC2Scanner(**scanner_kwargs)


def _build_empty_artifacts(user: Dict[str, Any], report_gen: ReportGenerator) -> ScanArtifacts:
    summary = SavingsSummary(
        total_instances=0,
        total_current_monthly_cost_inr=0,
        potential_monthly_savings_inr=0,
        potential_annual_savings_inr=0,
        savings_percentage=0,
    )
    analysis = {
        "summary": summary.model_dump(),
        "breakdown": {},
        "details": {},
        "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
        "currency": "INR",
        "exchange_rate_used": get_settings().default_usd_to_inr_rate,
        "all_instance_costs": [],
    }
    response = ScanResponse(
        user=_serialize_user(user),
        summary=summary,
        recommendations=[],
        message="No instances found in the specified region.",
        summary_card=report_gen.generate_summary_card(analysis),
        report_text=report_gen.generate_text_report(analysis),
        analysis=analysis,
    )
    return ScanArtifacts(response=response, cost_analysis=analysis)


def run_scan(payload: ScanRequest, user: Dict[str, Any] | None) -> ScanArtifacts:
    """Run the EC2 optimization workflow and build a dashboard-friendly payload."""
    settings = get_settings()
    report_gen = ReportGenerator()
    idle_detector = IdleDetector(cpu_threshold=payload.cpu_threshold)
    cost_calc = CostCalculator(usd_to_inr_rate=settings.default_usd_to_inr_rate)

    if not payload.use_mock_data and payload.aws_credentials is None:
        raise HTTPException(
            status_code=400,
            detail="AWS credentials are required when use_mock_data is false.",
        )

    if payload.use_mock_data:
        instances = get_mock_instances()
    else:
        scanner = _build_scanner(payload.region, payload.aws_credentials)
        instances = scanner.scan_all_instances(days=payload.days)

    if not instances:
        return _build_empty_artifacts(user, report_gen)

    analysis_result = idle_detector.analyze_instances(instances)
    cost_analysis = cost_calc.analyze_costs(instances, analysis_result)
    recommendations = idle_detector.get_recommendations(analysis_result)
    summary = cost_analysis["summary"]

    response = ScanResponse(
        user=_serialize_user(user),
        summary=SavingsSummary(
            total_instances=summary["total_instances"],
            total_current_monthly_cost_inr=summary["total_current_monthly_cost_inr"],
            potential_monthly_savings_inr=summary["potential_monthly_savings_inr"],
            potential_annual_savings_inr=summary["potential_annual_savings_inr"],
            savings_percentage=summary["savings_percentage"],
        ),
        recommendations=[
            InstanceRecommendation(
                InstanceId=rec["InstanceId"],
                InstanceType=rec["InstanceType"],
                Action=rec["Action"],
                Priority=rec["Priority"],
                Reason=rec["Reason"],
                EstimatedSavings=rec["EstimatedSavings"],
            )
            for rec in recommendations
        ],
        message=f"🎯 Saved ₹{summary['potential_monthly_savings_inr']:,.2f} per month",
        summary_card=report_gen.generate_summary_card(cost_analysis),
        report_text=report_gen.generate_text_report(cost_analysis),
        analysis=cost_analysis,
    )

    return ScanArtifacts(response=response, cost_analysis=cost_analysis)
