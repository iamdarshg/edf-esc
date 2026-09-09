#ifndef EDF_ESC_CONTROL_H
#define EDF_ESC_CONTROL_H

#include <stdbool.h>
#include <stdint.h>

typedef enum {
    PHASE_FLOAT = 0,
    PHASE_PWM_HIGH,
    PHASE_LOW_ON,
} phase_drive_t;

typedef struct {
    phase_drive_t u;
    phase_drive_t v;
    phase_drive_t w;
} esc_outputs_t;

typedef enum {
    ESC_DISARMED = 0,
    ESC_ALIGN,
    ESC_OPEN_LOOP_RAMP,
    ESC_CLOSED_LOOP,
    ESC_FAULT,
} esc_mode_t;

enum {
    ESC_FAULT_CONTROL_TIMEOUT = 1u << 0,
    ESC_FAULT_EMERGENCY_STOP = 1u << 1,
    ESC_FAULT_OVERCURRENT = 1u << 2,
    ESC_FAULT_GATE_SUPPLY = 1u << 3,
    ESC_FAULT_STARTUP = 1u << 4,
    ESC_FAULT_OVERTEMPERATURE = 1u << 5,
    ESC_FAULT_UNDERVOLTAGE = 1u << 6,
    ESC_FAULT_OVERVOLTAGE = 1u << 7,
    ESC_FAULT_STALL = 1u << 8,
};

typedef struct {
    uint32_t align_time_us;
    uint32_t ramp_time_us;
    uint32_t control_timeout_us;
    uint32_t software_target_ma;
    uint32_t soft_limit_ma;
    uint32_t aggressive_limit_ma;
    uint32_t hard_limit_ma;
    int16_t temperature_warning_c;
    int16_t temperature_shutdown_c;
    uint32_t undervoltage_mv;
    uint32_t overvoltage_mv;
    uint32_t stall_timeout_us;
} esc_config_t;

typedef struct {
    esc_mode_t mode;
    uint32_t faults;
    uint16_t commanded_duty;
    uint32_t last_control_us;
    uint32_t state_started_us;
    uint32_t last_commutation_us;
    bool bemf_reliable;
} esc_state_t;

esc_config_t esc_default_config(void);
esc_outputs_t esc_outputs_for_sector(uint8_t sector);
void esc_init(esc_state_t *state, const esc_config_t *config);
void esc_set_control(esc_state_t *state, uint16_t duty, uint32_t now_us);
void esc_arm(esc_state_t *state, uint32_t now_us);
void esc_step(esc_state_t *state, const esc_config_t *config, uint32_t now_us);
void esc_set_bemf_reliable(esc_state_t *state, bool reliable);
uint16_t esc_limit_duty(const esc_config_t *config, uint32_t current_ma, uint16_t requested);
uint16_t esc_protected_duty(const esc_config_t *config, uint32_t current_ma,
                            int16_t temperature_c, uint16_t requested);
void esc_evaluate_protection(esc_state_t *state, const esc_config_t *config,
                             uint32_t current_ma, int16_t temperature_c,
                             uint32_t bus_mv, uint32_t now_us);
void esc_note_commutation(esc_state_t *state, uint32_t now_us);
void esc_emergency_stop(esc_state_t *state);

#endif
