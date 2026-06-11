"""
FastAPI Application Entry Point
Owner: Harsha (Engineering Lead)

Starts the VidyaSahayak backend API server.
Run: uvicorn app.main:app --reload
"""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import asr, events, rag, riar, route, session, tts
from app.core.config import settings
from app.websockets.session_ws import websocket_session_handler

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

    # Initialize SQLite database schema
    from app.core.session_store import get_session, init_db
    await init_db()

    # Seed demo session for frontend local development
    try:
        demo_session = await get_session("demo_session_id")
        if not demo_session:
            logger.info("Seeding demo_session_id for development/testing...")
            import json
            from datetime import datetime

            import aiosqlite
            os.makedirs(os.path.dirname(settings.SQLITE_DB_PATH) or ".", exist_ok=True)
            async with aiosqlite.connect(settings.SQLITE_DB_PATH) as db:
                await db.execute(
                    "INSERT OR IGNORE INTO sessions (session_id, created_at, status, metadata) VALUES (?,?,?,?)",
                    ("demo_session_id", datetime.utcnow().isoformat(), "active", "{}"),
                )
                await db.commit()

            try:
                from app.core.session_store import get_redis
                redis = await get_redis()
                await redis.set(
                    "session:demo_session_id",
                    json.dumps({
                        "session_id": "demo_session_id",
                        "created_at": datetime.utcnow().isoformat(),
                        "status": "active",
                        "metadata": {}
                    }),
                    ex=settings.SESSION_TTL_SECONDS
                )
            except Exception:
                pass
    except Exception as e:
        logger.warning(f"Could not seed demo session: {e}")

    yield

    # Clean up connections
    try:
        from app.core.session_store import close_redis
        await close_redis()
    except Exception:
        pass
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
    allow_origin_regex=r"https?://.*",
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


# WebSocket Route
@app.websocket("/ws/session/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket_session_handler(websocket, session_id)


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "version": "0.1.0", "project": "VidyaSahayak"}
