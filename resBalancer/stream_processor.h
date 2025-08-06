#ifndef STREAM_PROCESSOR_H
#define STREAM_PROCESSOR_H

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

// Frame data structure for high-bandwidth streaming
typedef struct {
    int width;
    int height;
    int channels;
    unsigned char* data;
    double timestamp;
    int frame_id;
    int processing_scale_level;
} FrameData;

// Streaming configuration
typedef struct {
    int input_width;
    int input_height;
    int target_fps;
    int max_queue_size;
    double max_processing_time_ms;
    bool enable_cuda;
    bool enable_concurrent_processing;
} StreamConfig;

// Performance metrics
typedef struct {
    double avg_processing_time;
    double current_fps;
    int frames_processed;
    int frames_dropped;
    double gpu_utilization;
    double cpu_utilization;
    int current_scale_level;
} StreamMetrics;

// High-bandwidth frame processor class
class HighBandwidthProcessor {
private:
    StreamConfig config;
    StreamMetrics metrics;
    
    // Threading components
    std::atomic<bool> processing_active;
    std::thread processing_thread;
    std::thread metrics_thread;
    
    // Queue management
    std::queue<FrameData*> input_queue;
    std::queue<FrameData*> output_queue;
    std::mutex input_mutex;
    std::mutex output_mutex;
    std::condition_variable input_cv;
    std::condition_variable output_cv;
    
    // Performance tracking
    std::vector<double> processing_times;
    std::atomic<int> current_scale_level;
    
    // CUDA context (if available)
    void* cuda_context;
    bool cuda_initialized;
    
    // Memory pools for different scales
    std::vector<std::vector<FrameData*>> memory_pools;
    
public:
    HighBandwidthProcessor(const StreamConfig& config);
    ~HighBandwidthProcessor();
    
    // Core streaming functions
    bool initialize();
    void shutdown();
    bool submit_frame(const FrameData* frame);
    FrameData* get_processed_frame();
    
    // Performance management
    void update_performance_metrics();
    StreamMetrics get_metrics() const;
    void adapt_processing_scale();
    
    // Memory management
    FrameData* allocate_frame(int width, int height, int channels);
    void release_frame(FrameData* frame);
    
private:
    // Internal processing methods
    void processing_loop();
    void metrics_loop();
    FrameData* process_frame_cpu(const FrameData* input);
    FrameData* process_frame_cuda(const FrameData* input);
    void initialize_memory_pools();
    void cleanup_memory_pools();
    bool initialize_cuda();
    void cleanup_cuda();
};

extern "C" {
    // C API for Python integration
    DLLEXPORT HighBandwidthProcessor* create_stream_processor(StreamConfig config);
    DLLEXPORT void destroy_stream_processor(HighBandwidthProcessor* processor);
    DLLEXPORT int submit_frame_data(HighBandwidthProcessor* processor, 
                                   unsigned char* data, int width, int height, 
                                   int channels, double timestamp);
    DLLEXPORT int get_processed_frame_data(HighBandwidthProcessor* processor,
                                          unsigned char** data, int* width, int* height,
                                          int* channels, double* timestamp);
    DLLEXPORT StreamMetrics get_stream_metrics(HighBandwidthProcessor* processor);
    DLLEXPORT void release_frame_data(HighBandwidthProcessor* processor, unsigned char* data);
    
    // Performance optimization functions
    DLLEXPORT void set_target_fps(HighBandwidthProcessor* processor, int fps);
    DLLEXPORT void enable_cuda_processing(HighBandwidthProcessor* processor, int enable);
    DLLEXPORT void force_scale_level(HighBandwidthProcessor* processor, int level);
    DLLEXPORT int get_optimal_scale_level(HighBandwidthProcessor* processor, 
                                        double cpu_usage, double gpu_usage);
    
    // Memory management functions
    DLLEXPORT int get_memory_usage_mb(HighBandwidthProcessor* processor);
    DLLEXPORT void optimize_memory_pools(HighBandwidthProcessor* processor);
}

#endif // STREAM_PROCESSOR_H
