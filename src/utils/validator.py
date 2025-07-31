# validator.py

def validate_config(config):
    """
    Validates the loaded configuration.
    """
    # Placeholder for configuration validation logic
    # This function will check if all necessary keys and values are present and valid
    # based on the project's requirements.
    print("Validating configuration...")
    if not isinstance(config, dict):
        print("Error: Configuration is not a dictionary.")
        return False
    
    # Example validation: check for a 'hand_tracking' section
    if "hand_tracking" not in config:
        print("Warning: 'hand_tracking' section missing in config.")
        # return False # Depending on strictness

    print("Configuration validation complete.")
    return True

def validate_landmarks(landmarks):
    """
    Validates the received hand landmarks.
    """
    # Placeholder for landmark data validation
    # This function will check if the landmark data is in the expected format
    # and contains all necessary points.
    # For example, check if it's a mediapipe NormalizedLandmarkList and has 21 landmarks.
    if not hasattr(landmarks, 'landmark') or len(landmarks.landmark) != 21:
        print("Error: Invalid landmark data.")
        return False
    return True
