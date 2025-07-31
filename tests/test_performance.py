#!/usr/bin/env python3
"""Quick test of the optimized engine with C++ extension"""

import sys
import os
sys.path.append('.')

try:
    from src.performance.optimized_engine import OptimizedGestureEngine
    print("✅ Importing OptimizedGestureEngine...")
    
    engine = OptimizedGestureEngine()
    print(f"✅ Engine created successfully")
    print(f"🔧 C++ extension available: {engine.cpp_available}")
    
    if engine.cpp_available:
        print("🚀 C++ performance extensions are ACTIVE!")
        print("   Expected ~75% performance improvement in geometric calculations")
    else:
        print("⚠️  Using Python fallback (slower)")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
