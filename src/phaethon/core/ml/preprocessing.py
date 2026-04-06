"""
Scikit-Learn Meta-Transformer for Phaethon Dimensional Algebra.
"""
from __future__ import annotations
from typing import Any, TYPE_CHECKING, Generic, TypeVar

from ...exceptions import DimensionMismatchError
from ..base import BaseUnit
from ..compat import HAS_NUMPY, HAS_SKLEARN

if TYPE_CHECKING:
    import numpy as np
    from typing_extensions import Self
    from ..compat import _InvTransformerT, DataFrameLike, NumericLike
else:
    _InvTransformerT = TypeVar("_InvTransformerT")
    Self = Any
    DataFrameLike = Any
    NumericLike = Any

if HAS_SKLEARN:
    import numpy as np
    from sklearn.base import BaseEstimator, TransformerMixin, clone
    from sklearn.utils.validation import check_is_fitted
else:
    class BaseEstimator: ...
    class TransformerMixin: ...
    def clone(*args: Any, **kwargs: Any) -> Any: return None
    def check_is_fitted(*args: Any, **kwargs: Any) -> None: pass

def _fmtdim(u_cls: Any) -> str:
    if u_cls is None: return "unknown"
    dim = getattr(u_cls, 'dimension', 'unknown')
    if dim == 'anonymous':
        sym = getattr(u_cls, 'symbol', '???')
        return f"Unregistered DNA [{sym}]"
    sym = getattr(u_cls, 'symbol', '')
    sym_str = f" [{sym}]" if sym else ""
    return f"{dim}{sym_str}"

class DimensionalTransformer(BaseEstimator, TransformerMixin, Generic[_InvTransformerT]):
    """
    A physical data scaling and normalization transformer.
    
    It standardizes dimensioned variables for algorithmic stability while preserving 
    their physical identity. During transformation, it safely evaluates the data into 
    dimensionless states for computation, and guarantees the exact restoration of the 
    original physical units during inverse transformations.
    """
    __module__ = "phaethon.ml"

    def __init__(self, transformer: _InvTransformerT) -> None:
        """
        A physical data scaling and normalization transformer.
    
        It standardizes dimensioned variables for algorithmic stability while preserving 
        their physical identity. During transformation, it safely evaluates the data into 
        dimensionless states for computation, and guarantees the exact restoration of the 
        original physical units during inverse transformations.

        Args:
            transformer: The underlying scaling algorithm 
                (e.g., StandardScaler, MinMaxScaler).

        Raises:
            DimensionMismatchError: If attempting to transform data that does not match 
                the physical dimension learned during the initial fitting phase.

        Examples:
            >>> import phaethon.ml as pml
            >>> from sklearn.preprocessing import StandardScaler
            >>> import phaethon.units as u
            >>> scaler = pml.DimensionalTransformer(StandardScaler())
            >>> X_scaled = scaler.fit_transform(u.Kelvin([300.0, 310.0, 320.0]))
            >>> # The output is mathematically dimensionless for safe ML consumption
            >>> X_restored = scaler.inverse_transform(X_scaled)
            >>> print(X_restored.dimension)
            'temperature'
        """
        if not HAS_SKLEARN:
            raise ImportError("Scikit-Learn is required to use the phaethon.ml module.")
        self.transformer = transformer

    def _strip_physics(self, data: Any) -> Any:
        """Melucuti jubah dimensi dengan aman."""
        if isinstance(data, BaseUnit):
            return data.mag
        if hasattr(data, 'to_numpy'):
            arr = data.to_numpy()
            if arr.dtype == object and len(arr) > 0 and isinstance(arr[0], BaseUnit):
                return np.array([item.mag for item in arr], dtype=float)
            return arr
        return data

    def _extract_unit(self, data: Any) -> type[BaseUnit] | None:
        if isinstance(data, BaseUnit):
            return data.__class__
        if HAS_NUMPY and isinstance(data, np.ndarray) and data.dtype == object:
            if len(data) > 0 and isinstance(data[0], BaseUnit):
                return data[0].__class__
        return None

    def fit(self, X: DataFrameLike | NumericLike | BaseUnit, y: Any = None, **fit_params: Any) -> Self:
        """
        Learns the physical unit of the input data and fits the underlying transformer.

        Args:
            X: The data used to compute the per-feature scaling parameters.
            y: Target values. Defaults to None.
            **fit_params: Additional fitting parameters for the underlying estimator.

        Returns:
            DimensionalTransformer: The fitted transformer instance.
        """
        # 1. HAFALKAN DIMENSI INPUT SEBELUM DI-FIT
        self.fitted_feature_unit_ = self._extract_unit(X)

        # 2. Clone Transformer Asli (Praktik standar Scikit-Learn)
        self.transformer_ = clone(self.transformer)

        # 3. Lucuti jubahnya dan fit data murni
        X_raw = self._strip_physics(X)
        y_raw = self._strip_physics(y)

        if y_raw is not None:
            self.transformer_.fit(X_raw, y_raw, **fit_params)
        else:
            self.transformer_.fit(X_raw, **fit_params)

        self.is_fitted_ = True
        return self

    def transform(self, X: DataFrameLike | NumericLike | BaseUnit) -> np.ndarray:
        """
        Transforms the data, evaluating it into a mathematically dimensionless state.

        Args:
            X (Any): The data to scale/transform, wrapped in physical units.

        Returns:
            np.ndarray: A raw NumPy array containing the transformed, dimensionless data 
            suitable for machine learning algorithms.
            
        Raises:
            DimensionMismatchError: If X does not match the physical dimension learned during fit.
        """
        check_is_fitted(self, 'is_fitted_')

        detected_X_unit = self._extract_unit(X)
        if self.fitted_feature_unit_ and detected_X_unit:
            if getattr(self.fitted_feature_unit_, 'dimension', None) != getattr(detected_X_unit, 'dimension', None):
                raise DimensionMismatchError(
                    _fmtdim(self.fitted_feature_unit_),
                    _fmtdim(detected_X_unit),
                    "DimensionalTransformer.transform() Security Validation"
                )

        X_raw = self._strip_physics(X)
        return self.transformer_.transform(X_raw)

    def inverse_transform(self, X: np.ndarray | DataFrameLike) -> BaseUnit | np.ndarray:
        """
        Inverses the transformation and resurrects the original physical units.

        Args:
            X: The transformed (dimensionless) data to be inverted.

        Returns:
            A Phaethon BaseUnit instance restoring the exact physical dimensions 
            learned during the fit phase.
            
        Raises:
            AttributeError: If the underlying transformer does not support inverse_transform.
        """
        check_is_fitted(self, 'is_fitted_')

        if not hasattr(self.transformer_, 'inverse_transform'):
            raise AttributeError(f"{self.transformer_.__class__.__name__} does not support inverse_transform.")

        X_raw = self._strip_physics(X)
        X_inverted_raw = self.transformer_.inverse_transform(X_raw)

        if self.fitted_feature_unit_ is not None:
            return self.fitted_feature_unit_(X_inverted_raw)

        return X_inverted_raw
    
    def fit_transform(self, X: DataFrameLike | NumericLike | BaseUnit, y: Any = None, **fit_params: Any) -> np.ndarray:
        """
        Fits the transformer to the physical data and then transforms it into a dimensionless state.
        
        This method explicitly overrides the default Mixin behavior to provide strict 
        type hinting for IDEs, ensuring developers know the output loses its physical 
        armor for safe algorithm consumption.

        Args:
            X: The data used to compute the per-feature scaling parameters. 
                Expected to be a Phaethon BaseUnit.
            y: Target values. Defaults to None.
            **fit_params: Additional fitting parameters.

        Returns:
            np.ndarray: A raw mathematically dimensionless NumPy array.
            
        Raises:
            DimensionMismatchError: If the input features violate physical contracts.
        """
        return self.fit(X, y, **fit_params).transform(X)