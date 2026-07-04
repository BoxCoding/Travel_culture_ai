from dataclasses import dataclass

from fastapi import Header, HTTPException, status
from jose import JWTError, jwt

from app.config import get_settings

ALGORITHM = "HS256"


@dataclass
class CurrentUser:
    sub: str
    email: str | None = None


def _decode(token: str) -> CurrentUser | None:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.auth_bridge_secret, algorithms=[ALGORITHM])
    except JWTError:
        return None

    sub = payload.get("sub")
    if not sub:
        return None
    return CurrentUser(sub=sub, email=payload.get("email"))


def _extract_token(authorization: str | None) -> str | None:
    if not authorization or not authorization.lower().startswith("bearer "):
        return None
    return authorization.split(" ", 1)[1].strip()


def get_current_user_optional(authorization: str | None = Header(default=None)) -> CurrentUser | None:
    token = _extract_token(authorization)
    if not token:
        return None
    return _decode(token)


def get_current_user_required(authorization: str | None = Header(default=None)) -> CurrentUser:
    token = _extract_token(authorization)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")

    user = _decode(token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    return user
