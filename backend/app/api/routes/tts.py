from fastapi import APIRouter

router = APIRouter()

@router.post("/tts")
async def text_to_speech():
    """
    Convert text to speech audio.
    Owner: Harsha

    TODO Week 2:
    - Accept text, language, voice_id, format
    - Run TTS (Coqui / ElevenLabs / Google)
    - Save audio file, return URL
    """
    return {
        "session_id": "ses_stub",
        "audio_url": "/static/audio/stub_response.mp3",
        "duration_seconds": 5.0,
        "format": "mp3",
        "latency_ms": 340
    }
