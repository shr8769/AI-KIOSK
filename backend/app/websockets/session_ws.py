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


# ── Connection Manager ────────────────────────

class ConnectionManager:
    def __init__(self):
        self.active: Dict[str, WebSocket] = {}   # session_id → WebSocket

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
                await manager.send(session_id, {
                    "type": "error",
                    "payload": {"message": "Invalid JSON"}
                })
                continue

            msg_type = msg.get("type", "unknown")
            payload = msg.get("payload", {})

            logger.debug(f"WS [{session_id}] received type={msg_type}")

            # ── Message dispatch ──────────────
            if msg_type == "ping":
                await manager.send(session_id, {"type": "pong", "payload": {}})

            elif msg_type == "audio_chunk":
                # TODO: pipe to ASRService → RIARService → RAGService → TTSService
                # For now, echo the transcript placeholder
                await manager.send(session_id, {
                    "type": "transcript",
                    "payload": {
                        "text": "[mock] Audio received, transcription pending real ASR",
                        "confidence": 0.0,
                        "final": True,
                    }
                })

            elif msg_type == "frame":
                # TODO: pipe to DetectionService
                await manager.send(session_id, {
                    "type": "detection",
                    "payload": {"person_detected": True, "confidence": 0.91}
                })

            elif msg_type == "text_query":
                # Direct text query shortcut (useful during dev)
                await manager.send(session_id, {
                    "type": "answer",
                    "payload": {
                        "text": f"[mock] You asked: {payload.get('text', '')}",
                        "sources": [],
                    }
                })

            else:
                await manager.send(session_id, {
                    "type": "error",
                    "payload": {"message": f"Unknown message type: {msg_type}"}
                })

    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception as e:
        logger.exception(f"WS error [{session_id}]: {e}")
        manager.disconnect(session_id)
