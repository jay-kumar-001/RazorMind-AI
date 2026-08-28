import os
from jose import JWTError, jwt

from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import User

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials"
    )

    if not SECRET_KEY:
        raise HTTPException(
            status_code=503,
            detail="Authentication is unavailable: SECRET_KEY is not configured"
        )

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user = (
        db.query(User)
        .filter(User.id == int(user_id))
        .first()
    )

    if user is None:
        raise credentials_exception

    return user
