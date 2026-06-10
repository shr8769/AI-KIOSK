import logging
from enum import Enum
import threading
import time

logger = logging.getLogger(__name__)

class AvatarState(Enum):
    IDLE = "idle"
    GREETING = "greeting"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"

class AvatarController:
    """
    State machine managing avatar behavior and animations.
    Owner: Haseeb
    
    Week 1: State machine skeleton
    Week 2: Animation integration
    """
    
    def __init__(self):
        self._state = AvatarState.IDLE
        self._lock = threading.Lock()
        logger.info("AvatarController initialized in IDLE state")
        
    @property
    def state(self) -> AvatarState:
        with self._lock:
            return self._state
            
    def _set_state(self, new_state: AvatarState):
        with self._lock:
            old_state = self._state
            self._state = new_state
            logger.info(f"Avatar state changed: {old_state.name} -> {new_state.name}")
            self._trigger_animation(new_state)
            
    def _trigger_animation(self, state: AvatarState):
        """Mock animation trigger. Will interact with frontend/MuseTalk later."""
        if state == AvatarState.IDLE:
            logger.debug("Playing idle loop animation")
        elif state == AvatarState.GREETING:
            logger.debug("Playing greeting animation")
        elif state == AvatarState.LISTENING:
            logger.debug("Playing active listening animation")
        elif state == AvatarState.PROCESSING:
            logger.debug("Playing thinking/processing animation")
        elif state == AvatarState.SPEAKING:
            logger.debug("Playing speaking animation (lip sync active)")

    # --- State Transitions ---

    def on_person_detected(self):
        """Triggered when detection module sees a person."""
        if self.state == AvatarState.IDLE:
            self._set_state(AvatarState.GREETING)
            # In a real scenario, we'd wait for the greeting animation to finish
            # before transitioning to listening.
            threading.Timer(2.0, self.on_greeting_complete).start()
            
    def on_greeting_complete(self):
        """Triggered when the greeting animation finishes."""
        if self.state == AvatarState.GREETING:
            self._set_state(AvatarState.LISTENING)
            
    def on_user_speaking_detected(self):
        """Triggered when VAD detects user starting to speak."""
        # Remain in listening, maybe change subtle animation
        if self.state in [AvatarState.LISTENING, AvatarState.IDLE]:
            self._set_state(AvatarState.LISTENING)
            
    def on_query_processing_started(self):
        """Triggered when user stops speaking and RIAR/RAG begins."""
        if self.state == AvatarState.LISTENING:
            self._set_state(AvatarState.PROCESSING)
            
    def on_response_ready(self, audio_url: str):
        """Triggered when TTS has generated the response."""
        if self.state == AvatarState.PROCESSING:
            self._set_state(AvatarState.SPEAKING)
            # Simulate speaking duration then return to listening
            threading.Timer(5.0, self.on_speaking_complete).start()
            
    def on_speaking_complete(self):
        """Triggered when TTS audio playback finishes."""
        if self.state == AvatarState.SPEAKING:
            self._set_state(AvatarState.LISTENING)
            
    def on_person_left(self):
        """Triggered when detection module reports person left."""
        self._set_state(AvatarState.IDLE)
