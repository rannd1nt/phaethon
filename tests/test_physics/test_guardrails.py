"""
Tests for Isomorphic Firewalls, Exclusive Domain Locks,
logarithmic guardrails, and comprehensive physics integration.
"""

import math

import numpy as np
import pytest

import phaethon as ptn
import phaethon.units as u
from phaethon.exceptions import (
    AxiomViolationError,
    DimensionMismatchError,
    PhysicalAlgebraError,
    SemanticMismatchError,
)


def test_logarithmic_unit_operations():
    """Verify dBm linearization, synthesis, and math guardrails."""
    signal = u.DecibelMilliwatt(30.0)
    linear_power = ~signal
    assert isinstance(linear_power, u.Watt)
    assert np.isclose(linear_power.mag, 1.0)

    time_span = u.Second(5.0)
    energy = signal * time_span
    assert isinstance(energy, u.Joule)
    assert np.isclose(energy.mag, 5.0)

    time_calc = u.Joule(20.0) / signal
    assert isinstance(time_calc, u.Second)
    assert np.isclose(time_calc.mag, 20.0)

    inv_power = 1.0 / signal
    expected_sig = frozenset({("mass", -1), ("length", -2), ("time", 3)})
    assert inv_power._signature == expected_sig
    assert np.isclose(inv_power.mag, 1.0)

    sig1 = u.DecibelMilliwatt(30.0)
    sig2 = u.DecibelMilliwatt(30.0)
    total_signal = sig1 + sig2
    assert isinstance(total_signal, u.DecibelMilliwatt)
    assert np.isclose(total_signal.mag, 33.0102999566)

    quake = u.MomentMagnitude(7.0)
    expected_joules = 10 ** (1.5 * 7.0 + 4.8)
    assert isinstance(~quake, u.Joule)
    assert np.isclose((~quake).mag, expected_joules)

    acid = u.pH(3.0)
    assert isinstance(~acid, u.MolesPerCubicMeter)
    assert np.isclose((~acid).mag, 1.0)

    with pytest.raises(AxiomViolationError, match="You cannot exponentiate"):
        _ = acid ** 2
    with pytest.raises(AxiomViolationError, match="You cannot exponentiate"):
        _ = signal // 2
    with pytest.raises(AxiomViolationError, match="You cannot exponentiate"):
        _ = signal % 3


def test_phantom_dimension_isolation():
    """Verify Hz, Bq, RPM and rad/s remain isolated despite sharing the same SI DNA."""
    frequency = u.Hertz(50)
    radioactivity = u.Becquerel(50)
    rpm = u.RevolutionsPerMinute(3000)
    angular_vel = u.RadianPerSecond(3.14)

    freq_synth = u.Cycle(100) / u.Second(2)
    decay_synth = u.Decay(100) / u.Second(2)

    assert freq_synth.dimension == "frequency"
    assert decay_synth.dimension == "radioactivity"
    assert freq_synth.mag == 50.0
    assert decay_synth.mag == 50.0

    with pytest.raises(SemanticMismatchError):
        frequency.to(u.Becquerel)
    with pytest.raises(SemanticMismatchError):
        radioactivity.to(u.Hertz)
    with pytest.raises(SemanticMismatchError):
        angular_vel.to(u.Hertz)

    assert rpm.to(u.Hertz).mag == 50.0


def test_radiology_domain_firewall():
    """Verify specific energy, absorbed dose, and equivalent dose cannot be mixed."""
    energy = u.Joule(10)
    mass = u.Kilogram(2)
    rad_factor = u.Radiation(1)
    bio_factor = u.BiologicalEffect(1)

    spec_energy = energy / mass
    absorbed = (energy * rad_factor) / mass
    equiv = (energy * bio_factor) / mass

    assert spec_energy.dimension == "specific_energy"
    assert absorbed.dimension == "absorbed_dose"
    assert equiv.dimension == "equivalent_dose"

    with pytest.raises(SemanticMismatchError):
        spec_energy.to(u.Gray)
    with pytest.raises(SemanticMismatchError):
        absorbed.to(u.Sievert)

    manual_gray = u.Gray(spec_energy.mag)
    assert manual_gray.dimension == "absorbed_dose"
    assert manual_gray.mag == 5.0


def test_physics_engine_comprehensive():
    """
    Comprehensive integration test covering electrical synthesis, domain methods,
    storage scaling, phantom rates, radiology, and exception guardrails.
    """
    Volt = u.Ampere * u.Ohm
    V = u.Ampere(50) * u.Ohm(10)
    I = Volt(400) / u.Ohm(10)
    R = Volt(400) / u.Ampere(50)
    assert V.mag == 500.0
    assert I.mag == 40.0
    assert R.mag == 8.0
    assert str(V.decompose()) == "500 kg·m²/(s³·A)"
    assert str(R.decompose()) == "8 kg·m²/(s³·A²)"

    assert u.Megahertz(0.5).period.mag == pytest.approx(2.0e-06)
    assert u.Celsius(-37).isabsolute is False
    assert u.Celsius(-37).to(u.Kelvin).isabsolute is True
    assert u.Degree(90).to(u.ArcMinute).wrap() == u.ArcMinute(5400.0)
    assert u.Revolution(1.5).to(u.Degree).wrap().mag == 180.0
    assert u.Degree(120).to(u.Radian).wrap().mag == pytest.approx(2.094395, rel=1e-4)
    assert u.Radian(1).to_dms() == "57° 17' 44.81\""
    assert u.ArcSecond(345).to(u.Degree).to_dms() == "0° 5' 45.00\""
    assert u.Kilovolt(3.45).rms().mag == pytest.approx(2.4395, rel=1e-4)
    assert u.Kilovolt(3.45).peak().mag == pytest.approx(4.879, rel=1e-4)

    hard_disk = u.Terabyte(1)
    assert hard_disk.bin().mag == pytest.approx(931.3226, rel=1e-4)
    assert str(hard_disk.bin().symbol) == "GiB"
    assert hard_disk.dec().mag == 1.0
    assert str(hard_disk.dec().symbol) == "TB"
    internet_speed = u.Megabit(100)
    assert internet_speed.dec().mag == 12.5
    assert str(internet_speed.dec().symbol) == "MB"

    pure_rate = 1000 / u.Second(1)
    assert pure_rate.mag == 1000.0
    assert (pure_rate + pure_rate).mag == 2000.0
    assert pure_rate.to(u.Hertz).mag == 1000.0
    assert pure_rate.to(u.Becquerel).mag == 1000.0
    assert pure_rate.to(u.Gigahertz).mag == 1e-6

    f_hz = u.Cycle(10) / u.Second(1)
    f_hourly = u.Cycle(100) / u.Hour(1)
    r_decay = u.Decay(50) / u.Minute(1)

    assert str(f_hz.symbol) == "Hz"
    assert f_hz.mag == 10.0
    assert str(f_hourly.symbol) == "cycle/h"
    assert f_hourly.to(u.Hertz).mag == pytest.approx(0.0278, rel=1e-2)
    assert (f_hourly + f_hourly).mag == 200.0
    assert str(r_decay.symbol) == "decay/min"
    assert r_decay.to(u.Becquerel).mag == pytest.approx(0.8333, rel=1e-3)
    assert r_decay.to(u.Rutherford).mag == pytest.approx(8.3333e-7, rel=1e-3)
    assert (r_decay - r_decay).mag == 0.0

    UnitA = u.Cycle(440) / u.Second(1)
    UnitB = u.Decay(10) / u.Second(1)
    UnitC = 80 / u.Second(1)
    UnitD = u.Decay(50) / u.Minute(0.1)
    UnitE = 80 / u.Minute(0.25)
    assert UnitA.mag == 440.0
    assert str(UnitA.symbol) == "Hz"
    assert UnitB.mag == 10.0
    assert str(UnitB.symbol) == "Bq"
    assert UnitC.mag == 80.0
    assert UnitD.mag == 500.0
    assert UnitE.mag == 320.0

    frequency = u.Hertz(50)
    radioactivity = u.Becquerel(50)
    rpm = u.RevolutionsPerMinute(3000)
    angular_vel = u.RadianPerSecond(3.14)
    f_synth = u.Cycle(100) / u.Second(2)
    d_synth = u.Decay(100) / u.Second(2)
    assert f_synth.dimension == "frequency"
    assert d_synth.dimension == "radioactivity"
    assert f_synth.mag == 50.0
    assert d_synth.mag == 50.0
    with pytest.raises(SemanticMismatchError):
        frequency.to(u.Becquerel)
    with pytest.raises(SemanticMismatchError):
        radioactivity.to(u.Hertz)
    with pytest.raises(SemanticMismatchError):
        angular_vel.to(u.Hertz)
    assert rpm.to(u.Hertz).mag == 50.0

    energy = u.Joule(10)
    mass = u.Kilogram(2)
    spec_energy_5 = energy / mass
    spec_energy_100 = (u.Meter(10) ** 2) / (u.Second(1) ** 2)

    abs_dose_synth = u.Radiation(1) * spec_energy_100
    eq_dose_synth = u.BiologicalEffect(20) * spec_energy_100
    dose_from_pure = spec_energy_5 * u.Radiation(1)
    eq_dose_from_pure = spec_energy_5 * u.BiologicalEffect(1)

    assert abs_dose_synth.mag == 100.0
    assert str(abs_dose_synth.symbol) == "Gy"
    assert eq_dose_synth.mag == 2000.0
    assert str(eq_dose_synth.symbol) == "Sv"
    assert str(dose_from_pure.symbol) == "Gy"
    assert str(eq_dose_from_pure.symbol) == "Sv"

    pure_rate_37 = 37000000000 / u.Second(1)
    assert pure_rate_37.mag == 37000000000.0
    assert pure_rate_37.dimension == "rate"

    freq_37 = pure_rate_37 * u.Cycle(1)
    assert freq_37.mag == 37000000000.0
    assert freq_37.dimension == "frequency"
    assert freq_37.to(u.Gigahertz).mag == 37.0

    radio_37 = pure_rate_37 * u.Decay(1)
    assert radio_37.mag == 37000000000.0
    assert radio_37.dimension == "radioactivity"
    assert radio_37.to(u.Curie).mag == 1.0

    baud = (9600000 / u.Second(1)) * u.SymbolData(1)
    assert baud.mag == 9600000.0
    assert baud.dimension == "baud_rate"
    assert baud.to(u.Kilobaud).mag == 9600.0

    pure_spec_energy = u.Joule(100) / u.Kilogram(1)
    assert pure_spec_energy.mag == 100.0
    assert pure_spec_energy.dimension == "specific_energy"

    gray_dose = pure_spec_energy * u.Radiation(1)
    assert gray_dose.mag == 100.0
    assert gray_dose.dimension == "absorbed_dose"
    assert gray_dose.to(u.Rad).mag == 10000.0

    sievert_dose = pure_spec_energy * u.BiologicalEffect(20)
    assert sievert_dose.mag == 2000.0
    assert sievert_dose.dimension == "equivalent_dose"
    assert sievert_dose.to(u.RoentgenEquivalentMan).mag == 200000.0

    pure_energy = u.Joule(50)
    assert pure_energy.mag == 50.0
    assert pure_energy.dimension == "energy"

    torque = pure_energy / u.Radian(1)
    assert torque.mag == 50.0
    assert torque.dimension == "torque"

    photon_E = pure_energy / u.Photon(1)
    assert photon_E.mag == 50.0
    assert photon_E.dimension == "photon_energy"
    assert photon_E.to(u.ElectronVoltPerPhoton).mag == pytest.approx(3.1207e+20, rel=1e-3)

    pure_grad = 100 / u.Meter(1)
    assert pure_grad.mag == 100.0
    assert pure_grad.dimension == "linear_attenuation"

    spatial_f = pure_grad * u.Cycle(1)
    assert spatial_f.mag == 100.0
    assert spatial_f.dimension == "spatial_frequency"
    assert spatial_f.to(u.CyclesPerMeter).mag == 100.0

    wavenumber = pure_grad * u.Radian(1)
    assert wavenumber.mag == 100.0
    assert wavenumber.dimension == "wavenumber"
    assert wavenumber.to(u.Kayser).mag == 1.0

    vol = u.Meter(1) ** 3
    mass_den = u.Kilogram(1000) / vol
    num_den = u.Count(1000000) / vol
    assert mass_den.mag == 1000.0
    assert mass_den.dimension == "density"
    assert num_den.mag == 1000000.0
    assert num_den.dimension == "number_density"
    assert num_den.to(u.ParticlesPerCubicCentimeter).mag == pytest.approx(1.0)

    with pytest.raises(SemanticMismatchError, match="Phantom Collision"):
        u.Hertz(100).to(u.Becquerel)
    with pytest.raises(SemanticMismatchError, match="Phantom Collision"):
        f_hz.to(u.Becquerel)
    with pytest.raises(SemanticMismatchError, match="Phantom Collision"):
        _ = abs_dose_synth + eq_dose_synth
    with pytest.raises(SemanticMismatchError, match="Phantom Collision"):
        abs_dose_synth.to(u.Sievert)
    with pytest.raises(TypeError, match="dimensionless scalar/array"):
        _ = r_decay - 1
    with pytest.raises(PhysicalAlgebraError):
        _ = r_decay - r_decay ** 0.5
    with pytest.raises(SemanticMismatchError, match="Phantom Collision.*frequency.*radioactivity"):
        _ = freq_37 + radio_37
    with pytest.raises(SemanticMismatchError, match="Phantom Collision.*baud_rate.*frequency"):
        _ = baud + freq_37
    with pytest.raises(SemanticMismatchError, match="Phantom Collision.*radiation.*biological_effect"):
        _ = gray_dose.to(u.Sievert)
    with pytest.raises(SemanticMismatchError, match="Phantom Collision.*torque.*photon_energy"):
        _ = torque + photon_E


def test_phantom_unit_domain_guardrails():
    """
    Exhaustive validation of phantom unit resolution, exclusive domain isolation,
    blank canvas casting, and SI core extractor/base converter operators.
    """
    Rate = 1 / u.Second
    Hertz = u.Cycle / u.Second
    Becquerel = u.Decay / u.Second
    Baud = u.SymbolData / u.Second
    ExpansionPerSecond = u.Expansion / u.Second
    SpecificEnergy = u.Joule / u.Kilogram
    Gray = (u.Joule * u.Radiation) / u.Kilogram
    Sievert = (u.Joule * u.BiologicalEffect) / u.Kilogram
    Pascal = u.Newton / u.Meter**2
    JoulePerCubicMeter = (u.Joule * u.EnergyContent) / u.Meter**3
    u.EnergyDensityUnit
    Density = u.Kilogram / u.Meter**3
    ParticlesPerCubicMeter = u.Count / u.Meter**3
    JoulePerPhoton = u.Joule / u.Photon
    Torque = u.Joule / u.Radian

    r = Rate(10)
    hz_cast = r.to(Hertz)
    assert hz_cast.mag == 10.0
    assert hz_cast.dimension == "frequency"

    bq_cast = r.to(Becquerel)
    assert bq_cast.mag == 10.0
    assert bq_cast.dimension == "radioactivity"

    bd_cast = r.to(Baud)
    assert bd_cast.mag == 10.0
    assert bd_cast.dimension == "baud_rate"

    assert hz_cast.to(Rate).mag == 10.0
    assert bq_cast.to(Rate).mag == 10.0

    chain_cast = Becquerel(10).to(Rate).to(Hertz)
    assert chain_cast.dimension == "frequency"
    assert chain_cast.mag == 10.0

    with pytest.raises(SemanticMismatchError, match="Phantom Collision"):
        Hertz(50).to(Becquerel)
    with pytest.raises(SemanticMismatchError, match="Phantom Collision"):
        Baud(9600).to(Hertz)
    with pytest.raises(SemanticMismatchError, match="Phantom Collision"):
        Gray(5).to(Sievert)
    with pytest.raises(SemanticMismatchError, match="Phantom Collision|Exclusive Domain Locked"):
        JoulePerCubicMeter(100).to(Pascal)

    with pytest.raises(SemanticMismatchError, match="Exclusive Domain Locked"):
        Rate(70).to(ExpansionPerSecond)
    with pytest.raises(SemanticMismatchError, match="Exclusive Domain Locked"):
        SpecificEnergy(5).to(Gray)
    with pytest.raises(SemanticMismatchError, match="Exclusive Domain Locked"):
        SpecificEnergy(5).to(Sievert)

    synthesized_gray = SpecificEnergy(5) * u.Radiation(1)
    assert synthesized_gray.dimension == "absorbed_dose"
    assert synthesized_gray.mag == 5.0

    synthesized_sievert = SpecificEnergy(5) * u.BiologicalEffect(2)
    assert synthesized_sievert.dimension == "equivalent_dose"
    assert synthesized_sievert.mag == 10.0

    synthesized_hubble = Rate(70) * u.Expansion(1)
    assert synthesized_hubble.dimension == "expansion_rate"
    assert synthesized_hubble.mag == 70.0

    assert math.isclose(Sievert(1).to(u.RoentgenEquivalentMan).mag, 100.0, rel_tol=1e-5)
    assert math.isclose(Gray(1).to(u.Rad).mag, 100.0, rel_tol=1e-5)

    with pytest.raises(SemanticMismatchError, match="Phantom Collision"):
        _ = Baud(100) + Hertz(100)
    with pytest.raises(SemanticMismatchError, match="Phantom Collision"):
        _ = Becquerel(50) - ExpansionPerSecond(50)
    with pytest.raises(SemanticMismatchError, match="Phantom Collision"):
        _ = Gray(10) + Sievert(10)
    with pytest.raises(SemanticMismatchError, match="Phantom Collision"):
        _ = JoulePerCubicMeter(100) + Pascal(100)
    with pytest.raises(PhysicalAlgebraError):
        _ = ParticlesPerCubicMeter(1000) + Density(1000)
    with pytest.raises(SemanticMismatchError, match="Phantom Collision"):
        _ = Torque(50) + u.Joule(50)
    with pytest.raises(SemanticMismatchError, match="Phantom Collision"):
        _ = JoulePerPhoton(1e-19) + u.Joule(1e-19)

    resolved_spec = Sievert(50) / u.BiologicalEffect(1)
    assert resolved_spec.dimension == "specific_energy"
    assert resolved_spec.mag == 50.0

    resolved_spec2 = Gray(25) / u.Radiation(1)
    assert resolved_spec2.dimension == "specific_energy"
    assert resolved_spec2.mag == 25.0

    resolved_energy = Torque(100) * u.Radian(1)
    assert resolved_energy.dimension == "energy"
    assert resolved_energy.mag == 100.0

    raw_symbols = Baud(9600) * u.Second(2)
    assert raw_symbols.dimension == "symbol"
    assert raw_symbols.mag == 19200.0

    rad = u.Radian(math.pi)
    deg = rad.to(u.Degree)
    assert math.isclose(deg.mag, 180.0, rel_tol=1e-5)
    wrapped_deg = u.Degree(360).wrap()
    assert math.isclose(wrapped_deg.mag, 0.0, abs_tol=1e-9)
    wrapped_rad = u.Radian(2 * math.pi).wrap()
    assert math.isclose(wrapped_rad.mag, 0.0, abs_tol=1e-9)
    dms_str = u.Degree(12.50).to_dms()
    assert "12° 30' 0.00\"" in dms_str
    assert u.Steradian(4 * math.pi).mag == pytest.approx(12.566, rel=1e-3)

    with pytest.raises(TypeError, match="Cannot add a dimensionless scalar"):
        _ = Sievert(10) + 5.0
    with pytest.raises(TypeError, match="Cannot subtrack a dimensionless scalar"):
        _ = Gray(10) - 2
    arr = np.array([1.0, 2.0, 3.0])
    with pytest.raises(TypeError, match="Cannot add a dimensionless scalar"):
        _ = Baud(10) + arr

    Planck_Action = u.Joule(10) * u.Second(1)
    Angular_Mom = (u.Kilogram(10) * u.Meter(1) ** 2) / (u.Second(1) * u.Radian(1))
    assert Planck_Action.dimension == "action"
    assert Angular_Mom.dimension == "angular_momentum"
    with pytest.raises(SemanticMismatchError, match="Domain Lock"):
        Planck_Action.to(Angular_Mom.__class__)
    with pytest.raises(SemanticMismatchError, match="Phantom Collision"):
        _ = Planck_Action + Angular_Mom

    k_spring = u.Newton(50) / u.Meter(1)
    gamma_water = u.Newton(50) / u.Meter(1)
    assert k_spring.dimension == "force_per_length"
    assert gamma_water.dimension == "force_per_length"
    total_fpl = k_spring + gamma_water
    assert total_fpl.mag == 100.0
    assert k_spring.to("stiffness").mag == 50.0
    assert gamma_water.to("surface_tension").mag == 50.0

    pure_candela = u.Candela(10)
    luminous_flux = pure_candela * u.Steradian(1)
    illuminance = luminous_flux / u.Meter(1) ** 2
    assert pure_candela.dimension == "luminous_intensity"
    assert luminous_flux.dimension == "luminous_flux"
    assert illuminance.dimension == "illuminance"
    with pytest.raises(DimensionMismatchError):
        pure_candela.to("lx")

    escaped_hz = Hertz(50).si
    assert escaped_hz.dimension == "rate"
    assert math.isclose(escaped_hz.to(Becquerel).mag, 50.0, rel_tol=1e-5)

    tq = Torque(10)
    raw_energy = tq.si
    assert raw_energy.dimension == "energy"
    assert math.isclose((raw_energy + u.Joule(10)).mag, 20.0, rel_tol=1e-5)

    sv = Sievert(5)
    raw_dose = sv.si
    assert raw_dose.dimension == "specific_energy"
    assert math.isclose(raw_dose.mag, 5.0, rel_tol=1e-5)

    h0 = ExpansionPerSecond(70)
    raw_rate = h0.si
    assert raw_rate.dimension == "rate"
    assert math.isclose(raw_rate.mag, 70.0, rel_tol=1e-5)

    lm = u.Candela(10) * u.Steradian(1)
    raw_cd = lm.si
    assert raw_cd.dimension == "luminous_intensity"
    assert math.isclose(raw_cd.mag, 10.0, rel_tol=1e-5)

    angular_momentum_q = (u.Joule(10) * u.Second(1)) / u.Radian(1)
    raw_action = angular_momentum_q.si
    assert raw_action.dimension == "action"
    assert math.isclose(raw_action.mag, 10.0, rel_tol=1e-5)

    f_50hz = Hertz(50)
    pure_seconds = (1 / f_50hz).si
    assert pure_seconds.dimension == "time"
    assert math.isclose(pure_seconds.mag, 0.02, rel_tol=1e-5)

    jerk_val = u.GravityPerSecond(9)
    base_jerk = ~jerk_val
    assert base_jerk.dimension == "jerk"
    assert math.isclose(base_jerk.mag, 88.25985, rel_tol=1e-5)

    base_ohm = ~u.Ohm(10)
    assert base_ohm.dimension == "electrical_resistance"
    assert math.isclose(base_ohm.mag, 10.0, rel_tol=1e-9)