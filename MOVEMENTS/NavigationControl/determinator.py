from gesture_definitions import get_gesture_definitions

def determine_navigation_status(landmarks, palm_bbox):
    """
    Determines the navigation status based on the revised gesture definitions.
    """
    navigation_definitions = get_gesture_definitions()["NAVIGATION_CONTROL"]

    for gesture, definition in navigation_definitions.items():
        if definition["validation"](landmarks, palm_bbox):
            return gesture

    return "NEUTRAL"