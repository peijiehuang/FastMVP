import uuid
from datetime import datetime, timedelta, timezone

from jose import jwt, JWTError
from passlib.context import CryptContext

from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_token(user_key: str) -> str:
    """Create a JWT token containing only the user's Redis key UUID."""
    payload = {
        "login_user_key": user_key,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")


def parse_token(token: str) -> str | None:
    """Extract login_user_key from JWT token. Returns None if invalid."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        return payload.get("login_user_key")
    except JWTError:
        return None


def generate_uuid() -> str:
    return str(uuid.uuid4()).replace("-", "")
