"""Dimensionally explicit first-order power-stage calculations.

These estimates size a prototype and define tests. They do not replace
double-pulse, thermal, current-calibration, or full-power measurements.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class GateMetrics:
    total_gate_charge_c: float
    minimum_turn_on_s: float
    minimum_turn_off_s: float
    gate_charge_per_second_c: float


@dataclass(frozen=True)
class FetLosses:
    conduction_w: float
    switching_w: float
    total_w: float


@dataclass(frozen=True)
class BuckRipple:
    duty_cycle: float
    inductor_ripple_a: float


@dataclass(frozen=True)
class DividerStress:
    nominal_output_v: float
    transient_open_output_v: float
    clamp_current_a: float


def _positive(name: str, value: float) -> None:
    if value <= 0:
        raise ValueError(f"{name} must be positive")


def gate_metrics(
    *, qg_c: float, count: int, source_a: float, sink_a: float, frequency_hz: float
) -> GateMetrics:
    for name, value in (
        ("qg_c", qg_c),
        ("count", float(count)),
        ("source_a", source_a),
        ("sink_a", sink_a),
        ("frequency_hz", frequency_hz),
    ):
        _positive(name, value)
    total_charge = qg_c * count
    return GateMetrics(
        total_gate_charge_c=total_charge,
        minimum_turn_on_s=total_charge / source_a,
        minimum_turn_off_s=total_charge / sink_a,
        gate_charge_per_second_c=total_charge * frequency_hz,
    )


def fet_losses(
    current_a: float,
    rds_hot_ohm: float,
    voltage_v: float,
    rise_s: float,
    fall_s: float,
    frequency_hz: float,
) -> FetLosses:
    for name, value in (
        ("current_a", current_a),
        ("rds_hot_ohm", rds_hot_ohm),
        ("voltage_v", voltage_v),
        ("rise_s", rise_s),
        ("fall_s", fall_s),
        ("frequency_hz", frequency_hz),
    ):
        _positive(name, value)
    conduction = current_a**2 * rds_hot_ohm
    switching = 0.5 * voltage_v * current_a * (rise_s + fall_s) * frequency_hz
    return FetLosses(conduction_w=conduction, switching_w=switching, total_w=conduction + switching)


def copper_resistance(
    *,
    length_m: float,
    width_m: float,
    thickness_m: float,
    layers: int,
    resistivity_ohm_m: float = 1.724e-8,
) -> float:
    for name, value in (
        ("length_m", length_m),
        ("width_m", width_m),
        ("thickness_m", thickness_m),
        ("layers", float(layers)),
        ("resistivity_ohm_m", resistivity_ohm_m),
    ):
        _positive(name, value)
    return resistivity_ohm_m * length_m / (width_m * thickness_m * layers)


def buck_ripple(*, vin_v: float, vout_v: float, frequency_hz: float, inductance_h: float) -> BuckRipple:
    for name, value in (
        ("vin_v", vin_v),
        ("vout_v", vout_v),
        ("frequency_hz", frequency_hz),
        ("inductance_h", inductance_h),
    ):
        _positive(name, value)
    if vout_v >= vin_v:
        raise ValueError("buck converter requires vout_v < vin_v")
    duty = vout_v / vin_v
    ripple = (vin_v - vout_v) * duty / (inductance_h * frequency_hz)
    return BuckRipple(duty_cycle=duty, inductor_ripple_a=ripple)


def divider_stress(*, nominal_input_v: float, transient_input_v: float,
                   upper_ohm: float, lower_ohm: float, series_ohm: float,
                   clamp_v: float) -> DividerStress:
    for name, value in (("nominal_input_v", nominal_input_v),
                        ("transient_input_v", transient_input_v),
                        ("upper_ohm", upper_ohm), ("lower_ohm", lower_ohm),
                        ("series_ohm", series_ohm), ("clamp_v", clamp_v)):
        _positive(name, value)
    ratio = lower_ohm / (upper_ohm + lower_ohm)
    nominal = nominal_input_v * ratio
    transient = transient_input_v * ratio
    thevenin = upper_ohm * lower_ohm / (upper_ohm + lower_ohm)
    clamp_current = max(0.0, (transient - clamp_v) / (thevenin + series_ohm))
    return DividerStress(nominal, transient, clamp_current)
