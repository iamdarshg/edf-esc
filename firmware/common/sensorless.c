#include "edf_esc/sensorless.h"

#include <stddef.h>

bemf_edge_t bemf_expected_edge(uint8_t sector, bool reverse) {
    static const bemf_edge_t forward[6] = {
        {PHASE_W, EDGE_RISING}, {PHASE_V, EDGE_FALLING},
        {PHASE_U, EDGE_RISING}, {PHASE_W, EDGE_FALLING},
        {PHASE_V, EDGE_RISING}, {PHASE_U, EDGE_FALLING},
    };
    if (sector >= 6) return (bemf_edge_t){PHASE_INVALID, EDGE_RISING};
    if (!reverse) return forward[sector];
    bemf_edge_t reversed = forward[5u - sector];
    reversed.polarity = reversed.polarity == EDGE_RISING ? EDGE_FALLING : EDGE_RISING;
    return reversed;
}

void bemf_detector_arm(bemf_detector_t *detector, bemf_edge_t expected,
                       uint32_t commutated_at_us, uint32_t blanking_us) {
    if (detector == NULL) return;
    *detector = (bemf_detector_t){
        .expected = expected,
        .blank_until_us = commutated_at_us + blanking_us,
        .hysteresis_mv = 50,
    };
}

bool bemf_detector_sample(bemf_detector_t *detector, uint16_t half_bus_mv,
                          uint16_t phase_mv, uint32_t now_us) {
    if (detector == NULL || detector->crossed || now_us <= detector->blank_until_us) return false;
    const uint16_t hysteresis = detector->hysteresis_mv;
    if (detector->expected.polarity == EDGE_RISING) {
        if ((uint32_t)phase_mv + hysteresis < half_bus_mv) detector->seen_pre_crossing = true;
        if (detector->seen_pre_crossing && phase_mv > (uint32_t)half_bus_mv + hysteresis) {
            detector->crossed = true;
            return true;
        }
    } else {
        if (phase_mv > (uint32_t)half_bus_mv + hysteresis) detector->seen_pre_crossing = true;
        if (detector->seen_pre_crossing && (uint32_t)phase_mv + hysteresis < half_bus_mv) {
            detector->crossed = true;
            return true;
        }
    }
    return false;
}

uint32_t commutation_delay_us(uint32_t zero_cross_interval_us, uint8_t advance_deg) {
    if (advance_deg >= 30) return 0;
    return zero_cross_interval_us * (uint32_t)(30u - advance_deg) / 60u;
}
