from ..core.gesture_definitions import get_fixed_gesture_definitions

def determine_action_status(landmarks, palm_bbox):
    """
    Determines the action status based on the revised gesture definitions.
    """
    action_definitions = get_fixed_gesture_definitions()["ActionControl"]

    for gesture, definition in action_definitions.items():
        if definition["validation"](landmarks, palm_bbox):
            return gesture

    return "NEUTRAL"