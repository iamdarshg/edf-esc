import math

from edf_esc.calculations import (
    buck_ripple,
    copper_resistance,
    divider_stress,
    fet_losses,
    gate_metrics,
)


def test_three_parallel_fets_present_243_nc_to_one_driver_output():
    result = gate_metrics(qg_c=81e-9, count=3, source_a=0.750, sink_a=1.5, frequency_hz=16_000)
    assert math.isclose(result.total_gate_charge_c, 243e-9)
    assert math.isclose(result.minimum_turn_on_s, 324e-9)
    assert math.isclose(result.minimum_turn_off_s, 162e-9)
    assert math.isclose(result.gate_charge_per_second_c, 0.003888)


def test_fet_loss_increases_with_current_and_frequency():
    low = fet_losses(100, 0.0015, 25.2, 324e-9, 162e-9, 12_000)
    high = fet_losses(150, 0.0015, 25.2, 324e-9, 162e-9, 24_000)
    assert low.conduction_w == 15.0
    assert high.conduction_w == 33.75
    assert high.switching_w > low.switching_w


def test_defined_copper_geometry_is_near_point_one_milliohm():
    resistance = copper_resistance(
        length_m=0.0116,
        width_m=0.028,
        thickness_m=70e-6,
        layers=1,
        resistivity_ohm_m=1.68e-8,
    )
    assert 95e-6 <= resistance <= 105e-6


def test_47_uh_bec_ripple_is_bounded_at_worst_case_input():
    result = buck_ripple(vin_v=25.2, vout_v=5.0, frequency_hz=180_000, inductance_h=47e-6)
    assert math.isclose(result.duty_cycle, 5.0 / 25.2)
    assert 0.45 < result.inductor_ripple_a < 0.55


def test_bemf_divider_nominal_range_and_transient_clamp_current():
    result = divider_stress(
        nominal_input_v=25.2,
        transient_input_v=60.0,
        upper_ohm=94_000,
        lower_ohm=12_000,
        series_ohm=1_000,
        clamp_v=3.6,
    )
    assert 2.8 < result.nominal_output_v < 2.9
    assert result.transient_open_output_v > 6.7
    assert 0.00025 < result.clamp_current_a < 0.00030
