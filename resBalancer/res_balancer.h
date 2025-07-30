#ifndef RES_BALANCER_H
#define RES_BALANCER_H

#ifdef _WIN32
#define DLLEXPORT __declspec(dllexport)
#else
#define DLLEXPORT
#endif

extern "C" {
    DLLEXPORT double calculate_distance(double p1_x, double p1_y, double p2_x, double p2_y);
}

#endif // RES_BALANCER_H