import sys
import os
import time
import logging

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from detection.detector import PersonDetector
from detection.presence_monitor import PresenceMonitor
from detection.event_publisher import EventPublisher
from backend.app.models.shared_models import DetectionEvent

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("Initializing Edge Sensor Microservice...")
    
    # 1. Initialize Network Layer
    # Use environment variable for backend URL, default to local
    backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
    publisher = EventPublisher(backend_url=backend_url)
    
    # 2. Initialize Computer Vision Layer
    # The detector is completely decoupled from API logic
    detector = PersonDetector(model_path="yolo11n.pt")
    
    # Wire the detector's callbacks to the event publisher
    def on_detected(event: DetectionEvent):
        logger.info("Detector fired PERSON_DETECTED. Publishing to backend...")
        publisher.publish_person_detected(
            camera_id=event.camera_id,
            confidence=event.confidence,
            box=event.bounding_box
        )
        
    def on_left(event: DetectionEvent):
        logger.info("Detector fired PERSON_LEFT. Publishing to backend...")
        publisher.publish_person_left(camera_id=event.camera_id)

    detector.on_person_detected(on_detected)
    detector.on_person_left(on_left)
    
    # 3. Initialize Temporal Monitor (Hardware layer)
    monitor = PresenceMonitor(detector)
    # Production is headless by default
    monitor.debug = os.getenv("VISION_DEBUG", "0") == "1"
    
    logger.info("Starting presence monitoring loop...")
    monitor.start()
    
    try:
        # Keep main thread alive and emit periodic heartbeats
        while monitor._running:
            time.sleep(30)
            publisher.publish_heartbeat(camera_id=detector.camera_id)
            
    except KeyboardInterrupt:
        logger.info("Interrupted by system or user. Shutting down...")
    finally:
        monitor.stop()
        logger.info("Edge Sensor Offline.")

if __name__ == "__main__":
    main()
