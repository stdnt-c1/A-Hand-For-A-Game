from ..core.gesture_definitions import get_fixed_gesture_definitions

def determine_camera_status(landmarks, palm_bbox, neutral_distances=None):
    """
    Determines the camera status based on the revised gesture definitions.
    """
    camera_definitions = get_fixed_gesture_definitions()["CameraControl"]

    for gesture, definition in camera_definitions.items():
        if neutral_distances and "validation" in definition:
            # For pan control, pass neutral distances
            if definition["validation"](landmarks, palm_bbox, neutral_distances):
                return gesture
        elif definition["validation"](landmarks, palm_bbox):
            return gesture

    return "NEUTRAL"