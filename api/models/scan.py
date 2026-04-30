"""Internal scan domain models."""

from dataclasses import dataclass
from typing import Any, Dict

from api.schemas.scan import ScanResponse


@dataclass(frozen=True)
class ScanArtifacts:
    response: ScanResponse
    cost_analysis: Dict[str, Any]
