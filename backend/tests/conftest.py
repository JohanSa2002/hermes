import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from unittest.mock import AsyncMock

from app.core.database import Base, get_db
from app.core.redis import get_redis
from app.main import app

# Importar todos los modelos para que Base.metadata los registre
from app.modules.auth.models import User  # noqa
from app.modules.business.models import Business, BusinessConfig  # noqa
from app.modules.reservations.models import Reservation  # noqa

TEST_DB_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/hermesmessages_test"


@pytest_asyncio.fixture(scope="session")
async def engine():
    _engine = create_async_engine(TEST_DB_URL)
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield _engine
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await _engine.dispose()


@pytest_asyncio.fixture
async def db(engine) -> AsyncSession:
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
def redis_mock() -> AsyncMock:
    mock = AsyncMock()
    mock.get = AsyncMock(return_value=None)
    mock.setex = AsyncMock()
    mock.delete = AsyncMock()
    mock.aclose = AsyncMock()
    return mock


@pytest_asyncio.fixture
async def client(db: AsyncSession, redis_mock: AsyncMock) -> AsyncClient:
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_redis] = lambda: redis_mock
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client_no_db(redis_mock: AsyncMock) -> AsyncClient:
    """Cliente HTTP sin fixture de base de datos — para endpoints que no usan DB."""
    app.dependency_overrides[get_redis] = lambda: redis_mock
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


# --- Helpers para crear datos de prueba ---

async def make_business(db: AsyncSession, **kwargs):
    from app.modules.business.models import Business, BusinessConfig
    from datetime import time

    business = Business(
        name=kwargs.get("name", "Restaurante Test"),
        type=kwargs.get("type", "restaurant"),
        timezone="UTC",
        status=kwargs.get("status", "active"),
        plan=kwargs.get("plan", "basic"),
        whatsapp_phone_number_id=kwargs.get("phone_number_id", "12345"),
        whatsapp_access_token=kwargs.get("access_token", "test-token"),
    )
    db.add(business)
    await db.flush()

    config = BusinessConfig(
        business_id=business.id,
        open_days=[0, 1, 2, 3, 4],  # lunes a viernes
        open_time=time(9, 0),
        close_time=time(18, 0),
        slot_duration=60,
        max_per_slot=1,
        blocked_dates=[],
        assistant_name="Hermes",
        tone="formal",
    )
    db.add(config)
    await db.commit()
    await db.refresh(business)
    return business


async def make_user(db: AsyncSession, business_id: int, **kwargs):
    from app.modules.auth.models import User
    from app.core.security import hash_password

    user = User(
        business_id=business_id,
        email=kwargs.get("email", "owner@test.com"),
        hashed_password=hash_password(kwargs.get("password", "secret123")),
        role=kwargs.get("role", "owner"),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
