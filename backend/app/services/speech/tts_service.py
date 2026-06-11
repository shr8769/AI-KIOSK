"""
TTS Service — Text-To-Speech wrapper using pyttsx3.
Owner: Harsha
"""

import asyncio
import logging
import os
import threading
import time
from typing import Any

from app.core.config import settings

logger = logging.getLogger(__name__)

# Lock to ensure only one thread uses SAPI5 engine at a time
_tts_lock = threading.Lock()


def _run_pyttsx3_synthesis(text: str, filepath: str, voice_id: str, speed_multiplier: float) -> float:
    """Synchronous pyttsx3 helper to run in a background thread."""
    with _tts_lock:
        import pyttsx3

        logger.debug(f"Initializing pyttsx3 for: {filepath}")
        engine = pyttsx3.init()

        # Configure speech rate (default is ~200 words per minute)
        rate = engine.getProperty("rate")
        engine.setProperty("rate", int(rate * speed_multiplier))

        # Select voice if requested
        if voice_id and voice_id != "default":
            voices = engine.getProperty("voices")
            for voice in voices:
                if voice_id.lower() in voice.name.lower() or voice_id == voice.id:
                    engine.setProperty("voice", voice.id)
                    logger.debug(f"Selected voice: {voice.name}")
                    break

        engine.save_to_file(text, filepath)
        engine.runAndWait()

        # Estimate duration based on word count (~150 WPM default)
        words = len(text.split())
        duration = round(words * (60.0 / int(rate * speed_multiplier)), 2)

        # Explicit clean-up of SAPI COM reference
        del engine
        return duration


class TTSService:
    async def synthesize(self, request) -> Any:
        """
        Convert text to speech.
        Saves output file to the static/audio directory and returns public audio URL.
        """
        from app.models.schemas import TTSResponse

        start_time = time.time()

        # Ensure static audio directory exists
        static_dir = os.path.join("static", "audio")
        os.makedirs(static_dir, exist_ok=True)

        if settings.USE_MOCK_SERVICES:
            # Mock TTS behavior
            latency_ms = int((time.time() - start_time) * 1000)
            return TTSResponse(
                session_id=request.session_id,
                audio_url="/static/audio/response.mp3",
                duration_seconds=5.0,
                format="mp3",
                latency_ms=latency_ms,
            )

        try:
            # Generate unique filename for this turn response
            filename = f"response_{request.session_id}_{int(time.time())}.wav"
            filepath = os.path.join(static_dir, filename)

            # Run the pyttsx3 code in a background thread to prevent blocking FastAPI event loop
            duration = await asyncio.to_thread(
                _run_pyttsx3_synthesis,
                request.text,
                filepath,
                request.voice_id,
                request.speed,
            )

            latency_ms = int((time.time() - start_time) * 1000)

            # Return absolute-path equivalent URL for static file serving
            audio_url = f"/static/audio/{filename}"

            return TTSResponse(
                session_id=request.session_id,
                audio_url=audio_url,
                duration_seconds=duration,
                format="wav",
                latency_ms=latency_ms,
            )

        except Exception as e:
            logger.exception(f"TTS Service synthesis failed: {e}")
            raise


# Singleton instance
tts_service = TTSService()
