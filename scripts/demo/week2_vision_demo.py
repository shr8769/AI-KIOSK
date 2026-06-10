import sys
import os
import time
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../"))
from detection.detector import PersonDetector
from detection.presence_monitor import PresenceMonitor
from backend.app.models.shared_models import DetectionEvent

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("Initializing YOLO11 Person Detector (yolo11n.pt)...")
    # Make sure we use the correct model requested
    detector = PersonDetector(model_path="yolo11n.pt")
    
    def on_detected(event: DetectionEvent):
        logger.info(f">>> SESSION STARTED: Person detected with confidence {event.confidence:.2f}")
        logger.info(f"    Bounding Box: {event.bounding_box}")
        
    def on_left(event: DetectionEvent):
        logger.info(f">>> SESSION ENDED: Person left frame for >5.0 seconds")

    detector.on_person_detected(on_detected)
    detector.on_person_left(on_left)
    
    monitor = PresenceMonitor(detector)
    # Enable debug mode to display the OpenCV window
    monitor.debug = True
    
    logger.info("Starting live camera feed. Press 'q' in the video window to quit.")
    monitor.start()
    
    try:
        while monitor._running:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Interrupted by user.")
        monitor.stop()

if __name__ == "__main__":
    main()
