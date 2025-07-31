import time
import threading
from collections import deque
import numpy as np

class PerformanceOptimizer:
    """
    Manages performance optimization for gesture recognition system.
    Implements adaptive frame processing, gesture caching, and load balancing.
    """
    
    def __init__(self):
        self.target_fps = 30  # Reduced from 60 to 30 for stability
        self.frame_time_buffer = deque(maxlen=10)
        self.gesture_cache = {}
        self.cache_timeout = 0.1  # 100ms cache validity
        self.adaptive_quality = True
        self.processing_skip_factor = 1
        self.last_process_time = 0.0
        
        # Performance metrics
        self.cpu_threshold_high = 80.0
        self.cpu_threshold_low = 60.0
        self.memory_threshold = 85.0
        
        # Gesture processing queue for async processing
        self.gesture_queue = deque(maxlen=5)
        self.processing_thread = None
        self.stop_processing = False
        
    def should_process_frame(self):
        """Determine if current frame should be processed based on performance."""
        current_time = time.time()
        
        # Skip frames if processing is too slow
        if current_time - self.last_process_time < (1.0 / self.target_fps):
            return False
            
        return True
    
    def update_performance_metrics(self, frame_time, cpu_usage, memory_usage):
        """Update performance metrics and adjust processing parameters."""
        self.frame_time_buffer.append(frame_time)
        
        avg_frame_time = np.mean(self.frame_time_buffer)
        
        # Adaptive quality adjustment
        if cpu_usage > self.cpu_threshold_high or memory_usage > self.memory_threshold:
            self.processing_skip_factor = min(4, self.processing_skip_factor + 1)
            self.target_fps = max(15, self.target_fps - 5)
        elif cpu_usage < self.cpu_threshold_low and avg_frame_time < 0.02:
            self.processing_skip_factor = max(1, self.processing_skip_factor - 1)
            self.target_fps = min(30, self.target_fps + 2)
    
    def get_cached_gesture(self, landmarks_hash):
        """Get cached gesture result if still valid."""
        if landmarks_hash in self.gesture_cache:
            cached_result, timestamp = self.gesture_cache[landmarks_hash]
            if time.time() - timestamp < self.cache_timeout:
                return cached_result
        return None
    
    def cache_gesture(self, landmarks_hash, result):
        """Cache gesture result."""
        self.gesture_cache[landmarks_hash] = (result, time.time())
        
        # Clean old cache entries
        current_time = time.time()
        expired_keys = [k for k, (_, t) in self.gesture_cache.items() 
                       if current_time - t > self.cache_timeout]
        for key in expired_keys:
            del self.gesture_cache[key]
    
    def create_landmarks_hash(self, landmarks):
        """Create a hash for landmarks to use as cache key."""
        # Use rounded coordinates to allow for small variations
        coords = []
        for lm in landmarks.landmark:
            coords.extend([round(lm.x, 3), round(lm.y, 3)])
        return hash(tuple(coords))
    
    def start_async_processing(self):
        """Start asynchronous gesture processing thread."""
        if self.processing_thread is None or not self.processing_thread.is_alive():
            self.stop_processing = False
            self.processing_thread = threading.Thread(target=self._async_processor)
            self.processing_thread.daemon = True
            self.processing_thread.start()
    
    def stop_async_processing(self):
        """Stop asynchronous processing."""
        self.stop_processing = True
        if self.processing_thread:
            self.processing_thread.join(timeout=1.0)
    
    def _async_processor(self):
        """Background thread for processing gestures."""
        while not self.stop_processing:
            if self.gesture_queue:
                try:
                    gesture_data = self.gesture_queue.popleft()
                    # Process gesture data here
                    time.sleep(0.001)  # Small delay to prevent CPU spinning
                except IndexError:
                    pass
            else:
                time.sleep(0.005)  # Wait if no data
