"""Authentication: register and login, returning bearer tokens."""

import re
import time
from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import create_token, dummy_hash, hash_password, verify_password
from app.models.models import User
from app.services.audit import record_audit

router = APIRouter(prefix="/auth", tags=["auth"])

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# In-memory per-IP rate limiter: 60 requests / minute on /auth/*
_RATE_LIMIT = 60
_RATE_WINDOW = 60.0
_hits: dict[str, list[float]] = defaultdict(list)


def check_rate_limit(ip: str) -> bool:
    """Return True if allowed; also usable directly in tests."""
    now = time.time()
    bucket = _hits[ip]
    _hits[ip] = [t for t in bucket if now - t < _RATE_WINDOW]
    if len(_hits[ip]) >= _RATE_LIMIT:
        return False
    _hits[ip].append(now)
    return True


def _enforce_rate_limit(request: Request) -> None:
    ip = request.client.host if request.client else "unknown"
    if not check_rate_limit(ip):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")


class Credentials(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=8, max_length=256)
    full_name: str | None = Field(default=None, max_length=254)

    from pydantic import field_validator

    @field_validator("email")
    @classmethod
    def _valid_email(cls, v: str) -> str:
        if not EMAIL_RE.match(v.strip()):
            raise ValueError("Invalid email format")
        return v


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/register", response_model=TokenOut, status_code=status.HTTP_201_CREATED)
def register(payload: Credentials, request: Request, db: Session = Depends(get_db)):
    _enforce_rate_limit(request)
    """Create a user and return a bearer token."""
    existing = db.query(User).filter(User.email == payload.email.lower()).first()
    if existing is not None:
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(
        email=payload.email.lower(),
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    record_audit(db, "auth.register", user_id=user.id, target=user.email)
    db.commit()
    return TokenOut(access_token=create_token(user.id))


@router.post("/login", response_model=TokenOut)
def login(payload: Credentials, request: Request, db: Session = Depends(get_db)):
    """Verify credentials and return a bearer token."""
    _enforce_rate_limit(request)
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    # Always verify (dummy hash when missing) to mitigate timing attacks
    hashed = user.hashed_password if user else dummy_hash()
    ok = verify_password(payload.password, hashed)
    if user is None or not ok:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    record_audit(db, "auth.login", user_id=user.id, target=user.email)
    db.commit()
    return TokenOut(access_token=create_token(user.id))
