from __future__ import annotations

import polars as pl
from typing import Any, Callable
from ....exceptions import AxiomViolationError, NormalizationError

class ValidatorStage:
    @staticmethod
    def process(
        packed_expr: pl.Expr,
        field_name: str,
        field: Any,
        on_err: str,
        target_dim: str | None,
        parse_bound_fn: Callable[..., Any]
    ) -> pl.Expr:
        
        if on_err == 'raise':
            def _raise_garbage(s: pl.Series, *args: Any, **kwargs: Any) -> pl.Series:
                res_s = s.struct.field("res")
                isna_s = s.struct.field("isna")
                raw_s = s.struct.field("raw")
                
                unprocessed_mask = (~isna_s) & res_s.is_null()
                
                if unprocessed_mask.any():
                    bad_samples = raw_s.filter(unprocessed_mask)
                    raw_sample = bad_samples[0] if len(bad_samples) > 0 else "unknown"
                    
                    if not field.parse_string:
                        issue_msg = "Data contains non-numeric characters but 'parse_string' is False."
                        suggestion_msg = "Set Field(parse_string=True) to extract numbers from text."
                    else:
                        issue_msg = "Data format rejected by parser (missing unit or invalid text)."
                        suggestion_msg = "Ensure the data contains both a number and a valid unit (e.g., '10 kg') or set Field(on_error='coerce')."

                    raise NormalizationError(
                        field=field_name, 
                        issue=issue_msg, 
                        indices=[],
                        raw_sample=str(raw_sample),
                        expected_dim=str(target_dim) if target_dim else "unknown",
                        suggestion=suggestion_msg
                    )
                return res_s
            
            expr = packed_expr.map_batches(_raise_garbage, return_dtype=pl.Float64)
        else:
            expr = packed_expr.struct.field("res")

        if field.min is not None:
            min_val = parse_bound_fn(field.min, field.target_unit)
            if on_err == 'raise':
                def _raise_min(s: pl.Series, *args: Any, **kwargs: Any) -> pl.Series:
                    if (s < min_val).any():
                        raise AxiomViolationError(f"Field '{field_name}' violates min bound of {field.min}.")
                    return s
                expr = expr.map_batches(_raise_min, return_dtype=pl.Float64)
            elif on_err == 'clip':
                expr = pl.when(expr < min_val).then(min_val).otherwise(expr)
            else:
                expr = pl.when(expr < min_val).then(None).otherwise(expr)
                
        if field.max is not None:
            max_val = parse_bound_fn(field.max, field.target_unit)
            if on_err == 'raise':
                def _raise_max(s: pl.Series, *args: Any, **kwargs: Any) -> pl.Series:
                    if (s > max_val).any():
                        raise AxiomViolationError(f"Field '{field_name}' violates max bound of {field.max}.")
                    return s
                expr = expr.map_batches(_raise_max, return_dtype=pl.Float64)
            elif on_err == 'clip':
                expr = pl.when(expr > max_val).then(max_val).otherwise(expr)
            else:
                expr = pl.when(expr > max_val).then(None).otherwise(expr)

        if field.outlier_std is not None:
            mean_expr = expr.mean()
            std_expr = expr.std()
            z_scores = ((expr - mean_expr) / std_expr).abs()
            
            if on_err == 'raise':
                def _raise_zscore(s: pl.Series, *args: Any, **kwargs: Any) -> pl.Series:
                    if s.drop_nulls().len() > 1 and s.std() > 0:
                        z = ((s - s.mean()) / s.std()).abs()
                        if (z > field.outlier_std).any():
                            raise AxiomViolationError(f"Field '{field_name}' contains anomalies > {field.outlier_std} STD.")
                    return s
                expr = expr.map_batches(_raise_zscore, return_dtype=pl.Float64)
            else:
                expr = pl.when(z_scores > field.outlier_std).then(None).otherwise(expr)

        return expr