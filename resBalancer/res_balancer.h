#ifndef RES_BALANCER_H
#define RES_BALANCER_H

#ifdef _WIN32
#define DLLEXPORT __declspec(dllexport)
#else
#define DLLEXPORT
#endif

extern "C" {
    DLLEXPORT double calculate_distance(double p1_x, double p1_y, double p2_x, double p2_y);
    DLLEXPORT double calculate_roi_overlap_fast(double roi1_x, double roi1_y, double roi1_r,
                                               double roi2_x, double roi2_y, double roi2_r);
    DLLEXPORT int batch_bbox_check(double* points_x, double* points_y, int num_points,
                                  double min_x, double max_x, double min_y, double max_y,
                                  int* results);
    DLLEXPORT void batch_distance_calculation(double* points1_x, double* points1_y,
                                             double* points2_x, double* points2_y,
                                             int num_pairs, double* results);
}

#endif // RES_BALANCER_H