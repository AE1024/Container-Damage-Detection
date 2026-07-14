from pydantic import BaseModel, field_validator

class RegisterRequest(BaseModel):
    first_name: str
    last_name:  str
    company: str
    password: str

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
    first_name: str
    last_name:  str
    password:   str

    @field_validator("first_name", "last_name")
    @classmethod
    def not_empty(cls, v: str) -> str:
        return v.strip()


class TokenResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"
    full_name:    str
    role:         str
    company:      str
