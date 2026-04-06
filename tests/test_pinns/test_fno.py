"""Tests for SpectralConv1d, FFT dimensional inversion, and FNO training."""

import pytest

import phaethon.units as u

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    from phaethon.pinns import PTensor as PnnTensor, SpectralConv1d, fft, ifft
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False


@pytest.mark.skipif(not HAS_TORCH, reason="PyTorch not installed")
def test_spectral_conv1d_forward():
    """Verify SpectralConv1d preserves spatial dimension and output shape."""
    batch_size, in_channels, out_channels, grid_points, modes = 2, 3, 4, 64, 8

    wave_mag = torch.rand(batch_size, in_channels, grid_points)
    wave_pt = PnnTensor(wave_mag, unit=u.MeterPerSecond)

    fno_layer = SpectralConv1d(in_channels=in_channels, out_channels=out_channels, modes=modes)
    out_pt = fno_layer(wave_pt)

    assert out_pt.shape == (batch_size, out_channels, grid_points)
    assert out_pt.unit.dimension == "speed"


@pytest.mark.skipif(not HAS_TORCH, reason="PyTorch not installed")
def test_fft_dimensional_inversion():
    """Verify FFT inverts physical units and IFFT restores them exactly."""
    x_mag = torch.rand(2, 3, 16)
    x_pt = PnnTensor(x_mag, unit=u.Meter)

    x_freq = fft(x_pt, dim=-1)
    assert x_freq.unit == u.Meter ** -1
    assert x_freq.mag.dtype in (torch.complex64, torch.complex128)

    x_recon = ifft(x_freq, dim=-1, n=x_mag.shape[-1])
    assert x_recon.unit == u.Meter
    assert torch.allclose(x_pt.mag, x_recon.mag, atol=1e-5)


@pytest.mark.skipif(not HAS_TORCH, reason="PyTorch not installed")
def test_spectral_conv_autograd_integrity():
    """Verify SpectralConv1d propagates gradients through complex Fourier weights."""
    layer = SpectralConv1d(in_channels=3, out_channels=4, modes=4)
    raw_in = torch.rand(2, 3, 16, requires_grad=True)
    v_in = PnnTensor(raw_in, unit=u.MeterPerSecond)

    v_out = layer(v_in)
    assert v_out.unit.dimension == "speed"
    assert v_out.shape == (2, 4, 16)

    loss = v_out.mag.sum()
    loss.backward()

    assert raw_in.grad is not None
    assert layer.weights_complex.grad is not None


@pytest.mark.skipif(not HAS_TORCH, reason="PyTorch not installed")
def test_fno_end_to_end_training():
    """Verify a mini FNO architecture learns (loss decreases) over 5 epochs."""
    class MiniWaveFNO(nn.Module):
        def __init__(self):
            super().__init__()
            self.lift = nn.Linear(1, 8)
            self.fourier = SpectralConv1d(in_channels=8, out_channels=8, modes=4)
            self.bypass = nn.Conv1d(8, 8, kernel_size=1)
            self.proj = nn.Linear(8, 1)

        def forward(self, u0_pt):
            x = self.lift(u0_pt.mag)
            x = x.permute(0, 2, 1)
            x_pt = PnnTensor(x, unit=u0_pt.unit)
            x_spectral_pt = self.fourier(x_pt)
            x_bypass = self.bypass(x_pt.mag)
            x = F.gelu(x_spectral_pt.mag + x_bypass)
            x = x.permute(0, 2, 1)
            u_out = self.proj(x)
            return PnnTensor(u_out, unit=u0_pt.unit)

    model = MiniWaveFNO()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

    grid_size = 32
    u_in = PnnTensor(
        torch.sin(torch.linspace(0, 2 * torch.pi, grid_size)).view(1, grid_size, 1),
        unit=u.MeterPerSecond,
    )
    u_target = PnnTensor(
        torch.cos(torch.linspace(0, 2 * torch.pi, grid_size)).view(1, grid_size, 1),
        unit=u.MeterPerSecond,
    )

    loss_history = []
    for _ in range(5):
        optimizer.zero_grad()
        u_pred = model(u_in)
        assert u_pred.unit.dimension == "speed"
        loss = F.mse_loss(u_pred.mag, u_target.mag)
        loss.backward()
        optimizer.step()
        loss_history.append(loss.item())

    assert loss_history[-1] < loss_history[0], "FNO failed to learn: loss did not decrease"
    assert not torch.isnan(torch.tensor(loss_history)).any(), "NaN detected in loss history"