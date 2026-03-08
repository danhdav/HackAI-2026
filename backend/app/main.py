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

# Allow the Vite dev server (and same-origin) to call the API.
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(parser_router)
