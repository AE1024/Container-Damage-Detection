from pydantic import BaseModel, field_validator
import re


class RegisterRequest(BaseModel):
    first_name: str
    last_name: str
    phone: str
    password: str
    company: str

    @field_validator("phone")
    @classmethod
    def clean_phone(cls, v: str) -> str:
        cleaned = re.sub(r"\D", "", v)
        if len(cleaned) < 10:
            raise ValueError("Telefon numarası en az 10 haneli olmalıdır.")
        return cleaned

    @field_validator("password")
    @classmethod
    def check_password(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Şifre en az 6 karakter olmalıdır.")
        return v

    @field_validator("first_name", "last_name", "company")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Bu alan boş bırakılamaz.")
        return v.strip()


class LoginRequest(BaseModel):
    phone: str
    password: str

    @field_validator("phone")
    @classmethod
    def clean_phone(cls, v: str) -> str:
        return re.sub(r"\D", "", v)
    


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    full_name: str
    role: str
    company: str
