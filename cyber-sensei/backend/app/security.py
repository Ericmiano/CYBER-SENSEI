"""
Authentication and security utilities for Cyber-Sensei.

Implements JWT-based authentication for API endpoints.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from jose import JWTError, jwt
import os
try:
    # Prefer python-jose verify from core to keep token handling consistent
    from .core.security import verify_token as core_verify_token
except Exception:
    core_verify_token = None

# Configuration
# Configuration
import secrets

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    if os.getenv("ENV") == "production":
        raise ValueError("JWT_SECRET_KEY must be set in production environment")
    # In development, generate a random key if not provided
    SECRET_KEY = secrets.token_urlsafe(32)
    # We can log a warning here if we had the logger set up, but print is fine for now or just silent
    print(f"WARNING: Using generated SECRET_KEY: {SECRET_KEY[:5]}...")

ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 480))

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Payload to encode (e.g., {"sub": "user_id"})
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Verify JWT token from HTTP Authorization header.

    This delegates to the core security implementation when available so tests
    that generate tokens with `app.core.security.create_access_token` will
    validate correctly.
    """
    if core_verify_token is not None:
        return await core_verify_token(credentials)

    token = credentials.credentials
    # Fallback simple validation using PyJWT if core isn't available
    try:
        import jwt as _pyjwt
        payload = _pyjwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user_id
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(user_id: str = Depends(verify_token)) -> str:
    """
    Get current authenticated user ID.
    
    Args:
        user_id: User ID from verified token
        
    Returns:
        User ID string
    """
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    return user_id


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[str]:
    """
    Get current authenticated user ID if token is provided, otherwise return None.
    Useful for endpoints that work with or without authentication.
    """
    if not credentials:
        return None
    
    try:
        return await verify_token(credentials)
    except HTTPException:
        return None