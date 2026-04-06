"""
Scikit-Learn Meta-Estimator for Phaethon Dimensional Algebra.
"""
from __future__ import annotations
from typing import Any, TYPE_CHECKING, Generic, TypeVar

from ...exceptions import DimensionMismatchError
from ..base import BaseUnit
from ..compat import HAS_NUMPY, HAS_SKLEARN

if TYPE_CHECKING:
    import numpy as np
    from typing_extensions import Self
    from ..compat import _EstimatorT, _UnitT, DataFrameLike, NumericLike, ConvertibleInput
else:
    _EstimatorT = TypeVar("_EstimatorT")
    _UnitT = TypeVar("_UnitT")
    Self = Any
    DataFrameLike = Any
    NumericLike = Any

if HAS_SKLEARN:
    if HAS_NUMPY:
        import numpy as np
    from sklearn.base import BaseEstimator, MetaEstimatorMixin, clone
    from sklearn.utils.validation import check_is_fitted
    from sklearn.utils.metaestimators import available_if
else:
    class BaseEstimator: ...
    class MetaEstimatorMixin: ...
    
    def clone(*args: Any, **kwargs: Any) -> Any: return None
    def check_is_fitted(*args: Any, **kwargs: Any) -> None: pass
    def available_if(*args: Any, **kwargs: Any) -> Any: return lambda x: x

def _estimator_has(attr: str) -> Any:
    """Helper untuk mendelegasikan metode (seperti predict_proba)."""
    return lambda self: (hasattr(self.estimator_, attr) if hasattr(self, 'estimator_') 
                         else hasattr(self.estimator, attr))

def _estimator_has(attr: str) -> Any:
    return lambda self: (hasattr(self.estimator_, attr) if hasattr(self, 'estimator_') 
                         else hasattr(self.estimator, attr))

def _fmtdim(u_cls: Any) -> str:
    if u_cls is None: return "unknown"
    dim = getattr(u_cls, 'dimension', 'unknown')
    if dim == 'anonymous':
        sym = getattr(u_cls, 'symbol', '???')
        return f"Unregistered DNA [{sym}]"
    sym = getattr(u_cls, 'symbol', '')
    sym_str = f" [{sym}]" if sym else ""
    return f"{dim}{sym_str}"

class DimensionalEstimator(BaseEstimator, MetaEstimatorMixin, Generic[_EstimatorT]):
    """
    A physics-aware predictive model that seamlessly bridges dimensional algebra 
    with classical machine learning. 

    It automatically infers the physical dimensions of the training data, ensures 
    dimensional consistency during inference, and structurally restores the exact 
    physical units to the final predictions without requiring manual intervention.
    """
    __module__ = "phaethon.ml"

    def __init__(
        self, 
        estimator: _EstimatorT, 
        enforce_target_unit: type[_UnitT] | None = None
    ) -> None:
        """
        A physics-aware predictive model that seamlessly bridges dimensional algebra 
        with classical machine learning. 

        It automatically infers the physical dimensions of the training data, ensures 
        dimensional consistency during inference, and structurally restores the exact 
        physical units to the final predictions without requiring manual intervention.

        Args:
            estimator (BaseEstimator): The core machine learning algorithm to be utilized 
                (e.g., RandomForestRegressor, Ridge).
            enforce_target_unit (type[BaseUnit] | None, optional): An explicit physical unit 
                to strictly enforce on the target variable. If None, the estimator will 
                perform Zero-Config Auto-Inference from the training data.

        Raises:
            DimensionMismatchError: If the input features or target variables during prediction 
                violate the dimensional contracts established during training.

        Examples:
            >>> import phaethon.ml as pml
            >>> from sklearn.ensemble import RandomForestRegressor
            >>> import phaethon.units as u
            >>> model = pml.DimensionalEstimator(RandomForestRegressor())
            >>> # The model learns that 'y' is strictly Energy (Joule)
            >>> model.fit(X_train, y_target=u.Joule([100, 200, 300]))
            >>> predictions = model.predict(X_test)
            >>> print(predictions.dimension)
            'energy'
        """
        if not HAS_SKLEARN:
            raise ImportError("Scikit-Learn is required to use the phaethon.ml module.")
            
        self.estimator = estimator
        self.enforce_target_unit = enforce_target_unit

    def _strip_physics(self, data: Any) -> Any:
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

    def fit(self, X: DataFrameLike | NumericLike | BaseUnit, y: ConvertibleInput, **fit_params: Any) -> Self:
        """
        Fits the underlying estimator while automatically inferring the physical 
        dimensions of both features and target variables.

        Args:
            X: The training input samples.
            y: The target values (class labels in classification, real numbers in regression).
            **fit_params: Additional fitting parameters for the underlying estimator.

        Returns:
            DimensionalEstimator: The fitted estimator instance.
            
        Raises:
            DimensionMismatchError: If the target data violates the explicitly enforced 
                target unit (if provided).
        """

        detected_target_unit = self._extract_unit(y)
        
        if self.enforce_target_unit is not None:
            if detected_target_unit and getattr(detected_target_unit, 'dimension', None) != getattr(self.enforce_target_unit, 'dimension', None):
                raise DimensionMismatchError(
                    _fmtdim(self.enforce_target_unit), 
                    _fmtdim(detected_target_unit), 
                    "DimensionalEstimator Strict Target Validation"
                )
            self.fitted_target_unit_ = self.enforce_target_unit
        else:
            self.fitted_target_unit_ = detected_target_unit

        self.fitted_feature_unit_ = self._extract_unit(X)

        self.estimator_ = clone(self.estimator)
        
        X_raw = self._strip_physics(X)
        y_raw = self._strip_physics(y)
        
        self.estimator_.fit(X_raw, y_raw, **fit_params)
        
        if hasattr(self.estimator_, 'classes_'):
            self.classes_ = self.estimator_.classes_
            
        self.is_fitted_ = True 
        return self

    def predict(self, X: DataFrameLike | NumericLike | BaseUnit) -> BaseUnit | np.ndarray:
        """
        Predicts using the underlying estimator and automatically reapplies 
        the learned physical units to the output.

        Args:
            X: The input samples to predict.

        Returns:
            The predicted values, structured as a Phaethon BaseUnit inheriting 
            the exact dimension of the training target.
            
        Raises:
            DimensionMismatchError: If the prediction input violates the dimensional 
                contract established during training.
        """
        check_is_fitted(self, 'is_fitted_')
        
        detected_X_unit = self._extract_unit(X)
        if self.fitted_feature_unit_ and detected_X_unit:
            if getattr(self.fitted_feature_unit_, 'dimension', None) != getattr(detected_X_unit, 'dimension', None):
                raise DimensionMismatchError(
                    _fmtdim(self.fitted_feature_unit_), 
                    _fmtdim(detected_X_unit), 
                    "DimensionalEstimator.predict() Input Validation"
                )

        X_raw = self._strip_physics(X)
        y_pred_raw = self.estimator_.predict(X_raw)
        
        if self.fitted_target_unit_ is not None:
            return self.fitted_target_unit_(y_pred_raw)
            
        return y_pred_raw

    @available_if(_estimator_has('predict_proba'))
    def predict_proba(self, X: Any) -> Any:
        """
        Predicts class probabilities for the input samples.

        Args:
            X: The input samples to predict.

        Returns:
            Any: The class probabilities. Returns a raw array as probabilities are dimensionless.
        """
        check_is_fitted(self, 'is_fitted_')
        return self.estimator_.predict_proba(self._strip_physics(X))

    @available_if(_estimator_has('score'))
    def score(self, X: Any, y: Any, sample_weight: Any = None) -> float:
        """
        Calculates the evaluation score of the underlying estimator.

        Args:
            X: Test samples.
            y: True labels for X.
            sample_weight: Sample weights. Defaults to None.

        Returns:
            float: The score of the estimator (dimensionless).
        """
        check_is_fitted(self, 'is_fitted_')
        return self.estimator_.score(
            self._strip_physics(X), 
            self._strip_physics(y), 
            sample_weight=self._strip_physics(sample_weight)
        )
    
class AxiomValidator(BaseEstimator, MetaEstimatorMixin, Generic[_EstimatorT]):
    """
    A physics-enforcement meta-estimator that clips mathematically valid 
    but physically impossible predictions.
    
    It wraps a trained dimensional estimator and intercepts its predictions. 
    If the underlying machine learning model predicts values that violate 
    the absolute bounds defined in Phaethon's unit registry (e.g., predicting 
    a negative mass or absolute temperature), this validator will forcefully 
    clip the magnitude to the nearest valid physical boundary.

    Args:
        estimator: The fitted DimensionalEstimator to be validated.

    Raises:
        RuntimeError: If the wrapped estimator does not return a Phaethon BaseUnit.
    """
    __module__ = "phaethon.ml"

    def __init__(self, estimator: DimensionalEstimator[_EstimatorT]) -> None:
        if not HAS_SKLEARN:
            raise ImportError("Scikit-Learn is required to use phaethon.ml.")
        self.estimator = estimator

    def fit(self, X: DataFrameLike | NumericLike | BaseUnit, y: ConvertibleInput, **fit_params: Any) -> Self:
        """
        Fits the underlying estimator.

        Args:
            X: Training features.
            y: Target values.
            **fit_params: Additional fitting parameters.

        Returns:
            The fitted AxiomValidator instance.
        """
        self.estimator_ = clone(self.estimator)
        self.estimator_.fit(X, y, **fit_params)
        self.is_fitted_ = True
        return self

    def predict(self, X: DataFrameLike | NumericLike | BaseUnit) -> BaseUnit | np.ndarray:
        """
        Predicts using the wrapped estimator and enforces physical boundaries.

        Args:
            X: Input features to predict.

        Returns:
            A clipped Phaethon BaseUnit ensuring absolute physical compliance.
        """
        check_is_fitted(self, 'is_fitted_')
        
        if hasattr(self.estimator_, 'estimator_') and hasattr(self.estimator_, 'fitted_target_unit_'):
            raw_model = self.estimator_.estimator_
            target_unit = self.estimator_.fitted_target_unit_
            
            X_raw = self.estimator_._strip_physics(X)
            y_pred_raw = raw_model.predict(X_raw)
            
            if target_unit is not None:
                min_val = getattr(target_unit, '__axiom_min__', None)
                max_val = getattr(target_unit, '__axiom_max__', None)
                
                if min_val is not None or max_val is not None:
                    if HAS_NUMPY:
                        y_pred_raw = np.clip(y_pred_raw, a_min=min_val, a_max=max_val)
                
                return target_unit(y_pred_raw)
                
            return y_pred_raw

        y_pred = self.estimator_.predict(X)
        if isinstance(y_pred, BaseUnit):
            min_val = getattr(y_pred.__class__, '__axiom_min__', None)
            max_val = getattr(y_pred.__class__, '__axiom_max__', None)
            if min_val is not None or max_val is not None:
                if HAS_NUMPY:
                    clipped_mag = np.clip(y_pred.mag, a_min=min_val, a_max=max_val)
                    return y_pred.__class__(clipped_mag, context=y_pred.context)
        return y_pred