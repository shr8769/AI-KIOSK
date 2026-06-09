import uuid
import json
from datetime import datetime
from typing import Optional, Dict, Any
import os

import redis.asyncio as aioredis
import aiosqlite

from app.core.config import settings
from app.core.logging import logger


class Session:
    def __init__(self, session_id: str, created_at: str, status: str = "active", metadata: Dict = None):
        self.session_id = session_id
        self.created_at = created_at
        self.status = status
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "created_at": self.created_at,
            "status": self.status,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Session":
        return cls(
            session_id=data["session_id"],
            created_at=data["created_at"],
            status=data.get("status", "active"),
            metadata=data.get("metadata", {}),
        )


_redis: Optional[aioredis.Redis] = None


async def get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
    return _redis


async def init_db():
    os.makedirs(os.path.dirname(settings.SQLITE_DB_PATH) or ".", exist_ok=True)
    async with aiosqlite.connect(settings.SQLITE_DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id  TEXT PRIMARY KEY,
                created_at  TEXT NOT NULL,
                closed_at   TEXT,
                status      TEXT NOT NULL DEFAULT 'active',
                metadata    TEXT DEFAULT '{}'
            )
        """)
        await db.commit()
    logger.info("SQLite DB initialised")


async def create_session(metadata: Dict = None) -> Session:
    session = Session(
        session_id=str(uuid.uuid4()),
        created_at=datetime.utcnow().isoformat(),
        metadata=metadata or {},
    )

    async with aiosqlite.connect(settings.SQLITE_DB_PATH) as db:
        await db.execute(
            "INSERT INTO sessions (session_id, created_at, status, metadata) VALUES (?,?,?,?)",
            (session.session_id, session.created_at, session.status, json.dumps(session.metadata)),
        )
        await db.commit()

    # Redis cache (best-effort)
    try:
        redis = await get_redis()
        await redis.set(
            f"session:{session.session_id}",
            json.dumps(session.to_dict()),
            ex=settings.SESSION_TTL_SECONDS,
        )
    except Exception as e:
        logger.warning(f"Redis unavailable, SQLite only: {e}")

    logger.info(f"Session created: {session.session_id}")
    return session


async def get_session(session_id: str) -> Optional[Session]:
    # Try Redis fast path
    try:
        redis = await get_redis()
        raw = await redis.get(f"session:{session_id}")
        if raw:
            return Session.from_dict(json.loads(raw))
    except Exception:
        pass

    # Fallback to SQLite
    async with aiosqlite.connect(settings.SQLITE_DB_PATH) as db:
        async with db.execute(
            "SELECT session_id, created_at, status, metadata FROM sessions WHERE session_id=?",
            (session_id,),
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return Session(session_id=row[0], created_at=row[1], status=row[2], metadata=json.loads(row[3]))
    return None


async def close_session(session_id: str) -> bool:
    closed_at = datetime.utcnow().isoformat()

    async with aiosqlite.connect(settings.SQLITE_DB_PATH) as db:
        result = await db.execute(
            "UPDATE sessions SET status='closed', closed_at=? WHERE session_id=? AND status='active'",
            (closed_at, session_id),
        )
        await db.commit()
        if result.rowcount == 0:
            return False

    try:
        redis = await get_redis()
        await redis.delete(f"session:{session_id}")
    except Exception:
        pass

    logger.info(f"Session closed: {session_id}")
    return True
