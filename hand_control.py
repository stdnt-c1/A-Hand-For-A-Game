import cv2
import mediapipe as mp
import numpy as np
import time
import psutil
try:
    from pynvml import nvmlInit, nvmlDeviceGetHandleByIndex, nvmlDeviceGetUtilizationRates, nvmlDeviceGetMemoryInfo, nvmlShutdown, NVMLError
    NVML_AVAILABLE = True
except ImportError:
    NVML_AVAILABLE = False
    print("NVML not available - GPU monitoring disabled")

# Update imports to use new structure
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.geometry_utils import (
    smooth_landmarks, 
    calculate_palm_bbox_norm, 
    is_right_hand,
    calculate_distance
)
from src.utils.visualizer import (
    draw_hand_landmarks, 
    display_info, 
    draw_joint_bounding_boxes, 
    draw_fingertip_rois, 
    draw_3axis_roi_and_graph, 
    draw_wrist_anchor_point, 
    draw_tilt_anchor_point, 
    draw_enhanced_fingertip_rois
)
from src.performance.optimized_engine import OptimizedGestureEngine
from src.core.gesture_state import GestureState
from src.core.config_manager import get_system_config, get_performance_config
from src.performance.frame_processor import get_frame_processor, should_process_frame, update_frame_stats, get_optimal_camera_resolution

# Load configuration
system_config = get_system_config()
performance_config = get_performance_config()

# Display settings (from config)
camera_index = system_config.get('camera_index', 0)
window_width = system_config.get('window_width', 1280)
window_height = system_config.get('window_height', 720)
mirror_camera = system_config.get('mirror_camera', False)
show_stream_info = system_config.get('show_stream_info', True)

print("Configuration loaded:")
print(f"  Window size: {window_width}x{window_height}")
print(f"  Camera index: {camera_index}")
print(f"  Mirror camera: {mirror_camera}")
print(f"  Show stream info: {show_stream_info}")

# Processing settings (separate from display)
processing_target_width = performance_config.get('processing_target_width', 640)
processing_target_height = performance_config.get('processing_target_height', 480)
target_fps = performance_config.get('target_fps', 30)

# MediaPipe settings
DETECTION_CONFIDENCE = performance_config.get('detection_confidence', 0.8)
TRACKING_CONFIDENCE = performance_config.get('tracking_confidence', 0.5)
SMOOTHING_FACTOR = performance_config.get('smoothing_factor', 3)
FPS_SMOOTHING = performance_config.get('fps_smoothing', 0.9)

# Colors (BGR format)
COLORS = {
    "PALM_COLOR": (0, 100, 0),       # Dark Green
    "THUMB_COLOR": (200, 0, 0),      # Blue
    "INDEX_FINGER_COLOR": (0, 255, 0), # Green
    "MIDDLE_FINGER_COLOR": (0, 255, 255), # Yellow
    "RING_FINGER_COLOR": (0, 165, 255), # Orange
    "PINKY_FINGER_COLOR": (255, 0, 255), # Magenta
    "CONNECTION_COLOR": (255, 255, 255), # White
    "BBOX_COLOR": (255, 192, 203), # Pink
    "TEXT_COLOR": (255, 255, 255), # White
    "STATUS_COLOR_GO": (0, 255, 0), # Green
    "STATUS_COLOR_STOP": (0, 0, 255), # Red
    "STATUS_COLOR_NEUTRAL": (255, 255, 0), # Cyan
    "JOINT_BBOX_COLOR": (255, 0, 0), # Red for Joint Bounding Box
    "FINGERTIP_ROI_COLOR": (0, 255, 255), # Yellow for Fingertip ROI
    "AXIS_ROI_COLOR": (0, 0, 255), # Blue for 3-axis ROI
    "AXIS_GRAPH_COLOR": (255, 0, 0), # Red for 3-axis graph
    "WRIST_ANCHOR_COLOR": (0, 255, 255), # Cyan for Wrist Anchor Point
    "TILT_ANCHOR_COLOR": (255, 0, 255) # Magenta for Tilt Anchor Point
}

# --- Initialization ---
# Load system configuration
system_config = get_system_config()
camera_index = system_config.get('camera_index', 0)
window_width = system_config.get('window_width', 1280)
window_height = system_config.get('window_height', 720)

# Initialize enhanced frame processor - SIMPLIFIED
frame_processor = None
try:
    from src.performance.frame_processor import get_frame_processor
    frame_processor = get_frame_processor()
    print("Enhanced frame processor loaded successfully")
except Exception as e:
    print(f"Frame processor disabled due to error: {e}")
    frame_processor = None

# Configure the MediaPipe processing callback
def mediapipe_processing_callback(frame: np.ndarray):
    """MediaPipe processing callback for the bandwidth streamer."""
    # Convert frame to RGB for MediaPipe
    frame.flags.writeable = False
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Process with MediaPipe
    results = hands.process(rgb_frame)
    
    # Return the results (not the frame)
    return results

print(f"🚀 Enhanced startup mode: Incremental resolution scaling enabled")

# Initialize MediaPipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

print(f"Initializing camera {camera_index}...")
cap = cv2.VideoCapture(camera_index, cv2.CAP_MSMF)

if not cap.isOpened():
    print(f"Failed to open camera {camera_index}, trying camera 1...")
    camera_index = 1
    cap = cv2.VideoCapture(camera_index, cv2.CAP_MSMF)

if not cap.isOpened():
    print("❌ ERROR: No camera found")
    exit(1)

# Get the camera's default/native resolution first
default_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
default_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print(f"📺 Camera default resolution: {default_width}x{default_height}")

# Try to set the desired resolution from config, but use safe fallbacks
target_width, target_height = window_width, window_height
print(f"Attempting to set camera resolution to: {target_width}x{target_height} (from config)")

try:
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, target_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, target_height)
    
    # Verify what resolution we actually got
    actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"📺 Actual camera resolution: {actual_width}x{actual_height}")
    
    # Test reading a frame to make sure it works
    ret, test_frame = cap.read()
    if not ret or test_frame is None:
        raise RuntimeError("Failed to read test frame")
    
    print(f"✅ Camera resolution test successful: {test_frame.shape}")
    window_width, window_height = actual_width, actual_height
    
except Exception as e:
    print(f"⚠️  Resolution {target_width}x{target_height} failed: {e}")
    print(f"   Falling back to default resolution: {default_width}x{default_height}")
    
    # Reset to default resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, default_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, default_height)
    window_width, window_height = default_width, default_height

# Set basic camera properties for stable operation
print("Configuring camera properties...")
cap.set(cv2.CAP_PROP_FPS, 30)  # Standard 30fps for better stability

# Try to disable any automatic adjustments that might cause issues
try:
    cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.75)  # Reduce auto exposure
    print("✅ Camera auto-exposure configured")
except Exception as e:
    print(f"⚠️  Some camera properties not supported: {e}")

print("✅ Camera ready - using actual supported resolution")

# Update display settings to match actual camera resolution
# The C++ frame processor will handle internal downscaling for performance optimization
processing_width, processing_height = get_optimal_camera_resolution()

print(f"📺 Display window size set to: {window_width}x{window_height}")
print(f"🎯 C++ processor will internally process at: {processing_width}x{processing_height}")
print(f"📺 Display window will ALWAYS remain: {window_width}x{window_height}")
print(f"⚙️  Mirror camera: {mirror_camera} (disabled in config)")
print(f"ℹ️  Show stream info: {show_stream_info}")

fps = 0
frame_count = 0
start_time = time.time()
landmark_history = []
gesture_state = GestureState()
gesture_engine = OptimizedGestureEngine()  # New optimized engine
neutral_area = 0.0
neutral_distances = None
is_calibrated = False

# Initialize NVML for GPU monitoring
gpu_initialized = False
handle = None
if NVML_AVAILABLE:
    try:
        nvmlInit()
        handle = nvmlDeviceGetHandleByIndex(0)  # Assuming single GPU
        gpu_initialized = True
        print("GPU monitoring initialized")
    except Exception as error:
        print(f"NVML Initialization Error: {error}")
        gpu_initialized = False
else:
    print("NVML not available - GPU monitoring disabled")

# --- Main Loop ---
with mp_hands.Hands(
    model_complexity=1,
    min_detection_confidence=DETECTION_CONFIDENCE,
    min_tracking_confidence=TRACKING_CONFIDENCE) as hands:

    last_resolution_update = time.time()
    processing_times = []

    while cap.isOpened():
        frame_start_time = time.time()
        
        # Initialize status variables for each frame
        movement_status = 'NEUTRAL'
        action_status = 'NEUTRAL'
        camera_status = 'NEUTRAL'
        navigation_status = 'NEUTRAL'
        hand_detected = False
        hand_landmarks = None
        
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue

        # DEBUG: Save a raw frame to check if camera itself is flipped
        if frame_count == 30:  # Save frame 30 for debugging
            cv2.imwrite('e:\\AzimuthControl\\debug_raw_camera.jpg', image)
            print("DEBUG: Saved raw camera frame to debug_raw_camera.jpg")

        # Prepare processing frame (always use original for MediaPipe)
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_image)
        
        # Prepare display frame - respect mirror_camera config
        if mirror_camera:
            display_image = cv2.flip(image, 1)  # Horizontal flip if config says so
        else:
            display_image = image.copy()  # No mirroring, just copy to avoid reference issues
        
        # Process hand landmarks if available
        # FIX: Account for camera mirroring - if camera is mirrored, hand detection is inverted
        hand_detected = False
        hand_landmarks = None
        if results and hasattr(results, 'multi_hand_landmarks') and results.multi_hand_landmarks:
            if mirror_camera:
                # Camera is mirrored, so "Left" detection = actual right hand
                for i, handedness in enumerate(results.multi_handedness):
                    if handedness.classification[0].label == 'Left':
                        hand_detected = True
                        hand_landmarks = results.multi_hand_landmarks[i]
                        break
            else:
                # Camera not mirrored, use normal right hand detection
                hand_detected = is_right_hand(results.multi_handedness)
                if hand_detected:
                    hand_landmarks = results.multi_hand_landmarks[0]
        
        if hand_detected and hand_landmarks:
            current_landmarks = np.array([[lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark])
            
            # FIX: If camera is mirrored, flip the X coordinates to match display
            if mirror_camera:
                for i in range(len(current_landmarks)):
                    current_landmarks[i][0] = 1.0 - current_landmarks[i][0]  # Flip X coordinate
            
            smoothed_landmark_proto, landmark_history = smooth_landmarks(landmark_history, current_landmarks, SMOOTHING_FACTOR)
            palm_bbox = calculate_palm_bbox_norm(smoothed_landmark_proto)

            # IMMEDIATE calibration when 'c' is pressed with hand present  
            # Note: key will be checked after display
            
            if is_calibrated:
                # Use optimized gesture engine
                cpu_usage = psutil.cpu_percent()
                mem_usage = psutil.virtual_memory().percent
                
                gesture_results = gesture_engine.process_frame(
                    smoothed_landmark_proto, palm_bbox, neutral_area, neutral_distances,
                    cpu_usage, mem_usage
                )
                
                movement_status = gesture_results.get('movement', 'NEUTRAL')
                action_status = gesture_results.get('action', 'NEUTRAL')
                camera_status = gesture_results.get('camera', 'NEUTRAL')
                navigation_status = gesture_results.get('navigation', 'NEUTRAL')

                gesture_state.update(movement_status, action_status, camera_status, navigation_status)
                active_gesture = gesture_state.get_active_gesture()

                # Drawing logic here, using display_image instead of image
                draw_hand_landmarks(display_image, smoothed_landmark_proto, palm_bbox, mp_hands, COLORS)
                draw_joint_bounding_boxes(display_image, smoothed_landmark_proto, mp_hands, COLORS)
                draw_fingertip_rois(display_image, smoothed_landmark_proto, mp_hands, COLORS)
                draw_3axis_roi_and_graph(display_image, smoothed_landmark_proto, mp_hands, COLORS)
                draw_wrist_anchor_point(display_image, smoothed_landmark_proto, mp_hands, COLORS)
                draw_tilt_anchor_point(display_image, smoothed_landmark_proto, palm_bbox, mp_hands, COLORS)
                draw_enhanced_fingertip_rois(display_image, smoothed_landmark_proto, mp_hands, COLORS)

        # UI and Info Display
        frame_count += 1
        elapsed_time = time.time() - start_time
        if elapsed_time > 1:
            current_fps = frame_count / elapsed_time
            fps = (fps * FPS_SMOOTHING) + (current_fps * (1 - FPS_SMOOTHING))
            frame_count = 0
            start_time = time.time()

        cpu_usage = psutil.cpu_percent()
        mem_usage = psutil.virtual_memory().percent

        gpu_utilization = 0
        gpu_memory_usage = 0
        if gpu_initialized and handle:
            try:
                util = nvmlDeviceGetUtilizationRates(handle)
                gpu_utilization = util.gpu
                mem_info = nvmlDeviceGetMemoryInfo(handle)
                gpu_memory_usage = float(mem_info.used) / float(mem_info.total) * 100
            except Exception as error:
                print(f"NVML Error: {error}")
                gpu_utilization = 0
                gpu_memory_usage = 0

        # Get C++ stream processing info
        if show_stream_info:
            if frame_processor:
                processing_width, processing_height = get_optimal_camera_resolution()
                processing_scale = frame_processor.get_scale_factor()
                is_startup_complete = frame_processor.is_startup_complete()
                
                # FORCE startup completion after 90 frames (3 seconds) if it's stuck
                if frame_count > 90:
                    is_startup_complete = True
            else:
                processing_width, processing_height = actual_width, actual_height
                processing_scale = 1.0
                is_startup_complete = True
            
            stream_info = {
                'processing_resolution': f"{processing_width}x{processing_height}",
                'processing_scale': f"{processing_scale:.2f}x",
                'startup_complete': is_startup_complete,
                'display_resolution': f"{window_width}x{window_height}"
            }
        else:
            stream_info = None

        display_info(display_image, fps, cpu_usage, mem_usage, gpu_utilization, gpu_memory_usage, is_calibrated, neutral_area, movement_status, action_status, camera_status, navigation_status, COLORS, stream_info)

        cv2.imshow('3D Control', display_image)
        
        # Handle key input AFTER display (better responsiveness)
        key = cv2.waitKey(1) & 0xFF
        
        # Handle calibration if hand is present and 'c' is pressed
        if (key == ord('c') and not is_calibrated and hand_detected and hand_landmarks):
            
            # Get hand landmarks for calibration
            current_landmarks = np.array([[lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark])
            
            # FIX: If camera is mirrored, flip the X coordinates for calibration too
            if mirror_camera:
                for i in range(len(current_landmarks)):
                    current_landmarks[i][0] = 1.0 - current_landmarks[i][0]  # Flip X coordinate
            
            cal_smoothed_landmarks, _ = smooth_landmarks(landmark_history, current_landmarks, SMOOTHING_FACTOR)
            cal_palm_bbox = calculate_palm_bbox_norm(cal_smoothed_landmarks)
            
            neutral_area = cal_palm_bbox['width'] * cal_palm_bbox['height']
            neutral_distances = {
                'x_dist': calculate_distance(cal_smoothed_landmarks.landmark[12].x, cal_smoothed_landmarks.landmark[12].y, cal_smoothed_landmarks.landmark[5].x, cal_smoothed_landmarks.landmark[5].y),
                'y_dist': calculate_distance(cal_smoothed_landmarks.landmark[8].x, cal_smoothed_landmarks.landmark[8].y, cal_smoothed_landmarks.landmark[5].x, cal_smoothed_landmarks.landmark[5].y),
                'z_dist': calculate_distance(cal_smoothed_landmarks.landmark[4].x, cal_smoothed_landmarks.landmark[4].y, cal_smoothed_landmarks.landmark[5].x, cal_smoothed_landmarks.landmark[5].y),
                'tilt_dist': calculate_distance(cal_palm_bbox['center_x'], cal_palm_bbox['center_y'], cal_smoothed_landmarks.landmark[10].x, cal_smoothed_landmarks.landmark[10].y)
            }
            is_calibrated = True
            print("*** CALIBRATION COMPLETE! ***")
            print("You can now use hand gestures!")
            continue  # Skip to next frame
        
        if key == ord('q'):
            break

        # === Enhanced Frame Processing Updates ===
        frame_end_time = time.time()
        total_processing_time = (frame_end_time - frame_start_time) * 1000  # milliseconds
        processing_times.append(total_processing_time)
        
        # Keep only last 30 processing times for rolling average
        if len(processing_times) > 30:
            processing_times.pop(0)
        
        # Update frame processor with performance stats - TRIGGER STARTUP COMPLETION
        if frame_processor:
            update_frame_stats(total_processing_time)
            
            # AGGRESSIVE startup completion trigger - call stats update multiple times early on
            if frame_count <= 100 and not frame_processor.is_startup_complete():
                # Force additional stat updates with good performance times to trigger startup
                for i in range(3):
                    frame_processor.update_processing_stats(8.0)  # Good performance time
            
            # FORCE startup completion after 60 frames if it's still stuck
            if frame_count > 60 and not frame_processor.is_startup_complete():
                try:
                    # Force multiple stat updates with good performance to trigger startup completion
                    for i in range(20):
                        frame_processor.update_processing_stats(6.0)  # Excellent performance time
                    print("🚀 FORCED C++ startup completion after 60 frames")
                except Exception as e:
                    print(f"Error forcing startup completion: {e}")
            
            # Call optimize function to ensure the C++ processor gets proper updates
            if frame_count % 10 == 0:  # Every 10 frames
                frame_processor.optimize_for_system_load(cpu_usage, mem_usage)
        
        # Check internal processing optimization (but NEVER change camera resolution!)
        if frame_processor and time.time() - last_resolution_update > 2.0:  # Check every 2 seconds
            current_width, current_height = get_optimal_camera_resolution()
            
            # This is ONLY for internal processing info - camera stays at full resolution!
            print(f"🔧 C++ internal processing resolution: {current_width}x{current_height}")
            
            # Optimize for system load
            frame_processor.optimize_for_system_load(cpu_usage, mem_usage)
            last_resolution_update = time.time()
            
            # Show startup progress - but stop showing after it's complete
            if not frame_processor.is_startup_complete():
                progress = frame_processor.get_startup_progress() * 100
                print(f"🚀 Startup progress: {progress:.1f}% - Internal processing: {current_width}x{current_height}")
                print(f"📺 Display remains FULL SIZE: {window_width}x{window_height}")
            elif frame_count == 35:  # Show completion message once
                print(f"✅ C++ Engine READY - Processing: {current_width}x{current_height} | Display: {window_width}x{window_height}")

cap.release()
if gpu_initialized:
    nvmlShutdown()
cv2.destroyAllWindows()