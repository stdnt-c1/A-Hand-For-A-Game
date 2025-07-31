from ..core.gesture_definitions import get_fixed_gesture_definitions

def determine_navigation_status(landmarks, palm_bbox):
    """
    Determines the navigation status based on the revised gesture definitions.
    """
    navigation_definitions = get_fixed_gesture_definitions()["NavigationControl"]

    for gesture, definition in navigation_definitions.items():
        if definition["validation"](landmarks, palm_bbox):
            return gesture

    return "NEUTRAL"