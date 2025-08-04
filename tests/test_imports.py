#!/usr/bin/env python3
"""
Import validation test script for AzimuthControl
"""

import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def test_imports():
    """Test all critical imports"""
    print("🧪 AZIMUTHCONTROL IMPORT VALIDATION")
    print("=" * 50)
    
    tests = []
    
    # Test 1: Basic dependencies
    try:
        import cv2
        import mediapipe as mp
        import numpy as np
        tests.append(("✅", "Basic dependencies (OpenCV, MediaPipe, NumPy)"))
    except ImportError as e:
        tests.append(("❌", f"Basic dependencies: {e}"))
    
    # Test 2: Core modules
    try:
        from src.core.config_manager import get_controls_config
        config = get_controls_config()
        tests.append(("✅", f"Config Manager ({len(config)} control types)"))
    except Exception as e:
        tests.append(("❌", f"Config Manager: {e}"))
    
    # Test 3: Gesture definitions
    try:
        from src.core.gesture_definitions import get_fixed_gesture_definitions
        gestures = get_fixed_gesture_definitions()
        tests.append(("✅", f"Gesture Definitions ({len(gestures)} gesture groups)"))
    except Exception as e:
        tests.append(("❌", f"Gesture Definitions: {e}"))
    
    # Test 4: Utility modules
    try:
        from src.utils.geometry_utils import HandLandmark, calculate_distance
        from src.utils.visualizer import draw_hand_landmarks
        tests.append(("✅", "Utility modules (geometry, visualizer)"))
    except Exception as e:
        tests.append(("❌", f"Utility modules: {e}"))
    
    # Test 5: Performance modules
    try:
        from src.performance.optimized_engine import OptimizedGestureEngine
        engine = OptimizedGestureEngine()
        tests.append(("✅", "Performance Engine (with C++ extension check)"))
    except Exception as e:
        tests.append(("❌", f"Performance Engine: {e}"))
    
    # Test 6: Control modules
    try:
        from src.controls.action_control import determine_action_status
        from src.controls.movement_control import determine_movement_status
        tests.append(("✅", "Control modules (action, movement)"))
    except Exception as e:
        tests.append(("❌", f"Control modules: {e}"))
    
    # Print results
    for status, message in tests:
        print(f"{status} {message}")
    
    # Summary
    passed = sum(1 for status, _ in tests if status == "✅")
    total = len(tests)
    
    print()
    print(f"📊 RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL IMPORTS SUCCESSFUL!")
        print("✨ System is ready to run: python hand_control.py")
        return True
    else:
        print(f"⚠️  {total - passed} import issues found")
        print("📋 Check the error messages above")
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
