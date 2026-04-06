"""
Phaethon Tensor Creation Module.
Provides physics-aware wrappers around NumPy's core array creation routines.
"""
from __future__ import annotations

from typing import Any, overload
from .compat import UnitLike, HAS_NUMPY, _UnitT
from .registry import ureg
from .base import BaseUnit

if HAS_NUMPY:
    import numpy as np

def _resolve_unit(unit: UnitLike) -> type[BaseUnit]:
    """Internal helper to safely resolve strings or classes into a BaseUnit class."""
    if isinstance(unit, str):
        return ureg().get_unit_class(unit)
    if isinstance(unit, type) and issubclass(unit, BaseUnit):
        return unit
    raise TypeError(f"The 'unit' argument must be a string alias or a BaseUnit class, got {type(unit).__name__}")


@overload
def array(object: Any, unit: type[_UnitT], dtype: Any = None, *, copy: bool = True, order: str = 'K', subok: bool = False, ndmin: int = 0) -> _UnitT: ...

@overload
def array(object: Any, unit: str, dtype: Any = None, *, copy: bool = True, order: str = 'K', subok: bool = False, ndmin: int = 0) -> BaseUnit: ...

def array(object: Any, unit: UnitLike, dtype: Any = None, *, copy: bool = True, order: str = 'K', subok: bool = False, ndmin: int = 0) -> BaseUnit:
    """
    Creates a physics-aware array.
    
    This function wraps `numpy.array`, meaning it constructs an array from the 
    given object and attaches the specified physical dimensional DNA.

    Args:
        object: An array, any object exposing the array interface, an object whose 
            __array__ method returns an array, or any (nested) sequence.
        unit: The physical dimension to attach. Can be a string alias (e.g., 'kg', 'm/s') 
            or a Phaethon BaseUnit class (e.g., u.Kilogram).
        dtype: The desired data-type for the array.
        copy: If true (default), then the object is copied.
        order: Specify the memory layout of the array ('C', 'F', 'A', 'K').
        subok: If True, then sub-classes will be passed-through.
        ndmin: Specifies the minimum number of dimensions that the resulting array should have.

    Returns:
        A Phaethon BaseUnit tensor wrapping the constructed array.
    """
    UnitClass = _resolve_unit(unit)
    
    if HAS_NUMPY:
        arr = np.array(object, dtype=dtype, copy=copy, order=order, subok=subok, ndmin=ndmin)
        return UnitClass(arr)
        
    return UnitClass(object)


@overload
def asarray(a: Any, unit: type[_UnitT], dtype: Any = None, order: str | None = None) -> _UnitT: ...

@overload
def asarray(a: Any, unit: str, dtype: Any = None, order: str | None = None) -> BaseUnit: ...

def asarray(a: Any, unit: UnitLike, dtype: Any = None, order: str | None = None) -> BaseUnit:
    """
    Converts the input to an array without copying if possible, attaching physics.
    
    This is a physics-aware wrapper for `numpy.asarray`. It is useful when you want 
    to ensure the input is a physical array but want to avoid unnecessary memory 
    duplication if the input is already a compatible ndarray.

    Args:
        a: Input data, in any form that can be converted to an array.
        unit: The physical dimension to attach.
        dtype: The desired data-type for the array.
        order: Specify the memory layout of the array.

    Returns:
        A Phaethon BaseUnit tensor wrapping the zero-copied array (if compatible).
    """
    UnitClass = _resolve_unit(unit)
    
    if HAS_NUMPY:
        arr = np.asarray(a, dtype=dtype, order=order)
        return UnitClass(arr)
        
    return UnitClass(a)


@overload
def asanyarray(a: Any, unit: type[_UnitT], dtype: Any = None, order: str | None = None) -> _UnitT: ...

@overload
def asanyarray(a: Any, unit: str, dtype: Any = None, order: str | None = None) -> BaseUnit: ...

def asanyarray(a: Any, unit: UnitLike, dtype: Any = None, order: str | None = None) -> BaseUnit:
    """
    Converts the input to an ndarray, but passes ndarray subclasses through.
    
    This is a physics-aware wrapper for `numpy.asanyarray`. Similar to `asarray`, 
    but it allows subclasses of ndarray (like matrix or masked arrays) to pass 
    through without forcing them to be base ndarrays.

    Args:
        a: Input data.
        unit: The physical dimension to attach.
        dtype: The desired data-type for the array.
        order: Specify the memory layout of the array.

    Returns:
        A Phaethon BaseUnit tensor wrapping the array or array subclass.
    """
    UnitClass = _resolve_unit(unit)
    
    if HAS_NUMPY:
        arr = np.asanyarray(a, dtype=dtype, order=order)
        return UnitClass(arr)
        
    return UnitClass(a)