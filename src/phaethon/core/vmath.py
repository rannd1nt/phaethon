"""
Vectorized Math Wrapper for Phaethon Axioms.

Polymorphically routes mathematical operations to NumPy (if handling arrays) 
or the standard Python `math` library/builtins (if handling scalar floats/Decimals).
This ensures custom Axiom physics formulas remain type-agnostic and clean.
"""
from __future__ import annotations

import math as std_math
import builtins
from typing import Any

from .compat import NumericLike, _NumericT

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

pi: float = std_math.pi
e: float = std_math.e

def _is_array(val: Any) -> bool:
    """Internal helper to determine if a value is a NumPy array/vector."""
    return HAS_NUMPY and isinstance(val, (np.ndarray, np.generic))

def sqrt(val: _NumericT) -> _NumericT:
    """
    Return the non-negative square root of the value.
    
    Args:
        val: A scalar numeric value or a NumPy array.
    Returns:
        The square root of the input. Type matches the input (scalar or array).
    """
    return np.sqrt(val) if _is_array(val) else std_math.sqrt(float(val)) # type: ignore

def max(val: _NumericT, limit: _NumericT) -> _NumericT:
    """
    Element-wise maximum of array elements or scalar values.
    
    Args:
        val: The primary value or array.
        limit: The lower limit threshold to enforce.
    Returns:
        The maximum value between `val` and `limit`.
    """
    return np.maximum(val, limit) if _is_array(val) else builtins.max(val, limit) # type: ignore

def min(val: _NumericT, limit: _NumericT) -> _NumericT:
    """
    Element-wise minimum of array elements or scalar values.
    
    Args:
        val: The primary value or array.
        limit: The upper limit threshold to enforce.
    Returns:
        The minimum value between `val` and `limit`.
    """
    return np.minimum(val, limit) if _is_array(val) else builtins.min(val, limit) # type: ignore

def exp(val: _NumericT) -> _NumericT:
    """
    Calculate the exponential of all elements in the input array or scalar.
    
    Args:
        val: Input value.
    Returns:
        Element-wise exponential (e^val).
    """
    return np.exp(val) if _is_array(val) else std_math.exp(float(val)) # type: ignore

def log(val: _NumericT) -> _NumericT:
    """
    Return the natural logarithm (base e) of the value.
    
    Args:
        val: Input value (must be > 0).
    Returns:
        Natural logarithm of the input.
    """
    return np.log(val) if _is_array(val) else std_math.log(float(val)) # type: ignore

def cos(val: _NumericT) -> _NumericT:
    """
    Return the cosine of the input value (measured in radians).
    """
    return np.cos(val) if _is_array(val) else std_math.cos(float(val)) # type: ignore

def sin(val: _NumericT) -> _NumericT:
    """
    Return the sine of the input value (measured in radians).
    """
    return np.sin(val) if _is_array(val) else std_math.sin(float(val)) # type: ignore

def tan(val: _NumericT) -> _NumericT:
    """
    Return the tangent of the input value (measured in radians).
    """
    return np.tan(val) if _is_array(val) else std_math.tan(float(val)) # type: ignore

def pow(val: _NumericT, exponent: int | float | NumericLike) -> _NumericT:
    """
    First array/scalar elements raised to powers from second array/scalar.
    
    Args:
        val: The base value(s).
        exponent: The exponent value(s).
    Returns:
        val raised to the power of exponent.
    """
    return np.power(val, exponent) if _is_array(val) else builtins.pow(val, exponent) # type: ignore

def abs(val: _NumericT) -> _NumericT:
    """
    Calculate the absolute value element-wise.
    
    Args:
        val: Input array or scalar.
    Returns:
        An array/scalar containing the absolute value of each element.
    """
    return np.abs(val) if _is_array(val) else builtins.abs(val) # type: ignore