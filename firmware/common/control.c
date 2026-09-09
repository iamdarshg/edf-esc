#include "edf_esc/control.h"

#include <stddef.h>

static void trip(esc_state_t *state, uint32_t fault) {
    state->faults |= fault;
    state->commanded_duty = 0;
    state->mode = ESC_FAULT;
}

esc_config_t esc_default_config(void) {
    return (esc_config_t){
        .align_time_us = 200000,
        .ramp_time_us = 600000,
        .control_timeout_us = 100000,
        .software_target_ma = 100000,
        .soft_limit_ma = 120000,
        .aggressive_limit_ma = 130000,
        .hard_limit_ma = 150000,
        .temperature_warning_c = 85,
        .temperature_shutdown_c = 105,
        .undervoltage_mv = 14000,
        .overvoltage_mv = 27000,
        .stall_timeout_us = 100000,
    };
}

esc_outputs_t esc_outputs_for_sector(uint8_t sector) {
    static const esc_outputs_t table[6] = {
        {PHASE_PWM_HIGH, PHASE_LOW_ON, PHASE_FLOAT},
        {PHASE_PWM_HIGH, PHASE_FLOAT, PHASE_LOW_ON},
        {PHASE_FLOAT, PHASE_PWM_HIGH, PHASE_LOW_ON},
        {PHASE_LOW_ON, PHASE_PWM_HIGH, PHASE_FLOAT},
        {PHASE_LOW_ON, PHASE_FLOAT, PHASE_PWM_HIGH},
        {PHASE_FLOAT, PHASE_LOW_ON, PHASE_PWM_HIGH},
    };
    const esc_outputs_t all_off = {PHASE_FLOAT, PHASE_FLOAT, PHASE_FLOAT};
    return sector < 6 ? table[sector] : all_off;
}

void esc_init(esc_state_t *state, const esc_config_t *config) {
    (void)config;
    if (state == NULL) return;
    *state = (esc_state_t){.mode = ESC_DISARMED};
}

void esc_set_control(esc_state_t *state, uint16_t duty, uint32_t now_us) {
    if (state == NULL || state->mode == ESC_FAULT) return;
    state->commanded_duty = duty;
    state->last_control_us = now_us;
}

void esc_arm(esc_state_t *state, uint32_t now_us) {
    if (state == NULL || state->faults != 0 || state->mode == ESC_FAULT) return;
    state->mode = ESC_ALIGN;
    state->state_started_us = now_us;
    state->last_control_us = now_us;
    state->last_commutation_us = now_us;
}

void esc_step(esc_state_t *state, const esc_config_t *config, uint32_t now_us) {
    if (state == NULL || config == NULL || state->mode == ESC_DISARMED || state->mode == ESC_FAULT) return;
    if ((uint32_t)(now_us - state->last_control_us) > config->control_timeout_us) {
        trip(state, ESC_FAULT_CONTROL_TIMEOUT);
        return;
    }
    const uint32_t elapsed = now_us - state->state_started_us;
    if (state->mode == ESC_ALIGN && elapsed >= config->align_time_us) {
        state->mode = ESC_OPEN_LOOP_RAMP;
        state->state_started_us += config->align_time_us;
    }
    if (state->mode == ESC_OPEN_LOOP_RAMP && state->bemf_reliable &&
        (uint32_t)(now_us - state->state_started_us) >= config->ramp_time_us) {
        state->mode = ESC_CLOSED_LOOP;
        state->state_started_us = now_us;
    }
}

void esc_set_bemf_reliable(esc_state_t *state, bool reliable) {
    if (state != NULL) state->bemf_reliable = reliable;
}

uint16_t esc_limit_duty(const esc_config_t *config, uint32_t current_ma, uint16_t requested) {
    if (config == NULL || current_ma >= config->hard_limit_ma) return 0;
    if (current_ma <= config->soft_limit_ma) return requested;
    if (current_ma < config->aggressive_limit_ma) {
        const uint32_t span = config->aggressive_limit_ma - config->soft_limit_ma;
        const uint32_t excess = current_ma - config->soft_limit_ma;
        return (uint16_t)((uint32_t)requested * (2u * span - excess) / (2u * span));
    }
    const uint32_t span = config->hard_limit_ma - config->aggressive_limit_ma;
    const uint32_t remaining = config->hard_limit_ma - current_ma;
    return (uint16_t)((uint32_t)requested * remaining / (2u * span));
}

uint16_t esc_protected_duty(const esc_config_t *config, uint32_t current_ma,
                            int16_t temperature_c, uint16_t requested) {
    uint16_t limited = esc_limit_duty(config, current_ma, requested);
    if (config == NULL || temperature_c >= config->temperature_shutdown_c) return 0;
    if (temperature_c <= config->temperature_warning_c) return limited;
    const uint32_t span = (uint32_t)(config->temperature_shutdown_c - config->temperature_warning_c);
    const uint32_t remaining = (uint32_t)(config->temperature_shutdown_c - temperature_c);
    return (uint16_t)((uint32_t)limited * remaining / span);
}

void esc_evaluate_protection(esc_state_t *state, const esc_config_t *config,
                             uint32_t current_ma, int16_t temperature_c,
                             uint32_t bus_mv, uint32_t now_us) {
    if (state == NULL || config == NULL || state->mode == ESC_FAULT) return;
    if (current_ma >= config->hard_limit_ma) {
        trip(state, ESC_FAULT_OVERCURRENT);
    } else if (temperature_c >= config->temperature_shutdown_c) {
        trip(state, ESC_FAULT_OVERTEMPERATURE);
    } else if (bus_mv < config->undervoltage_mv) {
        trip(state, ESC_FAULT_UNDERVOLTAGE);
    } else if (bus_mv > config->overvoltage_mv) {
        trip(state, ESC_FAULT_OVERVOLTAGE);
    } else if (state->mode == ESC_CLOSED_LOOP &&
               (uint32_t)(now_us - state->last_commutation_us) > config->stall_timeout_us) {
        trip(state, ESC_FAULT_STALL);
    }
}

void esc_note_commutation(esc_state_t *state, uint32_t now_us) {
    if (state != NULL) state->last_commutation_us = now_us;
}

void esc_emergency_stop(esc_state_t *state) {
    if (state != NULL) trip(state, ESC_FAULT_EMERGENCY_STOP);
}
