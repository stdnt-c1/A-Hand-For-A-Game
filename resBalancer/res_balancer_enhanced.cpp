#include "res_balancer.h"
#include <cmath>
#include <algorithm>
#include <cstdlib>
#include <cstring>

// OpenCV includes (will be conditional)
#ifdef WITH_OPENCV
#include <opencv2/opencv.hpp>
#include <opencv2/imgproc.hpp>
#endif

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

extern "C" {
    // Original geometry functions (unchanged)
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

#ifdef WITH_OPENCV
    // === NEW: OpenCV-Enhanced Frame Processing Functions ===
    
    DLLEXPORT int resize_frame_opencv(unsigned char* input_data, int input_width, int input_height,
                                     unsigned char* output_data, int output_width, int output_height,
                                     int channels, int interpolation_type) {
        // Critical safety checks to prevent OpenCV assertion failures
        if (!input_data || !output_data) return 0;
        if (!safe_dimension_check(input_width, input_height)) return 0;
        if (!safe_dimension_check(output_width, output_height)) return 0;
        if (channels < 1 || channels > 4) return 0;
        
        try {
            // Create OpenCV Mat from input data with safety validation
            cv::Mat input_mat(input_height, input_width, 
                             channels == 3 ? CV_8UC3 : (channels == 4 ? CV_8UC4 : CV_8UC1), input_data);
            
            // Validate the created matrix
            if (input_mat.empty() || input_mat.rows != input_height || input_mat.cols != input_width) {
                return 0;
            }
            
            // Create output Mat with validation
            cv::Mat output_mat(output_height, output_width, 
                              channels == 3 ? CV_8UC3 : (channels == 4 ? CV_8UC4 : CV_8UC1), output_data);
            
            if (output_mat.empty()) {
                return 0;
            }
            
            // Choose interpolation method
            int cv_interpolation;
            switch (interpolation_type) {
                case 0: cv_interpolation = cv::INTER_NEAREST; break;
                case 1: cv_interpolation = cv::INTER_LINEAR; break;
                case 2: cv_interpolation = cv::INTER_AREA; break;
                case 3: cv_interpolation = cv::INTER_CUBIC; break;
                case 4: cv_interpolation = cv::INTER_LANCZOS4; break;
                default: cv_interpolation = cv::INTER_LINEAR; break;
            }
            
            // Perform resize with additional safety checks
            if (output_width > 0 && output_height > 0 && output_width < 32767 && output_height < 32767) {
                cv::resize(input_mat, output_mat, cv::Size(output_width, output_height), 
                          0, 0, cv_interpolation);
            } else {
                return 0;
            }
            
            return 1; // Success
        } catch (const cv::Exception& e) {
            // Log OpenCV-specific errors
            return 0;
        } catch (...) {
            return 0; // Failure
        }
    }
    
    DLLEXPORT int apply_gaussian_blur(unsigned char* input_data, int width, int height, 
                                     int channels, double sigma) {
        try {
            cv::Mat image(height, width, channels == 3 ? CV_8UC3 : CV_8UC1, input_data);
            
            int kernel_size = (int)(sigma * 6) | 1; // Ensure odd kernel size
            cv::GaussianBlur(image, image, cv::Size(kernel_size, kernel_size), sigma);
            
            return 1; // Success
        } catch (...) {
            return 0; // Failure
        }
    }
    
    DLLEXPORT int convert_color_space(unsigned char* input_data, int width, int height,
                                     unsigned char* output_data, int conversion_code) {
        try {
            cv::Mat input_mat(height, width, CV_8UC3, input_data);
            cv::Mat output_mat(height, width, CV_8UC3, output_data);
            
            cv::cvtColor(input_mat, output_mat, conversion_code);
            
            return 1; // Success
        } catch (...) {
            return 0; // Failure
        }
    }
    
    DLLEXPORT int adaptive_threshold(unsigned char* input_data, int width, int height,
                                    unsigned char* output_data, double max_value, 
                                    int adaptive_method, int threshold_type, 
                                    int block_size, double C) {
        try {
            cv::Mat input_mat(height, width, CV_8UC1, input_data);
            cv::Mat output_mat(height, width, CV_8UC1, output_data);
            
            cv::adaptiveThreshold(input_mat, output_mat, max_value, adaptive_method,
                                 threshold_type, block_size, C);
            
            return 1; // Success
        } catch (...) {
            return 0; // Failure
        }
    }
    
    DLLEXPORT const char* get_opencv_version() {
        return CV_VERSION;
    }
    
    DLLEXPORT int test_opencv_features() {
        try {
            // Create a small test image
            cv::Mat test_image = cv::Mat::zeros(100, 100, CV_8UC3);
            cv::Mat resized;
            cv::resize(test_image, resized, cv::Size(50, 50));
            
            return 1; // OpenCV working
        } catch (...) {
            return 0; // OpenCV not working
        }
    }

#else
    // Fallback functions when OpenCV is not available
    DLLEXPORT int resize_frame_opencv(unsigned char* input_data, int input_width, int input_height,
                                     unsigned char* output_data, int output_width, int output_height,
                                     int channels, int interpolation_type) {
        return 0; // Not implemented without OpenCV
    }
    
    DLLEXPORT const char* get_opencv_version() {
        return "OpenCV not available";
    }
    
    DLLEXPORT int test_opencv_features() {
        return 0; // OpenCV not available
    }
#endif

    // === Enhanced Frame Processing Functions (all available regardless of OpenCV) ===
    
    DLLEXPORT FrameProcessor* create_frame_processor(int target_width, int target_height, double target_fps) {
        // Critical overflow protection
        if (target_width <= 0 || target_height <= 0 || target_width > 32000 || target_height > 32000) {
            return nullptr;
        }
        if (target_fps <= 0 || target_fps > 1000) {
            return nullptr;
        }
        
        FrameProcessor* processor = (FrameProcessor*)malloc(sizeof(FrameProcessor));
        if (!processor) return nullptr;
        
        // Ensure safe boundaries for all dimensions
        processor->target_width = std::min(target_width, 32000);
        processor->target_height = std::min(target_height, 32000);
        processor->target_fps = target_fps;
        
        // Start with reduced resolution for cold start - with overflow protection
        processor->current_width = std::max(320, std::min(target_width / 4, 16000));
        processor->current_height = std::max(240, std::min(target_height / 4, 16000));
        
        processor->startup_frames_processed = 0;
        processor->frames_since_last_adjust = 0;
        processor->avg_processing_time = 0.0;
        processor->is_startup_complete = false;
        processor->skip_factor = 1;
        processor->scale_factor = (double)processor->current_width / processor->target_width;
        
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
            
            // If processing time is good, increase resolution safely
            if (processor->avg_processing_time < target_frame_time * 0.7) {
                int new_width = std::min(processor->target_width, 
                                       std::min((int)(processor->current_width * 1.5), 32000));
                int new_height = std::min(processor->target_height, 
                                        std::min((int)(processor->current_height * 1.5), 32000));
                
                // Additional safety check for OpenCV limits
                if (new_width < 32767 && new_height < 32767 && new_width != processor->current_width) {
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
    
    // Test function to verify DLL functionality
    DLLEXPORT int test_dll_functionality() {
        // Test basic math functions
        double distance = calculate_distance(0, 0, 3, 4);
        if (abs(distance - 5.0) > 0.001) return 0;
        
        // Test frame processor creation
        FrameProcessor* processor = create_frame_processor(640, 480, 30.0);
        if (!processor) return 0;
        
        destroy_frame_processor(processor);
        
        return 1; // All tests passed
    }
    
    DLLEXPORT const char* get_dll_info() {
        #ifdef WITH_OPENCV
        return "AzimuthControl Enhanced Frame Processor with OpenCV " CV_VERSION;
        #else
        return "AzimuthControl Frame Processor (OpenCV-free)";
        #endif
    }
    
    // Safe dimension checking to prevent OpenCV assertion failures
    DLLEXPORT int safe_dimension_check(int width, int height) {
        if (width <= 0 || height <= 0) return 0;
        if (width > 32767 || height > 32767) return 0;  // OpenCV SHRT_MAX limit
        if (width * height > 100000000) return 0;  // 100MP safety limit
        return 1;
    }
    
    // Mirror transform with safety checks
    DLLEXPORT int apply_mirror_transform(unsigned char* input_data, int width, int height, 
                                        int channels, unsigned char* output_data, int mirror_horizontal) {
        if (!input_data || !output_data) return 0;
        if (!safe_dimension_check(width, height)) return 0;
        if (channels < 1 || channels > 4) return 0;
        
        try {
            if (mirror_horizontal) {
                // Horizontal flip - reverse pixel order in each row
                for (int y = 0; y < height; y++) {
                    for (int x = 0; x < width; x++) {
                        int src_idx = (y * width + x) * channels;
                        int dst_idx = (y * width + (width - 1 - x)) * channels;
                        
                        for (int c = 0; c < channels; c++) {
                            output_data[dst_idx + c] = input_data[src_idx + c];
                        }
                    }
                }
            } else {
                // No mirroring - direct copy
                memcpy(output_data, input_data, width * height * channels);
            }
            return 1;
        } catch (...) {
            return 0;
        }
    }
}
