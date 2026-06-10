import sys
import os
import logging
from typing import Callable, Optional, Dict, Any, Tuple
from ultralytics import YOLO

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../"))
from backend.app.models.shared_models import DetectionEvent, BoundingBox

logger = logging.getLogger(__name__)

class PersonDetector:
    """
    YOLO11-based person detector.
    Owner: Haseeb
    """
    
    def __init__(self, camera_id: str = "cam_front_01", model_path: str = "yolo11n.pt"):
        self.camera_id = camera_id
        # We use YOLO11 Nano for ultra-low latency real-time detection.
        logger.info(f"Loading YOLO model: {model_path}...")
        self.model = YOLO(model_path)
        logger.info("YOLO model loaded.")
        
        self._on_person_detected: Optional[Callable[[DetectionEvent], None]] = None
        self._on_person_left: Optional[Callable[[DetectionEvent], None]] = None

    def on_person_detected(self, callback: Callable[[DetectionEvent], None]):
        """Register callback for when a person is detected."""
        self._on_person_detected = callback

    def on_person_left(self, callback: Callable[[DetectionEvent], None]):
        """Register callback for when a person leaves."""
        self._on_person_left = callback
        
    def analyze_frame(self, frame) -> Optional[DetectionEvent]:
        """
        Run YOLO11 inference on a single frame.
        Filter for 'person' class (0), find the highest confidence,
        and return a DetectionEvent if found.
        """
        # Run inference on CPU (to bypass RTX 5000 series CUDA sm_120 compatibility issue)
        results = self.model(frame, verbose=False, device='cpu')
        
        best_conf = 0.0
        best_box = None
        
        for result in results:
            boxes = result.boxes
            for box in boxes:
                # Class 0 is 'person' in COCO dataset
                if int(box.cls[0].item()) == 0:
                    conf = float(box.conf[0].item())
                    if conf > best_conf:
                        best_conf = conf
                        # Get x, y, w, h
                        xywh = box.xywh[0].tolist()
                        best_box = BoundingBox(
                            x=int(xywh[0]),
                            y=int(xywh[1]),
                            w=int(xywh[2]),
                            h=int(xywh[3])
                        )
                        
        if best_box is not None:
            return DetectionEvent(
                camera_id=self.camera_id,
                confidence=best_conf,
                bounding_box=best_box
            )
            
        return None
        
    def trigger_detected(self, event: DetectionEvent):
        """Called by the PresenceMonitor to officially trigger the session."""
        if self._on_person_detected:
            self._on_person_detected(event)
            
    def trigger_left(self, event: DetectionEvent):
        """Called by the PresenceMonitor to officially end the session."""
        if self._on_person_left:
            self._on_person_left(event)
