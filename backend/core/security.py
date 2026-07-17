import os
import pathlib
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

_ENV_PATH = pathlib.Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(_ENV_PATH)

SECRET_KEY = os.getenv("SECRET_KEY", "port-konteyner-gizli-anahtar-2024")
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 8


def create_access_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRE_HOURS)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None
