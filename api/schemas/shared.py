"""Shared API schemas for frontend and scan-related metadata."""

from pydantic import BaseModel


class FrontendConfig(BaseModel):
    frontend_origin: str
    configured: bool


class CurrentUser(BaseModel):
    sub: str | None = None
    name: str | None = None
    email: str | None = None
    picture: str | None = None