"""
Phaethon Linear Algebra Module.
Physics-aware wrappers around numpy.linalg operations.
"""
from __future__ import annotations
from typing import Any, overload

from .compat import HAS_NUMPY, _UnitT
from .base import BaseUnit

if HAS_NUMPY:
    import numpy as np

def inv(a: _UnitT) -> BaseUnit:
    """
    Computes the (multiplicative) inverse of a physical matrix.
    
    In dimensional algebra, the inverse of a matrix A with dimension [D] 
    results in a matrix with dimension [1/D].
    
    Args:
        a: A square physical tensor (BaseUnit).
        
    Returns:
        A BaseUnit tensor representing the inverse matrix with inverted dimensions.
        
    Raises:
        LinAlgError: If the matrix is not square or is singular.
    """
    if not HAS_NUMPY:
        raise ImportError("NumPy is required for phaethon.linalg operations.")
    if not isinstance(a, BaseUnit):
        raise TypeError("Input must be a Phaethon BaseUnit.")
        
    raw_inv = np.linalg.inv(a.mag)
    
    ResultClass = 1 / a.__class__
    merged_context = {**a.context, "__is_math_op__": True}
    return ResultClass(raw_inv, context=merged_context)


def det(a: _UnitT) -> BaseUnit:
    """
    Computes the determinant of a physical matrix.
    
    The determinant of an N x N matrix with dimension [D] 
    synthesizes a new physical dimension of [D^N]. 
    For example, the determinant of a 2x2 Meter matrix is an Area (Meter^2).
    
    Args:
        a: A square physical tensor (BaseUnit).
        
    Returns:
        A scalar BaseUnit representing the determinant with exponentiated dimensions.
    """
    if not HAS_NUMPY:
        raise ImportError("NumPy is required for phaethon.linalg operations.")
    if not isinstance(a, BaseUnit):
        raise TypeError("Input must be a Phaethon BaseUnit.")
        
    raw_det = np.linalg.det(a.mag)
    n = a.shape[-1]
    
    _dummy_scalar = a.__class__(1.0, context=a.context) ** n
    ResultClass = _dummy_scalar.__class__
    merged_context = {**a.context, "__is_math_op__": True}
    return ResultClass(raw_det, context=merged_context)

def solve(a: BaseUnit, b: BaseUnit | Any) -> BaseUnit:
    """
    Solves a linear matrix equation, or system of linear scalar equations (Ax = B).
    
    In physics, if A * x = B, then the dimension of the solution x 
    must exactly equal the dimension of B divided by the dimension of A.
    
    Args:
        a: Coefficient physical matrix (N, N).
        b: Ordinate or "dependent variable" physical values (N,) or (N, K).
        
    Returns:
        A physical tensor 'x' satisfying the equation Ax = B.
    """
    if not HAS_NUMPY:
        raise ImportError("NumPy is required for phaethon.linalg operations.")
        
    a_mag = a.mag if isinstance(a, BaseUnit) else a
    b_mag = b.mag if isinstance(b, BaseUnit) else b
    
    raw_solve = np.linalg.solve(a_mag, b_mag)
    
    if isinstance(a, BaseUnit) and isinstance(b, BaseUnit):
        ResultClass = b.__class__ / a.__class__
        merged_context = {**a.context, **b.context, "__is_math_op__": True}
    elif isinstance(a, BaseUnit):
        ResultClass = 1 / a.__class__
        merged_context = {**a.context, "__is_math_op__": True}
    else:
        ResultClass = b.__class__
        merged_context = {**b.context, "__is_math_op__": True}
        
    if getattr(ResultClass, 'dimension', None) == 'dimensionless':
        from .units.scalar import Dimensionless
        return Dimensionless(raw_solve, context=merged_context)
        
    return ResultClass(raw_solve, context=merged_context)


def norm(x: _UnitT, ord: Any = None, axis: Any = None, keepdims: bool = False) -> _UnitT:
    """
    Matrix or vector norm.
    
    Unlike determinants or inverses, the norm of a physical vector (like velocity 
    or force) calculates its magnitude. Therefore, the physical dimension 
    remains completely unaltered.
    
    Args:
        x: Input physical tensor.
        ord: Order of the norm (see numpy.linalg.norm for details).
        axis: Axis or axes along which to compute the vector norms.
        keepdims: If this is set to True, the axes which are normed are left in the result.
        
    Returns:
        The magnitude of the physical vector/matrix, preserving the original dimension.
    """
    if not HAS_NUMPY:
        raise ImportError("NumPy is required for phaethon.linalg operations.")
    if not isinstance(x, BaseUnit):
        raise TypeError("Input must be a Phaethon BaseUnit.")
        
    raw_norm = np.linalg.norm(x.mag, ord=ord, axis=axis, keepdims=keepdims)
    merged_context = {**x.context, "__is_math_op__": True}
    
    return x.__class__(raw_norm, context=merged_context)