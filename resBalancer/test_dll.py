#!/usr/bin/env python3
"""Test script for res_balancer.dll"""

import ctypes
import os
import sys

def test_dll():
    """Test the res_balancer.dll functionality"""
    dll_path = os.path.join(os.path.dirname(__file__), 'build', 'res_balancer.dll')
    
    if not os.path.exists(dll_path):
        print(f"❌ DLL not found at: {dll_path}")
        return False
    
    try:
        # Load the DLL
        print(f"📂 Loading DLL from: {dll_path}")
        lib = ctypes.CDLL(dll_path)
        print("✅ DLL loaded successfully!")
        
        # Test calculate_distance function
        lib.calculate_distance.argtypes = [ctypes.c_double, ctypes.c_double, 
                                          ctypes.c_double, ctypes.c_double]
        lib.calculate_distance.restype = ctypes.c_double
        
        # Test with sample coordinates
        x1, y1 = 0.0, 0.0
        x2, y2 = 3.0, 4.0
        distance = lib.calculate_distance(x1, y1, x2, y2)
        expected = 5.0  # sqrt(3^2 + 4^2) = 5
        
        print(f"🧮 Distance calculation test:")
        print(f"   Points: ({x1}, {y1}) to ({x2}, {y2})")
        print(f"   Result: {distance}")
        print(f"   Expected: {expected}")
        
        if abs(distance - expected) < 0.001:
            print("✅ Distance calculation test PASSED!")
        else:
            print("❌ Distance calculation test FAILED!")
            return False
        
        # Test ROI overlap function
        lib.calculate_roi_overlap_fast.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.c_double,
                                                  ctypes.c_double, ctypes.c_double, ctypes.c_double]
        lib.calculate_roi_overlap_fast.restype = ctypes.c_double
        
        # Test overlapping circles
        overlap = lib.calculate_roi_overlap_fast(0.0, 0.0, 2.0, 1.0, 0.0, 2.0)
        
        print(f"🔄 ROI overlap test:")
        print(f"   Circle 1: center (0,0), radius 2")
        print(f"   Circle 2: center (1,0), radius 2") 
        print(f"   Overlap: {overlap:.2f}")
        
        if overlap > 0:
            print("✅ ROI overlap test PASSED!")
        else:
            print("❌ ROI overlap test FAILED!")
            return False
        
        print("\n🎉 All tests PASSED! DLL is working correctly.")
        return True
        
    except OSError as e:
        print(f"❌ Failed to load DLL: {e}")
        return False
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

if __name__ == "__main__":
    success = test_dll()
    sys.exit(0 if success else 1)
