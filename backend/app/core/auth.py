import json
from dataclasses import dataclass
from typing import Any

from fastapi import Header, HTTPException, status

from app.core.config import get_settings


@dataclass(frozen=True)
class AuthenticatedUser:
    auth_sub: str
    email: str | None = None
    display_name: str | None = None
    photo_url: str | None = None


def _bearer_token(authorization: str | None) -> str:
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bearer token required")
    return token.strip()


def _test_user(token: str) -> AuthenticatedUser | None:
    settings = get_settings()
    if settings.app_env != "test" or not settings.life_test_auth_token:
        return None
    if token != settings.life_test_auth_token:
        return None
    return AuthenticatedUser(
        auth_sub=settings.life_test_auth_sub,
        email="test@ariva.local",
        display_name="Ariva Test User",
    )


def _firebase_app():
    settings = get_settings()
    if not settings.firebase_project_id and not settings.firebase_credentials_json and not settings.firebase_credentials_path:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Firebase auth is not configured")
    try:
        import firebase_admin
        from firebase_admin import credentials
    except ImportError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Firebase admin SDK is not installed") from exc

    if firebase_admin._apps:
        return firebase_admin.get_app()

    options = {"projectId": settings.firebase_project_id} if settings.firebase_project_id else None
    credential = None
    if settings.firebase_credentials_json:
        credential = credentials.Certificate(json.loads(settings.firebase_credentials_json))
    elif settings.firebase_credentials_path:
        credential = credentials.Certificate(settings.firebase_credentials_path)
    return firebase_admin.initialize_app(credential, options=options)


def _firebase_user(token: str) -> AuthenticatedUser:
    try:
        from firebase_admin import auth as firebase_auth

        decoded: dict[str, Any] = firebase_auth.verify_id_token(token, app=_firebase_app(), check_revoked=True)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Firebase token") from exc

    auth_sub = str(decoded.get("uid") or decoded.get("sub") or "")
    if not auth_sub:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Firebase token")
    return AuthenticatedUser(
        auth_sub=auth_sub,
        email=decoded.get("email"),
        display_name=decoded.get("name"),
        photo_url=decoded.get("picture"),
    )


def require_user(authorization: str | None = Header(default=None)) -> AuthenticatedUser:
    token = _bearer_token(authorization)
    test_user = _test_user(token)
    if test_user is not None:
        return test_user
    return _firebase_user(token)


def require_internal_token(authorization: str | None = Header(default=None)) -> None:
    settings = get_settings()
    if not settings.life_internal_token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Internal alert evaluation is not configured")
    token = _bearer_token(authorization)
    if token != settings.life_internal_token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid internal token")
