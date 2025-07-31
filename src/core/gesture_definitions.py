"""
Fixed gesture definitions that properly implement the README specifications
with correct signatures, validation logic, and compatibility rules.
"""

import math
from ..utils.geometry_utils import calculate_fingertip_roi, calculate_pip_joint_roi, calculate_roi_overlap, is_finger_in_palm_bbox, calculate_tilt_angle, calculate_distance, HandLandmark

# Visualizer Constants (matching README specs)
PALM_BOUNDING_BOX_POINTS = [HandLandmark.WRIST, HandLandmark.INDEX_FINGER_MCP, HandLandmark.MIDDLE_FINGER_MCP, HandLandmark.RING_FINGER_MCP, HandLandmark.PINKY_MCP]
FINGERTIP_ROI_RADIUS_PERCENT = 0.05  # 5% of Palm Bounding Box width
JOINT_ROI_RADIUS_PERCENT = 0.10  # 10% of Palm Bounding Box width

# Helper Functions (Enhanced for README compliance)

def calculate_n_axis_point(landmarks, palm_bbox):
    """Calculate N-axis point near Index MCP2 as specified in README."""
    index_mcp = landmarks.landmark[HandLandmark.INDEX_FINGER_MCP]
    return {
        'x': index_mcp.x + (palm_bbox['width'] * 0.02),  # Near, not exactly at MCP
        'y': index_mcp.y,
        'radius': palm_bbox['width'] * 0.05
    }

def calculate_palm_center(palm_bbox):
    """Calculate palm bounding box center for tilt anchor point."""
    return {
        'x': palm_bbox['center_x'],
        'y': palm_bbox['center_y']
    }

def _other_fingers_out_of_action_zone(landmarks, palm_bbox, current_tip_idx):
    """Enhanced validation for Action Control finger positioning."""
    other_tips = [HandLandmark.THUMB_TIP, HandLandmark.INDEX_FINGER_TIP, HandLandmark.MIDDLE_FINGER_TIP, HandLandmark.RING_FINGER_TIP, HandLandmark.PINKY_TIP]
    if current_tip_idx in other_tips:
        other_tips.remove(current_tip_idx)

    for tip_idx in other_tips:
        # Must be outside Palm Bounding Box
        if is_finger_in_palm_bbox(landmarks, tip_idx, palm_bbox):
            return False
        
        # For non-thumb fingers, must be outside Joint ROI
        if tip_idx != HandLandmark.THUMB_TIP:
            pip_idx = tip_idx - 2 
            if calculate_roi_overlap(
                calculate_fingertip_roi(landmarks, tip_idx, palm_bbox['width']),
                calculate_pip_joint_roi(landmarks, pip_idx, palm_bbox['width'])
            ) >= 50:
                return False
    return True

def _ring_pinky_in_palm(landmarks, palm_bbox):
    """Check if Ring and Pinky are in Palm Bounding Box (Camera Control requirement)."""
    return is_finger_in_palm_bbox(landmarks, HandLandmark.RING_FINGER_TIP, palm_bbox) and \
           is_finger_in_palm_bbox(landmarks, HandLandmark.PINKY_TIP, palm_bbox)

def _index_middle_thumb_extended(landmarks, palm_bbox):
    """Check if Index, Middle, Thumb are extended outward (Camera Control requirement)."""
    return not is_finger_in_palm_bbox(landmarks, HandLandmark.INDEX_FINGER_TIP, palm_bbox) and \
           not is_finger_in_palm_bbox(landmarks, HandLandmark.MIDDLE_FINGER_TIP, palm_bbox) and \
           not is_finger_in_palm_bbox(landmarks, HandLandmark.THUMB_TIP, palm_bbox)

def _is_peace_sign_positioned_correctly(landmarks, palm_bbox):
    """Validate peace sign positioning above Palm Bounding Box TOP."""
    return (landmarks.landmark[HandLandmark.INDEX_FINGER_TIP].y < palm_bbox['min_y'] and
            landmarks.landmark[HandLandmark.MIDDLE_FINGER_TIP].y < palm_bbox['min_y'] and
            calculate_distance(
                landmarks.landmark[HandLandmark.INDEX_FINGER_TIP].x, landmarks.landmark[HandLandmark.INDEX_FINGER_TIP].y,
                landmarks.landmark[HandLandmark.MIDDLE_FINGER_TIP].x, landmarks.landmark[HandLandmark.MIDDLE_FINGER_TIP].y
            ) > 0.1 * palm_bbox['width'])

# Fixed Gesture Definitions with proper signatures and validation
FIXED_GESTURE_DEFINITIONS = {
    "ACTION_CONTROL": {
        "NEUTRAL": {
            "description": "Palm is in a neutral position - all fingertips extended outward.",
            "validation": lambda landmarks, palm_bbox: (
                # All fingertips (TIP1-TIP5) are extended outward and not within the Palm Bounding Box
                all(not is_finger_in_palm_bbox(landmarks, tip, palm_bbox) for tip in [
                    HandLandmark.THUMB_TIP, HandLandmark.INDEX_FINGER_TIP, 
                    HandLandmark.MIDDLE_FINGER_TIP, HandLandmark.RING_FINGER_TIP, 
                    HandLandmark.PINKY_TIP
                ]) and
                # Ensure no overlap with joint ROIs for non-thumb fingers (≥50% rule)
                all(
                    calculate_roi_overlap(
                        calculate_fingertip_roi(landmarks, tip, palm_bbox['width']),
                        calculate_pip_joint_roi(landmarks, tip - 2, palm_bbox['width'])
                    ) < 50 
                    for tip in [HandLandmark.INDEX_FINGER_TIP, HandLandmark.MIDDLE_FINGER_TIP, 
                               HandLandmark.RING_FINGER_TIP, HandLandmark.PINKY_TIP]
                )
            ),
            "priority": 1
        },
        "ATTACK": {
            "description": "Thumb is within the Palm Bounding Box (LMB/Attack).",
            "validation": lambda landmarks, palm_bbox: (
                is_finger_in_palm_bbox(landmarks, HandLandmark.THUMB_TIP, palm_bbox) and
                _other_fingers_out_of_action_zone(landmarks, palm_bbox, HandLandmark.THUMB_TIP)
            ),
            "priority": 2
        },
        "SKILL_1": {
            "description": "Index finger is curled (≥50% ROI overlap).",
            "validation": lambda landmarks, palm_bbox: (
                calculate_roi_overlap(
                    calculate_fingertip_roi(landmarks, HandLandmark.INDEX_FINGER_TIP, palm_bbox['width']),
                    calculate_pip_joint_roi(landmarks, HandLandmark.INDEX_FINGER_PIP, palm_bbox['width'])
                ) >= 50 and
                not is_finger_in_palm_bbox(landmarks, HandLandmark.INDEX_FINGER_TIP, palm_bbox) and
                _other_fingers_out_of_action_zone(landmarks, palm_bbox, HandLandmark.INDEX_FINGER_TIP)
            ),
            "priority": 3
        },
        "SKILL_2": {
            "description": "Middle finger is curled (≥50% ROI overlap).",
            "validation": lambda landmarks, palm_bbox: (
                calculate_roi_overlap(
                    calculate_fingertip_roi(landmarks, HandLandmark.MIDDLE_FINGER_TIP, palm_bbox['width']),
                    calculate_pip_joint_roi(landmarks, HandLandmark.MIDDLE_FINGER_PIP, palm_bbox['width'])
                ) >= 50 and
                not is_finger_in_palm_bbox(landmarks, HandLandmark.MIDDLE_FINGER_TIP, palm_bbox) and
                _other_fingers_out_of_action_zone(landmarks, palm_bbox, HandLandmark.MIDDLE_FINGER_TIP)
            ),
            "priority": 4
        },
        "SKILL_3": {
            "description": "Ring finger is curled (≥50% ROI overlap).",
            "validation": lambda landmarks, palm_bbox: (
                calculate_roi_overlap(
                    calculate_fingertip_roi(landmarks, HandLandmark.RING_FINGER_TIP, palm_bbox['width']),
                    calculate_pip_joint_roi(landmarks, HandLandmark.RING_FINGER_PIP, palm_bbox['width'])
                ) >= 50 and
                not is_finger_in_palm_bbox(landmarks, HandLandmark.RING_FINGER_TIP, palm_bbox) and
                _other_fingers_out_of_action_zone(landmarks, palm_bbox, HandLandmark.RING_FINGER_TIP)
            ),
            "priority": 5
        },
        "UTILITY": {
            "description": "Pinky finger is curled (≥50% ROI overlap).",
            "validation": lambda landmarks, palm_bbox: (
                calculate_roi_overlap(
                    calculate_fingertip_roi(landmarks, HandLandmark.PINKY_TIP, palm_bbox['width']),
                    calculate_pip_joint_roi(landmarks, HandLandmark.PINKY_PIP, palm_bbox['width'])
                ) >= 50 and
                not is_finger_in_palm_bbox(landmarks, HandLandmark.PINKY_TIP, palm_bbox) and
                _other_fingers_out_of_action_zone(landmarks, palm_bbox, HandLandmark.PINKY_TIP)
            ),
            "priority": 6
        }
    },
    
    "MOVEMENT_CONTROL": {
        "NEUTRAL": {
            "description": "Ring finger is within the Palm Bounding Box or fist gesture.",
            "validation": lambda landmarks, palm_bbox, neutral_area, neutral_distances: (
                is_finger_in_palm_bbox(landmarks, HandLandmark.RING_FINGER_TIP, palm_bbox) or
                # Fist gesture - all fingertips within palm bbox
                all(is_finger_in_palm_bbox(landmarks, tip, palm_bbox) for tip in [
                    HandLandmark.THUMB_TIP, HandLandmark.INDEX_FINGER_TIP, 
                    HandLandmark.MIDDLE_FINGER_TIP, HandLandmark.RING_FINGER_TIP, 
                    HandLandmark.PINKY_TIP
                ])
            ),
            "priority": 1
        },
        "FORWARD": {
            "description": "Hand moves closer to camera (>10% palm area increase).",
            "validation": lambda landmarks, palm_bbox, neutral_area, neutral_distances: (
                is_finger_in_palm_bbox(landmarks, HandLandmark.RING_FINGER_TIP, palm_bbox) and
                (palm_bbox['width'] * palm_bbox['height']) > neutral_area * 1.1
            ),
            "priority": 2
        },
        "BACKWARD": {
            "description": "Hand moves away from camera (>10% palm area decrease).",
            "validation": lambda landmarks, palm_bbox, neutral_area, neutral_distances: (
                is_finger_in_palm_bbox(landmarks, HandLandmark.RING_FINGER_TIP, palm_bbox) and
                (palm_bbox['width'] * palm_bbox['height']) < neutral_area * 0.9
            ),
            "priority": 3
        },
        "LEFT": {
            "description": "Thumb extended outward while Ring finger in palm.",
            "validation": lambda landmarks, palm_bbox, neutral_area, neutral_distances: (
                is_finger_in_palm_bbox(landmarks, HandLandmark.RING_FINGER_TIP, palm_bbox) and
                not is_finger_in_palm_bbox(landmarks, HandLandmark.THUMB_TIP, palm_bbox) and
                # Ensure Pinky is NOT extended (would conflict with RIGHT)
                not (not is_finger_in_palm_bbox(landmarks, HandLandmark.PINKY_TIP, palm_bbox))
            ),
            "priority": 4
        },
        "RIGHT": {
            "description": "Pinky extended outward while Ring finger in palm.",
            "validation": lambda landmarks, palm_bbox, neutral_area, neutral_distances: (
                is_finger_in_palm_bbox(landmarks, HandLandmark.RING_FINGER_TIP, palm_bbox) and
                not is_finger_in_palm_bbox(landmarks, HandLandmark.PINKY_TIP, palm_bbox) and
                # Ensure Thumb is NOT extended (would conflict with LEFT)
                not (not is_finger_in_palm_bbox(landmarks, HandLandmark.THUMB_TIP, palm_bbox))
            ),
            "priority": 5
        },
        "SHIFT": {
            "description": "Index finger raised and curled while Ring finger in palm.",
            "validation": lambda landmarks, palm_bbox, neutral_area, neutral_distances: (
                calculate_roi_overlap(
                    calculate_fingertip_roi(landmarks, HandLandmark.INDEX_FINGER_TIP, palm_bbox['width']),
                    calculate_pip_joint_roi(landmarks, HandLandmark.INDEX_FINGER_PIP, palm_bbox['width'])
                ) >= 50 and
                not is_finger_in_palm_bbox(landmarks, HandLandmark.INDEX_FINGER_TIP, palm_bbox) and
                is_finger_in_palm_bbox(landmarks, HandLandmark.RING_FINGER_TIP, palm_bbox)
            ),
            "priority": 6
        },
        "JUMP": {
            "description": "Thumb and Pinky extended with hand tilted backward.",
            "validation": lambda landmarks, palm_bbox, neutral_area, neutral_distances: (
                # Both Thumb and Pinky extended
                not is_finger_in_palm_bbox(landmarks, HandLandmark.THUMB_TIP, palm_bbox) and
                not is_finger_in_palm_bbox(landmarks, HandLandmark.PINKY_TIP, palm_bbox) and
                # Tilt calculation: Palm center to Middle PIP distance decreases >10%
                neutral_distances is not None and 'tilt_dist' in neutral_distances and
                calculate_distance(
                    palm_bbox['center_x'], palm_bbox['center_y'], 
                    landmarks.landmark[HandLandmark.MIDDLE_FINGER_PIP].x, 
                    landmarks.landmark[HandLandmark.MIDDLE_FINGER_PIP].y
                ) < neutral_distances['tilt_dist'] * 0.9
            ),
            "priority": 7
        }
    },
    
    "CAMERA_CONTROL": {
        "NEUTRAL": {
            "description": "3-axis formation stable with Ring/Pinky in palm, Index/Middle/Thumb extended.",
            "validation": lambda landmarks, palm_bbox, neutral_distances: (
                _ring_pinky_in_palm(landmarks, palm_bbox) and
                _index_middle_thumb_extended(landmarks, palm_bbox)
            ),
            "priority": 1
        },
        "PAN_UP": {
            "description": "Y-axis decreases >10%, X-axis increases >10%, Z-axis stable ±10%.",
            "validation": lambda landmarks, palm_bbox, neutral_distances: (
                _ring_pinky_in_palm(landmarks, palm_bbox) and
                _index_middle_thumb_extended(landmarks, palm_bbox) and
                neutral_distances is not None and
                # Y-axis (Index to N-point) decreases >10%
                calculate_distance(
                    landmarks.landmark[HandLandmark.INDEX_FINGER_TIP].x, landmarks.landmark[HandLandmark.INDEX_FINGER_TIP].y,
                    landmarks.landmark[HandLandmark.INDEX_FINGER_MCP].x, landmarks.landmark[HandLandmark.INDEX_FINGER_MCP].y
                ) < neutral_distances.get('y_dist', 0) * 0.9 and
                # X-axis (Middle to N-point) increases >10%
                calculate_distance(
                    landmarks.landmark[HandLandmark.MIDDLE_FINGER_TIP].x, landmarks.landmark[HandLandmark.MIDDLE_FINGER_TIP].y,
                    landmarks.landmark[HandLandmark.INDEX_FINGER_MCP].x, landmarks.landmark[HandLandmark.INDEX_FINGER_MCP].y
                ) > neutral_distances.get('x_dist', 0) * 1.1 and
                # Z-axis (Thumb to N-point) remains within ±10%
                abs(calculate_distance(
                    landmarks.landmark[HandLandmark.THUMB_TIP].x, landmarks.landmark[HandLandmark.THUMB_TIP].y,
                    landmarks.landmark[HandLandmark.INDEX_FINGER_MCP].x, landmarks.landmark[HandLandmark.INDEX_FINGER_MCP].y
                ) - neutral_distances.get('z_dist', 0)) < neutral_distances.get('z_dist', 0) * 0.1
            ),
            "priority": 2
        },
        "PAN_DOWN": {
            "description": "Y-axis increases >10%, X-axis decreases >10%, Z-axis stable ±10%.",
            "validation": lambda landmarks, palm_bbox, neutral_distances: (
                _ring_pinky_in_palm(landmarks, palm_bbox) and
                _index_middle_thumb_extended(landmarks, palm_bbox) and
                neutral_distances is not None and
                # Y-axis increases >10%
                calculate_distance(
                    landmarks.landmark[HandLandmark.INDEX_FINGER_TIP].x, landmarks.landmark[HandLandmark.INDEX_FINGER_TIP].y,
                    landmarks.landmark[HandLandmark.INDEX_FINGER_MCP].x, landmarks.landmark[HandLandmark.INDEX_FINGER_MCP].y
                ) > neutral_distances.get('y_dist', 0) * 1.1 and
                # X-axis decreases >10%
                calculate_distance(
                    landmarks.landmark[HandLandmark.MIDDLE_FINGER_TIP].x, landmarks.landmark[HandLandmark.MIDDLE_FINGER_TIP].y,
                    landmarks.landmark[HandLandmark.INDEX_FINGER_MCP].x, landmarks.landmark[HandLandmark.INDEX_FINGER_MCP].y
                ) < neutral_distances.get('x_dist', 0) * 0.9 and
                # Z-axis stable
                abs(calculate_distance(
                    landmarks.landmark[HandLandmark.THUMB_TIP].x, landmarks.landmark[HandLandmark.THUMB_TIP].y,
                    landmarks.landmark[HandLandmark.INDEX_FINGER_MCP].x, landmarks.landmark[HandLandmark.INDEX_FINGER_MCP].y
                ) - neutral_distances.get('z_dist', 0)) < neutral_distances.get('z_dist', 0) * 0.1
            ),
            "priority": 3
        },
        "PAN_LEFT": {
            "description": "Y-axis stable ±10%, X-axis increases >10%, Z-axis decreases >10%.",
            "validation": lambda landmarks, palm_bbox, neutral_distances: (
                _ring_pinky_in_palm(landmarks, palm_bbox) and
                _index_middle_thumb_extended(landmarks, palm_bbox) and
                neutral_distances is not None and
                # Y-axis stable
                abs(calculate_distance(
                    landmarks.landmark[HandLandmark.INDEX_FINGER_TIP].x, landmarks.landmark[HandLandmark.INDEX_FINGER_TIP].y,
                    landmarks.landmark[HandLandmark.INDEX_FINGER_MCP].x, landmarks.landmark[HandLandmark.INDEX_FINGER_MCP].y
                ) - neutral_distances.get('y_dist', 0)) < neutral_distances.get('y_dist', 0) * 0.1 and
                # X-axis increases >10%
                calculate_distance(
                    landmarks.landmark[HandLandmark.MIDDLE_FINGER_TIP].x, landmarks.landmark[HandLandmark.MIDDLE_FINGER_TIP].y,
                    landmarks.landmark[HandLandmark.INDEX_FINGER_MCP].x, landmarks.landmark[HandLandmark.INDEX_FINGER_MCP].y
                ) > neutral_distances.get('x_dist', 0) * 1.1 and
                # Z-axis decreases >10%
                calculate_distance(
                    landmarks.landmark[HandLandmark.THUMB_TIP].x, landmarks.landmark[HandLandmark.THUMB_TIP].y,
                    landmarks.landmark[HandLandmark.INDEX_FINGER_MCP].x, landmarks.landmark[HandLandmark.INDEX_FINGER_MCP].y
                ) < neutral_distances.get('z_dist', 0) * 0.9
            ),
            "priority": 4
        },
        "PAN_RIGHT": {
            "description": "Y-axis stable ±10%, X-axis decreases >10%, Z-axis increases >10%.",
            "validation": lambda landmarks, palm_bbox, neutral_distances: (
                _ring_pinky_in_palm(landmarks, palm_bbox) and
                _index_middle_thumb_extended(landmarks, palm_bbox) and
                neutral_distances is not None and
                # Y-axis stable
                abs(calculate_distance(
                    landmarks.landmark[HandLandmark.INDEX_FINGER_TIP].x, landmarks.landmark[HandLandmark.INDEX_FINGER_TIP].y,
                    landmarks.landmark[HandLandmark.INDEX_FINGER_MCP].x, landmarks.landmark[HandLandmark.INDEX_FINGER_MCP].y
                ) - neutral_distances.get('y_dist', 0)) < neutral_distances.get('y_dist', 0) * 0.1 and
                # X-axis decreases >10%
                calculate_distance(
                    landmarks.landmark[HandLandmark.MIDDLE_FINGER_TIP].x, landmarks.landmark[HandLandmark.MIDDLE_FINGER_TIP].y,
                    landmarks.landmark[HandLandmark.INDEX_FINGER_MCP].x, landmarks.landmark[HandLandmark.INDEX_FINGER_MCP].y
                ) < neutral_distances.get('x_dist', 0) * 0.9 and
                # Z-axis increases >10%
                calculate_distance(
                    landmarks.landmark[HandLandmark.THUMB_TIP].x, landmarks.landmark[HandLandmark.THUMB_TIP].y,
                    landmarks.landmark[HandLandmark.INDEX_FINGER_MCP].x, landmarks.landmark[HandLandmark.INDEX_FINGER_MCP].y
                ) > neutral_distances.get('z_dist', 0) * 1.1
            ),
            "priority": 5
        },
        "LOCK": {
            "description": "3-axis ROIs collapse into overlapping formation toward left.",
            "validation": lambda landmarks, palm_bbox, neutral_distances: (
                # Index-Middle ROI overlap
                calculate_roi_overlap(
                    calculate_fingertip_roi(landmarks, HandLandmark.INDEX_FINGER_TIP, palm_bbox['width']),
                    calculate_fingertip_roi(landmarks, HandLandmark.MIDDLE_FINGER_TIP, palm_bbox['width'])
                ) > 0 and
                # Index-Thumb ROI overlap
                calculate_roi_overlap(
                    calculate_fingertip_roi(landmarks, HandLandmark.INDEX_FINGER_TIP, palm_bbox['width']),
                    calculate_fingertip_roi(landmarks, HandLandmark.THUMB_TIP, palm_bbox['width'])
                ) > 0 and
                # Extended toward Palm Bounding Box - LEFT
                landmarks.landmark[HandLandmark.INDEX_FINGER_TIP].x < palm_bbox['min_x']
            ),
            "priority": 6
        }
    },
    
    "NAVIGATION_CONTROL": {
        "NEUTRAL": {
            "description": "Open palm - all fingertips extended, no ROI overlaps.",
            "validation": lambda landmarks, palm_bbox: (
                # All fingertips outside Palm Bounding Box
                all(not is_finger_in_palm_bbox(landmarks, tip, palm_bbox) for tip in [
                    HandLandmark.THUMB_TIP, HandLandmark.INDEX_FINGER_TIP, 
                    HandLandmark.MIDDLE_FINGER_TIP, HandLandmark.RING_FINGER_TIP, 
                    HandLandmark.PINKY_TIP
                ]) and
                # No Joint ROI overlaps for non-thumb fingers
                all(
                    calculate_roi_overlap(
                        calculate_fingertip_roi(landmarks, tip, palm_bbox['width']),
                        calculate_pip_joint_roi(landmarks, tip - 2, palm_bbox['width'])
                    ) < 50 
                    for tip in [HandLandmark.INDEX_FINGER_TIP, HandLandmark.MIDDLE_FINGER_TIP, 
                               HandLandmark.RING_FINGER_TIP, HandLandmark.PINKY_TIP]
                )
            ),
            "priority": 1
        },
        "OK": {
            "description": "Peace sign - Index/Middle above TOP, Thumb/Ring/Pinky in palm.",
            "validation": lambda landmarks, palm_bbox: (
                # Index and Middle extended and positioned above TOP
                not is_finger_in_palm_bbox(landmarks, HandLandmark.INDEX_FINGER_TIP, palm_bbox) and
                not is_finger_in_palm_bbox(landmarks, HandLandmark.MIDDLE_FINGER_TIP, palm_bbox) and
                # Thumb, Ring, Pinky within palm
                is_finger_in_palm_bbox(landmarks, HandLandmark.THUMB_TIP, palm_bbox) and
                is_finger_in_palm_bbox(landmarks, HandLandmark.RING_FINGER_TIP, palm_bbox) and
                is_finger_in_palm_bbox(landmarks, HandLandmark.PINKY_TIP, palm_bbox) and
                # Correct positioning and spacing
                _is_peace_sign_positioned_correctly(landmarks, palm_bbox)
            ),
            "priority": 2
        },
        "F": {
            "description": "Tilted peace sign - Peace sign with >15° tilt from vertical.",
            "validation": lambda landmarks, palm_bbox: (
                # Basic peace sign requirements
                not is_finger_in_palm_bbox(landmarks, HandLandmark.INDEX_FINGER_TIP, palm_bbox) and
                not is_finger_in_palm_bbox(landmarks, HandLandmark.MIDDLE_FINGER_TIP, palm_bbox) and
                is_finger_in_palm_bbox(landmarks, HandLandmark.THUMB_TIP, palm_bbox) and
                is_finger_in_palm_bbox(landmarks, HandLandmark.RING_FINGER_TIP, palm_bbox) and
                is_finger_in_palm_bbox(landmarks, HandLandmark.PINKY_TIP, palm_bbox) and
                _is_peace_sign_positioned_correctly(landmarks, palm_bbox) and
                # Tilt requirement: >15° deviation from vertical
                abs(calculate_tilt_angle(
                    landmarks.landmark[HandLandmark.WRIST].x, landmarks.landmark[HandLandmark.WRIST].y,
                    landmarks.landmark[HandLandmark.MIDDLE_FINGER_PIP].x, landmarks.landmark[HandLandmark.MIDDLE_FINGER_PIP].y
                )) > 15
            ),
            "priority": 3
        },
        "ESC": {
            "description": "Thumbs down - Thumb >10% below BOTTOM, other fingers in palm.",
            "validation": lambda landmarks, palm_bbox: (
                # Thumb extended downward and positioned below BOTTOM
                not is_finger_in_palm_bbox(landmarks, HandLandmark.THUMB_TIP, palm_bbox) and
                landmarks.landmark[HandLandmark.THUMB_TIP].y > palm_bbox['max_y'] + (palm_bbox['height'] * 0.1) and
                # All other fingers within palm
                all(is_finger_in_palm_bbox(landmarks, tip, palm_bbox) for tip in [
                    HandLandmark.INDEX_FINGER_TIP, HandLandmark.MIDDLE_FINGER_TIP, 
                    HandLandmark.RING_FINGER_TIP, HandLandmark.PINKY_TIP
                ])
            ),
            "priority": 4
        }
    }
}

def get_fixed_gesture_definitions():
    """Return the corrected gesture definitions that properly implement README specs."""
    return FIXED_GESTURE_DEFINITIONS
