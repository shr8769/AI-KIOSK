from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.kiosk import router as kiosk_router
from app.core.config import settings
from app.core.logging import logger
from app.core.middleware import RequestIDMiddleware
from app.core.session_store import init_db, close_redis
from app.websockets.session_ws import websocket_session_handler


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # ── Middleware ────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestIDMiddleware)

    # ── Routers ───────────────────────────────
    app.include_router(kiosk_router, prefix="/api/v1")

    # ── WebSocket ─────────────────────────────
    @app.websocket("/ws/session/{session_id}")
    async def ws_endpoint(websocket: WebSocket, session_id: str):
        await websocket_session_handler(websocket, session_id)

    # ── Lifecycle ─────────────────────────────
    @app.on_event("startup")
    async def on_startup():
        await init_db()
        logger.info(f"🚀  {settings.APP_NAME} v{settings.APP_VERSION} ready")
        logger.info(f"    Mock services: {settings.USE_MOCK_SERVICES}")

    @app.on_event("shutdown")
    async def on_shutdown():
        logger.info("Shutting down...")
        await close_redis()

    return app


app = create_app()
