from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_business, get_current_user
from app.modules.business import schemas, service

router = APIRouter()


@router.get("/me", response_model=schemas.BusinessRead)
async def get_my_business(
    business_id: int = Depends(get_current_business),
    db: AsyncSession = Depends(get_db),
):
    return await service.get_business(db, business_id)


@router.put("/me", response_model=schemas.BusinessRead)
async def update_my_business(
    body: schemas.BusinessUpdate,
    business_id: int = Depends(get_current_business),
    db: AsyncSession = Depends(get_db),
):
    return await service.update_business(db, business_id, body)


@router.get("/me/config", response_model=schemas.BusinessConfigRead)
async def get_my_config(
    business_id: int = Depends(get_current_business),
    db: AsyncSession = Depends(get_db),
):
    return await service.get_business_config(db, business_id)


@router.put("/me/config", response_model=schemas.BusinessConfigRead)
async def update_my_config(
    body: schemas.BusinessConfigUpdate,
    business_id: int = Depends(get_current_business),
    db: AsyncSession = Depends(get_db),
):
    return await service.update_business_config(db, business_id, body)


@router.get("/me/tables", response_model=list[schemas.TableTypeRead])
async def list_tables(
    business_id: int = Depends(get_current_business),
    db: AsyncSession = Depends(get_db),
):
    return await service.list_table_types(db, business_id)


@router.post("/me/tables", response_model=schemas.TableTypeRead, status_code=201)
async def create_table(
    body: schemas.TableTypeCreate,
    business_id: int = Depends(get_current_business),
    db: AsyncSession = Depends(get_db),
):
    return await service.create_table_type(db, business_id, body)


@router.put("/me/tables/{table_id}", response_model=schemas.TableTypeRead)
async def update_table(
    table_id: int,
    body: schemas.TableTypeUpdate,
    business_id: int = Depends(get_current_business),
    db: AsyncSession = Depends(get_db),
):
    return await service.update_table_type(db, business_id, table_id, body)


@router.delete("/me/tables/{table_id}", status_code=204)
async def delete_table(
    table_id: int,
    business_id: int = Depends(get_current_business),
    db: AsyncSession = Depends(get_db),
):
    await service.delete_table_type(db, business_id, table_id)
    return Response(status_code=204)


@router.get("/me/services", response_model=list[schemas.ServiceRead])
async def list_services(
    business_id: int = Depends(get_current_business),
    db: AsyncSession = Depends(get_db),
):
    return await service.list_services(db, business_id)


@router.post("/me/services", response_model=schemas.ServiceRead, status_code=201)
async def create_service(
    body: schemas.ServiceCreate,
    business_id: int = Depends(get_current_business),
    db: AsyncSession = Depends(get_db),
):
    return await service.create_service(db, business_id, body)


@router.put("/me/services/{service_id}", response_model=schemas.ServiceRead)
async def update_service(
    service_id: int,
    body: schemas.ServiceUpdate,
    business_id: int = Depends(get_current_business),
    db: AsyncSession = Depends(get_db),
):
    return await service.update_service(db, business_id, service_id, body)


@router.delete("/me/services/{service_id}", status_code=204)
async def delete_service(
    service_id: int,
    business_id: int = Depends(get_current_business),
    db: AsyncSession = Depends(get_db),
):
    await service.delete_service(db, business_id, service_id)
    return Response(status_code=204)
