from fastapi import APIRouter, HTTPException, status
from auth.schema import LoginRequest, RegisterRequest, TokenResponse
from auth.service import authenticate_user, register_user, phone_exists
from core.security import create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", status_code=201)
def register(body: RegisterRequest):
    if phone_exists(body.phone):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Bu telefon numarası zaten kayıtlı.",
        )
    user = register_user(
        first_name=body.first_name,
        last_name=body.last_name,
        phone=body.phone,
        password=body.password,
        company=body.company,
    )
    return {
        "message": f"{user['first_name'].capitalize()} {user['last_name'].capitalize()} başarıyla kayıt edildi.",
        "role": user["role"],
    }


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest):
    user = authenticate_user(body.phone, body.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Telefon numarası veya şifre hatalı.",
        )
    token = create_access_token({
        "sub": user["phone"],
        "full_name": f"{user['first_name'].capitalize()} {user['last_name'].capitalize()}",
        "role": user["role"],
        "company": user["company"],
    })
    return TokenResponse(
        access_token=token,
        full_name=f"{user['first_name'].capitalize()} {user['last_name'].capitalize()}",
        role=user["role"],
        company=user["company"],
    )
