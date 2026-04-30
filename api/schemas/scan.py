"""Scan request and response schemas."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, SecretStr


class AWSCredentials(BaseModel):
    access_key_id: SecretStr
    secret_access_key: SecretStr
    session_token: Optional[SecretStr] = None


class ScanRequest(BaseModel):
    region: str = "us-east-1"
    cpu_threshold: float = 5.0
    days: int = 7
    use_mock_data: bool = False
    aws_credentials: Optional[AWSCredentials] = None


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


class ScanResponse(BaseModel):
    user: Optional[Dict[str, Any]] = None
    summary: SavingsSummary
    recommendations: List[InstanceRecommendation]
    message: str
    summary_card: str
    report_text: str
    analysis: Dict[str, Any]
