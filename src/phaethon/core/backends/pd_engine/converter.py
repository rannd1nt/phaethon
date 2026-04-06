from __future__ import annotations

import pandas as pd
import numpy as np
import warnings
from typing import Any
from ...registry import ureg
from ....exceptions import AxiomViolationError, NormalizationError, UnitNotFoundError, DimensionMismatchError
from ...config import get_merged_context, get_config

class ConverterStage:
    @staticmethod
    def process(
        working_df: pd.DataFrame,
        field_name: str,
        field: Any,
        raw_series: pd.Series,
        values_array: np.ndarray,
        units_array: np.ndarray | None,
        isna_mask: np.ndarray,
        on_err: str,
        target_dim: str | None
    ) -> np.ndarray:
        
        result_array = np.full(len(raw_series), np.nan, dtype=float)
        
        active_context = get_merged_context(getattr(field, 'context', {}))
        if getattr(field, 'axiom_strictness_level', None) is not None:
            active_context["axiom_strictness_level"] = field.axiom_strictness_level
        if getattr(field, 'on_error', None) is not None:
            active_context["default_on_error"] = field.on_error

        strictness = get_config("axiom_strictness_level", getattr(field, 'axiom_strictness_level', None)) or "default"
        should_warn = strictness in ("strict_warn", "loose_warn")
        should_enforce = strictness in ("default", "strict", "strict_warn")

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
                        
                        # VALIDASI MIN
                        if axiom_min is not None:
                            violators = raw_masked < float(axiom_min)
                            if violators.any():
                                violator_indices = working_df.index[mask][violators].tolist()
                                msg = f"Raw '{u_str}' violates min bound of {axiom_min} at indices {violator_indices}"
                                
                                if should_warn and not should_enforce:
                                    warnings.warn(f"Phaethon Axiom Warning: {msg}", category=UserWarning, stacklevel=2)
                                
                                if should_enforce:
                                    if on_err == 'raise':
                                        raise AxiomViolationError(msg)
                                    elif on_err == 'clip':
                                        raw_masked[violators] = float(axiom_min)
                                    else:
                                        raw_masked[violators] = np.nan
                                
                        # VALIDASI MAX
                        if axiom_max is not None:
                            violators = raw_masked > float(axiom_max)
                            if violators.any():
                                violator_indices = working_df.index[mask][violators].tolist()
                                msg = f"Raw '{u_str}' violates max bound of {axiom_max} at indices {violator_indices}"
                                
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
                            target_instances = source_instances.to(field.target_unit)
                            result_array[mask] = target_instances.mag
                            
                    except UnitNotFoundError:
                        if on_err == 'raise':
                            bad_indices = working_df.index[mask].tolist()
                            raw_sample = raw_series.loc[bad_indices[0]] if len(bad_indices) > 0 else u_str
                            clean_u_str = str(u_str).strip()
                            issue_msg = "Missing or malformed unit string." if clean_u_str.isnumeric() or clean_u_str == "" else f"Unrecognized unit '{u_str}'."
                            raise NormalizationError(
                                field=field_name, issue=issue_msg, indices=bad_indices,
                                raw_sample=str(raw_sample), expected_dim=str(target_dim) if target_dim else "unknown",
                                suggestion="Fix the raw data, register the unit alias, or set Field(on_error='coerce')."
                            )
                    except DimensionMismatchError as e:
                        if on_err == 'raise':
                            bad_indices = working_df.index[mask].tolist()
                            raw_sample = raw_series.loc[bad_indices[0]] if len(bad_indices) > 0 else "unknown"
                            raise NormalizationError(
                                field=field_name, issue=str(e), indices=bad_indices,
                                raw_sample=str(raw_sample), expected_dim=str(target_dim) if target_dim else "unknown",
                                suggestion=f"Check the source data. Expected '{target_dim}' but received a completely different dimension."
                            )
                    except Exception as e:
                        if on_err == 'raise':
                            if isinstance(e, AxiomViolationError): raise e
                            bad_indices = working_df.index[mask].tolist()
                            raw_sample = raw_series.loc[bad_indices[0]] if len(bad_indices) > 0 else "unknown"
                            raise NormalizationError(
                                field=field_name, issue=str(e), indices=bad_indices,
                                raw_sample=str(raw_sample), expected_dim=str(target_dim) if target_dim else "unknown",
                                suggestion="Verify data formatting or set Field(on_error='coerce')."
                            )
            
            pure_num_mask = pd.isna(units_array) & (~isna_mask) & (~np.isnan(values_array))
        else:
            pure_num_mask = (~isna_mask) & (~np.isnan(values_array))

        if pure_num_mask.any():
            if field.parse_string:
                source_cls = field.source_unit
            else:
                source_cls = field.source_unit or field.target_unit

            if source_cls is None:
                if on_err == 'raise':
                    bad_indices = working_df.index[pure_num_mask].tolist()
                    raise NormalizationError(
                        field=field_name, 
                        issue="Value has no unit, and no 'source_unit' fallback was provided.",
                        indices=bad_indices, 
                        raw_sample="unknown", 
                        expected_dim=str(target_dim) if target_dim else "unknown",
                        suggestion="Provide 'source_unit' in Field() to handle numbers without units, or ensure all data contains valid units."
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
                    
                    # PURE NUM VALIDASI MIN
                    if axiom_min is not None:
                        violators = raw_masked < float(axiom_min)
                        if violators.any():
                            violator_indices = working_df.index[pure_num_mask][violators].tolist()
                            msg = f"Pure number violates min bound of {axiom_min} at indices {violator_indices}"
                            
                            if should_warn and not should_enforce:
                                warnings.warn(f"Phaethon Axiom Warning: {msg}", category=UserWarning, stacklevel=2)
                                
                            if should_enforce:
                                if on_err == 'raise':
                                    raise AxiomViolationError(msg)
                                elif on_err == 'clip':
                                    raw_masked[violators] = float(axiom_min)
                                else:
                                    raw_masked[violators] = np.nan
                            
                    # PURE NUM VALIDASI MAX
                    if axiom_max is not None:
                        violators = raw_masked > float(axiom_max)
                        if violators.any():
                            violator_indices = working_df.index[pure_num_mask][violators].tolist()
                            msg = f"Pure number violates max bound of {axiom_max} at indices {violator_indices}"
                            
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
                        result_array[pure_num_mask] = raw_masked
                    else:
                        source_instances = source_cls(raw_masked, context=active_context)
                        target_instances = source_instances.to(field.target_unit)
                        result_array[pure_num_mask] = target_instances.mag
                        
                except Exception as e:
                    if on_err == 'raise':
                        if isinstance(e, AxiomViolationError): raise e
                        bad_indices = working_df.index[pure_num_mask].tolist()
                        raw_sample = raw_series.loc[bad_indices[0]] if len(bad_indices) > 0 else "unknown"
                        raise NormalizationError(
                            field=field_name, issue=str(e), indices=bad_indices,
                            raw_sample=str(raw_sample), expected_dim=str(target_dim) if target_dim else "unknown",
                            suggestion="Check upstream data formatting or set Field(on_error='coerce')."
                        )
                    else:
                        raise e

        return result_array