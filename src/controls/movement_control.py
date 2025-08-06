from ..core.gesture_definitions import get_fixed_gesture_definitions
from ..core.config_manager import get_controls_config
import numpy as np

class MovementController:
    """
    Enhanced movement controller with depth-based forward/backward detection
    using Palm Bounding Box (PBB) deformations.
    """
    
    def __init__(self):
        # Load configuration
        self.config = get_controls_config().get("MovementControl", {})
        self.enabled = self.config.get("enabled", True)
        
        # Get enabled gestures from config
        self.enabled_gestures = {}
        if "gestures" in self.config:
            for gesture in self.config["gestures"]:
                self.enabled_gestures[gesture["name"]] = gesture.get("enabled", True)
        
        # Calibration for depth-based movement detection
        self.neutral_area = None
        self.calibration_samples = []
        self.calibration_complete = False
        self.sample_count = 0
        self.required_samples = 30  # Samples needed for calibration
        
        # Depth detection thresholds (author-calibrated)
        self.forward_threshold = 1.15   # 15% larger area = forward
        self.backward_threshold = 0.85  # 15% smaller area = backward  
        self.deadzone_multiplier = 0.05 # 5% deadzone around neutral
        
        # Smoothing for area calculations
        self.area_history = []
        self.history_size = 5
        
        # State tracking for hysteresis deadzone
        self.last_movement_state = "NEUTRAL"
        
    def calibrate_neutral_area(self, palm_bbox):
        """
        Calibrate the neutral palm area by sampling during rest position.
        Call this when hand is in neutral position for stable calibration.
        """
        current_area = palm_bbox['width'] * palm_bbox['height']
        
        # Only accept reasonable palm areas for calibration
        if 0.01 < current_area < 0.5:  # Reasonable palm area range
            self.calibration_samples.append(current_area)
            self.sample_count += 1
            
            if self.sample_count >= self.required_samples:
                # Calculate neutral area as median of samples (more robust than mean)
                self.neutral_area = np.median(self.calibration_samples)
                self.calibration_complete = True
                print(f"Movement calibration complete! Neutral area: {self.neutral_area:.4f}")
                return True
        
        return False
    
    def get_smoothed_area(self, palm_bbox):
        """Get smoothed palm area using rolling average."""
        current_area = palm_bbox['width'] * palm_bbox['height']
        
        # Add to history
        self.area_history.append(current_area)
        if len(self.area_history) > self.history_size:
            self.area_history.pop(0)
        
        # Return smoothed area
        return np.mean(self.area_history)
    
    def detect_depth_movement(self, palm_bbox):
        """
        Detect forward/backward movement based on PBB size changes.
        Returns: 'FORWARD', 'BACKWARD', or 'NEUTRAL'
        
        Enhanced deadzone logic with hysteresis:
        - Primary thresholds: 1.15 (forward) and 0.85 (backward)
        - Hysteresis deadzone prevents oscillation at boundaries
        - Once in FORWARD/BACKWARD, need to cross return threshold to go back to NEUTRAL
        """
        if not self.calibration_complete or self.neutral_area is None:
            return 'NEUTRAL'
        
        smoothed_area = self.get_smoothed_area(palm_bbox)
        area_ratio = smoothed_area / self.neutral_area
        
        # Calculate hysteresis thresholds
        forward_enter = self.forward_threshold
        forward_exit = self.forward_threshold - self.deadzone_multiplier
        backward_enter = self.backward_threshold
        backward_exit = self.backward_threshold + self.deadzone_multiplier
        
        # State machine with hysteresis deadzone
        if self.last_movement_state == "NEUTRAL":
            # From neutral, need to cross main thresholds
            if area_ratio >= forward_enter:
                self.last_movement_state = "FORWARD"
                return 'FORWARD'
            elif area_ratio <= backward_enter:
                self.last_movement_state = "BACKWARD"
                return 'BACKWARD'
            else:
                return 'NEUTRAL'
                
        elif self.last_movement_state == "FORWARD":
            # From forward, need to drop below exit threshold to return to neutral
            if area_ratio >= forward_exit:
                return 'FORWARD'  # Stay in forward
            else:
                self.last_movement_state = "NEUTRAL"
                # Check if we've crossed into backward territory
                if area_ratio <= backward_enter:
                    self.last_movement_state = "BACKWARD"
                    return 'BACKWARD'
                return 'NEUTRAL'
                
        elif self.last_movement_state == "BACKWARD":
            # From backward, need to rise above exit threshold to return to neutral  
            if area_ratio <= backward_exit:
                return 'BACKWARD'  # Stay in backward
            else:
                self.last_movement_state = "NEUTRAL"
                # Check if we've crossed into forward territory
                if area_ratio >= forward_enter:
                    self.last_movement_state = "FORWARD"
                    return 'FORWARD'
                return 'NEUTRAL'
        
        # Default fallback
        self.last_movement_state = "NEUTRAL"
        return 'NEUTRAL'
    
    def is_ring_finger_in_palm_numpy(self, landmarks_array, palm_bbox):
        """
        Check if ring finger is in palm using numpy array format.
        landmarks_array is numpy array with shape (21, 3) where each row is [x, y, z]
        """
        try:
            # HandLandmark.RING_FINGER_TIP = 16
            ring_finger_tip = landmarks_array[16]  # [x, y, z]
            tip_x, tip_y = ring_finger_tip[0], ring_finger_tip[1]
            
            # Check if tip is within palm bounding box
            return (palm_bbox['min_x'] <= tip_x <= palm_bbox['max_x'] and
                    palm_bbox['min_y'] <= tip_y <= palm_bbox['max_y'])
        except (IndexError, KeyError) as e:
            print(f"Error checking ring finger position: {e}")
            return False
    
    def is_gesture_enabled(self, gesture_name):
        """Check if a specific gesture is enabled in config."""
        if not self.enabled:
            return False
        return self.enabled_gestures.get(gesture_name, True)
    
    def determine_movement_status(self, landmarks, palm_bbox):
        """
        Determines the movement status with enhanced depth detection.
        Handles both MediaPipe landmark objects and numpy arrays.
        Respects config-based gesture enabling/disabling.
        """
        try:
            # Check if movement control is enabled
            if not self.enabled:
                return "NEUTRAL"
            
            # Handle different landmark formats
            if hasattr(landmarks, 'landmark'):
                # MediaPipe landmark object format
                landmarks_array = np.array([[lm.x, lm.y, lm.z] for lm in landmarks.landmark])
            elif isinstance(landmarks, np.ndarray):
                # Already numpy array format
                landmarks_array = landmarks
            else:
                print(f"Error: Unknown landmarks format: {type(landmarks)}")
                return "NEUTRAL"
            
            # Check if we need calibration (when hand appears to be in neutral position)
            if not self.calibration_complete:
                # Attempt calibration if ring finger is in palm (neutral indicator)
                if self.is_ring_finger_in_palm_numpy(landmarks_array, palm_bbox):
                    self.calibrate_neutral_area(palm_bbox)
            
            # Get depth-based movement first (if enabled)
            if self.is_gesture_enabled("FORWARD") or self.is_gesture_enabled("BACKWARD"):
                depth_movement = self.detect_depth_movement(palm_bbox)
                
                # For FORWARD/BACKWARD, use our depth detection
                if depth_movement == "FORWARD" and self.is_gesture_enabled("FORWARD"):
                    return "FORWARD"
                elif depth_movement == "BACKWARD" and self.is_gesture_enabled("BACKWARD"):
                    return "BACKWARD"
            
            # For other movements, check traditional gestures using numpy array
            movement_definitions = get_fixed_gesture_definitions()["MOVEMENT_CONTROL"]
            
            # Check LEFT (thumb extended) - if enabled
            if self.is_gesture_enabled("LEFT") and self._check_thumb_extended_numpy(landmarks_array, palm_bbox):
                return "LEFT"
            
            # Check RIGHT (pinky extended) - if enabled
            if self.is_gesture_enabled("RIGHT") and self._check_pinky_extended_numpy(landmarks_array, palm_bbox):
                return "RIGHT"
            
            # Check SHIFT (index finger curled) - if enabled
            if self.is_gesture_enabled("SHIFT") and self._check_index_curled_numpy(landmarks_array, palm_bbox):
                return "SHIFT"
            
            # Check JUMP (thumb and pinky extended with tilt) - if enabled
            if self.is_gesture_enabled("JUMP") and self._check_jump_gesture_numpy(landmarks_array, palm_bbox):
                return "JUMP"
            
            return "NEUTRAL"
            
        except Exception as e:
            print(f"Error processing movement: {e}")
            return "NEUTRAL"
    
    def _check_thumb_extended_numpy(self, landmarks_array, palm_bbox):
        """Check if thumb is extended (LEFT movement)"""
        try:
            # HandLandmark.THUMB_TIP = 4, RING_FINGER_TIP = 16, PINKY_TIP = 20
            thumb_tip = landmarks_array[4]
            ring_tip = landmarks_array[16] 
            pinky_tip = landmarks_array[20]
            
            # Thumb should be outside palm, ring finger inside, pinky inside
            thumb_outside = not (palm_bbox['min_x'] <= thumb_tip[0] <= palm_bbox['max_x'] and
                               palm_bbox['min_y'] <= thumb_tip[1] <= palm_bbox['max_y'])
            ring_inside = (palm_bbox['min_x'] <= ring_tip[0] <= palm_bbox['max_x'] and
                          palm_bbox['min_y'] <= ring_tip[1] <= palm_bbox['max_y'])
            pinky_inside = (palm_bbox['min_x'] <= pinky_tip[0] <= palm_bbox['max_x'] and
                           palm_bbox['min_y'] <= pinky_tip[1] <= palm_bbox['max_y'])
            
            return thumb_outside and ring_inside and pinky_inside
        except (IndexError, KeyError):
            return False
    
    def _check_pinky_extended_numpy(self, landmarks_array, palm_bbox):
        """Check if pinky is extended (RIGHT movement)"""
        try:
            # HandLandmark.PINKY_TIP = 20, RING_FINGER_TIP = 16, THUMB_TIP = 4
            pinky_tip = landmarks_array[20]
            ring_tip = landmarks_array[16]
            thumb_tip = landmarks_array[4]
            
            # Pinky should be outside palm, ring finger inside, thumb inside
            pinky_outside = not (palm_bbox['min_x'] <= pinky_tip[0] <= palm_bbox['max_x'] and
                               palm_bbox['min_y'] <= pinky_tip[1] <= palm_bbox['max_y'])
            ring_inside = (palm_bbox['min_x'] <= ring_tip[0] <= palm_bbox['max_x'] and
                          palm_bbox['min_y'] <= ring_tip[1] <= palm_bbox['max_y'])
            thumb_inside = (palm_bbox['min_x'] <= thumb_tip[0] <= palm_bbox['max_x'] and
                           palm_bbox['min_y'] <= thumb_tip[1] <= palm_bbox['max_y'])
            
            return pinky_outside and ring_inside and thumb_inside
        except (IndexError, KeyError):
            return False
    
    def _check_index_curled_numpy(self, landmarks_array, palm_bbox):
        """Check if index finger is curled (SHIFT)"""
        try:
            # HandLandmark.INDEX_FINGER_TIP = 8
            index_tip = landmarks_array[8]
            
            # Index finger should be inside palm
            index_inside = (palm_bbox['min_x'] <= index_tip[0] <= palm_bbox['max_x'] and
                           palm_bbox['min_y'] <= index_tip[1] <= palm_bbox['max_y'])
            
            return index_inside
        except (IndexError, KeyError):
            return False
    
    def _check_jump_gesture_numpy(self, landmarks_array, palm_bbox):
        """Check for jump gesture (thumb and pinky extended with tilt)"""
        try:
            # HandLandmark.THUMB_TIP = 4, PINKY_TIP = 20
            thumb_tip = landmarks_array[4]
            pinky_tip = landmarks_array[20]
            
            # Both thumb and pinky should be outside palm
            thumb_outside = not (palm_bbox['min_x'] <= thumb_tip[0] <= palm_bbox['max_x'] and
                               palm_bbox['min_y'] <= thumb_tip[1] <= palm_bbox['max_y'])
            pinky_outside = not (palm_bbox['min_x'] <= pinky_tip[0] <= palm_bbox['max_x'] and
                               palm_bbox['min_y'] <= pinky_tip[1] <= palm_bbox['max_y'])
            
            # Simple tilt check: if thumb and pinky are both extended, likely jump gesture
            return thumb_outside and pinky_outside
        except (IndexError, KeyError):
            return False

# Global controller instance
_movement_controller = MovementController()

def determine_movement_status(landmarks, palm_bbox):
    """
    Legacy interface for compatibility.
    Uses enhanced movement controller with depth detection.
    """
    return _movement_controller.determine_movement_status(landmarks, palm_bbox)

def get_movement_controller():
    """Get the movement controller instance for manual calibration."""
    return _movement_controller