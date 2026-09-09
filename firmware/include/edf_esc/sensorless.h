#ifndef EDF_ESC_SENSORLESS_H
#define EDF_ESC_SENSORLESS_H

#include <stdbool.h>
#include <stdint.h>

typedef enum { PHASE_U = 0, PHASE_V, PHASE_W, PHASE_INVALID } bemf_phase_t;
typedef enum { EDGE_RISING = 0, EDGE_FALLING } bemf_polarity_t;

typedef struct {
    bemf_phase_t phase;
    bemf_polarity_t polarity;
} bemf_edge_t;

typedef struct {
    bemf_edge_t expected;
    uint32_t blank_until_us;
    uint16_t hysteresis_mv;
    bool crossed;
    bool seen_pre_crossing;
} bemf_detector_t;

bemf_edge_t bemf_expected_edge(uint8_t sector, bool reverse);
void bemf_detector_arm(bemf_detector_t *detector, bemf_edge_t expected,
                       uint32_t commutated_at_us, uint32_t blanking_us);
bool bemf_detector_sample(bemf_detector_t *detector, uint16_t half_bus_mv,
                          uint16_t phase_mv, uint32_t now_us);
uint32_t commutation_delay_us(uint32_t zero_cross_interval_us, uint8_t advance_deg);

#endif
