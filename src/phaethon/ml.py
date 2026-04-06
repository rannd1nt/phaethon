"""
Phaethon Machine Learning Bridge for Scikit-Learn.

This module provides a robust integration layer for classical machine learning, allowing 
standard Scikit-Learn estimators and transformers to operate directly on physical data 
while maintaining strict dimensional integrity and automated feature synthesis via 
the Buckingham Pi Theorem.

Dependency Note:
        Requires Scikit-Learn.
        Install via: `pip install 'phaethon[sklearn]'` or `pip install 'phaethon[sciml]'`
"""
from __future__ import annotations
from typing import TYPE_CHECKING as _TCHECK, Any

__all__ = [
    'DimensionalEstimator', 'AxiomValidator', 'DimensionalTransformer',
    'BuckinghamTransformer', 'DimensionalFeatureSelector', 'physics_train_test_split',
    'physics_mean_absolute_error', 'physics_mean_squared_error', 'physics_r2_score'
]

if _TCHECK:
    from .core.ml.estimator import DimensionalEstimator as DimensionalEstimator, AxiomValidator as AxiomValidator
    from .core.ml.preprocessing import DimensionalTransformer as DimensionalTransformer
    from .core.ml.features import BuckinghamTransformer as BuckinghamTransformer, DimensionalFeatureSelector as DimensionalFeatureSelector
    from .core.ml.selection import physics_train_test_split as physics_train_test_split
    from .core.ml.metrics import (
        physics_mean_absolute_error as physics_mean_absolute_error, 
        physics_mean_squared_error as physics_mean_squared_error, 
        physics_r2_score as physics_r2_score
    )

from .core.compat import HAS_SKLEARN as _HAS_SKLEARN, require_sklearn as _reqsklearn

if _HAS_SKLEARN:
    from .core.ml.estimator import DimensionalEstimator, AxiomValidator
    from .core.ml.preprocessing import DimensionalTransformer
    from .core.ml.features import BuckinghamTransformer, DimensionalFeatureSelector
    from .core.ml.selection import physics_train_test_split
    from .core.ml.metrics import (
        physics_mean_absolute_error, physics_mean_squared_error, physics_r2_score
    )
else:
    __all__ = []
    def __getattr__(name: str) -> Any:
        _reqsklearn(f"Accessing '{name}'")
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")