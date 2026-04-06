"""Tests for BaseUnit instantiation, operators, NumPy proxy, and tolerance."""

import numpy as np
import pytest

import phaethon as ptn
import phaethon.units as u
from phaethon.exceptions import (
    AxiomViolationError,
    DimensionMismatchError,
    PhysicalAlgebraError,
)


def test_physics_engine_core():
    """Integration test for fundamental dimensional synthesis across common domains."""
    distance = u.Kilometer(3.6)
    time_val = u.Hour(1)
    speed = distance / time_val
    assert speed.dimension == "speed"
    assert speed.to(u.MeterPerSecond).mag == 1.0

    current = u.Ampere(2.0)
    resistance = u.Ohm(50.0)
    voltage = current * resistance
    assert voltage.dimension == "electric_potential"
    assert voltage.mag == 100.0

    force = u.Newton(500.0)
    area = u.SquareMeter(2.0)
    pressure = force / area
    assert pressure.mag == 250.0

    field = u.Hectare(1.0)
    tile = u.SquareMeter(1.0)
    tile_count = field / tile
    assert tile_count.dimension == "dimensionless"
    assert tile_count.mag == 10000.0

    mass = u.Kilogram(10.0)
    vel = u.MeterPerSecond(5.0)
    momentum = mass * vel
    assert momentum.dimension == "momentum"
    assert momentum.mag == 50.0

    power_ac = u.Kilowatt(1.5)
    duration = u.Hour(2.0)
    energy = power_ac * duration
    assert energy.dimension == "energy"
    assert energy.mag == 3.0
    assert energy._to_base_value() == 10800000.0

    chain_result = u.Meter(10) / u.Centimeter(150) * u.Kilometer(0.005)
    assert "Kilometer" in str(repr(chain_result))
    assert np.isclose(chain_result.mag, 0.033333)


def test_operator_arithmetic():
    """Verify arithmetic operators (+, -, *, /, //, %, **) and comparison semantics."""
    x = u.Volt(-10.555)
    assert (+x).mag == -10.555
    assert (-x).mag == 10.555
    assert abs(x).mag == 10.555
    assert round(x, 1).mag == -10.6

    m = u.Meter(10.0)
    assert (m * 2).mag == 20.0
    assert (2 * m).mag == 20.0
    assert (m / 2).mag == 5.0
    assert (m // 3).mag == 3.0
    assert (m % 3).mag == 1.0
    assert (m ** 2).dimension == "area"

    a = u.Kilometer(1.0)
    b = u.Meter(500.0)
    assert (a + b).mag == 1.5
    assert (a - b).mag == 0.5
    assert (a / b).mag == 2.0
    assert (a // b).mag == 2.0
    assert (a % b).mag == 0.0

    cm_100 = u.Centimeter(100.0)
    m_1 = u.Meter(1.0)
    m_2 = u.Meter(2.0)
    assert cm_100 == m_1
    assert m_2 > cm_100
    assert cm_100 != m_2
    assert (cm_100 == "not-a-unit") is False

    with pytest.raises(PhysicalAlgebraError):
        _ = u.Meter(10) + u.Second(5)


def test_matrix_multiplication():
    """Verify @ operator triggers dimensional synthesis via np.matmul."""
    V = u.Volt(np.array([[10.0, 20.0, 30.0], [40.0, 50.0, 60.0]]))
    I = u.Ampere(np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]]))
    P = V @ I
    assert P.mag.shape == (2, 2)
    assert P.mag[0, 0] == 220.0

    force = u.Newton(np.array([100.0, 200.0]))
    swap = np.array([[0.0, 1.0], [1.0, 0.0]])
    swapped = force @ swap
    assert swapped.dimension == "force"
    assert np.all(swapped.mag == np.array([200.0, 100.0]))

    with pytest.raises(ValueError):
        _ = u.Volt(np.array([[1, 2]])) @ u.Ampere(np.array([[1, 2]]))


def test_baseunit_numpy_proxy():
    """Verify NumPy proxy methods (shape, T, flatten, reshape, sum, mean, max, min)."""
    arr = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
    V = u.Volt(arr)

    assert V.shape == (2, 3)
    assert V.ndim == 2

    V_T = V.T
    assert V_T.shape == (3, 2)
    assert V_T.dimension == "electric_potential"

    V_flat = V.flatten()
    assert V_flat.shape == (6,)
    assert V_flat.dimension == "electric_potential"

    V_reshaped = V.reshape((3, 2))
    assert V_reshaped.shape == (3, 2)

    total = V.sum()
    assert total.mag == 21.0
    assert total.dimension == "electric_potential"

    assert V.max().mag == 6.0
    assert V.min().mag == 1.0

    mean_axis = V.mean(axis=1)
    assert mean_axis.shape == (2,)
    assert np.allclose(mean_axis.mag, np.array([2.0, 5.0]))
    assert mean_axis.dimension == "electric_potential"


def test_floating_point_tolerance():
    """Verify atol and rtol protect equality comparisons from FPU artifacts."""
    a = u.Meter(1e-15)
    b = u.Meter(0.0)
    assert a == b

    jupiter_1 = u.Kilogram(1.898e27)
    jupiter_2 = u.Kilogram(1.898000001e27)
    assert jupiter_1 == jupiter_2

    with ptn.using(rtol=0.0, atol=1e-20):
        assert jupiter_1 != jupiter_2