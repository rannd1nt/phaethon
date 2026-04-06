"""
Phaethon Physics-Informed Neural Networks (PINNs) Module.

A high-level differentiable physics engine powered by PyTorch that enables the training 
of neural networks under physical constraints, featuring specialized layers for spectral 
operators, automated dimensional group extraction, and native physical calculus for 
solving complex differential equations.

Dependency Note:
        Requires PyTorch.
        Install via: `pip install 'phaethon[torch]'` or `pip install 'phaethon[sciml]'`
"""
from __future__ import annotations
from typing import TYPE_CHECKING as _TCHECK, Any

__all__ = [
    "PTensor", "BuckinghamPi", "SpectralConv1d", "AxiomLoss", 
    "ResidualLoss", "grad", "laplace", "div", "curl", 
    "cat", "stack", "assemble", "fft", "ifft"
]

if _TCHECK:
    from .core.pinns.tensor import PTensor as PTensor
    from .core.pinns.pi_theorem import BuckinghamPi as BuckinghamPi
    from .core.pinns.layers import SpectralConv1d as SpectralConv1d
    from .core.pinns.loss import AxiomLoss as AxiomLoss, ResidualLoss as ResidualLoss
    from .core.pinns.calculus import grad as grad, laplace as laplace, div as div, curl as curl
    from .core.pinns.ops import cat as cat, stack as stack, assemble as assemble, fft as fft, ifft as ifft

from .core.compat import HAS_TORCH as _HAS_TORCH, require_torch as _reqtorch

if _HAS_TORCH:
    from .core.pinns.tensor import PTensor
    from .core.pinns.pi_theorem import BuckinghamPi
    from .core.pinns.layers import SpectralConv1d
    from .core.pinns.loss import AxiomLoss, ResidualLoss
    from .core.pinns.calculus import grad, laplace, div, curl
    from .core.pinns.ops import cat, stack, assemble, fft, ifft
    

else:
    __all__ = []
    def __getattr__(name: str) -> Any:
        _reqtorch(f"Accessing '{name}'")
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")