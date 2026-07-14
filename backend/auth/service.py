import bcrypt
from datetime import datetime, timezone
from core.database import users_col


def _hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def _verify(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def user_exists(first_name: str, last_name: str) -> bool:
    return users_col.find_one(
        {"first_name": first_name.strip().lower(), "last_name": last_name.strip().lower()},
        {"_id": 1},
    ) is not None


def register_user(first_name: str, last_name: str, company: str, password: str) -> dict:
    user = {
        "first_name":    first_name.strip().lower(),
        "last_name":     last_name.strip().lower(),
        "company":       company.strip(),
        "password_hash": _hash(password),
        "role":          "operator",
        "created_at":    datetime.now(timezone.utc),
    }
    users_col.insert_one(user)
    return user


def authenticate_user(first_name: str, last_name: str, password: str) -> dict | None:
    user = users_col.find_one({
        "first_name": first_name.strip().lower(),
        "last_name":  last_name.strip().lower(),
    })
    if user and _verify(password, user["password_hash"]):
        return user
    return None


def seed_admin() -> None:
    if not user_exists("admin", "admin"):
        users_col.insert_one({
            "first_name":    "admin",
            "last_name":     "admin",
            "company":       "YILPORT",
            "password_hash": _hash("admin123"),
            "role":          "admin",
            "created_at":    datetime.now(timezone.utc),
        })
