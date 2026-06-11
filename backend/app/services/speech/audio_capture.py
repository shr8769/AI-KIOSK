"""
Audio Capture Service — Handles local microphone input and Voice Activity Detection (VAD).
Owner: Harsha
"""

import asyncio
import logging
import os
import time
import wave
import numpy as np

logger = logging.getLogger(__name__)


class AudioCaptureService:
    def __init__(
        self,
        sample_rate: int = 16000,
        channels: int = 1,
        chunk_duration_ms: int = 30,
        silence_duration_seconds: float = 1.5,
    ):
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = int(sample_rate * chunk_duration_ms / 1000)
        self.silence_duration_seconds = silence_duration_seconds

    async def record_until_silence(
        self,
        output_path: str,
        silence_threshold: float = 0.015,
        max_duration: float = 15.0,
    ) -> bool:
        """
        Record audio from the default microphone until silence is detected
        or max_duration is reached. Saves the audio as a 16kHz 16-bit mono WAV.
        
        Gracefully handles environments without a microphone.
        """
        try:
            import sounddevice as sd
        except Exception as e:
            logger.warning(f"sounddevice not imported (expected in mock mode): {e}")
            # Simulate wait to represent speaking
            await asyncio.sleep(2.0)
            return False

        all_frames = []
        silence_limit = int(self.silence_duration_seconds * self.sample_rate / self.chunk_size)
        silence_counter = 0
        speech_detected = False
        speech_counter = 0
        speech_trigger_limit = 5  # ~150ms of consecutive speech to trigger active state

        start_time = time.time()

        def callback(indata, frames, time_info, status):
            if status:
                logger.warning(f"Sounddevice callback status: {status}")
            all_frames.append(indata.copy())

        try:
            # Query standard audio input device first
            devices = sd.query_devices()
            input_device_exists = False
            for d in devices:
                if d.get("max_input_channels", 0) > 0:
                    input_device_exists = True
                    break
            
            if not input_device_exists:
                logger.warning("No microphone input device detected. Skipping physical recording.")
                # Wait representing conversation turn in mock mode
                await asyncio.sleep(2.0)
                return False

            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype="int16",
                blocksize=self.chunk_size,
                callback=callback,
            ):
                logger.info("Microphone active. Listening...")

                while time.time() - start_time < max_duration:
                    await asyncio.sleep(0.05)

                    if len(all_frames) > 0:
                        latest_frame = all_frames[-1]
                        latest_float = latest_frame.astype(np.float32) / 32768.0
                        rms = np.sqrt(np.mean(latest_float**2))

                        if rms > silence_threshold:
                            silence_counter = 0
                            if not speech_detected:
                                speech_counter += 1
                                if speech_counter >= speech_trigger_limit:
                                    speech_detected = True
                                    logger.info("VAD: Speech started.")
                        else:
                            if speech_detected:
                                silence_counter += 1
                                if silence_counter >= silence_limit:
                                    logger.info("VAD: End of speech detected (silence limit).")
                                    break
                            else:
                                speech_counter = max(0, speech_counter - 1)

            if all_frames:
                # Compile and write audio frames to disk
                recording_data = np.concatenate(all_frames, axis=0)
                os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
                
                with wave.open(output_path, "wb") as wf:
                    wf.setnchannels(self.channels)
                    wf.setsampwidth(2)  # 16-bit
                    wf.setframerate(self.sample_rate)
                    wf.writeframes(recording_data.tobytes())

                logger.info(f"Recorded audio saved to: {output_path} ({len(recording_data)/self.sample_rate:.2f}s)")
                return True

            return False

        except Exception as e:
            logger.warning(f"Could not open input audio stream: {e}. Skipping recording.")
            await asyncio.sleep(2.0)
            return False


# Singleton instance
audio_capture_service = AudioCaptureService()
