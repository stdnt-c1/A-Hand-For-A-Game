"""
Enhanced Frame Processor Integration for AzimuthControl

This module provides Python integration with the enhanced C++ frame processing system
for dynamic resolution management and startup optimization.
"""

import ctypes
import time
import os
from pathlib import Path
from typing import Tuple, Optional
from ..core.config_manager import get_system_config, get_performance_config
from ..core.dll_manager import get_frame_processor_dll, cleanup_dll_conflicts


class FrameProcessorWrapper:
    """Python wrapper for the C++ frame processor with dynamic resolution management."""
    
    def __init__(self):
        self.dll = None
        self.processor = None
        self.startup_time = time.time()
        self.frame_count = 0
        self.last_fps_time = time.time()
        self.fps_counter = 0
        self.current_fps = 0.0
        
        # Load configuration
        self.system_config = get_system_config()
        self.performance_config = get_performance_config()
        
        # Use processing target resolution, NOT display resolution
        self.target_width = self.performance_config.get('processing_target_width', 640)
        self.target_height = self.performance_config.get('processing_target_height', 480)
        self.target_fps = self.performance_config.get('target_fps', 30)
        
        print(f"🎯 Frame processor target: {self.target_width}x{self.target_height} @ {self.target_fps}fps")
        print(f"📺 Display window: {self.system_config.get('window_width', 1280)}x{self.system_config.get('window_height', 720)}")
        
        self._load_dll()
        self._initialize_processor()
    
    def _load_dll(self):
        """Load the enhanced C++ extension using DLL manager."""
        try:
            # Clean up any conflicting DLLs first
            cleanup_dll_conflicts()
            
            # Load DLL through the manager
            self.dll = get_frame_processor_dll()
            
            if self.dll is None:
                raise RuntimeError("Failed to load frame processor DLL through manager")
            
            # Define function signatures
            self._define_function_signatures()
            
            print(f"✅ Enhanced C++ frame processor loaded successfully via DLL manager")
            
        except Exception as e:
            print(f"❌ Failed to load enhanced C++ extension: {e}")
            print("   Make sure the DLL is compiled for the correct architecture (x64)")
            self.dll = None
    
    def _define_function_signatures(self):
        """Define C function signatures for ctypes."""
        if not self.dll:
            return
        
        # FrameProcessor management
        self.dll.create_frame_processor.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_double]
        self.dll.create_frame_processor.restype = ctypes.c_void_p
        
        self.dll.destroy_frame_processor.argtypes = [ctypes.c_void_p]
        self.dll.destroy_frame_processor.restype = None
        
        self.dll.should_process_frame.argtypes = [ctypes.c_void_p, ctypes.c_double]
        self.dll.should_process_frame.restype = ctypes.c_int
        
        self.dll.update_processing_stats.argtypes = [ctypes.c_void_p, ctypes.c_double]
        self.dll.update_processing_stats.restype = None
        
        self.dll.get_optimal_resolution.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
        self.dll.get_optimal_resolution.restype = None
        
        self.dll.get_scale_factor.argtypes = [ctypes.c_void_p]
        self.dll.get_scale_factor.restype = ctypes.c_double
        
        self.dll.is_startup_complete.argtypes = [ctypes.c_void_p]
        self.dll.is_startup_complete.restype = ctypes.c_int
        
        self.dll.optimize_processing_pipeline.argtypes = [ctypes.c_void_p, ctypes.c_double, ctypes.c_double]
        self.dll.optimize_processing_pipeline.restype = None
        
        # Safety and mirror functions
        try:
            self.dll.safe_dimension_check.argtypes = [ctypes.c_int, ctypes.c_int]
            self.dll.safe_dimension_check.restype = ctypes.c_int
            
            self.dll.apply_mirror_transform.argtypes = [
                ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, 
                ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int
            ]
            self.dll.apply_mirror_transform.restype = ctypes.c_int
            print("🔧 Mirror transform functions loaded")
        except AttributeError:
            print("⚠️ Mirror transform functions not available in this DLL version")
        
        # New frame downscaling functions
        self.dll.should_downscale_frame.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, 
                                                   ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
        self.dll.should_downscale_frame.restype = ctypes.c_int
        
        self.dll.get_processing_scale_factor.argtypes = [ctypes.c_void_p]
        self.dll.get_processing_scale_factor.restype = ctypes.c_double
    
    def _initialize_processor(self):
        """Initialize the C++ frame processor."""
        if not self.dll:
            return
        
        try:
            self.processor = self.dll.create_frame_processor(
                self.target_width, 
                self.target_height, 
                self.target_fps
            )
            
            if self.processor:
                print(f"✅ Frame processor initialized: target {self.target_width}x{self.target_height} @ {self.target_fps}fps")
            else:
                print("❌ Failed to create frame processor")
                
        except Exception as e:
            print(f"❌ Failed to initialize frame processor: {e}")
    
    def should_process_frame(self, processing_time_ms: float) -> bool:
        """Check if the current frame should be processed based on performance."""
        if not self.dll or not self.processor:
            return True
        
        try:
            result = self.dll.should_process_frame(self.processor, processing_time_ms)
            return bool(result)
        except Exception as e:
            print(f"Error in should_process_frame: {e}")
            return True
    
    def update_processing_stats(self, processing_time_ms: float):
        """Update processing statistics and adjust parameters."""
        if not self.dll or not self.processor:
            return
        
        try:
            self.dll.update_processing_stats(self.processor, processing_time_ms)
            self.frame_count += 1
            
            # Update FPS calculation
            current_time = time.time()
            self.fps_counter += 1
            
            if current_time - self.last_fps_time >= 1.0:
                self.current_fps = self.fps_counter / (current_time - self.last_fps_time)
                self.fps_counter = 0
                self.last_fps_time = current_time
                
        except Exception as e:
            print(f"Error updating processing stats: {e}")
    
    def get_optimal_resolution(self) -> Tuple[int, int]:
        """Get the current optimal resolution for processing."""
        if not self.dll or not self.processor:
            return self.target_width, self.target_height
        
        try:
            width = ctypes.c_int()
            height = ctypes.c_int()
            self.dll.get_optimal_resolution(self.processor, ctypes.byref(width), ctypes.byref(height))
            return width.value, height.value
        except Exception as e:
            print(f"Error getting optimal resolution: {e}")
            return self.target_width, self.target_height
    
    def get_scale_factor(self) -> float:
        """Get current resolution scale factor."""
        if not self.dll or not self.processor:
            return 1.0
        
        try:
            return self.dll.get_scale_factor(self.processor)
        except Exception as e:
            print(f"Error getting scale factor: {e}")
            return 1.0
    
    def is_startup_complete(self) -> bool:
        """Check if startup phase is complete."""
        if not self.dll or not self.processor:
            return True
        
        try:
            result = self.dll.is_startup_complete(self.processor)
            return bool(result)
        except Exception as e:
            print(f"Error checking startup status: {e}")
            return True
    
    def optimize_for_system_load(self, cpu_usage: float, memory_usage: float):
        """Optimize processing pipeline based on system load."""
        if not self.dll or not self.processor:
            return
        
        try:
            self.dll.optimize_processing_pipeline(self.processor, cpu_usage, memory_usage)
        except Exception as e:
            print(f"Error optimizing processing pipeline: {e}")
    
    def should_downscale_frame(self, input_width: int, input_height: int) -> Tuple[bool, int, int]:
        """
        Check if frame should be downscaled for processing optimization.
        Returns (should_downscale, output_width, output_height)
        """
        if not self.dll or not self.processor:
            return False, input_width, input_height
        
        try:
            output_width = ctypes.c_int()
            output_height = ctypes.c_int()
            should_downscale = self.dll.should_downscale_frame(
                self.processor, input_width, input_height, 
                ctypes.byref(output_width), ctypes.byref(output_height)
            )
            return bool(should_downscale), output_width.value, output_height.value
        except Exception as e:
            print(f"Error checking frame downscaling: {e}")
            return False, input_width, input_height
    
    def get_processing_scale_factor(self) -> float:
        """Get the scale factor for processing (different from display scale)."""
        if not self.dll or not self.processor:
            return 1.0
        
        try:
            return self.dll.get_processing_scale_factor(self.processor)
        except Exception as e:
            print(f"Error getting processing scale factor: {e}")
            return 1.0
    
    def get_startup_progress(self) -> float:
        """Get startup progress as percentage (0.0 to 1.0)."""
        if self.is_startup_complete():
            return 1.0
        
        # Estimate progress based on time and frame count
        elapsed_time = time.time() - self.startup_time
        time_progress = min(1.0, elapsed_time / 10.0)  # 10 seconds estimated startup
        frame_progress = min(1.0, self.frame_count / 150.0)  # 150 frames estimated
        
        return max(time_progress, frame_progress)
    
    def get_performance_stats(self) -> dict:
        """Get current performance statistics."""
        return {
            'current_fps': self.current_fps,
            'target_fps': self.target_fps,
            'frames_processed': self.frame_count,
            'startup_complete': self.is_startup_complete(),
            'startup_progress': self.get_startup_progress(),
            'current_resolution': self.get_optimal_resolution(),
            'target_resolution': (self.target_width, self.target_height),
            'scale_factor': self.get_scale_factor(),
            'startup_time_elapsed': time.time() - self.startup_time
        }
    
    def apply_mirror_transform(self, input_data: bytes, width: int, height: int, 
                              channels: int = 3, mirror_horizontal: bool = True) -> bytes:
        """Apply mirror transformation using C++ implementation."""
        if not self.dll or not hasattr(self.dll, 'apply_mirror_transform'):
            # Fallback to Python implementation
            return self._python_mirror_fallback(input_data, width, height, channels, mirror_horizontal)
        
        try:
            # Check dimensions safety
            if hasattr(self.dll, 'safe_dimension_check'):
                if not self.dll.safe_dimension_check(width, height):
                    raise ValueError("Unsafe dimensions for mirroring")
            
            # Prepare buffers  
            input_array = (ctypes.c_ubyte * len(input_data)).from_buffer(bytearray(input_data))
            output_data = bytearray(len(input_data))
            output_array = (ctypes.c_ubyte * len(output_data)).from_buffer(output_data)
            
            # Call C++ mirror function
            result = self.dll.apply_mirror_transform(
                input_array, width, height, channels, output_array, 1 if mirror_horizontal else 0
            )
            
            if result:
                return bytes(output_data)
            else:
                return self._python_mirror_fallback(input_data, width, height, channels, mirror_horizontal)
                
        except Exception as e:
            print(f"C++ mirror failed, using Python fallback: {e}")
            return self._python_mirror_fallback(input_data, width, height, channels, mirror_horizontal)
    
    def _python_mirror_fallback(self, input_data: bytes, width: int, height: int, 
                               channels: int, mirror_horizontal: bool) -> bytes:
        """Python fallback for mirror transformation."""
        if not mirror_horizontal:
            return input_data
        
        # Simple horizontal flip without numpy dependency
        output_data = bytearray(len(input_data))
        for y in range(height):
            for x in range(width):
                src_idx = (y * width + x) * channels
                dst_idx = (y * width + (width - 1 - x)) * channels
                for c in range(channels):
                    output_data[dst_idx + c] = input_data[src_idx + c]
        
        return bytes(output_data)
    
    def __del__(self):
        """Cleanup when the wrapper is destroyed."""
        if self.dll and self.processor:
            try:
                self.dll.destroy_frame_processor(self.processor)
            except:
                pass


# Global instance for easy access
_frame_processor = None

def get_frame_processor() -> FrameProcessorWrapper:
    """Get the global frame processor instance."""
    global _frame_processor
    if _frame_processor is None:
        _frame_processor = FrameProcessorWrapper()
    return _frame_processor

def should_process_frame(processing_time_ms: float) -> bool:
    """Check if frame should be processed (convenience function)."""
    return get_frame_processor().should_process_frame(processing_time_ms)

def update_frame_stats(processing_time_ms: float):
    """Update frame processing statistics (convenience function)."""
    get_frame_processor().update_processing_stats(processing_time_ms)

def get_optimal_camera_resolution() -> Tuple[int, int]:
    """Get optimal camera resolution for current conditions."""
    return get_frame_processor().get_optimal_resolution()

def get_performance_info() -> dict:
    """Get current performance information."""
    return get_frame_processor().get_performance_stats()
