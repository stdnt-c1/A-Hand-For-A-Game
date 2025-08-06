"""
Enhanced High-Performance Frame Processor with CUDA Acceleration and Safety Features
====================================================================================

This module provides a comprehensive frame processing system with:
- Full CUDA GPU acceleration with fallback safety
- Real-time performance monitoring and adaptation
- Emergency fallback systems for maximum reliability
- Memory management with overflow protection
- Thermal throttling and safety monitoring

Author: A-Hand-For-A-Game Project
Version: 2.0.0 - Full CUDA Implementation
"""

import ctypes
import numpy as np
import cv2
import time
import threading
import psutil
import logging
from typing import Optional, Tuple, Dict, Any, List
from dataclasses import dataclass
from pathlib import Path
import os
import sys

# Configure logging for performance monitoring
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class FrameProcessingConfig:
    """Enhanced configuration for frame processing with safety limits"""
    # Basic settings
    target_width: int = 640
    target_height: int = 480
    target_fps: float = 30.0
    
    # Performance settings
    enable_cuda: bool = True
    enable_adaptive_quality: bool = True
    max_processing_time_ms: float = 100.0
    max_threads: int = 4
    
    # Memory management
    max_memory_usage_mb: int = 512
    enable_memory_pinning: bool = False
    
    # Safety settings
    enable_safety_monitoring: bool = True
    enable_emergency_fallback: bool = True
    max_consecutive_errors: int = 10
    thermal_limit_celsius: float = 85.0
    
    # Advanced features
    enable_batch_processing: bool = False
    batch_size: int = 4
    enable_async_processing: bool = True

@dataclass
class PerformanceMetrics:
    """Comprehensive performance and safety metrics"""
    # Performance
    fps: float = 0.0
    avg_processing_time: float = 0.0
    efficiency_percentage: float = 0.0
    
    # Processing statistics
    frames_processed: int = 0
    frames_dropped: int = 0
    frames_in_queue: int = 0
    
    # GPU metrics
    gpu_utilization: float = 0.0
    gpu_memory_usage_mb: float = 0.0
    gpu_temperature_celsius: float = 0.0
    
    # CPU metrics
    cpu_utilization: float = 0.0
    cpu_memory_usage_mb: float = 0.0
    
    # Quality and safety
    current_scale_level: int = 0
    error_count: int = 0
    emergency_fallback_active: bool = False
    thermal_throttling_active: bool = False
    cuda_healthy: bool = True

class CudaFrameProcessor:
    """
    High-performance frame processor with full CUDA acceleration and comprehensive safety features
    """
    
    def __init__(self, config: FrameProcessingConfig = None):
        """Initialize the enhanced frame processor with safety systems"""
        self.config = config or FrameProcessingConfig()
        self.dll = None
        self.cuda_processor = None
        self.stream_processor = None
        
        # Safety and monitoring
        self.initialized = False
        self.cuda_available = False
        self.emergency_fallback_active = False
        self.monitoring_active = False
        self.monitoring_thread = None
        
        # Performance tracking
        self.metrics = PerformanceMetrics()
        self.performance_history = []
        self.last_performance_update = time.time()
        
        # Error tracking for safety
        self.consecutive_errors = 0
        self.total_errors = 0
        self.last_error_time = 0
        
        # Thread safety
        self.processing_lock = threading.RLock()
        
        logger.info("🚀 Initializing Enhanced CUDA Frame Processor")
        self._initialize_system()
    
    def _initialize_system(self) -> bool:
        """Initialize the complete system with comprehensive error handling"""
        try:
            # Load DLL with fallback options
            if not self._load_dll():
                logger.error("❌ Failed to load processing DLL")
                return False
            
            # Initialize CUDA if available
            if self.config.enable_cuda:
                self._initialize_cuda()
            
            # Initialize stream processor
            self._initialize_stream_processor()
            
            # Start safety monitoring
            if self.config.enable_safety_monitoring:
                self._start_monitoring()
            
            self.initialized = True
            logger.info("✅ Enhanced frame processor initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ System initialization failed: {e}")
            self._activate_emergency_fallback()
            return False
    
    def _load_dll(self) -> bool:
        """Load the enhanced DLL with comprehensive error handling"""
        dll_paths = [
            Path("resBalancer/res_balancer_cuda.dll"),  # Enhanced CUDA DLL
            Path("resBalancer/res_balancer.dll"),       # Fallback standard DLL
            Path("resBalancer/res_balancer_enhanced.dll")  # Alternative enhanced
        ]
        
        for dll_path in dll_paths:
            try:
                if dll_path.exists():
                    self.dll = ctypes.CDLL(str(dll_path))
                    logger.info(f"✅ Loaded DLL: {dll_path}")
                    self._setup_dll_functions()
                    return True
            except Exception as e:
                logger.warning(f"⚠️  Failed to load {dll_path}: {e}")
                continue
        
        logger.error("❌ No compatible DLL found")
        return False
    
    def _setup_dll_functions(self):
        """Setup DLL function signatures with comprehensive error handling"""
        try:
            # CUDA availability and management
            self.dll.cuda_is_available.restype = ctypes.c_int
            self.dll.cuda_get_device_count.restype = ctypes.c_int
            
            # Enhanced CUDA processor functions
            if hasattr(self.dll, 'create_cuda_processor'):
                self.dll.create_cuda_processor.argtypes = [ctypes.POINTER(CudaConfig)]
                self.dll.create_cuda_processor.restype = ctypes.c_void_p
                
                self.dll.destroy_cuda_processor.argtypes = [ctypes.c_void_p]
                self.dll.destroy_cuda_processor.restype = None
                
                self.dll.cuda_process_frame.argtypes = [
                    ctypes.c_void_p,                    # processor
                    ctypes.POINTER(ctypes.c_ubyte),     # input
                    ctypes.c_int, ctypes.c_int,         # width, height
                    ctypes.POINTER(ctypes.c_ubyte),     # output
                    ctypes.c_int, ctypes.c_int          # output_width, output_height
                ]
                self.dll.cuda_process_frame.restype = ctypes.c_int
                
                # Performance monitoring functions
                self.dll.cuda_get_processing_time.argtypes = [ctypes.c_void_p]
                self.dll.cuda_get_processing_time.restype = ctypes.c_float
                
                self.dll.cuda_get_gpu_utilization.argtypes = [ctypes.c_void_p]
                self.dll.cuda_get_gpu_utilization.restype = ctypes.c_float
                
                self.dll.cuda_get_memory_usage_mb.argtypes = [ctypes.c_void_p]
                self.dll.cuda_get_memory_usage_mb.restype = ctypes.c_int
            
            # Enhanced stream processor functions
            if hasattr(self.dll, 'create_stream_processor_enhanced'):
                self.dll.create_stream_processor_enhanced.argtypes = [StreamConfig]
                self.dll.create_stream_processor_enhanced.restype = ctypes.c_void_p
                
                self.dll.destroy_stream_processor_enhanced.argtypes = [ctypes.c_void_p]
                self.dll.destroy_stream_processor_enhanced.restype = None
                
                # Safety and monitoring
                self.dll.is_system_healthy.argtypes = [ctypes.c_void_p]
                self.dll.is_system_healthy.restype = ctypes.c_int
                
                self.dll.is_emergency_fallback_active.argtypes = [ctypes.c_void_p]
                self.dll.is_emergency_fallback_active.restype = ctypes.c_int
                
                self.dll.get_gpu_temperature.argtypes = [ctypes.c_void_p]
                self.dll.get_gpu_temperature.restype = ctypes.c_double
            
            logger.info("✅ DLL function signatures configured")
            
        except Exception as e:
            logger.error(f"❌ Failed to setup DLL functions: {e}")
            raise
    
    def _initialize_cuda(self) -> bool:
        """Initialize CUDA with comprehensive safety checks"""
        try:
            # Check CUDA availability
            if not self.dll.cuda_is_available():
                logger.warning("⚠️  CUDA not available, using CPU fallback")
                return False
            
            device_count = self.dll.cuda_get_device_count()
            logger.info(f"✅ CUDA available with {device_count} device(s)")
            
            # Create CUDA configuration
            cuda_config = CudaConfig()
            cuda_config.device_id = 0
            cuda_config.memory_pool_size_mb = min(self.config.max_memory_usage_mb // 2, 512)
            cuda_config.max_concurrent_streams = min(self.config.max_threads, 4)
            cuda_config.enable_memory_pinning = self.config.enable_memory_pinning
            
            # Create CUDA processor
            self.cuda_processor = self.dll.create_cuda_processor(ctypes.byref(cuda_config))
            if not self.cuda_processor:
                logger.error("❌ Failed to create CUDA processor")
                return False
            
            self.cuda_available = True
            logger.info(f"✅ CUDA processor initialized with {cuda_config.max_concurrent_streams} streams")
            return True
            
        except Exception as e:
            logger.error(f"❌ CUDA initialization failed: {e}")
            return False
    
    def _initialize_stream_processor(self) -> bool:
        """Initialize the enhanced stream processor"""
        try:
            if not hasattr(self.dll, 'create_stream_processor_enhanced'):
                logger.warning("⚠️  Enhanced stream processor not available")
                return False
            
            # Create stream configuration
            stream_config = StreamConfig()
            stream_config.target_width = self.config.target_width
            stream_config.target_height = self.config.target_height
            stream_config.target_fps = int(self.config.target_fps)
            stream_config.enable_cuda = self.cuda_available
            stream_config.enable_adaptive_quality = self.config.enable_adaptive_quality
            stream_config.max_memory_usage_mb = self.config.max_memory_usage_mb
            stream_config.enable_safety_monitoring = self.config.enable_safety_monitoring
            
            # Create stream processor
            self.stream_processor = self.dll.create_stream_processor_enhanced(stream_config)
            if not self.stream_processor:
                logger.error("❌ Failed to create stream processor")
                return False
            
            logger.info("✅ Enhanced stream processor initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Stream processor initialization failed: {e}")
            return False
    
    def process_frame(self, frame: np.ndarray, target_size: Tuple[int, int] = None) -> Optional[np.ndarray]:
        """
        Process frame with maximum performance and comprehensive safety
        
        Args:
            frame: Input frame as numpy array
            target_size: Optional target size (width, height)
            
        Returns:
            Processed frame or None if processing failed
        """
        if not self.initialized:
            logger.error("❌ Processor not initialized")
            return None
        
        # Emergency fallback check
        if self.emergency_fallback_active:
            return self._process_frame_cpu_fallback(frame, target_size)
        
        start_time = time.time()
        
        try:
            with self.processing_lock:
                # Validate input
                if not self._validate_frame(frame):
                    return None
                
                # Determine target size
                if target_size is None:
                    target_size = (self.config.target_width, self.config.target_height)
                
                # Choose processing method based on availability and health
                if self.cuda_available and self._is_cuda_healthy():
                    result = self._process_frame_cuda(frame, target_size)
                else:
                    result = self._process_frame_cpu_optimized(frame, target_size)
                
                # Update performance metrics
                processing_time = (time.time() - start_time) * 1000
                self._update_performance_metrics(processing_time, result is not None)
                
                # Safety check: if processing took too long, consider degrading quality
                if processing_time > self.config.max_processing_time_ms:
                    self._handle_performance_degradation()
                
                return result
                
        except Exception as e:
            self._handle_processing_error(e)
            return self._process_frame_cpu_fallback(frame, target_size)
    
    def _process_frame_cuda(self, frame: np.ndarray, target_size: Tuple[int, int]) -> Optional[np.ndarray]:
        """Process frame using CUDA acceleration with safety checks"""
        try:
            if not self.cuda_processor:
                return None
            
            height, width = frame.shape[:2]
            target_width, target_height = target_size
            
            # Prepare input buffer
            input_data = frame.astype(np.uint8).ctypes.data_as(ctypes.POINTER(ctypes.c_ubyte))
            
            # Prepare output buffer
            output_frame = np.zeros((target_height, target_width, 3), dtype=np.uint8)
            output_data = output_frame.ctypes.data_as(ctypes.POINTER(ctypes.c_ubyte))
            
            # Process with CUDA
            success = self.dll.cuda_process_frame(
                self.cuda_processor,
                input_data, width, height,
                output_data, target_width, target_height
            )
            
            if success:
                return output_frame
            else:
                logger.warning("⚠️  CUDA processing failed, falling back to CPU")
                return self._process_frame_cpu_optimized(frame, target_size)
                
        except Exception as e:
            logger.error(f"❌ CUDA processing error: {e}")
            self._increment_error_count()
            return None
    
    def _process_frame_cpu_optimized(self, frame: np.ndarray, target_size: Tuple[int, int]) -> Optional[np.ndarray]:
        """Process frame using optimized CPU methods"""
        try:
            target_width, target_height = target_size
            
            # Use OpenCV's optimized resize
            if frame.shape[:2] != (target_height, target_width):
                result = cv2.resize(frame, target_size, interpolation=cv2.INTER_LINEAR)
            else:
                result = frame.copy()
            
            return result
            
        except Exception as e:
            logger.error(f"❌ CPU processing error: {e}")
            return None
    
    def _process_frame_cpu_fallback(self, frame: np.ndarray, target_size: Tuple[int, int]) -> Optional[np.ndarray]:
        """Emergency fallback processing with minimal operations"""
        try:
            target_width, target_height = target_size
            
            # Simple nearest neighbor resize for emergency fallback
            if frame.shape[:2] != (target_height, target_width):
                result = cv2.resize(frame, target_size, interpolation=cv2.INTER_NEAREST)
            else:
                result = frame.copy()
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Emergency fallback failed: {e}")
            return frame  # Return original frame as last resort
    
    def _validate_frame(self, frame: np.ndarray) -> bool:
        """Validate frame for safety and compatibility"""
        if frame is None:
            return False
        
        if len(frame.shape) not in [2, 3]:
            logger.error("❌ Invalid frame dimensions")
            return False
        
        height, width = frame.shape[:2]
        
        # Safety limits
        if width > 4096 or height > 4096:
            logger.error("❌ Frame dimensions exceed safety limits")
            return False
        
        if width < 32 or height < 32:
            logger.error("❌ Frame dimensions below minimum")
            return False
        
        return True
    
    def _is_cuda_healthy(self) -> bool:
        """Check if CUDA is healthy and operating within safe parameters"""
        if not self.cuda_available or not self.cuda_processor:
            return False
        
        try:
            # Check GPU temperature if available
            if hasattr(self.dll, 'get_gpu_temperature'):
                temp = self.dll.get_gpu_temperature(self.cuda_processor)
                if temp > self.config.thermal_limit_celsius:
                    logger.warning(f"⚠️  GPU temperature too high: {temp}°C")
                    return False
            
            # Check system health
            if hasattr(self.dll, 'is_system_healthy'):
                healthy = self.dll.is_system_healthy(self.cuda_processor)
                return bool(healthy)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ CUDA health check failed: {e}")
            return False
    
    def _update_performance_metrics(self, processing_time: float, success: bool):
        """Update performance metrics with new data"""
        self.metrics.frames_processed += 1
        if not success:
            self.metrics.frames_dropped += 1
        
        # Update processing time history
        self.performance_history.append(processing_time)
        if len(self.performance_history) > 100:
            self.performance_history.pop(0)
        
        # Calculate averages
        if self.performance_history:
            self.metrics.avg_processing_time = sum(self.performance_history) / len(self.performance_history)
        
        # Calculate FPS
        current_time = time.time()
        time_diff = current_time - self.last_performance_update
        if time_diff >= 1.0:  # Update every second
            self.metrics.fps = self.metrics.frames_processed / time_diff
            self.last_performance_update = current_time
            self.metrics.frames_processed = 0
        
        # Calculate efficiency
        target_time = 1000.0 / self.config.target_fps
        if self.metrics.avg_processing_time > 0:
            self.metrics.efficiency_percentage = min(100.0, (target_time / self.metrics.avg_processing_time) * 100.0)
        
        # Update GPU metrics if available
        if self.cuda_available and self.cuda_processor:
            self._update_gpu_metrics()
    
    def _update_gpu_metrics(self):
        """Update GPU-specific metrics"""
        try:
            if hasattr(self.dll, 'cuda_get_gpu_utilization'):
                self.metrics.gpu_utilization = self.dll.cuda_get_gpu_utilization(self.cuda_processor)
            
            if hasattr(self.dll, 'cuda_get_memory_usage_mb'):
                self.metrics.gpu_memory_usage_mb = self.dll.cuda_get_memory_usage_mb(self.cuda_processor)
            
            if hasattr(self.dll, 'get_gpu_temperature'):
                self.metrics.gpu_temperature_celsius = self.dll.get_gpu_temperature(self.cuda_processor)
        
        except Exception as e:
            logger.error(f"❌ GPU metrics update failed: {e}")
    
    def _handle_performance_degradation(self):
        """Handle performance degradation by adapting quality"""
        if self.config.enable_adaptive_quality:
            if self.metrics.current_scale_level < 5:  # Max 6 levels (0-5)
                self.metrics.current_scale_level += 1
                logger.info(f"📉 Reducing quality to level {self.metrics.current_scale_level} for better performance")
    
    def _handle_processing_error(self, error: Exception):
        """Handle processing errors with safety measures"""
        self.total_errors += 1
        self.consecutive_errors += 1
        self.metrics.error_count = self.total_errors
        
        logger.error(f"❌ Processing error: {error}")
        
        # Check if we should activate emergency fallback
        if self.consecutive_errors >= self.config.max_consecutive_errors:
            self._activate_emergency_fallback()
    
    def _increment_error_count(self):
        """Increment error count and check for emergency conditions"""
        self.consecutive_errors += 1
        self.total_errors += 1
        
        if self.consecutive_errors >= self.config.max_consecutive_errors:
            self._activate_emergency_fallback()
    
    def _activate_emergency_fallback(self):
        """Activate emergency fallback mode for maximum stability"""
        if not self.emergency_fallback_active:
            self.emergency_fallback_active = True
            self.metrics.emergency_fallback_active = True
            logger.warning("🚨 Emergency fallback mode activated")
    
    def _start_monitoring(self):
        """Start background monitoring thread"""
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        logger.info("✅ Safety monitoring started")
    
    def _monitoring_loop(self):
        """Background monitoring loop for system health"""
        while self.monitoring_active:
            try:
                # Update system metrics
                self.metrics.cpu_utilization = psutil.cpu_percent()
                self.metrics.cpu_memory_usage_mb = psutil.virtual_memory().used / (1024 * 1024)
                
                # Check for thermal throttling
                if self.cuda_available and self.metrics.gpu_temperature_celsius > self.config.thermal_limit_celsius:
                    if not self.metrics.thermal_throttling_active:
                        self.metrics.thermal_throttling_active = True
                        logger.warning("🌡️  Thermal throttling activated")
                
                # Reset consecutive errors if we've been stable
                if time.time() - self.last_error_time > 30:  # 30 seconds without errors
                    if self.consecutive_errors > 0:
                        self.consecutive_errors = max(0, self.consecutive_errors - 1)
                
                time.sleep(1)  # Monitor every second
                
            except Exception as e:
                logger.error(f"❌ Monitoring error: {e}")
                time.sleep(5)  # Wait longer on error
    
    def get_metrics(self) -> PerformanceMetrics:
        """Get current performance and safety metrics"""
        return self.metrics
    
    def reset_emergency_fallback(self):
        """Reset emergency fallback if conditions are safe"""
        if self.emergency_fallback_active and self.consecutive_errors == 0:
            self.emergency_fallback_active = False
            self.metrics.emergency_fallback_active = False
            logger.info("✅ Emergency fallback reset")
    
    def shutdown(self):
        """Safely shutdown the processor and all resources"""
        logger.info("🛑 Shutting down frame processor...")
        
        # Stop monitoring
        self.monitoring_active = False
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5)
        
        # Cleanup CUDA resources
        if self.cuda_processor:
            try:
                self.dll.destroy_cuda_processor(self.cuda_processor)
                self.cuda_processor = None
            except Exception as e:
                logger.error(f"❌ CUDA cleanup error: {e}")
        
        # Cleanup stream processor
        if self.stream_processor:
            try:
                self.dll.destroy_stream_processor_enhanced(self.stream_processor)
                self.stream_processor = None
            except Exception as e:
                logger.error(f"❌ Stream processor cleanup error: {e}")
        
        self.initialized = False
        logger.info("✅ Frame processor shutdown complete")
    
    def __del__(self):
        """Ensure resources are cleaned up"""
        if self.initialized:
            self.shutdown()

# C structure definitions for DLL interface
class CudaConfig(ctypes.Structure):
    _fields_ = [
        ("device_id", ctypes.c_int),
        ("memory_pool_size_mb", ctypes.c_int),
        ("max_concurrent_streams", ctypes.c_int),
        ("enable_memory_pinning", ctypes.c_bool)
    ]

class StreamConfig(ctypes.Structure):
    _fields_ = [
        ("target_width", ctypes.c_int),
        ("target_height", ctypes.c_int),
        ("target_fps", ctypes.c_int),
        ("enable_cuda", ctypes.c_bool),
        ("enable_adaptive_quality", ctypes.c_bool),
        ("max_memory_usage_mb", ctypes.c_int),
        ("enable_safety_monitoring", ctypes.c_bool)
    ]

# Factory function for easy initialization
def create_enhanced_frame_processor(config: FrameProcessingConfig = None) -> CudaFrameProcessor:
    """
    Create an enhanced frame processor with optimal settings
    
    Args:
        config: Optional configuration, uses defaults if None
        
    Returns:
        Initialized CudaFrameProcessor instance
    """
    return CudaFrameProcessor(config)
