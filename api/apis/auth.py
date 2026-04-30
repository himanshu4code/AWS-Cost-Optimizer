"""Auth routes - deprecated."""

from fastapi import APIRouter

router = APIRouter(tags=["auth"])


# Auth0 has been deprecated in favor of session-based credential management.
