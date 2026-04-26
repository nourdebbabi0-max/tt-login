from datetime import datetime, timedelta
from hashlib import sha256
import secrets
from passlib.context import CryptContext
from jose import jwt
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )


def hash_session_token(token: str) -> str:
    return sha256(token.encode("utf-8")).hexdigest()


def generate_secure_token() -> str:
    return secrets.token_urlsafe(32)


def hash_generic_token(token: str) -> str:
    return sha256(token.encode("utf-8")).hexdigest()