from gesture_definitions import get_gesture_definitions

def determine_movement_status(landmarks, palm_bbox, neutral_area, neutral_distances):
    """
    Determines the movement status based on the revised gesture definitions.
    """ 
    movement_definitions = get_gesture_definitions()["MOVEMENT_CONTROL"]

    for gesture, definition in movement_definitions.items():
        if definition["validation"](landmarks, palm_bbox, neutral_area, neutral_distances):
            return gesture

    return "NEUTRAL"
