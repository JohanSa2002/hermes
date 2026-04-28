from fastapi import APIRouter, Depends, HTTPException, Response, status
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import create_access_token, decode_token
from app.modules.auth import schemas, service

router = APIRouter()


@router.post("/register", response_model=schemas.RegisterResponse, status_code=201)
async def register(body: schemas.RegisterRequest, db: AsyncSession = Depends(get_db)):
    token, business_id, user_id = await service.register_business(
        db,
        business_name=body.business_name,
        business_type=body.business_type,
        timezone=body.timezone,
        email=body.email,
        password=body.password,
    )
    return schemas.RegisterResponse(
        access_token=token,
        business_id=business_id,
        user_id=user_id,
    )


@router.post("/login", response_model=schemas.TokenResponse)
async def login(body: schemas.LoginRequest, db: AsyncSession = Depends(get_db)):
    token = await service.authenticate_user(db, body.email, body.password)
    return schemas.TokenResponse(access_token=token)


@router.post("/meta-callback", response_model=schemas.TokenResponse)
async def meta_callback(body: schemas.MetaCallbackRequest, db: AsyncSession = Depends(get_db)):
    token = await service.meta_oauth_login(db, body.code, body.redirect_uri)
    return schemas.TokenResponse(access_token=token)


@router.post("/refresh", response_model=schemas.TokenResponse)
async def refresh(body: schemas.RefreshRequest):
    try:
        payload = decode_token(body.access_token)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
    new_token = create_access_token(
        {"sub": payload["sub"], "business_id": payload["business_id"]}
    )
    return schemas.TokenResponse(access_token=new_token)


@router.post("/logout", status_code=204)
async def logout():
    return Response(status_code=204)
