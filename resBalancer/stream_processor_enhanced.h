#ifndef STREAM_PROCESSOR_ENHANCED_H
#define STREAM_PROCESSOR_ENHANCED_H

#ifdef _WIN32
#define DLLEXPORT __declspec(dllexport)
#else
#define DLLEXPORT
#endif

#include <vector>
#include <memory>
#include <atomic>
#include <thread>
#include <queue>
#include <mutex>
#include <condition_variable>
#include <chrono>

// Enhanced configuration structure with comprehensive safety and performance settings
typedef struct {
    // Basic settings
    int input_width = 640;
    int input_height = 480;
    int target_width = 640;
    int target_height = 480;
    int target_fps = 30;
    int max_queue_size = 10;
    
    // Performance settings
    double max_processing_time_ms = 100.0;
    bool enable_cuda = true;
    bool enable_concurrent_processing = true;
    bool enable_adaptive_quality = true;
    int max_threads = 4;
    
    // Memory management
    int max_memory_usage_mb = 512;
    bool enable_memory_pinning = false;
    
    // Safety and monitoring
    bool enable_safety_monitoring = true;
    bool enable_emergency_fallback = true;
    double thermal_limit_celsius = 85.0;
    int max_consecutive_errors = 10;
    
    // Advanced features
    bool enable_async_processing = true;
    bool enable_batch_processing = false;
    int batch_size = 4;
} StreamConfig;

// Enhanced frame data structure with comprehensive metadata
typedef struct {
    int width;
    int height;
    int channels;
    unsigned char* data;
    double timestamp;
    int frame_id;
    
    // Processing metadata
    int processing_scale_level;
    bool cuda_processed;
    double processing_time_ms;
    bool emergency_fallback_used;
    
    // Quality metrics
    double quality_score;
    int compression_level;
    bool adaptive_scaling_applied;
} FrameData;

// Comprehensive performance and safety metrics
typedef struct {
    // Performance metrics
    double avg_processing_time;
    double current_fps;
    double target_fps;
    double efficiency_percentage;
    
    // Processing statistics
    int frames_processed;
    int frames_dropped;
    int frames_in_queue;
    
    // GPU metrics
    double gpu_utilization;
    double gpu_memory_usage_mb;
    double gpu_temperature_celsius;
    
    // CPU metrics
    double cpu_utilization;
    double cpu_memory_usage_mb;
    
    // Quality metrics
    int current_scale_level;
    double average_quality_score;
    
    // Safety metrics
    int error_count;
    int consecutive_errors;
    bool emergency_fallback_active;
    bool thermal_throttling_active;
    
    // System health
    double system_load_average;
    bool cuda_healthy;
    bool memory_pressure_detected;
} StreamMetrics;

// Advanced high-bandwidth frame processor with comprehensive safety features
class HighBandwidthProcessor {
private:
    StreamConfig config;
    StreamMetrics metrics;
    
    // Core threading components
    std::atomic<bool> processing_active;
    std::thread processing_thread;
    std::thread metrics_thread;
    std::thread safety_monitor_thread;
    std::thread performance_optimizer_thread;
    
    // Queue management with overflow protection
    std::queue<FrameData*> input_queue;
    std::queue<FrameData*> output_queue;
    std::mutex input_mutex;
    std::mutex output_mutex;
    std::condition_variable input_cv;
    std::condition_variable output_cv;
    
    // Performance tracking and optimization
    std::vector<double> processing_times;
    std::vector<double> gpu_utilization_history;
    std::atomic<int> current_scale_level;
    std::chrono::high_resolution_clock::time_point last_performance_check;
    
    // Safety and error handling
    std::atomic<int> error_count;
    std::atomic<int> consecutive_errors;
    std::atomic<bool> emergency_fallback_active;
    std::atomic<bool> thermal_throttling_active;
    std::atomic<bool> safety_monitor_active;
    
    // CUDA context and advanced GPU management
    void* cuda_context;
    std::atomic<bool> cuda_initialized;
    std::atomic<bool> cuda_healthy;
    
    // Advanced memory management
    std::vector<std::vector<FrameData*>> memory_pools;
    std::vector<unsigned char> cpu_memory_pool;
    std::atomic<size_t> current_memory_usage;
    
    // Performance optimization
    std::atomic<bool> performance_optimizer_active;
    double adaptive_quality_factor;
    
public:
    HighBandwidthProcessor(const StreamConfig& config);
    ~HighBandwidthProcessor();
    
    // Core streaming functions with enhanced error handling
    bool initialize();
    void shutdown();
    bool submit_frame(const FrameData* frame);
    FrameData* get_processed_frame();
    bool submit_frame_async(const FrameData* frame);
    bool get_processed_frame_batch(FrameData** frames, int max_count, int* actual_count);
    
    // Advanced performance management
    void update_performance_metrics();
    StreamMetrics get_metrics() const;
    void adapt_processing_scale();
    void optimize_for_target_fps(double target_fps);
    bool is_performing_optimally() const;
    
    // Safety and monitoring
    void enable_safety_monitoring(bool enable);
    bool check_system_health();
    void handle_emergency_fallback();
    void reset_error_counters();
    
    // GPU and CUDA management
    bool is_cuda_available() const;
    bool is_cuda_healthy() const;
    void force_cuda_reset();
    double get_gpu_temperature() const;
    
    // Memory management with safety
    FrameData* allocate_frame_safe(int width, int height, int channels);
    void release_frame_safe(FrameData* frame);
    size_t get_memory_usage_bytes() const;
    bool is_memory_pressure_detected() const;
    void optimize_memory_usage();
    
    // Configuration management
    void update_config(const StreamConfig& new_config);
    StreamConfig get_current_config() const;
    
private:
    // Enhanced internal processing methods
    void processing_loop();
    void metrics_loop();
    void safety_monitor_loop();
    void performance_optimizer_loop();
    
    // Frame processing with fallback
    FrameData* process_frame_safe(const FrameData* input);
    FrameData* process_frame_cpu_optimized(const FrameData* input);
    FrameData* process_frame_cuda_safe(const FrameData* input);
    
    // Advanced initialization and cleanup
    bool validate_configuration();
    bool initialize_memory_pools_safe();
    bool initialize_cuda_safe();
    void cleanup_memory_pools_safe();
    void cleanup_cuda_safe();
    
    // Safety and monitoring helpers
    void monitor_system_health();
    void monitor_gpu_health();
    void handle_processing_error(const std::exception& e);
    bool should_activate_emergency_fallback();
    
    // Performance optimization helpers
    void calculate_optimal_scale_level();
    void adjust_processing_parameters();
    double calculate_quality_score(const FrameData* frame);
    void update_adaptive_quality_factor();
};

extern "C" {
    // Enhanced C API for Python integration
    DLLEXPORT HighBandwidthProcessor* create_stream_processor_enhanced(StreamConfig config);
    DLLEXPORT void destroy_stream_processor_enhanced(HighBandwidthProcessor* processor);
    
    // Core processing functions
    DLLEXPORT int submit_frame_data_safe(HighBandwidthProcessor* processor, 
                                        unsigned char* data, int width, int height, 
                                        int channels, double timestamp);
    DLLEXPORT int get_processed_frame_data_safe(HighBandwidthProcessor* processor,
                                               unsigned char** data, int* width, int* height,
                                               int* channels, double* timestamp);
    
    // Batch processing
    DLLEXPORT int submit_frame_batch(HighBandwidthProcessor* processor,
                                    unsigned char** data_array, int* widths, int* heights,
                                    int batch_size, double* timestamps);
    DLLEXPORT int get_processed_frame_batch(HighBandwidthProcessor* processor,
                                           unsigned char*** data_array, int* widths, int* heights,
                                           int max_count, int* actual_count);
    
    // Enhanced metrics and monitoring
    DLLEXPORT StreamMetrics get_stream_metrics_enhanced(HighBandwidthProcessor* processor);
    DLLEXPORT int is_system_healthy(HighBandwidthProcessor* processor);
    DLLEXPORT int is_emergency_fallback_active(HighBandwidthProcessor* processor);
    DLLEXPORT double get_current_fps(HighBandwidthProcessor* processor);
    DLLEXPORT double get_processing_efficiency(HighBandwidthProcessor* processor);
    
    // GPU and CUDA functions
    DLLEXPORT int is_cuda_available_safe();
    DLLEXPORT int get_gpu_device_count();
    DLLEXPORT double get_gpu_utilization(HighBandwidthProcessor* processor);
    DLLEXPORT double get_gpu_memory_usage_mb(HighBandwidthProcessor* processor);
    DLLEXPORT double get_gpu_temperature(HighBandwidthProcessor* processor);
    DLLEXPORT int force_gpu_reset(HighBandwidthProcessor* processor);
    
    // Performance optimization
    DLLEXPORT void optimize_for_target_fps(HighBandwidthProcessor* processor, double target_fps);
    DLLEXPORT void enable_adaptive_quality(HighBandwidthProcessor* processor, int enable);
    DLLEXPORT void force_scale_level_safe(HighBandwidthProcessor* processor, int level);
    DLLEXPORT int get_optimal_scale_level(HighBandwidthProcessor* processor);
    
    // Safety and error handling
    DLLEXPORT void enable_safety_monitoring(HighBandwidthProcessor* processor, int enable);
    DLLEXPORT void reset_error_counters(HighBandwidthProcessor* processor);
    DLLEXPORT int get_error_count(HighBandwidthProcessor* processor);
    DLLEXPORT void handle_emergency_shutdown(HighBandwidthProcessor* processor);
    
    // Memory management
    DLLEXPORT size_t get_memory_usage_bytes(HighBandwidthProcessor* processor);
    DLLEXPORT int is_memory_pressure_detected(HighBandwidthProcessor* processor);
    DLLEXPORT void optimize_memory_usage(HighBandwidthProcessor* processor);
    DLLEXPORT void release_frame_data_safe(HighBandwidthProcessor* processor, unsigned char* data);
    
    // Configuration management
    DLLEXPORT void update_stream_config(HighBandwidthProcessor* processor, StreamConfig config);
    DLLEXPORT StreamConfig get_current_stream_config(HighBandwidthProcessor* processor);
}

#endif // STREAM_PROCESSOR_ENHANCED_H
