"""Tests for phaethon.linalg and phaethon.random."""

import numpy as np
import numpy.ma as ma
import pytest

import phaethon as ptn
import phaethon.units as u
from phaethon.exceptions import AxiomViolationError, DimensionMismatchError


def test_native_scientific_compute():
    """
    Integration test for the native compute ecosystem:
    array creation, linear algebra synthesis, vector norms, and stochastic physics.
    """
    raw_matrix = [[1.0, 2.0], [3.0, 4.0]]

    arr_f32 = ptn.array(raw_matrix, u.Meter, dtype=np.float32, ndmin=3, order="F")
    assert arr_f32.shape == (1, 2, 2)
    assert arr_f32.mag.dtype == np.float32
    assert arr_f32.mag.flags["F_CONTIGUOUS"] is True
    assert arr_f32.dimension == "length"

    massive_data = np.arange(1000, dtype=np.float64)
    arr_zero_copy = ptn.asarray(massive_data, u.Joule)
    assert np.shares_memory(massive_data, arr_zero_copy.mag)
    assert arr_zero_copy.dimension == "energy"

    masked_raw = ma.masked_array([10.0, -999.0, 30.0], mask=[0, 1, 0])
    safe_temp = ptn.asanyarray(masked_raw, u.Kelvin)
    assert isinstance(safe_temp.mag, ma.MaskedArray)
    assert safe_temp.mag.mask[1] == True

    A_mat = ptn.array([[4.0, 7.0], [2.0, 6.0]], u.Meter)
    A_inv = ptn.linalg.inv(A_mat)
    assert A_inv.dimension == "linear_attenuation"
    identity = A_mat @ A_inv
    assert identity.dimension == "dimensionless"
    assert np.allclose(identity.mag, np.eye(2))

    A_3x3 = ptn.array([[1, 2, 3], [0, 1, 4], [5, 6, 0]], u.Meter)
    det_vol = ptn.linalg.det(A_3x3)
    assert det_vol.dimension == "volume"
    assert np.isclose(det_vol.mag, 1.0)

    M_mass = ptn.array([[10.0, 2.0], [3.0, 5.0]], u.Kilogram)
    F_force = ptn.array([50.0, 25.0], u.Newton)
    accel_x = ptn.linalg.solve(M_mass, F_force)
    assert accel_x.dimension == "acceleration"
    assert isinstance(accel_x, u.MeterPerSecondSquared)

    F_mat = ptn.array([[50.0, 10.0], [10.0, 25.0]], u.Newton)
    F_vec = ptn.array([100.0, 50.0], u.Newton)
    ratio_x = ptn.linalg.solve(F_mat, F_vec)
    assert ratio_x.dimension == "dimensionless"

    vec_v = ptn.array([3.0, 4.0], u.MeterPerSecond)
    mag_v = ptn.linalg.norm(vec_v)
    assert mag_v.dimension == "speed"
    assert np.isclose(mag_v.mag, 5.0)

    mat_norm = ptn.linalg.norm(M_mass, ord="fro", keepdims=True)
    assert mat_norm.dimension == "mass"
    assert mat_norm.shape == (1, 1)

    p_uni = ptn.random.uniform(low=10.5, high=20.5, size=(5, 5), unit=u.Pascal)
    assert p_uni.shape == (5, 5)
    assert p_uni.dimension == "pressure"
    assert np.all((p_uni.mag >= 10.5) & (p_uni.mag <= 20.5))

    mass_norm = ptn.random.normal(loc=100.0, scale=2.5, size=10, unit="kg")
    assert mass_norm.dimension == "mass"
    assert mass_norm.shape == (10,)

    bq_decay = ptn.random.poisson(lam=50.0, size=(100,), unit=u.Becquerel)
    assert bq_decay.dimension == "radioactivity"
    assert bq_decay.mag.dtype in (np.int32, np.int64)

    t_half = ptn.random.exponential(scale=1.5, size=(3, 3, 3), unit=u.Second)
    assert t_half.dimension == "time"
    assert t_half.ndim == 3

    with pytest.raises(np.linalg.LinAlgError, match="square"):
        ptn.linalg.inv(ptn.array([[1, 2, 3], [4, 5, 6]], u.Meter))

    mat_db = ptn.array([[30, 30], [30, 30]], u.Decibel)
    with pytest.raises(AxiomViolationError, match="You cannot exponentiate"):
        ptn.linalg.det(mat_db)

    with pytest.raises(ValueError, match="physical unit must be specified"):
        ptn.random.uniform(size=5)

    with pytest.raises(np.linalg.LinAlgError, match="at least two-dimensional"):
        ptn.linalg.inv(ptn.array([1, 2, 3], u.Meter))