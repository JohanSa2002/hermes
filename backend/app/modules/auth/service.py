import asyncio
import httpx
from datetime import time as dtime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_access_token, hash_password, verify_password
from app.modules.auth.models import User
from app.modules.business.models import Business, BusinessConfig


def _token_for_user(user: User) -> str:
    return create_access_token({"sub": str(user.id), "business_id": user.business_id})


async def register_business(
    db: AsyncSession,
    business_name: str,
    business_type: str,
    timezone: str,
    email: str,
    password: str,
) -> tuple[str, int, int]:
    existing = await get_user_by_email(db, email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El correo ya está registrado",
        )

    business = Business(
        name=business_name,
        type=business_type,
        timezone=timezone,
        status="trial",
        plan="free",
    )
    db.add(business)
    await db.flush()

    db.add(
        BusinessConfig(
            business_id=business.id,
            open_days=[0, 1, 2, 3, 4],
            open_time=dtime(9, 0),
            close_time=dtime(18, 0),
            slot_duration=60,
            max_per_slot=1,
            blocked_dates=[],
            assistant_name="Hermes",
            tone="formal",
        )
    )

    hashed = await asyncio.to_thread(hash_password, password)
    user = User(
        business_id=business.id,
        email=email,
        hashed_password=hashed,
        role="owner",
    )
    db.add(user)
    await db.flush()

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El correo ya está registrado",
        )

    return _token_for_user(user), business.id, user.id


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def authenticate_user(db: AsyncSession, email: str, password: str) -> str:
    user = await get_user_by_email(db, email)
    if not user or not user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
        )
    if not await asyncio.to_thread(verify_password, password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
        )
    return _token_for_user(user)


async def exchange_meta_code(code: str, redirect_uri: str) -> dict:
    """Intercambia el código de autorización de Meta por un access token."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://graph.facebook.com/v20.0/oauth/access_token",
            params={
                "client_id": settings.META_APP_ID,
                "client_secret": settings.META_APP_SECRET,
                "code": code,
                "redirect_uri": redirect_uri,
            },
        )
    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al intercambiar código con Meta",
        )
    return response.json()


async def get_meta_user_info(access_token: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://graph.facebook.com/me",
            params={"fields": "id,email", "access_token": access_token},
        )
    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al obtener información del usuario de Meta",
        )
    return response.json()


async def meta_oauth_login(db: AsyncSession, code: str, redirect_uri: str) -> str:
    token_data = await exchange_meta_code(code, redirect_uri)
    meta_info = await get_meta_user_info(token_data["access_token"])

    result = await db.execute(select(User).where(User.meta_user_id == meta_info["id"]))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado. Completa el registro primero.",
        )

    return _token_for_user(user)
