"""
Physics-Aware Model Selection Utilities.
"""
from __future__ import annotations
from typing import Any

from ..base import BaseUnit
from ..compat import HAS_NUMPY, HAS_SKLEARN, DataFrameLike

if HAS_SKLEARN:
    import numpy as np
    from sklearn.model_selection import train_test_split as sk_train_test_split
else:
    def sk_train_test_split(*args: Any, **kwargs: Any) -> Any: pass

def physics_train_test_split(*arrays: BaseUnit | DataFrameLike | np.ndarray | list[Any], **options: Any) -> list[Any]:
    """
    Split arrays or matrices into random train and test subsets while strictly 
    preserving Phaethon dimensional physics.

    This function intercepts the Scikit-Learn train_test_split engine. It safely 
    strips physical units before splitting (preventing Sklearn from degrading 
    custom instances into raw arrays) and perfectly resurrects the exact physical 
    dimensions on the output subsets.

    Args:
        *arrays: Allowed inputs are lists, numpy arrays, or Phaethon BaseUnits.
        **options: Standard Scikit-Learn options (e.g., test_size, random_state, shuffle).

    Returns:
        List containing the train-test split of inputs, re-wrapped in their 
        original physical dimensions.
    """
    if not HAS_SKLEARN:
        raise ImportError("Scikit-Learn is required to use phaethon.ml.")

    def extract_unit(data: Any) -> type[BaseUnit] | None:
        if isinstance(data, BaseUnit): return data.__class__
        if HAS_NUMPY and isinstance(data, np.ndarray) and data.dtype == object:
            if len(data) > 0 and isinstance(data[0], BaseUnit): return data[0].__class__
        return None

    def strip_physics(data: Any) -> Any:
        if isinstance(data, BaseUnit): return data.mag
        if hasattr(data, 'to_numpy'):
            arr = data.to_numpy()
            if arr.dtype == object and len(arr) > 0 and isinstance(arr[0], BaseUnit):
                return np.array([item.mag for item in arr], dtype=float)
            return arr
        return data

    saved_units = [extract_unit(arr) for arr in arrays]
    raw_arrays = [strip_physics(arr) for arr in arrays]
    split_raw_results = sk_train_test_split(*raw_arrays, **options)
    
    restored_results = []
    
    for i, raw_result in enumerate(split_raw_results):
        original_unit = saved_units[i // 2]
        
        if original_unit is not None:
            restored_results.append(original_unit(raw_result))
        else:
            restored_results.append(raw_result)
            
    return restored_results