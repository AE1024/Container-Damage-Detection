from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from core.security import verify_token
from core.database import revoked_tokens_col

bearer = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer)) -> dict:
    token = credentials.credentials
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Geçersiz veya süresi dolmuş token. Lütfen tekrar giriş yapın.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if revoked_tokens_col.find_one({"token": token}):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Oturum sonlandırılmış. Lütfen tekrar giriş yapın.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload
