"""
Camera Detection and Configuration Tool for AzimuthControl

This tool helps detect available cameras and test camera configuration.
"""

import cv2
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core.config_manager import get_system_config


def detect_available_cameras():
    """Detect all available cameras on the system."""
    print("=== Available Cameras ===")
    available_cameras = []
    
    for i in range(10):  # Check first 10 camera indices
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                height, width = frame.shape[:2]
                available_cameras.append({
                    'index': i,
                    'resolution': f"{width}x{height}",
                    'working': True
                })
                print(f"✅ Camera {i}: Available ({width}x{height})")
            else:
                print(f"⚠️  Camera {i}: Detected but no frame")
        else:
            print(f"❌ Camera {i}: Not available")
        cap.release()
    
    return available_cameras


def show_current_config():
    """Show current camera configuration."""
    print("\n=== Current Configuration ===")
    config = get_system_config()
    
    camera_index = config.get('camera_index', 0)
    window_width = config.get('window_width', 1280)
    window_height = config.get('window_height', 720)
    
    print(f"Configured Camera: {camera_index}")
    print(f"Configured Resolution: {window_width}x{window_height}")
    
    # Test the configured camera
    print(f"\n=== Testing Configured Camera {camera_index} ===")
    cap = cv2.VideoCapture(camera_index)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret and frame is not None:
            height, width = frame.shape[:2]
            print(f"✅ Camera {camera_index} working: {width}x{height}")
            
            # Test if we can set the desired resolution
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, window_width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, window_height)
            
            actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            if actual_width == window_width and actual_height == window_height:
                print(f"✅ Resolution set successfully: {actual_width}x{actual_height}")
            else:
                print(f"⚠️  Resolution mismatch - Requested: {window_width}x{window_height}, Got: {actual_width}x{actual_height}")
        else:
            print(f"❌ Camera {camera_index} detected but no frame available")
    else:
        print(f"❌ Camera {camera_index} not available")
    
    cap.release()


def recommend_settings(available_cameras):
    """Recommend optimal camera settings."""
    print("\n=== Recommendations ===")
    
    if not available_cameras:
        print("❌ No cameras detected - check hardware connections")
        return
    
    # Find best camera (highest resolution working camera)
    best_camera = max(available_cameras, key=lambda c: int(c['resolution'].split('x')[0]))
    
    print(f"🎯 Recommended camera: {best_camera['index']}")
    print(f"   Resolution: {best_camera['resolution']}")
    print(f"   Status: {'Working' if best_camera['working'] else 'Issues'}")
    
    print("\n📝 To change camera in config:")
    print(f'   Edit config/controls.json: "camera_index": {best_camera["index"]}')
    
    if len(available_cameras) > 1:
        print(f"\n🔄 Alternative cameras:")
        for cam in available_cameras:
            if cam['index'] != best_camera['index']:
                print(f"   Camera {cam['index']}: {cam['resolution']}")


if __name__ == "__main__":
    available_cameras = detect_available_cameras()
    show_current_config()
    recommend_settings(available_cameras)
