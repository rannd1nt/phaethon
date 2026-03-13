from __future__ import annotations

import pandas as pd
import numpy as np
from typing import Any, Callable

class ImputerStage:
    @staticmethod
    def process(
        result_array: np.ndarray,
        field: Any,
        parse_bound_fn: Callable[..., Any]
    ) -> np.ndarray:
        
        if field.impute_by is not None:
            series_res = pd.Series(result_array)
            if field.impute_by == 'mean':
                series_res = series_res.fillna(series_res.mean())
            elif field.impute_by == 'median':
                series_res = series_res.fillna(series_res.median())
            elif field.impute_by == 'mode':
                modes = series_res.mode()
                if not modes.empty: 
                    series_res = series_res.fillna(modes[0])
            elif field.impute_by == 'ffill':
                series_res = series_res.ffill()
            elif field.impute_by == 'bfill':
                series_res = series_res.bfill()
            else:
                fill_val = parse_bound_fn(field.impute_by, field.target_unit)
                series_res = series_res.fillna(fill_val)
            result_array = series_res.values

        if getattr(field, 'round', None) is not None:
            result_array = np.round(result_array, field.round)
            
        return result_array