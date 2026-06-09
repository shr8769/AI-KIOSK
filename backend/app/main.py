"""
FastAPI Application Entry Point
Owner: Harsha (Engineering Lead)

Starts the VidyaSahayak backend API server.
Run: uvicorn backend.app.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from backend.app.api.routes import detect, asr, riar, route, rag, tts, session
from backend.app.core.config import settings

logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle."""
    logger.info("🚀 VidyaSahayak backend starting...")
    logger.info(f"   Mode: {'DEBUG' if settings.DEBUG else 'PRODUCTION'}")
    logger.info(f"   Using real ASR: {settings.USE_REAL_ASR}")
    logger.info(f"   Using real RIAR: {settings.USE_REAL_RIAR}")
    logger.info(f"   Using real agents: {settings.USE_REAL_AGENTS}")
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

# ── Register Routers ──────────────────────────────────────────────────────────
app.include_router(detect.router, prefix="/api/v1", tags=["Detection"])
app.include_router(asr.router, prefix="/api/v1", tags=["ASR"])
app.include_router(riar.router, prefix="/api/v1", tags=["RIAR"])
app.include_router(route.router, prefix="/api/v1", tags=["Routing"])
app.include_router(rag.router, prefix="/api/v1", tags=["RAG"])
app.include_router(tts.router, prefix="/api/v1", tags=["TTS"])
app.include_router(session.router, prefix="/api/v1", tags=["Session"])


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "version": "0.1.0", "project": "VidyaSahayak"}
