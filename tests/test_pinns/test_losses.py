"""Tests for BuckinghamPi layer, AxiomLoss, and ResidualLoss."""

import pytest

import phaethon.units as u
from phaethon.exceptions import AxiomViolationError, DimensionMismatchError

try:
    import torch
    from phaethon.pinns import (
        PTensor as PnnTensor,
        BuckinghamPi,
        AxiomLoss,
        ResidualLoss,
    )
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

try:
    from phaethon.exceptions import EquationBalanceError
except ImportError:
    EquationBalanceError = None


@pytest.mark.skipif(not HAS_TORCH, reason="PyTorch not installed")
def test_buckingham_pi_reynolds_number():
    """Verify BuckinghamPi discovers the Reynolds number from fluid variables."""
    pi_layer = BuckinghamPi()

    v = PnnTensor([10.0], unit=u.MeterPerSecond)
    d = PnnTensor([0.5], unit=u.Meter)
    rho = PnnTensor([1000.0], unit=u.KilogramPerCubicMeter)
    mu = PnnTensor([0.001], unit=u.PascalSecond)

    reynolds = pi_layer(v, d, rho, mu)
    assert reynolds.unit.dimension == "dimensionless"
    assert isinstance(reynolds.mag, torch.Tensor)
    assert abs(reynolds.item() - 5000000.0) < 1.0

    with pytest.raises(AxiomViolationError, match="empty null space"):
        _ = pi_layer(v, d, rho)


@pytest.mark.skipif(not HAS_TORCH, reason="PyTorch not installed")
def test_axiom_and_residual_loss():
    """Verify AxiomLoss ReLU penalty and ResidualLoss equation balance guard."""
    mass_tribunal = AxiomLoss(expected_dimension="mass")

    pred_mass = PnnTensor([10.0, -5.0], unit=u.Kilogram)
    penalty = mass_tribunal(pred_mass)
    assert penalty.item() == 2.5

    pred_speed = PnnTensor([10.0, 20.0], unit=u.MeterPerSecond)
    with pytest.raises(DimensionMismatchError, match="Tribunal"):
        _ = mass_tribunal(pred_speed)

    pde_loss = ResidualLoss()
    residual_energy = PnnTensor([5.0, -5.0], unit=u.Joule)
    loss_val = pde_loss(residual_energy, target=0.0)
    assert loss_val.item() == 25.0

    target_wrong = PnnTensor([0.0, 0.0], unit=u.Watt)
    exc_type = EquationBalanceError if EquationBalanceError else DimensionMismatchError
    with pytest.raises(exc_type):
        _ = pde_loss(residual_energy, target=target_wrong)