"""Application settings and environment helpers."""

from dataclasses import dataclass
from functools import lru_cache
from typing import List
import os


@dataclass(frozen=True)
class Settings:
    app_name: str = "AWS Cost Optimizer API"
    description: str = "API for scanning EC2 instances and identifying cost savings opportunities"
    version: str = "1.0.0"
    default_region: str = "us-east-1"
    default_cpu_threshold: float = 5.0
    default_days: int = 7
    default_usd_to_inr_rate: float = 83.0
    default_frontend_origin: str = "http://localhost:5173"
    frontend_origins: tuple[str, ...] = ()


def _parse_csv(value: str) -> tuple[str, ...]:
    return tuple(item.strip() for item in value.split(",") if item.strip())


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Read settings once and reuse them across the app."""
    return Settings(
        frontend_origins=_parse_csv(os.getenv("FRONTEND_ORIGINS", "http://localhost:5173")),
    )


def get_frontend_origins() -> List[str]:
    return list(get_settings().frontend_origins)
