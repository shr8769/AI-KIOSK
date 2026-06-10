from dataclasses import dataclass, field
from typing import List, Optional
import time

@dataclass
class BoundingBox:
    x: int
    y: int
    w: int
    h: int

@dataclass
class PersonDetectedEvent:
    camera_id: str
    confidence: float
    bounding_box: BoundingBox
    timestamp: float = field(default_factory=time.time)
    frame_width: int = 1920
    frame_height: int = 1080

    def to_dict(self):
        return {
            "camera_id": self.camera_id,
            "confidence": self.confidence,
            "bounding_box": {
                "x": self.bounding_box.x,
                "y": self.bounding_box.y,
                "w": self.bounding_box.w,
                "h": self.bounding_box.h
            },
            "frame_width": self.frame_width,
            "frame_height": self.frame_height
        }
