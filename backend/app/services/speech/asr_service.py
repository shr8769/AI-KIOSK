"""
ASR Service — Speech-To-Text wrapper using Whisper.
Owner: Harsha
"""

import base64
import io
import logging
import time
import wave
from typing import Any

import numpy as np

from app.core.config import settings

logger = logging.getLogger(__name__)


class ASRService:
    def __init__(self):
        self.model = None

    def _get_model(self):
        """Lazy load Whisper model to avoid slow server startup."""
        if self.model is None:
            model_size = settings.WHISPER_MODEL_SIZE
            logger.info(f"Loading faster-whisper model '{model_size}' on CPU...")
            from faster_whisper import WhisperModel
            # Using configured model with int8 quantization for speed on CPU
            self.model = WhisperModel(model_size, device="cpu", compute_type="int8")
            logger.info(f"faster-whisper model '{model_size}' loaded.")
        return self.model

    def _load_wav_to_numpy(self, audio_bytes: bytes) -> np.ndarray:
        """
        Decodes WAV file bytes directly into a normalized float32 numpy array.
        Bypasses FFmpeg dependency entirely. Falls back to raw 16-bit PCM.
        """
        try:
            with wave.open(io.BytesIO(audio_bytes), "rb") as wav_file:
                n_channels = wav_file.getnchannels()
                sample_width = wav_file.getsampwidth()
                framerate = wav_file.getframerate()
                n_frames = wav_file.getnframes()

                raw_data = wav_file.readframes(n_frames)

                if sample_width == 2:
                    data = np.frombuffer(raw_data, dtype=np.int16)
                elif sample_width == 1:
                    data = np.frombuffer(raw_data, dtype=np.uint8) - 128
                elif sample_width == 4:
                    data = np.frombuffer(raw_data, dtype=np.int32)
                else:
                    raise ValueError(f"Unsupported WAV sample width: {sample_width}")

                # Normalize to [-1.0, 1.0]
                if sample_width == 2:
                    data = data.astype(np.float32) / 32768.0
                elif sample_width == 1:
                    data = data.astype(np.float32) / 128.0
                elif sample_width == 4:
                    data = data.astype(np.float32) / 2147483648.0

                # Convert stereo to mono
                if n_channels > 1:
                    data = data.reshape(-1, n_channels).mean(axis=1)

                # Resample to 16kHz if needed (Whisper expects 16kHz)
                if framerate != 16000:
                    duration = len(data) / framerate
                    target_samples = int(duration * 16000)
                    data = np.interp(
                        np.linspace(0, len(data), target_samples, endpoint=False),
                        np.arange(len(data)),
                        data,
                    ).astype(np.float32)

                return data
        except Exception as e:
            # Fallback to raw PCM 16kHz 16-bit mono
            try:
                data = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
                return data
            except Exception:
                raise ValueError(f"Failed to decode audio bytes as WAV or raw PCM: {e}")

    async def transcribe(self, request) -> Any:
        """
        Transcribe audio to text.
        Returns ASRResponse with transcript and latency.
        """
        from app.models.schemas import ASRResponse

        start_time = time.time()

        if settings.USE_MOCK_SERVICES:
            # Mock transcription behavior
            latency_ms = int((time.time() - start_time) * 1000)
            return ASRResponse(
                session_id=request.session_id,
                turn_id=request.turn_id,
                transcript="Where is the admissions office?",
                transcript_en="Where is the admissions office?",
                detected_language="en",
                confidence=0.95,
                duration_ms=3000,
                latency_ms=latency_ms,
            )

        try:
            # Decode base64 WAV/PCM bytes
            audio_bytes = base64.b64decode(request.audio_base64)
            audio_data = self._load_wav_to_numpy(audio_bytes)

            model = self._get_model()
            lang_hint = request.language_hint if request.language_hint in ["en", "kn", "hi"] else None

            # Define language-specific prompt to guide the script/spelling of Whisper
            initial_prompt = None
            if lang_hint == "kn":
                initial_prompt = "ಕನ್ನಡ"
            elif lang_hint == "hi":
                initial_prompt = "हिंदी"
            elif lang_hint == "en":
                initial_prompt = "English"

            # Transcribe audio array with VAD filtering and script prompt guidance
            segments, info = model.transcribe(
                audio_data,
                beam_size=5,
                language=lang_hint,
                initial_prompt=initial_prompt,
                vad_filter=True
            )
            transcript = "".join([segment.text for segment in segments]).strip()

            duration_ms = int(info.duration * 1000)
            latency_ms = int((time.time() - start_time) * 1000)

            # Simple translation skeleton: if English is detected, transcript_en matches transcript
            transcript_en = transcript

            return ASRResponse(
                session_id=request.session_id,
                turn_id=request.turn_id,
                transcript=transcript,
                transcript_en=transcript_en,
                detected_language=info.language,
                confidence=round(info.language_probability, 3),
                duration_ms=duration_ms,
                latency_ms=latency_ms,
            )

        except Exception as e:
            logger.exception(f"ASR Service transcription failed: {e}")
            raise


# Singleton instance
asr_service = ASRService()
