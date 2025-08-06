/*
 * OpenCV-Free C++ Implementation for AzimuthControl
 * 
 * This implementation provides all the performance benefits of C++ processing
 * without requiring OpenCV dependencies, making build and deployment much simpler.
 */

#include "opencv_free_processor.h"
#include <cstring>
#include <algorithm>
#include <iostream>

// Implementation file - all functions are defined in the header for this simple version

// Test function to verify the DLL is working
extern "C" {
    __declspec(dllexport) int test_opencv_free_dll() {
        std::cout << "✅ OpenCV-free processor DLL loaded successfully!" << std::endl;
        return 42; // Test value
    }
    
    __declspec(dllexport) const char* get_processor_version() {
        return "AzimuthControl OpenCV-Free Processor v1.0";
    }
}
