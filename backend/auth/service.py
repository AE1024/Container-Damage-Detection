import bcrypt
from datetime import datetime, timezone
from bson import ObjectId
from core.database import users_col
from typing import Optional


def _hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def _verify(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def username_exists(username: str) -> bool:
    return users_col.find_one({"username": username.strip().lower()}) is not None


def register_user(first_name: str, last_name: str, username: str, company: str, password: str) -> dict:
    user = {
        "first_name":    first_name.strip().lower(),
        "last_name":     last_name.strip().lower(),
        "username":      username.strip().lower(),
        "company":       company.strip(),
        "password_hash": _hash(password),
        "role":          "operator",
        "created_at":    datetime.now(timezone.utc),
    }
    users_col.insert_one(user)
    return user


def authenticate_user(username: str, password: str) -> dict | None:
    user = users_col.find_one({"username": username.strip().lower()})
    if user and _verify(password, user["password_hash"]):
        return user
    return None

def update_profile(user_id: str, first_name: Optional[str], last_name: Optional[str], company: Optional[str], password: Optional[str]) -> dict:
    updated_fields = {}
    oid = ObjectId(user_id)
    user = users_col.find_one({"_id": oid})
    if not user:
        return {"status": "error", "message": "Kullanıcı bulunamadı."}

    if first_name is not None:
        updated_fields["first_name"] = first_name.strip().lower()
    if last_name is not None:
        updated_fields["last_name"] = last_name.strip().lower()
    if company is not None:
        updated_fields["company"] = company.strip()

    if password is not None:
        if _verify(password, user["password_hash"]):
            return {"status": "error", "message": "Yeni şifre eskisinden farklı olmalıdır."}
        updated_fields["password_hash"] = _hash(password)

    if updated_fields:
        users_col.update_one({"_id": oid}, {"$set": updated_fields})
        return {"status": "success"}

    return {"status": "no_changes"}

def delete_user(user_id: str) -> None:
    users_col.delete_one({"_id": ObjectId(user_id)})