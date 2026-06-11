import cv2
import time
import threading
import logging
import os
from typing import Optional

from detection.detector import PersonDetector
from backend.app.models.shared_models import DetectionEvent, BoundingBox

logger = logging.getLogger(__name__)

class PresenceMonitor:
    """
    Monitors the camera feed in a background thread, using PersonDetector 
    to analyze frames. Applies temporal logic to prevent false positives.
    """
    def __init__(self, detector: PersonDetector):
        self.detector = detector
        
        # Load configurable camera index
        camera_idx_str = os.getenv("CAMERA_INDEX", "0")
        try:
            self.camera_index = int(camera_idx_str)
        except ValueError:
            self.camera_index = camera_idx_str # Could be a video file or stream URL
            
        self.presence_threshold = 0.5  # seconds
        self.absence_threshold = 3.0   # seconds
        self.confidence_threshold = 0.5
        
        self._running = False
        self._thread: Optional[threading.Thread] = None
        
        self.is_person_present = False
        
        # Timing state
        self.first_detected_time: Optional[float] = None
        self.last_detected_time: Optional[float] = None
        
        self.debug = False
        
    def start(self):
        """Start the background monitoring thread."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
        logger.info(f"PresenceMonitor started on camera {self.camera_index}.")
        
    def stop(self):
        """Stop the background monitoring thread."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
        logger.info("PresenceMonitor stopped.")

    def _monitor_loop(self):
        cap = cv2.VideoCapture(self.camera_index)
        
        if not cap.isOpened():
            logger.error(f"Failed to open camera {self.camera_index}")
            self._running = False
            return
            
        logger.info("Camera feed opened successfully.")
        
        while self._running:
            ret, frame = cap.read()
            if not ret:
                logger.warning("Failed to read frame from camera. Retrying in 1s...")
                time.sleep(1)
                continue
                
            # Use detector to analyze the frame
            event = self.detector.analyze_frame(frame)
            current_time = time.time()
            
            if event and event.confidence > self.confidence_threshold:
                # Valid person detected
                self.last_detected_time = current_time
                
                if not self.is_person_present:
                    if self.first_detected_time is None:
                        self.first_detected_time = current_time
                    elif (current_time - self.first_detected_time) >= self.presence_threshold:
                        # Person has been present long enough!
                        self.is_person_present = True
                        logger.info("Person presence confirmed! Triggering start event.")
                        self.detector.trigger_detected(event)
            else:
                # No valid person detected in this frame
                self.first_detected_time = None
                
                if self.is_person_present and self.last_detected_time is not None:
                    if (current_time - self.last_detected_time) >= self.absence_threshold:
                        # Person has been absent long enough!
                        self.is_person_present = False
                        logger.info("Person absence confirmed! Triggering left event.")
                        empty_event = DetectionEvent(
                            camera_id=self.detector.camera_id,
                            confidence=0.0,
                            bounding_box=BoundingBox(x=0, y=0, w=0, h=0)
                        )
                        self.detector.trigger_left(empty_event)
                        
            if self.debug:
                # Draw bounding box if person detected
                if event and event.confidence > self.confidence_threshold:
                    box = event.bounding_box
                    cv2.rectangle(frame, (box.x - int(box.w/2), box.y - int(box.h/2)), 
                                  (box.x + int(box.w/2), box.y + int(box.h/2)), (0, 255, 0), 2)
                    cv2.putText(frame, f"Conf: {event.confidence:.2f}", (box.x - int(box.w/2), box.y - int(box.h/2) - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                # Show presence status
                status = "PRESENT" if self.is_person_present else "ABSENT"
                color = (0, 255, 0) if self.is_person_present else (0, 0, 255)
                cv2.putText(frame, f"State: {status}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 2)
                
                cv2.imshow(f"VidyaSahayak - Camera {self.camera_index}", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    self._running = False
                        
            # Sleep slightly to prevent 100% CPU usage if camera reads are instantly returning
            # (Usually cap.read() blocks for ~30ms at 30fps, but just in case)
            time.sleep(0.01)
            
        cap.release()
        if self.debug:
            cv2.destroyAllWindows()
        logger.info("Camera feed released.")
