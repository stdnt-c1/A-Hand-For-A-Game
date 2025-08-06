#include "stream_processor.h"
#include "cuda_frame_processor.h"
#include <iostream>
#include <chrono>
#include <algorithm>
#include <cstring>

// OpenCV includes (conditional)
#ifdef WITH_OPENCV
#include <opencv2/opencv.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/core/cuda.hpp>
#endif

#include <thread>
#include <memory>
#include <atomic>
#include <limits.h>

#ifdef _WIN32
#include <windows.h>
#include <psapi.h>
#pragma comment(lib, "psapi.lib")
#else
#include <sys/resource.h>
#include <unistd.h>
#endif

// Scale levels for adaptive quality
static const int SCALE_LEVELS[][2] = {
    {320, 240},   // Level 0: Very low quality
    {480, 360},   // Level 1: Low quality  
    {640, 480},   // Level 2: Medium quality
    {800, 600},   // Level 3: High quality
    {1024, 768}   // Level 4: Full quality
};

HighBandwidthProcessor::HighBandwidthProcessor(const StreamConfig& cfg) 
    : config(cfg), processing_active(false), cuda_context(nullptr), 
      cuda_initialized(false), current_scale_level(2) {
    
    // Initialize metrics
    metrics.avg_processing_time = 0.0;
    metrics.current_fps = 0.0;
    metrics.frames_processed = 0;
    metrics.frames_dropped = 0;
    metrics.gpu_utilization = 0.0;
    metrics.cpu_utilization = 0.0;
    metrics.current_scale_level = 2;
}

HighBandwidthProcessor::~HighBandwidthProcessor() {
    shutdown();
}

bool HighBandwidthProcessor::initialize() {
    try {
        initialize_memory_pools();
        
        if (config.enable_cuda) {
            cuda_initialized = initialize_cuda();
        }
        
        processing_active = true;
        
        if (config.enable_concurrent_processing) {
            processing_thread = std::thread(&HighBandwidthProcessor::processing_loop, this);
            metrics_thread = std::thread(&HighBandwidthProcessor::metrics_loop, this);
        }
        
        return true;
    } catch (const std::exception& e) {
        std::cerr << "Failed to initialize processor: " << e.what() << std::endl;
        return false;
    }
}

void HighBandwidthProcessor::shutdown() {
    processing_active = false;
    
    if (processing_thread.joinable()) {
        input_cv.notify_all();
        processing_thread.join();
    }
    
    if (metrics_thread.joinable()) {
        metrics_thread.join();
    }
    
    cleanup_cuda();
    cleanup_memory_pools();
}

bool HighBandwidthProcessor::submit_frame(const FrameData* frame) {
    if (!frame || !processing_active) return false;
    
    std::unique_lock<std::mutex> lock(input_mutex);
    
    if (input_queue.size() >= static_cast<size_t>(config.max_queue_size)) {
        metrics.frames_dropped++;
        return false;
    }
    
    // Create a copy of the frame data
    FrameData* frame_copy = allocate_frame(frame->width, frame->height, frame->channels);
    if (!frame_copy) return false;
    
    memcpy(frame_copy->data, frame->data, frame->width * frame->height * frame->channels);
    frame_copy->timestamp = frame->timestamp;
    frame_copy->frame_id = frame->frame_id;
    
    input_queue.push(frame_copy);
    input_cv.notify_one();
    
    return true;
}

FrameData* HighBandwidthProcessor::get_processed_frame() {
    std::unique_lock<std::mutex> lock(output_mutex);
    
    if (output_queue.empty()) return nullptr;
    
    FrameData* frame = output_queue.front();
    output_queue.pop();
    
    return frame;
}

void HighBandwidthProcessor::processing_loop() {
    while (processing_active) {
        std::unique_lock<std::mutex> lock(input_mutex);
        input_cv.wait(lock, [this] { return !input_queue.empty() || !processing_active; });
        
        if (!processing_active) break;
        
        FrameData* input_frame = input_queue.front();
        input_queue.pop();
        lock.unlock();
        
        auto start_time = std::chrono::high_resolution_clock::now();
        
        FrameData* output_frame = nullptr;
        if (cuda_initialized && config.enable_cuda) {
            output_frame = process_frame_cuda(input_frame);
        } else {
            output_frame = process_frame_cpu(input_frame);
        }
        
        auto end_time = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time);
        
        processing_times.push_back(duration.count());
        if (processing_times.size() > 100) {
            processing_times.erase(processing_times.begin());
        }
        
        release_frame(input_frame);
        
        if (output_frame) {
            std::unique_lock<std::mutex> output_lock(output_mutex);
            output_queue.push(output_frame);
            output_cv.notify_one();
            metrics.frames_processed++;
        }
    }
}

void HighBandwidthProcessor::metrics_loop() {
    while (processing_active) {
        std::this_thread::sleep_for(std::chrono::seconds(1));
        update_performance_metrics();
        adapt_processing_scale();
    }
}

FrameData* HighBandwidthProcessor::process_frame_cpu(const FrameData* input) {
    if (!input) return nullptr;
    
    int scale_level = current_scale_level.load();
    int target_width = SCALE_LEVELS[scale_level][0];
    int target_height = SCALE_LEVELS[scale_level][1];
    
    FrameData* output = allocate_frame(target_width, target_height, input->channels);
    if (!output) return nullptr;
    
    output->timestamp = input->timestamp;
    output->frame_id = input->frame_id;
    output->processing_scale_level = scale_level;
    
#ifdef WITH_OPENCV
    cv::Mat input_mat(input->height, input->width, CV_8UC3, input->data);
    cv::Mat output_mat(target_height, target_width, CV_8UC3, output->data);
    
    if (target_width != input->width || target_height != input->height) {
        cv::resize(input_mat, output_mat, cv::Size(target_width, target_height), 
                  0, 0, cv::INTER_AREA);
    } else {
        input_mat.copyTo(output_mat);
    }
    
    if (scale_level >= 3) {
        cv::GaussianBlur(output_mat, output_mat, cv::Size(3, 3), 0.5);
    }
#else
    // Basic CPU fallback without OpenCV
    if (target_width != input->width || target_height != input->height) {
        for (int y = 0; y < target_height; y++) {
            for (int x = 0; x < target_width; x++) {
                int src_x = (x * input->width) / target_width;
                int src_y = (y * input->height) / target_height;
                
                src_x = (src_x < input->width - 1) ? src_x : (input->width - 1);
                src_y = (src_y < input->height - 1) ? src_y : (input->height - 1);
                
                for (int c = 0; c < input->channels; c++) {
                    output->data[(y * target_width + x) * input->channels + c] = 
                        input->data[(src_y * input->width + src_x) * input->channels + c];
                }
            }
        }
    } else {
        memcpy(output->data, input->data, input->width * input->height * input->channels);
    }
#endif
    
    return output;
}

FrameData* HighBandwidthProcessor::process_frame_cuda(const FrameData* input) {
    // CUDA implementation - for now, fallback to CPU
    return process_frame_cpu(input);
}

void HighBandwidthProcessor::update_performance_metrics() {
    if (processing_times.empty()) return;
    
    double sum = 0.0;
    for (double time : processing_times) {
        sum += time;
    }
    metrics.avg_processing_time = sum / processing_times.size();
    
    // Calculate FPS based on processing time
    if (metrics.avg_processing_time > 0) {
        metrics.current_fps = 1000.0 / metrics.avg_processing_time;
    }
    
    metrics.current_scale_level = current_scale_level.load();
}

StreamMetrics HighBandwidthProcessor::get_metrics() const {
    return metrics;
}

void HighBandwidthProcessor::adapt_processing_scale() {
    if (metrics.current_fps < config.target_fps * 0.8) {
        // Decrease quality to improve performance
        int new_level = (0 > current_scale_level.load() - 1) ? 0 : (current_scale_level.load() - 1);
        current_scale_level.store(new_level);
    } else if (metrics.current_fps > config.target_fps * 1.2) {
        // Increase quality
        int new_level = (4 < current_scale_level.load() + 1) ? 4 : (current_scale_level.load() + 1);
        current_scale_level.store(new_level);
    }
}

FrameData* HighBandwidthProcessor::allocate_frame(int width, int height, int channels) {
    FrameData* frame = new FrameData();
    frame->width = width;
    frame->height = height;
    frame->channels = channels;
    frame->data = new unsigned char[width * height * channels];
    frame->timestamp = 0.0;
    frame->frame_id = 0;
    frame->processing_scale_level = 0;
    return frame;
}

void HighBandwidthProcessor::release_frame(FrameData* frame) {
    if (frame) {
        delete[] frame->data;
        delete frame;
    }
}

void HighBandwidthProcessor::initialize_memory_pools() {
    // Initialize memory pools for different scale levels
    memory_pools.resize(5);
}

void HighBandwidthProcessor::cleanup_memory_pools() {
    for (auto& pool : memory_pools) {
        for (auto frame : pool) {
            release_frame(frame);
        }
        pool.clear();
    }
}

bool HighBandwidthProcessor::initialize_cuda() {
    try {
        if (cuda_is_available() > 0) {
            cuda_context = reinterpret_cast<void*>(1); // Dummy context
            return true;
        }
    } catch (...) {
        // CUDA initialization failed
    }
    return false;
}

void HighBandwidthProcessor::cleanup_cuda() {
    if (cuda_initialized) {
        // No explicit cleanup function needed - CUDA handles this automatically
        cuda_context = nullptr;
        cuda_initialized = false;
    }
}

// C API Implementation
extern "C" {
    DLLEXPORT HighBandwidthProcessor* create_stream_processor(StreamConfig config) {
        try {
            return new HighBandwidthProcessor(config);
        } catch (...) {
            return nullptr;
        }
    }
    
    DLLEXPORT void destroy_stream_processor(HighBandwidthProcessor* processor) {
        delete processor;
    }
    
    DLLEXPORT int submit_frame_data(HighBandwidthProcessor* processor, 
                                   unsigned char* data, int width, int height, 
                                   int channels, double timestamp) {
        if (!processor || !data) return 0;
        
        FrameData frame;
        frame.width = width;
        frame.height = height;
        frame.channels = channels;
        frame.data = data;
        frame.timestamp = timestamp;
        frame.frame_id = 0;
        
        return processor->submit_frame(&frame) ? 1 : 0;
    }
    
    DLLEXPORT int get_processed_frame_data(HighBandwidthProcessor* processor,
                                          unsigned char** data, int* width, int* height,
                                          int* channels, double* timestamp) {
        if (!processor) return 0;
        
        FrameData* frame = processor->get_processed_frame();
        if (!frame) return 0;
        
        *data = frame->data;
        *width = frame->width;
        *height = frame->height;
        *channels = frame->channels;
        *timestamp = frame->timestamp;
        
        return 1;
    }
    
    DLLEXPORT StreamMetrics get_stream_metrics(HighBandwidthProcessor* processor) {
        if (processor) {
            return processor->get_metrics();
        }
        StreamMetrics empty = {0};
        return empty;
    }
    
    DLLEXPORT void release_frame_data(HighBandwidthProcessor* processor, unsigned char* data) {
        // Frame data cleanup handled by processor
    }
    
    DLLEXPORT void set_target_fps(HighBandwidthProcessor* processor, int fps) {
        // Implementation would update the target FPS
    }
    
    DLLEXPORT void enable_cuda_processing(HighBandwidthProcessor* processor, int enable) {
        // Implementation would toggle CUDA processing
    }
    
    DLLEXPORT void force_scale_level(HighBandwidthProcessor* processor, int level) {
        // Implementation would force a specific scale level
    }
    
    DLLEXPORT int get_optimal_scale_level(HighBandwidthProcessor* processor, 
                                        double cpu_usage, double gpu_usage) {
        // Implementation would calculate optimal scale based on system load
        return 2; // Default to medium quality
    }
    
    DLLEXPORT int get_memory_usage_mb(HighBandwidthProcessor* processor) {
        // Implementation would return memory usage
        return 0;
    }
    
    DLLEXPORT void optimize_memory_pools(HighBandwidthProcessor* processor) {
        // Implementation would optimize memory pools
    }
}
