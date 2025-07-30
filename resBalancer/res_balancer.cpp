#include "res_balancer.h"
#include <cmath>

extern "C" {
    DLLEXPORT double calculate_distance(double p1_x, double p1_y, double p2_x, double p2_y) {
        return std::hypot(p1_x - p2_x, p1_y - p2_y);
    }
}