"""Tests for PTensor dimensional synthesis, operations, and multi-physics coupling."""

import pytest

import phaethon.units as u
from phaethon.exceptions import DimensionMismatchError, PhysicalAlgebraError

try:
    import torch
    from phaethon.pinns import PTensor as PnnTensor, cat, stack, assemble
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False


@pytest.mark.skipif(not HAS_TORCH, reason="PyTorch not installed")
def test_ptensor_dimensional_synthesis():
    """Verify PTensor dimensional algebra, autograd continuity, and type safety."""
    mass = PnnTensor([10.0, 20.0], unit=u.Kilogram, requires_grad=True)
    accel = PnnTensor([9.8, 5.0], unit=u.MeterPerSecondSquared)

    assert mass.requires_grad is True
    assert mass.unit.dimension == "mass"
    assert isinstance(mass.mag, torch.Tensor)

    force = mass * accel
    assert force.unit.dimension == "force"
    assert torch.allclose(force.mag, torch.tensor([98.0, 100.0]))
    assert force.grad_fn is not None

    with pytest.raises(PhysicalAlgebraError):
        _ = mass + accel

    total_force = force.sum()
    assert total_force.unit.dimension == "force"
    assert total_force.item() == 198.0


@pytest.mark.skipif(not HAS_TORCH, reason="PyTorch not installed")
def test_ptensor_cat_stack_assemble():
    """Verify pnn.cat scale alignment, pnn.stack, and pnn.assemble stripping."""
    t1 = PnnTensor([[1.0], [2.0]], unit=u.Meter)
    t2 = PnnTensor([[3.0], [4.0]], unit=u.Kilometer)

    res_cat = cat([t1, t2], dim=0)
    assert res_cat.shape == (4, 1)
    assert res_cat.unit == u.Meter
    assert res_cat[2, 0].item() == 3000.0

    res_stack = stack([t1, t2], dim=1)
    assert res_stack.shape == (2, 2, 1)
    assert res_stack.unit == u.Meter

    t_time = PnnTensor([[5.0], [6.0]], unit=u.Second)
    with pytest.raises(DimensionMismatchError, match="cat at index 1"):
        _ = cat([t1, t_time])

    nn_input = assemble(t1, t_time, dim=-1)
    assert isinstance(nn_input, torch.Tensor)
    assert not isinstance(nn_input, PnnTensor)
    assert nn_input.shape == (2, 2)
    assert nn_input[0, 1].item() == 5.0


@pytest.mark.skipif(not HAS_TORCH, reason="PyTorch not installed")
def test_multi_physics_coupling_safety():
    """Verify PTensor blocks illegal cross-domain additions in multi-physics setups."""
    temperature = PnnTensor([300.0], unit=u.Kelvin)
    velocity = PnnTensor([5.0], unit=u.MeterPerSecond)
    gravity = PnnTensor([9.81], unit=u.MeterPerSecondSquared)

    beta = PnnTensor([0.003], unit=u.Kelvin ** -1)
    buoyancy_correct = gravity * beta * temperature
    assert buoyancy_correct.unit.dimension == "acceleration"

    buoyancy_wrong = beta * temperature  # dimensionless

    with pytest.raises(PhysicalAlgebraError):
        accel_ptensor = PnnTensor([1.0], unit=u.MeterPerSecondSquared)
        _ = accel_ptensor + buoyancy_wrong