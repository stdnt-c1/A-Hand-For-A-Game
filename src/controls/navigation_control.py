from ..core.gesture_definitions import get_fixed_gesture_definitions
from ..core.config_manager import get_controls_config

def determine_navigation_status(landmarks, palm_bbox):
    """
    Determines the navigation status based on the revised gesture definitions.
    Respects config-based enabling/disabling.
    """
    # Load configuration
    config = get_controls_config().get("NavigationControl", {})
    enabled = config.get("enabled", True)
    
    # Check if navigation control is enabled
    if not enabled:
        return "NEUTRAL"
    
    navigation_definitions = get_fixed_gesture_definitions()["NavigationControl"]

    for gesture, definition in navigation_definitions.items():
        if definition["validation"](landmarks, palm_bbox):
            return gesture

    return "NEUTRAL"