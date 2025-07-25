
import cv2
import mediapipe as mp
import numpy as np
import time
import psutil
import math

# --- Anatomical Reference ---
"""
Hand Bone Terminology:
- Distal Phalanges (DP): Fingertip bones (TIP in MediaPipe)
- Middle Phalanges (MP): Middle finger bones (DIP to PIP joints)
- Proximal Phalanges (PP): Base finger bones (PIP to MCP joints)
- Metacarpals (MC): Palm bones (MCP to CMC/wrist)

Joint Terminology:
- DIP: Distal Interphalangeal Joint (last joint near fingertip)
- PIP: Proximal Interphalangeal Joint (middle joint)
- MCP: Metacarpophalangeal Joint (base knuckle)
- CMC: Carpometacarpal Joint (wrist joint for thumb)
"""

# --- Gesture Detection Functions ---

def is_fist(landmarks):
    """
    Checks if the core fingers (index, middle, ring) are curled into a fist.
    Ignores thumb and pinky positions to allow simultaneous gestures.
    """
    try:
        # Core finger tips (index, middle, ring)
        index_tip_y = landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y
        middle_tip_y = landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y
        ring_tip_y = landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP].y

        # Core finger PIP joints (middle knuckles)
        index_pip_y = landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_PIP].y
        middle_pip_y = landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y
        ring_pip_y = landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_PIP].y

        # A fist is when the core fingertips are "below" (have a larger y-value) their PIP joints
        return (index_tip_y > index_pip_y and
                middle_tip_y > middle_pip_y and
                ring_tip_y > ring_pip_y)
    except:
        return False

def is_thumb_out(landmarks, handedness, palm_bbox, image=None):
    """
    Checks if the thumb is extended based on a clear set of rules.
    """
    try:
        thumb_tip = landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
        index_mcp = landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP]
        wrist = landmarks.landmark[mp_hands.HandLandmark.WRIST]
        min_x, max_x, min_y, max_y = palm_bbox

        # Rule 1: Is the thumb tip outside the palm's bounding box?
        is_outside = (thumb_tip.x < min_x or thumb_tip.x > max_x or
                      thumb_tip.y < min_y or thumb_tip.y > max_y)
        if not is_outside:
            return False # Fail fast if it's inside the box

        # Rule 2: Is it far enough away from multiple reference points?
        palm_width = max_x - min_x
        dist_to_index_mcp = math.hypot(thumb_tip.x - index_mcp.x, thumb_tip.y - index_mcp.y)
        dist_to_wrist = math.hypot(thumb_tip.x - wrist.x, thumb_tip.y - wrist.y)
        
        # Determine closest edge of the bounding box for the third distance check
        dist_to_bbox_edge = min(abs(thumb_tip.x - min_x), abs(thumb_tip.x - max_x))

        is_far_enough = (dist_to_index_mcp > palm_width * 0.6 and
                         dist_to_wrist > palm_width * 0.6 and
                         dist_to_bbox_edge > palm_width * 0.1)

        is_valid = is_outside and is_far_enough

        if image is not None:
            # Visualization for debugging
            h, w, _ = image.shape
            color = (0, 255, 0) if is_valid else (0, 0, 255)
            cv2.line(image, (int(thumb_tip.x*w), int(thumb_tip.y*h)), (int(index_mcp.x*w), int(index_mcp.y*h)), color, 1)
            cv2.line(image, (int(thumb_tip.x*w), int(thumb_tip.y*h)), (int(wrist.x*w), int(wrist.y*h)), color, 1)

        return is_valid
    except:
        return False

def is_pinky_out(landmarks, handedness, palm_bbox, image=None):
    """
    Checks if the pinky is extended based on a clear set of rules.
    """
    try:
        pinky_tip = landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
        ring_mcp = landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_MCP]
        wrist = landmarks.landmark[mp_hands.HandLandmark.WRIST]
        min_x, max_x, min_y, max_y = palm_bbox

        # Rule 1: Is the pinky tip outside the palm's bounding box?
        is_outside = (pinky_tip.x < min_x or pinky_tip.x > max_x or
                      pinky_tip.y < min_y or pinky_tip.y > max_y)
        if not is_outside:
            return False # Fail fast if it's inside the box

        # Rule 2: Is it far enough away from multiple reference points?
        palm_width = max_x - min_x
        dist_to_ring_mcp = math.hypot(pinky_tip.x - ring_mcp.x, pinky_tip.y - ring_mcp.y)
        dist_to_wrist = math.hypot(pinky_tip.x - wrist.x, pinky_tip.y - wrist.y)
        
        # Determine closest edge of the bounding box for the third distance check
        dist_to_bbox_edge = min(abs(pinky_tip.x - min_x), abs(pinky_tip.x - max_x))

        is_far_enough = (dist_to_ring_mcp > palm_width * 0.4 and
                         dist_to_wrist > palm_width * 0.6 and
                         dist_to_bbox_edge > palm_width * 0.1)

        is_valid = is_outside and is_far_enough

        if image is not None:
            # Visualization for debugging
            h, w, _ = image.shape
            color = (0, 255, 0) if is_valid else (0, 0, 255)
            cv2.line(image, (int(pinky_tip.x*w), int(pinky_tip.y*h)), (int(ring_mcp.x*w), int(ring_mcp.y*h)), color, 1)
            cv2.line(image, (int(pinky_tip.x*w), int(pinky_tip.y*h)), (int(wrist.x*w), int(wrist.y*h)), color, 1)

        return is_valid
    except:
        return False





# --- Configuration ---
# Screen and Camera
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
FPS_SMOOTHING = 0.9

# Hand Tracking
DETECTION_CONFIDENCE = 0.8
TRACKING_CONFIDENCE = 0.5

# Movement Logic
# Thresholds for hand area relative to frame area (in percentage)
FORWARD_THRESHOLD_PERCENT = 0.15  # 15% change from neutral
BACKWARD_THRESHOLD_PERCENT = 0.15  # 15% change from neutral
NEUTRAL_AREA = 0.0  # Default, will be calibrated (stores relative hand area)
is_calibrated = False

# Smoothing
SMOOTHING_FACTOR = 3
area_history = []  # Store history of hand areas
landmark_history = []

# Colors (BGR format)
PALM_COLOR = (0, 100, 0)       # Dark Green
THUMB_COLOR = (200, 0, 0)      # Blue
INDEX_FINGER_COLOR = (0, 255, 0) # Green
MIDDLE_FINGER_COLOR = (0, 255, 255) # Yellow
RING_FINGER_COLOR = (0, 165, 255) # Orange
PINKY_FINGER_COLOR = (255, 0, 255) # Magenta
CONNECTION_COLOR = (255, 255, 255) # White
BBOX_COLOR = (255, 192, 203) # Pink
TEXT_COLOR = (255, 255, 255) # White
STATUS_COLOR_GO = (0, 255, 0) # Green
STATUS_COLOR_STOP = (0, 0, 255) # Red
STATUS_COLOR_NEUTRAL = (255, 255, 0) # Cyan

# --- Initialization ---
# MediaPipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# OpenCV Video Capture
# Attempt to use MSMF backend with DX11 for better performance on Windows
cap = cv2.VideoCapture(0, cv2.CAP_MSMF)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, SCREEN_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, SCREEN_HEIGHT)
cap.set(cv2.CAP_PROP_FPS, 60)

# FPS and Resource Counters
fps = 0
frame_count = 0
start_time = time.time()

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

        # Flip the image horizontally for a selfie-view display.
        image = cv2.flip(image, 1)

        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(image)
        image.flags.writeable = True

        # Convert back to BGR for rendering
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # --- Hand Processing ---
        z_axis_status = "NEUTRAL"
        y_axis_status = "NEUTRAL"
        z_status_color = STATUS_COLOR_NEUTRAL
        y_status_color = STATUS_COLOR_NEUTRAL
        
        # Initialize tracking variables
        min_x = max_x = min_y = max_y = 0

        if results.multi_hand_landmarks:
            # Use only the first detected hand
            hand_landmarks = results.multi_hand_landmarks[0]
            handedness = results.multi_handedness[0]

            # --- Smoothing ---
            current_landmarks = np.array([[lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark])
            if len(landmark_history) < SMOOTHING_FACTOR:
                landmark_history.append(current_landmarks)
            else:
                landmark_history.pop(0)
                landmark_history.append(current_landmarks)

            smoothed_landmarks_np = np.mean(landmark_history, axis=0)
            
            from mediapipe.framework.formats import landmark_pb2
            smoothed_landmark_proto = landmark_pb2.NormalizedLandmarkList()
            for lm in smoothed_landmarks_np:
                landmark = smoothed_landmark_proto.landmark.add()
                landmark.x, landmark.y, landmark.z = lm

            # --- Bounding Box (Metacarpal Region) ---
            h, w, _ = image.shape
            # Only use metacarpal landmarks (MCP joints) and wrist
            metacarpal_landmarks = [
                mp_hands.HandLandmark.WRIST,           # Carpal bones (wrist)
                mp_hands.HandLandmark.THUMB_CMC,       # Thumb Carpometacarpal joint
                mp_hands.HandLandmark.INDEX_FINGER_MCP,# Index Metacarpophalangeal joint
                mp_hands.HandLandmark.MIDDLE_FINGER_MCP,# Middle Metacarpophalangeal joint
                mp_hands.HandLandmark.RING_FINGER_MCP, # Ring Metacarpophalangeal joint
                mp_hands.HandLandmark.PINKY_MCP        # Pinky Metacarpophalangeal joint
            ]
            
            # Calculate normalized coordinates for palm bounding box
            min_x_norm, min_y_norm = 1.0, 1.0
            max_x_norm, max_y_norm = 0.0, 0.0
            for landmark_idx in metacarpal_landmarks:
                lm = smoothed_landmark_proto.landmark[landmark_idx]
                min_x_norm = min(min_x_norm, lm.x)
                max_x_norm = max(max_x_norm, lm.x)
                min_y_norm = min(min_y_norm, lm.y)
                max_y_norm = max(max_y_norm, lm.y)
            
            # Convert normalized coordinates to pixel coordinates for drawing
            min_x = int(min_x_norm * w)
            max_x = int(max_x_norm * w)
            min_y = int(min_y_norm * h)
            max_y = int(max_y_norm * h)
            
            palm_bbox_norm = (min_x_norm, max_x_norm, min_y_norm, max_y_norm)

            # --- Gesture-based Movement Logic ---
            if is_calibrated:
                # Calculate current palm area ratio
                palm_width = max_x_norm - min_x_norm
                palm_height = max_y_norm - min_y_norm
                current_area_ratio = palm_width * palm_height

                # Calculate thresholds based on calibrated area
                forward_threshold = NEUTRAL_AREA * (1.0 + FORWARD_THRESHOLD_PERCENT)
                backward_threshold = NEUTRAL_AREA * (1.0 - BACKWARD_THRESHOLD_PERCENT)

                # Check Y-axis (Left/Right) first - these work independently
                # Pass image for visualization of validation lines
                thumb_extended = is_thumb_out(smoothed_landmark_proto, handedness, palm_bbox_norm, image)
                pinky_extended = is_pinky_out(smoothed_landmark_proto, handedness, palm_bbox_norm, image)
                
                # Set Y-axis status based on finger positions
                if thumb_extended and not pinky_extended:
                    y_axis_status = "LEFT"
                    y_status_color = STATUS_COLOR_GO
                elif pinky_extended and not thumb_extended:
                    y_axis_status = "RIGHT"
                    y_status_color = STATUS_COLOR_GO
                # If both are extended or neither is extended, stay neutral
                
                # Check Z-axis (Forward/Backward) only when making a fist
                # This works independently of the Y-axis status
                if is_fist(smoothed_landmark_proto):
                    # Larger area means hand is closer (FORWARD)
                    if current_area_ratio > forward_threshold:
                        z_axis_status = "FORWARD"
                        z_status_color = STATUS_COLOR_GO
                    elif current_area_ratio < backward_threshold:
                        z_axis_status = "BACKWARD"
                        z_status_color = STATUS_COLOR_STOP
                # If not a fist, Z-axis remains in its previous state

            # --- Drawing ---
            cv2.rectangle(image, (int(min_x), int(min_y)), (int(max_x), int(max_y)), BBOX_COLOR, 2)
            connections = mp_hands.HAND_CONNECTIONS
            for connection in connections:
                start_idx = connection[0]
                end_idx = connection[1]
                if start_idx in mp_hands.HandLandmark and end_idx in mp_hands.HandLandmark:
                    start_point = (int(smoothed_landmark_proto.landmark[start_idx].x * w), int(smoothed_landmark_proto.landmark[start_idx].y * h))
                    end_point = (int(smoothed_landmark_proto.landmark[end_idx].x * w), int(smoothed_landmark_proto.landmark[end_idx].y * h))
                    cv2.line(image, start_point, end_point, CONNECTION_COLOR, 2)

            for idx, lm in enumerate(smoothed_landmark_proto.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                color = PALM_COLOR
                if idx in [mp_hands.HandLandmark.THUMB_TIP, mp_hands.HandLandmark.THUMB_IP, mp_hands.HandLandmark.THUMB_MCP, mp_hands.HandLandmark.THUMB_CMC]:
                    color = THUMB_COLOR
                elif idx in [mp_hands.HandLandmark.INDEX_FINGER_TIP, mp_hands.HandLandmark.INDEX_FINGER_DIP, mp_hands.HandLandmark.INDEX_FINGER_PIP, mp_hands.HandLandmark.INDEX_FINGER_MCP]:
                    color = INDEX_FINGER_COLOR
                elif idx in [mp_hands.HandLandmark.MIDDLE_FINGER_TIP, mp_hands.HandLandmark.MIDDLE_FINGER_DIP, mp_hands.HandLandmark.MIDDLE_FINGER_PIP, mp_hands.HandLandmark.MIDDLE_FINGER_MCP]:
                    color = MIDDLE_FINGER_COLOR
                elif idx in [mp_hands.HandLandmark.RING_FINGER_TIP, mp_hands.HandLandmark.RING_FINGER_DIP, mp_hands.HandLandmark.RING_FINGER_PIP, mp_hands.HandLandmark.RING_FINGER_MCP]:
                    color = RING_FINGER_COLOR
                elif idx in [mp_hands.HandLandmark.PINKY_TIP, mp_hands.HandLandmark.PINKY_DIP, mp_hands.HandLandmark.PINKY_PIP, mp_hands.HandLandmark.PINKY_MCP]:
                    color = PINKY_FINGER_COLOR
                cv2.circle(image, (cx, cy), 5, color, cv2.FILLED)


        # --- UI and Information Display ---
        # Calculate FPS
        frame_count += 1
        elapsed_time = time.time() - start_time
        if elapsed_time > 1:
            current_fps = frame_count / elapsed_time
            fps = (fps * FPS_SMOOTHING) + (current_fps * (1 - FPS_SMOOTHING))
            frame_count = 0
            start_time = time.time()

        # Get resource usage
        cpu_usage = psutil.cpu_percent()
        mem_usage = psutil.virtual_memory().percent

        # Display Info
        cv2.putText(image, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, TEXT_COLOR, 2)
        cv2.putText(image, f"CPU: {cpu_usage:.1f}%", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, TEXT_COLOR, 2)
        cv2.putText(image, f"MEM: {mem_usage:.1f}%", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, TEXT_COLOR, 2)
        
        # Display Calibration and Movement Status
        if not is_calibrated:
            cv2.putText(image, "Clench fist in neutral pose and press 'c' to calibrate", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.8, STATUS_COLOR_NEUTRAL, 2)
        else:
            # Determine the overall color based on priority (Z-axis > Y-axis)
            display_color = z_status_color if z_axis_status != "NEUTRAL" else y_status_color
            
            # Format the movement status string
            movement_text = f"MOVEMENT=[{z_axis_status}, {y_axis_status}]"
            
            cv2.putText(image, movement_text, (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, display_color, 2)
            cv2.putText(image, f"Calibrated Depth: {NEUTRAL_AREA:.3f}", (10, 190), cv2.FONT_HERSHEY_SIMPLEX, 0.6, TEXT_COLOR, 1)


        # --- Show the final image ---
        cv2.imshow('3D Control', image)

        # --- Keyboard Controls ---
        key = cv2.waitKey(5) & 0xFF
        if key == ord('q'):
            break
        if key == ord('c') and not is_calibrated and results.multi_hand_landmarks:
            # Calibrate using palm area ratio
            palm_width = max_x_norm - min_x_norm
            palm_height = max_y_norm - min_y_norm
            NEUTRAL_AREA = palm_width * palm_height
            is_calibrated = True
            print(f"Calibrated! Neutral palm area ratio: {NEUTRAL_AREA:.4f}")


cap.release()
cv2.destroyAllWindows()
