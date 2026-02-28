"""
FastAPI application entry point.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import create_tables
from app.auth import router as auth_router
from app.routers.campaigns import router as campaigns_router
from app.routers.webhooks import router as webhooks_router
from app.routers.settings import router as settings_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create DB tables on startup."""
    create_tables()
    yield


app = FastAPI(
    title="SentinalGrid",
    description="Agentic Spreadsheet & Communication Platform",
    version="0.1.0",
    lifespan=lifespan,
)

# ── CORS — allow Streamlit frontend ──
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ──
app.include_router(auth_router)
app.include_router(campaigns_router)
app.include_router(webhooks_router)
app.include_router(settings_router)


@app.get("/health", tags=["system"])
async def health_check():
    return {"status": "ok"}
