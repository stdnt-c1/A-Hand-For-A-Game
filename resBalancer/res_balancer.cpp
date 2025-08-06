#include "res_balancer.h"
#include <cmath>
#include <algorithm>
#include <cstdlib>
#include <cstring>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

extern "C" {
    // Original geometry functions
    DLLEXPORT double calculate_distance(double p1_x, double p1_y, double p2_x, double p2_y) {
        return std::hypot(p1_x - p2_x, p1_y - p2_y);
    }
    
    DLLEXPORT double calculate_roi_overlap_fast(double roi1_x, double roi1_y, double roi1_r,
                                               double roi2_x, double roi2_y, double roi2_r) {
        double dist = calculate_distance(roi1_x, roi1_y, roi2_x, roi2_y);
        double r1 = roi1_r, r2 = roi2_r;
        
        if (dist >= r1 + r2) {
            return 0.0;
        }
        
        if (dist <= std::abs(r1 - r2)) {
            double smaller_roi_area = M_PI * std::min(r1, r2) * std::min(r1, r2);
            return smaller_roi_area > 0 ? 100.0 : 0.0;
        }
        
        double r1_sq = r1 * r1, r2_sq = r2 * r2;
        double dist_sq = dist * dist;
        
        double angle1 = std::acos((dist_sq + r1_sq - r2_sq) / (2 * dist * r1));
        double angle2 = std::acos((dist_sq + r2_sq - r1_sq) / (2 * dist * r2));
        
        double intersection_area = (r1_sq * angle1) + (r2_sq * angle2) - 
                                  0.5 * std::sqrt((-dist + r1 + r2) * (dist + r1 - r2) * 
                                                 (dist - r1 + r2) * (dist + r1 + r2));
        
        double smaller_roi_area = M_PI * std::min(r1, r2) * std::min(r1, r2);
        
        return smaller_roi_area == 0 ? 0.0 : (intersection_area / smaller_roi_area) * 100.0;
    }
    
    DLLEXPORT int batch_bbox_check(double* points_x, double* points_y, int num_points,
                                  double min_x, double max_x, double min_y, double max_y,
                                  int* results) {
        int inside_count = 0;
        for (int i = 0; i < num_points; i++) {
            results[i] = (points_x[i] >= min_x && points_x[i] <= max_x &&
                         points_y[i] >= min_y && points_y[i] <= max_y) ? 1 : 0;
            inside_count += results[i];
        }
        return inside_count;
    }
    
    DLLEXPORT void batch_distance_calculation(double* points1_x, double* points1_y,
                                             double* points2_x, double* points2_y,
                                             int num_pairs, double* results) {
        for (int i = 0; i < num_pairs; i++) {
            results[i] = calculate_distance(points1_x[i], points1_y[i], 
                                          points2_x[i], points2_y[i]);
        }
    }
    
    // === NEW: Dynamic Frame Processing Functions ===
    
    DLLEXPORT FrameProcessor* create_frame_processor(int target_width, int target_height, double target_fps) {
        FrameProcessor* processor = (FrameProcessor*)malloc(sizeof(FrameProcessor));
        if (!processor) return nullptr;
        
        processor->target_width = target_width;
        processor->target_height = target_height;
        processor->target_fps = target_fps;
        
        // Start with reduced resolution for cold start
        processor->current_width = std::max(320, target_width / 4);
        processor->current_height = std::max(240, target_height / 4);
        
        processor->startup_frames_processed = 0;
        processor->frames_since_last_adjust = 0;
        processor->avg_processing_time = 0.0;
        processor->is_startup_complete = false;
        processor->skip_factor = 1;
        processor->scale_factor = (double)processor->current_width / target_width;
        
        return processor;
    }
    
    DLLEXPORT void destroy_frame_processor(FrameProcessor* processor) {
        if (processor) {
            free(processor);
        }
    }
    
    DLLEXPORT int should_process_frame(FrameProcessor* processor, double processing_time_ms) {
        if (!processor) return 1;
        
        processor->frames_since_last_adjust++;
        
        // During startup, be more aggressive with frame skipping
        if (!processor->is_startup_complete) {
            // Skip more frames if processing time is high
            double time_threshold = 1000.0 / processor->target_fps; // Target frame time
            if (processing_time_ms > time_threshold * 1.5) {
                processor->skip_factor = std::min(4, processor->skip_factor + 1);
            } else if (processing_time_ms < time_threshold * 0.8) {
                processor->skip_factor = std::max(1, processor->skip_factor - 1);
            }
            
            return (processor->frames_since_last_adjust % processor->skip_factor) == 0;
        }
        
        // After startup, use normal processing
        return 1;
    }
    
    DLLEXPORT void update_processing_stats(FrameProcessor* processor, double processing_time_ms) {
        if (!processor) return;
        
        // Update rolling average processing time
        double alpha = 0.1; // Smoothing factor
        if (processor->avg_processing_time == 0.0) {
            processor->avg_processing_time = processing_time_ms;
        } else {
            processor->avg_processing_time = alpha * processing_time_ms + 
                                           (1.0 - alpha) * processor->avg_processing_time;
        }
        
        processor->startup_frames_processed++;
        
        // Check if we should progress to next resolution stage
        if (!processor->is_startup_complete && processor->startup_frames_processed % 30 == 0) {
            double target_frame_time = 1000.0 / processor->target_fps;
            
            // If processing time is good, increase resolution
            if (processor->avg_processing_time < target_frame_time * 0.7) {
                int new_width = std::min(processor->target_width, 
                                       (int)(processor->current_width * 1.5));
                int new_height = std::min(processor->target_height, 
                                        (int)(processor->current_height * 1.5));
                
                if (new_width != processor->current_width) {
                    processor->current_width = new_width;
                    processor->current_height = new_height;
                    processor->scale_factor = (double)processor->current_width / processor->target_width;
                }
                
                // Mark startup complete when target resolution reached
                if (processor->current_width >= processor->target_width) {
                    processor->is_startup_complete = true;
                    processor->skip_factor = 1;
                }
            }
        }
    }
    
    DLLEXPORT void get_optimal_resolution(FrameProcessor* processor, int* width, int* height) {
        if (!processor) {
            *width = 640;
            *height = 480;
            return;
        }
        
        *width = processor->current_width;
        *height = processor->current_height;
    }
    
    DLLEXPORT double get_scale_factor(FrameProcessor* processor) {
        return processor ? processor->scale_factor : 1.0;
    }
    
    DLLEXPORT int is_startup_complete(FrameProcessor* processor) {
        return processor ? (processor->is_startup_complete ? 1 : 0) : 1;
    }
    
    DLLEXPORT void reset_processor(FrameProcessor* processor) {
        if (!processor) return;
        
        processor->current_width = std::max(320, processor->target_width / 4);
        processor->current_height = std::max(240, processor->target_height / 4);
        processor->startup_frames_processed = 0;
        processor->frames_since_last_adjust = 0;
        processor->avg_processing_time = 0.0;
        processor->is_startup_complete = false;
        processor->skip_factor = 1;
        processor->scale_factor = (double)processor->current_width / processor->target_width;
    }
    
    DLLEXPORT void calculate_startup_resolution(int target_width, int target_height, 
                                               int startup_frame_count, 
                                               int* current_width, int* current_height) {
        // Progressive resolution scaling during startup
        double progress = std::min(1.0, startup_frame_count / 150.0); // 150 frames to full res
        double scale = 0.25 + 0.75 * progress; // Start at 25%, progress to 100%
        
        *current_width = std::max(320, (int)(target_width * scale));
        *current_height = std::max(240, (int)(target_height * scale));
    }
    
    DLLEXPORT double calculate_adaptive_skip_factor(double current_fps, double target_fps, 
                                                   double processing_time_ms) {
        if (current_fps >= target_fps * 0.9) {
            return 1.0; // No skipping needed
        }
        
        // Calculate how much we need to skip to reach target FPS
        double fps_ratio = target_fps / std::max(1.0, current_fps);
        return std::min(4.0, fps_ratio);
    }
    
    DLLEXPORT int estimate_memory_usage(int width, int height, int channels) {
        // Estimate memory usage in MB for frame processing
        int frame_size = width * height * channels;
        int buffer_count = 3; // Input, processing, output buffers
        return (frame_size * buffer_count) / (1024 * 1024);
    }
    
    DLLEXPORT void optimize_processing_pipeline(FrameProcessor* processor, 
                                               double cpu_usage, double memory_usage) {
        if (!processor) return;
        
        // Adjust processing based on system load
        if (cpu_usage > 80.0 || memory_usage > 80.0) {
            // High system load - reduce processing
            processor->skip_factor = std::min(3, processor->skip_factor + 1);
            
            // Temporarily reduce resolution if very high load
            if (cpu_usage > 90.0 && !processor->is_startup_complete) {
                processor->current_width = std::max(320, (int)(processor->current_width * 0.8));
                processor->current_height = std::max(240, (int)(processor->current_height * 0.8));
                processor->scale_factor = (double)processor->current_width / processor->target_width;
            }
        } else if (cpu_usage < 50.0 && memory_usage < 50.0) {
            // Low system load - can increase processing
            processor->skip_factor = std::max(1, processor->skip_factor - 1);
        }
    }
    
    // New frame downscaling functions for internal processing optimization
    DLLEXPORT int should_downscale_frame(FrameProcessor* processor, int input_width, int input_height,
                                        int* output_width, int* output_height) {
        if (!processor || !output_width || !output_height) return 0;
        
        // Always downscale during startup phase for performance
        if (!processor->is_startup_complete) {
            *output_width = processor->current_width;
            *output_height = processor->current_height;
            return 1; // Should downscale
        }
        
        // Check if system performance suggests downscaling
        if (processor->avg_processing_time > 33.0) { // Taking more than 33ms (30fps)
            // Calculate optimal processing resolution based on performance
            double performance_scale = std::min(1.0, 25.0 / processor->avg_processing_time);
            *output_width = (int)(input_width * performance_scale);
            *output_height = (int)(input_height * performance_scale);
            
            // Ensure minimum resolution
            *output_width = std::max(320, *output_width);
            *output_height = std::max(240, *output_height);
            
            return 1; // Should downscale
        }
        
        // No downscaling needed - use full resolution
        *output_width = input_width;
        *output_height = input_height;
        return 0; // No downscaling
    }
    
    DLLEXPORT double get_processing_scale_factor(FrameProcessor* processor) {
        if (!processor) return 1.0;
        
        // Return the scale factor for processing (not display)
        if (!processor->is_startup_complete) {
            return processor->scale_factor;
        }
        
        // During normal operation, calculate dynamic scale based on performance
        if (processor->avg_processing_time > 33.0) {
            return std::min(1.0, 25.0 / processor->avg_processing_time);
        }
        
        return 1.0; // Full resolution processing
    }
}