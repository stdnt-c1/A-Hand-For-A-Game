"""
Fixed gesture determinators with proper validation ordering,
exclusivity checks, and README-compliant logic.
"""

from .gesture_definitions import get_fixed_gesture_definitions

class GestureCompatibilityValidator:
    """
    Validates gesture compatibility according to README specifications.
    Implements the detailed compatibility matrix and exclusivity rules.
    """
    
    def __init__(self):
        # Compatibility matrix from README
        self.compatibility_rules = {
            # ACTION_CONTROL compatibility
            ("ACTION", "NEUTRAL"): {
                "can_coexist": [("MOVEMENT", "FORWARD"), ("MOVEMENT", "BACKWARD"), 
                              ("MOVEMENT", "LEFT"), ("MOVEMENT", "RIGHT"), ("MOVEMENT", "JUMP"),
                              ("NAVIGATION", "NEUTRAL")],
                "cannot_coexist": [("ACTION", "*"), ("CAMERA", "*"), ("NAVIGATION", "OK"), 
                                 ("NAVIGATION", "F"), ("NAVIGATION", "ESC")]
            },
            ("ACTION", "ATTACK"): {
                "can_coexist": [("MOVEMENT", "FORWARD"), ("MOVEMENT", "BACKWARD"), ("MOVEMENT", "SHIFT")],
                "cannot_coexist": [("ACTION", "*"), ("CAMERA", "*"), ("MOVEMENT", "LEFT"), 
                                 ("MOVEMENT", "RIGHT"), ("MOVEMENT", "JUMP"), ("NAVIGATION", "*")]
            },
            
            # MOVEMENT_CONTROL compatibility  
            ("MOVEMENT", "NEUTRAL"): {
                "can_coexist": [("ACTION", "NEUTRAL"), ("ACTION", "ATTACK"), ("ACTION", "SKILL_1"),
                              ("ACTION", "SKILL_2"), ("ACTION", "SKILL_3"), ("ACTION", "UTILITY"),
                              ("NAVIGATION", "NEUTRAL")],
                "cannot_coexist": [("MOVEMENT", "*"), ("CAMERA", "*"), ("NAVIGATION", "OK"),
                                 ("NAVIGATION", "F"), ("NAVIGATION", "ESC")]
            },
            
            # CAMERA_CONTROL compatibility
            ("CAMERA", "NEUTRAL"): {
                "can_coexist": [("MOVEMENT", "FORWARD"), ("MOVEMENT", "BACKWARD")],
                "cannot_coexist": [("ACTION", "*"), ("CAMERA", "*"), ("MOVEMENT", "LEFT"),
                                 ("MOVEMENT", "RIGHT"), ("MOVEMENT", "SHIFT"), ("MOVEMENT", "JUMP"),
                                 ("NAVIGATION", "*")]
            },
            
            # NAVIGATION_CONTROL compatibility (highest priority - excludes most others)
            ("NAVIGATION", "OK"): {
                "can_coexist": [],
                "cannot_coexist": [("*", "*")]  # Excludes all others
            },
            ("NAVIGATION", "F"): {
                "can_coexist": [],
                "cannot_coexist": [("*", "*")]  # Excludes all others
            },
            ("NAVIGATION", "ESC"): {
                "can_coexist": [],
                "cannot_coexist": [("*", "*")]  # Excludes all others
            }
        }
    
    def validate_gesture_combination(self, detected_gestures):
        """
        Validate if detected gesture combination is allowed per README rules.
        Returns the highest priority valid gesture.
        """
        # Priority order: Navigation > Camera > Movement > Action
        priority_order = ["NAVIGATION", "CAMERA", "MOVEMENT", "ACTION"]
        
        # Find highest priority gesture
        for gesture_type in priority_order:
            if gesture_type in detected_gestures and detected_gestures[gesture_type] != "NEUTRAL":
                gesture_name = detected_gestures[gesture_type]
                
                # Check if this gesture conflicts with any others
                if self._has_conflicts(gesture_type, gesture_name, detected_gestures):
                    continue  # Skip conflicting gesture
                
                return gesture_type, gesture_name
        
        # If no specific gestures, return neutral state
        return "ACTION", "NEUTRAL"  # Default to action neutral
    
    def _has_conflicts(self, gesture_type, gesture_name, all_detected):
        """Check if a gesture conflicts with any other detected gestures."""
        key = (gesture_type, gesture_name)
        
        if key not in self.compatibility_rules:
            return False  # No specific rules = no conflicts
        
        rules = self.compatibility_rules[key]
        
        # Check cannot_coexist rules
        for conflict_type, conflict_name in rules["cannot_coexist"]:
            if conflict_type == "*":  # Conflicts with everything
                return len([g for g in all_detected.values() if g != "NEUTRAL"]) > 1
            
            if conflict_name == "*":  # Conflicts with any gesture of this type
                if conflict_type in all_detected and all_detected[conflict_type] != "NEUTRAL":
                    return True
            else:  # Specific gesture conflict
                if (conflict_type in all_detected and 
                    all_detected[conflict_type] == conflict_name):
                    return True
        
        return False

class OrderedGestureDeterminator:
    """
    Enhanced gesture determinator that validates gestures in proper order
    and enforces compatibility rules from README.
    """
    
    def __init__(self):
        self.validator = GestureCompatibilityValidator()
        self.gesture_definitions = get_fixed_gesture_definitions()
        
        # Validation order by computational complexity (simplest first)
        self.validation_order = {
            "ACTION_CONTROL": ["NEUTRAL", "ATTACK", "SKILL_1", "SKILL_2", "SKILL_3", "UTILITY"],
            "MOVEMENT_CONTROL": ["NEUTRAL", "LEFT", "RIGHT", "FORWARD", "BACKWARD", "SHIFT", "JUMP"],
            "CAMERA_CONTROL": ["NEUTRAL", "LOCK", "PAN_LEFT", "PAN_RIGHT", "PAN_UP", "PAN_DOWN"],
            "NAVIGATION_CONTROL": ["NEUTRAL", "ESC", "OK", "F"]
        }
    
    def determine_action_status(self, landmarks, palm_bbox):
        """Enhanced action status determination with proper ordering."""
        action_definitions = self.gesture_definitions["ACTION_CONTROL"]
        
        # Validate in order of complexity
        for gesture_name in self.validation_order["ACTION_CONTROL"]:
            if gesture_name in action_definitions:
                definition = action_definitions[gesture_name]
                try:
                    if definition["validation"](landmarks, palm_bbox):
                        return gesture_name
                except Exception as e:
                    # Skip gesture if validation fails
                    continue
        
        return "NEUTRAL"
    
    def determine_movement_status(self, landmarks, palm_bbox, neutral_area, neutral_distances):
        """Enhanced movement status determination with proper parameters."""
        movement_definitions = self.gesture_definitions["MOVEMENT_CONTROL"]
        
        # Validate in order of complexity
        for gesture_name in self.validation_order["MOVEMENT_CONTROL"]:
            if gesture_name in movement_definitions:
                definition = movement_definitions[gesture_name]
                try:
                    if definition["validation"](landmarks, palm_bbox, neutral_area, neutral_distances):
                        return gesture_name
                except Exception as e:
                    # Skip gesture if validation fails
                    continue
        
        return "NEUTRAL"
    
    def determine_camera_status(self, landmarks, palm_bbox, neutral_distances):
        """Enhanced camera status determination with proper axis calculations."""
        camera_definitions = self.gesture_definitions["CAMERA_CONTROL"]
        
        # Validate in order of complexity
        for gesture_name in self.validation_order["CAMERA_CONTROL"]:
            if gesture_name in camera_definitions:
                definition = camera_definitions[gesture_name]
                try:
                    if definition["validation"](landmarks, palm_bbox, neutral_distances):
                        return gesture_name
                except Exception as e:
                    # Skip gesture if validation fails
                    continue
        
        return "NEUTRAL"
    
    def determine_navigation_status(self, landmarks, palm_bbox):
        """Enhanced navigation status determination with proper positioning checks."""
        navigation_definitions = self.gesture_definitions["NAVIGATION_CONTROL"]
        
        # Validate in order of complexity
        for gesture_name in self.validation_order["NAVIGATION_CONTROL"]:
            if gesture_name in navigation_definitions:
                definition = navigation_definitions[gesture_name]
                try:
                    if definition["validation"](landmarks, palm_bbox):
                        return gesture_name
                except Exception as e:
                    # Skip gesture if validation fails
                    continue
        
        return "NEUTRAL"
    
    def determine_all_gestures(self, landmarks, palm_bbox, neutral_area=None, neutral_distances=None):
        """
        Determine all gesture types and return the highest priority valid combination.
        This is the main method that should be used for gesture recognition.
        """
        # Detect all possible gestures
        detected_gestures = {
            "ACTION": self.determine_action_status(landmarks, palm_bbox),
            "MOVEMENT": self.determine_movement_status(landmarks, palm_bbox, neutral_area, neutral_distances),
            "CAMERA": self.determine_camera_status(landmarks, palm_bbox, neutral_distances),
            "NAVIGATION": self.determine_navigation_status(landmarks, palm_bbox)
        }
        
        # Validate compatibility and return highest priority gesture
        gesture_type, gesture_name = self.validator.validate_gesture_combination(detected_gestures)
        
        # Return all statuses with priority-resolved active gesture
        result = {
            "movement_status": "NEUTRAL",
            "action_status": "NEUTRAL", 
            "camera_status": "NEUTRAL",
            "navigation_status": "NEUTRAL",
            "active_gesture_type": gesture_type,
            "active_gesture_name": gesture_name
        }
        
        # Set the active gesture
        if gesture_type == "ACTION":
            result["action_status"] = gesture_name
        elif gesture_type == "MOVEMENT":
            result["movement_status"] = gesture_name
        elif gesture_type == "CAMERA":
            result["camera_status"] = gesture_name
        elif gesture_type == "NAVIGATION":
            result["navigation_status"] = gesture_name
        
        return result

# Global instance for backward compatibility
_determinator = OrderedGestureDeterminator()

# Fixed individual functions for existing code compatibility
def determine_action_status(landmarks, palm_bbox):
    return _determinator.determine_action_status(landmarks, palm_bbox)

def determine_movement_status(landmarks, palm_bbox, neutral_area, neutral_distances):
    return _determinator.determine_movement_status(landmarks, palm_bbox, neutral_area, neutral_distances)

def determine_camera_status(landmarks, palm_bbox, neutral_distances):
    return _determinator.determine_camera_status(landmarks, palm_bbox, neutral_distances)

def determine_navigation_status(landmarks, palm_bbox):
    return _determinator.determine_navigation_status(landmarks, palm_bbox)
