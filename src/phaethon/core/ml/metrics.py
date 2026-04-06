"""
Physics-Aware Evaluation Metrics for Scikit-Learn.
"""
from __future__ import annotations
from typing import Any, Literal, overload
from ..compat import NumericLike, _UnitT

from ...exceptions import PhysicalAlgebraError
from ..base import BaseUnit
from ..compat import HAS_NUMPY, HAS_SKLEARN

if HAS_SKLEARN:
    if HAS_NUMPY:
        import numpy as np
    from sklearn.metrics import (
        mean_squared_error as sk_mse,
        mean_absolute_error as sk_mae,
        r2_score as sk_r2
    )
else:
    def sk_mse(*args: Any, **kwargs: Any) -> Any: pass
    def sk_mae(*args: Any, **kwargs: Any) -> Any: pass
    def sk_r2(*args: Any, **kwargs: Any) -> Any: pass

def _extract_and_validate(y_true: Any, y_pred: Any) -> tuple[Any, Any, type[BaseUnit] | None]:
    """
    Mengekstrak unit, memastikan keduanya sejalan, dan melucuti jubahnya.
    """
    def get_unit(data: Any) -> type[BaseUnit] | None:
        if isinstance(data, BaseUnit): return data.__class__
        if HAS_NUMPY and isinstance(data, np.ndarray) and data.dtype == object:
            if len(data) > 0 and isinstance(data[0], BaseUnit): return data[0].__class__
        return None

    def strip(data: Any) -> Any:
        if isinstance(data, BaseUnit): return data.mag
        if hasattr(data, 'to_numpy'):
            arr = data.to_numpy()
            if arr.dtype == object and len(arr) > 0 and isinstance(arr[0], BaseUnit):
                return np.array([item.mag for item in arr], dtype=float)
            return arr
        return data

    u_true = get_unit(y_true)
    u_pred = get_unit(y_pred)

    if u_true and u_pred:
        if getattr(u_true, 'dimension', None) != getattr(u_pred, 'dimension', None):
            raise PhysicalAlgebraError(
                "Metric Evaluation (y_true vs y_pred)",
                _fmtdim(u_true),
                _fmtdim(u_pred)
            )
            
    return strip(y_true), strip(y_pred), (u_true or u_pred)

def _fmtdim(u_cls: Any) -> str:
    if u_cls is None: return "unknown"
    dim = getattr(u_cls, 'dimension', 'unknown')
    if dim == 'anonymous':
        sym = getattr(u_cls, 'symbol', '???')
        return f"Unregistered DNA [{sym}]"
    sym = getattr(u_cls, 'symbol', '')
    sym_str = f" [{sym}]" if sym else ""
    return f"{dim}{sym_str}"

# =========================================================================
# PUBLIC METRICS API
# =========================================================================

@overload
def physics_mean_absolute_error(y_true: _UnitT, y_pred: Any, **kwargs: Any) -> _UnitT: ...
@overload
def physics_mean_absolute_error(y_true: NumericLike, y_pred: Any, **kwargs: Any) -> float: ...

def physics_mean_absolute_error(y_true: Any, y_pred: Any, **kwargs: Any) -> BaseUnit | float:
    """
    Calculates the mean absolute error (MAE) while preserving physical dimensions.
    
    Unlike standard metrics that return raw floats, this function ensures that 
    the error metric retains the exact physical unit of the target variables.

    Args:
        y_true: Ground truth (correct) target values. Should be a Phaethon BaseUnit.
        y_pred: Estimated target values as returned by a classifier/regressor.
        **kwargs: Additional arguments passed to sklearn.metrics.mean_absolute_error.

    Returns:
        A Phaethon BaseUnit instance representing the absolute error.

    Raises:
        DimensionMismatchError: If y_true and y_pred have incompatible dimensions.

    Examples:
        >>> import phaethon.ml as pml
        >>> import phaethon.units as u
        >>> y_true = u.Kelvin([300.0, 310.0])
        >>> y_pred = u.Kelvin([305.0, 310.0])
        >>> error = pml.physics_mean_absolute_error(y_true, y_pred)
        >>> print(error.dimension)
        'temperature'
    """
    if not HAS_SKLEARN: raise ImportError("Scikit-Learn required.")
    
    y_t_raw, y_p_raw, target_unit = _extract_and_validate(y_true, y_pred)
    error_val = sk_mae(y_t_raw, y_p_raw, **kwargs)
    
    if target_unit:
        return target_unit(error_val)
    return error_val

@overload
def physics_mean_squared_error(y_true: _UnitT, y_pred: Any, squared: Literal[False], **kwargs: Any) -> _UnitT: ...
@overload
def physics_mean_squared_error(y_true: _UnitT, y_pred: Any, squared: Literal[True] = ..., **kwargs: Any) -> BaseUnit: ...
@overload
def physics_mean_squared_error(y_true: NumericLike, y_pred: Any, squared: bool = ..., **kwargs: Any) -> float: ...

def physics_mean_squared_error(y_true: Any, y_pred: Any, squared: bool = True, **kwargs: Any) -> BaseUnit | float:
    """
    Evaluates the mean squared error (MSE) while strictly adhering to dimensional algebra.

    Unlike standard evaluation metrics, this function synthesizes the mathematically 
    correct dimensional output. If calculating MSE, the physical dimension of the error 
    is dynamically squared (e.g., Distance yields Area). If calculating Root Mean Squared 
    Error (RMSE), the original dimension is perfectly preserved.

    Args:
        y_true: The ground truth target values. Should be a Phaethon BaseUnit instance.
        y_pred: The predicted target values.
        squared: If True, returns MSE (synthesizes squared dimensions). 
            If False, returns RMSE (preserves original dimensions). Defaults to True.
        **kwargs: Additional parameters passed to the underlying evaluation engine.

    Raises:
        DimensionMismatchError: If the ground truth and predicted values belong to 
            incompatible physical dimensions.

    Returns:
        A dynamically synthesized Phaethon BaseUnit representing the physical error.

    Examples:
        >>> import phaethon.ml as pnn
        >>> import phaethon.units as u
        >>> y_true = u.Meter([10.0, 20.0])
        >>> y_pred = u.Meter([12.0, 18.0])
        >>> mse = pnn.physics_mean_squared_error(y_true, y_pred, squared=True)
        >>> print(mse.dimension)
        'area'  # Meter squared dynamically becomes Area
    """
    if not HAS_SKLEARN: raise ImportError("Scikit-Learn required.")
    
    y_t_raw, y_p_raw, target_unit = _extract_and_validate(y_true, y_pred)
    
    error_val = sk_mse(y_t_raw, y_p_raw, **kwargs)
    
    if not squared:
        error_val = np.sqrt(error_val)
    
    if target_unit:
        if squared:
            SquaredUnit = target_unit ** 2
            return SquaredUnit(error_val)
        else:
            return target_unit(error_val)
            
    return error_val

def physics_r2_score(y_true: BaseUnit | NumericLike, y_pred: BaseUnit | NumericLike, **kwargs: Any) -> float:
    """
    Calculates the R-squared (coefficient of determination) regression score function.
    
    Since R-squared represents the proportion of the variance in the dependent 
    variable that is predictable from the independent variable, the result is 
    strictly a dimensionless float, regardless of the physical units of the input.

    Args:
        y_true: Ground truth (correct) target values. Can be a Phaethon BaseUnit.
        y_pred: Estimated target values as returned by a classifier/regressor.
        **kwargs: Additional arguments passed to sklearn.metrics.r2_score.

    Returns:
        float: The R-squared score.

    Examples:
        >>> import phaethon.ml as pml
        >>> import phaethon.units as u
        >>> y_true = u.Joule([3.0, -0.5, 2.0, 7.0])
        >>> y_pred = u.Joule([2.5, 0.0, 2.0, 8.0])
        >>> score = pml.physics_r2_score(y_true, y_pred)
        >>> print(type(score))
        <class 'float'>
    """
    if not HAS_SKLEARN: raise ImportError("Scikit-Learn required.")
    
    y_t_raw, y_p_raw, _ = _extract_and_validate(y_true, y_pred)
    
    return float(sk_r2(y_t_raw, y_p_raw, **kwargs))