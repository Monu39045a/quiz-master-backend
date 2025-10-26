from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt

import secrets

# Secret key
SECRET_KEY = "abcdefghijklmnopqrstuvwxyz1234567890"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def create_access_token(sub: str, role_payload: dict = None, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = {"sub": sub}
    if role_payload:
        to_encode.update(role_payload)
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + \
            timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
