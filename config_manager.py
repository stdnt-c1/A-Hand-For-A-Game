#!/usr/bin/env python3
"""
Config management script for AzimuthControl.
Allows easy enabling/disabling of controls and gestures from command line.
"""

import sys
import argparse
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.utils.config_helper import (
    set_control_enabled, 
    set_gesture_enabled,
    disable_all_except,
    enable_development_mode,
    enable_movement_only_forward_backward,
    enable_movement_full,
    print_config_status,
    get_enabled_controls,
    get_enabled_gestures
)


def main():
    parser = argparse.ArgumentParser(description="Manage AzimuthControl configuration")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show current configuration status')
    
    # Enable/disable control commands
    control_parser = subparsers.add_parser('control', help='Enable/disable control categories')
    control_parser.add_argument('name', help='Control name (MovementControl, ActionControl, etc.)')
    control_parser.add_argument('state', choices=['enable', 'disable'], help='Enable or disable')
    
    # Enable/disable gesture commands
    gesture_parser = subparsers.add_parser('gesture', help='Enable/disable specific gestures')
    gesture_parser.add_argument('control', help='Control category name')
    gesture_parser.add_argument('gesture', help='Gesture name')
    gesture_parser.add_argument('state', choices=['enable', 'disable'], help='Enable or disable')
    
    # Preset commands
    preset_parser = subparsers.add_parser('preset', help='Apply configuration presets')
    preset_parser.add_argument('name', choices=[
        'dev', 'movement-fb', 'movement-full', 'all'
    ], help='Preset name')
    
    args = parser.parse_args()
    
    if args.command == 'status':
        print_config_status()
    
    elif args.command == 'control':
        enabled = args.state == 'enable'
        set_control_enabled(args.name, enabled)
        print_config_status()
    
    elif args.command == 'gesture':
        enabled = args.state == 'enable'
        set_gesture_enabled(args.control, args.gesture, enabled)
        print_config_status()
    
    elif args.command == 'preset':
        if args.name == 'dev':
            enable_development_mode()
        elif args.name == 'movement-fb':
            enable_movement_only_forward_backward()
        elif args.name == 'movement-full':
            enable_movement_full()
        elif args.name == 'all':
            # Enable all controls
            for control in ['MovementControl', 'ActionControl', 'CameraControl', 'NavigationControl']:
                set_control_enabled(control, True)
        print_config_status()
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
