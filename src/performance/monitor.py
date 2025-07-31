import time
import threading
from collections import deque
import json

class PerformanceMonitor:
    """
    Real-time performance monitoring for the gesture recognition system.
    """
    
    def __init__(self):
        self.metrics = {
            'frame_times': deque(maxlen=60),
            'gesture_processing_times': deque(maxlen=60),
            'cpu_usage': deque(maxlen=60),
            'memory_usage': deque(maxlen=60),
            'gpu_usage': deque(maxlen=60),
            'cache_hit_rate': deque(maxlen=60),
            'gesture_counts': {},
            'performance_warnings': deque(maxlen=20)
        }
        
        self.thresholds = {
            'max_frame_time': 0.033,  # 30 FPS
            'max_processing_time': 0.020,  # 20ms
            'max_cpu_usage': 85.0,
            'max_memory_usage': 90.0,
            'min_cache_hit_rate': 0.3
        }
        
        self.monitoring_active = False
        self.monitor_thread = None
        
    def start_monitoring(self):
        """Start the performance monitoring thread."""
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
    def stop_monitoring(self):
        """Stop the performance monitoring."""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
    
    def log_frame_time(self, frame_time):
        """Log frame processing time."""
        self.metrics['frame_times'].append(frame_time)
        
        if frame_time > self.thresholds['max_frame_time']:
            self._add_warning(f"High frame time: {frame_time:.3f}s")
    
    def log_gesture_processing_time(self, processing_time):
        """Log gesture processing time."""
        self.metrics['gesture_processing_times'].append(processing_time)
        
        if processing_time > self.thresholds['max_processing_time']:
            self._add_warning(f"High processing time: {processing_time:.3f}s")
    
    def log_system_metrics(self, cpu_usage, memory_usage, gpu_usage=0):
        """Log system resource usage."""
        self.metrics['cpu_usage'].append(cpu_usage)
        self.metrics['memory_usage'].append(memory_usage)
        self.metrics['gpu_usage'].append(gpu_usage)
        
        if cpu_usage > self.thresholds['max_cpu_usage']:
            self._add_warning(f"High CPU usage: {cpu_usage:.1f}%")
        
        if memory_usage > self.thresholds['max_memory_usage']:
            self._add_warning(f"High memory usage: {memory_usage:.1f}%")
    
    def log_gesture_detection(self, gesture_type, gesture_name):
        """Log detected gestures for analysis."""
        key = f"{gesture_type}_{gesture_name}"
        self.metrics['gesture_counts'][key] = self.metrics['gesture_counts'].get(key, 0) + 1
    
    def log_cache_performance(self, cache_hits, total_requests):
        """Log cache performance metrics."""
        hit_rate = cache_hits / total_requests if total_requests > 0 else 0
        self.metrics['cache_hit_rate'].append(hit_rate)
        
        if hit_rate < self.thresholds['min_cache_hit_rate']:
            self._add_warning(f"Low cache hit rate: {hit_rate:.2f}")
    
    def get_performance_summary(self):
        """Get a summary of current performance metrics."""
        summary = {}
        
        if self.metrics['frame_times']:
            frame_times = list(self.metrics['frame_times'])
            summary['avg_frame_time'] = sum(frame_times) / len(frame_times)
            summary['max_frame_time'] = max(frame_times)
            summary['current_fps'] = 1.0 / summary['avg_frame_time'] if summary['avg_frame_time'] > 0 else 0
        
        if self.metrics['gesture_processing_times']:
            proc_times = list(self.metrics['gesture_processing_times'])
            summary['avg_processing_time'] = sum(proc_times) / len(proc_times)
            summary['max_processing_time'] = max(proc_times)
        
        if self.metrics['cpu_usage']:
            cpu_usage = list(self.metrics['cpu_usage'])
            summary['avg_cpu_usage'] = sum(cpu_usage) / len(cpu_usage)
            summary['max_cpu_usage'] = max(cpu_usage)
        
        if self.metrics['memory_usage']:
            mem_usage = list(self.metrics['memory_usage'])
            summary['avg_memory_usage'] = sum(mem_usage) / len(mem_usage)
            summary['max_memory_usage'] = max(mem_usage)
        
        if self.metrics['cache_hit_rate']:
            hit_rates = list(self.metrics['cache_hit_rate'])
            summary['avg_cache_hit_rate'] = sum(hit_rates) / len(hit_rates)
        
        summary['gesture_counts'] = dict(self.metrics['gesture_counts'])
        summary['recent_warnings'] = list(self.metrics['performance_warnings'])
        
        return summary
    
    def _add_warning(self, warning_msg):
        """Add a performance warning."""
        timestamp = time.strftime("%H:%M:%S")
        self.metrics['performance_warnings'].append(f"[{timestamp}] {warning_msg}")
    
    def _monitor_loop(self):
        """Background monitoring loop."""
        while self.monitoring_active:
            # Perform periodic analysis and cleanup
            self._analyze_performance_trends()
            time.sleep(5.0)  # Check every 5 seconds
    
    def _analyze_performance_trends(self):
        """Analyze performance trends and generate insights."""
        if len(self.metrics['frame_times']) < 30:
            return  # Not enough data
        
        recent_frame_times = list(self.metrics['frame_times'])[-30:]
        avg_recent = sum(recent_frame_times) / len(recent_frame_times)
        
        # Check for performance degradation
        if avg_recent > self.thresholds['max_frame_time'] * 1.2:
            self._add_warning("Performance degradation detected")
    
    def export_metrics(self, filename):
        """Export metrics to a JSON file for analysis."""
        export_data = {
            'timestamp': time.time(),
            'summary': self.get_performance_summary(),
            'raw_metrics': {
                'frame_times': list(self.metrics['frame_times']),
                'processing_times': list(self.metrics['gesture_processing_times']),
                'cpu_usage': list(self.metrics['cpu_usage']),
                'memory_usage': list(self.metrics['memory_usage']),
                'cache_hit_rates': list(self.metrics['cache_hit_rate'])
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"Performance metrics exported to {filename}")
    
    def reset_metrics(self):
        """Reset all metrics for a fresh start."""
        for key in self.metrics:
            if isinstance(self.metrics[key], deque):
                self.metrics[key].clear()
            elif isinstance(self.metrics[key], dict):
                self.metrics[key].clear()
