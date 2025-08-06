"""
Movement Detection Diagnostic Tool for AzimuthControl

This tool helps analyze and tune the forward/backward movement detection
parameters including thresholds and deadzone settings.
"""

import sys
from pathlib import Path
import time

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.controls.movement_control import get_movement_controller


def analyze_current_settings():
    """Analyze the current movement detection settings."""
    controller = get_movement_controller()
    
    print("=== Movement Detection Analysis ===")
    print(f"Forward Threshold: {controller.forward_threshold} (area ratio)")
    print(f"Backward Threshold: {controller.backward_threshold} (area ratio)")
    print(f"Deadzone Multiplier: {controller.deadzone_multiplier}")
    print(f"Calibration Complete: {controller.calibration_complete}")
    print(f"Neutral Area: {controller.neutral_area}")
    print(f"History Size: {controller.history_size}")
    print(f"Required Samples: {controller.required_samples}")
    print()
    
    # Calculate effective zones
    if controller.neutral_area:
        neutral_area = controller.neutral_area
        
        print("=== Detection Zones (Enhanced Hysteresis) ===")
        print(f"Neutral Area: {neutral_area:.6f}")
        
        # Forward zone with hysteresis
        forward_enter = neutral_area * controller.forward_threshold
        forward_exit = neutral_area * (controller.forward_threshold - controller.deadzone_multiplier)
        print(f"Forward Enter: {forward_enter:.6f} (area >= {controller.forward_threshold}x neutral)")
        print(f"Forward Exit: {forward_exit:.6f} (must drop below {controller.forward_threshold - controller.deadzone_multiplier:.2f}x to exit)")
        
        # Backward zone with hysteresis
        backward_enter = neutral_area * controller.backward_threshold
        backward_exit = neutral_area * (controller.backward_threshold + controller.deadzone_multiplier)
        print(f"Backward Enter: {backward_enter:.6f} (area <= {controller.backward_threshold}x neutral)")
        print(f"Backward Exit: {backward_exit:.6f} (must rise above {controller.backward_threshold + controller.deadzone_multiplier:.2f}x to exit)")
        
        # Neutral zone
        print(f"Neutral Zone: {backward_exit:.6f} - {forward_exit:.6f} (hysteresis boundaries)")
        print(f"Stable Neutral: {backward_enter:.6f} - {forward_enter:.6f} (always neutral)")
        
        print("\n=== Sensitivity Analysis ===")
        area_change_forward = (controller.forward_threshold - 1.0) * 100
        area_change_backward = (1.0 - controller.backward_threshold) * 100
        deadzone_percent = controller.deadzone_multiplier * 100
        hysteresis_range = ((controller.forward_threshold - controller.deadzone_multiplier) - 
                           (controller.backward_threshold + controller.deadzone_multiplier)) * 100
        
        print(f"Forward Sensitivity: {area_change_forward:.1f}% area increase required")
        print(f"Backward Sensitivity: {area_change_backward:.1f}% area decrease required") 
        print(f"Hysteresis Deadzone: {deadzone_percent:.1f}% prevents oscillation")
        print(f"Neutral Range: {hysteresis_range:.1f}% of neutral area")
        
        # Recommendations
        print("\n=== Tuning Recommendations ===")
        if area_change_forward > 20:
            print("⚠️  Forward sensitivity is low (needs >20% area change)")
            print("   Consider lowering forward_threshold to 1.10 (10% change)")
        elif area_change_forward < 10:
            print("⚠️  Forward sensitivity is high (needs <10% area change)")
            print("   Consider raising forward_threshold to 1.15 (15% change)")
        else:
            print("✅ Forward sensitivity looks reasonable")
            
        if area_change_backward > 20:
            print("⚠️  Backward sensitivity is low (needs >20% area change)")
            print("   Consider raising backward_threshold to 0.90 (10% change)")
        elif area_change_backward < 10:
            print("⚠️  Backward sensitivity is high (needs <10% area change)")
            print("   Consider lowering backward_threshold to 0.85 (15% change)")
        else:
            print("✅ Backward sensitivity looks reasonable")
            
        if deadzone_percent > 8:
            print("⚠️  Deadzone is large (may cause sluggish response)")
            print("   Consider reducing deadzone_multiplier to 0.03 (3%)")
        elif deadzone_percent < 3:
            print("⚠️  Deadzone is small (may cause jittery detection)")
            print("   Consider increasing deadzone_multiplier to 0.05 (5%)")
        else:
            print("✅ Deadzone size looks reasonable")
    else:
        print("❌ Calibration not complete - run the detection system first")


def suggest_optimal_settings():
    """Suggest optimal settings based on gaming requirements."""
    print("\n=== Optimal Gaming Settings ===")
    print("Based on gaming requirements and responsiveness:")
    print()
    print("Conservative (stable):")
    print("  forward_threshold = 1.20  # 20% area increase")
    print("  backward_threshold = 0.80  # 20% area decrease") 
    print("  deadzone_multiplier = 0.08  # 8% deadzone")
    print()
    print("Balanced (current):")
    print("  forward_threshold = 1.15  # 15% area increase")
    print("  backward_threshold = 0.85  # 15% area decrease")
    print("  deadzone_multiplier = 0.05  # 5% deadzone")
    print()
    print("Sensitive (responsive):")
    print("  forward_threshold = 1.10  # 10% area increase")
    print("  backward_threshold = 0.90  # 10% area decrease")
    print("  deadzone_multiplier = 0.03  # 3% deadzone")
    print()
    print("Ultra-sensitive (expert):")
    print("  forward_threshold = 1.08  # 8% area increase")
    print("  backward_threshold = 0.92  # 8% area decrease")
    print("  deadzone_multiplier = 0.02  # 2% deadzone")


def test_detection_logic():
    """Test the detection logic with sample values."""
    controller = get_movement_controller()
    
    if not controller.neutral_area:
        print("❌ No calibration data available")
        return
        
    print("\n=== Detection Logic Test ===")
    neutral_area = controller.neutral_area
    
    # Test various area ratios
    test_ratios = [0.70, 0.80, 0.85, 0.90, 0.95, 1.00, 1.05, 1.10, 1.15, 1.20, 1.30]
    
    print("Area Ratio | Expected | Actual Detection")
    print("-" * 40)
    
    for ratio in test_ratios:
        test_area = neutral_area * ratio
        
        # Mock palm_bbox for testing
        mock_palm_bbox = {
            'width': test_area ** 0.5,  # Assuming square palm
            'height': test_area ** 0.5
        }
        
        # Temporarily modify area history for testing
        original_history = controller.area_history.copy()
        controller.area_history = [test_area] * controller.history_size
        
        detection = controller.detect_depth_movement(mock_palm_bbox)
        
        # Restore original history
        controller.area_history = original_history
        
        if ratio <= 0.85:
            expected = "BACKWARD"
        elif ratio >= 1.15:
            expected = "FORWARD"
        else:
            expected = "NEUTRAL"
            
        status = "✅" if detection == expected else "❌"
        print(f"{ratio:8.2f} | {expected:8s} | {detection:8s} {status}")


if __name__ == "__main__":
    analyze_current_settings()
    suggest_optimal_settings()
    test_detection_logic()
