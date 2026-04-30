"""Auth related API schemas."""

from pydantic import BaseModel


class Auth0Config(BaseModel):
    domain: str
    audience: str
    client_id: str
    issuer: str
    frontend_origin: str
    configured: bool


class CurrentUser(BaseModel):
    sub: str | None = None
    name: str | None = None
    email: str | None = None
    picture: str | None = None
