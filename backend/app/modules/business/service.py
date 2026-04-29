from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.business.models import Business, BusinessConfig, Service, TableType
from app.modules.business.schemas import (
    BusinessConfigUpdate,
    BusinessUpdate,
    ServiceCreate,
    ServiceUpdate,
    TableTypeCreate,
    TableTypeUpdate,
)


async def get_business(db: AsyncSession, business_id: int) -> Business:
    result = await db.execute(select(Business).where(Business.id == business_id))
    business = result.scalar_one_or_none()
    if not business:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Negocio no encontrado")
    return business


async def update_business(
    db: AsyncSession, business_id: int, data: BusinessUpdate
) -> Business:
    business = await get_business(db, business_id)
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(business, field, value)
    await db.commit()
    await db.refresh(business)
    return business


async def get_business_config(db: AsyncSession, business_id: int) -> BusinessConfig:
    result = await db.execute(
        select(BusinessConfig).where(BusinessConfig.business_id == business_id)
    )
    config = result.scalar_one_or_none()
    if not config:
        config = BusinessConfig(business_id=business_id)
        db.add(config)
        await db.commit()
        await db.refresh(config)
    return config


async def update_business_config(
    db: AsyncSession, business_id: int, data: BusinessConfigUpdate
) -> BusinessConfig:
    config = await get_business_config(db, business_id)
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(config, field, value)
    await db.commit()
    await db.refresh(config)
    return config


async def list_table_types(db: AsyncSession, business_id: int) -> list[TableType]:
    result = await db.execute(
        select(TableType)
        .where(TableType.business_id == business_id)
        .order_by(TableType.capacity)
    )
    return list(result.scalars().all())


async def create_table_type(db: AsyncSession, business_id: int, data: TableTypeCreate) -> TableType:
    table = TableType(business_id=business_id, **data.model_dump())
    db.add(table)
    await db.commit()
    await db.refresh(table)
    return table


async def update_table_type(
    db: AsyncSession, business_id: int, table_id: int, data: TableTypeUpdate
) -> TableType:
    result = await db.execute(
        select(TableType).where(TableType.id == table_id, TableType.business_id == business_id)
    )
    table = result.scalar_one_or_none()
    if not table:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tipo de mesa no encontrado")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(table, field, value)
    await db.commit()
    await db.refresh(table)
    return table


async def delete_table_type(db: AsyncSession, business_id: int, table_id: int) -> None:
    result = await db.execute(
        select(TableType).where(TableType.id == table_id, TableType.business_id == business_id)
    )
    table = result.scalar_one_or_none()
    if not table:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tipo de mesa no encontrado")
    await db.delete(table)
    await db.commit()


async def list_services(db: AsyncSession, business_id: int) -> list[Service]:
    result = await db.execute(
        select(Service)
        .where(Service.business_id == business_id)
        .order_by(Service.name)
    )
    return list(result.scalars().all())


async def create_service(db: AsyncSession, business_id: int, data: ServiceCreate) -> Service:
    service = Service(business_id=business_id, **data.model_dump())
    db.add(service)
    await db.commit()
    await db.refresh(service)
    return service


async def update_service(
    db: AsyncSession, business_id: int, service_id: int, data: ServiceUpdate
) -> Service:
    result = await db.execute(
        select(Service).where(Service.id == service_id, Service.business_id == business_id)
    )
    service = result.scalar_one_or_none()
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Servicio no encontrado")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(service, field, value)
    await db.commit()
    await db.refresh(service)
    return service


async def delete_service(db: AsyncSession, business_id: int, service_id: int) -> None:
    result = await db.execute(
        select(Service).where(Service.id == service_id, Service.business_id == business_id)
    )
    service = result.scalar_one_or_none()
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Servicio no encontrado")
    await db.delete(service)
    await db.commit()
