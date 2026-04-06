"""
Physics-Aware Tensor Operations.
Safely concatenates, stacks, and assembles tensors while strictly 
enforcing dimensional homogeneity and auto-scaling.
"""
from __future__ import annotations
from typing import Sequence, Any, TYPE_CHECKING, overload

from ..compat import HAS_TORCH
from .tensor import PTensor

if TYPE_CHECKING:
    import torch
    import torch.fft as tfft
    from ..compat import _UnitT_co 
elif HAS_TORCH:
    import torch
    import torch.fft as tfft

def _align_tensors(tensors: Sequence[PTensor | torch.Tensor], op_name: str) -> tuple[list[torch.Tensor], Any]:
    for t in tensors:
        if isinstance(t, PTensor) and getattr(t, 'unit', None) is not None:
            ref_u = t.unit
            break

    if ref_u is None:
        return [t.mag if isinstance(t, PTensor) else t for t in tensors], None

    ref_dim = getattr(ref_u, 'dimension', None)
    ref_mult = float(getattr(ref_u, 'base_multiplier', 1.0))
    ref_off = float(getattr(ref_u, 'base_offset', 0.0))

    def _d_str(u_cls: Any) -> str:
        d = getattr(u_cls, 'dimension', 'unknown')
        if d == 'anonymous':
            sym = getattr(u_cls, 'symbol', '???')
            return f"Unregistered DNA [{sym}]"
        return d
    
    mags = []
    for i, t in enumerate(tensors):
        if isinstance(t, PTensor):
            t_dim = getattr(t.unit, 'dimension', None)
            if t_dim != ref_dim:
                from ...exceptions import DimensionMismatchError
                raise DimensionMismatchError(
                    _d_str(ref_u), 
                    _d_str(t.unit), 
                    f"pnn.{op_name} at index {i}"
                )

            if t.unit != ref_u:
                t_mult = float(getattr(t.unit, 'base_multiplier', 1.0))
                t_off = float(getattr(t.unit, 'base_offset', 0.0))
                base_val = (t.mag * t_mult) + t_off
                aligned_val = (base_val - ref_off) / ref_mult
                mags.append(aligned_val)
            else:
                mags.append(t.mag)
        else:
            mags.append(t)

    return mags, ref_u
if TYPE_CHECKING:
    @overload
    def cat(tensors: Sequence[PTensor[_UnitT_co]], dim: int = ...) -> PTensor[_UnitT_co]: ...
    @overload
    def cat(tensors: Sequence[torch.Tensor], dim: int = ...) -> torch.Tensor: ...

def cat(tensors: Sequence[PTensor[Any] | torch.Tensor], dim: int = 0) -> PTensor[Any] | torch.Tensor:
    """
    Concatenates a sequence of physical tensors along an existing dimension.
    
    This operation strictly enforces dimensional homogeneity. If the input tensors 
    possess differing units of the same dimension (e.g., Meters and Kilometers), 
    the engine automatically performs a JIT scaling transformation to align all 
    elements with the unit of the first tensor in the sequence.

    Args:
        tensors: A sequence of Phaethon or PyTorch tensors to join.
        dim: The dimension along which the tensors will be concatenated.

    Returns:
        A concatenated tensor preserving physical dimensionality.
        
    Raises:
        DimensionMismatchError: If any tensor in the sequence belongs to an 
            incompatible physical dimension.
    """
    if not HAS_TORCH: raise ImportError("PyTorch required.")
    mags, ref_u = _align_tensors(tensors, "cat")
    res = torch.cat(mags, dim=dim)
    return PTensor(res, unit=ref_u) if ref_u else res

if TYPE_CHECKING:
    @overload
    def stack(tensors: Sequence[PTensor[_UnitT_co]], dim: int = ...) -> PTensor[_UnitT_co]: ...
    @overload
    def stack(tensors: Sequence[torch.Tensor], dim: int = ...) -> torch.Tensor: ...

def stack(tensors: Sequence[PTensor[Any] | torch.Tensor], dim: int = 0) -> PTensor[Any] | torch.Tensor:
    """
    Stacks a sequence of physical tensors along a new dimension.
    
    Like concatenation, stacking strictly enforces dimensional homogeneity and 
    triggers automated scaling if units within the sequence differ (e.g., stacking 
    Celsius and Kelvin). The resulting tensor adopts the unit of the first 
    element in the sequence.

    Args:
        tensors: A sequence of Phaethon or PyTorch tensors to stack.
        dim: The new dimension index where the stacking will occur.

    Returns:
        A stacked tensor with a new dimension, preserving physical dimensionality.
        
    Raises:
        DimensionMismatchError: If any tensor in the sequence belongs to an 
            incompatible physical dimension.
    """
    if not HAS_TORCH: raise ImportError("PyTorch required.")
    mags, ref_u = _align_tensors(tensors, "stack")
    res = torch.stack(mags, dim=dim)
    return PTensor(res, unit=ref_u) if ref_u else res

def assemble(*tensors: PTensor[Any] | torch.Tensor, dim: int = -1) -> torch.Tensor:
    """
    Strips physical metadata and concatenates heterogeneous tensors for model ingestion.
    
    This is the designated gateway for feeding mixed physical data (e.g., velocity, 
    pressure, and time) into standard neural network architectures that do not 
    support dimensional units.

    Args:
        *tensors: Variadic physical tensors to be assembled.
        dim: The dimension along which to concatenate.

    Returns:
        A raw PyTorch tensor stripped of all Phaethon metadata.
    """
    if not HAS_TORCH: raise ImportError("PyTorch required.")
    mags = [t.mag if isinstance(t, PTensor) else t for t in tensors]
    return torch.cat(mags, dim=dim)

def fft(tensor: PTensor[Any] | torch.Tensor, dim: int = -1) -> PTensor[Any] | torch.Tensor:
    """
    Transforms a physical tensor from the Spatial/Temporal domain to the Frequency domain.
    
    Utilizes Real Fast Fourier Transform (RFFT) while simultaneously performing a 
    dimensional inversion on the unit metadata (e.g., Time [T] is automatically 
    transformed into Frequency [T^-1]).

    Args:
        tensor: The input tensor in the physical domain.
        dim: The dimension along which to take the FFT.

    Returns:
        A complex-valued tensor in the spectral domain with inverted units.
    """
    if not HAS_TORCH: raise ImportError("PyTorch required.")
    if not isinstance(tensor, PTensor):
        return tfft.rfft(tensor, dim=dim)
    
    freq_mag = tfft.rfft(tensor.mag, dim=dim)
    
    derived_unit = tensor.unit ** -1
    return PTensor(freq_mag, unit=derived_unit)

def ifft(tensor: PTensor[Any] | torch.Tensor, dim: int = -1, n: int | None = None) -> PTensor[Any] | torch.Tensor:
    """
    Transforms a spectral tensor back to the Spatial/Temporal physical domain.
    
    Executes an Inverse Real Fast Fourier Transform (IRFFT) and automatically 
    re-inverts the physical units (e.g., Frequency [T^-1] returns to Time [T]). 
    This is essential for interpreting Neural Operator outputs in real-world units.

    Args:
        tensor: The complex-valued spectral tensor to be inverted.
        dim: The dimension along which to take the Inverse FFT.
        n: The output length of the transformed physical dimension.

    Returns:
        A real-valued tensor restored to its original physical domain.
    """
    if not HAS_TORCH: raise ImportError("PyTorch required.")
    if not isinstance(tensor, PTensor):
        return tfft.irfft(tensor, n=n, dim=dim)
    
    spatial_mag = tfft.irfft(tensor.mag, n=n, dim=dim)
    
    derived_unit = tensor.unit ** -1
    return PTensor(spatial_mag, unit=derived_unit)