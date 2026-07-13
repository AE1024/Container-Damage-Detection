import bcrypt

# Mockup kullanıcı deposu — DB gelince sadece bu değişir
_users_db: list[dict] = [
    {
        "first_name": "admin",
        "last_name": "admin",
        "phone": "5554443322",
        "password_hash": bcrypt.hashpw(b"admin123", bcrypt.gensalt()),
        "company": "Liman Operasyonları A.Ş.",
        "role": "admin",
    }
]


def _hash(password: str) -> bytes:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())


def _verify(password: str, hashed: bytes) -> bool:
    return bcrypt.checkpw(password.encode(), hashed)


def phone_exists(phone: str) -> bool:
    return any(u["phone"] == phone for u in _users_db)


def register_user(first_name: str, last_name: str, phone: str, password: str, company: str) -> dict:
    user = {
        "first_name": first_name.strip(),
        "last_name": last_name.strip(),
        "phone": phone,
        "password_hash": _hash(password),
        "company": company.strip(),
        "role": "operator",
    }
    _users_db.append(user)
    return user


def authenticate_user(phone: str, password: str) -> dict | None:
    for user in _users_db:
        if user["phone"] == phone and _verify(password, user["password_hash"]):
            return user
    return None
