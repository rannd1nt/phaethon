from __future__ import annotations

import pandas as pd
import numpy as np

class ExtractorStage:
    @staticmethod
    def process(
        series: pd.Series, 
        parse_string: bool, 
        unit_col_data: pd.Series | None = None
    ) -> tuple[np.ndarray, np.ndarray | None, np.ndarray]:
        
        isna_mask = np.asarray(series.isna(), dtype=bool)
        
        if series.dtype == object or pd.api.types.is_string_dtype(series):
            blank_str_mask = np.asarray(series.astype(str).str.strip() == "", dtype=bool)
            isna_mask = isna_mask | blank_str_mask
            
        values_array = np.full(len(series), np.nan, dtype=float)
        units_array = None

        if parse_string:
            extracted = series.astype(str).str.extract(r'^\s*([-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?)(?:\s+(.*?))?\s*$')
            values_array = pd.to_numeric(extracted[0], errors='coerce').values
            units_array = np.asarray(extracted[1].values, dtype=object)
            units_array[units_array == ''] = np.nan
            
        elif unit_col_data is not None:
            values_array = pd.to_numeric(series, errors='coerce').values
            units_array = np.asarray(unit_col_data.values, dtype=object)
        else:
            values_array = pd.to_numeric(series, errors='coerce').values

        return values_array, units_array, isna_mask