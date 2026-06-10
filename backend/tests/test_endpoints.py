import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_detect():
    r = client.post("/api/v1/detect", json={
        "camera_id": "cam_front_01",
        "confidence": 0.95,
        "bounding_box": {"x": 100, "y": 100, "w": 200, "h": 400}
    })
    assert r.status_code == 200
    data = r.json()
    assert "session_id" in data
    assert data["action"] == "session_created"

def test_full_pipeline():
    # Detect creates session
    r_detect = client.post("/api/v1/detect", json={
        "camera_id": "cam_front_01",
        "confidence": 0.95,
        "bounding_box": {"x": 100, "y": 100, "w": 200, "h": 400}
    })
    sid = r_detect.json()["session_id"]

    # ASR
    r_asr = client.post("/api/v1/asr", json={
        "session_id": sid, "audio_base64": "AAAA", "language_hint": "en", "turn_id": 1
    })
    assert r_asr.status_code == 200
    transcript = r_asr.json()["transcript"]

    # RIAR
    r_riar = client.post("/api/v1/riar", json={
        "session_id": sid, "turn_id": 1, "query": transcript, "language": "en", "session_history": []
    })
    assert r_riar.status_code == 200

    # Route
    r_route = client.post("/api/v1/route", json={
        "session_id": sid, "refined_query": transcript, "domain": "admissions", "language": "en", "top_k": 5
    })
    assert r_route.status_code == 200

    # RAG
    r_rag = client.post("/api/v1/rag", json={
        "session_id": sid, "query": transcript, "context": r_route.json()["context_window"], "domain": "admissions", "language": "en"
    })
    assert r_rag.status_code == 200

    # TTS
    r_tts = client.post("/api/v1/tts", json={
        "session_id": sid, "text": r_rag.json()["answer"], "language": "en"
    })
    assert r_tts.status_code == 200
    assert "audio_url" in r_tts.json()
