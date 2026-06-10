import requests
import logging
from typing import Optional, Dict, Any
from datetime import datetime
import time

logger = logging.getLogger(__name__)

class EventPublisher:
    """
    Stateless event publisher for the edge sensor.
    Fires off JSON telemetry events to the backend's unified /events endpoint.
    Implements robust retry logic in case the backend is down.
    """
    
    def __init__(self, backend_url: str = "http://localhost:8000"):
        self.events_url = f"{backend_url}/api/v1/events"
        self.max_retries = 3
        
    def _post_with_retry(self, payload: dict) -> Optional[dict]:
        """Fire and forget with exponential backoff."""
        for attempt in range(1, self.max_retries + 1):
            try:
                # Add timestamp if missing
                if "timestamp" not in payload:
                    payload["timestamp"] = datetime.utcnow().isoformat()
                    
                response = requests.post(self.events_url, json=payload, timeout=5.0)
                response.raise_for_status()
                data = response.json()
                logger.debug(f"Event published successfully: {data.get('action_taken')}")
                return data
            except requests.exceptions.RequestException as e:
                logger.warning(f"Failed to publish event (attempt {attempt}/{self.max_retries}): {e}")
                if attempt < self.max_retries:
                    time.sleep(2 ** attempt) # Exponential backoff: 2s, 4s, 8s
        
        logger.error(f"Event dropped after {self.max_retries} attempts.")
        return None

    def publish_person_detected(self, camera_id: str, confidence: float, box: Any) -> None:
        """Publishes PERSON_DETECTED event."""
        payload = {
            "event_type": "PERSON_DETECTED",
            "camera_id": camera_id,
            "payload": {
                "confidence": confidence,
                "bounding_box": {
                    "x": box.x, "y": box.y, "w": box.w, "h": box.h
                }
            }
        }
        self._post_with_retry(payload)

    def publish_person_left(self, camera_id: str) -> None:
        """Publishes PERSON_LEFT event."""
        payload = {
            "event_type": "PERSON_LEFT",
            "camera_id": camera_id,
            "payload": {}
        }
        self._post_with_retry(payload)
        
    def publish_heartbeat(self, camera_id: str, status: str = "online") -> None:
        """Publishes HEARTBEAT event."""
        payload = {
            "event_type": "HEARTBEAT",
            "camera_id": camera_id,
            "payload": {"status": status}
        }
        self._post_with_retry(payload)
