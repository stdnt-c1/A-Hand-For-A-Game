#include "res_balancer.h"
#include <cmath>
#include <algorithm>

extern "C" {
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
}