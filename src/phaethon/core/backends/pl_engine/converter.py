from __future__ import annotations

from ...compat import HAS_POLARS
if HAS_POLARS:
    import polars as pl
import numpy as np
import pandas as pd
import warnings
from typing import Any
from ...registry import ureg
from ....exceptions import AxiomViolationError, NormalizationError, DimensionMismatchError
from ...config import get_merged_context, get_config

class ConverterStage:
    @staticmethod
    def process(
        expr: pl.Expr,
        field_name: str,
        field: Any,
        on_err: str,
        target_dim: str | None
    ) -> pl.Expr:
        
        active_context = get_merged_context(getattr(field, 'context', {}))
        if getattr(field, 'axiom_strictness_level', None) is not None:
            active_context["axiom_strictness_level"] = field.axiom_strictness_level
        if getattr(field, 'on_error', None) is not None:
            active_context["default_on_error"] = field.on_error

        strictness = get_config("axiom_strictness_level", getattr(field, 'axiom_strictness_level', None)) or "default"
        should_warn = strictness in ("strict_warn", "loose_warn")
        should_enforce = strictness in ("default", "strict", "strict_warn")

        def _vectorized_numpy_bridge(s: pl.Series, *args: Any, **kwargs: Any) -> pl.Series:
            if s.dtype == pl.Struct:
                values_array = s.struct.field("value").cast(pl.Float64, strict=False).to_numpy()
                units_array = s.struct.field("unit").cast(pl.String).to_numpy(allow_copy=True) 
            else:
                values_array = s.cast(pl.Float64, strict=False).to_numpy()
                units_array = None

            result_array = np.full(len(values_array), np.nan, dtype=float)
            isna_mask = np.isnan(values_array)

            if units_array is not None:
                valid_unit_mask = (~pd.isna(units_array)) & (~isna_mask)
                if valid_unit_mask.any():
                    unique_units = pd.Series(units_array[valid_unit_mask]).unique()
                    for u_str in unique_units:
                        mask = (units_array == u_str) & valid_unit_mask
                        try:
                            source_cls = ureg().get_unit_class(u_str, expected_dim=target_dim)
                            raw_masked = values_array[mask].astype(float)
                            
                            if strictness == "ignore":
                                axiom_min, axiom_max = None, None
                            else:
                                axiom_min = getattr(source_cls, '__axiom_min__', None)
                                axiom_max = getattr(source_cls, '__axiom_max__', None)
                            
                            if axiom_min is not None:
                                violators = raw_masked < float(axiom_min)
                                if violators.any():
                                    msg = f"Raw '{u_str}' violates min bound of {axiom_min}."
                                    if should_warn and not should_enforce:
                                        warnings.warn(f"Phaethon Axiom Warning: {msg}", category=UserWarning, stacklevel=2)
                                    if should_enforce:
                                        if on_err == 'raise':
                                            raise AxiomViolationError(msg)
                                        elif on_err == 'clip':
                                            raw_masked[violators] = float(axiom_min)
                                        else:
                                            raw_masked[violators] = np.nan
                                        
                            if axiom_max is not None:
                                violators = raw_masked > float(axiom_max)
                                if violators.any():
                                    msg = f"Raw '{u_str}' violates max bound of {axiom_max}."
                                    if should_warn and not should_enforce:
                                        warnings.warn(f"Phaethon Axiom Warning: {msg}", category=UserWarning, stacklevel=2)
                                    if should_enforce:
                                        if on_err == 'raise':
                                            raise AxiomViolationError(msg)
                                        elif on_err == 'clip':
                                            raw_masked[violators] = float(axiom_max)
                                        else:
                                            raw_masked[violators] = np.nan
                            
                            src_name = getattr(source_cls, '__name__', str(source_cls))
                            tgt_name = getattr(field.target_unit, '__name__', str(field.target_unit))
                            
                            if source_cls == field.target_unit or src_name == tgt_name:
                                result_array[mask] = raw_masked
                            else:
                                source_instances = source_cls(raw_masked, context=active_context)
                                target_instances = source_instances.to(field.target_unit, active_context)
                                result_array[mask] = target_instances.mag
                                
                        except Exception as e:
                            if on_err == 'raise':
                                if isinstance(e, AxiomViolationError):
                                    raise e
                                raise NormalizationError(
                                    field=field_name, issue=str(e), indices=[],
                                    raw_sample=str(u_str), expected_dim=str(target_dim) if target_dim else "unknown",
                                    suggestion="Check unit format or set Field(on_error='coerce')."
                                )

                pure_num_mask = pd.isna(units_array) & (~isna_mask)
            else:
                pure_num_mask = (~isna_mask)

            if pure_num_mask.any():
                source_cls = field.source_unit if field.parse_string else (field.source_unit or field.target_unit)

                if source_cls is None:
                    if on_err == 'raise':
                        raise NormalizationError(
                            field=field_name, issue="Value has no unit, and no 'source_unit' provided.",
                            indices=[], raw_sample="unknown", expected_dim=str(target_dim) if target_dim else "unknown",
                            suggestion="Provide 'source_unit' or ensure data has units."
                        )
                    else:
                        result_array[pure_num_mask] = np.nan
                else:
                    try:
                        if isinstance(source_cls, str):
                            source_cls = ureg().get_unit_class(source_cls, expected_dim=target_dim)
                        
                        raw_masked = values_array[pure_num_mask].astype(float)
                        
                        if strictness == "ignore":
                            axiom_min, axiom_max = None, None
                        else:
                            axiom_min = getattr(source_cls, '__axiom_min__', None)
                            axiom_max = getattr(source_cls, '__axiom_max__', None)
                        
                        if axiom_min is not None:
                            violators = raw_masked < float(axiom_min)
                            if violators.any():
                                msg = f"Pure number violates min bound of {axiom_min}."
                                if should_warn and not should_enforce:
                                    warnings.warn(f"Phaethon Axiom Warning: {msg}", category=UserWarning, stacklevel=2)
                                if should_enforce:
                                    if on_err == 'raise':
                                        raise AxiomViolationError(msg)
                                    elif on_err == 'clip':
                                        raw_masked[violators] = float(axiom_min)
                                    else:
                                        raw_masked[violators] = np.nan
                                        
                        if axiom_max is not None:
                            violators = raw_masked > float(axiom_max)
                            if violators.any():
                                msg = f"Pure number violates max bound of {axiom_max}."
                                if should_warn and not should_enforce:
                                    warnings.warn(f"Phaethon Axiom Warning: {msg}", category=UserWarning, stacklevel=2)
                                if should_enforce:
                                    if on_err == 'raise':
                                        raise AxiomViolationError(msg)
                                    elif on_err == 'clip':
                                        raw_masked[violators] = float(axiom_max)
                                    else:
                                        raw_masked[violators] = np.nan

                        if getattr(source_cls, '__name__', '') == getattr(field.target_unit, '__name__', ''):
                            result_array[pure_num_mask] = raw_masked
                        else:
                            result_array[pure_num_mask] = source_cls(raw_masked, context=active_context).to(field.target_unit, active_context).mag
                            
                    except Exception as e:
                        if on_err == 'raise':
                            if isinstance(e, AxiomViolationError):
                                raise e
                            raise NormalizationError(
                                field=field_name, issue=str(e), indices=[],
                                raw_sample="unknown", expected_dim=str(target_dim) if target_dim else "unknown",
                                suggestion="Check upstream data or set Field(on_error='coerce')."
                            )

            return pl.Series(result_array)

        mapped_expr = expr.map_batches(_vectorized_numpy_bridge, return_dtype=pl.Float64)
        return pl.when(mapped_expr.is_nan()).then(pl.lit(None, dtype=pl.Float64)).otherwise(mapped_expr)