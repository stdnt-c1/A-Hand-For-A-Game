import cv2
import mediapipe as mp
import numpy as np
import time
import psutil
from pynvml import * # Import NVML library

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

# --- Configuration ---
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
FPS_SMOOTHING = 0.9
DETECTION_CONFIDENCE = 0.8
TRACKING_CONFIDENCE = 0.5
SMOOTHING_FACTOR = 3

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
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

cap = cv2.VideoCapture(0, cv2.CAP_MSMF)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, SCREEN_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, SCREEN_HEIGHT)
cap.set(cv2.CAP_PROP_FPS, 30)  # Reduced from 60 to 30 for better performance

fps = 0
frame_count = 0
start_time = time.time()
landmark_history = []
gesture_state = GestureState()
gesture_engine = OptimizedGestureEngine()  # New optimized engine
neutral_area = 0.0
neutral_distances = None
is_calibrated = False

# Initialize NVML
try:
    nvmlInit()
    handle = nvmlDeviceGetHandleByIndex(0) # Assuming single GPU
    gpu_initialized = True
except Exception as error:
    print(f"NVML Initialization Error: {error}")
    gpu_initialized = False

# --- Main Loop ---
with mp_hands.Hands(
    model_complexity=1,
    min_detection_confidence=DETECTION_CONFIDENCE,
    min_tracking_confidence=TRACKING_CONFIDENCE) as hands:

    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue

        image = cv2.flip(image, 1)
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        movement_status = "NEUTRAL"
        action_status = "NEUTRAL"
        camera_status = "NEUTRAL"
        navigation_status = "NEUTRAL"

        if results.multi_hand_landmarks and is_right_hand(results.multi_handedness):
            hand_landmarks = results.multi_hand_landmarks[0]
            current_landmarks = np.array([[lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark])
            smoothed_landmark_proto, landmark_history = smooth_landmarks(landmark_history, current_landmarks, SMOOTHING_FACTOR)
            palm_bbox = calculate_palm_bbox_norm(smoothed_landmark_proto)

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

                # Drawing logic here, using active_gesture
                draw_hand_landmarks(image, smoothed_landmark_proto, palm_bbox, mp_hands, COLORS)
                draw_joint_bounding_boxes(image, smoothed_landmark_proto, mp_hands, COLORS)
                draw_fingertip_rois(image, smoothed_landmark_proto, mp_hands, COLORS)
                draw_3axis_roi_and_graph(image, smoothed_landmark_proto, mp_hands, COLORS)
                draw_wrist_anchor_point(image, smoothed_landmark_proto, mp_hands, COLORS)
                draw_tilt_anchor_point(image, smoothed_landmark_proto, palm_bbox, mp_hands, COLORS)
                draw_enhanced_fingertip_rois(image, smoothed_landmark_proto, mp_hands, COLORS)

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
        if gpu_initialized:
            try:
                util = nvmlDeviceGetUtilizationRates(handle)
                gpu_utilization = util.gpu
                mem_info = nvmlDeviceGetMemoryInfo(handle)
                gpu_memory_usage = (mem_info.used / mem_info.total) * 100
            except NVMLError as error:
                print(f"NVML Error: {error}")

        display_info(image, fps, cpu_usage, mem_usage, gpu_utilization, gpu_memory_usage, is_calibrated, neutral_area, movement_status, action_status, camera_status, navigation_status, COLORS)

        cv2.imshow('3D Control', image)

        key = cv2.waitKey(5) & 0xFF
        if key == ord('q'):
            break
        if key == ord('c') and not is_calibrated and results.multi_hand_landmarks:
            palm_bbox = calculate_palm_bbox_norm(smoothed_landmark_proto)
            neutral_area = palm_bbox['width'] * palm_bbox['height']
            neutral_distances = {
                'x_dist': calculate_distance(smoothed_landmark_proto.landmark[12].x, smoothed_landmark_proto.landmark[12].y, smoothed_landmark_proto.landmark[5].x, smoothed_landmark_proto.landmark[5].y),
                'y_dist': calculate_distance(smoothed_landmark_proto.landmark[8].x, smoothed_landmark_proto.landmark[8].y, smoothed_landmark_proto.landmark[5].x, smoothed_landmark_proto.landmark[5].y),
                'z_dist': calculate_distance(smoothed_landmark_proto.landmark[4].x, smoothed_landmark_proto.landmark[4].y, smoothed_landmark_proto.landmark[5].x, smoothed_landmark_proto.landmark[5].y),
                'tilt_dist': calculate_distance(palm_bbox['center_x'], palm_bbox['center_y'], smoothed_landmark_proto.landmark[10].x, smoothed_landmark_proto.landmark[10].y)
            }
            is_calibrated = True
            print(f"Calibrated! Neutral palm area ratio: {neutral_area:.4f}")

cap.release()
if gpu_initialized:
    nvmlShutdown()
cv2.destroyAllWindows()