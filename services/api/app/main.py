"""FastAPI Application Entry Point."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.config import get_config
from app.database import init_engine
# from app.api.router import api_router  # Will add soon

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_engine()
    yield
    # Shutdown
    # (Close engine if needed, though asyncpg usually cleans up)


config = get_config()

app = FastAPI(
    title="AcoustiStruct API",
    description="Dialect-aware, voice-first semantic data-capture system.",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[config.frontend_url] if not config.demo_mode else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "env": config.env, "demo_mode": config.demo_mode}

# app.include_router(api_router, prefix="/api/v1")
