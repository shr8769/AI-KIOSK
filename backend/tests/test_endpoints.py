"""
Basic smoke tests for the FastAPI backend.
Run:  pytest backend/tests/ -v
"""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.core.session_store import init_db
from app.main import app


@pytest_asyncio.fixture(autouse=True)
async def setup_db(tmp_path, monkeypatch):
    """Use a temp SQLite DB for each test run."""
    db_path = str(tmp_path / "test.db")
    monkeypatch.setenv("SQLITE_DB_PATH", db_path)
    # Re-import settings so the env var is picked up
    import app.core.config as cfg
    cfg.settings.SQLITE_DB_PATH = db_path
    import app.core.session_store as ss
    ss.settings.SQLITE_DB_PATH = db_path
    await init_db()


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


# ── Health ────────────────────────────────────

@pytest.mark.asyncio
async def test_health(client):
    r = await client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


# ── Session CRUD ──────────────────────────────

@pytest.mark.asyncio
async def test_session_create_and_get(client):
    r = await client.post("/api/v1/session", json={"metadata": {"user": "test"}})
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    sid = data["session_id"]

    r2 = await client.get(f"/api/v1/session/{sid}")
    assert r2.status_code == 200
    assert r2.json()["session_id"] == sid


@pytest.mark.asyncio
async def test_session_close(client):
    r = await client.post("/api/v1/session", json={})
    sid = r.json()["session_id"]

    r2 = await client.delete(f"/api/v1/session/{sid}")
    assert r2.status_code == 200
    assert r2.json()["status"] == "closed"


@pytest.mark.asyncio
async def test_session_not_found(client):
    r = await client.get("/api/v1/session/nonexistent-id")
    assert r.status_code == 404


# ── Pipeline endpoints ────────────────────────

@pytest.mark.asyncio
async def test_detect(client):
    r = await client.post("/api/v1/detect", json={"source": "camera"})
    assert r.status_code == 200
    data = r.json()
    assert "person_detected" in data
    assert 0.0 <= data["confidence"] <= 1.0


@pytest.mark.asyncio
async def test_asr_requires_valid_session(client):
    r = await client.post("/api/v1/asr", json={
        "session_id": "bad-id",
        "audio_base64": "AAAA",
        "language": "en",
    })
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_full_pipeline(client):
    # Create session
    sid = (await client.post("/api/v1/session", json={})).json()["session_id"]

    # ASR
    r_asr = await client.post("/api/v1/asr", json={
        "session_id": sid, "audio_base64": "AAAA", "language": "en"
    })
    assert r_asr.status_code == 200
    transcript = r_asr.json()["transcript"]

    # RIAR
    r_riar = await client.post("/api/v1/riar", json={
        "session_id": sid, "transcript": transcript, "language": "en"
    })
    assert r_riar.status_code == 200

    # RAG
    r_rag = await client.post("/api/v1/rag", json={
        "session_id": sid, "query": transcript, "language": "en"
    })
    assert r_rag.status_code == 200
    assert "answer" in r_rag.json()

    # TTS
    r_tts = await client.post("/api/v1/tts", json={
        "session_id": sid, "text": r_rag.json()["answer"], "language": "en"
    })
    assert r_tts.status_code == 200
    assert "audio_base64" in r_tts.json()
