"""FastAPI application entrypoint."""

from fastapi import FastAPI

from app.config import settings
from app.routes.calculations import router as calculations_router
from app.routes.chatbot import router as chatbot_router
from app.routes.health import router as health_router
from app.routes.parser import router as parser_router
from app.routes.tax_session import router as tax_session_router

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    debug=settings.app_debug,
    description=(
        "TaxMaxx backend skeleton for document intake, tax session storage, "
        "deterministic 1040 draft calculations, and optional chatbot scaffolding."
    ),
)

app.include_router(health_router)
app.include_router(parser_router)
app.include_router(tax_session_router)
app.include_router(calculations_router)
app.include_router(chatbot_router)
