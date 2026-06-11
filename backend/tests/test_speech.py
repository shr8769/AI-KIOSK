"""
Speech Pipeline Unit Tests
Owner: Harsha
"""

import io
import os
import wave

import numpy as np
import pytest

from app.core.config import settings
from app.models.schemas import ASRRequest, TTSRequest
from app.services.speech.asr_service import asr_service
from app.services.speech.tts_service import tts_service


def generate_silent_wav(sample_rate: int = 16000, duration_seconds: float = 0.5) -> bytes:
    """Generates a valid mono 16-bit PCM WAV file in bytes containing silence."""
    output = io.BytesIO()
    with wave.open(output, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit PCM
        wf.setframerate(sample_rate)
        # Write silence frames (2 bytes per sample)
        wf.writeframes(b"\x00\x00" * int(sample_rate * duration_seconds))
    return output.getvalue()


class TestASRService:
    @pytest.mark.asyncio
    async def test_asr_mock_transcribe(self):
        """Test ASR Service under mock settings."""
        # Force mock settings for this test
        old_val = settings.USE_MOCK_SERVICES
        settings.USE_MOCK_SERVICES = True

        try:
            req = ASRRequest(
                session_id="test_sess_01",
                audio_base64="AAAA",  # invalid but fine for mock
                language_hint="en",
                turn_id=1
            )
            response = await asr_service.transcribe(req)
            assert response.session_id == "test_sess_01"
            assert response.turn_id == 1
            assert response.transcript is not None
            assert response.detected_language == "en"
        finally:
            settings.USE_MOCK_SERVICES = old_val

    def test_wav_decoding_to_numpy(self):
        """Verify in-memory WAV decoding decodes accurately to normalized numpy array."""
        wav_bytes = generate_silent_wav(sample_rate=16000, duration_seconds=0.2)
        audio_data = asr_service._load_wav_to_numpy(wav_bytes)

        assert isinstance(audio_data, np.ndarray)
        assert audio_data.dtype == np.float32
        # Check that it's all silence/zeros
        assert np.allclose(audio_data, 0.0, atol=1e-4)
        # Length check (16000 Hz * 0.2s = 3200 samples)
        assert len(audio_data) == 3200


class TestTTSService:
    @pytest.mark.asyncio
    async def test_tts_mock_synthesis(self):
        """Test mock TTS synthesis endpoints."""
        old_val = settings.USE_MOCK_SERVICES
        settings.USE_MOCK_SERVICES = True

        try:
            req = TTSRequest(
                session_id="test_sess_01",
                text="Hello PES University",
                language="en"
            )
            response = await tts_service.synthesize(req)
            assert response.session_id == "test_sess_01"
            assert response.audio_url == "/static/audio/response.mp3"
            assert response.duration_seconds > 0
        finally:
            settings.USE_MOCK_SERVICES = old_val

    @pytest.mark.asyncio
    async def test_tts_real_synthesis(self):
        """Test local offline TTS SAPI5 file creation."""
        import sys
        if sys.platform != "win32":
            pytest.skip("pyttsx3 real synthesis is only supported on Windows hosts.")

        old_val = settings.USE_MOCK_SERVICES
        settings.USE_MOCK_SERVICES = False

        try:
            req = TTSRequest(
                session_id="test_sess_real",
                text="Welcome to the kiosk.",
                language="en",
                speed=1.0
            )
            response = await tts_service.synthesize(req)

            assert response.session_id == "test_sess_real"
            assert "response_test_sess_real_" in response.audio_url
            assert response.format == "wav"

            # Verify the output file was actually created in the filesystem
            local_path = response.audio_url.lstrip("/")
            assert os.path.exists(local_path)
            assert os.path.getsize(local_path) > 44  # Larger than empty WAV header

            # Clean up the test audio file
            if os.path.exists(local_path):
                os.remove(local_path)
        finally:
            settings.USE_MOCK_SERVICES = old_val
