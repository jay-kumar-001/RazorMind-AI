from datetime import datetime, timedelta
import os

from jose import jwt
from passlib.context import CryptContext

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def _get_secret_key() -> str:
    if not SECRET_KEY:
        raise RuntimeError("SECRET_KEY must be configured in the environment")
    return SECRET_KEY

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
):
    return pwd_context.verify(
        plain_password,
        hashed_password
    )


def create_access_token(data: dict):

    to_encode = data.copy()

    expire = (
        datetime.utcnow()
        + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        _get_secret_key(),
        algorithm=ALGORITHM
    )
