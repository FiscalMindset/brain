"""Password hashing and self-contained HMAC auth tokens (stdlib only)."""

from __future__ import annotations

import hashlib
import hmac
import time
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db

_bearer = HTTPBearer(auto_error=False)

# ---------------------------------------------------------------- passwords
# passlib is pinned for bcrypt, but its $2b$ hashes trip a version check on
# newer bcrypt releases. PBKDF2-HMAC-SHA256 is stdlib-only and sufficient here.
_PBKDF2_ROUNDS = 120_000


def hash_password(password: str) -> str:
    """Return a ``pbkdf2_sha256$<salt>$<hex>`` hash for *password*."""
    salt = hashlib.sha256(f"{settings.SECRET_KEY}:{time.time_ns()}".encode()).hexdigest()[:32]
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), _PBKDF2_ROUNDS)
    return f"pbkdf2_sha256${salt}${digest.hex()}"


def verify_password(password: str, hashed: str) -> bool:
    """Constant-time check of *password* against a hash from :func:`hash_password`."""
    try:
        algo, salt, expected = hashed.split("$", 2)
        if algo != "pbkdf2_sha256":
            return False
    except ValueError:
        return False
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), _PBKDF2_ROUNDS)
    return hmac.compare_digest(digest.hex(), expected)


# -------------------------------------------------------------------- tokens
def _sign(payload: str) -> str:
    return hmac.new(settings.SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()


def create_token(user_id: str, expires_in: int = 86_400) -> str:
    """Create a ``<user_id>.<exp>.<sig>`` bearer token."""
    exp = int(time.time()) + expires_in
    payload = f"{user_id}.{exp}"
    return f"{payload}.{_sign(payload)}"


def decode_token(token: str) -> dict[str, Any] | None:
    """Verify *token* and return ``{"user_id": ..., "exp": ...}`` or ``None``."""
    try:
        user_id, exp, sig = token.rsplit(".", 2)
        if not hmac.compare_digest(_sign(f"{user_id}.{exp}"), sig):
            return None
        exp_i = int(exp)
    except (ValueError, AttributeError):
        return None
    if exp_i < int(time.time()):
        return None
    return {"user_id": user_id, "exp": exp_i}


def _unauthorized(detail: str = "Not authenticated") -> HTTPException:
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


_DUMMY_HASH = hash_password("dummy-password-for-timing-mitigation")

def dummy_hash() -> str:
    return _DUMMY_HASH

def require_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
):
    """FastAPI dependency: resolve the bearer token to a persisted user."""
    from app.models.models import User

    if credentials is None:
        raise _unauthorized()
    claims = decode_token(credentials.credentials)
    if claims is None:
        raise _unauthorized("Invalid or expired token")
    user = db.get(User, claims["user_id"])
    if user is None:
        raise _unauthorized("User not found")
    return user
