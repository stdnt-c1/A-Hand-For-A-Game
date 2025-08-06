"""
Configuration helper utilities for AzimuthControl.
Provides easy config modification and validation functions.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

# Handle both relative and absolute imports
try:
    from ..core.config_manager import get_controls_config
except ImportError:
    # Add parent directories to path for direct execution
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from core.config_manager import get_controls_config


def get_config_file_path() -> Path:
    """Get the path to the controls.json config file."""
    project_root = Path(__file__).parent.parent.parent
    return project_root / "config" / "controls.json"


def load_full_config() -> Dict[str, Any]:
    """Load the complete configuration from controls.json."""
    config_path = get_config_file_path()
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Config file not found: {config_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in config file: {e}")


def save_config(config: Dict[str, Any]) -> None:
    """Save configuration back to controls.json."""
    config_path = get_config_file_path()
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        raise IOError(f"Failed to save config: {e}")


def set_control_enabled(control_name: str, enabled: bool) -> None:
    """Enable or disable an entire control category."""
    config = load_full_config()
    
    if control_name not in config.get("gesture_controls", {}):
        raise ValueError(f"Control '{control_name}' not found in config")
    
    config["gesture_controls"][control_name]["enabled"] = enabled
    save_config(config)
    print(f"Set {control_name} enabled = {enabled}")


def set_gesture_enabled(control_name: str, gesture_name: str, enabled: bool) -> None:
    """Enable or disable a specific gesture within a control category."""
    config = load_full_config()
    
    controls = config.get("gesture_controls", {})
    if control_name not in controls:
        raise ValueError(f"Control '{control_name}' not found in config")
    
    gestures = controls[control_name].get("gestures", [])
    gesture_found = False
    
    for gesture in gestures:
        if gesture["name"] == gesture_name:
            gesture["enabled"] = enabled
            gesture_found = True
            break
    
    if not gesture_found:
        raise ValueError(f"Gesture '{gesture_name}' not found in {control_name}")
    
    save_config(config)
    print(f"Set {control_name}.{gesture_name} enabled = {enabled}")


def get_enabled_controls() -> List[str]:
    """Get list of enabled control categories."""
    config = get_controls_config()
    enabled_controls = []
    
    for control_name, control_data in config.items():
        if control_data.get("enabled", True):
            enabled_controls.append(control_name)
    
    return enabled_controls


def get_enabled_gestures(control_name: str) -> List[str]:
    """Get list of enabled gestures for a specific control category."""
    config = get_controls_config()
    
    if control_name not in config:
        return []
    
    control_data = config[control_name]
    if not control_data.get("enabled", True):
        return []
    
    enabled_gestures = []
    if "gestures" in control_data:
        for gesture in control_data["gestures"]:
            if gesture.get("enabled", True):
                enabled_gestures.append(gesture["name"])
    
    return enabled_gestures


def disable_all_except(control_name: str, gesture_names: Optional[List[str]] = None) -> None:
    """
    Disable all controls except the specified one, and optionally only enable specific gestures.
    
    Args:
        control_name: The control category to keep enabled
        gesture_names: Optional list of gesture names to enable (if None, enable all gestures)
    """
    config = load_full_config()
    controls = config.get("gesture_controls", {})
    
    # Disable all controls first
    for ctrl_name in controls:
        controls[ctrl_name]["enabled"] = False
    
    # Enable the specified control
    if control_name in controls:
        controls[control_name]["enabled"] = True
        
        # If specific gestures are requested, disable all then enable only those
        if gesture_names is not None:
            gestures = controls[control_name].get("gestures", [])
            for gesture in gestures:
                gesture["enabled"] = gesture["name"] in gesture_names
    
    save_config(config)
    
    enabled_gestures = gesture_names if gesture_names else "all gestures"
    print(f"Disabled all controls except {control_name} with {enabled_gestures}")


def print_config_status() -> None:
    """Print current configuration status."""
    print("\n=== Control Configuration Status ===")
    
    config = get_controls_config()
    for control_name, control_data in config.items():
        enabled = control_data.get("enabled", True)
        status = "✅ ENABLED" if enabled else "❌ DISABLED"
        print(f"{control_name}: {status}")
        
        if enabled and "gestures" in control_data:
            for gesture in control_data["gestures"]:
                gesture_enabled = gesture.get("enabled", True)
                gesture_status = "✅" if gesture_enabled else "❌"
                print(f"  └─ {gesture['name']}: {gesture_status}")
    
    print("=====================================\n")


# Quick configuration presets
def enable_movement_only_forward_backward() -> None:
    """Quick preset: Enable only movement control with FORWARD/BACKWARD gestures."""
    disable_all_except("MovementControl", ["NEUTRAL", "FORWARD", "BACKWARD"])


def enable_movement_full() -> None:
    """Quick preset: Enable full movement control."""
    disable_all_except("MovementControl")


def enable_development_mode() -> None:
    """Quick preset: Enable only movement for development/testing."""
    enable_movement_only_forward_backward()
    print("Development mode: Only FORWARD/BACKWARD movement enabled")


if __name__ == "__main__":
    # If run directly, show current config status
    print_config_status()
