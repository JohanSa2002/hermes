from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.errors import global_exception_handler

app = FastAPI(
    title="HermesMessages API",
    description="Plataforma SaaS de automatización de reservas via WhatsApp",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.ENVIRONMENT == "development" else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(Exception, global_exception_handler)

# Routers — se van añadiendo por módulo
from app.modules.auth.router import router as auth_router
from app.modules.business.router import router as business_router
from app.modules.whatsapp.router import router as whatsapp_router
from app.modules.calendar.router import router as calendar_router
from app.modules.reservations.router import router as reservations_router
from app.modules.dashboard.router import router as dashboard_router
from app.modules.billing.router import router as billing_router
from app.modules.admin.router import router as admin_router

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(business_router, prefix="/business", tags=["business"])
app.include_router(whatsapp_router, prefix="/whatsapp", tags=["whatsapp"])
app.include_router(calendar_router, prefix="/calendar", tags=["calendar"])
app.include_router(reservations_router, prefix="/reservations", tags=["reservations"])
app.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
app.include_router(billing_router, prefix="/billing", tags=["billing"])
app.include_router(admin_router, prefix="/admin", tags=["admin"])
