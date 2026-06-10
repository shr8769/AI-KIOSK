import requests
import logging
from typing import Optional
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../"))
from backend.app.models.shared_models import DetectionEvent

logger = logging.getLogger(__name__)

class SessionTrigger:
    """
    Sends detection events to the backend to trigger session creation/closure.
    Owner: Haseeb
    """
    
    def __init__(self, backend_url: str = "http://localhost:8000"):
        self.backend_url = backend_url
        
    def trigger_session_created(self, event: DetectionEvent) -> Optional[dict]:
        """
        Send POST request to backend when a person is detected.
        Returns the session data (including greeting) if successful.
        """
        try:
            url = f"{self.backend_url}/api/v1/detect"
            response = requests.post(url, json=event.to_dict(), timeout=10.0)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Session created successfully: {data.get('session_id')}")
            return data
        except Exception as e:
            logger.error(f"Failed to trigger session creation: {e}")
            return None
            
    def trigger_session_closed(self, session_id: str) -> bool:
        """
        Send DELETE request to backend when person leaves.
        """
        try:
            url = f"{self.backend_url}/api/v1/detect/{session_id}"
            response = requests.delete(url, timeout=10.0)
            response.raise_for_status()
            logger.info(f"Session {session_id} closed successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to close session {session_id}: {e}")
            return False
