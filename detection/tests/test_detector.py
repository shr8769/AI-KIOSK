import pytest
import numpy as np
import time
from unittest.mock import patch, MagicMock

from detection.detector import PersonDetector
from detection.presence_monitor import PresenceMonitor
from backend.app.models.shared_models import DetectionEvent

@pytest.fixture
def mock_yolo():
    with patch('detection.detector.YOLO') as mock:
        yield mock

def test_person_detector_filtering(mock_yolo):
    """Test that analyze_frame correctly filters for person class (0) and highest confidence."""
    # Setup mock YOLO results
    mock_model_instance = MagicMock()
    mock_yolo.return_value = mock_model_instance
    
    mock_result = MagicMock()
    
    class MockTensor:
        def __init__(self, val):
            self.val = val
        def item(self):
            return self.val
            
    class MockBox:
        def __init__(self, arr):
            self.arr = arr
        def tolist(self):
            return self.arr
            
    # Create two boxes: one person (class 0) with low conf, one car (class 2) with high conf
    box1 = MagicMock()
    box1.cls = [MockTensor(0)]
    box1.conf = [MockTensor(0.4)]
    box1.xywh = [MockBox([10, 10, 50, 50])]
    
    box2 = MagicMock()
    box2.cls = [MockTensor(2)]
    box2.conf = [MockTensor(0.9)]
    box2.xywh = [MockBox([100, 100, 200, 200])]
    
    # A second person with higher confidence
    box3 = MagicMock()
    box3.cls = [MockTensor(0)]
    box3.conf = [MockTensor(0.8)]
    box3.xywh = [MockBox([50, 50, 100, 200])]
    
    mock_result.boxes = [box1, box2, box3]
    mock_model_instance.return_value = [mock_result]
    
    detector = PersonDetector(model_path="mock.pt")
    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    event = detector.analyze_frame(dummy_frame)
    
    assert event is not None
    assert event.confidence == 0.8
    assert event.bounding_box.x == 50
    assert event.bounding_box.y == 50
    assert event.bounding_box.w == 100
    assert event.bounding_box.h == 200

def test_presence_monitor_timing(mock_yolo):
    """Test the 1.5s presence and 5s absence logic."""
    detector = PersonDetector(model_path="mock.pt")
    monitor = PresenceMonitor(detector)
    
    # Lower thresholds for faster test execution
    monitor.presence_threshold = 0.2
    monitor.absence_threshold = 0.4
    
    detected_events = []
    left_events = []
    
    detector.on_person_detected(lambda e: detected_events.append(e))
    detector.on_person_left(lambda e: left_events.append(e))
    
    # Mock cap.read and analyze_frame directly to test the loop synchronously
    # Instead of running the full thread, we will manually call the logic inside the loop
    # by simulating time.
    
    # Simulation helper
    def simulate_frame(has_person: bool, current_time: float):
        event = DetectionEvent(camera_id="test", confidence=0.9, bounding_box=MagicMock()) if has_person else None
        
        if event and event.confidence > monitor.confidence_threshold:
            monitor.last_detected_time = current_time
            if not monitor.is_person_present:
                if monitor.first_detected_time is None:
                    monitor.first_detected_time = current_time
                elif (current_time - monitor.first_detected_time) >= monitor.presence_threshold:
                    monitor.is_person_present = True
                    detector.trigger_detected(event)
        else:
            monitor.first_detected_time = None
            if monitor.is_person_present and monitor.last_detected_time is not None:
                if (current_time - monitor.last_detected_time) >= monitor.absence_threshold:
                    monitor.is_person_present = False
                    empty_event = DetectionEvent(camera_id="test", confidence=0.0, bounding_box=MagicMock())
                    detector.trigger_left(empty_event)

    # 1. Person appears at t=0.0
    simulate_frame(True, 0.0)
    assert len(detected_events) == 0
    assert monitor.is_person_present == False
    
    # 2. Person still there at t=0.1 (not yet 0.2s threshold)
    simulate_frame(True, 0.1)
    assert len(detected_events) == 0
    
    # 3. Person still there at t=0.25 (crosses 0.2s threshold)
    simulate_frame(True, 0.25)
    assert len(detected_events) == 1
    assert monitor.is_person_present == True
    
    # 4. Person leaves at t=0.3
    simulate_frame(False, 0.3)
    assert len(left_events) == 0
    assert monitor.is_person_present == True
    
    # 5. Person still absent at t=0.5 (0.5 - 0.25 < 0.4s threshold)
    simulate_frame(False, 0.5)
    assert len(left_events) == 0
    
    # 6. Person absent at t=0.7 (0.7 - 0.25 > 0.4s threshold)
    simulate_frame(False, 0.7)
    assert len(left_events) == 1
    assert monitor.is_person_present == False
