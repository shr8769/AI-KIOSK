import os
import sys
import subprocess

def main():
    print("==================================================")
    print(" Running Week 2 Vision Demo (Event-Driven Mode)")
    print("==================================================")
    print("This will launch the production Edge Sensor Microservice")
    print("with the OpenCV debug window enabled.")
    print("")
    
    # Set the environment variable to enable debug window
    env = os.environ.copy()
    env["VISION_DEBUG"] = "1"
    
    # Get the path to detection/main.py relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, "../../"))
    main_py_path = os.path.join(project_root, "detection", "main.py")
    
    try:
        subprocess.run([sys.executable, main_py_path], env=env)
    except KeyboardInterrupt:
        print("\nDemo terminated.")

if __name__ == "__main__":
    main()
