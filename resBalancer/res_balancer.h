#ifndef RES_BALANCER_H
#define RES_BALANCER_H

#ifdef _WIN32
#define DLLEXPORT __declspec(dllexport)
#else
#define DLLEXPORT
#endif

// Frame processing structure for dynamic resolution management
typedef struct {
    int current_width;
    int current_height;
    int target_width;
    int target_height;
    int startup_frames_processed;
    int frames_since_last_adjust;
    double avg_processing_time;
    double target_fps;
    bool is_startup_complete;
    int skip_factor;
    double scale_factor;
} FrameProcessor;

extern "C" {
    // Original geometry functions
    DLLEXPORT double calculate_distance(double p1_x, double p1_y, double p2_x, double p2_y);
    DLLEXPORT double calculate_roi_overlap_fast(double roi1_x, double roi1_y, double roi1_r,
                                               double roi2_x, double roi2_y, double roi2_r);
    DLLEXPORT int batch_bbox_check(double* points_x, double* points_y, int num_points,
                                  double min_x, double max_x, double min_y, double max_y,
                                  int* results);
    DLLEXPORT void batch_distance_calculation(double* points1_x, double* points1_y,
                                             double* points2_x, double* points2_y,
                                             int num_pairs, double* results);
    
    // New frame processing functions for dynamic resolution management
    DLLEXPORT FrameProcessor* create_frame_processor(int target_width, int target_height, double target_fps);
    DLLEXPORT void destroy_frame_processor(FrameProcessor* processor);
    DLLEXPORT int should_process_frame(FrameProcessor* processor, double processing_time_ms);
    DLLEXPORT void update_processing_stats(FrameProcessor* processor, double processing_time_ms);
    DLLEXPORT void get_optimal_resolution(FrameProcessor* processor, int* width, int* height);
    DLLEXPORT double get_scale_factor(FrameProcessor* processor);
    DLLEXPORT int is_startup_complete(FrameProcessor* processor);
    DLLEXPORT void reset_processor(FrameProcessor* processor);
    
    // Progressive startup management
    DLLEXPORT void calculate_startup_resolution(int target_width, int target_height, 
                                               int startup_frame_count, 
                                               int* current_width, int* current_height);
    DLLEXPORT double calculate_adaptive_skip_factor(double current_fps, double target_fps, 
                                                   double processing_time_ms);
    
    // Frame downscaling for internal processing optimization
    DLLEXPORT int should_downscale_frame(FrameProcessor* processor, int input_width, int input_height,
                                        int* output_width, int* output_height);
    DLLEXPORT double get_processing_scale_factor(FrameProcessor* processor);
    
    // Memory and performance optimization
    DLLEXPORT int estimate_memory_usage(int width, int height, int channels);
    DLLEXPORT void optimize_processing_pipeline(FrameProcessor* processor, 
                                               double cpu_usage, double memory_usage);
    
    // Mirror and transformation handling
    DLLEXPORT int apply_mirror_transform(unsigned char* input_data, int width, int height, 
                                        int channels, unsigned char* output_data, int mirror_horizontal);
    DLLEXPORT int safe_dimension_check(int width, int height);
}

#endif // RES_BALANCER_H