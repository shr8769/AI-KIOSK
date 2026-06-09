# API_CONTRACT.md
## VidyaSahayak — API Contract Specification
**Version:** 1.0 | **Date:** June 2026 | **Owner:** Harsha (Engineering Lead)

> **This document is the single source of truth for all inter-module API contracts.**
> Any changes to these contracts require approval from Harsha (Engineering Lead) and must be versioned.

---

## Base URL

```
http://localhost:8000/api/v1
```

All requests must include:
```
Content-Type: application/json
X-Session-ID: <session_id>   # Required for all stateful endpoints
```

---

## Shared Data Models

### SessionObject (Canonical)

```json
{
  "session_id": "ses_abc123xyz",
  "created_at": "2026-06-09T10:30:00Z",
  "updated_at": "2026-06-09T10:30:45Z",
  "status": "active",

  "person_detection": {
    "detected": true,
    "confidence": 0.94,
    "first_detected_at": "2026-06-09T10:30:00Z",
    "bounding_box": { "x": 120, "y": 80, "w": 200, "h": 400 },
    "camera_id": "cam_front_01"
  },

  "language": {
    "detected": "kn",
    "preferred": "kn",
    "supported": ["en", "kn", "hi"]
  },

  "turns": [
    {
      "turn_id": 1,
      "role": "user",
      "raw_audio_path": "sessions/ses_abc123xyz/turn_1_audio.wav",
      "transcript": "ನಮ್ಮ ಕಾಲೇಜಿನಲ್ಲಿ ಪ್ರವೇಶ ಹೇಗೆ ಪಡೆಯುವುದು?",
      "transcript_en": "How to get admission in our college?",
      "timestamp": "2026-06-09T10:30:05Z"
    },
    {
      "turn_id": 2,
      "role": "assistant",
      "text": "PES University admissions are...",
      "audio_path": "sessions/ses_abc123xyz/turn_2_response.mp3",
      "timestamp": "2026-06-09T10:30:12Z"
    }
  ],

  "riar": {
    "original_query": "How to get admission in our college?",
    "probe_chunks_retrieved": 10,
    "ambiguity_score": 0.72,
    "ambiguity_detected": true,
    "ambiguity_type": "CONTEXTUAL",
    "clarification_question": "Are you asking about undergraduate (B.Tech) or postgraduate (M.Tech) admissions?",
    "user_clarification": "B.Tech admissions",
    "refined_query": "How to get B.Tech undergraduate admission at PES University?",
    "domain": "admissions",
    "domains_considered": ["admissions", "academics"],
    "routing_confidence": 0.91
  },

  "rag": {
    "retrieved_chunks": [
      {
        "chunk_id": "adm_chunk_042",
        "source": "admissions/ug_process_2025.pdf",
        "page": 3,
        "text": "B.Tech admissions at PES University are based on PESSAT scores...",
        "relevance_score": 0.87
      }
    ],
    "answer": "B.Tech admissions at PES University are conducted through PESSAT (PES Scholastic Aptitude Test). You need to...",
    "answer_language": "kn",
    "citations": ["admissions/ug_process_2025.pdf:p3", "admissions/eligibility_2025.pdf:p1"],
    "generation_model": "gpt-4o",
    "tokens_used": 847
  },

  "avatar": {
    "state": "speaking",
    "current_animation": "speaking_base.mp4",
    "lip_sync_active": true
  },

  "metrics": {
    "asr_latency_ms": 480,
    "riar_latency_ms": 310,
    "rag_latency_ms": 1200,
    "tts_latency_ms": 340,
    "total_latency_ms": 2330
  }
}
```

---

## Endpoint Reference

---

### POST /detect

**Purpose:** Receive a person detection event from the detection module.
**Owner:** Harsha (receives) / Haseeb (sends)
**Called by:** `detection/session_trigger.py`

#### Request

```json
{
  "camera_id": "cam_front_01",
  "confidence": 0.94,
  "bounding_box": {
    "x": 120,
    "y": 80,
    "w": 200,
    "h": 400
  },
  "detected_at": "2026-06-09T10:30:00Z",
  "frame_width": 1920,
  "frame_height": 1080
}
```

#### Response `200 OK`

```json
{
  "session_id": "ses_abc123xyz",
  "action": "session_created",
  "greeting_text": "Hello! Welcome to PES University. How can I help you today?",
  "greeting_audio_url": "/static/audio/greeting_en.mp3",
  "language_prompt": "Please speak in English, Kannada, or Hindi."
}
```

#### Response `409 Conflict` (Session already active)

```json
{
  "error": "session_already_active",
  "existing_session_id": "ses_xyz789"
}
```

---

### DELETE /detect/{session_id}

**Purpose:** Notify backend that person has left. Triggers session close.
**Owner:** Harsha / Haseeb

#### Response `200 OK`

```json
{
  "session_id": "ses_abc123xyz",
  "action": "session_closed",
  "duration_seconds": 142,
  "turns_completed": 3
}
```

---

### POST /asr

**Purpose:** Transcribe audio to text.
**Owner:** Harsha
**Called by:** Frontend WebSocket handler or detection pipeline

#### Request (multipart/form-data)

```
audio_file: <WAV binary>
session_id: "ses_abc123xyz"
language_hint: "kn"          # optional, auto-detected if omitted
turn_id: 1
```

#### Response `200 OK`

```json
{
  "session_id": "ses_abc123xyz",
  "turn_id": 1,
  "transcript": "ನಮ್ಮ ಕಾಲೇಜಿನಲ್ಲಿ ಪ್ರವೇಶ ಹೇಗೆ ಪಡೆಯುವುದು?",
  "transcript_en": "How to get admission in our college?",
  "detected_language": "kn",
  "confidence": 0.91,
  "duration_ms": 3200,
  "latency_ms": 480
}
```

#### Response `422 Unprocessable`

```json
{
  "error": "audio_too_short",
  "min_duration_ms": 500,
  "received_duration_ms": 210
}
```

---

### POST /riar

**Purpose:** Run RIAR pipeline on a transcript.
**Owner:** Haseeb (logic) / Harsha (endpoint)
**Called by:** Backend session handler after ASR

#### Request

```json
{
  "session_id": "ses_abc123xyz",
  "turn_id": 1,
  "query": "How to get admission in our college?",
  "language": "kn",
  "session_history": [
    {
      "turn_id": 0,
      "role": "user",
      "text": "Hello"
    }
  ]
}
```

#### Response `200 OK` — CLEAR query

```json
{
  "session_id": "ses_abc123xyz",
  "ambiguity_detected": false,
  "ambiguity_score": 0.18,
  "ambiguity_type": "CLEAR",
  "refined_query": "How to get admission in our college?",
  "domain": "admissions",
  "routing_confidence": 0.95,
  "requires_clarification": false
}
```

#### Response `200 OK` — AMBIGUOUS query

```json
{
  "session_id": "ses_abc123xyz",
  "ambiguity_detected": true,
  "ambiguity_score": 0.72,
  "ambiguity_type": "CONTEXTUAL",
  "clarification_question": "Are you asking about B.Tech or M.Tech admissions?",
  "clarification_audio_url": "/api/v1/tts/inline?text=...",
  "requires_clarification": true,
  "domain": null,
  "probe_chunks": [
    {
      "chunk_id": "adm_042",
      "text": "...",
      "score": 0.71
    }
  ]
}
```

---

### POST /riar/clarify

**Purpose:** Submit user's clarification response and get refined query.
**Owner:** Haseeb / Harsha

#### Request

```json
{
  "session_id": "ses_abc123xyz",
  "turn_id": 2,
  "clarification_response": "B.Tech admissions",
  "original_query": "How to get admission in our college?",
  "ambiguity_type": "CONTEXTUAL"
}
```

#### Response `200 OK`

```json
{
  "session_id": "ses_abc123xyz",
  "refined_query": "How to get B.Tech undergraduate admission at PES University?",
  "domain": "admissions",
  "routing_confidence": 0.91,
  "ready_for_rag": true
}
```

---

### POST /route

**Purpose:** Route refined query to appropriate domain agent.
**Owner:** Harsha (coordinator)

#### Request

```json
{
  "session_id": "ses_abc123xyz",
  "refined_query": "How to get B.Tech undergraduate admission at PES University?",
  "domain": "admissions",
  "language": "kn",
  "top_k": 5
}
```

#### Response `200 OK`

```json
{
  "session_id": "ses_abc123xyz",
  "agent": "AdmissionsAgent",
  "domain": "admissions",
  "retrieved_chunks": [
    {
      "chunk_id": "adm_chunk_042",
      "source": "admissions/ug_process_2025.pdf",
      "page": 3,
      "text": "B.Tech admissions at PES University are based on PESSAT scores...",
      "relevance_score": 0.87
    }
  ],
  "context_window": "B.Tech admissions at PES University are based on PESSAT...\n\nEligibility: 10+2 with PCM...",
  "retrieval_latency_ms": 210
}
```

---

### POST /rag

**Purpose:** Generate grounded answer from retrieved context.
**Owner:** Harsha (endpoint) / Gowtham (domain agent logic)

#### Request

```json
{
  "session_id": "ses_abc123xyz",
  "query": "How to get B.Tech undergraduate admission at PES University?",
  "context": "B.Tech admissions at PES University are based on PESSAT scores...",
  "domain": "admissions",
  "language": "kn",
  "max_tokens": 500,
  "citations_required": true
}
```

#### Response `200 OK`

```json
{
  "session_id": "ses_abc123xyz",
  "answer": "PES University B.Tech ಪ್ರವೇಶಕ್ಕೆ, ನೀವು PESSAT ಪರೀಕ್ಷೆಯಲ್ಲಿ ಭಾಗವಹಿಸಬೇಕು...",
  "answer_en": "For PES University B.Tech admission, you need to appear for PESSAT...",
  "citations": [
    "admissions/ug_process_2025.pdf:p3",
    "admissions/eligibility_2025.pdf:p1"
  ],
  "model_used": "gpt-4o",
  "tokens_used": 847,
  "generation_latency_ms": 1200,
  "confidence_score": 0.88
}
```

---

### POST /tts

**Purpose:** Convert text to speech audio.
**Owner:** Harsha

#### Request

```json
{
  "session_id": "ses_abc123xyz",
  "text": "PES University B.Tech ಪ್ರವೇಶಕ್ಕೆ, ನೀವು PESSAT ಪರೀಕ್ಷೆಯಲ್ಲಿ ಭಾಗವಹಿಸಬೇಕು...",
  "language": "kn",
  "voice_id": "kn_female_01",
  "speed": 1.0,
  "format": "mp3"
}
```

#### Response `200 OK`

```json
{
  "session_id": "ses_abc123xyz",
  "audio_url": "/static/sessions/ses_abc123xyz/response_turn2.mp3",
  "duration_seconds": 8.4,
  "format": "mp3",
  "latency_ms": 340
}
```

---

### POST /session/{session_id}/history

**Purpose:** Retrieve session turn history for context window.
**Owner:** Harsha

#### Response `200 OK`

```json
{
  "session_id": "ses_abc123xyz",
  "turns": [...],
  "total_turns": 4,
  "session_duration_seconds": 142
}
```

---

## WebSocket Endpoints

### WS /ws/session/{session_id}

**Purpose:** Real-time bidirectional communication between frontend and backend.
**Owner:** Harsha

**Message Types (Client → Server):**

```json
{ "type": "audio_chunk", "data": "<base64_audio>", "sequence": 1 }
{ "type": "audio_end" }
{ "type": "user_text", "text": "..." }
{ "type": "ping" }
```

**Message Types (Server → Client):**

```json
{ "type": "session_created", "session_id": "ses_abc123xyz" }
{ "type": "transcription", "text": "...", "language": "kn" }
{ "type": "clarification_required", "question": "...", "audio_url": "..." }
{ "type": "answer_ready", "text": "...", "audio_url": "...", "citations": [] }
{ "type": "avatar_state", "state": "speaking" }
{ "type": "error", "code": "asr_failed", "message": "..." }
{ "type": "session_closed" }
{ "type": "pong" }
```

---

## Error Codes Reference

| Code | HTTP Status | Description |
|---|---|---|
| `session_not_found` | 404 | Session ID does not exist |
| `session_already_active` | 409 | Duplicate session creation |
| `audio_too_short` | 422 | Audio below minimum duration |
| `language_not_supported` | 400 | Language code not in [en, kn, hi] |
| `asr_failed` | 500 | Whisper model error |
| `retrieval_failed` | 500 | Vector store query failed |
| `llm_unavailable` | 503 | LLM API not reachable |
| `tts_failed` | 500 | TTS generation error |
| `domain_not_found` | 404 | No agent for specified domain |
| `riar_timeout` | 504 | RIAR pipeline exceeded 2s limit |

---

## Versioning Policy

- All endpoints are versioned under `/api/v1/`
- Breaking changes increment the major version: `/api/v2/`
- Non-breaking additions do not change the version
- Deprecated endpoints must be marked with `X-Deprecated: true` header for one sprint before removal
- **All schema changes must be announced in the Monday standup before merging**
