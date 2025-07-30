from gesture_definitions import get_gesture_definitions

def determine_camera_status(landmarks, palm_bbox, neutral_distances):
    """
    Determines the camera status based on the revised gesture definitions.
    """
    camera_definitions = get_gesture_definitions()["CAMERA_CONTROL"]

    for gesture, definition in camera_definitions.items():
        if definition["validation"](landmarks, palm_bbox, neutral_distances):
            return gesture

    return "NEUTRAL"