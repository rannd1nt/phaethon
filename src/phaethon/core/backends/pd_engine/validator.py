from __future__ import annotations

import pandas as pd
import numpy as np
from typing import Any, Callable
from ....exceptions import AxiomViolationError, NormalizationError

class ValidatorStage:
    @staticmethod
    def process(
        working_df: pd.DataFrame,
        field_name: str,
        field: Any,
        result_array: np.ndarray,
        raw_series: pd.Series,
        isna_mask: np.ndarray,
        on_err: str,
        target_dim: str | None,
        parse_bound_fn: Callable[..., Any]
    ) -> np.ndarray:
        
        if on_err == 'raise':
            unprocessed_mask = (~isna_mask) & np.isnan(result_array)
            if unprocessed_mask.any():
                bad_indices = working_df.index[unprocessed_mask].tolist()
                raw_sample = raw_series.loc[bad_indices[0]]
                
                if not field.parse_string:
                    issue_msg = "Data contains non-numeric characters but 'parse_string' is False."
                    suggestion_msg = "Set Field(parse_string=True) to extract numbers from text, or clean upstream data."
                else:
                    issue_msg = "Data format rejected by parser (missing unit or invalid text)."
                    suggestion_msg = "Ensure the data contains both a number and a valid unit (e.g., '10 kg') or set Field(on_error='coerce')."

                raise NormalizationError(
                    field=field_name, 
                    issue=issue_msg, 
                    indices=bad_indices,
                    raw_sample=str(raw_sample),
                    expected_dim=str(target_dim) if target_dim else "unknown",
                    suggestion=suggestion_msg
                )

        valid_mask = ~np.isnan(result_array)
        if valid_mask.any():
            if field.min is not None:
                min_val = parse_bound_fn(field.min, field.target_unit)
                violators = result_array < min_val
                if violators.any():
                    if on_err == 'raise':
                        raise AxiomViolationError(f"Field '{field_name}' violates min bound of {field.min}.")
                    elif on_err == 'clip':
                        result_array[violators] = min_val
                    else:
                        result_array[violators] = np.nan
                        
            if field.max is not None:
                max_val = parse_bound_fn(field.max, field.target_unit)
                violators = result_array > max_val
                if violators.any():
                    if on_err == 'raise':
                        raise AxiomViolationError(f"Field '{field_name}' violates max bound of {field.max}.")
                    elif on_err == 'clip':
                        result_array[violators] = max_val
                    else:
                        result_array[violators] = np.nan

        if field.outlier_std is not None:
            valid_mask = ~np.isnan(result_array)
            if valid_mask.sum() > 1:
                mean_val = np.nanmean(result_array)
                std_val = np.nanstd(result_array)
                
                if std_val > 0:
                    z_scores = np.abs((result_array - mean_val) / std_val)
                    outliers = valid_mask & (z_scores > field.outlier_std)
                    if outliers.any():
                        if on_err == 'raise':
                            raise AxiomViolationError(f"Field '{field_name}' contains anomalies > {field.outlier_std} STD.")
                        elif on_err == 'clip':
                            result_array[outliers] = np.nan
                        else:
                            result_array[outliers] = np.nan
                            
        return result_array