import time
import subprocess
import os
import sys

# Add project root to PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from avatar.avatar_controller import AvatarController, AvatarState
from detection.detector import DetectorStub

def main():
    print("="*50)
    print(" Week 1 Integration Demo (Architecture Validation)")
    print("="*50)
    
    # 1. Start the Avatar
    avatar = AvatarController()
    
    print("\n[Demo] Waiting for a person...")
    time.sleep(1)
    
    # 2. Simulate Detection
    detector = DetectorStub()
    
    # Press Enter or just automate it for the demo script
    print("\n>>> Simulating a person walking up to the kiosk...")
    time.sleep(1)
    
    session_id = detector.simulate_detection()
    
    if session_id:
        print("\n[Demo] Backend confirmed session. Notifying Avatar.")
        # 3. Avatar transitions
        avatar.on_person_detected()
        
        # Simulate greeting finish
        time.sleep(2)
        print("\n>>> Simulating greeting finished...")
        avatar.on_greeting_finished()
        
        # In a real flow, ASR would start now.
        print("\n[Demo] Success! The skeleton flow is functional.")
        print(f"Active Session ID: {session_id}")
        print(f"Final Avatar State: {avatar.state.value}")
    else:
        print("\n[Error] Backend API failed. Ensure 'uvicorn backend.app.main:app' is running.")

if __name__ == "__main__":
    main()
