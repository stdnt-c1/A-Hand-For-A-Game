#ifndef CUDA_FRAME_PROCESSOR_H
#define CUDA_FRAME_PROCESSOR_H

#include <vector>
#include <memory>
#include <chrono>
#include <atomic>

#ifdef _WIN32
#define DLLEXPORT __declspec(dllexport)
#else
#define DLLEXPORT
#endif

// CUDA-specific frame processing for maximum performance
typedef struct {
    void* d_input;       // Device input buffer
    void* d_output;      // Device output buffer
    void* d_temp;        // Device temporary buffer
    int width;
    int height;
    int channels;
    size_t pitch;        // Memory pitch for 2D arrays
} CudaFrameBuffer;

typedef struct {
    int device_id;
    size_t memory_pool_size_mb;
    int max_concurrent_streams;
    bool enable_tensor_cores;
    bool enable_memory_pinning;
} CudaConfig;

class CudaFrameProcessor {
private:
    CudaConfig config;
    void* cuda_context;
    void* cuda_streams[8];  // Multiple CUDA streams for concurrency
    
    // Memory management
    std::vector<CudaFrameBuffer> frame_buffers;
    void* memory_pool;
    size_t memory_pool_size;
    
    // Performance tracking
    float* processing_times;
    int time_index;
    std::atomic<bool> initialized;  // Use atomic for thread safety
    
public:
    CudaFrameProcessor(const CudaConfig& config);
    ~CudaFrameProcessor();
    
    bool initialize();
    void shutdown();
    
    // High-performance frame processing
    bool process_frame_async(const unsigned char* input, int width, int height,
                           unsigned char* output, int output_width, int output_height,
                           int stream_id = 0);
    bool wait_for_completion(int stream_id = 0);
    
    // Batch processing for maximum throughput
    bool process_frame_batch(unsigned char** inputs, int batch_size,
                           int width, int height, unsigned char** outputs,
                           int output_width, int output_height);
    
    // Memory management
    CudaFrameBuffer* allocate_frame_buffer(int width, int height, int channels);
    void release_frame_buffer(CudaFrameBuffer* buffer);
    
    // Performance utilities
    float get_average_processing_time() const;
    float get_gpu_utilization() const;
    size_t get_memory_usage() const;
    
private:
    bool allocate_memory_pools();
    void cleanup_memory_pools();
    bool create_cuda_streams();
    void cleanup_cuda_streams();  // Add missing method declaration
    void destroy_cuda_streams();
};

extern "C" {
    // C API for CUDA frame processing
    DLLEXPORT CudaFrameProcessor* create_cuda_processor(CudaConfig config);
    DLLEXPORT void destroy_cuda_processor(CudaFrameProcessor* processor);
    
    DLLEXPORT int cuda_process_frame(CudaFrameProcessor* processor,
                                   unsigned char* input, int width, int height,
                                   unsigned char* output, int output_width, int output_height);
    
    DLLEXPORT int cuda_process_frame_batch(CudaFrameProcessor* processor,
                                         unsigned char** inputs, int batch_size,
                                         int width, int height,
                                         unsigned char** outputs,
                                         int output_width, int output_height);
    
    DLLEXPORT float cuda_get_processing_time(CudaFrameProcessor* processor);
    DLLEXPORT float cuda_get_gpu_utilization(CudaFrameProcessor* processor);
    DLLEXPORT int cuda_get_memory_usage_mb(CudaFrameProcessor* processor);
    
    // CUDA device management
    DLLEXPORT int cuda_get_device_count();
    DLLEXPORT int cuda_get_device_memory_mb(int device_id);
    DLLEXPORT int cuda_set_device(int device_id);
    DLLEXPORT int cuda_is_available();
}

#endif // CUDA_FRAME_PROCESSOR_H
