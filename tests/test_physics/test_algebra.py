"""Tests for dimensional synthesis, collapse, logarithmic algebra, and AST engine."""

import math
import warnings

import numpy as np
import pytest

import phaethon as ptn
import phaethon.units as u
from phaethon.exceptions import AxiomViolationError, DimensionMismatchError, PhysicalAlgebraError
from phaethon.units import Dimensionless


def test_dimensional_collapse():
    """Verify that ratio operations collapse to a pure dimensionless scalar."""
    dist1 = u.Kilometer(1)
    dist2 = u.Meter(250)
    time_val = u.Hour(2)

    distance_ratio = dist1 / dist2
    time_ratio = time_val / u.Minute(30)
    collapse_result = distance_ratio * time_ratio

    assert isinstance(distance_ratio, Dimensionless)
    assert isinstance(time_ratio, Dimensionless)
    assert isinstance(collapse_result, Dimensionless)
    assert collapse_result.mag == 16.0
    assert collapse_result.dimension == "dimensionless"


def test_logarithmic_algebra():
    """Verify logarithmic addition (pH and dB) obeys implicit linearization rules."""
    acid1 = u.pH(2.0)
    acid2 = u.pH(2.0)
    acid_mix = acid1 + acid2
    assert math.isclose(acid_mix.mag, 1.69897, rel_tol=1e-4)
    assert type(acid_mix).__name__ == "pH"

    sound1 = u.Decibel(30)
    sound2 = u.Decibel(30)
    sound_total = sound1 + sound2
    assert math.isclose(sound_total.mag, 33.0103, rel_tol=1e-4)

    with pytest.raises(ptn.exceptions.AxiomViolationError):
        _ = sound1 ** 2

    with pytest.raises(ptn.exceptions.AxiomViolationError):
        _ = acid1 // 2


def test_deep_unit_synthesis():
    """Verify deep synthesis chains resolve correctly to canonical registry classes."""
    mass = u.Gram(5000)
    acceleration = u.KilometerPerHourSquared(12960)
    force = mass * acceleration

    official_force = force.to(u.Newton)
    assert official_force.mag == 5.0
    assert official_force.dimension == "force"
    assert type(official_force).__name__ == "Newton"

    area = u.SquareMeter(0.5)
    pressure = official_force / area

    official_pressure = pressure.to(u.Pascal)
    assert official_pressure.mag == 10.0
    assert official_pressure.dimension == "pressure"


def test_linear_nonlinear_mixed_ops():
    """Verify dB gain/attenuation applied to linear Watt units."""
    gain_db = u.Decibel(30)
    input_power = u.Watt(2)
    output_power = gain_db * input_power
    assert output_power.dimension == "power"
    assert type(output_power).__name__ == "Watt"
    assert math.isclose(output_power.mag, 2000.0, rel_tol=1e-5)

    attenuation_db = u.Decibel(10)
    initial_power = u.Watt(500)
    final_power = initial_power / attenuation_db
    assert final_power.dimension == "power"
    assert math.isclose(final_power.mag, 50.0, rel_tol=1e-5)

    sound_a = u.Decibel(30)
    sound_b = u.Decibel(30)
    sound_total = sound_a + sound_b
    sound_diff = sound_total - sound_b
    assert type(sound_total).__name__ == "Decibel"
    assert math.isclose(sound_total.mag, 33.0103, rel_tol=1e-4)
    assert math.isclose(sound_diff.mag, 30.0, rel_tol=1e-4)

    pure_ratio = u.Decibel(20).to(u.Dimensionless)
    assert type(pure_ratio).__name__ == "Dimensionless"
    assert math.isclose(pure_ratio.mag, 100.0, rel_tol=1e-5)

    test_db = u.Decibel(15)
    with pytest.raises(ptn.exceptions.AxiomViolationError, match="You cannot exponentiate"):
        _ = test_db ** 2
    with pytest.raises(ptn.exceptions.AxiomViolationError, match="You cannot exponentiate"):
        _ = test_db // 2
    with pytest.raises(ptn.exceptions.AxiomViolationError, match="You cannot exponentiate"):
        _ = test_db % 3


def test_axiom_strictness_hierarchy():
    """Validate all 5 axiom strictness levels across raw ingestion and math operations."""
    with ptn.using(axiom_strictness_level="default"):
        with pytest.raises(AxiomViolationError):
            _ = u.Meter(-10)
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            res = u.Meter(5) - u.Meter(10)
            assert res.mag == -5.0
            assert len(w) == 0

    with ptn.using(axiom_strictness_level="strict_warn"):
        with pytest.raises(AxiomViolationError):
            _ = u.Meter(-1)
        with pytest.warns(UserWarning, match="Phaethon Axiom Warning"):
            res_arr = u.Meter(np.array([1, 2])) - u.Meter(np.array([5, 5]))
            assert np.array_equal(res_arr.mag, np.array([-4, -3]))

    with ptn.using(axiom_strictness_level="strict"):
        with pytest.raises(AxiomViolationError):
            _ = u.Kelvin(-273)
        with pytest.raises(AxiomViolationError):
            _ = u.Pascal(100) - u.Pascal(200)

    with ptn.using(axiom_strictness_level="loose_warn"):
        with pytest.warns(UserWarning, match="Phaethon Axiom Warning"):
            dirty_val = u.Meter(-5)
            assert dirty_val.mag == -5.0
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            res = u.Newton(10) * -1
            assert res.mag == -10.0
            assert len(w) == 0

    with ptn.using(axiom_strictness_level="ignore"):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            x = u.Meter(-999)
            y = x * 2
            z = u.Kelvin(np.array([-10, -20, -30]))
            assert y.mag == -1998.0
            assert z.mag[0] == -10.0
            assert len(w) == 0

    with ptn.using(axiom_strictness_level="default"):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            diff = u.Meter(10) - u.Meter(50)
            positive_val = np.abs(diff)
            assert positive_val.mag == 40.0
            assert len(w) == 0


def test_metaclass_ast_synthesis():
    """Validate Metaclass AST canonical class recovery across physics domains."""
    Ohm = u.Kilogram * u.Meter**2 / (u.Second**3 * u.Ampere**2)
    Volt = u.Kilogram * u.Meter**2 / (u.Second**3 * u.Ampere)
    Farad = (u.Ampere * u.Second) / Volt
    Coulomb = Farad * Volt
    Weber = Volt * u.Second
    Tesla = Weber / u.Meter ** 2
    Gravity = u.Meter ** 3 / (u.Kilogram * u.Second ** 2)
    Newton = u.Kilogram * u.Meter / u.Second ** 2
    Joule = Newton * u.Meter
    Watt = Joule / u.Second
    Henry = (Volt * u.Second) / u.Ampere
    Pascal = Newton / u.Meter ** 2
    JoulePerKelvin = Joule / u.Kelvin
    R_Unit = Joule / (u.Mole * u.Kelvin)
    MagneticFieldStrength = u.Ampere / u.Meter
    JoulePerKilogram = Joule / u.Kilogram
    Gray = JoulePerKilogram * u.Radiation
    Sievert = JoulePerKilogram * u.BiologicalEffect
    DynamicViscosity = Pascal * u.Second
    Lumen = u.Candela * u.Steradian
    Lux = Lumen / u.Meter**2
    SpecificEnergy = Joule / u.Kilogram
    Momentum = u.Kilogram * (u.Meter / u.Second)
    SpringConstant = Newton / u.Meter
    CurrentDensity = u.Ampere / u.Meter**2
    StefanBoltzmann = Watt / (u.Meter**2 * u.Kelvin**4)
    Planck = Joule * u.Second
    SpecificHeat = Joule / (u.Kilogram * u.Kelvin)
    ThermalConductivity = Watt / (u.Meter * u.Kelvin)
    JoulePM3 = (u.Joule * u.EnergyContent) / u.Meter ** 3
    GrayPerSecond = Gray / u.Second
    Volume = u.Meter ** 3
    FlowRate = Volume / u.Second
    KinematicViscosity = u.Meter**2 / u.Second
    SurfaceTension = Newton / u.Meter
    Velocity = u.Meter / u.Second
    Density = u.Kilogram / u.Meter ** 3
    Reynold = (Density * Velocity * u.Meter) / DynamicViscosity
    Rate = 1 / u.Second
    Hertz = u.Cycle / u.Second
    Becquerel = u.Decay / u.Second
    ExpansionPerSecond = u.Expansion / u.Second

    assert Ohm.__name__ == "Ohm"
    assert Volt.__name__ == "Volt"
    assert Farad.__name__ == "Farad"
    assert Coulomb.__name__ == "Coulomb"
    assert Weber.__name__ == "Weber"
    assert Tesla.__name__ == "Tesla"
    assert Henry.__name__ == "Henry"
    assert Gravity.__name__ == "CubicMeterPerKilogramSecondSquared"
    assert Newton.__name__ == "Newton"
    assert Joule.__name__ == "Joule"
    assert Watt.__name__ == "Watt"
    assert Pascal.__name__ == "Pascal"
    assert JoulePerKelvin.__name__ == "JoulePerKelvin"
    assert R_Unit.__name__ == "JoulePerMoleKelvin"
    assert MagneticFieldStrength.__name__ == "AmperePerMeter"
    assert JoulePerKilogram.__name__ == "JoulePerKilogram"
    assert Gray.__name__ == "Gray"
    assert Sievert.__name__ == "Sievert"
    assert DynamicViscosity.__name__ == "PascalSecond"
    assert Lux.__name__ == "Lux"
    assert SpecificEnergy.__name__ == "JoulePerKilogram"
    assert Momentum.__name__ == "KilogramMeterPerSecond"
    assert SpringConstant.__name__ == "NewtonPerMeter"
    assert CurrentDensity.__name__ == "AmperePerSquareMeter"
    assert StefanBoltzmann.__name__ == "WattPerSquareMeterKelvinFourth"
    assert Planck.__name__ == "JouleSecond"
    assert SpecificHeat.__name__ == "JoulePerKilogramKelvin"
    assert ThermalConductivity.__name__ == "WattPerMeterKelvin"
    assert ExpansionPerSecond.__name__ == "ExpansionPerSecond"
    assert JoulePM3.__name__ == "JoulePerCubicMeter"
    assert GrayPerSecond.__name__ == "GrayPerSecond"
    assert Volume.__name__ == "CubicMeter"
    assert FlowRate.__name__ == "CubicMeterPerSecond"
    assert KinematicViscosity.__name__ == "SquareMeterPerSecond"
    assert SurfaceTension.__name__ == "NewtonPerMeter"
    assert Density.__name__ == "KilogramPerCubicMeter"
    assert Reynold.__name__ == "Dimensionless"
    assert Hertz.__name__ == "Hertz"
    assert Becquerel.__name__ == "Becquerel"
    assert Rate.dimension == "rate"
    assert "1" in repr(Rate(1)) and "s" in repr(Rate(1))

    Megapascal = 1e6 * Pascal
    Gigapascal = 1e9 * Pascal
    Electronvolt = 1.602176634e-19 * Joule
    Barn = 1e-28 * u.Meter**2
    Picobarn = 1e-12 * Barn
    Kilometer = 1000 * u.Meter
    Megaparsec = 3.08567758e22 * u.Meter

    assert Gigapascal.__name__ == "Gigapascal"
    assert Megaparsec.__name__ == "Megaparsec"
    assert Picobarn.__name__ == "Picobarn"
    assert Electronvolt.__name__ == "Electronvolt"

    car_mass = u.Kilogram(1500)
    car_velocity = Velocity(20)
    kinetic_energy = 0.5 * car_mass * car_velocity**2
    time_val = u.Second(10)
    car_power = kinetic_energy / time_val
    assert "Joule" in repr(kinetic_energy)
    assert math.isclose(kinetic_energy.mag, 300000.0, rel_tol=1e-6)
    assert "Watt" in repr(car_power)
    assert math.isclose(car_power.mag, 30000.0, rel_tol=1e-6)

    m1, m2 = u.Kilogram(70), u.Kilogram(5.972e24)
    radius = u.Meter(6.371e6)
    G_val = Gravity(6.674e-11)
    gravity_force = G_val * (m1 * m2) / radius**2
    assert "Newton" in repr(gravity_force)
    assert math.isclose(gravity_force.mag, 687.3672422971172, rel_tol=1e-9)
    assert "kg" in gravity_force.decompose() and "m" in gravity_force.decompose()

    Epsilon0 = 8.854e-12 * (u.Ampere**2 * u.Second**4) / (u.Kilogram * u.Meter**3)
    Mu0 = 1.256e-6 * (u.Kilogram * u.Meter) / (u.Second**2 * u.Ampere**2)
    c_calc = (Epsilon0 * Mu0) ** (-0.5)
    ly = c_calc(1)
    assert math.isclose(ly.to(Velocity).mag, 299792458.0, rel_tol=1e-3)
    assert "m/s" in ly.decompose() or "m·s⁻¹" in ly.decompose().replace("·", "*")

    m_rel = u.Kilogram(1)
    c_exact = Velocity(299792458)
    energy_rel = m_rel * c_exact**2
    h_val = Planck(6.626e-34)
    planck_length = (h_val * G_val / c_exact**3) ** 0.5
    assert "Joule" in repr(energy_rel)
    assert math.isclose(energy_rel.mag, 8.987551787e16, rel_tol=1e-6)
    assert math.isclose(planck_length.mag, 4.05124e-35, rel_tol=1e-4)

    I0 = Watt(1e-12) / (u.Meter(1) ** 2)
    I_rock = Watt(1.0) / (u.Meter(1) ** 2)
    ratio = I_rock / I0
    sound_level = ratio.to(u.Decibel)
    db_total = u.Decibel(120) + u.Decibel(120)
    inversed_sound = ~u.Decibel(60)
    assert "Decibel" in repr(sound_level)
    assert math.isclose(sound_level.mag, 120.0, rel_tol=1e-9)
    assert math.isclose(db_total.mag, 123.0102999, rel_tol=1e-5)
    assert "Dimensionless" in repr(inversed_sound)
    assert math.isclose(float(inversed_sound), 1000000.0, rel_tol=1e-6)

    e_charge = Coulomb(1.602176634e-19)
    h_bar = Planck(6.62607015e-34) / (2 * math.pi)
    FaradPerMeter = Farad / u.Meter
    epsilon0_exact = FaradPerMeter(8.8541878128e-12)
    alpha = (e_charge**2) / (epsilon0_exact * h_bar * c_exact * (4 * math.pi))
    nu = DynamicViscosity(1.5) / Density(1200)
    gamma = (u.Dimensionless(1.0) - (Velocity(250000000) / c_exact) ** 2) ** (-0.5)
    assert "Dimensionless" in repr(alpha)
    assert math.isclose(alpha.mag, 0.00729735, rel_tol=1e-5)
    assert math.isclose(1 / alpha.mag, 137.035999, rel_tol=1e-5)
    assert "SquareMeterPerSecond" in repr(nu)
    assert math.isclose(nu.mag, 0.00125, rel_tol=1e-9)
    assert math.isclose(gamma.mag, 1.811922, rel_tol=1e-5)

    Kappa = (8 * math.pi * G_val) / (c_exact**4)
    assert math.isclose(Kappa.mag, 2.07655e-43, rel_tol=1e-4)
    assert "s" in Kappa.decompose() and "kg" in Kappa.decompose()

    strain_matrix = np.array([
        [0.001, 0.0002, 0.0],
        [0.0002, 0.001, 0.0],
        [0.0, 0.0, 0.0005],
    ])
    stress_tensor = Gigapascal(70) * strain_matrix
    von_mises = np.sqrt(0.5 * (
        (stress_tensor[0, 0] - stress_tensor[1, 1]) ** 2
        + (stress_tensor[1, 1] - stress_tensor[2, 2]) ** 2
        + (stress_tensor[2, 2] - stress_tensor[0, 0]) ** 2
        + 6 * (stress_tensor[0, 1] ** 2 + stress_tensor[1, 2] ** 2 + stress_tensor[2, 0] ** 2)
    ))
    assert "Gigapascal" in repr(stress_tensor)
    assert isinstance(stress_tensor.mag, np.ndarray)
    assert math.isclose(von_mises.to(Megapascal).mag, 42.5793, rel_tol=1e-4)

    np.random.seed(42)
    velocity_field = Velocity(np.random.uniform(1, 10, (3, 2, 2, 3)))
    specific_energy_field = 0.5 * (velocity_field ** 2).sum(axis=-1)
    energy_jkg = specific_energy_field.to(JoulePerKilogram)
    assert specific_energy_field.shape == (3, 2, 2)
    assert "JoulePerKilogram" in repr(energy_jkg)
    assert np.allclose(specific_energy_field[0, 0].mag, energy_jkg[0, 0].mag, rtol=1e-9)

    E_higgs = Electronvolt(125.1e9)
    m_higgs = E_higgs / (c_exact**2)
    sigma = Barn(50 * 1e-15)
    InvMeterSqSec = 1 / (u.Meter**2 * u.Second)
    Luminosity = InvMeterSqSec(1e34 * 1e4)
    EventRate = Luminosity * sigma
    RealEventRate = EventRate.to(Rate)
    assert "kg" in m_higgs.decompose()
    assert math.isclose(m_higgs.to(u.Kilogram).mag, 2.23011e-25, rel_tol=1e-4)
    assert math.isclose(RealEventRate.mag, 0.0005, rel_tol=1e-5)

    H0 = Velocity(70_000) / Megaparsec(1)
    T_hubble = 1 / H0
    T_hubble_sec = T_hubble.to(u.Second)
    age_gyr = T_hubble_sec.mag / (3600 * 24 * 365.25 * 1e9)
    assert "1/s" in H0.decompose() or "s⁻¹" in H0.decompose()
    assert math.isclose(H0.to(Rate).mag, 2.26855e-18, rel_tol=1e-4)
    assert math.isclose(age_gyr, 13.97, rel_tol=1e-3)