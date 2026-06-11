"""
WebSocket handler for /ws/session/{session_id}

Message protocol (JSON):
  Client → Server:  { "type": "ping" | "audio_chunk" | "frame", "payload": <any> }
  Server → Client:  { "type": "pong" | "transcript" | "answer" | "tts_chunk" | "error", "payload": <any> }
"""

import json
from typing import Dict

from fastapi import WebSocket, WebSocketDisconnect

from app.core.logging import logger
from app.core.session_store import get_session
from app.models.schemas import ASRRequest, RIARRequest, RouteRequest, RAGRequest, TTSRequest
from app.services.speech.asr_service import asr_service
from app.services.speech.tts_service import tts_service
from app.services.mock_services import riar_service, route_service, rag_service

# ── Connection Manager ────────────────────────


class ConnectionManager:
    def __init__(self):
        self.active: Dict[str, WebSocket] = {}  # session_id → WebSocket

    async def connect(self, session_id: str, ws: WebSocket):
        await ws.accept()
        self.active[session_id] = ws
        logger.info(f"WS connected: {session_id}  (total={len(self.active)})")

    def disconnect(self, session_id: str):
        self.active.pop(session_id, None)
        logger.info(f"WS disconnected: {session_id}  (total={len(self.active)})")

    async def send(self, session_id: str, message: dict):
        ws = self.active.get(session_id)
        if ws:
            await ws.send_json(message)

    async def broadcast(self, message: dict):
        for ws in self.active.values():
            await ws.send_json(message)


manager = ConnectionManager()


# ── Handler ───────────────────────────────────


async def websocket_session_handler(websocket: WebSocket, session_id: str):
    # Validate session exists
    session = await get_session(session_id)
    if not session:
        await websocket.accept()
        await websocket.send_json({"type": "error", "payload": {"message": "Session not found"}})
        await websocket.close(code=4004)
        return

    await manager.connect(session_id, websocket)

    try:
        while True:
            raw = await websocket.receive_text()

            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                await manager.send(
                    session_id, {"type": "error", "payload": {"message": "Invalid JSON"}}
                )
                continue

            msg_type = msg.get("type", "unknown")
            payload = msg.get("payload", {})

            logger.debug(f"WS [{session_id}] received type={msg_type}")

            # ── Message dispatch ──────────────
            if msg_type == "ping":
                await manager.send(session_id, {"type": "pong", "payload": {}})

            elif msg_type == "audio_chunk":
                audio_base64 = payload.get("audio_base64")
                if not audio_base64:
                    await manager.send(
                        session_id,
                        {"type": "error", "payload": {"message": "Missing audio_base64 payload"}},
                    )
                    continue

                turn_id = payload.get("turn_id", 1)
                language_hint = payload.get("language_hint", "en")

                # Send processing state update (thinking)
                await manager.send(session_id, {"type": "thinking", "payload": {}})

                try:
                    # 1. ASR Transcription
                    asr_req = ASRRequest(
                        session_id=session_id,
                        audio_base64=audio_base64,
                        language_hint=language_hint,
                        turn_id=turn_id,
                    )
                    asr_resp = await asr_service.transcribe(asr_req)

                    # Send transcription transcript back to client
                    await manager.send(
                        session_id,
                        {
                            "type": "transcript",
                            "payload": {
                                "text": asr_resp.transcript,
                                "confidence": asr_resp.confidence,
                                "final": True,
                            },
                        },
                    )

                    # 2. Intent Refinement & Ambiguity Classification (RIAR)
                    riar_req = RIARRequest(
                        session_id=session_id,
                        turn_id=turn_id,
                        query=asr_resp.transcript,
                        language=asr_resp.detected_language,
                        session_history=[],
                    )
                    riar_resp = await riar_service.classify(riar_req)

                    if riar_resp.requires_clarification:
                        # 3a. TTS for Clarification question
                        tts_req = TTSRequest(
                            session_id=session_id,
                            text=riar_resp.clarification_question or "Could you clarify?",
                            language=asr_resp.detected_language,
                        )
                        tts_resp = await tts_service.synthesize(tts_req)

                        # Send clarifying message to client
                        await manager.send(
                            session_id,
                            {
                                "type": "clarifying",
                                "payload": {
                                    "text": riar_resp.clarification_question,
                                    "audio_url": tts_resp.audio_url,
                                    "ambiguity_type": riar_resp.ambiguity_type,
                                },
                            },
                        )
                    else:
                        # 3b. Route query to domain agent
                        await manager.send(session_id, {"type": "retrieving", "payload": {}})
                        
                        route_req = RouteRequest(
                            session_id=session_id,
                            refined_query=riar_resp.refined_query or asr_resp.transcript,
                            domain=riar_resp.domain or "general",
                            language=asr_resp.detected_language,
                        )
                        route_resp = await route_service.route(route_req)

                        # 4b. RAG grounded answer generation
                        rag_req = RAGRequest(
                            session_id=session_id,
                            query=riar_resp.refined_query or asr_resp.transcript,
                            context=route_resp.context_window,
                            domain=riar_resp.domain or "general",
                            language=asr_resp.detected_language,
                        )
                        rag_resp = await rag_service.generate(rag_req)

                        # 5b. TTS Response audio generation
                        tts_req = TTSRequest(
                            session_id=session_id,
                            text=rag_resp.answer,
                            language=asr_resp.detected_language,
                        )
                        tts_resp = await tts_service.synthesize(tts_req)

                        # Send final answer payload to client (speaking state)
                        await manager.send(
                            session_id,
                            {
                                "type": "answer",
                                "payload": {
                                    "text": rag_resp.answer,
                                    "audio_url": tts_resp.audio_url,
                                    "sources": rag_resp.citations,
                                },
                            },
                        )

                except Exception as e:
                    logger.exception(f"Pipeline error processing audio: {e}")
                    await manager.send(
                        session_id,
                        {"type": "error", "payload": {"message": f"Pipeline processing failed: {str(e)}"}},
                    )

            elif msg_type == "frame":
                # TODO: pipe to DetectionService
                await manager.send(
                    session_id,
                    {"type": "detection", "payload": {"person_detected": True, "confidence": 0.91}},
                )

            elif msg_type == "text_query":
                # Direct text query shortcut (useful during dev)
                await manager.send(
                    session_id,
                    {
                        "type": "answer",
                        "payload": {
                            "text": f"[mock] You asked: {payload.get('text', '')}",
                            "sources": [],
                        },
                    },
                )

            else:
                await manager.send(
                    session_id,
                    {"type": "error", "payload": {"message": f"Unknown message type: {msg_type}"}},
                )

    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception as e:
        logger.exception(f"WS error [{session_id}]: {e}")
        manager.disconnect(session_id)
