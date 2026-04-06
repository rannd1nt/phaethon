"""
Physics-Aware Feature Engineering for Scikit-Learn.
Dynamically extracts dimensionless groups (Pi Groups) using NumPy SVD.
"""
from __future__ import annotations
from typing import Any, Sequence, TYPE_CHECKING

from ...exceptions import DimensionMismatchError, AxiomViolationError
from ..base import BaseUnit
from ..compat import HAS_SKLEARN

if TYPE_CHECKING:
    import numpy as np
    from typing_extensions import Self
else:
    Self = Any

if HAS_SKLEARN:
    import numpy as np
    from sklearn.base import BaseEstimator, TransformerMixin
    from sklearn.utils.validation import check_is_fitted
else:
    class BaseEstimator: ...
    class TransformerMixin: ...
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

class BuckinghamTransformer(BaseEstimator, TransformerMixin):
    """
    An automated feature engineering transformer powered by the Buckingham Pi Theorem.
    
    It evaluates a sequence of distinct physical variables, extracts their dimensional 
    signatures, and utilizes Singular Value Decomposition (SVD) to discover the dimensional 
    null space. It then synthesizes highly predictive, purely dimensionless groups 
    (e.g., Reynolds Number, Fourier Number) to be used as robust features for machine learning.

    Args:
        tolerance: The singular value threshold for determining the rank of the 
            dimensional matrix. Defaults to 1e-5.

    Raises:
        ValueError: If the provided variables lack a valid null space and cannot 
            mathematically form any dimensionless groups.
        TypeError: If the input is not a valid sequence of Phaethon BaseUnit instances.

    Examples:
        >>> import phaethon.ml as pml
        >>> import phaethon.units as u
        >>> pi_extractor = pml.BuckinghamTransformer()
        >>> # Provide velocity, diameter, density, and viscosity
        >>> X_features = [u.MeterPerSecond([...]), u.Meter([...]), u.KilogramPerCubicMeter([...]), u.PascalSecond([...])]
        >>> dimensionless_groups = pi_extractor.fit_transform(X_features)
        >>> print(dimensionless_groups.shape)
        (n_samples, n_pi_groups)
    """
    __module__ = "phaethon.ml"

    def __init__(self, tolerance: float = 1e-5) -> None:
        if not HAS_SKLEARN:
            raise ImportError("Scikit-Learn is required to use phaethon.ml.")
        self.tolerance = tolerance

    def _build_dimensional_matrix(self, signatures: list[dict[str, int]]) -> np.ndarray:
        """
        Constructs the internal Dimensional Matrix from physical signatures.
        Rows represent fundamental dimensions, columns represent variables.
        """
        all_dims = set()
        for sig in signatures:
            all_dims.update(sig.keys())
            
        dim_list = sorted(list(all_dims))
        matrix = np.zeros((len(dim_list), len(signatures)), dtype=float)
        
        for col_idx, sig in enumerate(signatures):
            for row_idx, dim in enumerate(dim_list):
                if dim in sig:
                    matrix[row_idx, col_idx] = sig[dim]
                    
        return matrix

    def _rationalize_null_vectors(self, vectors: np.ndarray) -> np.ndarray:
        """
        Scales and normalizes the SVD null vectors into human-readable 
        physical exponents (e.g., rounding to nearest halves or integers).
        """
        rationalized = []
        for v in vectors:
            mask = np.abs(v) > 1e-4
            if not np.any(mask):
                rationalized.append(v)
                continue
            
            min_val = np.min(np.abs(v[mask]))
            v_scaled = v / min_val
            v_rounded = np.round(v_scaled * 2.0) / 2.0 
            
            first_nonzero = np.nonzero(mask)[0][0]
            if v_rounded[first_nonzero] < 0:
                v_rounded = -v_rounded
                
            rationalized.append(v_rounded)
        return np.array(rationalized)

    def fit(self, X: Sequence[BaseUnit], y: Any = None) -> Self:
        """
        Executes Singular Value Decomposition (SVD) to find the Null Space 
        of the provided physical inputs.

        Args:
            X: A sequence (list/tuple) of Phaethon BaseUnit tensors representing 
                the independent physical variables.
            y: Target values (ignored, kept for Scikit-Learn pipeline compatibility).

        Returns:
            The fitted transformer instance.
            
        Raises:
            TypeError: If X is not a sequence of BaseUnit instances.
            AxiomViolationError: If the dimensional matrix lacks a valid null space.
        """
        if not isinstance(X, (list, tuple)) or not all(isinstance(x, BaseUnit) for x in X):
            raise TypeError("BuckinghamTransformer requires X to be a list/tuple of BaseUnit instances.")

        self.input_signatures_ = [dict(getattr(x, '_signature', frozenset())) for x in X]
        M = self._build_dimensional_matrix(self.input_signatures_)
        
        U, S, Vh = np.linalg.svd(M, full_matrices=True)
        rank = np.sum(S > self.tolerance)
        num_vars = M.shape[1]
        
        if rank == num_vars:
            raise AxiomViolationError(
                "The dimensional matrix has an empty null space. "
                "These variables CANNOT mathematically form a dimensionless group! "
                "Are you missing a balancing variable (like Time or Mass)?"
            )
            
        null_vectors = Vh[rank:, :]
        self.pi_exponents_ = self._rationalize_null_vectors(null_vectors)
        self.is_fitted_ = True
        return self

    def transform(self, X: Sequence[BaseUnit]) -> np.ndarray:
        """
        Synthesizes the dimensionless groups and strips their metadata.

        Args:
            X: A sequence of Phaethon BaseUnit tensors to be transformed.

        Returns:
            A raw 2D NumPy array of shape (n_samples, n_dimensionless_groups) 
            containing the mathematically synthesized features.

        Raises:
            ValueError: If the number of variables in X does not match the fitted state.
            DimensionMismatchError: If the synthesized feature fails to collapse 
                into a pure dimensionless state.
        """
        check_is_fitted(self, 'is_fitted_')
        
        if len(X) != len(self.input_signatures_):
            raise ValueError(f"Expected {len(self.input_signatures_)} variables, got {len(X)}.")

        pi_groups_raw = []
        
        for exponents in self.pi_exponents_:
            pi_tensor: BaseUnit | None = None
            
            for var, power in zip(X, exponents):
                if abs(power) < 1e-4:
                    continue
                    
                term = var ** power
                pi_tensor = term if pi_tensor is None else pi_tensor * term
                
            if pi_tensor is None:
                continue
                
            dim_result = getattr(pi_tensor, 'dimension', None)
            
            # The Void Collapse validation!
            if dim_result not in ('dimensionless', 'anonymous', None):
                raise DimensionMismatchError(
                    "dimensionless", 
                    _fmtdim(pi_tensor.__class__ if pi_tensor else None),
                    "Buckingham Synthesis Collapse"
                )
                
            pi_groups_raw.append(np.asarray(pi_tensor.mag).flatten())
            
        return np.column_stack(pi_groups_raw)
        
    def fit_transform(self, X: Sequence[BaseUnit], y: Any = None, **fit_params: Any) -> np.ndarray:
        """
        Fits the transformer to the physical sequence and synthesizes the dimensionless groups.
        
        Explicitly overridden to provide strict IDE Type Hinting.

        Args:
            X: A sequence of Phaethon BaseUnit tensors.
            y: Target values. Defaults to None.
            **fit_params: Additional fitting parameters.

        Returns:
            A raw mathematically dimensionless NumPy array.
        """
        return self.fit(X, y, **fit_params).transform(X)
    
class DimensionalFeatureSelector(BaseEstimator, TransformerMixin):
    """
    A feature selection transformer that filters input columns strictly 
    based on their dimensional identity.
    
    It scans a sequence of input features and drops any feature that lacks 
    a valid physical dimension (e.g., purely dimensionless columns, raw arrays, 
    or ID numbers) to prevent machine learning models from overfitting on 
    spurious, non-physical correlations.
    """
    __module__ = "phaethon.ml"

    def __init__(self, strict_physics: bool = True) -> None:
        """
        A feature selection transformer that filters input columns strictly 
        based on their dimensional identity.
        
        It scans a sequence of input features and drops any feature that lacks 
        a valid physical dimension (e.g., purely dimensionless columns, raw arrays, 
        or ID numbers) to prevent machine learning models from overfitting on 
        spurious, non-physical correlations.

        Args:
            strict_physics: If True, explicitly drops dimensionless and anonymous 
                features. If False, allows them to pass through. Defaults to True.

        Raises:
            ValueError: If the number of input features during transform does not 
                match the fitted state.
        """
        if not HAS_SKLEARN:
            raise ImportError("Scikit-Learn is required to use phaethon.ml.")
        self.strict_physics = strict_physics

    def fit(self, X: Sequence[BaseUnit | np.ndarray | Any], y: Any = None) -> Self:
        """
        Analyzes the dimensional signatures of the input sequence to build 
        the selection mask.

        Args:
            X: A sequence of features (Phaethon BaseUnits or raw arrays).
            y: Target values (ignored).

        Returns:
            The fitted selector instance.
        """
        self.support_mask_ = []
        for feature in X:
            if isinstance(feature, BaseUnit):
                dim = getattr(feature, 'dimension', 'dimensionless')
                if self.strict_physics and dim in ('dimensionless', 'anonymous', None):
                    self.support_mask_.append(False)
                else:
                    self.support_mask_.append(True)
            else:
                self.support_mask_.append(not self.strict_physics)
                
        self.is_fitted_ = True
        return self

    def transform(self, X: Sequence[BaseUnit | np.ndarray | Any]) -> list[BaseUnit | np.ndarray | Any]:
        """
        Filters the sequence of features, dropping non-physical columns.

        Args:
            X: A sequence of features to be filtered.

        Returns:
            A subset list containing only physically valid feature representations.
            
        Raises:
            ValueError: If the sequence length doesn't match the fit phase.
        """
        check_is_fitted(self, 'is_fitted_')
        
        if len(X) != len(self.support_mask_):
            raise ValueError(f"Expected {len(self.support_mask_)} features, got {len(X)}.")
            
        return [feature for feature, keep in zip(X, self.support_mask_) if keep]
    
    def fit_transform(self, X: Sequence[BaseUnit | np.ndarray], y: Any = None, **fit_params: Any) -> list[BaseUnit | np.ndarray]:
        """
        Fits the selector to the input sequence and returns the filtered features.
        
        Explicitly overridden to provide strict IDE Type Hinting.

        Args:
            X: A sequence of features.
            y: Target values. Defaults to None.
            **fit_params: Additional fitting parameters.

        Returns:
            A subset list of physically valid features.
        """
        return self.fit(X, y, **fit_params).transform(X)