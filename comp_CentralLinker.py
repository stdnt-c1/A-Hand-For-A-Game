import json

class CentralLinker:
    def __init__(self, gesture_definitions_path):
        self.gesture_definitions = self._load_gesture_definitions(gesture_definitions_path)

    def _load_gesture_definitions(self, path):
        with open(path, 'r') as f:
            return json.load(f)

    def process_gestures(self, movement_status, action_status, camera_status, navigation_status):
        # Movement Control
        if movement_status != "NEUTRAL":
            print(f"Movement Gesture Detected: {movement_status}")
            # Call appropriate movement handler

        # Action Control
        if action_status != "NONE":
            print(f"Action Gesture Detected: {action_status}")
            # Call appropriate action handler

        # Camera Control
        if camera_status != "NONE":
            print(f"Camera Gesture Detected: {camera_status}")
            # Call appropriate camera handler

        # Navigation Control
        if navigation_status != "NONE":
            print(f"Navigation Gesture Detected: {navigation_status}")
            # Call appropriate navigation handler