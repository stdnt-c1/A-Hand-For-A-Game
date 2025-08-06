import cv2
import sys
import mediapipe as mp
from pathlib import Path

# Handle both relative and absolute imports
try:
    from .geometry_utils import HandLandmark
except ImportError:
    # Add current directory to path for direct execution
    sys.path.insert(0, str(Path(__file__).parent))
    from geometry_utils import HandLandmark

def draw_hand_landmarks(image, landmarks, palm_bbox, mp_hands, colors):
    h, w, _ = image.shape
    min_x = int(palm_bbox['min_x'] * w)
    max_x = int(palm_bbox['max_x'] * w)
    min_y = int(palm_bbox['min_y'] * h)
    max_y = int(palm_bbox['max_y'] * h)

    cv2.rectangle(image, (min_x, min_y), (max_x, max_y), colors["BBOX_COLOR"], 2)

    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.5
    font_thickness = 1
    text_color = colors["TEXT_COLOR"]

    cv2.putText(image, "TOP", (min_x + (max_x - min_x) // 2 - 15, min_y - 10), font, font_scale, text_color, font_thickness)
    cv2.putText(image, "BOTTOM", (min_x + (max_x - min_x) // 2 - 25, max_y + 20), font, font_scale, text_color, font_thickness)
    cv2.putText(image, "LEFT", (min_x - 40, min_y + (max_y - min_y) // 2 + 5), font, font_scale, text_color, font_thickness)
    cv2.putText(image, "RIGHT", (max_x + 10, min_y + (max_y - min_y) // 2 + 5), font, font_scale, text_color, font_thickness)

    connections = mp_hands.HAND_CONNECTIONS
    for connection in connections:
        start_idx = connection[0]
        end_idx = connection[1]
        start_point = (int(landmarks.landmark[start_idx].x * w), int(landmarks.landmark[start_idx].y * h))
        end_point = (int(landmarks.landmark[end_idx].x * w), int(landmarks.landmark[end_idx].y * h))
        cv2.line(image, start_point, end_point, colors["CONNECTION_COLOR"], 2)

    for idx, lm in enumerate(landmarks.landmark):
        cx, cy = int(lm.x * w), int(lm.y * h)
        color = colors["PALM_COLOR"]
        if idx in [HandLandmark.THUMB_TIP, HandLandmark.THUMB_IP, HandLandmark.THUMB_MCP, HandLandmark.THUMB_CMC]:
            color = colors["THUMB_COLOR"]
        elif idx in [HandLandmark.INDEX_FINGER_TIP, HandLandmark.INDEX_FINGER_DIP, HandLandmark.INDEX_FINGER_PIP, HandLandmark.INDEX_FINGER_MCP]:
            color = colors["INDEX_FINGER_COLOR"]
        elif idx in [HandLandmark.MIDDLE_FINGER_TIP, HandLandmark.MIDDLE_FINGER_DIP, HandLandmark.MIDDLE_FINGER_PIP, HandLandmark.MIDDLE_FINGER_MCP]:
            color = colors["MIDDLE_FINGER_COLOR"]
        elif idx in [HandLandmark.RING_FINGER_TIP, HandLandmark.RING_FINGER_DIP, HandLandmark.RING_FINGER_PIP, HandLandmark.RING_FINGER_MCP]:
            color = colors["RING_FINGER_COLOR"]
        elif idx in [HandLandmark.PINKY_TIP, HandLandmark.PINKY_DIP, HandLandmark.PINKY_PIP, HandLandmark.PINKY_MCP]:
            color = colors["PINKY_FINGER_COLOR"]
        cv2.circle(image, (cx, cy), 5, color, cv2.FILLED)

def draw_joint_bounding_boxes(image, landmarks, mp_hands, colors):
    h, w, _ = image.shape
    joint_landmarks = [
        HandLandmark.INDEX_FINGER_PIP,
        HandLandmark.MIDDLE_FINGER_PIP,
        HandLandmark.RING_FINGER_PIP,
        HandLandmark.PINKY_PIP
    ]
    for lm_idx in joint_landmarks:
        lm = landmarks.landmark[lm_idx]
        cx, cy = int(lm.x * w), int(lm.y * h)
        bbox_radius_pixel = 35
        cv2.circle(image, (cx, cy), bbox_radius_pixel, colors["JOINT_BBOX_COLOR"], 1)

def draw_fingertip_rois(image, landmarks, mp_hands, colors):
    h, w, _ = image.shape
    fingertip_landmarks = [
        HandLandmark.THUMB_TIP,
        HandLandmark.INDEX_FINGER_TIP,
        HandLandmark.MIDDLE_FINGER_TIP,
        HandLandmark.RING_FINGER_TIP,
        HandLandmark.PINKY_TIP
    ]
    for lm_idx in fingertip_landmarks:
        lm = landmarks.landmark[lm_idx]
        cx, cy = int(lm.x * w), int(lm.y * h)
        cv2.circle(image, (cx, cy), 10, colors["FINGERTIP_ROI_COLOR"], 1)

def draw_enhanced_fingertip_rois(image, landmarks, mp_hands, colors):
    h, w, _ = image.shape
    enhanced_fingertip_landmarks = [
        HandLandmark.INDEX_FINGER_TIP,
        HandLandmark.MIDDLE_FINGER_TIP,
        HandLandmark.RING_FINGER_TIP,
        HandLandmark.PINKY_TIP
    ]
    for lm_idx in enhanced_fingertip_landmarks:
        lm = landmarks.landmark[lm_idx]
        cx, cy = int(lm.x * w), int(lm.y * h)
        cv2.circle(image, (cx, cy), 20, (0, 255, 255), 2)

def draw_3axis_roi_and_graph(image, landmarks, mp_hands, colors):
    h, w, _ = image.shape
    middle_tip = landmarks.landmark[HandLandmark.MIDDLE_FINGER_TIP]
    index_tip = landmarks.landmark[HandLandmark.INDEX_FINGER_TIP]
    thumb_tip = landmarks.landmark[HandLandmark.THUMB_TIP]
    index_mcp = landmarks.landmark[HandLandmark.INDEX_FINGER_MCP]

    cv2.circle(image, (int(middle_tip.x * w), int(middle_tip.y * h)), 15, colors["AXIS_ROI_COLOR"], 1)
    cv2.circle(image, (int(index_tip.x * w), int(index_tip.y * h)), 15, colors["AXIS_ROI_COLOR"], 1)
    cv2.circle(image, (int(thumb_tip.x * w), int(thumb_tip.y * h)), 15, colors["AXIS_ROI_COLOR"], 1)

    n_axis_point_pixel = (int(index_mcp.x * w), int(index_mcp.y * h))

    n_axis_roi_radius = 20
    cv2.circle(image, n_axis_point_pixel, n_axis_roi_radius, colors["AXIS_GRAPH_COLOR"], 1)

    cv2.line(image, (int(middle_tip.x * w), int(middle_tip.y * h)), n_axis_point_pixel, colors["AXIS_GRAPH_COLOR"], 1)
    cv2.line(image, (int(index_tip.x * w), int(index_tip.y * h)), n_axis_point_pixel, colors["AXIS_GRAPH_COLOR"], 1)
    cv2.line(image, (int(thumb_tip.x * w), int(thumb_tip.y * h)), n_axis_point_pixel, colors["AXIS_GRAPH_COLOR"], 1)
    cv2.circle(image, n_axis_point_pixel, 5, colors["AXIS_GRAPH_COLOR"], cv2.FILLED)

    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.5
    font_thickness = 1
    text_color = colors["TEXT_COLOR"]

    cv2.putText(image, "X", (int(middle_tip.x * w) + 10, int(middle_tip.y * h) - 10), font, font_scale, text_color, font_thickness)
    cv2.putText(image, "Y", (int(index_tip.x * w) + 10, int(index_tip.y * h) - 10), font, font_scale, text_color, font_thickness)
    cv2.putText(image, "Z", (int(thumb_tip.x * w) + 10, int(thumb_tip.y * h) - 10), font, font_scale, text_color, font_thickness)
    cv2.putText(image, "N", (n_axis_point_pixel[0] + 10, n_axis_point_pixel[1] - 10), font, font_scale, text_color, font_thickness)

def draw_wrist_anchor_point(image, landmarks, mp_hands, colors):
    h, w, _ = image.shape
    wrist_lm = landmarks.landmark[HandLandmark.WRIST]
    wrist_point_pixel = (int(wrist_lm.x * w), int(wrist_lm.y * h))
    cv2.circle(image, wrist_point_pixel, 8, colors["WRIST_ANCHOR_COLOR"], -1)

def draw_tilt_anchor_point(image, landmarks, palm_bbox, mp_hands, colors):
    h, w, _ = image.shape
    palm_center_x = int(palm_bbox['center_x'] * w)
    palm_center_y = int(palm_bbox['center_y'] * h)
    palm_center_point = (palm_center_x, palm_center_y)

    middle_pip_lm = landmarks.landmark[HandLandmark.MIDDLE_FINGER_PIP]
    middle_pip_point = (int(middle_pip_lm.x * w), int(middle_pip_lm.y * h))

    cv2.line(image, palm_center_point, middle_pip_point, colors["TILT_ANCHOR_COLOR"], 2)
    cv2.circle(image, palm_center_point, 5, colors["TILT_ANCHOR_COLOR"], -1)
    cv2.circle(image, middle_pip_point, 5, colors["TILT_ANCHOR_COLOR"], -1)

def display_info(image, fps, cpu_usage, mem_usage, gpu_utilization, gpu_memory_usage, is_calibrated, neutral_area, movement_status, action_status, camera_status, navigation_status, colors, stream_info=None):
    cv2.putText(image, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, colors["TEXT_COLOR"], 2)
    cv2.putText(image, f"CPU: {cpu_usage:.1f}%", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, colors["TEXT_COLOR"], 2)
    cv2.putText(image, f"MEM: {mem_usage:.1f}%", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, colors["TEXT_COLOR"], 2)
    cv2.putText(image, f"GPU Util: {gpu_utilization:.1f}%", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, colors["TEXT_COLOR"], 2)
    cv2.putText(image, f"GPU Mem: {gpu_memory_usage:.1f}%", (10, 190), cv2.FONT_HERSHEY_SIMPLEX, 1, colors["TEXT_COLOR"], 2)

    # Display stream processing info if enabled
    if stream_info:
        cv2.putText(image, f"Processing: {stream_info['processing_resolution']}", (10, 230), cv2.FONT_HERSHEY_SIMPLEX, 0.7, colors["TEXT_COLOR"], 2)
        cv2.putText(image, f"Scale: {stream_info['processing_scale']}", (10, 255), cv2.FONT_HERSHEY_SIMPLEX, 0.7, colors["TEXT_COLOR"], 2)
        cv2.putText(image, f"Display: {stream_info['display_resolution']}", (10, 280), cv2.FONT_HERSHEY_SIMPLEX, 0.7, colors["TEXT_COLOR"], 2)
        startup_status = "Ready" if stream_info['startup_complete'] else "Starting..."
        cv2.putText(image, f"C++ Engine: {startup_status}", (10, 305), cv2.FONT_HERSHEY_SIMPLEX, 0.7, colors["TEXT_COLOR"], 2)
        status_y_offset = 340
    else:
        status_y_offset = 230

    if not is_calibrated:
        cv2.putText(image, "Clench fist in neutral pose and press 'c' to calibrate", (10, status_y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.8, colors["STATUS_COLOR_NEUTRAL"], 2)
    else:
        cv2.putText(image, f"MOVEMENT: {movement_status}", (10, status_y_offset), cv2.FONT_HERSHEY_SIMPLEX, 1, colors["STATUS_COLOR_GO"], 2)
        cv2.putText(image, f"ACTION: {action_status}", (10, status_y_offset + 40), cv2.FONT_HERSHEY_SIMPLEX, 1, colors["STATUS_COLOR_GO"], 2)
        cv2.putText(image, f"CAMERA: {camera_status}", (10, status_y_offset + 80), cv2.FONT_HERSHEY_SIMPLEX, 1, colors["STATUS_COLOR_GO"], 2)
        cv2.putText(image, f"NAVIGATION: {navigation_status}", (10, status_y_offset + 120), cv2.FONT_HERSHEY_SIMPLEX, 1, colors["STATUS_COLOR_GO"], 2)