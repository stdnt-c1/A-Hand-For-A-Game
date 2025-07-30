import time

class GestureState:
    def __init__(self, gesture_duration=0.3, reengagement_delay=0.2):
        self.gesture_duration = gesture_duration
        self.reengagement_delay = reengagement_delay
        self.current_gesture = None
        self.last_gesture_time = 0
        self.last_detected_gesture = None
        self.last_detection_time = 0

    def update(self, movement_status, action_status, camera_status, navigation_status):
        # Priority Hierarchy: Navigation > Camera > Movement > Action
        if navigation_status != "NEUTRAL":
            detected_gesture = navigation_status
        elif camera_status != "NEUTRAL":
            detected_gesture = camera_status
        elif movement_status != "NEUTRAL":
            detected_gesture = movement_status
        elif action_status != "NEUTRAL":
            detected_gesture = action_status
        else:
            detected_gesture = "NEUTRAL"

        current_time = time.time()

        if detected_gesture == self.last_detected_gesture:
            if current_time - self.last_detection_time >= self.gesture_duration:
                if self.current_gesture != detected_gesture:
                    if current_time - self.last_gesture_time >= self.reengagement_delay:
                        self.current_gesture = detected_gesture
                        self.last_gesture_time = current_time
        else:
            self.last_detected_gesture = detected_gesture
            self.last_detection_time = current_time
            if detected_gesture == "NEUTRAL":
                if self.current_gesture != "NEUTRAL":
                    if current_time - self.last_gesture_time >= self.reengagement_delay:
                        self.current_gesture = "NEUTRAL"
                        self.last_gesture_time = current_time

    def get_active_gesture(self):
        return self.current_gesture
