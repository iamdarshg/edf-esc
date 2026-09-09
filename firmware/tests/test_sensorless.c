#include "edf_esc/sensorless.h"

#include <assert.h>
#include <stdio.h>

static void test_floating_phase_sequence(void) {
    const bemf_edge_t expected[6] = {
        {PHASE_W, EDGE_RISING}, {PHASE_V, EDGE_FALLING},
        {PHASE_U, EDGE_RISING}, {PHASE_W, EDGE_FALLING},
        {PHASE_V, EDGE_RISING}, {PHASE_U, EDGE_FALLING},
    };
    for (unsigned sector = 0; sector < 6; ++sector) {
        bemf_edge_t edge = bemf_expected_edge((uint8_t)sector, false);
        assert(edge.phase == expected[sector].phase);
        assert(edge.polarity == expected[sector].polarity);
    }
}

static void test_blanking_hysteresis_and_single_crossing(void) {
    bemf_detector_t detector;
    bemf_detector_arm(&detector, (bemf_edge_t){PHASE_W, EDGE_RISING}, 1000, 30);
    assert(!bemf_detector_sample(&detector, 1100, 1000, 1010));
    assert(!bemf_detector_sample(&detector, 1100, 1000, 1031));
    assert(bemf_detector_sample(&detector, 1100, 1200, 1040));
    assert(!bemf_detector_sample(&detector, 1100, 1200, 1050));
}

static void test_advance_delay(void) {
    assert(commutation_delay_us(1000, 0) == 500);
    assert(commutation_delay_us(1000, 10) == 333);
    assert(commutation_delay_us(1000, 29) == 16);
    assert(commutation_delay_us(1000, 30) == 0);
    assert(commutation_delay_us(1000, 45) == 0);
}

int main(void) {
    test_floating_phase_sequence();
    test_blanking_hysteresis_and_single_crossing();
    test_advance_delay();
    puts("sensorless tests passed");
    return 0;
}
