"""
Random Physics Module.
Generates stochastic tensors strictly bounded by physical dimensions.
"""
from __future__ import annotations
from typing import Any, overload

from .compat import UnitLike, HAS_NUMPY, _UnitT
from .registry import ureg
from .base import BaseUnit

if HAS_NUMPY:
    import numpy as np

def _resolve_unit(unit: UnitLike) -> type[BaseUnit]:
    if isinstance(unit, str):
        return ureg().get_unit_class(unit)
    if isinstance(unit, type) and issubclass(unit, BaseUnit):
        return unit
    raise TypeError(f"The 'unit' argument must be a string alias or a BaseUnit class.")

# =========================================================================
# ptn.random.uniform()
# =========================================================================
@overload
def uniform(low: float = ..., high: float = ..., size: Any = ..., unit: type[_UnitT] = ...) -> _UnitT: ...
@overload
def uniform(low: float = ..., high: float = ..., size: Any = ..., unit: str = ...) -> BaseUnit: ...

def uniform(low: float = 0.0, high: float = 1.0, size: Any = None, unit: UnitLike | None = None) -> BaseUnit:
    """
    Draws samples from a uniform distribution and injects physical DNA.
    
    Args:
        low: Lower boundary of the output interval.
        high: Upper boundary of the output interval.
        size: Output shape (e.g., (2, 3)).
        unit: The physical dimension to attach (Class or alias string).
        
    Returns:
        A BaseUnit tensor containing uniformly distributed physical values.
    """
    if not HAS_NUMPY: raise ImportError("NumPy is required.")
    if unit is None: raise ValueError("A physical unit must be specified.")
        
    raw_arr = np.random.uniform(low, high, size)
    UnitClass = _resolve_unit(unit)
    return UnitClass(raw_arr)

# =========================================================================
# ptn.random.normal()
# =========================================================================
@overload
def normal(loc: float = ..., scale: float = ..., size: Any = ..., unit: type[_UnitT] = ...) -> _UnitT: ...
@overload
def normal(loc: float = ..., scale: float = ..., size: Any = ..., unit: str = ...) -> BaseUnit: ...

def normal(loc: float = 0.0, scale: float = 1.0, size: Any = None, unit: UnitLike | None = None) -> BaseUnit:
    """
    Draws random samples from a normal (Gaussian) distribution.
    
    Args:
        loc: Mean ("centre") of the distribution.
        scale: Standard deviation (spread or "width").
        size: Output shape.
        unit: The physical dimension to attach.
    """
    if not HAS_NUMPY: raise ImportError("NumPy is required.")
    if unit is None: raise ValueError("A physical unit must be specified.")
        
    raw_arr = np.random.normal(loc, scale, size)
    UnitClass = _resolve_unit(unit)
    return UnitClass(raw_arr)

@overload
def poisson(lam: float = ..., size: Any = ..., unit: type[_UnitT] = ...) -> _UnitT: ...
@overload
def poisson(lam: float = ..., size: Any = ..., unit: str = ...) -> BaseUnit: ...

def poisson(lam: float = 1.0, size: Any = None, unit: UnitLike | None = None) -> BaseUnit:
    """
    Draws samples from a Poisson distribution.
    
    Extremely useful in Phaethon for modeling discrete physical events over 
    a continuous interval, such as radioactive decays (u.Becquerel) or 
    photon strikes (u.Photon).
    
    Args:
        lam: Expected number of events occurring in a fixed-time interval.
        size: Output shape.
        unit: The physical dimension to attach.
    """
    if not HAS_NUMPY: raise ImportError("NumPy is required.")
    if unit is None: raise ValueError("A physical unit must be specified.")
        
    raw_arr = np.random.poisson(lam, size)
    UnitClass = _resolve_unit(unit)
    return UnitClass(raw_arr)

@overload
def exponential(scale: float = ..., size: Any = ..., unit: type[_UnitT] = ...) -> _UnitT: ...
@overload
def exponential(scale: float = ..., size: Any = ..., unit: str = ...) -> BaseUnit: ...

def exponential(scale: float = 1.0, size: Any = None, unit: UnitLike | None = None) -> BaseUnit:
    """
    Draws samples from an exponential distribution.
    
    Ideal for simulating the time between independent physics events, 
    such as the decay time of radioactive isotopes or thermodynamic 
    relaxation times.
    
    Args:
        scale: The scale parameter, \u03b2 = 1/\u03bb. Must be non-negative.
        size: Output shape.
        unit: The physical dimension to attach (typically u.Second).
    """
    if not HAS_NUMPY: raise ImportError("NumPy is required.")
    if unit is None: raise ValueError("A physical unit must be specified.")
        
    raw_arr = np.random.exponential(scale, size)
    UnitClass = _resolve_unit(unit)
    return UnitClass(raw_arr)