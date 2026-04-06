"""Tests for ptn.Dataset .phx serialization and PTensor I/O."""

import os
import tempfile

import numpy as np
import pytest

import phaethon as ptn
import phaethon.units as u

try:
    import torch
    from phaethon.pinns import PTensor
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False


def test_phx_format_io():
    """Verify .phx save/load preserves physical dimension, value, and class identity."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_scalar = os.path.join(tmpdir, "scalar.phx")
        file_array = os.path.join(tmpdir, "array.phx")
        file_derived = os.path.join(tmpdir, "derived.phx")

        original_mass = u.Kilogram(50.5)
        ptn.save(file_scalar, ptn.Dataset(mass=original_mass))
        ds_scalar = ptn.load(file_scalar)
        loaded_mass = ds_scalar["mass"].array
        assert loaded_mass.dimension == "mass"
        assert loaded_mass.mag == 50.5
        assert isinstance(loaded_mass, u.Kilogram)

        arr_val = np.array([10.0, 20.0, 30.0])
        original_vel = u.MeterPerSecond(arr_val)
        ptn.save(file_array, ptn.Dataset(vel=original_vel))
        ds_array = ptn.load(file_array)
        loaded_vel = ds_array["vel"].array
        assert loaded_vel.dimension == "speed"
        assert loaded_vel.shape == (3,)
        assert np.allclose(loaded_vel.mag, arr_val)

        original_torque = u.Newton(5) * u.Meter(2) / u.Radian(1)
        ptn.save(file_derived, ptn.Dataset(torque=original_torque))
        ds_derived = ptn.load(file_derived)
        loaded_torque = ds_derived["torque"].value
        assert loaded_torque.dimension == "torque"
        assert loaded_torque.mag == 10.0


@pytest.mark.skipif(not HAS_TORCH, reason="PyTorch not installed")
def test_ptensor_phx_io():
    """Verify .phx I/O preserves PTensor unit and autograd state."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_tensor = os.path.join(tmpdir, "tensor.phx")

        raw_tensor = torch.tensor([[1.0, 2.0], [3.0, 4.0]], requires_grad=True)
        original_pt = PTensor(raw_tensor, unit=u.Volt)
        ptn.save(file_tensor, ptn.Dataset(voltage=original_pt))

        ds_tensor = ptn.load(file_tensor)
        loaded_pt = ds_tensor["voltage"].tensor

        assert isinstance(loaded_pt, PTensor)
        assert loaded_pt.unit.dimension == "electric_potential"
        assert isinstance(loaded_pt.mag, torch.Tensor)
        assert loaded_pt.mag.requires_grad is True
        assert torch.allclose(loaded_pt.mag, raw_tensor)