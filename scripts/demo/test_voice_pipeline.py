"""
Interactive Speech Pipeline Test Script
Owner: Harsha

Runs local mic capture, VAD, Whisper ASR (multilingual), and pyttsx3 TTS playback.
"""

import asyncio
import base64
import os
import sys
import time

# Ensure project root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../backend")))

# Force real mode (USE_MOCK_SERVICES = False)
os.environ["USE_MOCK_SERVICES"] = "False"

from backend.app.core.config import settings
settings.USE_MOCK_SERVICES = False

from backend.app.services.speech.audio_capture import audio_capture_service
from backend.app.services.speech.asr_service import asr_service
from backend.app.services.speech.tts_service import tts_service
from backend.app.models.schemas import ASRRequest


async def main():
    print("=" * 65)
    print("  VidyaSahayak Multilingual Speech Pipeline Test")
    print("=" * 65)
    
    # 0. Prompt for Whisper Model Size
    print("\nSelect Whisper Model Size:")
    print("  [1] base  (Fastest on CPU, ~140MB)")
    print("  [2] small (Better accuracy, ~460MB)")
    print("  [3] medium (Best accuracy, recommended for Kannada, ~1.5GB)")
    model_choice = input("Enter choice [1-3] (default 1): ").strip()
    
    model_size = "base"
    if model_choice == "2":
        model_size = "small"
    elif model_choice == "3":
        model_size = "medium"
        
    # Apply model size override to settings
    settings.USE_MOCK_SERVICES = False
    
    # 0b. Prompt for Language Hint
    print("\nSelect Language Hint:")
    print("  [1] Auto-Detect")
    print("  [2] English ('en')")
    print("  [3] Hindi ('hi')")
    print("  [4] Kannada ('kn')")
    lang_choice = input("Enter choice [1-4] (default 1): ").strip()
    
    lang_hint = None
    if lang_choice == "2":
        lang_hint = "en"
    elif lang_choice == "3":
        lang_hint = "hi"
    elif lang_choice == "4":
        lang_hint = "kn"

    print("\nMicrophone will activate. Speak clearly!")
    print("VAD will stop recording automatically when you pause speaking for 1.5s.")
    print("-" * 65)
    
    # Ensure static directory exists
    os.makedirs(os.path.join("backend", "static", "audio"), exist_ok=True)
    test_wav_path = os.path.join("backend", "static", "audio", "interactive_test.wav")
    
    # Override lazy-load method in ASR service to use our chosen model size
    def custom_get_model():
        if asr_service.model is None:
            print(f"Loading faster-whisper model '{model_size}' on CPU...")
            from faster_whisper import WhisperModel
            asr_service.model = WhisperModel(model_size, device="cpu", compute_type="int8")
            print(f"faster-whisper model '{model_size}' loaded.")
        return asr_service.model
        
    asr_service._get_model = custom_get_model
    
    # 1. Record until silence is detected
    success = await audio_capture_service.record_until_silence(
        output_path=test_wav_path,
        silence_threshold=0.015,
        max_duration=15.0
    )
    
    if not success:
        print("\n[Error] Did not capture audio. Check if a microphone is connected and active.")
        return
        
    print(f"\n>>> Audio recorded. Processing through local Whisper ({model_size}) ASR...")
    
    # 2. Read file and encode to base64
    with open(test_wav_path, "rb") as f:
        audio_bytes = f.read()
    audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
    
    # 3. Transcribe base64 audio
    req = ASRRequest(
        session_id="test_interactive_session",
        audio_base64=audio_base64,
        language_hint=lang_hint,
        turn_id=1
    )
    
    try:
        asr_resp = await asr_service.transcribe(req)
        
        print("\n" + "=" * 65)
        print(" ASR TRANSCRIPTION RESULTS:")
        print("=" * 65)
        print(f"  Detected Language : {asr_resp.detected_language.upper()} (probability: {asr_resp.confidence:.2f})")
        print(f"  Transcribed Text  : \"{asr_resp.transcript}\"")
        print(f"  ASR Processing    : {asr_resp.latency_ms} ms")
        print("=" * 65 + "\n")
        
        if not asr_resp.transcript.strip():
            print("ASR returned empty transcript. Try speaking louder or closer to the microphone.")
            return

        # 4. Speak transcription back to the user out loud using SAPI5
        import pyttsx3
        print(">>> Synthesizing voice feedback...")
        engine = pyttsx3.init()
        
        feedback_text = f"You said: {asr_resp.transcript}"
        print(f"TTS Playing: \"{feedback_text}\"")
        engine.say(feedback_text)
        engine.runAndWait()
        
    except Exception as e:
        print(f"\n[Error] Pipeline execution failed: {e}")
        
    finally:
        # Clean up temporary capture WAV
        if os.path.exists(test_wav_path):
            try:
                os.remove(test_wav_path)
            except Exception:
                pass


if __name__ == "__main__":
    asyncio.run(main())
