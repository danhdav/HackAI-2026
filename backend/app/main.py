"""FastAPI application entrypoint."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.parser import router as parser_router

app = FastAPI(
    title="TaxMaxx Backend",
    version="0.1.0",
    debug=True,
    description=("TaxMaxx backend for document intake and parsing."),
)

# CORS: allow frontend (and any origin in dev). Use specific origins in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # permits any origin when credentials are not sent
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(parser_router)
