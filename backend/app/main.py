"""
FastAPI Application Entry Point
Owner: Harsha (Engineering Lead)

Starts the VidyaSahayak backend API server.
Run: uvicorn app.main:app --reload
"""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import asr, events, rag, riar, route, session, tts
from app.core.config import settings

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle."""
    logger.info("🚀 VidyaSahayak backend starting...")
    logger.info(f"   Mode: {'DEBUG' if settings.DEBUG else 'PRODUCTION'}")
    logger.info(f"   Using mock services: {settings.USE_MOCK_SERVICES}")
    yield
    logger.info("⏹  VidyaSahayak backend shutting down...")


app = FastAPI(
    title="VidyaSahayak API",
    description="AI Avatar Kiosk Backend — PES University Research Project",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS — allow frontend (React on :3000) to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files folder
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# ── Register Routers ────────────────────────────────────────────────────────
app.include_router(events.router, prefix="/api/v1", tags=["Detection"])
app.include_router(asr.router, prefix="/api/v1", tags=["ASR"])
app.include_router(riar.router, prefix="/api/v1", tags=["RIAR"])
app.include_router(route.router, prefix="/api/v1", tags=["Routing"])
app.include_router(rag.router, prefix="/api/v1", tags=["RAG"])
app.include_router(tts.router, prefix="/api/v1", tags=["TTS"])
app.include_router(session.router, prefix="/api/v1", tags=["Session"])


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "version": "0.1.0", "project": "VidyaSahayak"}
