"""
Fixed CentralLinker with consistent status checking and proper gesture routing.
"""

import json
from .gesture_determinator import OrderedGestureDeterminator

class FixedCentralLinker:
    """
    Enhanced CentralLinker that properly implements README specifications
    with consistent status checking and gesture compatibility validation.
    """
    
    def __init__(self, gesture_definitions_path=None):
        self.gesture_determinator = OrderedGestureDeterminator()
        self.gesture_definitions = None
        
        if gesture_definitions_path:
            self.gesture_definitions = self._load_gesture_definitions(gesture_definitions_path)
        
        # Gesture action handlers registry
        self.gesture_handlers = {
            "ACTION": {
                "ATTACK": self._handle_attack,
                "SKILL_1": self._handle_skill_1,
                "SKILL_2": self._handle_skill_2,
                "SKILL_3": self._handle_skill_3,
                "UTILITY": self._handle_utility
            },
            "MOVEMENT": {
                "FORWARD": self._handle_move_forward,
                "BACKWARD": self._handle_move_backward,
                "LEFT": self._handle_move_left,
                "RIGHT": self._handle_move_right,
                "SHIFT": self._handle_shift,
                "JUMP": self._handle_jump
            },
            "CAMERA": {
                "PAN_UP": self._handle_camera_pan_up,
                "PAN_DOWN": self._handle_camera_pan_down,
                "PAN_LEFT": self._handle_camera_pan_left,
                "PAN_RIGHT": self._handle_camera_pan_right,
                "LOCK": self._handle_camera_lock
            },
            "NAVIGATION": {
                "OK": self._handle_navigation_ok,
                "F": self._handle_navigation_f,
                "ESC": self._handle_navigation_esc
            }
        }
    
    def _load_gesture_definitions(self, path):
        """Load gesture definitions from JSON file."""
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load gesture definitions from {path}: {e}")
            return None
    
    def process_gestures_enhanced(self, landmarks, palm_bbox, neutral_area=None, neutral_distances=None):
        """
        Enhanced gesture processing that determines all gestures and handles compatibility.
        This replaces the old individual status-based approach.
        """
        # Determine all gestures with proper compatibility validation
        gesture_result = self.gesture_determinator.determine_all_gestures(
            landmarks, palm_bbox, neutral_area, neutral_distances
        )
        
        # Process the active gesture
        active_type = gesture_result["active_gesture_type"]
        active_name = gesture_result["active_gesture_name"]
        
        if active_name != "NEUTRAL":
            self._execute_gesture_action(active_type, active_name)
        
        return gesture_result
    
    def process_gestures(self, movement_status, action_status, camera_status, navigation_status):
        """
        Legacy method for backward compatibility.
        Fixed to use consistent "NEUTRAL" checking instead of "NONE".
        """
        # Priority Hierarchy: Navigation > Camera > Movement > Action (per README)
        
        # Navigation Control (Highest Priority)
        if navigation_status != "NEUTRAL":  # Fixed: was "NONE"
            print(f"Navigation Gesture Detected: {navigation_status}")
            self._execute_gesture_action("NAVIGATION", navigation_status)
            return
        
        # Camera Control
        if camera_status != "NEUTRAL":  # Fixed: was "NONE"
            print(f"Camera Gesture Detected: {camera_status}")
            self._execute_gesture_action("CAMERA", camera_status)
            return
        
        # Movement Control
        if movement_status != "NEUTRAL":
            print(f"Movement Gesture Detected: {movement_status}")
            self._execute_gesture_action("MOVEMENT", movement_status)
            return
        
        # Action Control (Lowest Priority)
        if action_status != "NEUTRAL":  # Fixed: was "NONE"
            print(f"Action Gesture Detected: {action_status}")
            self._execute_gesture_action("ACTION", action_status)
    
    def _execute_gesture_action(self, gesture_type, gesture_name):
        """Execute the appropriate action for a detected gesture."""
        if (gesture_type in self.gesture_handlers and 
            gesture_name in self.gesture_handlers[gesture_type]):
            
            handler = self.gesture_handlers[gesture_type][gesture_name]
            try:
                handler()
            except Exception as e:
                print(f"Error executing {gesture_type}:{gesture_name} - {e}")
        else:
            print(f"No handler found for {gesture_type}:{gesture_name}")
    
    # Action Control Handlers
    def _handle_attack(self):
        print("ACTION: Attack/LMB triggered")
        # TODO: Implement actual game input (mouse click, keyboard, etc.)
    
    def _handle_skill_1(self):
        print("ACTION: Skill 1/Key E triggered")
        # TODO: Implement skill 1 activation
    
    def _handle_skill_2(self):
        print("ACTION: Skill 2/Key R triggered")
        # TODO: Implement skill 2 activation
    
    def _handle_skill_3(self):
        print("ACTION: Skill 3/Key Q triggered")
        # TODO: Implement skill 3 activation
    
    def _handle_utility(self):
        print("ACTION: Utility/Key T triggered")
        # TODO: Implement utility activation
    
    # Movement Control Handlers
    def _handle_move_forward(self):
        print("MOVEMENT: Forward/W triggered")
        # TODO: Implement forward movement
    
    def _handle_move_backward(self):
        print("MOVEMENT: Backward/S triggered")
        # TODO: Implement backward movement
    
    def _handle_move_left(self):
        print("MOVEMENT: Left/A triggered")
        # TODO: Implement left movement
    
    def _handle_move_right(self):
        print("MOVEMENT: Right/D triggered")
        # TODO: Implement right movement
    
    def _handle_shift(self):
        print("MOVEMENT: Shift/Sprint/Crouch triggered")
        # TODO: Implement shift functionality
    
    def _handle_jump(self):
        print("MOVEMENT: Jump/Space triggered")
        # TODO: Implement jump functionality
    
    # Camera Control Handlers
    def _handle_camera_pan_up(self):
        print("CAMERA: Pan Up triggered")
        # TODO: Implement camera pan up
    
    def _handle_camera_pan_down(self):
        print("CAMERA: Pan Down triggered")
        # TODO: Implement camera pan down
    
    def _handle_camera_pan_left(self):
        print("CAMERA: Pan Left triggered")
        # TODO: Implement camera pan left
    
    def _handle_camera_pan_right(self):
        print("CAMERA: Pan Right triggered")
        # TODO: Implement camera pan right
    
    def _handle_camera_lock(self):
        print("CAMERA: Lock/Middle Click triggered")
        # TODO: Implement camera lock
    
    # Navigation Control Handlers
    def _handle_navigation_ok(self):
        print("NAVIGATION: OK/Confirmation/Enter triggered")
        # TODO: Implement confirmation action
    
    def _handle_navigation_f(self):
        print("NAVIGATION: F/Interact triggered")
        # TODO: Implement interaction
    
    def _handle_navigation_esc(self):
        print("NAVIGATION: ESC/Cancel triggered")
        # TODO: Implement cancel/escape action
    
    def get_gesture_status_summary(self, landmarks, palm_bbox, neutral_area=None, neutral_distances=None):
        """Get a summary of all gesture statuses for debugging."""
        result = self.gesture_determinator.determine_all_gestures(
            landmarks, palm_bbox, neutral_area, neutral_distances
        )
        
        return {
            "movement": result["movement_status"],
            "action": result["action_status"],
            "camera": result["camera_status"],
            "navigation": result["navigation_status"],
            "active": f"{result['active_gesture_type']}:{result['active_gesture_name']}"
        }

# Backward compatibility
class CentralLinker(FixedCentralLinker):
    """Backward compatible CentralLinker class."""
    pass
