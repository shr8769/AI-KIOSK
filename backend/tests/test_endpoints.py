"""
Endpoint Integration Tests
Owner: Engineering Team

Tests for all API endpoints: detection, ASR, RIAR, routing, RAG, TTS, and session management.
"""

from fastapi.testclient import TestClient


class TestHealth:
    """Health check endpoint tests."""

    def test_health(self, client: TestClient):
        """Test health endpoint."""
        r = client.get("/health")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"
        assert "version" in data
        assert "project" in data


class TestDetection:
    """Detection endpoint tests."""

    def test_detect(self, client: TestClient):
        """Test person detection endpoint creates session."""
        r = client.post(
            "/api/v1/events",
            json={
                "event_type": "PERSON_DETECTED",
                "camera_id": "cam_front_01",
                "payload": {
                    "confidence": 0.95,
                    "bounding_box": {"x": 100, "y": 100, "w": 200, "h": 400},
                },
            },
        )
        assert r.status_code == 200
        data = r.json()
        assert "session_id" in data
        assert data["action_taken"] == "session_created"
        assert "message" in data


class TestFullPipeline:
    """End-to-end pipeline tests."""

    def test_full_pipeline(self, client: TestClient):
        """
        Test complete user interaction flow:
        Detect → ASR → RIAR → Route → RAG → TTS
        """
        # Step 1: Detect person and create session
        r_detect = client.post(
            "/api/v1/events",
            json={
                "event_type": "PERSON_DETECTED",
                "camera_id": "cam_front_01",
                "payload": {
                    "confidence": 0.95,
                    "bounding_box": {"x": 100, "y": 100, "w": 200, "h": 400},
                },
            },
        )
        assert r_detect.status_code == 200
        sid = r_detect.json()["session_id"]
        assert sid is not None

        # Step 2: ASR - Convert audio to text
        r_asr = client.post(
            "/api/v1/asr",
            json={"session_id": sid, "audio_base64": "AAAA", "language_hint": "en", "turn_id": 1},
        )
        assert r_asr.status_code == 200
        transcript = r_asr.json()["transcript"]
        assert transcript is not None

        # Step 3: RIAR - Refine intent and context
        r_riar = client.post(
            "/api/v1/riar",
            json={
                "session_id": sid,
                "turn_id": 1,
                "query": transcript,
                "language": "en",
                "session_history": [],
            },
        )
        assert r_riar.status_code == 200
        refined_query = r_riar.json()["refined_query"]

        # Step 4: Route - Determine domain
        r_route = client.post(
            "/api/v1/route",
            json={
                "session_id": sid,
                "refined_query": refined_query,
                "domain": "admissions",
                "language": "en",
                "top_k": 5,
            },
        )
        assert r_route.status_code == 200
        context_window = r_route.json().get("context_window")

        # Step 5: RAG - Retrieve and generate answer
        r_rag = client.post(
            "/api/v1/rag",
            json={
                "session_id": sid,
                "query": refined_query,
                "context": context_window,
                "domain": "admissions",
                "language": "en",
            },
        )
        assert r_rag.status_code == 200
        answer = r_rag.json()["answer"]
        assert answer is not None

        # Step 6: TTS - Convert answer to speech
        r_tts = client.post(
            "/api/v1/tts", json={"session_id": sid, "text": answer, "language": "en"}
        )
        assert r_tts.status_code == 200
        data = r_tts.json()
        assert "audio_url" in data
