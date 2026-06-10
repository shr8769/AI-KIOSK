import sys
import os
import logging
from typing import Callable, Optional
import time
import threading

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../"))
from backend.app.models.shared_models import DetectionEvent, BoundingBox

logger = logging.getLogger(__name__)

class PersonDetector:
    """
    Stub for the person detector.
    Owner: Haseeb

    In Week 2, this will use OpenCV and YOLOv8 to detect persons.
    Currently, this acts as a stub that can be triggered manually or via a timer.
    """
    
    def __init__(self, camera_id: str = "cam_front_01"):
        self.camera_id = camera_id
        self._on_person_detected: Optional[Callable[[DetectionEvent], None]] = None
        self._on_person_left: Optional[Callable[[DetectionEvent], None]] = None
        self._running = False
        
    def start_monitoring(self):
        """Start monitoring camera feed for persons."""
        self._running = True
        logger.info(f"Detector [{self.camera_id}]: Monitoring started.")
        # Stub: just a mock background loop that does nothing for now
        threading.Thread(target=self._mock_loop, daemon=True).start()
        
    def stop_monitoring(self):
        """Stop monitoring."""
        self._running = False
        logger.info(f"Detector [{self.camera_id}]: Monitoring stopped.")

    def on_person_detected(self, callback: Callable[[DetectionEvent], None]):
        """Register callback for when a person is detected."""
        self._on_person_detected = callback

    def on_person_left(self, callback: Callable[[DetectionEvent], None]):
        """Register callback for when a person leaves."""
        self._on_person_left = callback
        
    def _mock_loop(self):
        """Mock background loop for testing before OpenCV integration."""
        while self._running:
            time.sleep(1)
            
    def trigger_mock_detection(self):
        """Manually trigger a detection event for testing."""
        if self._on_person_detected:
            event = DetectionEvent(
                camera_id=self.camera_id,
                confidence=0.98,
                bounding_box=BoundingBox(x=100, y=100, w=250, h=500)
            )
            logger.info(f"Detector [{self.camera_id}]: Mock person detected!")
            self._on_person_detected(event)
            
    def trigger_mock_left(self):
        """Manually trigger a person left event for testing."""
        if self._on_person_left:
            event = DetectionEvent(
                camera_id=self.camera_id,
                confidence=0.0,
                bounding_box=BoundingBox(x=0, y=0, w=0, h=0)
            )
            logger.info(f"Detector [{self.camera_id}]: Mock person left!")
            self._on_person_left(event)
