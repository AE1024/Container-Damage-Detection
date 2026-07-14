from fastapi import APIRouter, HTTPException, status, Depends
from auth.schema import LoginRequest, RegisterRequest, TokenResponse
from auth.service import authenticate_user, register_user, user_exists
from core.security import create_access_token
from core.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", status_code=201)
def register(body: RegisterRequest):
    if user_exists(body.first_name, body.last_name):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Bu isimde bir kullanıcı zaten kayıtlı.",
        )
    user = register_user(
        first_name=body.first_name,
        last_name=body.last_name,
        company=body.company,
        password=body.password,
    )
    full_name = f"{user['first_name'].capitalize()} {user['last_name'].capitalize()}"
    return {"message": f"{full_name} başarıyla kayıt edildi.", "role": user["role"]}


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest):
    user = authenticate_user(body.first_name, body.last_name, body.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="İsim, soyisim veya şifre hatalı.",
        )
    full_name = f"{user['first_name'].capitalize()} {user['last_name'].capitalize()}"
    token = create_access_token({
        "sub":       f"{user['first_name']}_{user['last_name']}",
        "full_name": full_name,
        "role":      user["role"],
        "company":   user["company"],
    })
    return TokenResponse(
        access_token=token,
        full_name=full_name,
        role=user["role"],
        company=user["company"],
    )


@router.get("/me")
def me(current_user: dict = Depends(get_current_user)):
    return {
        "full_name": current_user["full_name"],
        "role":      current_user["role"],
        "company":   current_user["company"],
    }


@router.post("/logout", status_code=200)
def logout(current_user: dict = Depends(get_current_user)):
    # JWT stateless — sunucuda silinecek oturum yok.
    # Token geçerliliği client tarafında sona erdirilir.
    return {"message": "Oturum sonlandırıldı.", "user": current_user["full_name"]}

