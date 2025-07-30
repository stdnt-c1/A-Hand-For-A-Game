import math
from utils import calculate_fingertip_roi, calculate_pip_joint_roi, calculate_roi_overlap, is_finger_in_palm_bbox, calculate_tilt_angle, calculate_distance, HandLandmark

# Gesture Definitions

# General Rules:
# - Right Hand Only: All controls are valid only for the right hand.
# - Gesture Duration: A gesture must be held for at least 0.3 seconds to trigger.
# - Priority Hierarchy: Navigation > Camera > Movement > Action.
# - Re-engagement: Requires a 0.2-second neutral state.
# - Tolerances: 10% for axis length changes, 50% for Fingertip ROI overlap.

# Visualizer Constants
PALM_BOUNDING_BOX_POINTS = [HandLandmark.WRIST, HandLandmark.INDEX_FINGER_MCP, HandLandmark.MIDDLE_FINGER_MCP, HandLandmark.RING_FINGER_MCP, HandLandmark.PINKY_MCP]
FINGERTIP_ROI_RADIUS_PERCENT = 0.05  # 5% of Palm Bounding Box width
JOINT_ROI_RADIUS_PERCENT = 0.10  # 10% of Palm Bounding Box width
TILT_ANCHOR_POINTS = [HandLandmark.MIDDLE_FINGER_MCP, HandLandmark.RING_FINGER_MCP] # Not directly used in validation, but for visualizer

# Helper for Action Control: Check if other fingertips are outside Palm Bounding Box and Joint ROIs
def _other_fingers_out_of_action_zone(landmarks, palm_bbox, current_tip_idx):
    other_tips = [HandLandmark.THUMB_TIP, HandLandmark.INDEX_FINGER_TIP, HandLandmark.MIDDLE_FINGER_TIP, HandLandmark.RING_FINGER_TIP, HandLandmark.PINKY_TIP]
    if current_tip_idx in other_tips:
        other_tips.remove(current_tip_idx)

    for tip_idx in other_tips:
        if is_finger_in_palm_bbox(landmarks, tip_idx, palm_bbox):
            return False
        # Check if outside Joint ROI for non-thumb fingers
        if tip_idx != HandLandmark.THUMB_TIP:
            # Assuming PIP is TIP - 2 for Index, Middle, Ring, Pinky
            pip_idx = tip_idx - 2 
            if calculate_roi_overlap(
                calculate_fingertip_roi(landmarks, tip_idx, palm_bbox['width']),
                calculate_pip_joint_roi(landmarks, pip_idx, palm_bbox['width'])
            ) >= 50:
                return False
    return True

# Helper for Camera Control: Check if Ring and Pinky are in Palm Bounding Box
def _ring_pinky_in_palm(landmarks, palm_bbox):
    return is_finger_in_palm_bbox(landmarks, HandLandmark.RING_FINGER_TIP, palm_bbox) and \
           is_finger_in_palm_bbox(landmarks, HandLandmark.PINKY_TIP, palm_bbox)

# Helper for Camera Control: Check if Index, Middle, Thumb are extended outward
def _index_middle_thumb_extended(landmarks, palm_bbox):
    return not is_finger_in_palm_bbox(landmarks, HandLandmark.INDEX_FINGER_TIP, palm_bbox) and \
           not is_finger_in_palm_bbox(landmarks, HandLandmark.MIDDLE_FINGER_TIP, palm_bbox) and \
           not is_finger_in_palm_bbox(landmarks, HandLandmark.THUMB_TIP, palm_bbox)


GESTURE_DEFINITIONS = {
    "ACTION_CONTROL": {
        "NEUTRAL": {
            "description": "Palm is in a neutral position.",
            "validation": lambda landmarks, palm_bbox: (
                # All fingertips (TIP1-TIP5) are extended outward and not within the Palm Bounding Box or any Joint ROI.
                all(not is_finger_in_palm_bbox(landmarks, tip, palm_bbox) for tip in [
                    HandLandmark.THUMB_TIP, HandLandmark.INDEX_FINGER_TIP, 
                    HandLandmark.MIDDLE_FINGER_TIP, HandLandmark.RING_FINGER_TIP, 
                    HandLandmark.PINKY_TIP
                ]) and
                # At least 4 fingertips must be detected outside the Palm Bounding Box (implicitly handled by 'all' above)
                # Ensure no overlap with joint ROIs for non-thumb fingers
                all(
                    calculate_roi_overlap(
                        calculate_fingertip_roi(landmarks, tip, palm_bbox['width']),
                        calculate_pip_joint_roi(landmarks, tip - 2, palm_bbox['width'])
                    ) < 50 
                    for tip in [HandLandmark.INDEX_FINGER_TIP, HandLandmark.MIDDLE_FINGER_TIP, HandLandmark.RING_FINGER_TIP, HandLandmark.PINKY_TIP]
                )
            )
        },
        "ATTACK": {
            "description": "Thumb is within the Palm Bounding Box.",
            "validation": lambda landmarks, palm_bbox: (
                is_finger_in_palm_bbox(landmarks, HandLandmark.THUMB_TIP, palm_bbox) and
                _other_fingers_out_of_action_zone(landmarks, palm_bbox, HandLandmark.THUMB_TIP)
            )
        },
        "SKILL_1": {
            "description": "Index finger is curled.",
            "validation": lambda landmarks, palm_bbox: (
                calculate_roi_overlap(
                    calculate_fingertip_roi(landmarks, HandLandmark.INDEX_FINGER_TIP, palm_bbox['width']),
                    calculate_pip_joint_roi(landmarks, HandLandmark.INDEX_FINGER_PIP, palm_bbox['width'])
                ) >= 50 and
                not is_finger_in_palm_bbox(landmarks, HandLandmark.INDEX_FINGER_TIP, palm_bbox) and
                _other_fingers_out_of_action_zone(landmarks, palm_bbox, HandLandmark.INDEX_FINGER_TIP)
            )
        },
        "SKILL_2": {
            "description": "Middle finger is curled.",
            "validation": lambda landmarks, palm_bbox: (
                calculate_roi_overlap(
                    calculate_fingertip_roi(landmarks, HandLandmark.MIDDLE_FINGER_TIP, palm_bbox['width']),
                    calculate_pip_joint_roi(landmarks, HandLandmark.MIDDLE_FINGER_PIP, palm_bbox['width'])
                ) >= 50 and
                not is_finger_in_palm_bbox(landmarks, HandLandmark.MIDDLE_FINGER_TIP, palm_bbox) and
                _other_fingers_out_of_action_zone(landmarks, palm_bbox, HandLandmark.MIDDLE_FINGER_TIP)
            )
        },
        "SKILL_3": {
            "description": "Ring finger is curled.",
            "validation": lambda landmarks, palm_bbox: (
                calculate_roi_overlap(
                    calculate_fingertip_roi(landmarks, HandLandmark.RING_FINGER_TIP, palm_bbox['width']),
                    calculate_pip_joint_roi(landmarks, HandLandmark.RING_FINGER_PIP, palm_bbox['width'])
                ) >= 50 and
                not is_finger_in_palm_bbox(landmarks, HandLandmark.RING_FINGER_TIP, palm_bbox) and
                _other_fingers_out_of_action_zone(landmarks, palm_bbox, HandLandmark.RING_FINGER_TIP)
            )
        },
        "UTILITY": {
            "description": "Pinky finger is curled.",
            "validation": lambda landmarks, palm_bbox: (
                calculate_roi_overlap(
                    calculate_fingertip_roi(landmarks, HandLandmark.PINKY_TIP, palm_bbox['width']),
                    calculate_pip_joint_roi(landmarks, HandLandmark.PINKY_PIP, palm_bbox['width'])
                ) >= 50 and
                not is_finger_in_palm_bbox(landmarks, HandLandmark.PINKY_TIP, palm_bbox) and
                _other_fingers_out_of_action_zone(landmarks, palm_bbox, HandLandmark.PINKY_TIP)
            )
        }
    },
    "MOVEMENT_CONTROL": {
        "NEUTRAL": {
            "description": "Ring finger is within the Palm Bounding Box.",
            "validation": lambda landmarks, palm_bbox, neutral_area, neutral_distances: (
                is_finger_in_palm_bbox(landmarks, HandLandmark.RING_FINGER_TIP, palm_bbox) or
                all(is_finger_in_palm_bbox(landmarks, tip, palm_bbox) for tip in [
                    HandLandmark.THUMB_TIP, HandLandmark.INDEX_FINGER_TIP, 
                    HandLandmark.MIDDLE_FINGER_TIP, HandLandmark.RING_FINGER_TIP, 
                    HandLandmark.PINKY_TIP
                ]) # Fist gesture
            )
        },
        "FORWARD": {
            "description": "Hand is moving forward.",
            "validation": lambda landmarks, palm_bbox, neutral_area, neutral_distances: (
                is_finger_in_palm_bbox(landmarks, HandLandmark.RING_FINGER_TIP, palm_bbox) and
                (palm_bbox['width'] * palm_bbox['height']) > neutral_area * 1.1 # >10% increase
            )
        },
        "BACKWARD": {
            "description": "Hand is moving backward.",
            "validation": lambda landmarks, palm_bbox, neutral_area, neutral_distances: (
                is_finger_in_palm_bbox(landmarks, HandLandmark.RING_FINGER_TIP, palm_bbox) and
                (palm_bbox['width'] * palm_bbox['height']) < neutral_area * 0.9 # >10% decrease
            )
        },
        "LEFT": {
            "description": "Thumb is extended outward.",
            "validation": lambda landmarks, palm_bbox, neutral_area, neutral_distances: (
                is_finger_in_palm_bbox(landmarks, HandLandmark.RING_FINGER_TIP, palm_bbox) and
                not is_finger_in_palm_bbox(landmarks, HandLandmark.THUMB_TIP, palm_bbox)
            )
        },
        "RIGHT": {
            "description": "Pinky is extended outward.",
            "validation": lambda landmarks, palm_bbox, neutral_area, neutral_distances: (
                is_finger_in_palm_bbox(landmarks, HandLandmark.RING_FINGER_TIP, palm_bbox) and
                not is_finger_in_palm_bbox(landmarks, HandLandmark.PINKY_TIP, palm_bbox)
            )
        },
        "SHIFT": {
            "description": "Index finger is raised and curled.",
            "validation": lambda landmarks, palm_bbox, neutral_area, neutral_distances: (
                calculate_roi_overlap(
                    calculate_fingertip_roi(landmarks, HandLandmark.INDEX_FINGER_TIP, palm_bbox['width']),
                    calculate_pip_joint_roi(landmarks, HandLandmark.INDEX_FINGER_PIP, palm_bbox['width'])
                ) >= 50 and
                not is_finger_in_palm_bbox(landmarks, HandLandmark.INDEX_FINGER_TIP, palm_bbox) and
                is_finger_in_palm_bbox(landmarks, HandLandmark.RING_FINGER_TIP, palm_bbox) # Ring TIP4 must be in palm bbox
            )
        },
        "JUMP": {
            "description": "Thumb and Pinky are extended outward and the hand is tilted.",
            "validation": lambda landmarks, palm_bbox, neutral_distances: (
                not is_finger_in_palm_bbox(landmarks, HandLandmark.THUMB_TIP, palm_bbox) and
                not is_finger_in_palm_bbox(landmarks, HandLandmark.PINKY_TIP, palm_bbox) and
                (calculate_distance(palm_bbox['center_x'], palm_bbox['center_y'], landmarks.landmark[HandLandmark.MIDDLE_FINGER_PIP].x, landmarks.landmark[HandLandmark.MIDDLE_FINGER_PIP].y) < neutral_distances['tilt_dist'] * 0.9) # Tilt anchor point line decreases by >10%
            )
        }
    },
    "CAMERA_CONTROL": {
        "NEUTRAL": {
            "description": "3-axis formation is stable.",
            "validation": lambda landmarks, palm_bbox, neutral_distances: (
                _ring_pinky_in_palm(landmarks, palm_bbox) and
                _index_middle_thumb_extended(landmarks, palm_bbox)
            )
        },
        "PAN_UP": {
            "description": "When the 3-axis formation changes to indicate upward panning.",
            "validation": lambda landmarks, palm_bbox, neutral_distances: (
                _ring_pinky_in_palm(landmarks, palm_bbox) and
                _index_middle_thumb_extended(landmarks, palm_bbox) and
                calculate_distance(
                    landmarks.landmark[HandLandmark.INDEX_FINGER_TIP].x, landmarks.landmark[HandLandmark.INDEX_FINGER_TIP].y,
                    landmarks.landmark[HandLandmark.INDEX_FINGER_MCP].x, landmarks.landmark[HandLandmark.INDEX_FINGER_MCP].y
                ) < neutral_distances['y_dist'] * 0.9 and # Y-axis length decreases by >10%
                calculate_distance(
                    landmarks.landmark[HandLandmark.MIDDLE_FINGER_TIP].x, landmarks.landmark[HandLandmark.MIDDLE_FINGER_TIP].y,
                    landmarks.landmark[HandLandmark.INDEX_FINGER_MCP].x, landmarks.landmark[HandLandmark.INDEX_FINGER_MCP].y
                ) > neutral_distances['x_dist'] * 1.1 and # X-axis length increases by >10%
                abs(calculate_distance(
                    landmarks.landmark[HandLandmark.THUMB_TIP].x, landmarks.landmark[HandLandmark.THUMB_TIP].y,
                    landmarks.landmark[HandLandmark.INDEX_FINGER_MCP].x, landmarks.landmark[HandLandmark.INDEX_FINGER_MCP].y
                ) - neutral_distances['z_dist']) < neutral_distances['z_dist'] * 0.1 # Z-axis length remains within +/-10%
            )
        },
        "PAN_DOWN": {
            "description": "When the 3-axis formation changes to indicate downward panning.",
            "validation": lambda landmarks, palm_bbox, neutral_distances: (
                _ring_pinky_in_palm(landmarks, palm_bbox) and
                _index_middle_thumb_extended(landmarks, palm_bbox) and
                calculate_distance(
                    landmarks.landmark[HandLandmark.INDEX_FINGER_TIP].x, landmarks.landmark[HandLandmark.INDEX_FINGER_TIP].y,
                    landmarks.landmark[HandLandmark.INDEX_FINGER_MCP].x, landmarks.landmark[HandLandmark.INDEX_FINGER_MCP].y
                ) > neutral_distances['y_dist'] * 1.1 and # Y-axis length increases by >10%
                calculate_distance(
                    landmarks.landmark[HandLandmark.MIDDLE_FINGER_TIP].x, landmarks.landmark[HandLandmark.MIDDLE_FINGER_TIP].y,
                    landmarks.landmark[HandLandmark.INDEX_FINGER_MCP].x, landmarks.landmark[HandLandmark.INDEX_FINGER_MCP].y
                ) < neutral_distances['x_dist'] * 0.9 and # X-axis length decreases by >10%
                abs(calculate_distance(
                    landmarks.landmark[HandLandmark.THUMB_TIP].x, landmarks.landmark[HandLandmark.THUMB_TIP].y,
                    landmarks.landmark[HandLandmark.INDEX_FINGER_MCP].x, landmarks.landmark[HandLandmark.INDEX_FINGER_MCP].y
                ) - neutral_distances['z_dist']) < neutral_distances['z_dist'] * 0.1 # Z-axis length remains within +/-10%
            )
        },
        "PAN_LEFT": {
            "description": "When the 3-axis formation changes to indicate leftward panning.",
            "validation": lambda landmarks, palm_bbox, neutral_distances: (
                _ring_pinky_in_palm(landmarks, palm_bbox) and
                _index_middle_thumb_extended(landmarks, palm_bbox) and
                abs(calculate_distance(
                    landmarks.landmark[HandLandmark.INDEX_FINGER_TIP].x, landmarks.landmark[HandLandmark.INDEX_FINGER_TIP].y,
                    landmarks.landmark[HandLandmark.INDEX_FINGER_MCP].x, landmarks.landmark[HandLandmark.INDEX_FINGER_MCP].y
                ) - neutral_distances['y_dist']) < neutral_distances['y_dist'] * 0.1 and # Y-axis length remains within +/-10%
                calculate_distance(
                    landmarks.landmark[HandLandmark.MIDDLE_FINGER_TIP].x, landmarks.landmark[HandLandmark.MIDDLE_FINGER_TIP].y,
                    landmarks.landmark[HandLandmark.INDEX_FINGER_MCP].x, landmarks.landmark[HandLandmark.INDEX_FINGER_MCP].y
                ) > neutral_distances['x_dist'] * 1.1 and # X-axis length increases by >10%
                calculate_distance(
                    landmarks.landmark[HandLandmark.THUMB_TIP].x, landmarks.landmark[HandLandmark.THUMB_TIP].y,
                    landmarks.landmark[HandLandmark.INDEX_FINGER_MCP].x, landmarks.landmark[HandLandmark.INDEX_FINGER_MCP].y
                ) < neutral_distances['z_dist'] * 0.9 # Z-axis length decreases by >10%
            )
        },
        "PAN_RIGHT": {
            "description": "When the 3-axis formation changes to indicate rightward panning.",
            "validation": lambda landmarks, palm_bbox, neutral_distances: (
                _ring_pinky_in_palm(landmarks, palm_bbox) and
                _index_middle_thumb_extended(landmarks, palm_bbox) and
                abs(calculate_distance(
                    landmarks.landmark[HandLandmark.INDEX_FINGER_TIP].x, landmarks.landmark[HandLandmark.INDEX_FINGER_TIP].y,
                    landmarks.landmark[HandLandmark.INDEX_FINGER_MCP].x, landmarks.landmark[HandLandmark.INDEX_FINGER_MCP].y
                ) - neutral_distances['y_dist']) < neutral_distances['y_dist'] * 0.1 and # Y-axis length remains within +/-10%
                calculate_distance(
                    landmarks.landmark[HandLandmark.MIDDLE_FINGER_TIP].x, landmarks.landmark[HandLandmark.MIDDLE_FINGER_TIP].y,
                    landmarks.landmark[HandLandmark.INDEX_FINGER_MCP].x, landmarks.landmark[HandLandmark.INDEX_FINGER_MCP].y
                ) < neutral_distances['x_dist'] * 0.9 and # X-axis length decreases by >10%
                calculate_distance(
                    landmarks.landmark[HandLandmark.THUMB_TIP].x, landmarks.landmark[HandLandmark.THUMB_TIP].y,
                    landmarks.landmark[HandLandmark.INDEX_FINGER_MCP].x, landmarks.landmark[HandLandmark.INDEX_FINGER_MCP].y
                ) > neutral_distances['z_dist'] * 1.1 # Z-axis length increases by >10%
            )
        },
        "LOCK": {
            "description": "When the 3-axis formation collapses into overlapping ROIs.",
            "validation": lambda landmarks, palm_bbox, neutral_distances: (
                calculate_roi_overlap(
                    calculate_fingertip_roi(landmarks, HandLandmark.INDEX_FINGER_TIP, palm_bbox['width']),
                    calculate_fingertip_roi(landmarks, HandLandmark.MIDDLE_FINGER_TIP, palm_bbox['width'])
                ) > 0 and # Overlap between Index and Middle
                calculate_roi_overlap(
                    calculate_fingertip_roi(landmarks, HandLandmark.INDEX_FINGER_TIP, palm_bbox['width']),
                    calculate_fingertip_roi(landmarks, HandLandmark.THUMB_TIP, palm_bbox['width'])
                ) > 0 and # Overlap between Index and Thumb
                landmarks.landmark[HandLandmark.INDEX_FINGER_TIP].x < palm_bbox['min_x'] # Extended toward Palm Bounding Box - LEFT
            )
        }
    },
    "NAVIGATION_CONTROL": {
        "NEUTRAL": {
            "description": "Open palm.",
            "validation": lambda landmarks, palm_bbox: (
                all(not is_finger_in_palm_bbox(landmarks, tip, palm_bbox) for tip in [
                    HandLandmark.THUMB_TIP, HandLandmark.INDEX_FINGER_TIP, 
                    HandLandmark.MIDDLE_FINGER_TIP, HandLandmark.RING_FINGER_TIP, 
                    HandLandmark.PINKY_TIP
                ]) and
                all(
                    calculate_roi_overlap(
                        calculate_fingertip_roi(landmarks, tip, palm_bbox['width']),
                        calculate_pip_joint_roi(landmarks, tip - 2, palm_bbox['width'])
                    ) < 50 
                    for tip in [HandLandmark.INDEX_FINGER_TIP, HandLandmark.MIDDLE_FINGER_TIP, HandLandmark.RING_FINGER_TIP, HandLandmark.PINKY_TIP]
                )
            )
        },
        "OK": {
            "description": "Peace sign.",
            "validation": lambda landmarks, palm_bbox: (
                not is_finger_in_palm_bbox(landmarks, HandLandmark.INDEX_FINGER_TIP, palm_bbox) and # Index out
                not is_finger_in_palm_bbox(landmarks, HandLandmark.MIDDLE_FINGER_TIP, palm_bbox) and # Middle out
                is_finger_in_palm_bbox(landmarks, HandLandmark.THUMB_TIP, palm_bbox) and # Thumb in
                is_finger_in_palm_bbox(landmarks, HandLandmark.RING_FINGER_TIP, palm_bbox) and # Ring in
                is_finger_in_palm_bbox(landmarks, HandLandmark.PINKY_TIP, palm_bbox) and # Pinky in
                landmarks.landmark[HandLandmark.INDEX_FINGER_TIP].y < palm_bbox['min_y'] and # Index above TOP
                landmarks.landmark[HandLandmark.MIDDLE_FINGER_TIP].y < palm_bbox['min_y'] and # Middle above TOP
                calculate_distance(
                    landmarks.landmark[HandLandmark.INDEX_FINGER_TIP].x, landmarks.landmark[HandLandmark.INDEX_FINGER_TIP].y,
                    landmarks.landmark[HandLandmark.MIDDLE_FINGER_TIP].x, landmarks.landmark[HandLandmark.MIDDLE_FINGER_TIP].y
                ) > 0.1 * palm_bbox['width'] # Spaced apart
            )
        },
        "F": {
            "description": "Tilted peace sign.",
            "validation": lambda landmarks, palm_bbox: (
                not is_finger_in_palm_bbox(landmarks, HandLandmark.INDEX_FINGER_TIP, palm_bbox) and # Index out
                not is_finger_in_palm_bbox(landmarks, HandLandmark.MIDDLE_FINGER_TIP, palm_bbox) and # Middle out
                is_finger_in_palm_bbox(landmarks, HandLandmark.THUMB_TIP, palm_bbox) and # Thumb in
                is_finger_in_palm_bbox(landmarks, HandLandmark.RING_FINGER_TIP, palm_bbox) and # Ring in
                is_finger_in_palm_bbox(landmarks, HandLandmark.PINKY_TIP, palm_bbox) and # Pinky in
                landmarks.landmark[HandLandmark.INDEX_FINGER_TIP].y < palm_bbox['min_y'] and # Index above TOP
                landmarks.landmark[HandLandmark.MIDDLE_FINGER_TIP].y < palm_bbox['min_y'] and # Middle above TOP
                calculate_distance(
                    landmarks.landmark[HandLandmark.INDEX_FINGER_TIP].x, landmarks.landmark[HandLandmark.INDEX_FINGER_TIP].y,
                    landmarks.landmark[HandLandmark.MIDDLE_FINGER_TIP].x, landmarks.landmark[HandLandmark.MIDDLE_FINGER_TIP].y
                ) > 0.1 * palm_bbox['width'] and # Spaced apart
                abs(calculate_tilt_angle(
                    landmarks.landmark[HandLandmark.WRIST].x, landmarks.landmark[HandLandmark.WRIST].y, # Wrist
                    landmarks.landmark[HandLandmark.MIDDLE_FINGER_PIP].x, landmarks.landmark[HandLandmark.MIDDLE_FINGER_PIP].y # Middle PIP
                )) > 15 # Tilted
            )
        },
        "ESC": {
            "description": "Thumbs down.",
            "validation": lambda landmarks, palm_bbox: (
                not is_finger_in_palm_bbox(landmarks, HandLandmark.THUMB_TIP, palm_bbox) and # Thumb out
                (landmarks.landmark[HandLandmark.THUMB_TIP].y > palm_bbox['max_y'] + (palm_bbox['height'] * 0.1)) and # Thumb >10% below BOTTOM
                all(is_finger_in_palm_bbox(landmarks, tip, palm_bbox) for tip in [
                    HandLandmark.INDEX_FINGER_TIP, HandLandmark.MIDDLE_FINGER_TIP, 
                    HandLandmark.RING_FINGER_TIP, HandLandmark.PINKY_TIP
                ]) # Other fingers in palm
            )
        }
    }
}

def get_gesture_definitions():
    return GESTURE_DEFINITIONS