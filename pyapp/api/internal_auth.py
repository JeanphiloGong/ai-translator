from typing import Optional

from fastapi import Header, HTTPException

from pyapp.settings import get_settings


def require_internal_api_key(x_api_key: Optional[str] = Header(None, alias="X-API-KEY")) -> None:
    settings = get_settings()
    if not settings.internal_api_key:
        raise HTTPException(
            status_code=500,
            detail={"code": "INTERNAL_KEY_NOT_CONFIGURED", "message": "internal api key not configured"},
        )
    if x_api_key != settings.internal_api_key:
        raise HTTPException(
            status_code=401,
            detail={"code": "UNAUTHORIZED", "message": "invalid api key"},
        )
