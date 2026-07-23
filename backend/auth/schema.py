from pydantic import BaseModel, field_validator
from typing import Optional
import re

class RegisterRequest(BaseModel):
    first_name: str
    last_name:  str
    username:   str
    company: str
    password: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        v = v.strip().lower()
        if len(v) < 3:
            raise ValueError("Kullanıcı adı en az 3 karakter olmalıdır.")
        if not re.match(r'^[a-z0-9_]+$', v):
            raise ValueError("Kullanıcı adı yalnızca harf, rakam ve alt çizgi içerebilir.")
        return v

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
    username:   str
    password:   str
    first_name: Optional[str] = None
    last_name:  Optional[str] = None

    @field_validator("password")
    @classmethod
    def check_password(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Şifre en az 6 karakter olmalıdır.")
        return v

    @field_validator("username")
    @classmethod
    def strip_username(cls, v: str) -> str:
        return v.strip().lower()


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    full_name:  str
    role:  str
    company:  str
    username:  str



class UpdateProfileRequest(BaseModel):
    first_name : Optional[str] = None 
    last_name : Optional[str] = None
    company : Optional[str] = None
    password : Optional[str] = None

    @field_validator("first_name", "last_name")
    @classmethod
    def not_empty(cls, v: str) -> str:
        return v.strip()
    
    @field_validator("password")
    @classmethod
    def check_password(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v) < 6:
            raise ValueError("Şifre en az 6 karakter olmalıdır.")
        return v