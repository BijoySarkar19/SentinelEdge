"""Security utilities for SentinelEdge.

Provides:
- Argon2 password hashing / verification
- JWT access-token creation and verification
- FastAPI dependencies: get_current_user, require_roles
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, VerifyMismatchError, InvalidHashError
from fastapi import Depends, HTTPException, Request, status
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import get_logger
from app.db.session import get_db

log = get_logger(__name__)

# ---------------------------------------------------------------------------
# Argon2 password hasher (singleton – thread-safe)
# ---------------------------------------------------------------------------
_ph = PasswordHasher(
    time_cost=2,        # number of iterations
    memory_cost=65536,  # 64 MiB
    parallelism=2,
    hash_len=32,
    salt_len=16,
)

# ---------------------------------------------------------------------------
# Password helpers
# ---------------------------------------------------------------------------

def hash_password(password: str) -> str:
    """Return an Argon2 hash of *password*.

    Parameters
    ----------
    password:
        The plain-text password supplied by the user.

    Returns
    -------
    str
        A string in the PHC format (``$argon2id$...``).
    """
    return _ph.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """Verify *plain* against an Argon2 *hashed* string.

    Returns ``True`` on success, ``False`` on mismatch.  Never raises.
    """
    try:
        return _ph.verify(hashed, plain)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


# ---------------------------------------------------------------------------
# JWT helpers
# ---------------------------------------------------------------------------

def create_access_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None,
) -> str:
    """Create a signed JWT access token.

    Parameters
    ----------
    data:
        Payload claims to embed (e.g. ``{"sub": user_id, "role": "admin"}``).
    expires_delta:
        Token lifetime.  Defaults to ``settings.access_token_expire_minutes``.

    Returns
    -------
    str
        Encoded JWT string.
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.access_token_expire_minutes)

    now = datetime.now(tz=timezone.utc)
    payload = {
        **data,
        "iat": now,
        "exp": now + expires_delta,
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def verify_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT access token.

    Parameters
    ----------
    token:
        The raw JWT string.

    Returns
    -------
    dict
        The decoded payload.

    Raises
    ------
    HTTPException (401)
        If the token is missing, expired, or has an invalid signature.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        log.warning("jwt verification failed", error=str(exc))
        raise credentials_exception from exc

    if payload.get("sub") is None:
        log.warning("jwt missing 'sub' claim")
        raise credentials_exception

    return payload


# ---------------------------------------------------------------------------
# FastAPI dependencies
# ---------------------------------------------------------------------------

def _extract_token(request: Request) -> str:
    """Pull the bearer token from the Authorization header or access_token cookie.

    Raises
    ------
    HTTPException (401)
        If no token can be found in either location.
    """
    # 1. Authorization: Bearer <token>
    auth_header: str | None = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header[len("Bearer "):]

    # 2. HTTP-only cookie fallback
    cookie_token: str | None = request.cookies.get("access_token")
    if cookie_token:
        return cookie_token

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated.",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """FastAPI dependency that returns the authenticated User ORM object.

    Reads the token from ``Authorization: Bearer`` or the ``access_token``
    cookie, verifies it, and fetches the corresponding user from the database.

    Parameters
    ----------
    request:
        The incoming HTTP request.
    db:
        Injected async database session.

    Returns
    -------
    User
        The authenticated user ORM instance.

    Raises
    ------
    HTTPException (401)
        If the token is invalid or the user no longer exists.
    """
    # Import here to avoid circular imports at module load time
    from app.models.user import User  # noqa: PLC0415

    token = _extract_token(request)
    payload = verify_token(token)

    user_id: str | None = payload.get("sub")
    result = await db.execute(select(User).where(User.id == user_id))
    user: User | None = result.scalar_one_or_none()

    if user is None:
        log.warning("authenticated user not found in db", user_id=user_id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def require_roles(*roles: str):
    """Dependency factory that enforces role-based access control.

    Usage::

        @router.get("/admin/dashboard", dependencies=[Depends(require_roles("admin"))])
        async def admin_dashboard():
            ...

        # Or inline:
        @router.delete("/cameras/{id}")
        async def delete_camera(user=Depends(require_roles("admin", "operator"))):
            ...

    Parameters
    ----------
    *roles:
        One or more role strings that are permitted to access the endpoint.

    Returns
    -------
    Callable
        A FastAPI dependency that raises ``HTTP 403`` when the authenticated
        user's role is not in *roles*.
    """

    async def _role_checker(
        current_user: Any = Depends(get_current_user),
    ) -> Any:
        user_role: str = getattr(current_user, "role", "")
        if user_role not in roles:
            log.warning(
                "access denied – insufficient role",
                user_id=str(getattr(current_user, "id", "?")),
                user_role=user_role,
                required_roles=list(roles),
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation requires one of the following roles: {', '.join(roles)}.",
            )
        return current_user

    return _role_checker


def require_role(roles: list[str] | str):
    """Alias for require_roles accepting list or single role."""
    if isinstance(roles, str):
        return require_roles(roles)
    return require_roles(*roles)


def decode_access_token(token: str) -> dict[str, Any] | None:
    """Safe token decode returning None on error (for test utilities)."""
    try:
        return verify_token(token)
    except Exception:
        return None

