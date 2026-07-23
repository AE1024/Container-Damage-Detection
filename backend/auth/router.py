from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from auth.schema import LoginRequest, RegisterRequest, TokenResponse , UpdateProfileRequest
from auth.service import authenticate_user, register_user, username_exists, update_profile, delete_user
from containers.service import delete_containers_by_user
from core.security import create_access_token
from core.dependencies import get_current_user
from core.database import revoked_tokens_col

bearer = HTTPBearer()

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.get("/check-username/{username}")
def check_username(username: str):
    exists = username_exists(username)
    return {"available": not exists}


@router.post("/register", status_code=201, response_model=TokenResponse)
def register(body: RegisterRequest):
    if username_exists(body.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Bu kullanıcı adı zaten alınmış.",
        )
    user = register_user(
        first_name=body.first_name,
        last_name=body.last_name,
        username=body.username,
        company=body.company,
        password=body.password,
    )
    full_name = f"{user['first_name'].capitalize()} {user['last_name'].capitalize()}"
    token = create_access_token({
        "sub":       str(user["_id"]),
        "full_name": full_name,
        "role":      user["role"],
        "company":   user["company"],
        "username":  user["username"],
    })
    return TokenResponse(
        access_token=token,
        full_name=full_name,
        role=user["role"],
        company=user["company"],
        username=user["username"],
    )


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest):
    user = authenticate_user(body.username, body.first_name, body.last_name, body.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Kullanıcı adı veya şifre hatalı.",
        )
    full_name = f"{user['first_name'].capitalize()} {user['last_name'].capitalize()}"
    token = create_access_token({
        "sub":  str(user["_id"]),
        "full_name": full_name,
        "role":  user["role"],
        "company": user["company"],
        "username": user["username"],
    })
    return TokenResponse(
        access_token=token,
        full_name=full_name,
        role=user["role"],
        company=user["company"],
        username=user["username"],
    )


@router.get("/me")
def me(current_user: dict = Depends(get_current_user)):
    return {
        "full_name": current_user["full_name"],
        "role":current_user["role"],
        "company": current_user["company"],
        "username": current_user.get("username", ""),
    }


@router.post("/logout", status_code=200)
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    current_user: dict = Depends(get_current_user),
):
    revoked_tokens_col.insert_one({
        "token":  credentials.credentials,
        "revoked_at": datetime.now(timezone.utc),
    })
    return {"message": "Oturum sonlandırıldı.", "user": current_user["full_name"]}


@router.put("/me/profile", status_code=200)
def update_me(
    body: UpdateProfileRequest,
    current_user: dict = Depends(get_current_user),
):
    result = update_profile(
        user_id=current_user["sub"],
        first_name=body.first_name,
        last_name=body.last_name,
        company=body.company,
        password=body.password,
    )
    if result["status"] == "error":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["message"])
    return result


@router.delete("/me", status_code=200)
def delete_me(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["sub"]
    delete_containers_by_user(user_id)
    delete_user(user_id)
    revoked_tokens_col.insert_one({
        "token": credentials.credentials,
        "revoked_at": datetime.now(timezone.utc),
    })
    return {"message": "Hesap ve ilişkili tüm konteynerler silindi."}