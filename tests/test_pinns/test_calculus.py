"""Tests for the differential calculus engine (grad, laplace, div, curl) and training loops."""

import pytest

import phaethon.units as u

try:
    import torch
    import torch.nn as nn
    from phaethon.pinns import (
        PTensor as PnnTensor,
        AxiomLoss,
        ResidualLoss,
        BuckinghamPi,
        assemble,
        grad,
        laplace,
        div,
        curl,
    )
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False


@pytest.mark.skipif(not HAS_TORCH, reason="PyTorch not installed")
def test_differential_calculus_engine():
    """Verify grad, laplace, div, and curl synthesize correct physical units."""
    t = PnnTensor([[2.0]], unit=u.Second, requires_grad=True)
    s_mag = 5.0 * (t.mag ** 2) + 2.0 * t.mag
    s = PnnTensor(s_mag, unit=u.Meter)

    v = grad(s, t)
    assert v.unit.dimension == "speed"
    assert v.item() == 22.0

    a = grad(v, t)
    assert a.unit.dimension == "acceleration"
    assert a.item() == 10.0

    xyz = PnnTensor([[1.0, 1.0, 1.0]], unit=u.Meter, requires_grad=True)
    x, y, z = xyz[..., 0:1], xyz[..., 1:2], xyz[..., 2:3]
    T_mag = 3.0 * (x.mag ** 2) + 4.0 * (y.mag ** 2) + 5.0 * (z.mag ** 2)
    T = PnnTensor(T_mag, unit=u.Kelvin)

    lap = laplace(T, xyz)
    assert lap.item() == 24.0
    assert lap.unit.dimension == "spatial_temperature_curvature"

    xyz_div = PnnTensor([[1.0, 2.0, 3.0]], unit=u.Meter, requires_grad=True)
    xd, yd, zd = xyz_div[..., 0], xyz_div[..., 1], xyz_div[..., 2]
    Vx = (xd ** 2) * yd
    Vy = (yd ** 2) * zd
    Vz = (zd ** 2) * xd
    V_div = PnnTensor(torch.stack([Vx, Vy, Vz], dim=-1), unit=u.MeterPerSecond)

    divergence = div(V_div, xyz_div)
    assert divergence.item() == 22.0
    assert divergence.unit.dimension == "rate"

    xyz_curl = PnnTensor([[1.0, 1.0, 1.0]], unit=u.Meter, requires_grad=True)
    xc, yc, zc = xyz_curl[..., 0], xyz_curl[..., 1], xyz_curl[..., 2]
    Ax = -yc
    Ay = xc
    Az = torch.zeros_like(xc)
    A_curl = PnnTensor(torch.stack([Ax, Ay, Az], dim=-1), unit=u.MeterPerSecond)

    curl_A = curl(A_curl, xyz_curl)
    expected_curl = torch.tensor([[0.0, 0.0, 2.0]])
    assert torch.allclose(curl_A.mag, expected_curl)
    assert curl_A.unit.dimension == "rate"


@pytest.mark.skipif(not HAS_TORCH, reason="PyTorch not installed")
def test_heat_equation_training_loop():
    """Integration test: heat equation PINNs training loop converges without error."""
    class HeatNet(nn.Module):
        def __init__(self):
            super().__init__()
            self.mlp = nn.Sequential(nn.Linear(2, 16), nn.Tanh(), nn.Linear(16, 1))

        def forward(self, x_pt, t_pt):
            features = assemble(x_pt, t_pt, dim=-1)
            T_mag = self.mlp(features)
            return PnnTensor(T_mag, unit=u.Kelvin)

    model = HeatNet()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    pde_loss_fn = ResidualLoss()
    axiom_loss_fn = AxiomLoss(expected_dimension="temperature")
    alpha = PnnTensor([1e-4], unit=u.SquareMeterPerSecond)

    x_sensor = PnnTensor(torch.rand(50, 1), unit=u.Meter, requires_grad=True)
    t_sensor = PnnTensor(torch.rand(50, 1), unit=u.Second, requires_grad=True)

    for _ in range(5):
        optimizer.zero_grad()
        T_pred = model(x_sensor, t_sensor)
        dT_dt = grad(T_pred, t_sensor, create_graph=True)
        d2T_dx2 = laplace(T_pred, x_sensor)
        pde_residual = dT_dt - (alpha * d2T_dx2)
        loss = pde_loss_fn(pde_residual, target=0.0) + axiom_loss_fn(T_pred)
        loss.backward()
        optimizer.step()

    assert loss.item() >= 0.0


@pytest.mark.skipif(not HAS_TORCH, reason="PyTorch not installed")
def test_buckingham_pi_sindy_variable_selection():
    """Verify BuckinghamPi SVD correctly eliminates an irrelevant variable (mass in pendulum)."""
    pi_engine = BuckinghamPi()

    T = PnnTensor([2.0], unit=u.Second)
    L = PnnTensor([1.0], unit=u.Meter)
    g = PnnTensor([9.8], unit=u.MeterPerSecondSquared)
    m = PnnTensor([5.0], unit=u.Kilogram)  # irrelevant variable

    _ = pi_engine(T, L, g, m)
    exponents = pi_engine._exponents.tolist()

    assert abs(exponents[3]) < 1e-5, "Mass should have near-zero exponent (irrelevant to pendulum)"
    assert exponents[1] * exponents[2] < 0, "L and g must have opposite signs in the Pi group"