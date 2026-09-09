#include "edf_esc/control.h"

#include <assert.h>
#include <stdint.h>
#include <stdio.h>

static void test_commutation_table(void) {
    const esc_outputs_t expected[6] = {
        {PHASE_PWM_HIGH, PHASE_LOW_ON, PHASE_FLOAT},
        {PHASE_PWM_HIGH, PHASE_FLOAT, PHASE_LOW_ON},
        {PHASE_FLOAT, PHASE_PWM_HIGH, PHASE_LOW_ON},
        {PHASE_LOW_ON, PHASE_PWM_HIGH, PHASE_FLOAT},
        {PHASE_LOW_ON, PHASE_FLOAT, PHASE_PWM_HIGH},
        {PHASE_FLOAT, PHASE_LOW_ON, PHASE_PWM_HIGH},
    };
    for (uint8_t sector = 0; sector < 6; ++sector) {
        esc_outputs_t actual = esc_outputs_for_sector(sector);
        assert(actual.u == expected[sector].u);
        assert(actual.v == expected[sector].v);
        assert(actual.w == expected[sector].w);
    }
    esc_outputs_t invalid = esc_outputs_for_sector(6);
    assert(invalid.u == PHASE_FLOAT && invalid.v == PHASE_FLOAT && invalid.w == PHASE_FLOAT);
}

static void test_state_machine_and_control_timeout(void) {
    esc_config_t cfg = esc_default_config();
    esc_state_t state;
    esc_init(&state, &cfg);
    assert(state.mode == ESC_DISARMED);
    esc_set_control(&state, 20000, 0);
    esc_arm(&state, 0);
    assert(state.mode == ESC_ALIGN);
    esc_set_control(&state, 20000, cfg.align_time_us + 1);
    esc_step(&state, &cfg, cfg.align_time_us + 1);
    assert(state.mode == ESC_OPEN_LOOP_RAMP);
    esc_set_bemf_reliable(&state, true);
    esc_set_control(&state, 20000, cfg.align_time_us + cfg.ramp_time_us + 2);
    esc_step(&state, &cfg, cfg.align_time_us + cfg.ramp_time_us + 2);
    assert(state.mode == ESC_CLOSED_LOOP);
    esc_step(&state, &cfg, cfg.control_timeout_us + cfg.align_time_us + cfg.ramp_time_us + 3);
    assert(state.mode == ESC_FAULT);
    assert(state.faults & ESC_FAULT_CONTROL_TIMEOUT);
    assert(state.commanded_duty == 0);
}

static void test_protection_tiers(void) {
    esc_config_t cfg = esc_default_config();
    assert(cfg.software_target_ma == 100000);
    assert(cfg.soft_limit_ma == 120000);
    assert(cfg.aggressive_limit_ma == 130000);
    assert(cfg.hard_limit_ma == 150000);
    assert(esc_limit_duty(&cfg, 100000, 50000) == 50000);
    assert(esc_limit_duty(&cfg, 125000, 50000) < 50000);
    assert(esc_limit_duty(&cfg, 135000, 50000) <= 25000);
    assert(esc_limit_duty(&cfg, 150000, 50000) == 0);
}

static void test_emergency_stop_latches(void) {
    esc_config_t cfg = esc_default_config();
    esc_state_t state;
    esc_init(&state, &cfg);
    esc_arm(&state, 0);
    esc_emergency_stop(&state);
    assert(state.mode == ESC_FAULT);
    assert(state.faults & ESC_FAULT_EMERGENCY_STOP);
    esc_arm(&state, 1);
    assert(state.mode == ESC_FAULT);
}

static void test_sampled_protection_faults(void) {
    esc_config_t cfg = esc_default_config();
    esc_state_t state;
    esc_init(&state, &cfg);
    esc_arm(&state, 100);
    esc_evaluate_protection(&state, &cfg, 151000, 25, 22000, 101);
    assert(state.mode == ESC_FAULT);
    assert(state.faults & ESC_FAULT_OVERCURRENT);

    esc_init(&state, &cfg);
    esc_arm(&state, 100);
    esc_evaluate_protection(&state, &cfg, 10000, 106, 22000, 101);
    assert(state.faults & ESC_FAULT_OVERTEMPERATURE);

    esc_init(&state, &cfg);
    esc_arm(&state, 100);
    esc_evaluate_protection(&state, &cfg, 10000, 25, 13000, 101);
    assert(state.faults & ESC_FAULT_UNDERVOLTAGE);

    esc_init(&state, &cfg);
    esc_arm(&state, 100);
    esc_evaluate_protection(&state, &cfg, 10000, 25, 28000, 101);
    assert(state.faults & ESC_FAULT_OVERVOLTAGE);
}

static void test_temperature_derating_and_stall(void) {
    esc_config_t cfg = esc_default_config();
    assert(esc_protected_duty(&cfg, 100000, 25, 50000) == 50000);
    assert(esc_protected_duty(&cfg, 100000, 95, 50000) < 50000);
    assert(esc_protected_duty(&cfg, 100000, 105, 50000) == 0);

    esc_state_t state;
    esc_init(&state, &cfg);
    esc_set_control(&state, 20000, 100);
    esc_arm(&state, 100);
    state.mode = ESC_CLOSED_LOOP;
    esc_note_commutation(&state, 100);
    esc_set_control(&state, 20000, cfg.stall_timeout_us + 101);
    esc_evaluate_protection(&state, &cfg, 10000, 25, 22000, cfg.stall_timeout_us + 101);
    assert(state.faults & ESC_FAULT_STALL);
}

int main(void) {
    test_commutation_table();
    test_state_machine_and_control_timeout();
    test_protection_tiers();
    test_emergency_stop_latches();
    test_sampled_protection_faults();
    test_temperature_derating_and_stall();
    puts("control tests passed");
    return 0;
}
