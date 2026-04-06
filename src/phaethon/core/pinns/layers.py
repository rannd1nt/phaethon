"""
Physics-Aware Neural Network Layers (Neural Operators).
"""
from __future__ import annotations
from typing import TYPE_CHECKING, Any, overload

from ..compat import HAS_TORCH
from .tensor import PTensor

if TYPE_CHECKING:
    import torch
    import torch.nn as nn
    from .ops import fft, ifft
    from ..compat import _UnitT_co
    _BaseModule = nn.Module
elif HAS_TORCH:
    import torch
    import torch.nn as nn
    from .ops import fft, ifft
    _BaseModule = nn.Module
else:
    _BaseModule = object

class SpectralConv1d(_BaseModule):
    """
    1D Fourier Layer (Spectral Convolution).
    The core building block of Fourier Neural Operators (FNO).
    
    This layer transforms physical data into the frequency domain, 
    applies a learned complex linear transformation to the lower frequency modes, 
    and transforms it back to the physical spatial domain.

    Args:
        in_channels (int): Number of input features/channels.
        out_channels (int): Number of output features/channels.
        modes (int): Number of low-frequency Fourier modes to keep.
                        Higher modes are truncated (Low-pass filter).
    """
    __module__ = "phaethon.pinns"

    def __init__(self, in_channels: int, out_channels: int, modes: int) -> None:
        """
        1D Fourier Layer (Spectral Convolution).
        The core building block of Fourier Neural Operators (FNO).
        
        This layer transforms physical data into the frequency domain, 
        applies a learned complex linear transformation to the lower frequency modes, 
        and transforms it back to the physical spatial domain.

        Args:
            in_channels: Number of input features/channels.
            out_channels: Number of output features/channels.
            modes: Number of low-frequency Fourier modes to keep.
                         Higher modes are truncated (Low-pass filter).
        """
        if not HAS_TORCH: raise ImportError("PyTorch is required for SpectralConv1d.")
        super().__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.modes = modes

        scale = (1 / (in_channels * out_channels))
        self.weights_complex = nn.Parameter(
            scale * torch.rand(in_channels, out_channels, self.modes, dtype=torch.cfloat)
        )

    if TYPE_CHECKING:
        @overload
        def __call__(self, x: PTensor[_UnitT_co]) -> PTensor[_UnitT_co]: ...
        @overload
        def __call__(self, x: torch.Tensor) -> torch.Tensor: ...
        
        @overload
        def forward(self, x: PTensor[_UnitT_co]) -> PTensor[_UnitT_co]: ...
        @overload
        def forward(self, x: torch.Tensor) -> torch.Tensor: ...
    
    def _complex_matmul_1d(self, input_ft: torch.Tensor, weights: torch.Tensor) -> torch.Tensor:
        return torch.einsum("bix,iox->box", input_ft, weights)

    def forward(self, x: PTensor[Any] | torch.Tensor) -> PTensor[Any] | torch.Tensor:
        """
        Executes the Spectral Convolution while preserving dimensional integrity.

        Args:
            x: Input physical tensor representing the spatial field.

        Returns:
            The convolved field in the original physical spatial domain.
        """
        x_ft = fft(x, dim=-1)
        
        batch_size = x_ft.mag.shape[0] if isinstance(x_ft, PTensor) else x_ft.shape[0]
        grid_points = x_ft.mag.shape[-1] if isinstance(x_ft, PTensor) else x_ft.shape[-1]
        
        out_ft_mag = torch.zeros(batch_size, self.out_channels, grid_points, 
                                 dtype=torch.cfloat, device=self.weights_complex.device)

        mag_to_process = x_ft.mag if isinstance(x_ft, PTensor) else x_ft
        out_ft_mag[:, :, :self.modes] = self._complex_matmul_1d(
            mag_to_process[:, :, :self.modes], self.weights_complex
        )

        if isinstance(x, PTensor):
            out_ft_pt = PTensor(out_ft_mag, unit=x_ft.unit)
        else:
            out_ft_pt = out_ft_mag

        x_spatial = ifft(out_ft_pt, dim=-1, n=x.shape[-1] if isinstance(x, PTensor) else x.shape[-1])
        
        return x_spatial