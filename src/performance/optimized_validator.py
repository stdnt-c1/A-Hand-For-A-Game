import numpy as np
from numba import jit, njit
import math
from ..utils.geometry_utils import HandLandmark

# Optimized geometric calculations using Numba JIT compilation
@njit
def fast_distance(p1_x, p1_y, p2_x, p2_y):
    """Fast distance calculation using Numba."""
    return math.sqrt((p1_x - p2_x)**2 + (p1_y - p2_y)**2)

@njit
def fast_roi_overlap(roi1_x, roi1_y, roi1_r, roi2_x, roi2_y, roi2_r):
    """Fast ROI overlap calculation using Numba."""
    dist = fast_distance(roi1_x, roi1_y, roi2_x, roi2_y)
    r1, r2 = roi1_r, roi2_r
    
    if dist >= r1 + r2:
        return 0.0
    
    if dist <= abs(r1 - r2):
        smaller_roi_area = math.pi * min(r1, r2)**2
        return 100.0 if smaller_roi_area > 0 else 0.0
    
    r1_sq, r2_sq = r1**2, r2**2
    dist_sq = dist**2
    
    angle1 = math.acos((dist_sq + r1_sq - r2_sq) / (2 * dist * r1))
    angle2 = math.acos((dist_sq + r2_sq - r1_sq) / (2 * dist * r2))
    
    intersection_area = (r1_sq * angle1) + (r2_sq * angle2) - 0.5 * math.sqrt((-dist + r1 + r2) * (dist + r1 - r2) * (dist - r1 + r2) * (dist + r1 + r2))
    
    smaller_roi_area = math.pi * min(r1, r2)**2
    
    if smaller_roi_area == 0:
        return 0.0
    
    return (intersection_area / smaller_roi_area) * 100

@njit
def fast_bbox_check(tip_x, tip_y, min_x, max_x, min_y, max_y):
    """Fast bounding box check using Numba."""
    return min_x <= tip_x <= max_x and min_y <= tip_y <= max_y

class OptimizedGestureValidator:
    """
    Optimized gesture validation with early exit patterns and vectorized operations.
    """
    
    def __init__(self):
        self.validation_order = {
            # Order gestures by computational complexity (simplest first)
            "ACTION_CONTROL": ["NEUTRAL", "ATTACK", "SKILL_1", "SKILL_2", "SKILL_3", "UTILITY"],
            "MOVEMENT_CONTROL": ["NEUTRAL", "LEFT", "RIGHT", "FORWARD", "BACKWARD", "SHIFT", "JUMP"],
            "CAMERA_CONTROL": ["NEUTRAL", "LOCK", "PAN_LEFT", "PAN_RIGHT", "PAN_UP", "PAN_DOWN"],
            "NAVIGATION_CONTROL": ["NEUTRAL", "ESC", "OK", "F"]
        }
        
        # Pre-computed constants
        self.fingertip_roi_radius_percent = 0.05
        self.joint_roi_radius_percent = 0.10
        
    def validate_action_gesture_optimized(self, landmarks_array, palm_bbox, gesture_type):
        """Optimized action gesture validation with early exits."""
        
        # Extract coordinates as numpy arrays for vectorized operations
        thumb_tip = landmarks_array[HandLandmark.THUMB_TIP]
        index_tip = landmarks_array[HandLandmark.INDEX_FINGER_TIP]
        middle_tip = landmarks_array[HandLandmark.MIDDLE_FINGER_TIP]
        ring_tip = landmarks_array[HandLandmark.RING_FINGER_TIP]
        pinky_tip = landmarks_array[HandLandmark.PINKY_TIP]
        
        # Fast bounding box checks
        thumb_in_palm = fast_bbox_check(thumb_tip[0], thumb_tip[1], 
                                       palm_bbox['min_x'], palm_bbox['max_x'],
                                       palm_bbox['min_y'], palm_bbox['max_y'])
        
        if gesture_type == "ATTACK":
            if not thumb_in_palm:
                return False
            # Quick check: if thumb is in palm, validate other fingers are out
            other_tips = [index_tip, middle_tip, ring_tip, pinky_tip]
            for tip in other_tips:
                if fast_bbox_check(tip[0], tip[1], palm_bbox['min_x'], palm_bbox['max_x'],
                                 palm_bbox['min_y'], palm_bbox['max_y']):
                    return False
            return True
        
        elif gesture_type == "NEUTRAL":
            # All fingertips must be outside palm bbox
            all_tips = [thumb_tip, index_tip, middle_tip, ring_tip, pinky_tip]
            for tip in all_tips:
                if fast_bbox_check(tip[0], tip[1], palm_bbox['min_x'], palm_bbox['max_x'],
                                 palm_bbox['min_y'], palm_bbox['max_y']):
                    return False
            
            # Check joint ROI overlaps only if bbox check passes
            return self._check_joint_roi_overlaps_optimized(landmarks_array, palm_bbox)
        
        elif gesture_type in ["SKILL_1", "SKILL_2", "SKILL_3", "UTILITY"]:
            finger_map = {
                "SKILL_1": (HandLandmark.INDEX_FINGER_TIP, HandLandmark.INDEX_FINGER_PIP),
                "SKILL_2": (HandLandmark.MIDDLE_FINGER_TIP, HandLandmark.MIDDLE_FINGER_PIP),
                "SKILL_3": (HandLandmark.RING_FINGER_TIP, HandLandmark.RING_FINGER_PIP),
                "UTILITY": (HandLandmark.PINKY_TIP, HandLandmark.PINKY_PIP)
            }
            
            tip_idx, pip_idx = finger_map[gesture_type]
            tip_coords = landmarks_array[tip_idx]
            pip_coords = landmarks_array[pip_idx]
            
            # Quick bbox check first
            if fast_bbox_check(tip_coords[0], tip_coords[1], 
                             palm_bbox['min_x'], palm_bbox['max_x'],
                             palm_bbox['min_y'], palm_bbox['max_y']):
                return False
            
            # ROI overlap check
            fingertip_radius = self.fingertip_roi_radius_percent * palm_bbox['width']
            joint_radius = self.joint_roi_radius_percent * palm_bbox['width']
            
            overlap = fast_roi_overlap(tip_coords[0], tip_coords[1], fingertip_radius,
                                     pip_coords[0], pip_coords[1], joint_radius)
            
            return overlap >= 50.0
        
        return False
    
    def _check_joint_roi_overlaps_optimized(self, landmarks_array, palm_bbox):
        """Optimized joint ROI overlap checking."""
        fingertip_radius = self.fingertip_roi_radius_percent * palm_bbox['width']
        joint_radius = self.joint_roi_radius_percent * palm_bbox['width']
        
        finger_pairs = [
            (HandLandmark.INDEX_FINGER_TIP, HandLandmark.INDEX_FINGER_PIP),
            (HandLandmark.MIDDLE_FINGER_TIP, HandLandmark.MIDDLE_FINGER_PIP),
            (HandLandmark.RING_FINGER_TIP, HandLandmark.RING_FINGER_PIP),
            (HandLandmark.PINKY_TIP, HandLandmark.PINKY_PIP)
        ]
        
        for tip_idx, pip_idx in finger_pairs:
            tip_coords = landmarks_array[tip_idx]
            pip_coords = landmarks_array[pip_idx]
            
            overlap = fast_roi_overlap(tip_coords[0], tip_coords[1], fingertip_radius,
                                     pip_coords[0], pip_coords[1], joint_radius)
            
            if overlap >= 50.0:
                return False
        
        return True
    
    def validate_movement_gesture_optimized(self, landmarks_array, palm_bbox, neutral_area, neutral_distances, gesture_type):
        """Optimized movement gesture validation."""
        
        ring_tip = landmarks_array[HandLandmark.RING_FINGER_TIP]
        ring_in_palm = fast_bbox_check(ring_tip[0], ring_tip[1],
                                     palm_bbox['min_x'], palm_bbox['max_x'],
                                     palm_bbox['min_y'], palm_bbox['max_y'])
        
        if gesture_type == "NEUTRAL":
            return ring_in_palm or self._check_fist_gesture(landmarks_array, palm_bbox)
        
        if not ring_in_palm:
            return False  # Early exit for most movement gestures
        
        if gesture_type == "FORWARD":
            current_area = palm_bbox['width'] * palm_bbox['height']
            return current_area > neutral_area * 1.1
        
        elif gesture_type == "BACKWARD":
            current_area = palm_bbox['width'] * palm_bbox['height']
            return current_area < neutral_area * 0.9
        
        elif gesture_type == "LEFT":
            thumb_tip = landmarks_array[HandLandmark.THUMB_TIP]
            return not fast_bbox_check(thumb_tip[0], thumb_tip[1],
                                     palm_bbox['min_x'], palm_bbox['max_x'],
                                     palm_bbox['min_y'], palm_bbox['max_y'])
        
        elif gesture_type == "RIGHT":
            pinky_tip = landmarks_array[HandLandmark.PINKY_TIP]
            return not fast_bbox_check(pinky_tip[0], pinky_tip[1],
                                     palm_bbox['min_x'], palm_bbox['max_x'],
                                     palm_bbox['min_y'], palm_bbox['max_y'])
        
        # More complex gestures (SHIFT, JUMP) handled separately if needed
        return False
    
    def _check_fist_gesture(self, landmarks_array, palm_bbox):
        """Check if all fingertips are in palm (fist gesture)."""
        fingertips = [HandLandmark.THUMB_TIP, HandLandmark.INDEX_FINGER_TIP,
                     HandLandmark.MIDDLE_FINGER_TIP, HandLandmark.RING_FINGER_TIP,
                     HandLandmark.PINKY_TIP]
        
        for tip_idx in fingertips:
            tip_coords = landmarks_array[tip_idx]
            if not fast_bbox_check(tip_coords[0], tip_coords[1],
                                 palm_bbox['min_x'], palm_bbox['max_x'],
                                 palm_bbox['min_y'], palm_bbox['max_y']):
                return False
        return True
