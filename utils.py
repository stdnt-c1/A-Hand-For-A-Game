import mediapipe as mp
import numpy as np
import math
from mediapipe.framework.formats import landmark_pb2

# Landmark indices from MediaPipe Hands
class HandLandmark:
    WRIST = 0
    THUMB_CMC = 1
    THUMB_MCP = 2
    THUMB_IP = 3
    THUMB_TIP = 4
    INDEX_FINGER_MCP = 5
    INDEX_FINGER_PIP = 6
    INDEX_FINGER_DIP = 7
    INDEX_FINGER_TIP = 8
    MIDDLE_FINGER_MCP = 9
    MIDDLE_FINGER_PIP = 10
    MIDDLE_FINGER_DIP = 11
    MIDDLE_FINGER_TIP = 12
    RING_FINGER_MCP = 13
    RING_FINGER_PIP = 14
    RING_FINGER_DIP = 15
    RING_FINGER_TIP = 16
    PINKY_MCP = 17
    PINKY_PIP = 18
    PINKY_DIP = 19
    PINKY_TIP = 20

def smooth_landmarks(landmark_history, current_landmarks, smoothing_factor):
    """
    Applies a simple moving average smoothing to hand landmarks.
    """
    if len(landmark_history) < smoothing_factor:
        landmark_history.append(current_landmarks)
    else:
        landmark_history.pop(0)
        landmark_history.append(current_landmarks)

    smoothed_landmarks_np = np.mean(landmark_history, axis=0)

    smoothed_landmark_proto = landmark_pb2.NormalizedLandmarkList()
    for lm in smoothed_landmarks_np:
        landmark = smoothed_landmark_proto.landmark.add()
        landmark.x, landmark.y, landmark.z = lm

    return smoothed_landmark_proto, landmark_history

def is_right_hand(handedness):
    """Checks if the detected hand is the right hand."""
    if handedness:
        for hand in handedness:
            if hand.classification[0].label == 'Right':
                return True
    return False

def get_landmark_coords(landmarks, landmark_index):
    """Returns the (x, y) coordinates of a specific landmark."""
    lm = landmarks.landmark[landmark_index]
    return lm.x, lm.y

def calculate_palm_bbox_norm(landmarks):
    """
    Calculates the normalized bounding box around the palm using specified landmarks.
    Returns a dictionary with min_x, max_x, min_y, max_y, width, height, and center.
    """
    palm_indices = [
        HandLandmark.WRIST,
        HandLandmark.INDEX_FINGER_MCP,
        HandLandmark.MIDDLE_FINGER_MCP,
        HandLandmark.RING_FINGER_MCP,
        HandLandmark.PINKY_MCP
    ]

    min_x, min_y = 1.0, 1.0
    max_x, max_y = 0.0, 0.0

    for index in palm_indices:
        lm = landmarks.landmark[index]
        min_x = min(min_x, lm.x)
        max_x = max(max_x, lm.x)
        min_y = min(min_y, lm.y)
        max_y = max(max_y, lm.y)

    width = max_x - min_x
    height = max_y - min_y
    center_x = min_x + width / 2
    center_y = min_y + height / 2

    return {
        "min_x": min_x, "max_x": max_x, "min_y": min_y, "max_y": max_y,
        "width": width, "height": height,
        "center_x": center_x, "center_y": center_y
    }

def is_finger_in_palm_bbox(landmarks, finger_tip_index, palm_bbox):
    """Checks if a fingertip is within the palm bounding box."""
    tip_x, tip_y = get_landmark_coords(landmarks, finger_tip_index)
    return (palm_bbox["min_x"] <= tip_x <= palm_bbox["max_x"] and
            palm_bbox["min_y"] <= tip_y <= palm_bbox["max_y"])

def calculate_pip_joint_roi(landmarks, finger_pip_index, palm_bbox_width):
    """
    Calculates the circular ROI for a PIP joint.
    Radius is 10% of the Palm Bounding Box width.
    """
    pip_x, pip_y = get_landmark_coords(landmarks, finger_pip_index)
    radius = 0.10 * palm_bbox_width
    return {"x": pip_x, "y": pip_y, "radius": radius}

def calculate_fingertip_roi(landmarks, finger_tip_index, palm_bbox_width):
    """
    Calculates the circular ROI for a fingertip.
    Radius is 5% of the Palm Bounding Box width.
    """
    tip_x, tip_y = get_landmark_coords(landmarks, finger_tip_index)
    radius = 0.05 * palm_bbox_width
    return {"x": tip_x, "y": tip_y, "radius": radius}

def calculate_distance(p1_x, p1_y, p2_x, p2_y):
    """Calculates the Euclidean distance between two points."""
    return math.hypot(p1_x - p2_x, p1_y - p2_y)

def calculate_roi_overlap(roi1, roi2):
    """
    Calculates the overlap percentage of two circular ROIs.
    The percentage is calculated as the intersection area divided by the area of the smaller ROI.
    """
    dist = calculate_distance(roi1['x'], roi1['y'], roi2['x'], roi2['y'])
    r1, r2 = roi1['radius'], roi2['radius']

    if dist >= r1 + r2:
        return 0.0  # No overlap

    if dist <= abs(r1 - r2):
        # One circle is entirely inside the other
        smaller_roi_area = math.pi * min(r1, r2)**2
        return 100.0 if smaller_roi_area > 0 else 0.0

    r1_sq, r2_sq = r1**2, r2**2
    dist_sq = dist**2

    # Using the formula for the area of intersection of two circles
    angle1 = math.acos((dist_sq + r1_sq - r2_sq) / (2 * dist * r1))
    angle2 = math.acos((dist_sq + r2_sq - r1_sq) / (2 * dist * r2))

    intersection_area = (r1_sq * angle1) + (r2_sq * angle2) - 0.5 * math.sqrt((-dist + r1 + r2) * (dist + r1 - r2) * (dist - r1 + r2) * (dist + r1 + r2))

    smaller_roi_area = math.pi * min(r1, r2)**2

    if smaller_roi_area == 0:
        return 0.0

    overlap_percentage = (intersection_area / smaller_roi_area) * 100
    return overlap_percentage

def calculate_tilt_angle(p1_x, p1_y, p2_x, p2_y):
    """Calculates the angle of a line with respect to the vertical axis."""
    delta_y = p2_y - p1_y
    delta_x = p2_x - p1_x
    angle_rad = math.atan2(delta_x, delta_y) # Angle with the positive Y-axis
    angle_deg = math.degrees(angle_rad)
    # Normalize to be 0 when vertical, positive to the right, negative to the left
    return angle_deg